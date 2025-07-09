import json
import requests
import logging
import threading
import time
import os
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import jsonschema

# Configure logging
logger = logging.getLogger(__name__)

class WeatherService:
    """
    Service for retrieving weather data from external APIs
    and providing forecasts relevant to pool maintenance.
    """
    
    # Weather API schema for validation
    WEATHER_SCHEMA = {
        "type": "object",
        "required": ["current", "forecast"],
        "properties": {
            "current": {
                "type": "object",
                "required": ["temp_c", "condition"],
                "properties": {
                    "temp_c": {"type": "number"},
                    "condition": {
                        "type": "object",
                        "required": ["text"],
                        "properties": {
                            "text": {"type": "string"}
                        }
                    }
                }
            },
            "forecast": {
                "type": "object",
                "required": ["forecastday"],
                "properties": {
                    "forecastday": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "required": ["date", "day"],
                            "properties": {
                                "date": {"type": "string"},
                                "day": {
                                    "type": "object",
                                    "required": ["maxtemp_c", "mintemp_c", "avgtemp_c", "condition"],
                                    "properties": {
                                        "maxtemp_c": {"type": "number"},
                                        "mintemp_c": {"type": "number"},
                                        "avgtemp_c": {"type": "number"},
                                        "condition": {
                                            "type": "object",
                                            "required": ["text"],
                                            "properties": {
                                                "text": {"type": "string"}
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    
    def __init__(self, api_key: Optional[str] = None, cache_dir: str = "cache"):
        """
        Initialize the WeatherService.
        
        Args:
            api_key: API key for the weather service. If None, will try to get from environment.
            cache_dir: Directory to store cached weather data
        """
        self.api_key = api_key or os.environ.get("WEATHER_API_KEY")
        if not self.api_key:
            logger.warning("No weather API key provided. Weather functionality will be limited.")
        
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
        
        self.base_url = "https://api.weatherapi.com/v1"
        self.last_request_time = 0
        self.min_request_interval = 1.0  # Minimum time between requests in seconds
        self.forecast_cache = {}  # Initialize the forecast cache
        self.MAX_CACHE_SIZE = 100  # Maximum number of forecasts to cache
        
        # Start the background worker thread
        self.worker_running = True
        self.worker_thread = threading.Thread(target=self._run_worker, daemon=True)
        self.worker_thread.start()
        
        logger.info("WeatherService initialized")
    
    def _run_worker(self):
        """Background worker thread to periodically update weather data"""
        while self.worker_running:
            try:
                # Check if we need to update the forecast
                if self._should_update_forecast():
                    logger.info("Updating weather forecast in background")
                    self.get_forecast("auto:ip", force_refresh=True)
            except Exception as e:
                logger.error(f"Error in weather worker thread: {str(e)}")
            
            # Sleep for a while before checking again
            time.sleep(3600)  # Check once per hour
    
    def _should_update_forecast(self) -> bool:
        """Check if the forecast needs to be updated"""
        cache_file = os.path.join(self.cache_dir, "forecast_auto.json")
        
        if not os.path.exists(cache_file):
            return True
            
        try:
            with open(cache_file, "r") as f:
                data = json.load(f)
                
            # Check the timestamp
            timestamp = data.get("timestamp")
            if not timestamp:
                return True
                
            last_update = datetime.fromisoformat(timestamp)
            now = datetime.now()
            
            # Update if more than 6 hours old
            return (now - last_update) > timedelta(hours=6)
        except Exception as e:
            logger.error(f"Error checking forecast update: {str(e)}")
            return True
    
    def _rate_limit_request(self):
        """Ensure we do not exceed the API rate limit"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_request_interval:
            time.sleep(self.min_request_interval - time_since_last)
            
        self.last_request_time = time.time()
    
    def get_forecast(self, location: str, days: int = 3, force_refresh: bool = False) -> Dict[str, Any]:
        """
        Get weather forecast for a location.
        
        Args:
            location: Location string (city name, zip code, lat/long, or "auto:ip")
            days: Number of days to forecast (1-10)
            force_refresh: Whether to force a refresh from the API
            
        Returns:
            Dictionary containing weather forecast data
        """
        if not self.api_key:
            logger.error("No API key available for weather service")
            return {"error": "No API key available"}
            
        # Check cache first
        cache_key = f"forecast_{location.replace(':', '_').replace(' ', '_')}.json"
        cache_file = os.path.join(self.cache_dir, cache_key)
        
        if not force_refresh and os.path.exists(cache_file):
            try:
                return self.get_stored_forecast(cache_key)
            except Exception as e:
                logger.error(f"Error reading cached forecast: {str(e)}")
        
        # Make API request
        try:
            self._rate_limit_request()
            
            url = f"{self.base_url}/forecast.json"
            params = {
                "key": self.api_key,
                "q": location,
                "days": days,
                "aqi": "no",
                "alerts": "no"
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            # Validate response against schema
            jsonschema.validate(instance=data, schema=self.WEATHER_SCHEMA)
            
            # Add timestamp and cache the data
            data["timestamp"] = datetime.now().isoformat()
            
            with open(cache_file, "w") as f:
                json.dump(data, f)
                
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Weather API request failed: {str(e)}")
            return {"error": f"API request failed: {str(e)}"}
        except jsonschema.exceptions.ValidationError as e:
            logger.error(f"Weather API response validation failed: {str(e)}")
            return {"error": "Invalid API response format"}
        except Exception as e:
            logger.error(f"Unexpected error in get_forecast: {str(e)}")
            return {"error": f"Unexpected error: {str(e)}"}
    
    def get_stored_forecast(self, cache_file: str):
        """
        Retrieve stored forecast from cache file.
        
        Args:
            cache_file: Name of the cache file
            
        Returns:
            Dictionary containing cached forecast data, or None if not found
        """
        try:
            with open(os.path.join(self.cache_dir, cache_file), 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return None
        except Exception as e:
            logger.error(f"Error reading cached forecast: {str(e)}")
            return None

    def fetch_forecast(self, latitude, longitude):
        """
        Fetch current weather and forecast from the API.
        
        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            
        Returns:
            Dictionary containing forecast data
        """
        if not self.api_key:
            logger.error("No API key available for weather service")
            return {"error": "No API key available"}
            
        try:
            self._rate_limit_request()
            
            params = {
                "key": self.api_key,
                "q": f"{latitude},{longitude}",
                "days": 3,
                "aqi": "no",
                "alerts": "no"
            }
            
            response = requests.get(f"{self.base_url}/forecast.json", params=params)
            response.raise_for_status()
            
            data = response.json()
            
            # Validate response
            jsonschema.validate(instance=data, schema=self.WEATHER_SCHEMA)
            
            return data
        except Exception as e:
            logger.error(f"Error fetching forecast: {str(e)}")
            return {"error": f"Error fetching forecast: {str(e)}"}

    def get_current_conditions(self, location):
        """
        Get current weather conditions for a location.
        
        Args:
            location: Location string (can be city name, zip code, coordinates, etc.)
            
        Returns:
            Dictionary containing current weather conditions
        """
        try:
            forecast = self.get_forecast(location, days=1)
            if "error" in forecast:
                return forecast
            return forecast.get("current", {})
        except Exception as e:
            logger.error(f"Error getting current conditions: {str(e)}")
            return {"error": f"Error getting current conditions: {str(e)}"}

    def get_weather_forecast(self, latitude, longitude):
        """
        Get weather forecast for the specified coordinates.
        
        This method first checks the cache for a recent forecast.
        If not found, it queues a request to the API.
        
        Args:
            latitude (float): The latitude coordinate
            longitude (float): The longitude coordinate
            
        Returns:
            dict: The forecast data, or None if not available and request was queued
        """
        try:
            # Try to get stored forecast first
            cache_key = f"{latitude}_{longitude}"
            
            # Check if we have a cached forecast
            if cache_key in self.forecast_cache:
                cached_data = self.forecast_cache[cache_key]
                # Check if the cache is still valid (less than 1 hour old)
                if time.time() - cached_data['timestamp'] < 3600:  # 1 hour in seconds
                    logger.debug(f"Using cached forecast for {latitude}, {longitude}")
                    return cached_data['data']
            
            # If no valid cache is found, queue a request for a new forecast
            self._queue_request(latitude, longitude)
            return None
        except Exception as e:
            logger.error(f"Error in get_weather_forecast: {e}")
            return None

    def _queue_request(self, latitude, longitude):
        """
        Queue a request to fetch forecast data for the specified coordinates.
        
        Args:
            latitude (float): The latitude coordinate
            longitude (float): The longitude coordinate
        """
        try:
            # For simplicity, fetch directly instead of queuing
            forecast_data = self.fetch_forecast(latitude, longitude)
            
            # Cache the new forecast
            cache_key = f"{latitude}_{longitude}"
            self.forecast_cache[cache_key] = {
                'timestamp': time.time(),
                'data': forecast_data
            }
            
            # Clean up old cache entries if cache is too large
            if len(self.forecast_cache) > self.MAX_CACHE_SIZE:
                self._clean_cache()
                
            return forecast_data
        except Exception as e:
            logger.error(f"Error queuing request: {str(e)}")
            return None

    def _clean_cache(self):
        """
        Clean up old entries from the forecast cache.
        Removes the oldest 20% of entries.
        """
        try:
            # Sort cache keys by timestamp
            sorted_keys = sorted(
                self.forecast_cache.keys(),
                key=lambda k: self.forecast_cache[k]['timestamp']
            )
            
            # Remove oldest 20% of entries
            entries_to_remove = int(len(sorted_keys) * 0.2)
            for key in sorted_keys[:entries_to_remove]:
                del self.forecast_cache[key]
                
            logger.debug(f"Cleaned {entries_to_remove} entries from forecast cache")
        except Exception as e:
            logger.error(f"Error cleaning cache: {e}")

    def shutdown(self):
        """Shutdown the weather service and clean up resources."""
        logger.info("Shutting down weather service")
        self.worker_running = False
        if self.worker_thread and self.worker_thread.is_alive():
            self.worker_thread.join(timeout=5.0)
        logger.info("Weather service shutdown complete")

    # Set up logging
    logging.basicConfig(level=logging.DEBUG)
    
    # Create the weather service
    weather_service = WeatherService(api_key="your_api_key_here")
    
    try:
        # Get forecast for a location
        forecast = weather_service.get_forecast("90210")
        print("Forecast:", forecast)
        
        # Get current conditions for a location
        current = weather_service.get_current_conditions("90210")
        print("Current conditions:", current)
        
    finally:
        weather_service.shutdown()
