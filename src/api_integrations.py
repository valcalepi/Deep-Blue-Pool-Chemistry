# api_integrations.py

"""
This module provides classes and functions for handling API integrations.
It includes classes for WeatherAPI, AddressVerificationAPI, and ArduinoInterface.
"""

import requests
import json
import logging
import serial
import time

# Configure the logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

class WeatherAPI:
    """
    A class to interact with the Weather API for retrieving weather data.
    """
    def __init__(self, api_key, base_url="https://www.weatherapi.com/my/"):
        """
        Initialize the WeatherAPI class.

        Args:
        - api_key (str): The API key for the Weather API.
        - base_url (str): The base URL for the Weather API. Defaults to "https://www.weatherapi.com/my/".
        """
        self.api_key = api_key
        self.base_url = base_url

    def get_weather_data(self, city):
        """
        Retrieve the current weather data for a given city.

        Args:
        - city (str): The name of the city.

        Returns:
        - dict: The weather data for the given city.
        """
        try:
            url = f"{self.base_url}weather?q={city}&appid={self.api_key}"
            response = requests.get(url)
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to retrieve weather data for {city}. Status code: {response.status_code}")
                return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Error retrieving weather data: {e}")
            return None


class ArduinoInterface:
    """
    A class to interact with an Arduino board for reading sensor data and sending commands.
    """
    def __init__(self, port, baudrate=9600, timeout=1):
        """
        Initialize the ArduinoInterface class.

        Args:
        - port (str): The port where the Arduino board is connected.
        - baudrate (int): The baudrate for the serial connection. Defaults to 9600.
        - timeout (int): The timeout for the serial connection. Defaults to 1.
        """
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial_connection = None

    def connect(self):
        """
        Establish a serial connection to the Arduino board.

        Returns:
        - bool: True if the connection is successful, False otherwise.
        """
        try:
            self.serial_connection = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=self.timeout
            )
            logger.info(f"Successfully connected to Arduino on port: {self.port}")
            return True
        except serial.SerialException as e:
            logger.error(f"Failed to connect to Arduino: {e}")
            return False

    def disconnect(self):
        """
        Close the serial connection to the Arduino board.
        """
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.close()
            logger.info(f"Disconnected from Arduino on port: {self.port}")

    def read_sensor_data(self, sensor_id):
        """
        Read data from a specific sensor connected to the Arduino.

        Args:
        - sensor_id (str): The ID of the sensor.

        Returns:
        - str: The sensor data.
        """
        if not self.serial_connection or not self.serial_connection.is_open:
            logger.error("Not connected to Arduino")
            return None

        try:
            self.serial_connection.write(f"read,{sensor_id}".encode())
            response = self.serial_connection.readline().decode().strip()
            logger.info(f"Received sensor data: {response}")
            return response
        except Exception as e:
            logger.error(f"Error reading sensor data: {e}")
            return None

    def send_command(self, command):
        """
        Send a command to the Arduino board.

        Args:
        - command (str): The command to be sent.

        Returns:
        - bool: True if the command is sent successfully, False otherwise.
        """
        if not self.serial_connection or not self.serial_connection.is_open:
            logger.error("Not connected to Arduino")
            return False

        try:
            self.serial_connection.write(command.encode())
            logger.info(f"Command sent to Arduino: {command}")
            return True
        except Exception as e:
            logger.error(f"Error sending command: {e}")
            return False


# Example usage
if __name__ == "__main__":
    # Weather API
    weather_api = WeatherAPI(api_key="6fff0780dfce4faa9b0170609250507")
    weather_data = weather_api.get_weather_data(city="New York")
    if weather_data:
        print(json.dumps(weather_data, indent=4))


    # Arduino Interface
    arduino = ArduinoInterface(port="COM3")
    if arduino.connect():
        sensor_data = arduino.read_sensor_data(sensor_id="pH")
        if sensor_data:
            print(f"Sensor data: {sensor_data}")
        arduino.disconnect()
    else:
        print("Failed to connect to Arduino")
