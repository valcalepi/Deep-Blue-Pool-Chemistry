# In services/secret_manager.py
import os
from dotenv import load_dotenv
import keyring

class SecretsManager:
    @staticmethod
    def get_api_key(service_name):
        # Try environment variables first
        key = os.getenv(f"{service_name.upper()}_API_KEY")
        if key:
            return key
            
        # Fall back to system keyring if available
        return keyring.get_password("deep_blue_pool", f"{service_name}_api_key")

# In weather_service.py
from services.secret_manager import SecretsManager

def __init__(self):
    self.api_key = SecretsManager.get_api_key("weather")
