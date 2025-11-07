"""
Deep Blue Pool Chemistry Management System
Copyright (c) 2024 Michael Hayes. All rights reserved.

This software is proprietary and confidential.
Unauthorized copying, distribution, or use is strictly prohibited.

Owner: Michael Hayes
"""

"""
Arduino Interface Module for Deep Blue Pool Chemistry
Handles serial communication with Arduino sensors

Author: Michael Hayes
Version: 1.0
"""

import serial
import serial.tools.list_ports
import time
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class ArduinoInterface:
    """Real Arduino Interface with Serial Communication"""
    
    def __init__(self, port: Optional[str] = None, baudrate: int = 9600, timeout: float = 1.0):
        """
        Initialize Arduino interface
        
        Args:
            port: COM port (e.g., 'COM3' or '/dev/ttyUSB0')
            baudrate: Communication speed (default 9600)
            timeout: Read timeout in seconds
        """
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial_connection: Optional[serial.Serial] = None
        self.is_connected = False
        self.last_reading: Optional[str] = None
        self.last_reading_time: Optional[datetime] = None
        self.error_count = 0
        self.max_errors = 5
        self.total_readings = 0
        self.successful_readings = 0
        self.last_read_time = None  # Track last read time for rate limiting
        
    def connect(self) -> bool:
        """
        Establish connection to Arduino
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            if self.serial_connection and self.serial_connection.is_open:
                logger.info("Already connected to Arduino")
                return True
            
            if not self.port:
                logger.error("No port specified")
                return False
                
            logger.info(f"Attempting to connect to Arduino on {self.port} at {self.baudrate} baud")
            
            self.serial_connection = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=self.timeout,
                write_timeout=self.timeout
            )
            
            # Wait for Arduino to reset (Arduino resets when serial connection opens)
            logger.info("Waiting for Arduino to initialize...")
            time.sleep(2)
            
            # Clear any initial garbage data
            self.serial_connection.reset_input_buffer()
            self.serial_connection.reset_output_buffer()
            
            self.is_connected = True
            self.error_count = 0
            logger.info(f"[OK] Successfully connected to Arduino on {self.port}")
            
            return True
            
        except serial.SerialException as e:
            logger.error(f"[ERROR] Serial connection failed: {e}")
            self.is_connected = False
            return False
        except Exception as e:
            logger.error(f"[ERROR] Unexpected error connecting to Arduino: {e}")
            self.is_connected = False
            return False
    
    def disconnect(self) -> bool:
        """
        Close Arduino connection
        
        Returns:
            bool: True if disconnection successful
        """
        try:
            if self.serial_connection and self.serial_connection.is_open:
                self.serial_connection.close()
                self.is_connected = False
                logger.info("Arduino disconnected successfully")
                return True
            else:
                logger.info("Arduino was not connected")
                return True
        except Exception as e:
            logger.error(f"Error disconnecting Arduino: {e}")
            return False
    
    def read_data(self) -> Optional[str]:
        """
        Read data from Arduino
        
        Expected format: "PH:7.2,CL:2.5,TEMP:78.5,ALK:100"
        
        Returns:
            str: Raw data string or None if error/no data
        """
        if not self.is_connected or not self.serial_connection:
            return None
        
        try:
            if self.serial_connection.in_waiting > 0:
                line = self.serial_connection.readline()
                decoded_line = line.decode('utf-8', errors='ignore').strip()
                
                if decoded_line:
                    self.last_reading = decoded_line
                    self.last_reading_time = datetime.now()
                    self.error_count = 0
                    self.total_readings += 1
                    self.successful_readings += 1
                    
                    logger.debug(f"Arduino data received: {decoded_line}")
                    return decoded_line
            
            return None
                        
        except serial.SerialException as e:
            self.error_count += 1
            self.total_readings += 1
            logger.error(f"Serial read error: {e}")
            
            if self.error_count >= self.max_errors:
                logger.error(f"Too many errors ({self.error_count}), disconnecting Arduino")
                self.disconnect()
                
        except UnicodeDecodeError as e:
            logger.warning(f"Unicode decode error (ignoring): {e}")
            
        except Exception as e:
            self.error_count += 1
            self.total_readings += 1
            logger.error(f"Unexpected error reading Arduino: {e}")
            
        return None
    
    def write_data(self, data: str) -> bool:
        """
        Send data to Arduino
        
        Args:
            data: String to send to Arduino
            
        Returns:
            bool: True if write successful
        """
        if not self.is_connected or not self.serial_connection:
            logger.warning("Cannot write: Arduino not connected")
            return False




    def read_sensors(self) -> Optional[Dict[str, float]]:
        """
        Read and parse sensor data from Arduino
        
        Returns:
            dict: Parsed sensor readings or None if error
        """
        if not self.is_connected or not self.serial_connection:
            logger.error("Arduino not connected")
            return None
        
        # Increment total readings counter
        self.total_readings += 1
        
        try:
            # CRITICAL FIX: Rate limiting to prevent too-fast clicks
            import time
            current_time = time.time()
            if self.last_read_time is not None:
                time_since_last = current_time - self.last_read_time
                if time_since_last < 0.5:  # Minimum 500ms between reads
                    wait_time = 0.5 - time_since_last
                    logger.debug(f"Rate limiting: waiting {wait_time:.2f}s")
                    time.sleep(wait_time)
            
            self.last_read_time = time.time()
            
            # CRITICAL FIX: Clear input buffer before sending command
            # This prevents old data from clogging the buffer on fast clicks
            if self.serial_connection.in_waiting > 0:
                self.serial_connection.reset_input_buffer()
                logger.debug("Cleared input buffer before read")
            
            # Send READ command to Arduino
            logger.info("Sending READ command to Arduino...")
            self.serial_connection.write(b'READ\n')
            self.serial_connection.flush()
            
            # Wait for response (reduced timeout for faster response)
            import time
            start_time = time.time()
            timeout = 3  # Reduced from 5 to 3 seconds
            
            while time.time() - start_time < timeout:
                if self.serial_connection.in_waiting > 0:
                    line = self.serial_connection.readline()
                    raw_data = line.decode('utf-8', errors='ignore').strip()
                    
                    if raw_data:
                        logger.info(f"Received from Arduino: {raw_data}")
                        
                        # Parse the data
                        parsed = ArduinoDataParser.parse_reading(raw_data)
                        if not parsed:
                            logger.warning(f"Could not parse data: {raw_data}")
                            self.error_count += 1
                            return None
                        
                        # Map to app fields
                        mapped = ArduinoDataParser.map_to_app_fields(parsed)
                        logger.info(f"Mapped sensor data: {mapped}")
                        
                        # Increment successful readings counter
                        self.successful_readings += 1
                        self.last_reading = mapped
                        self.last_reading_time = datetime.now()
                        
                        return mapped
                
                time.sleep(0.05)  # Reduced from 0.1 to 0.05 for faster response
            
            logger.warning("Timeout waiting for Arduino response")
            self.error_count += 1
            return None
            
        except Exception as e:
            logger.error(f"Error reading sensors: {e}")
            self.error_count += 1
            return None

        
        try:
            message = f"{data}\n".encode('utf-8')
            self.serial_connection.write(message)
            logger.debug(f"Sent to Arduino: {data}")
            return True
        except Exception as e:
            logger.error(f"Error writing to Arduino: {e}")
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get connection status and statistics
        
        Returns:
            dict: Status information
        """
        success_rate = 0
        if self.total_readings > 0:
            success_rate = (self.successful_readings / self.total_readings) * 100
        
        return {
            'connected': self.is_connected,
            'port': self.port,
            'baudrate': self.baudrate,
            'last_reading': self.last_reading,
            'last_reading_time': self.last_reading_time.isoformat() if self.last_reading_time else None,
            'error_count': self.error_count,
            'total_readings': self.total_readings,
            'successful_readings': self.successful_readings,
            'success_rate': round(success_rate, 2)
        }
    
    @staticmethod
    def list_available_ports() -> List[Dict[str, str]]:
        """
        List all available serial ports
        
        Returns:
            list: List of port dictionaries with device, description, and hwid
        """
        try:
            ports = serial.tools.list_ports.comports()
            return [
                {
                    'device': p.device,
                    'description': p.description,
                    'hwid': p.hwid
                }
                for p in ports
            ]
        except Exception as e:
            logger.error(f"Error listing ports: {e}")
            return []
    
    @staticmethod
    def find_arduino_port() -> Optional[str]:
        """
        Automatically find Arduino port
        
        Returns:
            str: Port name if found, None otherwise
        """
        ports = ArduinoInterface.list_available_ports()
        
        # Look for common Arduino identifiers
        arduino_keywords = ['arduino', 'ch340', 'ch341', 'usb serial', 'usb-serial', 'ftdi']
        
        for port in ports:
            description_lower = port['description'].lower()
            hwid_lower = port['hwid'].lower()
            
            for keyword in arduino_keywords:
                if keyword in description_lower or keyword in hwid_lower:
                    logger.info(f"Found potential Arduino on {port['device']}: {port['description']}")
                    return port['device']
        
        # If no Arduino found, return first available port
        if ports:
            logger.info(f"No Arduino found, using first available port: {ports[0]['device']}")
            return ports[0]['device']
        
        return None


class ArduinoDataParser:
    """Parse and validate Arduino sensor data"""
    
    # Mapping from Arduino keys to application field names
    FIELD_MAPPING = {
        'PH': 'ph',
        'CL': 'free_chlorine',
        'FCL': 'free_chlorine',  # Alternative key
        'TCL': 'total_chlorine',
        'ALK': 'alkalinity',
        'HARD': 'calcium_hardness',
        'CALC': 'calcium_hardness',  # Alternative key
        'CYA': 'cyanuric_acid',
        'STAB': 'cyanuric_acid',  # Alternative key
        'SALT': 'salt',
        'BR': 'bromine',
        'BROM': 'bromine',  # Alternative key
        'TEMP': 'temperature',
        'TMP': 'temperature'  # Alternative key
    }
    
    # Valid ranges for each parameter
    VALID_RANGES = {
        'ph': (0.0, 14.0),
        'free_chlorine': (0.0, 20.0),
        'total_chlorine': (0.0, 20.0),
        'alkalinity': (0.0, 500.0),
        'calcium_hardness': (0.0, 1000.0),
        'cyanuric_acid': (0.0, 200.0),
        'salt': (0.0, 10000.0),
        'bromine': (0.0, 20.0),
        'temperature': (0.0, 120.0)
    }
    
    @staticmethod
    def parse_reading(data_string: str) -> Optional[Dict[str, float]]:
        """
        Parse Arduino data string
        
        Supported formats:
        - CSV: "PH:7.2,CL:2.5,TEMP:78.5,ALK:100"
        - Space-separated: "PH:7.2 CL:2.5 TEMP:78.5"
        - Tab-separated: "PH:7.2\tCL:2.5\tTEMP:78.5"
        
        Args:
            data_string: Raw data from Arduino
            
        Returns:
            dict: Parsed readings with Arduino keys, or None if invalid
        """
        if not data_string:
            return None
        
        readings = {}
        
        try:
            # Try multiple delimiters
            for delimiter in [',', '|', ' ', '\t', ';']:
                if delimiter in data_string:
                    items = data_string.split(delimiter)
                    break
            else:
                # No delimiter found, try single item
                items = [data_string]
            
            for item in items:
                item = item.strip()
                if ':' in item:
                    key, value = item.split(':', 1)
                    key = key.strip().upper()
                    value = value.strip()
                    
                    try:
                        readings[key] = float(value)
                    except ValueError:
                        logger.warning(f"Could not convert '{value}' to float for key '{key}'")
                        continue
            
            return readings if readings else None
            
        except Exception as e:
            logger.error(f"Error parsing Arduino data '{data_string}': {e}")
            return None
    
    @staticmethod
    def map_to_app_fields(readings: Dict[str, float]) -> Dict[str, float]:
        """
        Map Arduino keys to application field names
        
        Args:
            readings: Dictionary with Arduino keys (e.g., 'PH', 'CL')
            
        Returns:
            dict: Dictionary with application keys (e.g., 'ph', 'free_chlorine')
        """
        if not readings:
            return {}
        
        mapped = {}
        
        for arduino_key, value in readings.items():
            app_key = ArduinoDataParser.FIELD_MAPPING.get(arduino_key.upper())
            if app_key:
                mapped[app_key] = value
            else:
                logger.warning(f"Unknown Arduino key: {arduino_key}")
        
        return mapped
    
    @staticmethod
    def validate_reading(field: str, value: float) -> bool:
        """
        Validate if a reading is within acceptable range
        
        Args:
            field: Field name (e.g., 'ph', 'free_chlorine')
            value: Reading value
            
        Returns:
            bool: True if valid, False otherwise
        """
        if field not in ArduinoDataParser.VALID_RANGES:
            return True  # Unknown field, assume valid
        
        min_val, max_val = ArduinoDataParser.VALID_RANGES[field]
        return min_val <= value <= max_val
    
    @staticmethod
    def validate_readings(readings: Dict[str, float]) -> Dict[str, Any]:
        """
        Validate all readings and return validation report
        
        Args:
            readings: Dictionary of readings
            
        Returns:
            dict: Validation report with 'valid', 'warnings', and 'errors'
        """
        report = {
            'valid': True,
            'warnings': [],
            'errors': []
        }
        
        for field, value in readings.items():
            if not ArduinoDataParser.validate_reading(field, value):
                min_val, max_val = ArduinoDataParser.VALID_RANGES.get(field, (None, None))
                error_msg = f"{field}: {value} is out of range ({min_val}-{max_val})"
                report['errors'].append(error_msg)
                report['valid'] = False
        
        return report


class ArduinoCalibration:
    """Handle Arduino sensor calibration"""
    
    def __init__(self, arduino: ArduinoInterface):
        """
        Initialize calibration helper
        
        Args:
            arduino: ArduinoInterface instance
        """
        self.arduino = arduino
        self.calibration_data = {}
    
    def calibrate_ph(self, reference_ph: float, num_samples: int = 10) -> Dict[str, Any]:
        """
        Calibrate pH sensor
        
        Args:
            reference_ph: Known pH value of calibration solution
            num_samples: Number of samples to average
            
        Returns:
            dict: Calibration results
        """
        if not self.arduino.is_connected:
            return {'success': False, 'error': 'Arduino not connected'}
        
        samples = []
        
        for i in range(num_samples):
            data = self.arduino.read_data()
            if data:
                parsed = ArduinoDataParser.parse_reading(data)
                if parsed and 'PH' in parsed:
                    samples.append(parsed['PH'])
            time.sleep(0.5)
        
        if not samples:
            return {'success': False, 'error': 'No pH readings received'}
        
        measured_ph = sum(samples) / len(samples)
        offset = reference_ph - measured_ph
        
        result = {
            'success': True,
            'reference_ph': reference_ph,
            'measured_ph': round(measured_ph, 2),
            'offset': round(offset, 2),
            'samples': len(samples),
            'std_dev': round(self._calculate_std_dev(samples), 3)
        }
        
        self.calibration_data['ph'] = result
        return result
    
    @staticmethod
    def _calculate_std_dev(values: List[float]) -> float:
        """Calculate standard deviation"""
        if len(values) < 2:
            return 0.0
        
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / (len(values) - 1)
        return variance ** 0.5
    
    def get_calibration_data(self) -> Dict[str, Any]:
        """Get all calibration data"""
        return self.calibration_data.copy()
    
    def save_calibration(self, filename: str) -> bool:
        """Save calibration data to file"""
        try:
            import json
            with open(filename, 'w') as f:
                json.dump(self.calibration_data, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Error saving calibration: {e}")
            return False
    
    def load_calibration(self, filename: str) -> bool:
        """Load calibration data from file"""
        try:
            import json
            with open(filename, 'r') as f:
                self.calibration_data = json.load(f)
            return True
        except Exception as e:
            logger.error(f"Error loading calibration: {e}")
            return False


# Example usage and testing
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("=" * 60)
    print("Arduino Interface Module - Test Mode")
    print("=" * 60)
    
    # List available ports
    print("\n[PORT] Available Serial Ports:")
    ports = ArduinoInterface.list_available_ports()
    if ports:
        for i, port in enumerate(ports, 1):
            print(f"  {i}. {port['device']}")
            print(f"     Description: {port['description']}")
            print(f"     HWID: {port['hwid']}")
    else:
        print("  No serial ports found")
    
    # Try to find Arduino
    print("\n[SEARCH] Searching for Arduino...")
    arduino_port = ArduinoInterface.find_arduino_port()
    if arduino_port:
        print(f"  Found: {arduino_port}")
    else:
        print("  No Arduino detected")
    
    # Test data parsing
    print("\n🧪 Testing Data Parser:")
    test_data = [
        "PH:7.2,CL:2.5,TEMP:78.5,ALK:100",
        "PH:7.2 CL:2.5 TEMP:78.5",
        "PH:7.2\tCL:2.5\tTEMP:78.5"
    ]
    
    for data in test_data:
        print(f"\n  Input: {data}")
        parsed = ArduinoDataParser.parse_reading(data)
        print(f"  Parsed: {parsed}")
        if parsed:
            mapped = ArduinoDataParser.map_to_app_fields(parsed)
            print(f"  Mapped: {mapped}")
            validation = ArduinoDataParser.validate_readings(mapped)
            print(f"  Valid: {validation['valid']}")
    
    print("\n" + "=" * 60)
    print("Test complete!")
    print("=" * 60)