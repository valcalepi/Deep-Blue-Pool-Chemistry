#!/usr/bin/env python3
"""
Weather Service for Deep Blue Pool Chemistry

This module provides weather data for pool chemistry analysis.
"""

import logging
import time
import threading
import json
import os
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

logger = logging.getLogger("weather_service")

class WeatherService:
    """
    Service for retrieving and managing weather data.
    """
    
    def __init__(self, config):
        """
        Initialize Weather service with configuration.
        
        Args:
            config: Configuration dictionary
        """
        self.location = config.get("location", "Florida")
        self.update_interval = config.get("update_interval", 3600)  # Default: 1 hour
        self.weather_data = {}
        self.forecast_data = []
        self.last_update = 0
        self.api_key = config.get("api_key", "")
        self.use_real_api = config.get("use_real_api", False) and self.api_key
        self.cache_file = config.get("cache_file", "weather_cache.json")
        
        logger.info(f"Weather Service initialized for {self.location} with update interval {self.update_interval}s")
        
        # Try to import requests for API calls
        try:
            import requests
            logger.info("Using requests module for weather data")
            self.requests = requests
        except ImportError:
            logger.warning("Requests module not found, using mock implementation")
            self.requests = None
            
        # Load cached data if available
        self._load_cached_data()
            
        # Initial update
        self.update_weather()
        
        # Start update thread
        self.update_thread = threading.Thread(target=self._update_loop, daemon=True)
        self.update_thread.start()
        
    def _load_cached_data(self):
        """Load weather data from cache file if available."""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r') as f:
                    cache = json.load(f)
                    
                    # Check if cache is recent (less than 2 hours old)
                    if cache.get("timestamp", 0) > time.time() - 7200:
                        self.weather_data = cache.get("current", {})
                        self.forecast_data = cache.get("forecast", [])
                        self.last_update = cache.get("timestamp", 0)
                        logger.info(f"Loaded weather data from cache, last updated: {datetime.fromtimestamp(self.last_update)}")
                        return True
        except Exception as e:
            logger.error(f"Error loading cached weather data: {e}")
            
        return False
        
    def _save_cached_data(self):
        """Save weather data to cache file."""
        try:
            cache = {
                "timestamp": self.last_update,
                "current": self.weather_data,
                "forecast": self.forecast_data
            }
            
            os.makedirs(os.path.dirname(os.path.abspath(self.cache_file)), exist_ok=True)
            with open(self.cache_file, 'w') as f:
                json.dump(cache, f)
                
            logger.info(f"Saved weather data to cache file: {self.cache_file}")
        except Exception as e:
            logger.error(f"Error saving weather data to cache: {e}")
        
    def update_weather(self):
        """Update weather data."""
        logger.info(f"Updating weather data for {self.location}")
        
        if self.use_real_api and self.requests:
            self._update_with_api()
        else:
            self._update_mock_data()
            
        self.last_update = time.time()
        logger.info(f"Weather data updated successfully for {self.location}")
        
        # Save to cache
        self._save_cached_data()
            
    def _update_with_api(self):
        """Update weather data using a real API."""
        try:
            # This would be a real API call in production
            # For example, using OpenWeatherMap API:
            # url = f"https://api.openweathermap.org/data/2.5/weather?q={self.location}&appid={self.api_key}&units=imperial"
            # response = self.requests.get(url)
            # data = response.json()
            
            # For now, use mock data since we don't have a real API key
            logger.warning("Real API configured but using mock data (no valid API key or API not implemented)")
            self._update_mock_data()
            
        except Exception as e:
            logger.error(f"Failed to update weather data from API: {e}")
            self._update_mock_data()
            
    def _update_mock_data(self):
        """Update with mock weather data."""
        import random
        
        # Generate somewhat realistic weather data
        is_rainy = random.random() < 0.3
        is_cloudy = random.random() < 0.4
        
        if is_rainy:
            conditions = random.choice(["Light Rain", "Rain", "Heavy Rain", "Thunderstorm"])
            precipitation = round(random.uniform(0.1, 2.0), 2)
            cloud_cover = random.randint(70, 100)
            uv_index = round(random.uniform(0, 3), 1)
        elif is_cloudy:
            conditions = random.choice(["Partly Cloudy", "Mostly Cloudy", "Cloudy"])
            precipitation = round(random.uniform(0, 0.1), 2)
            cloud_cover = random.randint(30, 70)
            uv_index = round(random.uniform(3, 6), 1)
        else:
            conditions = random.choice(["Sunny", "Clear", "Mostly Sunny"])
            precipitation = 0
            cloud_cover = random.randint(0, 30)
            uv_index = round(random.uniform(6, 11), 1)
        
        # Base temperature on time of year (assuming Northern Hemisphere)
        month = datetime.now().month
        if 5 <= month <= 9:  # Summer months
            base_temp = random.uniform(75, 95)
        elif month in [4, 10]:  # Spring/Fall
            base_temp = random.uniform(60, 80)
        else:  # Winter
            base_temp = random.uniform(40, 70)
            
        # Adjust for weather conditions
        if is_rainy:
            base_temp -= random.uniform(5, 15)
        
        self.weather_data = {
            "temperature": round(base_temp, 1),
            "humidity": round(random.uniform(40, 90), 1),
            "conditions": conditions,
            "wind_speed": round(random.uniform(0, 15), 1),
            "precipitation": precipitation,
            "uv_index": uv_index,
            "cloud_cover": cloud_cover,
            "timestamp": datetime.now().isoformat()
        }
        
        # Generate forecast data
        self._generate_mock_forecast()
        
    def _generate_mock_forecast(self, days=7):
        """Generate mock forecast data."""
        import random
        
        forecast = []
        start_date = datetime.now()
        
        # Use current conditions as a starting point
        prev_temp = self.weather_data.get("temperature", 75)
        prev_conditions = self.weather_data.get("conditions", "Sunny")
        prev_uv = self.weather_data.get("uv_index", 5)
        
        for i in range(days):
            day_date = start_date + timedelta(days=i)
            
            # Temperature varies by \u00b15\u00b0F from previous day
            temp_change = random.uniform(-5, 5)
            temperature = prev_temp + temp_change
            
            # Weather patterns tend to persist with some randomness
            if "Rain" in prev_conditions or random.random() < 0.3:
                conditions = random.choice(["Light Rain", "Rain", "Heavy Rain", "Thunderstorm", "Partly Cloudy", "Mostly Cloudy"])
                precipitation = round(random.uniform(0.1, 2.0), 2) if "Rain" in conditions else 0
                cloud_cover = random.randint(50, 100)
                uv_index = round(random.uniform(0, 5), 1)
            elif "Cloud" in prev_conditions or random.random() < 0.4:
                conditions = random.choice(["Partly Cloudy", "Mostly Cloudy", "Cloudy", "Sunny"])
                precipitation = 0
                cloud_cover = random.randint(30, 70)
                uv_index = round(random.uniform(3, 8), 1)
            else:
                conditions = random.choice(["Sunny", "Clear", "Mostly Sunny"])
                precipitation = 0
                cloud_cover = random.randint(0, 30)
                uv_index = round(random.uniform(6, 11), 1)
            
            forecast.append({
                "date": day_date.strftime("%Y-%m-%d"),
                "temperature": round(temperature, 1),
                "conditions": conditions,
                "precipitation": precipitation,
                "humidity": round(random.uniform(40, 90), 1),
                "wind_speed": round(random.uniform(0, 15), 1),
                "uv_index": uv_index,
                "cloud_cover": cloud_cover
            })
            
            # Update previous values for next iteration
            prev_temp = temperature
            prev_conditions = conditions
            prev_uv = uv_index
            
        self.forecast_data = forecast
        
    def _update_loop(self):
        """Background thread to update weather data periodically."""
        while True:
            time.sleep(self.update_interval)
            self.update_weather()
            
    def get_weather(self):
        """
        Get current weather data.
        
        Returns:
            Dict[str, Any]: Current weather data
        """
        # Update if data is stale
        if time.time() - self.last_update > self.update_interval:
            self.update_weather()
            
        return self.weather_data
        
    def get_forecast(self, days=7):
        """
        Get weather forecast data.
        
        Args:
            days: Number of days to forecast (max 7)
            
        Returns:
            List[Dict[str, Any]]: Forecast data
        """
        # Update if data is stale
        if time.time() - self.last_update > self.update_interval:
            self.update_weather()
            
        # Return requested number of days (up to what we have)
        return self.forecast_data[:min(days, len(self.forecast_data))]
        
    def get_uv_forecast(self, days=7):
        """
        Get UV index forecast.
        
        Args:
            days: Number of days to forecast
            
        Returns:
            List[Dict[str, Any]]: UV forecast data
        """
        forecast = self.get_forecast(days)
        return [{"date": day["date"], "uv_index": day["uv_index"]} for day in forecast]
        
    def get_precipitation_forecast(self, days=7):
        """
        Get precipitation forecast.
        
        Args:
            days: Number of days to forecast
            
        Returns:
            List[Dict[str, Any]]: Precipitation forecast data
        """
        forecast = self.get_forecast(days)
        return [{"date": day["date"], "precipitation": day["precipitation"], "conditions": day["conditions"]} for day in forecast]

# Test function
def test_weather_service():
    """Test the weather service."""
    logging.basicConfig(level=logging.INFO)
    
    config = {
        "location": "Miami, FL",
        "update_interval": 3600,
        "cache_file": "weather_test_cache.json"
    }
    
    service = WeatherService(config)
    
    # Test getting current weather
    weather = service.get_weather()
    print(f"Current weather in {config['location']}:")
    print(f"  Temperature: {weather.get('temperature')}\u00b0F")
    print(f"  Conditions: {weather.get('conditions')}")
    print(f"  Humidity: {weather.get('humidity')}%")
    print(f"  Wind Speed: {weather.get('wind_speed')} mph")
    print(f"  Precipitation: {weather.get('precipitation')} inches")
    print(f"  UV Index: {weather.get('uv_index')}")
    
    # Test getting forecast
    forecast = service.get_forecast(3)
    print("\
3-Day Forecast:")
    for day in forecast:
        print(f"  {day['date']}: {day['temperature']}\u00b0F, {day['conditions']}, UV: {day['uv_index']}")
    
    # Test getting UV forecast
    uv_forecast = service.get_uv_forecast(3)
    print("\
UV Forecast:")
    for day in uv_forecast:
        print(f"  {day['date']}: UV Index {day['uv_index']}")
    
    # Test getting precipitation forecast
    precip_forecast = service.get_precipitation_forecast(3)
    print("\
Precipitation Forecast:")
    for day in precip_forecast:
        print(f"  {day['date']}: {day['precipitation']} inches, {day['conditions']}")

if __name__ == "__main__":
    test_weather_service()
