# services/weather_service.py
import requests
import json
import time
import logging
import os
from pathlib import Path
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class WeatherService:
    """Service for fetching and processing weather data."""
    
    def __init__(self, api_key=None):
        self.api_key = api_key or os.environ.get("WEATHER_API_KEY")
        if not self.api_key:
            logger.warning("No Weather API key provided")
        
        self.cache_dir = Path("cache")
        self.cache_dir.mkdir(exist_ok=True)
        self.cache_duration = 3600  # 1 hour in seconds
        
    def get_weather_data(self, location, use_cache=True):
        """
        Get weather data for a location (ZIP code, city name, etc.)
        
        Args:
            location (str): Location identifier (ZIP code, city name)
            use_cache (bool): Whether to use cached data if available
            
        Returns:
            dict: Weather data or error information
        """
        cache_file = self.cache_dir / f"weather_{location}.json"
        
        # Try to use cached data if allowed and available
        if use_cache and self._is_valid_cache(cache_file):
            try:
                with open(cache_file, 'r') as f:
                    cached_data = json.load(f)
                    logger.info(f"Using cached weather data for {location}")
                    return cached_data
            except Exception as e:
                logger.warning(f"Failed to load cached weather data: {e}")
        
        # Make API request
        base_url = "https://api.weatherapi.com/v1/current.json"
        params = {
            "key": self.api_key,
            "q": location,
            "aqi": "no"
        }
        
        try:
            response = requests.get(base_url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                # Cache the successful response
                self._cache_response(cache_file, data)
                return data
            else:
                # Try to use expired cache as fallback
                fallback_data = self._get_fallback_cache(cache_file)
                if fallback_data:
                    return fallback_data
                    
                try:
                    error_details = response.json()
                    return {"error": f"API Error: {response.status_code} - {error_details.get('error', {}).get('message', 'Unknown error')}"}
                except json.JSONDecodeError:
                    return {"error": f"Invalid response format. Status code: {response.status_code}"}
                    
        except requests.RequestException as e:
            # Try to use cached data as fallback
            fallback_data = self._get_fallback_cache(cache_file)
            if fallback_data:
                return fallback_data
                    
            return {"error": f"Network error: {str(e)}"}
    
    def _is_valid_cache(self, cache_file):
        """Check if cache file exists and is not expired"""
        if not cache_file.exists():
            return False
            
        file_age = time.time() - cache_file.stat().st_mtime
        return file_age < self.cache_duration
    
    def _cache_response(self, cache_file, data):
        """Cache the API response to a file"""
        try:
            with open(cache_file, 'w') as f:
                json.dump(data, f)
        except Exception as e:
            logger.warning(f"Failed to cache weather data: {e}")
    
    def _get_fallback_cache(self, cache_file):
        """Try to get cached data as fallback even if expired"""
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    cached_data = json.load(f)
                    logger.warning(f"Using expired cached weather data")
                    cached_data["cached"] = True
                    cached_data["cache_warning"] = "Using outdated weather data"
                    return cached_data
            except Exception:
                pass
        return None
        
    def calculate_pool_impact(self, weather_data):
        """Calculate the impact of weather on pool chemistry"""
        try:
            current = weather_data.get('current', {})
            temp = current.get('temp_f', 75)
            humidity = current.get('humidity', 50)
            conditions = current.get('condition', {}).get('text', '').lower()
            
            impact = "Low"
            
            # Higher temperatures increase chlorine demand
            if temp > 85:
                impact = "High"
            elif temp > 75:
                impact = "Medium"
                
            # Rain can affect pH and dilute chemicals
            if any(term in conditions for term in ['rain', 'shower', 'drizzle', 'precipitation']):
                impact = "High"
                
            # High humidity can reduce water evaporation
            if humidity > 80 and impact != "High":
                impact = "Medium"
                
            return {
                "impact": impact,
                "reasons": self._generate_impact_reasons(impact, temp, humidity, conditions)
            }
        except Exception as e:
            logger.error(f"Error calculating weather impact: {e}")
            return {"impact": "Unknown", "reasons": ["Error calculating impact"]}
    
    def _generate_impact_reasons(self, impact, temp, humidity, conditions):
        """Generate human-readable reasons for the calculated impact"""
        reasons = []
        
        if temp > 85:
            reasons.append("High temperature increases chlorine demand")
        elif temp > 75:
            reasons.append("Moderate temperature may affect chemical balance")
            
        if any(term in conditions for term in ['rain', 'shower', 'drizzle', 'precipitation']):
            reasons.append("Precipitation can affect pH and dilute chemicals")
            
        if humidity > 80:
            reasons.append("High humidity reduces water evaporation")
            
        return reasons
