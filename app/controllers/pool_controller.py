
import logging
import time
import threading
from datetime import datetime

logger = logging.getLogger("PoolController")

class PoolController:
    def __init__(self, arduino_service, weather_service, database_service, config):
        """Initialize Pool Controller with services and configuration"""
        self.arduino_service = arduino_service
        self.weather_service = weather_service
        self.database_service = database_service
        self.config = config
        
        self.pool_size = config.get("size", 15000)  # Gallons
        self.pool_type = config.get("type", "chlorine")
        
        self.system_state = {
            "pump_running": False,
            "heater_running": False,
            "cleaning_mode": False,
            "last_maintenance": datetime.now().isoformat(),
            "last_chemical_check": datetime.now().isoformat()
        }
        
        # Start monitoring thread
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        logger.info("Starting monitoring loop")
        self.monitor_thread.start()
        logger.info("Monitoring thread started successfully")
        
    def _monitoring_loop(self):
        """Background thread for continuous monitoring"""
        while self.monitoring:
            try:
                # Read sensor data
                sensor_data = self.arduino_service.read_data()
                
                # Get weather data
                weather_data = self.weather_service.get_weather()
                
                # Log data to database
                if sensor_data:
                    self.database_service.log_sensor_data(sensor_data)
                
                # Check conditions and adjust as needed
                self._check_conditions(sensor_data, weather_data)
                
                # Sleep for a bit
                time.sleep(60)  # Check every minute
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(60)  # Wait a bit before retrying
                
    def _check_conditions(self, sensor_data, weather_data):
        """Check conditions and adjust pool settings as needed"""
        if not sensor_data:
            return
            
        # Check water temperature
        water_temp = sensor_data.get("water_temp", 0)
        outside_temp = weather_data.get("temperature", 0)
        
        # Heater control
        if water_temp < 78 and outside_temp < 80:
            self._start_heater()
        elif water_temp > 82 or outside_temp > 85:
            self._stop_heater()
            
        # Check pH level
        ph_level = sensor_data.get("ph_level", 7.0)
        if ph_level < 7.0:
            logger.info("pH level low, recommend adding pH increaser")
        elif ph_level > 7.8:
            logger.info("pH level high, recommend adding pH decreaser")
            
        # Check chlorine level
        chlorine_level = sensor_data.get("chlorine_level", 0)
        if chlorine_level < 1.0:
            logger.info("Chlorine level low, recommend adding chlorine")
        elif chlorine_level > 5.0:
            logger.info("Chlorine level high, recommend reducing chlorine")
            
    def _start_heater(self):
        """Start the pool heater"""
        if not self.system_state["heater_running"]:
            logger.info("Starting pool heater")
            self.arduino_service.send_command("HEATER:ON")
            self.system_state["heater_running"] = True
            self.database_service.log_maintenance("Heater started", "Automatic temperature control")
            
    def _stop_heater(self):
        """Stop the pool heater"""
        if self.system_state["heater_running"]:
            logger.info("Stopping pool heater")
            self.arduino_service.send_command("HEATER:OFF")
            self.system_state["heater_running"] = False
            self.database_service.log_maintenance("Heater stopped", "Automatic temperature control")
            
    def start_pump(self):
        """Start the pool pump"""
        logger.info("Starting pool pump")
        self.arduino_service.send_command("PUMP:ON")
        self.system_state["pump_running"] = True
        self.database_service.log_maintenance("Pump started", "Manual control")
        return True
        
    def stop_pump(self):
        """Stop the pool pump"""
        logger.info("Stopping pool pump")
        self.arduino_service.send_command("PUMP:OFF")
        self.system_state["pump_running"] = False
        self.database_service.log_maintenance("Pump stopped", "Manual control")
        return True
        
    def start_cleaning(self):
        """Start cleaning mode"""
        logger.info("Starting cleaning mode")
        self.arduino_service.send_command("CLEAN:ON")
        self.system_state["cleaning_mode"] = True
        self.database_service.log_maintenance("Cleaning mode started", "Manual control")
        return True
        
    def stop_cleaning(self):
        """Stop cleaning mode"""
        logger.info("Stopping cleaning mode")
        self.arduino_service.send_command("CLEAN:OFF")
        self.system_state["cleaning_mode"] = False
        self.database_service.log_maintenance("Cleaning mode stopped", "Manual control")
        return True
        
    def get_status(self):
        """Get current system status"""
        sensor_data = self.arduino_service.read_data() or {}
        weather_data = self.weather_service.get_weather() or {}
        
        return {
            "system_state": self.system_state,
            "sensor_data": sensor_data,
            "weather_data": weather_data,
            "timestamp": datetime.now().isoformat()
        }
        
    def add_chemical(self, chemical, amount):
        """Log chemical addition"""
        logger.info(f"Adding {amount} of {chemical}")
        self.database_service.log_chemical_addition(chemical, amount, "Manual addition")
        self.system_state["last_chemical_check"] = datetime.now().isoformat()
        return True
        
    def perform_maintenance(self, action, details=""):
        """Log maintenance action"""
        logger.info(f"Performing maintenance: {action}")
        self.database_service.log_maintenance(action, details, "Manual")
        self.system_state["last_maintenance"] = datetime.now().isoformat()
        return True
