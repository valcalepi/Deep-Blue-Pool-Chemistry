import requests
import logging
import json
import os
from datetime import datetime

logger = logging.getLogger("weather_service")

class WeatherService:
    def __init__(self, location="Florida", update_interval=3600):
        self.location = location
        self.update_interval = update_interval
        self.cache_file = "weather_cache.json"
        self.weather_data = {}

        logger.info(f"Weather Service initialized for {self.location} with update interval {self.update_interval}s")
        self._load_cache()
        self.update_weather()

    def _load_cache(self):
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, "r") as f:
                    self.weather_data = json.load(f)
                logger.info(f"Loaded weather data from cache, last updated: {self.weather_data.get('timestamp')}")
            except Exception as e:
                logger.warning(f"Failed to load weather cache: {e}")

    def update_weather(self):
        try:
            logger.info(f"Updating weather data for {self.location}")
            # Simulated weather data (replace with real API call if needed)
            self.weather_data = {
                "location": self.location,
                "temperature": "82°F",
                "humidity": "65%",
                "uv_index": "Moderate",
                "timestamp": str(datetime.now())
            }
            self._save_cache()
            logger.info(f"Weather data updated successfully for {self.location}")
        except Exception as e:
            logger.error(f"Failed to update weather data: {e}")

    def _save_cache(self):
        try:
            with open(self.cache_file, "w") as f:
                json.dump(self.weather_data, f, indent=4)
            logger.info(f"Saved weather data to cache file: {self.cache_file}")
        except Exception as e:
            logger.warning(f"Failed to save weather cache: {e}")

    def get_latest(self):
        return self.weather_data
