#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Arduino Service Module

This module provides a service interface for communicating with Arduino
devices over a serial connection.
"""

import serial
import time
import logging

class ArduinoService:
    """
    Service class for communication with Arduino devices.
    
    This class handles the serial communication with an Arduino board,
    providing methods to send commands and receive data.
    """
    
    def __init__(self, port='/dev/ttyACM0', baud_rate=9600, timeout=2):
        """
        Initialize the Arduino service.
        
        Args:
            port (str): Serial port where Arduino is connected
            baud_rate (int): Communication baud rate
            timeout (int): Serial connection timeout in seconds
        """
        self.port = port
        self.baud_rate = baud_rate
        self.timeout = timeout
        self.serial = None
        self.logger = logging.getLogger(__name__)
    
    def connect(self):
        """
        Establish serial connection to the Arduino.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            self.serial = serial.Serial(
                port=self.port,
                baudrate=self.baud_rate,
                timeout=self.timeout
            )
            # Allow Arduino to reset
            time.sleep(2)
            self.logger.info(f"Connected to Arduino on {self.port}")
            return True
        except serial.SerialException as e:
            self.logger.error(f"Failed to connect to Arduino: {e}")
            return False
    
    def disconnect(self):
        """
        Close the serial connection.
        """
        if self.serial and self.serial.is_open:
            self.serial.close()
            self.logger.info("Disconnected from Arduino")
    
    def send_command(self, command):
        """
        Send a command to the Arduino.
        
        Args:
            command (str): Command to send
        
        Returns:
            bool: True if command sent successfully, False otherwise
        """
        if not self.serial or not self.serial.is_open:
            self.logger.error("Cannot send command: Not connected to Arduino")
            return False
        
        try:
            # Ensure command ends with newline
            if not command.endswith('\n'):
                command += '\n'
            
            # Send command as bytes
            self.serial.write(command.encode('utf-8'))
            self.serial.flush()
            self.logger.debug(f"Sent command: {command.strip()}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to send command: {e}")
            return False
    
    def read_response(self, timeout=5):
        """
        Read response from Arduino.
        
        Args:
            timeout (int): Maximum time to wait for response in seconds
        
        Returns:
            str: Response from Arduino or None if timeout
        """
        if not self.serial or not self.serial.is_open:
            self.logger.error("Cannot read response: Not connected to Arduino")
            return None
        
        try:
            # Wait for data to be available
            start_time = time.time()
            while self.serial.in_waiting == 0:
                if time.time() - start_time > timeout:
                    self.logger.warning("Timeout waiting for response")
                    return None
                time.sleep(0.1)
            
            # Read the data
            response = self.serial.readline().decode('utf-8').strip()
            self.logger.debug(f"Received response: {response}")
            return response
        except Exception as e:
            self.logger.error(f"Failed to read response: {e}")
            return None
    
    def send_and_receive(self, command, timeout=5):
        """
        Send a command and wait for response.
        
        Args:
            command (str): Command to send
            timeout (int): Maximum time to wait for response in seconds
        
        Returns:
            str: Response from Arduino or None if timeout or error
        """
        if self.send_command(command):
            return self.read_response(timeout)
        return None
    
    def get_sensor_reading(self, sensor_id):
        """
        Get reading from a specific sensor.
        
        Args:
            sensor_id (int): ID of the sensor to read
        
        Returns:
            str: Sensor reading or None if error
        """
        command = f"READ_SENSOR {sensor_id}"
        return self.send_and_receive(command)
    
    def set_pin_mode(self, pin, mode):
        """
        Set pin mode on Arduino.
        
        Args:
            pin (int): Pin number
            mode (str): 'INPUT', 'OUTPUT', or 'INPUT_PULLUP'
        
        Returns:
            bool: True if successful, False otherwise
        """
        command = f"SET_MODE {pin} {mode}"
        response = self.send_and_receive(command)
        return response == "OK"
    
    def digital_write(self, pin, value):
        """
        Write digital value to pin.
        
        Args:
            pin (int): Pin number
            value (int): 0 for LOW, 1 for HIGH
        
        Returns:
            bool: True if successful, False otherwise
        """
        command = f"DIGITAL_WRITE {pin} {value}"
        response = self.send_and_receive(command)
        return response == "OK"
    
    def digital_read(self, pin):
        """
        Read digital value from pin.
        
        Args:
            pin (int): Pin number
        
        Returns:
            int: 0 for LOW, 1 for HIGH, or None if error
        """
        command = f"DIGITAL_READ {pin}"
        response = self.send_and_receive(command)
        try:
            return int(response)
        except (ValueError, TypeError):
            self.logger.error(f"Invalid response for digital read: {response}")
            return None
    
    def analog_write(self, pin, value):
        """
        Write analog value to pin.
        
        Args:
            pin (int): Pin number
            value (int): Value between 0-255
        
        Returns:
            bool: True if successful, False otherwise
        """
        command = f"ANALOG_WRITE {pin} {value}"
        response = self.send_and_receive(command)
        return response == "OK"
    
    def analog_read(self, pin):
        """
        Read analog value from pin.
        
        Args:
            pin (int): Pin number
        
        Returns:
            int: Value between 0-1023, or None if error
        """
        command = f"ANALOG_READ {pin}"
        response = self.send_and_receive(command)
        try:
            return int(response)
        except (ValueError, TypeError):
            self.logger.error(f"Invalid response for analog read: {response}")
            return None


def main():
    """
    Example usage of ArduinoService.
    """
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create and connect to Arduino
    arduino = ArduinoService(port='/dev/ttyACM0', baud_rate=9600)
    if arduino.connect():
        # Set pin mode for LED
        arduino.set_pin_mode(13, 'OUTPUT')
        
        # Blink LED
        for _ in range(5):
            arduino.digital_write(13, 1)  # LED ON
            time.sleep(0.5)
            arduino.digital_write(13, 0)  # LED OFF
            time.sleep(0.5)
        
        # Read analog value
        value = arduino.analog_read(0)
        print(f"Analog value: {value}")
        
        # Disconnect
        arduino.disconnect()
