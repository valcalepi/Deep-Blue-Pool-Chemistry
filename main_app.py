#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main application file for the Pool Controller system.
This module serves as the entry point and orchestrator for all pool control services.
"""

import sys
import time
import logging
import threading
import json
from datetime import datetime
import signal
from pathlib import Path

# Import custom services
try:
    from services.arduino_service import ArduinoService
    from services.weather_service import WeatherService
    from services.water_quality_analyzer import WaterQualityAnalyzer
    from services.secret_manager import SecretManager
except ImportError:
    # Add parent directory to path if running script directly
    sys.path.append(str(Path(__file__).parent.parent))
    
# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("pool_controller.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("PoolController")


class PoolController:
    """
    Main controller class for managing the pool systems.
    Coordinates between different services and handles the main application logic.
    """
    
    def __init__(self, config_path="config.json"):
        """
        Initialize the Pool Controller application.
        
        Args:
            config_path (str): Path to the configuration file
        """
        self.running = False
        self.logger = logger
        self.logger.info("Initializing Pool Controller")
        
        # Load configuration
        self.config = self._load_config(config_path)
        
        # Initialize Secret Manager
        self.secret_manager = SecretManager()
        
        # Initialize services
        self.arduino_service = ArduinoService(
            port=self.config.get("arduino", {}).get("port", "/dev/ttyUSB0"),
            baud_rate=self.config.get("arduino", {}).get("baud_rate", 9600)
        )
        
        self.weather_service = WeatherService(
            api_key=self.secret_manager.get_secret("weather_api_key"),
            location=self.config.get("weather", {}).get("location", "New York"),
            update_interval=self.config.get("weather", {}).get("update_interval", 3600)
        )
        
        self.water_analyzer = WaterQualityAnalyzer(
            arduino_service=self.arduino_service,
            thresholds=self.config.get("water_quality", {}).get("thresholds", {})
        )
        
        # Initialize state variables
        self.pump_active = False
        self.heater_active = False
        self.last_maintenance = datetime.now()
        self.schedule = self.config.get("schedule", {})
        
        # Set up signal handling for graceful shutdown
        signal.signal(signal.SIGINT, self._shutdown)
        signal.signal(signal.SIGTERM, self._shutdown)

    def _load_config(self, config_path):
        """
        Load configuration from JSON file.
        
        Args:
            config_path (str): Path to the configuration file
            
        Returns:
            dict: Configuration as a dictionary
        """
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
                self.logger.info(f"Configuration loaded successfully from {config_path}")
                return config
        except FileNotFoundError:
            self.logger.error(f"Configuration file not found at {config_path}")
            return {}
        except json.JSONDecodeError:
            self.logger.error(f"Error decoding JSON from the configuration file at {config_path}")
            return {}

    def run(self):
        """Main run loop for the pool controller."""
        self.running = True
        self.logger.info("Pool Controller is now running")

        try:
            while self.running:
                # Perform scheduled tasks
                self._perform_scheduled_tasks()
                # Sleep for a specified interval before next iteration
                time.sleep(300)  # Sleep for 5 minutes
        except Exception as e:
            self.logger.error(f"An error occurred: {e}")
        finally:
            self._shutdown()

    def _perform_scheduled_tasks(self):
        """Perform all scheduled tasks, such as monitoring and adjusting pool settings."""
        self.logger.debug("Performing scheduled tasks")
        
        try:
            # Monitor weather
            weather_forecast = self.weather_service.get_forecast(
                location=self.config.get("weather", {}).get("location", "auto:ip"), 
                force_refresh=False
            )
            
            # Check water quality and adjust as needed
            water_quality_data = self.water_analyzer.analyze()
            
            # Check if actions are needed based on weather and water quality
            self._adjust_pool_settings(weather_forecast, water_quality_data)
            
            # Log current status
            self._log_status()
            
        except Exception as e:
            self.logger.error(f"Error during scheduled task execution: {e}")

    def _adjust_pool_settings(self, weather_forecast, water_quality_data):
        """
        Adjust pool settings based on weather forecast and water quality data.
        
        Args:
            weather_forecast (dict): Weather forecast data
            water_quality_data (dict): Water quality analysis results
        """
        try:
            # Check if we need to adjust based on temperature
            if 'current' in weather_forecast and 'temp_c' in weather_forecast['current']:
                current_temp = weather_forecast['current']['temp_c']
                self.logger.info(f"Current temperature: {current_temp}°C")
                
                temp_threshold = self.config.get("temperature_control", {}).get("threshold", 25)
                if current_temp < temp_threshold and not self.heater_active:
                    self._activate_heater()
                elif current_temp >= temp_threshold and self.heater_active:
                    self._deactivate_heater()
            
            # Check if we need to adjust based on water quality
            if water_quality_data:
                # Example: adjust chlorine levels if needed
                if water_quality_data.get('chlorine', 0) < self.config.get("water_quality", {}).get("thresholds", {}).get("chlorine_min", 1):
                    self._increase_chlorine()
        except Exception as e:
            self.logger.error(f"Error adjusting pool settings: {e}")

    def _activate_heater(self):
        """Activate the pool heater."""
        try:
            self.logger.info("Activating pool heater")
            self.arduino_service.send_command("heater", "on")
            self.heater_active = True
        except Exception as e:
            self.logger.error(f"Failed to activate heater: {e}")

    def _deactivate_heater(self):
        """Deactivate the pool heater."""
        try:
            self.logger.info("Deactivating pool heater")
            self.arduino_service.send_command("heater", "off")
            self.heater_active = False
        except Exception as e:
            self.logger.error(f"Failed to deactivate heater: {e}")

    def _increase_chlorine(self):
        """Increase chlorine levels in the pool."""
        try:
            self.logger.info("Increasing chlorine levels")
            self.arduino_service.send_command("chlorine_pump", "on")
            # Run for a specified duration
            time.sleep(self.config.get("chlorine_control", {}).get("duration", 60))
            self.arduino_service.send_command("chlorine_pump", "off")
        except Exception as e:
            self.logger.error(f"Failed to adjust chlorine: {e}")
            # Ensure pump is turned off even if there's an error
            try:
                self.arduino_service.send_command("chlorine_pump", "off")
            except:
                pass

    def _log_status(self):
        """Log the current status of the pool system."""
        status = {
            "timestamp": datetime.now().isoformat(),
            "pump_active": self.pump_active,
            "heater_active": self.heater_active,
            "last_maintenance": self.last_maintenance.isoformat()
        }
        
        self.logger.info(f"Current system status: {json.dumps(status)}")
        
        # Save status to a file for external monitoring
        try:
            with open("pool_status.json", "w") as f:
                json.dump(status, f)
        except Exception as e:
            self.logger.error(f"Failed to save status: {e}")

    def _shutdown(self, signum=None, frame=None):
        """Shutdown all services gracefully."""
        self.logger.info("Shutting down Pool Controller...")
        self.running = False
        
        # Ensure all systems are in safe state
        try:
            self.arduino_service.send_command("heater", "off")
            self.arduino_service.send_command("pump", "off")
            self.arduino_service.send_command("chlorine_pump", "off")
        except Exception as e:
            self.logger.error(f"Error during shutdown safety procedures: {e}")
            
        # Shutdown individual services
        try:
            self.weather_service.shutdown()
        except Exception as e:
            self.logger.error(f"Error shutting down weather service: {e}")
            
        self.logger.info("Pool Controller has been shutdown successfully.")


if __name__ == "__main__":
    # Start the application
    controller = PoolController(config_path="config.json")
    controller.run()
