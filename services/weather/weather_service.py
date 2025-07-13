
import logging
import time
import threading

logger = logging.getLogger("weather_service")

class WeatherService:
    def __init__(self, config):
        """Initialize Weather service with configuration"""
        self.location = config.get("location", "Florida")
        self.update_interval = config.get("update_interval", 3600)  # Default: 1 hour
        self.weather_data = {}
        self.last_update = 0
        
        logger.info(f"Weather Service initialized for {self.location} with update interval {self.update_interval}s")
        
        try:
            import requests
            logger.info("Using requests module for weather data")
            self.requests = requests
        except ImportError:
            logger.warning("Requests module not found, using mock implementation")
            self.requests = None
            
        # Initial update
        self.update_weather()
        
        # Start update thread
        self.update_thread = threading.Thread(target=self._update_loop, daemon=True)
        self.update_thread.start()
        
    def update_weather(self):
        """Update weather data"""
        logger.info(f"Updating weather data for {self.location}")
        
        if self.requests is None:
            self._update_mock_data()
            return
            
        try:
            # This would be a real API call in production
            # response = self.requests.get(f"https://api.weather.com/current?location={self.location}")
            # self.weather_data = response.json()
            
            # Mock data for demonstration
            self._update_mock_data()
            
            self.last_update = time.time()
            logger.info(f"Weather data updated successfully for {self.location}")
        except Exception as e:
            logger.error(f"Failed to update weather data: {e}")
            
    def _update_mock_data(self):
        """Update with mock weather data"""
        import random
        
        self.weather_data = {
            "temperature": round(random.uniform(70, 95), 1),
            "humidity": round(random.uniform(40, 90), 1),
            "conditions": random.choice(["Sunny", "Partly Cloudy", "Cloudy", "Rainy"]),
            "wind_speed": round(random.uniform(0, 15), 1),
            "precipitation": round(random.uniform(0, 0.5), 2) if random.random() < 0.3 else 0
        }
        
    def _update_loop(self):
        """Background thread to update weather data periodically"""
        while True:
            time.sleep(self.update_interval)
            self.update_weather()
            
    def get_weather(self):
        """Get current weather data"""
        # Update if data is stale
        if time.time() - self.last_update > self.update_interval:
            self.update_weather()
            
        return self.weather_data
