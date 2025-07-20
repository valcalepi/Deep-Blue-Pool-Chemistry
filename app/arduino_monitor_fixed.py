
"""
Arduino Monitor Module for Deep Blue Pool Chemistry Application
This module handles communication with Arduino devices for sensor data.
"""

import logging
import threading
import time
import random
import re
import serial
import serial.tools.list_ports

logger = logging.getLogger("DeepBluePoolApp")

class ArduinoMonitor:
    """Arduino monitor for reading sensor data."""
    
    def __init__(self):
        """Initialize the Arduino monitor."""
        self.serial_port = None
        self.is_connected = False
        self.is_monitoring = False
        self.monitor_thread = None
        self.data_callback = None
        self.available_ports = []
        self.update_available_ports()
        self.buffer = ""
    
    def update_available_ports(self):
        """Update the list of available serial ports."""
        try:
            self.available_ports = [port.device for port in serial.tools.list_ports.comports()]
            logger.info(f"Available ports: {self.available_ports}")
        except Exception as e:
            logger.error(f"Error getting available ports: {e}")
            self.available_ports = []
        return self.available_ports
    
    def connect(self, port, baud_rate=9600):
        """
        Connect to the Arduino.
        
        Args:
            port: Serial port
            baud_rate: Baud rate
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            self.serial_port = serial.Serial(port, baud_rate, timeout=1)
            self.is_connected = True
            logger.info(f"Connected to Arduino on port {port}")
            return True
        except Exception as e:
            logger.error(f"Error connecting to Arduino: {e}")
            self.is_connected = False
            return False
    
    def disconnect(self):
        """Disconnect from the Arduino."""
        if self.is_connected:
            self.stop_monitoring()
            try:
                self.serial_port.close()
            except Exception as e:
                logger.error(f"Error closing serial port: {e}")
            self.is_connected = False
            logger.info("Disconnected from Arduino")
    
    def start_monitoring(self, callback):
        """
        Start monitoring Arduino data.
        
        Args:
            callback: Function to call with received data
        """
        if not self.is_connected:
            logger.error("Cannot start monitoring: Not connected to Arduino")
            return False
        
        if self.is_monitoring:
            logger.warning("Already monitoring Arduino")
            return True
        
        self.data_callback = callback
        self.is_monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        logger.info("Started monitoring Arduino")
        return True
    
    def stop_monitoring(self):
        """Stop monitoring Arduino data."""
        if self.is_monitoring:
            self.is_monitoring = False
            if self.monitor_thread:
                self.monitor_thread.join(timeout=1)
            logger.info("Stopped monitoring Arduino")
    
    def _monitor_loop(self):
        """Monitor loop for reading Arduino data."""
        while self.is_monitoring and self.is_connected:
            try:
                if self.serial_port.in_waiting > 0:
                    # Read data from serial port
                    data = self.serial_port.read(self.serial_port.in_waiting).decode('utf-8', errors='ignore')
                    self.buffer += data
                    
                    # Process complete lines
                    lines = self.buffer.split('\
')
                    self.buffer = lines.pop()  # Keep the last incomplete line in the buffer
                    
                    for line in lines:
                        line = line.strip()
                        if line:
                            if self.data_callback:
                                self.data_callback(line)
            except Exception as e:
                logger.error(f"Error reading from Arduino: {e}")
                self.is_monitoring = False
                self.is_connected = False
            time.sleep(0.1)
    
    def send_command(self, command):
        """
        Send a command to the Arduino.
        
        Args:
            command: Command to send
        
        Returns:
            True if command sent successfully, False otherwise
        """
        if not self.is_connected:
            logger.error("Cannot send command: Not connected to Arduino")
            return False
        
        try:
            self.serial_port.write(f"{command}\
".encode('utf-8'))
            logger.info(f"Sent command to Arduino: {command}")
            return True
        except Exception as e:
            logger.error(f"Error sending command to Arduino: {e}")
            return False
    
    def simulate_data(self):
        """Simulate Arduino data for testing."""
        # Simulate pH, temperature, and ORP readings
        ph = round(random.uniform(7.0, 8.0), 2)
        temp = round(random.uniform(75.0, 85.0), 1)
        orp = round(random.uniform(650, 750))
        
        # Choose a random format
        formats = [
            f"pH:{ph},Temp:{temp},ORP:{orp}",  # Format 1: CSV
            f"{{'pH': {ph}, 'Temp': {temp}, 'ORP': {orp}}}",  # Format 2: JSON-like
            f"{orp}",  # Format 3: Simple ORP value
            f"Reading: pH: {ph}, Temperature: {temp}, ORP: {orp}"  # Format 4: Text with values
        ]
        
        data = formats[0]  # Use the most common format
        
        if self.data_callback:
            self.data_callback(data)
        
        return data
