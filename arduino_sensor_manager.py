
#!/usr/bin/env python3
"""
Arduino Sensor Manager for Deep Blue Pool Chemistry

This module handles communication with Arduino-based sensors and processes
the sensor data for use in the application.
"""

import json
import time
import logging
import threading
import queue
from typing import Dict, Any, Optional, List, Tuple
import serial
import serial.tools.list_ports

# Configure logging
logger = logging.getLogger("arduino_sensor_manager")

class ArduinoSensorManager:
    """
    Manages communication with Arduino-based sensors and processes sensor data.
    
    This class handles:
    - Serial communication with Arduino
    - Parsing sensor data
    - Calibration of sensors
    - Real-time data streaming
    """
    
    def __init__(self, port: Optional[str] = None, baud_rate: int = 9600):
        """
        Initialize the Arduino Sensor Manager.
        
        Args:
            port: Serial port to connect to. If None, will attempt to auto-detect.
            baud_rate: Baud rate for serial communication.
        """
        self.port = port
        self.baud_rate = baud_rate
        self.serial_conn = None
        self.connected = False
        self.running = False
        self.read_thread = None
        self.data_queue = queue.Queue()
        self.latest_data = {}
        self.data_callbacks = []
        self.connection_callbacks = []
        
        # Initialize logger
        self.logger = logging.getLogger("arduino_sensor_manager")
        
    def connect(self) -> bool:
        """
        Connect to the Arduino.
        
        If port is not specified, attempts to auto-detect the Arduino port.
        
        Returns:
            bool: True if connection successful, False otherwise.
        """
        if self.connected:
            return True
            
        try:
            # If port not specified, try to auto-detect
            if self.port is None:
                self.port = self._find_arduino_port()
                if self.port is None:
                    self.logger.error("Could not auto-detect Arduino port")
                    return False
            
            # Connect to the serial port
            self.serial_conn = serial.Serial(self.port, self.baud_rate, timeout=1)
            time.sleep(2)  # Allow time for Arduino to reset
            
            # Check if connection is successful
            if self.serial_conn.is_open:
                self.connected = True
                self.logger.info(f"Connected to Arduino on port {self.port}")
                
                # Notify connection callbacks
                for callback in self.connection_callbacks:
                    callback(True)
                
                return True
            else:
                self.logger.error(f"Failed to connect to Arduino on port {self.port}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error connecting to Arduino: {e}")
            return False
    
    def disconnect(self) -> None:
        """
        Disconnect from the Arduino.
        """
        if self.connected and self.serial_conn:
            # Stop the read thread
            self.stop()
            
            # Close the serial connection
            self.serial_conn.close()
            self.connected = False
            self.logger.info("Disconnected from Arduino")
            
            # Notify connection callbacks
            for callback in self.connection_callbacks:
                callback(False)
    
    def start(self) -> bool:
        """
        Start reading data from the Arduino.
        
        Returns:
            bool: True if started successfully, False otherwise.
        """
        if not self.connected:
            if not self.connect():
                return False
        
        if self.running:
            return True
        
        # Start the read thread
        self.running = True
        self.read_thread = threading.Thread(target=self._read_data_thread)
        self.read_thread.daemon = True
        self.read_thread.start()
        self.logger.info("Started reading data from Arduino")
        return True
    
    def stop(self) -> None:
        """
        Stop reading data from the Arduino.
        """
        self.running = False
        if self.read_thread:
            self.read_thread.join(timeout=1.0)
            self.read_thread = None
        self.logger.info("Stopped reading data from Arduino")
    
    def send_command(self, command: Dict[str, Any]) -> bool:
        """
        Send a command to the Arduino.
        
        Args:
            command: Dictionary containing the command to send.
        
        Returns:
            bool: True if command sent successfully, False otherwise.
        """
        if not self.connected:
            self.logger.error("Cannot send command: Not connected to Arduino")
            return False
        
        try:
            # Convert command to JSON string
            command_str = json.dumps(command) + "\
"
            
            # Send command
            self.serial_conn.write(command_str.encode())
            self.logger.debug(f"Sent command to Arduino: {command}")
            return True
        except Exception as e:
            self.logger.error(f"Error sending command to Arduino: {e}")
            return False
    
    def calibrate_sensor(self, sensor: str, value: float) -> bool:
        """
        Calibrate a sensor.
        
        Args:
            sensor: Name of the sensor to calibrate (e.g., "pH", "orp").
            value: Calibration value.
        
        Returns:
            bool: True if calibration command sent successfully, False otherwise.
        """
        command = {
            "calibrate": sensor,
            "value": value
        }
        return self.send_command(command)
    
    def set_update_interval(self, interval_ms: int) -> bool:
        """
        Set the update interval for sensor readings.
        
        Args:
            interval_ms: Interval in milliseconds.
        
        Returns:
            bool: True if command sent successfully, False otherwise.
        """
        command = {
            "interval": interval_ms
        }
        return self.send_command(command)
    
    def get_latest_data(self) -> Dict[str, Any]:
        """
        Get the latest sensor data.
        
        Returns:
            dict: Dictionary containing the latest sensor data.
        """
        return self.latest_data.copy()
    
    def register_data_callback(self, callback) -> None:
        """
        Register a callback function to be called when new data is received.
        
        Args:
            callback: Function to call with the new data.
        """
        if callback not in self.data_callbacks:
            self.data_callbacks.append(callback)
    
    def unregister_data_callback(self, callback) -> None:
        """
        Unregister a data callback function.
        
        Args:
            callback: Function to unregister.
        """
        if callback in self.data_callbacks:
            self.data_callbacks.remove(callback)
    
    def register_connection_callback(self, callback) -> None:
        """
        Register a callback function to be called when connection status changes.
        
        Args:
            callback: Function to call with the connection status (True/False).
        """
        if callback not in self.connection_callbacks:
            self.connection_callbacks.append(callback)
    
    def unregister_connection_callback(self, callback) -> None:
        """
        Unregister a connection callback function.
        
        Args:
            callback: Function to unregister.
        """
        if callback in self.connection_callbacks:
            self.connection_callbacks.remove(callback)
    
    def list_available_ports(self) -> List[Tuple[str, str]]:
        """
        List all available serial ports.
        
        Returns:
            list: List of tuples (port, description).
        """
        ports = []
        for port in serial.tools.list_ports.comports():
            ports.append((port.device, port.description))
        return ports
    
    def _find_arduino_port(self) -> Optional[str]:
        """
        Attempt to auto-detect the Arduino port.
        
        Returns:
            str: Port name if found, None otherwise.
        """
        # Look for common Arduino identifiers in port descriptions
        arduino_identifiers = ["arduino", "uno", "mega", "nano", "leonardo", "ch340", "ft232", "cp210"]
        
        for port in serial.tools.list_ports.comports():
            # Check if any identifier is in the port description (case insensitive)
            if any(identifier in port.description.lower() for identifier in arduino_identifiers):
                return port.device
        
        # If no Arduino-specific port found, return the first available port if any
        ports = list(serial.tools.list_ports.comports())
        if ports:
            return ports[0].device
        
        return None
    
    def _read_data_thread(self) -> None:
        """
        Thread function to continuously read data from the Arduino.
        """
        self.logger.debug("Read thread started")
        
        while self.running:
            try:
                if self.serial_conn and self.serial_conn.is_open:
                    # Check if data is available
                    if self.serial_conn.in_waiting > 0:
                        # Read a line from the serial port
                        line = self.serial_conn.readline().decode('utf-8').strip()
                        
                        # Try to parse as JSON
                        try:
                            data = json.loads(line)
                            
                            # Update latest data
                            self.latest_data = data
                            
                            # Add to queue
                            self.data_queue.put(data)
                            
                            # Notify callbacks
                            for callback in self.data_callbacks:
                                try:
                                    callback(data)
                                except Exception as e:
                                    self.logger.error(f"Error in data callback: {e}")
                            
                            self.logger.debug(f"Received data: {data}")
                        except json.JSONDecodeError:
                            # Not JSON data, might be a debug message
                            if line:
                                self.logger.debug(f"Arduino message: {line}")
                else:
                    # Connection lost
                    if self.connected:
                        self.logger.warning("Serial connection lost")
                        self.connected = False
                        
                        # Notify connection callbacks
                        for callback in self.connection_callbacks:
                            callback(False)
                        
                        # Try to reconnect
                        time.sleep(1)
                        try:
                            self.serial_conn.open()
                            if self.serial_conn.is_open:
                                self.connected = True
                                self.logger.info("Reconnected to Arduino")
                                
                                # Notify connection callbacks
                                for callback in self.connection_callbacks:
                                    callback(True)
                        except Exception as e:
                            self.logger.error(f"Error reconnecting to Arduino: {e}")
                
                # Small delay to prevent high CPU usage
                time.sleep(0.01)
                
            except Exception as e:
                self.logger.error(f"Error reading data from Arduino: {e}")
                time.sleep(1)  # Wait before retrying
        
        self.logger.debug("Read thread stopped")


# Example usage
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create Arduino sensor manager
    arduino = ArduinoSensorManager()
    
    # List available ports
    print("Available ports:")
    for port, desc in arduino.list_available_ports():
        print(f"  {port}: {desc}")
    
    # Define callback function
    def on_data(data):
        print(f"Received data: pH={data.get('pH', 'N/A')}, "
              f"Temp={data.get('temp', 'N/A')}\u00b0C, "
              f"ORP={data.get('orp', 'N/A')}mV, "
              f"TDS={data.get('tds', 'N/A')}ppm, "
              f"Turbidity={data.get('turb', 'N/A')}NTU")
    
    # Register callback
    arduino.register_data_callback(on_data)
    
    # Connect and start reading
    if arduino.connect():
        arduino.start()
        
        try:
            # Run for 30 seconds
            print("Reading data for 30 seconds...")
            time.sleep(30)
        except KeyboardInterrupt:
            print("Interrupted by user")
        finally:
            # Stop and disconnect
            arduino.stop()
            arduino.disconnect()
    else:
        print("Failed to connect to Arduino")
