
#!/usr/bin/env python3
"""
Enhanced Weather Service for Deep Blue Pool Chemistry.

This module provides weather data retrieval and analysis with a focus on
how weather conditions affect pool chemistry. It supports zip code-based
location lookup and provides detailed 5-day forecasts with pool chemistry
impact analysis.

Features:
- Zip code-based location lookup
- Current weather conditions
- 5-day weather forecast
- Detailed pool chemistry impact analysis
- Weather data caching to reduce API calls
"""

import os
import json
import logging
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Union

# Configure logging
logger = logging.getLogger(__name__)

class EnhancedWeatherService:
    """
    Enhanced weather service for retrieving and analyzing weather data.
    
    This class provides methods for retrieving current weather conditions
    and forecasts based on zip code, and analyzing how weather conditions
    affect pool chemistry.
    
    Attributes:
        api_key: API key for the weather service
        cache_file: Path to the cache file
        update_interval: Time in seconds before refreshing weather data
        cache: Dictionary containing cached weather data
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        cache_file: str = "data/weather_cache.json",
        update_interval: int = 3600
    ):
        """
        Initialize the EnhancedWeatherService.
        
        Args:
            api_key: API key for the weather service. If None, will use environment
                variable WEATHER_API_KEY or a default test key.
            cache_file: Path to the cache file for storing weather data.
            update_interval: Time in seconds before refreshing weather data.
        """
        self.api_key = api_key or os.environ.get("WEATHER_API_KEY", "demo_key")
        self.cache_file = cache_file
        self.update_interval = update_interval
        self.cache = self._load_cache()
        
        # Ensure cache file directory exists
        os.makedirs(os.path.dirname(cache_file), exist_ok=True)
    
    def _load_cache(self) -> Dict[str, Any]:
        """
        Load weather data from the cache file.
        
        Returns:
            Dictionary containing cached weather data.
        """
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r') as f:
                    return json.load(f)
            return {}
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Error loading weather cache: {e}")
            return {}
    
    def _save_cache(self) -> None:
        """Save weather data to the cache file."""
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(self.cache, f, indent=2)
        except IOError as e:
            logger.error(f"Error saving weather cache: {e}")
    
    def _is_cache_valid(self, location_key: str) -> bool:
        """
        Check if the cached data for a location is still valid.
        
        Args:
            location_key: Key for the location in the cache.
            
        Returns:
            True if the cache is valid, False otherwise.
        """
        if location_key not in self.cache:
            return False
        
        if "timestamp" not in self.cache[location_key]:
            return False
        
        try:
            cache_time = datetime.fromisoformat(self.cache[location_key]["timestamp"])
            current_time = datetime.now()
            
            # Check if the cache is older than the update interval
            if (current_time - cache_time).total_seconds() > self.update_interval:
                return False
            
            return True
        except (ValueError, TypeError) as e:
            logger.error(f"Error checking cache validity: {e}")
            return False
    
    def _fetch_location_data(self, zip_code: str) -> Dict[str, Any]:
        """
        Fetch location data for a zip code.
        
        Args:
            zip_code: The zip code to look up.
            
        Returns:
            Dictionary containing location data.
        """
        try:
            url = f"http://api.weatherapi.com/v1/search.json?key={self.api_key}&q={zip_code}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data and len(data) > 0:
                    return {
                        "name": data[0]["name"],
                        "region": data[0]["region"],
                        "country": data[0]["country"],
                        "lat": data[0]["lat"],
                        "lon": data[0]["lon"]
                    }
            
            logger.warning(f"Failed to fetch location data for zip code {zip_code}: {response.status_code}")
            return {
                "name": f"Unknown ({zip_code})",
                "region": "Unknown",
                "country": "Unknown",
                "lat": 0,
                "lon": 0
            }
        except Exception as e:
            logger.error(f"Error fetching location data: {e}")
            return {
                "name": f"Error ({zip_code})",
                "region": "Error",
                "country": "Error",
                "lat": 0,
                "lon": 0
            }
    
    def _fetch_current_weather(self, zip_code: str) -> Dict[str, Any]:
        """
        Fetch current weather data for a zip code.
        
        Args:
            zip_code: The zip code to get weather data for.
            
        Returns:
            Dictionary containing current weather data.
        """
        try:
            url = f"http://api.weatherapi.com/v1/current.json?key={self.api_key}&q={zip_code}&aqi=no"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                location_data = self._fetch_location_data(zip_code)
                
                return {
                    "location": location_data,
                    "temperature": data["current"]["temp_f"],
                    "humidity": data["current"]["humidity"],
                    "conditions": data["current"]["condition"]["text"],
                    "precipitation": data["current"]["precip_in"],
                    "uv_index": data["current"]["uv"],
                    "wind_mph": data["current"]["wind_mph"],
                    "timestamp": datetime.now().isoformat()
                }
            
            logger.warning(f"Failed to fetch weather data for zip code {zip_code}: {response.status_code}")
            return self._get_default_weather_data(zip_code)
        except Exception as e:
            logger.error(f"Error fetching weather data: {e}")
            return self._get_default_weather_data(zip_code)
    
    def _fetch_forecast(self, zip_code: str, days: int = 5) -> List[Dict[str, Any]]:
        """
        Fetch weather forecast for a zip code.
        
        Args:
            zip_code: The zip code to get forecast data for.
            days: Number of days to forecast (max 10).
            
        Returns:
            List of dictionaries containing forecast data.
        """
        try:
            url = f"http://api.weatherapi.com/v1/forecast.json?key={self.api_key}&q={zip_code}&days={days}&aqi=no&alerts=no"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                forecast = []
                
                for day in data["forecast"]["forecastday"]:
                    forecast.append({
                        "date": day["date"],
                        "temperature_high": day["day"]["maxtemp_f"],
                        "temperature_low": day["day"]["mintemp_f"],
                        "humidity": day["day"]["avghumidity"],
                        "conditions": day["day"]["condition"]["text"],
                        "precipitation": day["day"]["totalprecip_in"],
                        "uv_index": day["day"]["uv"],
                        "wind_mph": day["day"]["maxwind_mph"],
                        "chance_of_rain": day["day"]["daily_chance_of_rain"],
                        "hourly": [
                            {
                                "time": hour["time"],
                                "temperature": hour["temp_f"],
                                "humidity": hour["humidity"],
                                "conditions": hour["condition"]["text"],
                                "precipitation": hour["precip_in"],
                                "uv_index": hour["uv"],
                                "wind_mph": hour["wind_mph"]
                            }
                            for hour in day["hour"]
                        ]
                    })
                
                return forecast
            
            logger.warning(f"Failed to fetch forecast data for zip code {zip_code}: {response.status_code}")
            return self._get_default_forecast(days)
        except Exception as e:
            logger.error(f"Error fetching forecast data: {e}")
            return self._get_default_forecast(days)
    
    def _get_default_weather_data(self, zip_code: str) -> Dict[str, Any]:
        """
        Get default weather data when API calls fail.
        
        Args:
            zip_code: The zip code that was requested.
            
        Returns:
            Dictionary containing default weather data.
        """
        location_data = self._fetch_location_data(zip_code)
        
        return {
            "location": location_data,
            "temperature": 75.0,
            "humidity": 50.0,
            "conditions": "Unknown",
            "precipitation": 0.0,
            "uv_index": 5,
            "wind_mph": 5.0,
            "timestamp": datetime.now().isoformat()
        }
    
    def _get_default_forecast(self, days: int = 5) -> List[Dict[str, Any]]:
        """
        Get default forecast data when API calls fail.
        
        Args:
            days: Number of days to forecast.
            
        Returns:
            List of dictionaries containing default forecast data.
        """
        forecast = []
        
        for i in range(days):
            date = (datetime.now() + timedelta(days=i)).strftime("%Y-%m-%d")
            forecast.append({
                "date": date,
                "temperature_high": 75.0,
                "temperature_low": 65.0,
                "humidity": 50.0,
                "conditions": "Unknown",
                "precipitation": 0.0,
                "uv_index": 5,
                "wind_mph": 5.0,
                "chance_of_rain": 0,
                "hourly": [
                    {
                        "time": f"{date} {hour:02d}:00",
                        "temperature": 70.0,
                        "humidity": 50.0,
                        "conditions": "Unknown",
                        "precipitation": 0.0,
                        "uv_index": 5,
                        "wind_mph": 5.0
                    }
                    for hour in range(24)
                ]
            })
        
        return forecast
    
    def get_current_weather(self, zip_code: str) -> Dict[str, Any]:
        """
        Get current weather data for a zip code.
        
        Args:
            zip_code: The zip code to get weather data for.
            
        Returns:
            Dictionary containing current weather data.
        """
        # Create a cache key from the zip code
        cache_key = f"zip_{zip_code}"
        
        # Check if we have valid cached data
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]
        
        # Fetch new data
        weather_data = self._fetch_current_weather(zip_code)
        
        # Update the cache
        self.cache[cache_key] = weather_data
        self._save_cache()
        
        return weather_data
    
    def get_forecast(self, zip_code: str, days: int = 5) -> List[Dict[str, Any]]:
        """
        Get weather forecast for a zip code.
        
        Args:
            zip_code: The zip code to get forecast data for.
            days: Number of days to forecast (max 10).
            
        Returns:
            List of dictionaries containing forecast data.
        """
        # Create a cache key from the zip code and days
        cache_key = f"forecast_{zip_code}_{days}"
        
        # Check if we have valid cached data
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]["forecast"]
        
        # Fetch new data
        forecast_data = self._fetch_forecast(zip_code, days)
        
        # Update the cache
        self.cache[cache_key] = {
            "forecast": forecast_data,
            "timestamp": datetime.now().isoformat()
        }
        self._save_cache()
        
        return forecast_data
    
    def get_temperature(self, zip_code: str) -> float:
        """
        Get the current temperature for a zip code.
        
        Args:
            zip_code: The zip code to get temperature for.
            
        Returns:
            Current temperature in Fahrenheit.
        """
        weather_data = self.get_current_weather(zip_code)
        return weather_data["temperature"]
    
    def get_humidity(self, zip_code: str) -> float:
        """
        Get the current humidity for a zip code.
        
        Args:
            zip_code: The zip code to get humidity for.
            
        Returns:
            Current humidity percentage.
        """
        weather_data = self.get_current_weather(zip_code)
        return weather_data["humidity"]
    
    def get_conditions(self, zip_code: str) -> str:
        """
        Get the current weather conditions for a zip code.
        
        Args:
            zip_code: The zip code to get conditions for.
            
        Returns:
            Current weather conditions description.
        """
        weather_data = self.get_current_weather(zip_code)
        return weather_data["conditions"]
    
    def get_precipitation(self, zip_code: str) -> float:
        """
        Get the current precipitation for a zip code.
        
        Args:
            zip_code: The zip code to get precipitation for.
            
        Returns:
            Current precipitation in inches.
        """
        weather_data = self.get_current_weather(zip_code)
        return weather_data["precipitation"]
    
    def get_uv_index(self, zip_code: str) -> int:
        """
        Get the current UV index for a zip code.
        
        Args:
            zip_code: The zip code to get UV index for.
            
        Returns:
            Current UV index.
        """
        weather_data = self.get_current_weather(zip_code)
        return weather_data["uv_index"]
    
    def analyze_weather_impact(self, zip_code: str) -> Dict[str, List[str]]:
        """
        Analyze the impact of current and forecasted weather on pool chemistry.
        
        This method analyzes how current and forecasted weather conditions
        will affect pool chemistry and provides detailed recommendations
        for maintaining proper chemical balance.
        
        Args:
            zip_code: The zip code to analyze weather impact for.
            
        Returns:
            Dictionary containing impact analysis and recommendations for
            each chemical parameter.
        """
        # Get current weather and forecast
        current = self.get_current_weather(zip_code)
        forecast = self.get_forecast(zip_code)
        
        # Initialize impact analysis
        impact = {
            "chlorine": [],
            "ph": [],
            "alkalinity": [],
            "calcium": [],
            "cyanuric_acid": [],
            "general": []
        }
        
        # Analyze current weather impact
        self._analyze_temperature_impact(current["temperature"], impact)
        self._analyze_uv_impact(current["uv_index"], impact)
        self._analyze_precipitation_impact(current["precipitation"], impact)
        self._analyze_humidity_impact(current["humidity"], impact)
        
        # Analyze forecast impact
        high_temp_days = 0
        rainy_days = 0
        high_uv_days = 0
        
        for day in forecast:
            if day["temperature_high"] > 90:
                high_temp_days += 1
            
            if day["precipitation"] > 0.1:
                rainy_days += 1
            
            if day["uv_index"] > 8:
                high_uv_days += 1
        
        # Add forecast-based recommendations
        if high_temp_days > 0:
            impact["chlorine"].append(
                f"High temperatures forecasted for {high_temp_days} days will accelerate chlorine depletion. "
                f"Consider increasing chlorine by 0.5 ppm for each day over 90\u00b0F."
            )
        
        if rainy_days > 0:
            impact["ph"].append(
                f"Rain is forecasted for {rainy_days} days, which may lower pH. "
                f"Monitor pH levels after rainfall and adjust as needed."
            )
            impact["alkalinity"].append(
                f"Rain is forecasted for {rainy_days} days, which may dilute alkalinity. "
                f"Be prepared to add alkalinity increaser after significant rainfall."
            )
        
        if high_uv_days > 0:
            impact["chlorine"].append(
                f"High UV levels forecasted for {high_uv_days} days will accelerate chlorine depletion. "
                f"Consider adding a UV stabilizer or increasing cyanuric acid levels."
            )
            impact["cyanuric_acid"].append(
                f"High UV levels forecasted for {high_uv_days} days. "
                f"Ensure cyanuric acid levels are between 30-50 ppm to protect chlorine."
            )
        
        # Add general recommendations based on forecast
        if high_temp_days > 2 and rainy_days == 0:
            impact["general"].append(
                "Extended hot, dry weather forecasted. Monitor water levels for evaporation "
                "and be prepared to add water. This may affect calcium hardness and total alkalinity."
            )
        
        if rainy_days > 2:
            impact["general"].append(
                "Significant rainfall forecasted. Consider covering the pool if possible. "
                "Be prepared to rebalance chemicals after rain subsides."
            )
        
        return impact
    
    def _analyze_temperature_impact(self, temperature: float, impact: Dict[str, List[str]]) -> None:
        """
        Analyze the impact of temperature on pool chemistry.
        
        Args:
            temperature: Current temperature in Fahrenheit.
            impact: Dictionary to update with impact analysis.
        """
        if temperature > 90:
            impact["chlorine"].append(
                f"High temperature ({temperature:.1f}\u00b0F) accelerates chlorine depletion. "
                f"Increase chlorine monitoring frequency and consider adding 0.5-1.0 ppm more than usual."
            )
            impact["general"].append(
                f"High temperature ({temperature:.1f}\u00b0F) increases water evaporation. "
                f"Monitor water level and be prepared to add water, which may affect overall chemical balance."
            )
        elif temperature > 85:
            impact["chlorine"].append(
                f"Warm temperature ({temperature:.1f}\u00b0F) moderately increases chlorine depletion. "
                f"Monitor chlorine levels more frequently."
            )
        elif temperature < 65:
            impact["chlorine"].append(
                f"Cool temperature ({temperature:.1f}\u00b0F) slows down chlorine depletion. "
                f"You may need less chlorine than usual."
            )
            impact["general"].append(
                f"Cool temperature ({temperature:.1f}\u00b0F) reduces effectiveness of some chemicals. "
                f"Chemical reactions may take longer to complete."
            )
    
    def _analyze_uv_impact(self, uv_index: int, impact: Dict[str, List[str]]) -> None:
        """
        Analyze the impact of UV index on pool chemistry.
        
        Args:
            uv_index: Current UV index.
            impact: Dictionary to update with impact analysis.
        """
        if uv_index > 8:
            impact["chlorine"].append(
                f"Very high UV index ({uv_index}) causes rapid chlorine depletion. "
                f"Expect to lose up to 5 ppm of chlorine per day without adequate cyanuric acid."
            )
            impact["cyanuric_acid"].append(
                f"Very high UV index ({uv_index}) requires adequate cyanuric acid protection. "
                f"Maintain 30-50 ppm of cyanuric acid to protect chlorine."
            )
        elif uv_index > 6:
            impact["chlorine"].append(
                f"High UV index ({uv_index}) increases chlorine depletion. "
                f"Ensure adequate cyanuric acid levels (30-50 ppm) to protect chlorine."
            )
    
    def _analyze_precipitation_impact(self, precipitation: float, impact: Dict[str, List[str]]) -> None:
        """
        Analyze the impact of precipitation on pool chemistry.
        
        Args:
            precipitation: Current precipitation in inches.
            impact: Dictionary to update with impact analysis.
        """
        if precipitation > 0.5:
            impact["ph"].append(
                f"Significant rainfall ({precipitation:.2f} inches) may lower pH due to acid rain. "
                f"Test and adjust pH after rain subsides."
            )
            impact["alkalinity"].append(
                f"Significant rainfall ({precipitation:.2f} inches) dilutes pool water. "
                f"Test and adjust alkalinity after rain subsides."
            )
            impact["chlorine"].append(
                f"Significant rainfall ({precipitation:.2f} inches) dilutes chlorine levels. "
                f"Test and adjust chlorine after rain subsides."
            )
            impact["calcium"].append(
                f"Significant rainfall ({precipitation:.2f} inches) dilutes calcium hardness. "
                f"Test and adjust calcium hardness after rain subsides."
            )
        elif precipitation > 0.1:
            impact["general"].append(
                f"Light rainfall ({precipitation:.2f} inches) may affect pool chemistry. "
                f"Consider testing water balance after rain subsides."
            )
    
    def _analyze_humidity_impact(self, humidity: float, impact: Dict[str, List[str]]) -> None:
        """
        Analyze the impact of humidity on pool chemistry.
        
        Args:
            humidity: Current humidity percentage.
            impact: Dictionary to update with impact analysis.
        """
        if humidity > 80:
            impact["general"].append(
                f"High humidity ({humidity:.1f}%) reduces water evaporation. "
                f"This helps maintain water level but may concentrate chemicals over time."
            )
        elif humidity < 30:
            impact["general"].append(
                f"Low humidity ({humidity:.1f}%) increases water evaporation. "
                f"Monitor water level and be prepared to add water, which may affect overall chemical balance."
            )
    
    def get_detailed_forecast_impact(self, zip_code: str) -> List[Dict[str, Any]]:
        """
        Get detailed impact analysis for each day in the forecast.
        
        Args:
            zip_code: The zip code to analyze forecast impact for.
            
        Returns:
            List of dictionaries containing detailed impact analysis for each day.
        """
        forecast = self.get_forecast(zip_code)
        detailed_impact = []
        
        for day in forecast:
            day_impact = {
                "date": day["date"],
                "conditions": day["conditions"],
                "temperature_high": day["temperature_high"],
                "temperature_low": day["temperature_low"],
                "precipitation": day["precipitation"],
                "uv_index": day["uv_index"],
                "chance_of_rain": day["chance_of_rain"],
                "impact": {
                    "chlorine": [],
                    "ph": [],
                    "alkalinity": [],
                    "calcium": [],
                    "cyanuric_acid": [],
                    "general": []
                },
                "severity": self._calculate_impact_severity(day)
            }
            
            # Analyze temperature impact
            if day["temperature_high"] > 90:
                day_impact["impact"]["chlorine"].append(
                    f"High temperature ({day['temperature_high']:.1f}\u00b0F) will accelerate chlorine depletion. "
                    f"Increase chlorine by 0.5-1.0 ppm."
                )
                day_impact["impact"]["general"].append(
                    f"High temperature ({day['temperature_high']:.1f}\u00b0F) will increase water evaporation. "
                    f"Monitor water level."
                )
            elif day["temperature_high"] > 85:
                day_impact["impact"]["chlorine"].append(
                    f"Warm temperature ({day['temperature_high']:.1f}\u00b0F) will moderately increase chlorine depletion."
                )
            
            # Analyze UV impact
            if day["uv_index"] > 8:
                day_impact["impact"]["chlorine"].append(
                    f"Very high UV index ({day['uv_index']}) will cause rapid chlorine depletion."
                )
                day_impact["impact"]["cyanuric_acid"].append(
                    f"Very high UV index ({day['uv_index']}) requires adequate cyanuric acid protection."
                )
            elif day["uv_index"] > 6:
                day_impact["impact"]["chlorine"].append(
                    f"High UV index ({day['uv_index']}) will increase chlorine depletion."
                )
            
            # Analyze precipitation impact
            if day["precipitation"] > 0.5 or day["chance_of_rain"] > 70:
                day_impact["impact"]["ph"].append(
                    f"Significant chance of rainfall ({day['chance_of_rain']}%) may lower pH."
                )
                day_impact["impact"]["alkalinity"].append(
                    f"Significant chance of rainfall ({day['chance_of_rain']}%) may dilute alkalinity."
                )
                day_impact["impact"]["chlorine"].append(
                    f"Significant chance of rainfall ({day['chance_of_rain']}%) may dilute chlorine levels."
                )
            
            detailed_impact.append(day_impact)
        
        return detailed_impact
    
    def _calculate_impact_severity(self, day: Dict[str, Any]) -> str:
        """
        Calculate the overall severity of weather impact for a day.
        
        Args:
            day: Dictionary containing forecast data for a day.
            
        Returns:
            Severity level: "low", "moderate", or "high".
        """
        severity_score = 0
        
        # Temperature impact
        if day["temperature_high"] > 95:
            severity_score += 3
        elif day["temperature_high"] > 90:
            severity_score += 2
        elif day["temperature_high"] > 85:
            severity_score += 1
        
        # UV impact
        if day["uv_index"] > 10:
            severity_score += 3
        elif day["uv_index"] > 8:
            severity_score += 2
        elif day["uv_index"] > 6:
            severity_score += 1
        
        # Precipitation impact
        if day["precipitation"] > 1.0 or day["chance_of_rain"] > 90:
            severity_score += 3
        elif day["precipitation"] > 0.5 or day["chance_of_rain"] > 70:
            severity_score += 2
        elif day["precipitation"] > 0.1 or day["chance_of_rain"] > 50:
            severity_score += 1
        
        # Determine severity level
        if severity_score >= 5:
            return "high"
        elif severity_score >= 3:
            return "moderate"
        else:
            return "low"
    
    def get_location_name(self, zip_code: str) -> str:
        """
        Get the location name for a zip code.
        
        Args:
            zip_code: The zip code to get location name for.
            
        Returns:
            Location name (city, region).
        """
        weather_data = self.get_current_weather(zip_code)
        location = weather_data["location"]
        return f"{location['name']}, {location['region']}"
