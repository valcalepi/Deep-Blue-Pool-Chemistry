# config.py
import os
from dotenv import load_dotenv
from config import Config

load_dotenv()

class Config:
    """Configuration class for application settings and secrets."""
    
    # API keys
    WEATHER_API_KEY = os.environ.get('b5a290b128a44885bb7112326251305')
    
    # Database credentials
    DATABASE_USERNAME = os.environ.get('DATABASE_USERNAME')
    DATABASE_PASSWORD = os.environ.get('DATABASE_PASSWORD')
    
    # Email credentials
    EMAIL_USERNAME = os.environ.get('EMAIL_USERNAME')
    EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD')
    
    # Other configuration parameters
    DEFAULT_POOL_VOLUME = 15000
    DEFAULT_TIMEOUT = 10  # seconds
    MAX_REQUESTS_PER_MINUTE = 60
    
    @classmethod
    def validate_config(cls):
        """Validate that all required configuration values are present."""
        required_values = ['WEATHER_API_KEY', 'DATABASE_USERNAME', 'DATABASE_PASSWORD']
        missing = [key for key in required_values if not getattr(cls, key)]
        
        if missing:
            raise ValueError(f"Missing required configuration values: {', '.join(missing)}")