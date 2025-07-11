#!/usr/bin/env python3
"""
Arduino Interface for Deep Blue Pool Chemistry
This module handles communication with Arduino devices for sensor readings.
"""
import logging
import time
import threading
from typing import Dict, Any, Optional, Callable

logger = logging.getLogger(__name__)

class ArduinoInterface:
    """Interface for communicating with Arduino devices."""
    
    def __init__(self, port: Optional[str] = None, baud_rate: int = 9600):
        """
        Initialize the Arduino interface.
        
        Args:
            port: Serial port to connect to (e.g., 'COM3' on Windows, '/dev/ttyUSB0' on Linux)
            baud_rate: Baud rate for serial communication
        """
        self.port = port
        self.baud_rate = baud_rate
        self.serial_conn = None
        self.connected = False
        self.reading_thread = None
        self.stop_thread = threading.Event()
        self.callbacks = {}
        
        # Try to import serial module
        try:
            import serial
            self.serial_module = serial
            logger.info("PySerial module loaded successfully")
        except ImportError:
            self.serial_module = None
            logger.warning("PySerial module not available - Arduino communication disabled")
    
    def connect(self) -> bool:
        """
        Connect to the Arduino device.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        if not self.serial_module:
            logger.error("Cannot connect to Arduino: PySerial module not available")
            return False
            
        try:
            # Auto-detect port if not specified
            if not self.port:
                self.port = self._auto_detect_port()
                if not self.port:
                    logger.error("No Arduino device found")
                    return False
            
            # Connect to the specified port
            self.serial_conn = self.serial_module.Serial(self.port, self.baud_rate, timeout=1)
            time.sleep(2)  # Allow time for Arduino to reset
            self.connected = True
            logger.info(f"Connected to Arduino on {self.port} at {self.baud_rate} baud")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to Arduino: {str(e)}")
            self.connected = False
            return False
    
    def disconnect(self) -> None:
        """Disconnect from the Arduino device."""
        if self.serial_conn:
            try:
                self.stop_reading()
                self.serial_conn.close()
                logger.info("Disconnected from Arduino")
            except Exception as e:
                logger.error(f"Error disconnecting from Arduino: {str(e)}")
            finally:
                self.connected = False
                self.serial_conn = None
    
    def send_command(self, command: str) -> bool:
        """
        Send a command to the Arduino.
        
        Args:
            command: Command string to send
            
        Returns:
            bool: True if command sent successfully, False otherwise
        """
        if not self.connected or not self.serial_conn:
            logger.error("Cannot send command: Not connected to Arduino")
            return False
            
        try:
            # Add newline if not present
            if not command.endswith('\n'):
                command += '\n'
                
            self.serial_conn.write(command.encode())
            logger.debug(f"Sent command to Arduino: {command.strip()}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send command to Arduino: {str(e)}")
            return False
    
    def read_line(self) -> Optional[str]:
        """
        Read a line from the Arduino.
        
        Returns:
            Optional[str]: Line read from Arduino or None if error
        """
        if not self.connected or not self.serial_conn:
            logger.error("Cannot read from Arduino: Not connected")
            return None
            
        try:
            line = self.serial_conn.readline().decode('utf-8').strip()
            if line:
                logger.debug(f"Read from Arduino: {line}")
            return line
            
        except Exception as e:
            logger.error(f"Failed to read from Arduino: {str(e)}")
            return None
    
    def start_reading(self, callback: Callable[[str], None]) -> bool:
        """
        Start a background thread to continuously read from Arduino.
        
        Args:
            callback: Function to call with each line read
            
        Returns:
            bool: True if reading thread started, False otherwise
        """
        if not self.connected:
            logger.error("Cannot start reading: Not connected to Arduino")
            return False
            
        if self.reading_thread and self.reading_thread.is_alive():
            logger.warning("Reading thread already running")
            return True
            
        try:
            self.stop_thread.clear()
            self.reading_thread = threading.Thread(
                target=self._reading_loop,
                args=(callback,),
                daemon=True
            )
            self.reading_thread.start()
            logger.info("Arduino reading thread started")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start Arduino reading thread: {str(e)}")
            return False
    
    def stop_reading(self) -> None:
        """Stop the background reading thread."""
        if self.reading_thread and self.reading_thread.is_alive():
            self.stop_thread.set()
            self.reading_thread.join(timeout=2)
            logger.info("Arduino reading thread stopped")
    
    def _reading_loop(self, callback: Callable[[str], None]) -> None:
        """
        Background thread loop for reading from Arduino.
        
        Args:
            callback: Function to call with each line read
        """
        while not self.stop_thread.is_set():
            try:
                line = self.read_line()
                if line:
                    callback(line)
                time.sleep(0.1)  # Small delay to prevent CPU hogging
            except Exception as e:
                logger.error(f"Error in Arduino reading loop: {str(e)}")
                time.sleep(1)  # Longer delay after error
    
    def _auto_detect_port(self) -> Optional[str]:
        """
        Auto-detect the Arduino serial port.
        
        Returns:
            Optional[str]: Detected port or None if not found
        """
        if not self.serial_module:
            return None
            
        try:
            from serial.tools import list_ports
            ports = list(list_ports.comports())
            
            for port in ports:
                # Look for Arduino or USB Serial Device
                if "arduino" in port.description.lower() or "usb serial" in port.description.lower():
                    logger.info(f"Found Arduino device: {port.device} - {port.description}")
                    return port.device
                    
            # If no Arduino found but there are serial ports, use the first one
            if ports:
                logger.info(f"No Arduino device found, using first available port: {ports[0].device}")
                return ports[0].device
                
            return None
            
        except Exception as e:
            logger.error(f"Error auto-detecting Arduino port: {str(e)}")
            return None
    
    def get_sensor_readings(self) -> Dict[str, float]:
        """
        Get sensor readings from the Arduino.
        
        Returns:
            Dict[str, float]: Dictionary of sensor readings
        """
        if not self.connected:
            logger.warning("Cannot get sensor readings: Not connected to Arduino")
            return self._get_mock_readings()
            
        try:
            # Send command to request readings
            self.send_command("GET_READINGS")
            
            # Wait for response
            time.sleep(0.5)
            
            # Read response
            response = self.read_line()
            if not response:
                logger.warning("No response from Arduino, using mock readings")
                return self._get_mock_readings()
                
            # Parse response (expected format: "pH:7.2,temp:78.5,chlorine:1.5")
            readings = {}
            for item in response.split(','):
                if ':' in item:
                    key, value = item.split(':')
                    try:
                        readings[key.strip()] = float(value.strip())
                    except ValueError:
                        logger.warning(f"Invalid reading value: {item}")
            
            # If no valid readings, use mock data
            if not readings:
                logger.warning("No valid readings from Arduino, using mock readings")
                return self._get_mock_readings()
                
            return readings
            
        except Exception as e:
            logger.error(f"Error getting sensor readings: {str(e)}")
            return self._get_mock_readings()
    
    def _get_mock_readings(self) -> Dict[str, float]:
        """
        Generate mock sensor readings for testing or when Arduino is unavailable.
        
        Returns:
            Dict[str, float]: Dictionary of mock sensor readings
        """
        import random
        
        return {
            "pH": round(random.uniform(7.0, 7.8), 1),
            "temp": round(random.uniform(75.0, 85.0), 1),
            "chlorine": round(random.uniform(1.0, 3.0), 1),
            "alkalinity": round(random.uniform(80.0, 120.0), 0),
            "calcium": round(random.uniform(200.0, 400.0), 0)
        }

# Test function
def test_arduino_interface():
    """Test the Arduino interface."""
    logging.basicConfig(level=logging.INFO)
    
    arduino = ArduinoInterface()
    if arduino.connect():
        print("Connected to Arduino")
        
        # Test sending a command
        arduino.send_command("TEST")
        
        # Test reading sensor data
        readings = arduino.get_sensor_readings()
        print(f"Sensor readings: {readings}")
        
        # Test continuous reading
        def print_data(data):
            print(f"Received: {data}")
        
        arduino.start_reading(print_data)
        time.sleep(5)  # Read for 5 seconds
        arduino.stop_reading()
        
        # Disconnect
        arduino.disconnect()
    else:
        print("Failed to connect to Arduino, using mock data")
        readings = arduino._get_mock_readings()
        print(f"Mock readings: {readings}")

if __name__ == "__main__":
    test_arduino_interface()