# utils/cache.py
from functools import wraps
import time

def timed_cache(max_age_seconds=300):
    """Cache decorator with expiration"""
    cache = {}
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create a key from the function arguments
            key = str(args) + str(kwargs)
            
            # Check if result is in cache and not expired
            if key in cache:
                result, timestamp = cache[key]
                if time.time() - timestamp < max_age_seconds:
                    return result
            
            # Call the function and cache the result
            result = func(*args, **kwargs)
            cache[key] = (result, time.time())
            return result
        return wrapper
    return decorator

# Using the cache in weather_service.py
from utils.cache import timed_cache

@timed_cache(max_age_seconds=1800)  # Cache for 30 minutes
def get_weather_forecast(self, location):
    # Make API call to weather service
    # This will only actually call the API once every 30 minutes
    # for the same location parameter
    pass
