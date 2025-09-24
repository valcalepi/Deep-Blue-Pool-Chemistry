#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Arduino Interface for Pool Management System

This module provides a communication interface between the Pool Management System
and Arduino hardware. It handles serial communication, data parsing, and error handling.
"""
import serial  # from pySerial: https://github.com/pyserial/pyserial via `pip install pyserial`
from time import sleep
import logging

logger = logging.getLogger(__name__)

class ArduinoInterface:
    """
    Arduino communication interface that manages serial connections and data exchange
    with Arduino hardware for the pool management system.
    """
    
    def __init__(self, port=None, baudrate=9600, cycle_delay=0.01):
        """
        Initialize the Arduino interface.
        
        Args:
            port (str, optional): Serial port to connect to. If None, auto-detection is attempted.
            baudrate (int, optional): Communication speed in bits per second. Defaults to 9600.
            cycle_delay (float, optional): Delay between read cycles in seconds. Defaults to 0.01.
        """
        logger.debug(f"Initializing ArduinoInterface with port={port}, baudrate={baudrate}")
        self.serial_connection = serial.Serial()
        self.serial_connection.port = port
        self.serial_connection.baudrate = baudrate
        self.cycle_delay = cycle_delay
        self.serial_buffer = ''
        self.read_delay = 0
        
        if port is not None and baudrate is not None:
            self.close()
            self.connect()
        else:
            if self.find_port(baudrate=baudrate):
                logger.info(f"Automatically found (PORT, BAUD): {(self.serial_connection.port, self.serial_connection.baudrate)}")
                print(f"Automatically found (PORT, BAUD): {(self.serial_connection.port, self.serial_connection.baudrate)}")
            else:
                logger.warning("Unable to automatically find (PORT, BAUD) combination.")
                print("Unable to automatically find (PORT, BAUD) combination.")
    
    def connect(self, port=None, baudrate=None):
        """
        Open a connection to the Arduino.
        
        Args:
            port (str, optional): Serial port to connect to. If None, uses the current port setting.
            baudrate (int, optional): Communication speed in bits per second. If None, uses the current baudrate setting.
            
        Returns:
            bool: True if connection is successful, False otherwise.
        """
        try:
            if port is not None and baudrate is not None:
                self.serial_connection.port = port
                self.serial_connection.baudrate = baudrate
            self.serial_connection.open()
            logger.info(f"Connected to Arduino on {self.serial_connection.port} at {self.serial_connection.baudrate} baud")
            return True
        except serial.SerialException as e:
            logger.error(f"Error connecting to Arduino: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error connecting to Arduino: {e}")
            return False
    
    def open(self, port=None, baudrate=None):
        """Alias for connect method for backward compatibility."""
        return self.connect(port, baudrate)
    
    def close(self, port=None, baudrate=None):
        """
        Close the connection to the Arduino.
        
        Args:
            port (str, optional): Serial port to close. If None, uses the current port setting.
            baudrate (int, optional): Communication speed in bits per second. If None, uses the current baudrate setting.
        """
        try:
            if port is not None and baudrate is not None:
                self.serial_connection.port = port
                self.serial_connection.baudrate = baudrate
            if self.serial_connection.is_open:
                self.serial_connection.close()
                logger.debug(f"Closed connection to Arduino on {self.serial_connection.port}")
        except Exception as e:
            logger.error(f"Error closing Arduino connection: {e}")
    
    def close_all(self, baudrate=None):
        """
        Close all possible serial connections.
        
        Args:
            baudrate (int, optional): Communication speed in bits per second to use when checking ports.
            
        Returns:
            int: Number of connections that failed to close.
        """
        unable = 0
        original_port = self.serial_connection.port
        original_baudrate = self.serial_connection.baudrate
        
        if baudrate is not None:
            self.serial_connection.baudrate = baudrate
            
        for port, _ in self.find_all_ports():
            self.serial_connection.port = port
            try:
                self.serial_connection.close()
            except Exception:
                unable += 1
                
        self.serial_connection.port = original_port
        self.serial_connection.baudrate = original_baudrate
        return unable
    
    def clear_buffer(self):
        """Clear the internal serial buffer."""
        self.serial_buffer = ''
    
    def find_port(self, baudrate=None):
        """
        Find and connect to the first available serial port.
        
        Args:
            baudrate (int, optional): Communication speed in bits per second to use when checking ports.
            
        Returns:
            bool: True if a port is found and connected, False otherwise.
        """
        if baudrate is not None:
            self.serial_connection.baudrate = baudrate
            
        prefixes = ['/dev/ttyACM', '/dev/ttyUSB', 'COM']
        port_list = [p+str(n) for p in prefixes for n in range(0, 100)]
        
        for port in port_list:
            self.close()
            try:
                self.connect(port, self.serial_connection.baudrate)
                return True
            except:
                pass
                
        self.serial_connection.port = None
        self.serial_connection.baudrate = None
        return False
    
    def find_all_ports(self, baudrate=None):
        """
        Find all available serial ports.
        
        Args:
            baudrate (int, optional): Communication speed in bits per second to use when checking ports.
            
        Returns:
            list: List of [port, baudrate] pairs that are available.
        """
        connections = []
        if baudrate is not None:
            self.serial_connection.baudrate = baudrate
            
        prefixes = ['/dev/ttyACM', '/dev/ttyUSB', 'COM']
        port_list = [p+str(n) for p in prefixes for n in range(0, 100)]
        
        for port in port_list:
            self.close()
            try:
                self.connect(port, self.serial_connection.baudrate)
                connections.append([self.serial_connection.port, self.serial_connection.baudrate])
            except:
                pass
                
        return connections
    
    def read(self):
        """
        Read data from the Arduino.
        
        Returns:
            str: Data read from the Arduino.
        """
        self.read_delay = 0
        self.clear_buffer()
        
        try:
            while self.serial_connection.in_waiting > 0:
                self.serial_buffer += self.serial_connection.read().decode('utf-8')
                if self.serial_connection.in_waiting <= 0:
                    sleep(self.cycle_delay)
                    self.read_delay += self.cycle_delay
            return self.serial_buffer
        except Exception as e:
            logger.error(f"Error reading from Arduino: {e}")
            return ""
    
    def waited(self):
        """
        Get the delay time during the last read operation.
        
        Returns:
            float: Seconds of delay during the last read.
        """
        return self.read_delay
    
    def write(self, input_str=''):
        """
        Write data to the Arduino.
        
        Args:
            input_str (str): Data to send to the Arduino.
            
        Returns:
            bool: True if write is successful, False otherwise.
        """
        try:
            output_str = str(input_str)
            if len(output_str) > 0:
                self.serial_connection.write(output_str.encode('utf-8'))
            return True
        except Exception as e:
            logger.error(f"Error writing to Arduino: {e}")
            return False
    
    def writeln(self, input_str=''):
        """
        Write a line of data to the Arduino (adds a newline character).
        
        Args:
            input_str (str): Data to send to the Arduino.
            
        Returns:
            bool: True if write is successful, False otherwise.
        """
        try:
            logger.debug(f"Writing to Arduino: {input_str}")
            return self.write(str(input_str) + '\n')
        except Exception as e:
            logger.error(f"Error writing line to Arduino: {e}")
            return False


if __name__ == '__main__':
    # Example usage when run directly
    logging.basicConfig(level=logging.DEBUG)
    arduino = ArduinoInterface()
    if arduino.serial_connection.is_open:
        arduino.writeln("Hello from Pool Management System")
        response = arduino.read()
        print(f"Arduino response: {response}")
        arduino.close()
