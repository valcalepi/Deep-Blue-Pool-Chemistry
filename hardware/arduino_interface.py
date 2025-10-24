import serial
import time

class ArduinoInterface:
    def __init__(self, port='COM3', baudrate=9600, timeout=2):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.connection = None

    def connect(self):
        try:
            self.connection = serial.Serial(self.port, self.baudrate, timeout=self.timeout)
            time.sleep(2)  # Allow time for Arduino to initialize
            print(f"Connected to Arduino on {self.port}")
        except serial.SerialException as e:
            print(f"Connection failed: {e}")

    def read_line(self):
        if self.connection and self.connection.in_waiting:
            return self.connection.readline().decode('utf-8').strip()
        return None

    def parse_data(self, line):
        try:
            parts = line.split(',')
            return {
                'pH': float(parts[0]),
                'chlorine': float(parts[1]),
                'temperature': float(parts[2])
            }
        except (IndexError, ValueError):
            return {}

    def get_sensor_data(self):
        line = self.read_line()
        if line:
            return self.parse_data(line)
        return {}
