"""
Weather service module for the Deep Blue Pool Chemistry application.

This module provides weather data retrieval and analysis for pool chemistry adjustments
based on current and forecasted weather conditions.
"""

import logging
import requests
import json
import os
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union

# Configure logger
logger = logging.getLogger(__name__)


class WeatherService:
    """
    Weather service for retrieving and analyzing weather data.
    
    This class provides methods for retrieving current and forecasted weather data
    and analyzing its impact on pool chemistry.
    
    Attributes:
        config: Configuration dictionary with API keys and settings
        cache_file: Path to the weather data cache file
        cache_data: Dictionary of cached weather data
        cache_expiry: Dictionary of cache expiry times
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the weather service.
        
        Args:
            config: Configuration dictionary with API keys and settings
        """
        self.config = config or {}
        self.location = self.config.get("location", "Florida")
        self.api_key = self.config.get("api_key", "")
        self.update_interval = self.config.get("update_interval", 3600)  # Default: 1 hour
        self.cache_file = self.config.get("cache_file", "weather_cache.json")
        self.cache_data = {}
        self.cache_expiry = {}
        
        # Load cached data if available
        self._load_cache()
        logger.info(f"Weather Service initialized for location: {self.location}")
    
    def _load_cache(self) -> None:
        """
        Load weather data from cache file.
        
        Raises:
            IOError: If there's an error reading the cache file
            json.JSONDecodeError: If the cache file contains invalid JSON
        """
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r') as f:
                    cache = json.load(f)
                    self.cache_data = cache.get("data", {})
                    self.cache_expiry = cache.get("expiry", {})
                logger.info(f"Loaded weather cache from {self.cache_file}")
        except (IOError, json.JSONDecodeError) as e:
            logger.error(f"Failed to load weather cache: {e}")
            self.cache_data = {}
            self.cache_expiry = {}
    
    def _save_cache(self) -> None:
        """
        Save weather data to cache file.
        
        Raises:
            IOError: If there's an error writing to the cache file
        """
        try:
            cache = {
                "data": self.cache_data,
                "expiry": self.cache_expiry
            }
            with open(self.cache_file, 'w') as f:
                json.dump(cache, f, indent=2)
            logger.info(f"Saved weather cache to {self.cache_file}")
        except IOError as e:
            logger.error(f"Failed to save weather cache: {e}")
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """
        Check if cached data is still valid.
        
        Args:
            cache_key: Cache key to check
            
        Returns:
            True if cache is valid, False otherwise
        """
        if cache_key not in self.cache_data or cache_key not in self.cache_expiry:
            return False
        
        expiry_time = self.cache_expiry.get(cache_key, 0)
        return time.time() < expiry_time
    
    def get_weather(self) -> Dict[str, Any]:
        """
        Get current weather data for the configured location.
        
        Returns:
            Dictionary containing weather data
            
        Raises:
            requests.RequestException: If there's an error retrieving weather data
        """
        cache_key = f"current_{self.location}"
        
        # Check if we have valid cached data
        if self._is_cache_valid(cache_key):
            logger.debug(f"Using cached weather data for {self.location}")
            return self.cache_data[cache_key]
        
        try:
            # In a real implementation, this would call a weather API
            # For this example, we'll return mock data
            weather_data = self._get_mock_weather_data()
            
            # Cache the data
            self.cache_data[cache_key] = weather_data
            self.cache_expiry[cache_key] = time.time() + self.update_interval
            self._save_cache()
            
            logger.info(f"Retrieved weather data for {self.location}")
            return weather_data
        except requests.RequestException as e:
            logger.error(f"Failed to retrieve weather data: {e}")
            
            # Return cached data if available, even if expired
            if cache_key in self.cache_data:
                logger.warning("Using expired cached weather data")
                return self.cache_data[cache_key]
            
            # Return empty data if no cache is available
            return {
                "temperature": 75,
                "humidity": 50,
                "conditions": "Unknown",
                "uv_index": 0,
                "wind_speed": 0,
                "precipitation": 0,
                "timestamp": datetime.now().isoformat()
            }
    
    def get_forecast(self, days: int = 3) -> List[Dict[str, Any]]:
        """
        Get weather forecast for the configured location.
        
        Args:
            days: Number of days to forecast
            
        Returns:
            List of dictionaries containing forecast data
            
        Raises:
            requests.RequestException: If there's an error retrieving forecast data
        """
        cache_key = f"forecast_{self.location}_{days}"
        
        # Check if we have valid cached data
        if self._is_cache_valid(cache_key):
            logger.debug(f"Using cached forecast data for {self.location}")
            return self.cache_data[cache_key]
        
        try:
            # In a real implementation, this would call a weather API
            # For this example, we'll return mock data
            forecast_data = self._get_mock_forecast_data(days)
            
            # Cache the data
            self.cache_data[cache_key] = forecast_data
            self.cache_expiry[cache_key] = time.time() + self.update_interval
            self._save_cache()
            
            logger.info(f"Retrieved {days}-day forecast for {self.location}")
            return forecast_data
        except requests.RequestException as e:
            logger.error(f"Failed to retrieve forecast data: {e}")
            
            # Return cached data if available, even if expired
            if cache_key in self.cache_data:
                logger.warning("Using expired cached forecast data")
                return self.cache_data[cache_key]
            
            # Return empty data if no cache is available
            return [self._get_mock_weather_data() for _ in range(days)]
    
    def _get_mock_weather_data(self) -> Dict[str, Any]:
        """
        Generate mock weather data for testing.
        
        Returns:
            Dictionary containing mock weather data
        """
        # Get current date and time
        now = datetime.now()
        
        # Generate mock data based on month (seasonal variations)
        month = now.month
        
        # Summer months (higher temperatures)
        if 5 <= month <= 9:
            temperature = 85 + (hash(now.strftime("%Y-%m-%d")) % 10)
            humidity = 65 + (hash(now.strftime("%H")) % 20)
            conditions = "Sunny" if hash(now.strftime("%Y-%m-%d")) % 4 != 0 else "Partly Cloudy"
            uv_index = 8 + (hash(now.strftime("%Y-%m-%d")) % 4)
            precipitation = 0 if hash(now.strftime("%Y-%m-%d")) % 5 != 0 else 0.2
        # Winter months (lower temperatures)
        else:
            temperature = 65 + (hash(now.strftime("%Y-%m-%d")) % 15)
            humidity = 45 + (hash(now.strftime("%H")) % 30)
            conditions = "Sunny" if hash(now.strftime("%Y-%m-%d")) % 3 != 0 else "Cloudy"
            uv_index = 4 + (hash(now.strftime("%Y-%m-%d")) % 3)
            precipitation = 0 if hash(now.strftime("%Y-%m-%d")) % 4 != 0 else 0.1
        
        # Wind speed is consistent year-round
        wind_speed = 5 + (hash(now.strftime("%H")) % 10)
        
        return {
            "temperature": temperature,
            "humidity": humidity,
            "conditions": conditions,
            "uv_index": uv_index,
            "wind_speed": wind_speed,
            "precipitation": precipitation,
            "timestamp": now.isoformat()
        }
    
    def _get_mock_forecast_data(self, days: int) -> List[Dict[str, Any]]:
        """
        Generate mock forecast data for testing.
        
        Args:
            days: Number of days to forecast
            
        Returns:
            List of dictionaries containing mock forecast data
        """
        forecast = []
        now = datetime.now()
        
        for i in range(days):
            forecast_date = now + timedelta(days=i)
            
            # Base the forecast on the mock weather data with some variations
            base_weather = self._get_mock_weather_data()
            
            # Add some variation for each day
            base_weather["temperature"] += (hash(forecast_date.strftime("%Y-%m-%d")) % 5) - 2
            base_weather["humidity"] += (hash(forecast_date.strftime("%Y-%m-%d")) % 10) - 5
            base_weather["timestamp"] = forecast_date.isoformat()
            
            # Change conditions occasionally
            if hash(forecast_date.strftime("%Y-%m-%d")) % 3 == 0:
                conditions = ["Sunny", "Partly Cloudy", "Cloudy", "Rainy"]
                base_weather["conditions"] = conditions[hash(forecast_date.strftime("%Y-%m-%d")) % len(conditions)]
                
                # Add precipitation for rainy days
                if base_weather["conditions"] == "Rainy":
                    base_weather["precipitation"] = 0.2 + (hash(forecast_date.strftime("%Y-%m-%d")) % 10) / 10
            
            forecast.append(base_weather)
        
        return forecast
    
    def analyze_weather_impact(self, weather_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze the impact of weather conditions on pool chemistry.
        
        Args:
            weather_data: Dictionary containing weather data
            
        Returns:
            Dictionary containing weather impact analysis
        """
        impact = {
            "evaporation_rate": 0.0,
            "chlorine_loss_rate": 0.0,
            "algae_growth_risk": "Low",
            "recommendations": []
        }
        
        # Calculate evaporation rate based on temperature, humidity, and wind speed
        temperature = weather_data.get("temperature", 75)
        humidity = weather_data.get("humidity", 50)
        wind_speed = weather_data.get("wind_speed", 0)
        uv_index = weather_data.get("uv_index", 0)
        conditions = weather_data.get("conditions", "Unknown")
        
        # Higher temperature, lower humidity, and higher wind speed increase evaporation
        evaporation_factor = (temperature / 100) * (1 - humidity / 100) * (1 + wind_speed / 10)
        impact["evaporation_rate"] = round(evaporation_factor * 0.25, 2)  # inches per day
        
        # Calculate chlorine loss rate based on temperature and UV index
        # Higher temperature and UV index increase chlorine loss
        chlorine_loss_factor = (temperature / 100) * (1 + uv_index / 5)
        impact["chlorine_loss_rate"] = round(chlorine_loss_factor * 0.5, 2)  # ppm per day
        
        # Determine algae growth risk based on temperature and conditions
        if temperature > 85 and conditions in ["Sunny", "Partly Cloudy"]:
            impact["algae_growth_risk"] = "High"
        elif temperature > 75:
            impact["algae_growth_risk"] = "Medium"
        else:
            impact["algae_growth_risk"] = "Low"
        
        # Generate recommendations based on analysis
        if impact["evaporation_rate"] > 0.2:
            impact["recommendations"].append("Monitor water level due to high evaporation rate")
        
        if impact["chlorine_loss_rate"] > 0.3:
            impact["recommendations"].append("Increase chlorine dosage to compensate for high UV-induced loss")
        
        if impact["algae_growth_risk"] == "High":
            impact["recommendations"].append("Consider algaecide treatment due to high algae growth risk")
        
        if conditions == "Rainy":
            impact["recommendations"].append("Check pH and alkalinity after rain")
        
        return impact
    
    def get_weather_with_impact(self) -> Dict[str, Any]:
        """
        Get current weather data with impact analysis.
        
        Returns:
            Dictionary containing weather data and impact analysis
        """
        weather_data = self.get_weather()
        impact = self.analyze_weather_impact(weather_data)
        
        return {
            "weather": weather_data,
            "impact": impact
        }
    
    def get_forecast_with_impact(self, days: int = 3) -> List[Dict[str, Any]]:
        """
        Get weather forecast with impact analysis.
        
        Args:
            days: Number of days to forecast
            
        Returns:
            List of dictionaries containing forecast data and impact analysis
        """
        forecast_data = self.get_forecast(days)
        forecast_with_impact = []
        
        for day_data in forecast_data:
            impact = self.analyze_weather_impact(day_data)
            forecast_with_impact.append({
                "weather": day_data,
                "impact": impact
            })
        
        return forecast_with_impact
    
    def clear_cache(self) -> None:
        """
        Clear the weather data cache.
        """
        self.cache_data = {}
        self.cache_expiry = {}
        
        # Remove cache file if it exists
        if os.path.exists(self.cache_file):
            try:
                os.remove(self.cache_file)
                logger.info(f"Removed weather cache file: {self.cache_file}")
            except OSError as e:
                logger.error(f"Failed to remove weather cache file: {e}")
        
        logger.info("Weather cache cleared")