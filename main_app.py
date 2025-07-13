
import logging
import sys
import os
import json
from datetime import datetime
from flask import Flask, jsonify

# Import services
from services.arduino.arduino_interface import ArduinoService
from services.weather.weather_service import WeatherService
from services.database.database_connection import DatabaseService

# Import controllers
from app.controllers.pool_controller import PoolController

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("PoolController")

class PoolControllerApp:
    def __init__(self):
        self.config = {}
        self.load_config()
        self.app = Flask(__name__)
        self.setup_routes()
        
        # Initialize services
        self.arduino_service = None
        self.weather_service = None
        self.database_service = None
        self.pool_controller = None
        
        self.init_services()
        
    def load_config(self):
        """Load configuration from config.json file"""
        try:
            with open('config/config.json', 'r') as f:
                self.config = json.load(f)
            logger.info("Configuration loaded successfully from config.json")
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            self.config = {
                "pool": {"size": 15000, "type": "chlorine"},
                "arduino": {"port": "COM3", "baud_rate": 9600},
                "weather": {"location": "Florida", "update_interval": 3600}
            }
            
    def init_services(self):
        """Initialize all services"""
        logger.info("Initializing Pool Controller")
        
        # Initialize Arduino service
        try:
            self.arduino_service = ArduinoService(self.config["arduino"])
            logger.info("Arduino Service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Arduino Service: {e}")
            
        # Initialize Weather service
        try:
            self.weather_service = WeatherService(self.config["weather"])
            logger.info("Weather Service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Weather Service: {e}")
            
        # Initialize Database service
        try:
            self.database_service = DatabaseService()
            logger.info("Database Service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Database Service: {e}")
            
        # Initialize Pool Controller
        try:
            self.pool_controller = PoolController(
                self.arduino_service,
                self.weather_service,
                self.database_service,
                self.config["pool"]
            )
            logger.info("Pool Controller initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Pool Controller: {e}")
            
    def setup_routes(self):
        """Set up Flask routes"""
        @self.app.route('/api/status', methods=['GET'])
        def get_status():
            return jsonify({
                "system_state": {
                    "pump_running": False,
                    "heater_running": False,
                    "cleaning_mode": False,
                    "last_maintenance": datetime.now().isoformat(),
                    "last_chemical_check": datetime.now().isoformat()
                },
                "sensor_data": {
                    "water_temp": 78.5,
                    "ph_level": 7.2,
                    "chlorine_level": 3.0
                },
                "weather_data": {},
                "timestamp": datetime.now().isoformat()
            })
            
    def run(self):
        """Run the Flask application"""
        self.app.run(host='0.0.0.0', port=8080)
        
if __name__ == "__main__":
    app = PoolControllerApp()
    app.run()
