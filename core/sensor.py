import serial

class SensorManager:
    def __init__(self, port='COM3', baudrate=9600):
        self.port = port
        self.baudrate = baudrate
        self.connection = None

    def connect(self):
        self.connection = serial.Serial(self.port, self.baudrate, timeout=2)

    def read_data(self):
        if self.connection and self.connection.in_waiting:
            line = self.connection.readline().decode('utf-8').strip()
            return self._parse_sensor_data(line)
        return {}

    def _parse_sensor_data(self, line):
        try:
            parts = line.split(',')
            return {
                'pH': float(parts[0]),
                'chlorine': float(parts[1]),
                'temperature': float(parts[2])
            }
        except (IndexError, ValueError):
            return {}
