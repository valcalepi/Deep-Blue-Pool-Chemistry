# weather_api.py
import json
import requests
import logging
from constants import WEATHER_API_URL, WEATHER_API_KEY, LOCATION

# Configure logging for this module
logger = logging.getLogger('WeatherAPI')

def update_weather():
    """
    Update weather data with robust error handling
    """
    try:
        # Replace with your actual weather API endpoint and parameters
        response = requests.get(WEATHER_API_URL, params={
            'key': WEATHER_API_KEY,
            'q': LOCATION,
            'format': 'json'
        }, timeout=10)
        
        # Check if response is successful
        if response.status_code == 200:
            # Check if content is not empty
            if response.content:
                try:
                    # Try to parse JSON
                    weather_data = json.loads(response.content)
                    return weather_data
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse weather data: {e}")
                    logger.debug(f"Response content: {response.content[:100]}...")
                    return None
            else:
                logger.error("Weather API returned empty response")
                return None
        else:
            logger.error(f"Weather API request failed with status code: {response.status_code}")
            logger.debug(f"Response content: {response.content[:100]}...")
            return None
            
    except requests.RequestException as e:
        logger.error(f"Weather API request exception: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error in update_weather: {e}")
        return None
