
import logging
import time

logger = logging.getLogger("arduino_service")

class ArduinoService:
    def __init__(self, config):
        """Initialize Arduino service with configuration"""
        logger.info("Arduino Service initialized")
        self.port = config.get("port", "COM3")
        self.baud_rate = config.get("baud_rate", 9600)
        self.connected = False
        self.serial = None
        
        try:
            import serial
            logger.info("Using serial module for Arduino communication")
            self.serial = serial.Serial(self.port, self.baud_rate, timeout=1)
            self.connected = True
        except ImportError:
            logger.warning("Serial module not found, using mock implementation")
        except Exception as e:
            logger.error(f"Failed to connect to Arduino: {e}")
            
    def send_command(self, command):
        """Send command to Arduino"""
        if not self.connected:
            logger.warning("Arduino not connected, command not sent")
            return False
            
        try:
            self.serial.write(command.encode())
            return True
        except Exception as e:
            logger.error(f"Failed to send command to Arduino: {e}")
            return False
            
    def read_data(self):
        """Read data from Arduino"""
        if not self.connected:
            logger.warning("Arduino not connected, returning mock data")
            return {
                "water_temp": 78.5,
                "ph_level": 7.2,
                "chlorine_level": 3.0
            }
            
        try:
            data = self.serial.readline().decode().strip()
            return self._parse_data(data)
        except Exception as e:
            logger.error(f"Failed to read data from Arduino: {e}")
            return None
            
    def _parse_data(self, data):
        """Parse data from Arduino"""
        try:
            parts = data.split(',')
            return {
                "water_temp": float(parts[0]),
                "ph_level": float(parts[1]),
                "chlorine_level": float(parts[2])
            }
        except Exception as e:
            logger.error(f"Failed to parse Arduino data: {e}")
            return None
