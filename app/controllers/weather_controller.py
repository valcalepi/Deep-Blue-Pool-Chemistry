# /controllers/weather_controller.py
import logging
from models.weather_model import WeatherModel
from utils.error_handler import handle_error
from utils.cache_manager import cache_result

class WeatherController:
    """Controller for weather-related operations."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.model = WeatherModel()
    
    @handle_error
    @cache_result(ttl=1800)  # Cache for 30 minutes
    def get_weather_forecast(self, location):
        """Retrieves weather forecast for a location."""
        self.logger.info(f"Retrieving weather forecast for {location}")
        return self.model.get_weather_forecast(location)
