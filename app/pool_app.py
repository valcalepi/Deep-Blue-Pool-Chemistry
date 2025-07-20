
"""
Deep Blue Pool Chemistry Application

This application provides a comprehensive pool chemistry management system
with Arduino integration, weather forecasting, and customer management.
"""

import os
import sys
import json
import logging
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, StringVar, DoubleVar, IntVar
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import threading
import time
import random
import re

try:
    import serial
    import serial.tools.list_ports
    SERIAL_AVAILABLE = True
except ImportError:
    SERIAL_AVAILABLE = False
    print("Warning: pyserial not installed. Arduino functionality will be simulated.")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("pool_chemistry.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("DeepBluePoolApp")

# Create necessary directories
os.makedirs("data", exist_ok=True)

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
        if SERIAL_AVAILABLE:
            self.available_ports = [port.device for port in serial.tools.list_ports.comports()]
        else:
            # Simulate some ports for testing
            self.available_ports = ["SIM_PORT_1", "SIM_PORT_2", "COM3"]
        
        logger.info(f"Available ports: {self.available_ports}")
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
        if not SERIAL_AVAILABLE or port.startswith("SIM_"):
            # Simulate connection
            self.is_connected = True
            logger.info(f"Simulated connection to Arduino on port {port}")
            return True
            
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
            if SERIAL_AVAILABLE and self.serial_port:
                self.serial_port.close()
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
                if not SERIAL_AVAILABLE or self.serial_port is None:
                    # Simulate data every 2 seconds
                    time.sleep(2)
                    self.simulate_data()
                    continue
                    
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
        
        if not SERIAL_AVAILABLE or self.serial_port is None:
            logger.info(f"Simulated sending command to Arduino: {command}")
            return True
        
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
        # Simulate ORP readings with trailing curly brace (like your actual Arduino)
        orp = round(random.uniform(450, 750))
        
        # Format like your actual Arduino data: "483}"
        data = f"{orp}}}"
        
        if self.data_callback:
            self.data_callback(data)
        
        return data

class WeatherService:
    """Weather service for fetching weather data."""
    
    def __init__(self, api_key="", default_zip="10001"):
        """
        Initialize the weather service.
        
        Args:
            api_key: API key for weather service
            default_zip: Default ZIP code
        """
        self.api_key = api_key
        self.default_zip = default_zip
    
    def get_weather(self, zip_code=None):
        """
        Get weather data for a ZIP code.
        
        Args:
            zip_code: ZIP code to get weather for
        
        Returns:
            Weather data dictionary
        """
        if not zip_code:
            zip_code = self.default_zip
        
        # In a real application, this would make an API call
        # For this simple version, we'll just return simulated data
        return self._simulate_weather_data(zip_code)
    
    def _simulate_weather_data(self, zip_code):
        """
        Simulate weather data for testing.
        
        Args:
            zip_code: ZIP code to simulate weather for
        
        Returns:
            Simulated weather data dictionary
        """
        # Generate random weather data
        return {
            "location": f"City for {zip_code}",
            "temperature": round(random.uniform(70, 85), 1),
            "humidity": round(random.uniform(40, 60)),
            "conditions": random.choice(["Sunny", "Partly Cloudy", "Cloudy", "Light Rain"]),
            "wind_speed": round(random.uniform(0, 15)),
            "wind_direction": random.choice(["N", "NE", "E", "SE", "S", "SW", "W", "NW"]),
            "pressure": round(random.uniform(1000, 1020)),
            "forecast": [
                {
                    "day": "Today",
                    "high": round(random.uniform(75, 90)),
                    "low": round(random.uniform(60, 75)),
                    "conditions": random.choice(["Sunny", "Partly Cloudy", "Cloudy", "Light Rain"])
                },
                {
                    "day": "Tomorrow",
                    "high": round(random.uniform(75, 90)),
                    "low": round(random.uniform(60, 75)),
                    "conditions": random.choice(["Sunny", "Partly Cloudy", "Cloudy", "Light Rain"])
                },
                {
                    "day": "Day 3",
                    "high": round(random.uniform(75, 90)),
                    "low": round(random.uniform(60, 75)),
                    "conditions": random.choice(["Sunny", "Partly Cloudy", "Cloudy", "Light Rain"])
                }
            ]
        }

class DatabaseService:
    """Database service for storing and retrieving data."""
    
    def __init__(self, data_dir="data"):
        """
        Initialize the database service.
        
        Args:
            data_dir: Directory to store data files
        """
        logger.info(f"Initializing Database Service with path: {data_dir}")
        self.data_dir = data_dir
        self.customers_file = os.path.join(data_dir, "customers.json")
        self.readings_file = os.path.join(data_dir, "readings.json")
        
        # Create data directory if it doesn't exist
        os.makedirs(data_dir, exist_ok=True)
        
        # Initialize data
        self.customers = []
        self.readings = []
        
        # Load data
        self._load_data()
    
    def _load_data(self):
        """Load data from files."""
        # Load customers
        if os.path.exists(self.customers_file):
            try:
                with open(self.customers_file, 'r') as f:
                    self.customers = json.load(f)
            except Exception as e:
                logger.error(f"Error loading customers data: {e}")
                # Create sample customers as fallback
                self._create_sample_customers()
        else:
            # Create sample customers
            self._create_sample_customers()
        
        # Load readings
        if os.path.exists(self.readings_file):
            try:
                with open(self.readings_file, 'r') as f:
                    self.readings = json.load(f)
            except Exception as e:
                logger.error(f"Error loading readings data: {e}")
                # Create sample readings as fallback
                self.readings = self._generate_sample_readings()
                self._save_readings()
        else:
            # Create sample readings
            self.readings = self._generate_sample_readings()
            self._save_readings()
    
    def _create_sample_customers(self):
        """Create sample customers."""
        self.customers = [
            {
                "id": 1,
                "name": "John Smith",
                "address": "123 Main St",
                "phone": "555-1234",
                "email": "john@example.com",
                "pools": [
                    {
                        "id": 1,
                        "type": "In-ground",
                        "volume": 20000,
                        "volume_unit": "gallons",
                        "surface": "Plaster"
                    }
                ]
            },
            {
                "id": 2,
                "name": "Jane Doe",
                "address": "456 Oak Ave",
                "phone": "555-5678",
                "email": "jane@example.com",
                "pools": [
                    {
                        "id": 2,
                        "type": "Above-ground",
                        "volume": 10000,
                        "volume_unit": "gallons",
                        "surface": "Vinyl"
                    }
                ]
            }
        ]
        self._save_customers()
    
    def _generate_sample_readings(self):
        """Generate sample readings for testing."""
        readings = []
        
        # Generate readings for the past 30 days
        for i in range(30):
            date = datetime.now() - timedelta(days=i)
            date_str = date.strftime("%Y-%m-%d")
            
            # Generate readings for each customer
            for customer in self.customers:
                for pool in customer.get("pools", []):
                    readings.append({
                        "id": len(readings) + 1,
                        "customer_id": customer["id"],
                        "pool_id": pool["id"],
                        "date": date_str,
                        "ph": round(random.uniform(7.0, 8.0), 1),
                        "free_chlorine": round(random.uniform(1.0, 3.0), 1),
                        "total_alkalinity": round(random.uniform(80, 120)),
                        "calcium_hardness": round(random.uniform(200, 400)),
                        "cyanuric_acid": round(random.uniform(30, 50)),
                        "salt": round(random.uniform(2700, 3400)),
                        "temperature": round(random.uniform(75, 85), 1)
                    })
        return readings
    
    def _save_customers(self):
        """Save customers data to file."""
        try:
            with open(self.customers_file, 'w') as f:
                json.dump(self.customers, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving customers: {e}")
    
    def _save_readings(self):
        """Save readings data to file."""
        try:
            with open(self.readings_file, 'w') as f:
                json.dump(self.readings, f, indent=2)
            logger.info(f"Saved readings data to {self.readings_file}")
        except Exception as e:
            logger.error(f"Error saving readings: {e}")
    
    def get_all_customers(self):
        """
        Get all customers.
        
        Returns:
            List of customer dictionaries
        """
        return self.customers
    
    def get_customer(self, customer_id):
        """
        Get a customer by ID.
        
        Args:
            customer_id: Customer ID
        
        Returns:
            Customer dictionary or None if not found
        """
        for customer in self.customers:
            if customer["id"] == customer_id:
                return customer
        return None
    
    def add_customer(self, customer_data):
        """
        Add a new customer.
        
        Args:
            customer_data: Customer data dictionary
        
        Returns:
            New customer dictionary
        """
        # Generate ID
        customer_id = max([c["id"] for c in self.customers], default=0) + 1
        
        # Create new customer
        new_customer = {
            "id": customer_id,
            "name": customer_data.get("name", ""),
            "address": customer_data.get("address", ""),
            "phone": customer_data.get("phone", ""),
            "email": customer_data.get("email", ""),
            "pools": []
        }
        
        # Add pool if provided
        if "pool_type" in customer_data and "pool_volume" in customer_data:
            pool_id = 1
            new_customer["pools"].append({
                "id": pool_id,
                "type": customer_data.get("pool_type", ""),
                "volume": float(customer_data.get("pool_volume", 0)),
                "volume_unit": customer_data.get("volume_unit", "gallons"),
                "surface": customer_data.get("surface", "")
            })
        
        # Add to list
        self.customers.append(new_customer)
        
        # Save to file
        self._save_customers()
        
        return new_customer
    
    def update_customer(self, customer_id, customer_data):
        """
        Update a customer.
        
        Args:
            customer_id: Customer ID
            customer_data: Customer data dictionary
        
        Returns:
            Updated customer dictionary or None if not found
        """
        for i, customer in enumerate(self.customers):
            if customer["id"] == customer_id:
                # Update fields
                self.customers[i]["name"] = customer_data.get("name", customer["name"])
                self.customers[i]["address"] = customer_data.get("address", customer["address"])
                self.customers[i]["phone"] = customer_data.get("phone", customer["phone"])
                self.customers[i]["email"] = customer_data.get("email", customer["email"])
                
                # Save to file
                self._save_customers()
                
                return self.customers[i]
        return None
    
    def delete_customer(self, customer_id):
        """
        Delete a customer.
        
        Args:
            customer_id: Customer ID
        
        Returns:
            True if deleted, False if not found
        """
        for i, customer in enumerate(self.customers):
            if customer["id"] == customer_id:
                # Remove from list
                del self.customers[i]
                
                # Save to file
                self._save_customers()
                
                return True
        return False
    
    def get_readings(self, customer_id=None, pool_id=None, days=30):
        """
        Get readings for a customer and pool.
        
        Args:
            customer_id: Customer ID (optional)
            pool_id: Pool ID (optional)
            days: Number of days to get readings for
        
        Returns:
            List of reading dictionaries
        """
        # Filter by date
        start_date = datetime.now() - timedelta(days=days)
        start_date_str = start_date.strftime("%Y-%m-%d")
        
        # Filter readings
        filtered_readings = []
        for reading in self.readings:
            # Check if reading has a date field
            if "date" not in reading:
                continue
                
            # Check date
            if reading["date"] < start_date_str:
                continue
            
            # Check customer ID
            if customer_id is not None and reading["customer_id"] != customer_id:
                continue
            
            # Check pool ID
            if pool_id is not None and reading["pool_id"] != pool_id:
                continue
            
            filtered_readings.append(reading)
        
        return filtered_readings
    
    def get_latest_reading(self, customer_id, pool_id=None):
        """
        Get the latest reading for a customer and pool.
        
        Args:
            customer_id: Customer ID
            pool_id: Pool ID (optional)
        
        Returns:
            Reading dictionary or None if not found
        """
        # Get readings for customer
        readings = self.get_readings(customer_id, pool_id)
        
        # Sort by date (newest first)
        readings.sort(key=lambda r: r.get("date", ""), reverse=True)
        
        # Return latest reading
        return readings[0] if readings else None
    
    def add_reading(self, reading_data):
        """
        Add a new reading.
        
        Args:
            reading_data: Reading data dictionary
        
        Returns:
            New reading dictionary
        """
        # Generate ID
        reading_id = max([r["id"] for r in self.readings], default=0) + 1
        
        # Create new reading
        new_reading = {
            "id": reading_id,
            "customer_id": reading_data.get("customer_id", 1),
            "pool_id": reading_data.get("pool_id", 1),
            "date": datetime.now().strftime("%Y-%m-%d"),
            "ph": float(reading_data.get("ph", 0)),
            "free_chlorine": float(reading_data.get("free_chlorine", 0)),
            "total_alkalinity": float(reading_data.get("total_alkalinity", 0)),
            "calcium_hardness": float(reading_data.get("calcium_hardness", 0)),
            "cyanuric_acid": float(reading_data.get("cyanuric_acid", 0)),
            "salt": float(reading_data.get("salt", 0)),
            "temperature": float(reading_data.get("temperature", 0))
        }
        
        # Add to the list
        self.readings.append(new_reading)
        
        # Save to file
        self._save_readings()
        
        return new_reading

class ChemicalParameterService:
    """Service for chemical parameter recommendations."""
    
    def __init__(self):
        """Initialize the chemical parameter service."""
        self.parameters = self._initialize_parameters()
    
    def _initialize_parameters(self):
        """Initialize chemical parameters."""
        return {
            "ph": {
                "name": "pH",
                "unit": "",
                "ideal_range": {"min": 7.2, "max": 7.8},
                "recommendations": {
                    "low": "Add pH increaser (sodium carbonate). For a 20,000 gallon pool, add 1 lb to raise pH by 0.2.",
                    "high": "Add pH decreaser (sodium bisulfate). For a 20,000 gallon pool, add 1 lb to lower pH by 0.2.",
                    "ok": "pH is in the ideal range."
                },
                "warnings": {
                    "low": "Low pH can cause eye and skin irritation, corrosion of equipment, and etching of pool surfaces.",
                    "high": "High pH can cause cloudy water, scale formation, reduced chlorine effectiveness, and skin/eye irritation."
                }
            },
            "free_chlorine": {
                "name": "Free Chlorine",
                "unit": "ppm",
                "ideal_range": {"min": 1.0, "max": 3.0},
                "recommendations": {
                    "low": "Add chlorine. For a 20,000 gallon pool, add 1 lb of calcium hypochlorite to raise free chlorine by 1 ppm.",
                    "high": "Reduce chlorine by exposing to sunlight or using a chlorine neutralizer.",
                    "ok": "Free chlorine is in the ideal range."
                },
                "warnings": {
                    "low": "Low chlorine can lead to algae growth and bacteria proliferation.",
                    "high": "High chlorine can cause eye and skin irritation, bleaching of swimwear, and damage to equipment."
                }
            },
            "total_alkalinity": {
                "name": "Total Alkalinity",
                "unit": "ppm",
                "ideal_range": {"min": 80, "max": 120},
                "recommendations": {
                    "low": "Add alkalinity increaser (sodium bicarbonate). For a 20,000 gallon pool, add 1.5 lbs to raise alkalinity by 10 ppm.",
                    "high": "Add pH decreaser (sodium bisulfate) gradually. For a 20,000 gallon pool, add 1 lb to lower alkalinity by 10 ppm.",
                    "ok": "Total alkalinity is in the ideal range."
                },
                "warnings": {
                    "low": "Low alkalinity can cause pH bounce, corrosion, and staining.",
                    "high": "High alkalinity can cause cloudy water, scale formation, and difficulty adjusting pH."
                }
            },
            "calcium_hardness": {
                "name": "Calcium Hardness",
                "unit": "ppm",
                "ideal_range": {"min": 200, "max": 400},
                "recommendations": {
                    "low": "Add calcium hardness increaser (calcium chloride). For a 20,000 gallon pool, add 1 lb to raise hardness by 10 ppm.",
                    "high": "Partially drain and refill with fresh water to dilute.",
                    "ok": "Calcium hardness is in the ideal range."
                },
                "warnings": {
                    "low": "Low calcium hardness can cause etching of pool surfaces and corrosion of equipment.",
                    "high": "High calcium hardness can cause scale formation, cloudy water, and clogged filters."
                }
            },
            "cyanuric_acid": {
                "name": "Cyanuric Acid",
                "unit": "ppm",
                "ideal_range": {"min": 30, "max": 50},
                "recommendations": {
                    "low": "Add cyanuric acid stabilizer. For a 20,000 gallon pool, add 1 lb to raise CYA by 10 ppm.",
                    "high": "Partially drain and refill with fresh water to dilute.",
                    "ok": "Cyanuric acid is in the ideal range."
                },
                "warnings": {
                    "low": "Low cyanuric acid can lead to rapid chlorine loss due to sunlight.",
                    "high": "High cyanuric acid can reduce chlorine effectiveness (chlorine lock)."
                }
            },
            "salt": {
                "name": "Salt",
                "unit": "ppm",
                "ideal_range": {"min": 2700, "max": 3400},
                "recommendations": {
                    "low": "Add pool salt. For a 20,000 gallon pool, add 170 lbs to raise salt level by 1000 ppm.",
                    "high": "Partially drain and refill with fresh water to dilute.",
                    "ok": "Salt level is in the ideal range."
                },
                "warnings": {
                    "low": "Low salt can reduce effectiveness of salt chlorine generator.",
                    "high": "High salt can damage pool equipment and lead to corrosion."
                }
            },
            "temperature": {
                "name": "Temperature",
                "unit": "\u00b0F",
                "ideal_range": {"min": 78, "max": 82},
                "recommendations": {
                    "low": "Consider using a pool heater to raise the temperature.",
                    "high": "Consider using a pool cooler or running the pump at night to lower the temperature.",
                    "ok": "Temperature is comfortable for swimming."
                },
                "warnings": {
                    "low": "Low temperature can make swimming uncomfortable.",
                    "high": "High temperature can accelerate chlorine loss and promote algae growth."
                }
            }
        }
    
    def get_parameter(self, name):
        """
        Get a parameter by name.
        
        Args:
            name: Parameter name
        
        Returns:
            Parameter dictionary or None if not found
        """
        return self.parameters.get(name)
    
    def get_all_parameters(self):
        """
        Get all parameters.
        
        Returns:
            Dictionary of parameters
        """
        return self.parameters
    
    def analyze_parameters(self, values):
        """
        Analyze chemical parameters and provide recommendations.
        
        Args:
            values: Dictionary of parameter values
        
        Returns:
            Dictionary of analysis results
        """
        results = {}
        
        # Analyze each parameter
        for name, value in values.items():
            # Skip if parameter not found
            if name not in self.parameters:
                continue
            
            # Get parameter
            parameter = self.parameters[name]
            
            # Determine status
            status = "ok"
            if value < parameter["ideal_range"]["min"]:
                status = "low"
            elif value > parameter["ideal_range"]["max"]:
                status = "high"
            
            # Add to results
            results[parameter["name"]] = {
                "value": value,
                "unit": parameter["unit"],
                "status": status,
                "recommendation": parameter["recommendations"][status],
                "warning": parameter["warnings"].get(status, "")
            }
        
        return results

class TestStripAnalyzer:
    """Analyzer for test strips."""
    
    def __init__(self):
        """Initialize the test strip analyzer."""
        self.parameters = ["Free Chlorine", "pH", "Total Alkalinity", "Calcium Hardness", "Cyanuric Acid", "Total Bromine"]
    
    def analyze_image(self, image_path):
        """
        Analyze a test strip image.
        
        Args:
            image_path: Path to image file
        
        Returns:
            Dictionary of analysis results
        """
        # In a real application, this would use computer vision to analyze the image
        # For this simple version, we'll just return simulated results
        return self._simulate_results()
    
    def _simulate_results(self):
        """
        Simulate test strip analysis results.
        
        Returns:
            Dictionary of simulated results
        """
        return {
            "Free Chlorine": {
                "value": round(random.uniform(1.0, 3.0), 1),
                "unit": "ppm",
                "status": "ok"
            },
            "pH": {
                "value": round(random.uniform(7.0, 8.0), 1),
                "unit": "",
                "status": "ok"
            },
            "Total Alkalinity": {
                "value": round(random.uniform(80, 120)),
                "unit": "ppm",
                "status": "ok"
            },
            "Calcium Hardness": {
                "value": round(random.uniform(200, 400)),
                "unit": "ppm",
                "status": "ok"
            },
            "Cyanuric Acid": {
                "value": round(random.uniform(30, 50)),
                "unit": "ppm",
                "status": "ok"
            },
            "Total Bromine": {
                "value": round(random.uniform(2.0, 4.0), 1),
                "unit": "ppm",
                "status": "ok"
            }
        }

class DeepBluePoolApp:
    """Deep Blue Pool Chemistry Application."""
    
    def __init__(self):
        """Initialize the application."""
        # Initialize variables first to avoid attribute errors
        self.chemical_vars = {}
        self.arduino_data_var = None
        self.customer_var = None
        self.name_var = None
        self.address_var = None
        self.phone_var = None
        self.pool_type_var = None
        self.pool_volume_var = None
        self.volume_var = None
        self.zip_var = None
        self.location_var = None
        self.temp_var = None
        self.conditions_var = None
        self.humidity_var = None
        self.wind_var = None
        self.forecast_vars = []
        self.impact_text = None
        self.recommendations_text = None
        self.warnings_text = None
        self.procedures_text = None
        self.readings_tree = None
        self.fig = None
        self.canvas = None
        self.param_var = None
        self.time_range_var = None
        self.port_var = None
        self.port_combo = None
        self.connect_button = None
        self.test_strip_results = None
        self.results_labels = {}
        self.image_label = None
        self.data_text = None
        
        # Log initialization
        logger.info("Initializing Deep Blue Pool Chemistry Application")
        
        # Initialize services
        self.db_service = DatabaseService()
        self.chemical_service = ChemicalParameterService()
        self.test_strip_analyzer = TestStripAnalyzer()
        self.arduino_monitor = ArduinoMonitor()
        self.weather_service = WeatherService()
        
        # Set default ZIP code
        self.default_zip = "10001"
        logger.info(f"Set default ZIP code to {self.default_zip}")
        
        # Initialize UI
        self.root = tk.Tk()
        self.setup_ui()
        
        logger.info("Deep Blue Pool Chemistry Application initialized successfully")
    
    def setup_ui(self):
        """Set up the user interface."""
        self.root.title("Deep Blue Pool Chemistry Monitor")
        self.root.geometry("1200x800")
        self.root.configure(bg="#f0f0f0")
        
        # Create main frame
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create navigation frame
        self.nav_frame = ttk.Frame(self.main_frame)
        self.nav_frame.pack(side=tk.TOP, fill=tk.X, pady=(0, 10))
        
        # Create tab control
        self.tab_control = ttk.Notebook(self.main_frame)
        self.tab_control.pack(fill=tk.BOTH, expand=True)
        
        # Create tabs
        self.dashboard_tab = ttk.Frame(self.tab_control)
        self.readings_tab = ttk.Frame(self.tab_control)
        self.test_strip_tab = ttk.Frame(self.tab_control)
        self.recommendations_tab = ttk.Frame(self.tab_control)
        self.trends_tab = ttk.Frame(self.tab_control)
        
        self.tab_control.add(self.dashboard_tab, text="Dashboard")
        self.tab_control.add(self.readings_tab, text="Readings")
        self.tab_control.add(self.test_strip_tab, text="Test Strip")
        self.tab_control.add(self.recommendations_tab, text="Recommendations")
        self.tab_control.add(self.trends_tab, text="Trends")
        
        # Set up tabs
        self.setup_dashboard()
        self.setup_readings()
        self.setup_test_strip()
        self.setup_recommendations()
        self.setup_trends()
        
        # Set up Arduino monitor
        self.arduino_data_var = tk.StringVar(value="Not connected")
        self.setup_arduino_monitor()
        
        # Update weather every 30 minutes
        self.update_weather()
        self.root.after(1800000, self.update_weather)
    
    def setup_dashboard(self):
        """Set up the dashboard tab."""
        # Create frames
        self.customer_frame = ttk.Frame(self.dashboard_tab)
        self.customer_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Set up customer info
        self.setup_customer_info()
        
        # Set up weather forecast
        self.setup_weather_forecast()
        
        # Set up chemical parameters
        self.setup_chemical_parameters()
    
    def setup_customer_info(self):
        """Set up the customer information section."""
        # Create left and right frames
        left_frame = ttk.Frame(self.customer_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        right_frame = ttk.Frame(self.customer_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # Customer selection
        customer_select_frame = ttk.LabelFrame(left_frame, text="Customer Information")
        customer_select_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Get customers
        customers = self.db_service.get_all_customers()
        customer_names = [c["name"] for c in customers]
        
        # Customer dropdown
        ttk.Label(customer_select_frame, text="Customer:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.customer_var = tk.StringVar()
        self.customer_combo = ttk.Combobox(customer_select_frame, textvariable=self.customer_var, values=customer_names, width=30)
        self.customer_combo.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        self.customer_combo.bind("<<ComboboxSelected>>", self.on_customer_selected)
        
        # Customer details
        details_frame = ttk.Frame(customer_select_frame)
        details_frame.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky="w")
        
        # Name
        ttk.Label(details_frame, text="Name:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.name_var = tk.StringVar()
        ttk.Label(details_frame, textvariable=self.name_var).grid(row=0, column=1, padx=5, pady=2, sticky="w")
        
        # Address
        ttk.Label(details_frame, text="Address:").grid(row=1, column=0, padx=5, pady=2, sticky="w")
        self.address_var = tk.StringVar()
        ttk.Label(details_frame, textvariable=self.address_var).grid(row=1, column=1, padx=5, pady=2, sticky="w")
        
        # Phone
        ttk.Label(details_frame, text="Phone:").grid(row=2, column=0, padx=5, pady=2, sticky="w")
        self.phone_var = tk.StringVar()
        ttk.Label(details_frame, textvariable=self.phone_var).grid(row=2, column=1, padx=5, pady=2, sticky="w")
        
        # Pool information
        pool_frame = ttk.LabelFrame(left_frame, text="Pool Information")
        pool_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Pool type
        ttk.Label(pool_frame, text="Type:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.pool_type_var = tk.StringVar()
        ttk.Label(pool_frame, textvariable=self.pool_type_var).grid(row=0, column=1, padx=5, pady=2, sticky="w")
        
        # Pool volume
        ttk.Label(pool_frame, text="Volume:").grid(row=1, column=0, padx=5, pady=2, sticky="w")
        self.pool_volume_var = tk.StringVar()
        ttk.Label(pool_frame, textvariable=self.pool_volume_var).grid(row=1, column=1, padx=5, pady=2, sticky="w")
        
        # Hidden volume variable for calculations
        self.volume_var = tk.StringVar(value="20000")
        
        # If we have customers, select the first one
        if customers:
            self.customer_var.set(customer_names[0])
            self.on_customer_selected(None)
    
    def setup_weather_forecast(self):
        """Set up the weather forecast section."""
        # Create weather frame
        self.weather_frame = ttk.LabelFrame(self.customer_frame, text="Weather Analysis & Forecast")
        self.weather_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # ZIP code input
        zip_frame = ttk.Frame(self.weather_frame)
        zip_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(zip_frame, text="ZIP Code:").pack(side=tk.LEFT, padx=5)
        self.zip_var = tk.StringVar(value=self.default_zip)
        zip_entry = ttk.Entry(zip_frame, textvariable=self.zip_var, width=10)
        zip_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(zip_frame, text="Update Weather", command=self.update_weather).pack(side=tk.LEFT, padx=5)
        
        # Weather display
        weather_display = ttk.Frame(self.weather_frame)
        weather_display.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Current conditions
        current_frame = ttk.LabelFrame(weather_display, text="Current Conditions")
        current_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Location
        ttk.Label(current_frame, text="Location:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.location_var = tk.StringVar()
        ttk.Label(current_frame, textvariable=self.location_var).grid(row=0, column=1, padx=5, pady=2, sticky="w")
        
        # Temperature
        ttk.Label(current_frame, text="Temperature:").grid(row=1, column=0, padx=5, pady=2, sticky="w")
        self.temp_var = tk.StringVar()
        ttk.Label(current_frame, textvariable=self.temp_var).grid(row=1, column=1, padx=5, pady=2, sticky="w")
        
        # Conditions
        ttk.Label(current_frame, text="Conditions:").grid(row=2, column=0, padx=5, pady=2, sticky="w")
        self.conditions_var = tk.StringVar()
        ttk.Label(current_frame, textvariable=self.conditions_var).grid(row=2, column=1, padx=5, pady=2, sticky="w")
        
        # Humidity
        ttk.Label(current_frame, text="Humidity:").grid(row=3, column=0, padx=5, pady=2, sticky="w")
        self.humidity_var = tk.StringVar()
        ttk.Label(current_frame, textvariable=self.humidity_var).grid(row=3, column=1, padx=5, pady=2, sticky="w")
        
        # Wind
        ttk.Label(current_frame, text="Wind:").grid(row=4, column=0, padx=5, pady=2, sticky="w")
        self.wind_var = tk.StringVar()
        ttk.Label(current_frame, textvariable=self.wind_var).grid(row=4, column=1, padx=5, pady=2, sticky="w")
        
        # Forecast
        forecast_frame = ttk.LabelFrame(weather_display, text="Forecast")
        forecast_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # Forecast days
        self.forecast_vars = []
        for i in range(3):
            day_frame = ttk.Frame(forecast_frame)
            day_frame.pack(fill=tk.X, pady=2)
            
            day_var = tk.StringVar()
            high_var = tk.StringVar()
            low_var = tk.StringVar()
            cond_var = tk.StringVar()
            
            ttk.Label(day_frame, textvariable=day_var, width=10).pack(side=tk.LEFT, padx=5)
            ttk.Label(day_frame, textvariable=high_var, width=5).pack(side=tk.LEFT, padx=5)
            ttk.Label(day_frame, textvariable=low_var, width=5).pack(side=tk.LEFT, padx=5)
            ttk.Label(day_frame, textvariable=cond_var).pack(side=tk.LEFT, padx=5)
            
            self.forecast_vars.append((day_var, high_var, low_var, cond_var))
        
        # Pool impact
        impact_frame = ttk.LabelFrame(self.weather_frame, text="Weather Impact on Pool Chemistry")
        impact_frame.pack(fill=tk.X, pady=5)
        
        self.impact_text = scrolledtext.ScrolledText(impact_frame, wrap=tk.WORD, height=4)
        self.impact_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.impact_text.config(state=tk.DISABLED)
    
    def setup_chemical_parameters(self):
        """Set up the chemical parameters section."""
        # Create chemical frame
        chem_frame = ttk.LabelFrame(self.customer_frame, text="Chemical Parameters")
        chem_frame.pack(fill=tk.BOTH, expand=True)
        
        # Chemical parameters
        chemical_entries = {}
        
        # pH
        ttk.Label(chem_frame, text="pH:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.chemical_vars['ph'] = tk.StringVar()
        chemical_entries['ph'] = ttk.Entry(chem_frame, textvariable=self.chemical_vars['ph'], width=10)
        chemical_entries['ph'].grid(row=0, column=1, padx=5, pady=5, sticky="w")
        ttk.Label(chem_frame, text="Ideal: 7.2 - 7.8").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        
        # Free Chlorine
        ttk.Label(chem_frame, text="Free Chlorine (ppm):").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.chemical_vars['free_chlorine'] = tk.StringVar()
        chemical_entries['free_chlorine'] = ttk.Entry(chem_frame, textvariable=self.chemical_vars['free_chlorine'], width=10)
        chemical_entries['free_chlorine'].grid(row=1, column=1, padx=5, pady=5, sticky="w")
        ttk.Label(chem_frame, text="Ideal: 1.0 - 3.0").grid(row=1, column=2, padx=5, pady=5, sticky="w")
        
        # Alkalinity
        ttk.Label(chem_frame, text="Alkalinity (ppm):").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.chemical_vars['total_alkalinity'] = tk.StringVar()
        chemical_entries['total_alkalinity'] = ttk.Entry(chem_frame, textvariable=self.chemical_vars['total_alkalinity'], width=10)
        chemical_entries['total_alkalinity'].grid(row=2, column=1, padx=5, pady=5, sticky="w")
        ttk.Label(chem_frame, text="Ideal: 80 - 120").grid(row=2, column=2, padx=5, pady=5, sticky="w")
        
        # Calcium Hardness
        ttk.Label(chem_frame, text="Calcium Hardness (ppm):").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.chemical_vars['calcium_hardness'] = tk.StringVar()
        chemical_entries['calcium_hardness'] = ttk.Entry(chem_frame, textvariable=self.chemical_vars['calcium_hardness'], width=10)
        chemical_entries['calcium_hardness'].grid(row=3, column=1, padx=5, pady=5, sticky="w")
        ttk.Label(chem_frame, text="Ideal: 200 - 400").grid(row=3, column=2, padx=5, pady=5, sticky="w")
        
        # Cyanuric Acid
        ttk.Label(chem_frame, text="Cyanuric Acid (ppm):").grid(row=4, column=0, padx=5, pady=5, sticky="w")
        self.chemical_vars['cyanuric_acid'] = tk.StringVar()
        chemical_entries['cyanuric_acid'] = ttk.Entry(chem_frame, textvariable=self.chemical_vars['cyanuric_acid'], width=10)
        chemical_entries['cyanuric_acid'].grid(row=4, column=1, padx=5, pady=5, sticky="w")
        ttk.Label(chem_frame, text="Ideal: 30 - 50").grid(row=4, column=2, padx=5, pady=5, sticky="w")
        
        # Salt
        ttk.Label(chem_frame, text="Salt (ppm):").grid(row=5, column=0, padx=5, pady=5, sticky="w")
        self.chemical_vars['salt'] = tk.StringVar()
        chemical_entries['salt'] = ttk.Entry(chem_frame, textvariable=self.chemical_vars['salt'], width=10)
        chemical_entries['salt'].grid(row=5, column=1, padx=5, pady=5, sticky="w")
        ttk.Label(chem_frame, text="Ideal: 2700 - 3400").grid(row=5, column=2, padx=5, pady=5, sticky="w")
        
        # Temperature
        ttk.Label(chem_frame, text="Temperature (\u00b0F):").grid(row=6, column=0, padx=5, pady=5, sticky="w")
        self.chemical_vars['temperature'] = tk.StringVar()
        chemical_entries['temperature'] = ttk.Entry(chem_frame, textvariable=self.chemical_vars['temperature'], width=10)
        chemical_entries['temperature'].grid(row=6, column=1, padx=5, pady=5, sticky="w")
        ttk.Label(chem_frame, text="Ideal: 78 - 82").grid(row=6, column=2, padx=5, pady=5, sticky="w")
        
        # Buttons
        button_frame = ttk.Frame(chem_frame)
        button_frame.grid(row=7, column=0, columnspan=3, padx=5, pady=10)
        
        ttk.Button(button_frame, text="Save Reading", command=self.save_reading).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Get Recommendations", command=self.get_recommendations).pack(side=tk.LEFT, padx=5)
    
    def setup_readings(self):
        """Set up the readings tab."""
        # Create frames
        self.readings_frame = ttk.Frame(self.readings_tab)
        self.readings_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Readings table
        table_frame = ttk.LabelFrame(self.readings_frame, text="Reading History")
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create treeview
        columns = ("date", "ph", "free_chlorine", "total_alkalinity", "calcium_hardness", "cyanuric_acid", "salt", "temperature")
        self.readings_tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        
        # Set column headings
        self.readings_tree.heading("date", text="Date")
        self.readings_tree.heading("ph", text="pH")
        self.readings_tree.heading("free_chlorine", text="Free Chlorine")
        self.readings_tree.heading("total_alkalinity", text="Total Alkalinity")
        self.readings_tree.heading("calcium_hardness", text="Calcium Hardness")
        self.readings_tree.heading("cyanuric_acid", text="Cyanuric Acid")
        self.readings_tree.heading("salt", text="Salt")
        self.readings_tree.heading("temperature", text="Temperature")
        
        # Set column widths
        self.readings_tree.column("date", width=100)
        self.readings_tree.column("ph", width=50)
        self.readings_tree.column("free_chlorine", width=100)
        self.readings_tree.column("total_alkalinity", width=100)
        self.readings_tree.column("calcium_hardness", width=120)
        self.readings_tree.column("cyanuric_acid", width=100)
        self.readings_tree.column("salt", width=80)
        self.readings_tree.column("temperature", width=100)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.readings_tree.yview)
        self.readings_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.readings_tree.pack(fill=tk.BOTH, expand=True)
        
        # Load readings
        self.load_readings()
    
    def setup_test_strip(self):
        """Set up the test strip tab."""
        # Create frames
        self.test_strip_frame = ttk.Frame(self.test_strip_tab)
        self.test_strip_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Test strip image
        image_frame = ttk.LabelFrame(self.test_strip_frame, text="Test Strip Image")
        image_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Image placeholder
        self.image_label = ttk.Label(image_frame, text="No image uploaded")
        self.image_label.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Buttons
        button_frame = ttk.Frame(image_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(button_frame, text="Take Photo", command=self.take_photo).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Upload Image", command=self.upload_test_strip).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Analyze", command=self.analyze_test_strip).pack(side=tk.LEFT, padx=5)
        
        # Results
        results_frame = ttk.LabelFrame(self.test_strip_frame, text="Analysis Results")
        results_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create results grid
        self.results_labels = {}
        for i, param in enumerate(self.test_strip_analyzer.parameters):
            ttk.Label(results_frame, text=f"{param}:").grid(row=i, column=0, padx=5, pady=5, sticky="w")
            self.results_labels[param] = ttk.Label(results_frame, text="--")
            self.results_labels[param].grid(row=i, column=1, padx=5, pady=5, sticky="w")
        
        # Apply button
        ttk.Button(results_frame, text="Apply Results to Readings", command=self.apply_test_strip_results).pack(pady=10)
    
    def setup_recommendations(self):
        """Set up the recommendations tab."""
        # Create frames
        self.recommendations_frame = ttk.Frame(self.recommendations_tab)
        self.recommendations_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Recommendations
        rec_frame = ttk.LabelFrame(self.recommendations_frame, text="Recommendations")
        rec_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.recommendations_text = scrolledtext.ScrolledText(rec_frame, wrap=tk.WORD, height=6)
        self.recommendations_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.recommendations_text.config(state=tk.DISABLED)
        
        # Warnings
        warn_frame = ttk.LabelFrame(self.recommendations_frame, text="Warnings")
        warn_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.warnings_text = scrolledtext.ScrolledText(warn_frame, wrap=tk.WORD, height=6)
        self.warnings_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.warnings_text.config(state=tk.DISABLED)
        
        # Procedures
        proc_frame = ttk.LabelFrame(self.recommendations_frame, text="Procedures")
        proc_frame.pack(fill=tk.BOTH, expand=True)
        
        self.procedures_text = scrolledtext.ScrolledText(proc_frame, wrap=tk.WORD, height=6)
        self.procedures_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.procedures_text.config(state=tk.DISABLED)
    
    def setup_trends(self):
        """Set up the trends tab."""
        # Create frames
        self.trends_frame = ttk.Frame(self.trends_tab)
        self.trends_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Controls
        controls_frame = ttk.Frame(self.trends_frame)
        controls_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Parameter selection
        ttk.Label(controls_frame, text="Parameter:").pack(side=tk.LEFT, padx=5)
        self.param_var = tk.StringVar(value="ph")
        param_combo = ttk.Combobox(controls_frame, textvariable=self.param_var, values=["ph", "free_chlorine", "total_alkalinity", "calcium_hardness", "cyanuric_acid", "salt", "temperature"], width=15)
        param_combo.pack(side=tk.LEFT, padx=5)
        param_combo.bind("<<ComboboxSelected>>", self.update_trends)
        
        # Time range selection
        ttk.Label(controls_frame, text="Time Range:").pack(side=tk.LEFT, padx=5)
        self.time_range_var = tk.StringVar(value="7 Days")
        time_combo = ttk.Combobox(controls_frame, textvariable=self.time_range_var, values=["7 Days", "30 Days"], width=10)
        time_combo.pack(side=tk.LEFT, padx=5)
        time_combo.bind("<<ComboboxSelected>>", self.update_trends)
        
        # Chart
        chart_frame = ttk.LabelFrame(self.trends_frame, text="Trends Chart")
        chart_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create figure and canvas
        self.fig = Figure(figsize=(10, 6), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.fig, master=chart_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Update trends
        self.update_trends()
    
    def setup_arduino_monitor(self):
        """Set up the Arduino monitor."""
        # Create Arduino frame
        arduino_frame = ttk.LabelFrame(self.root, text="Arduino Monitor")
        arduino_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        # Create Arduino controls
        controls_frame = ttk.Frame(arduino_frame)
        controls_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Port selection
        ttk.Label(controls_frame, text="Port:").pack(side=tk.LEFT, padx=5)
        self.port_var = tk.StringVar()
        self.port_combo = ttk.Combobox(controls_frame, textvariable=self.port_var, width=15)
        self.port_combo.pack(side=tk.LEFT, padx=5)
        
        # Refresh ports button
        ttk.Button(controls_frame, text="Refresh", command=self.refresh_ports).pack(side=tk.LEFT, padx=5)
        
        # Connect button
        self.connect_button = ttk.Button(controls_frame, text="Connect", command=self.toggle_arduino_connection)
        self.connect_button.pack(side=tk.LEFT, padx=5)
        
        # Simulate button
        ttk.Button(controls_frame, text="Simulate Data", command=self.simulate_arduino_data).pack(side=tk.LEFT, padx=5)
        
        # Arduino data display
        ttk.Label(controls_frame, text="Data:").pack(side=tk.LEFT, padx=5)
        ttk.Label(controls_frame, textvariable=self.arduino_data_var).pack(side=tk.LEFT, padx=5)
        
        # Refresh ports
        self.refresh_ports()
    
    def refresh_ports(self):
        """Refresh the list of available serial ports."""
        ports = self.arduino_monitor.update_available_ports()
        self.port_combo['values'] = ports
        if ports:
            self.port_var.set(ports[0])
    
    def toggle_arduino_connection(self):
        """Toggle Arduino connection."""
        if self.arduino_monitor.is_connected:
            self.arduino_monitor.disconnect()
            self.connect_button.config(text="Connect")
            self.arduino_data_var.set("Not connected")
        else:
            port = self.port_var.get()
            if port:
                if self.arduino_monitor.connect(port):
                    self.connect_button.config(text="Disconnect")
                    self.arduino_monitor.start_monitoring(self.handle_arduino_data)
                else:
                    messagebox.showerror("Connection Error", f"Failed to connect to {port}")
            else:
                messagebox.showerror("Connection Error", "No port selected")
    
    def handle_arduino_data(self, data):
        """
        Handle data received from Arduino.
        
        Args:
            data: Data string from Arduino
        """
        self.arduino_data_var.set(data)
        
        # Parse data
        try:
            # Clean up the data by removing any non-numeric characters except decimal points
            cleaned_data = re.sub(r'[^\d.]', '', data)
            
            if cleaned_data:
                try:
                    # Try to parse as a number (likely ORP value)
                    orp = float(cleaned_data)
                    
                    # Update ORP-related values
                    # Rough estimation: ORP 650 mV \u2248 1.0 ppm free chlorine
                    free_chlorine = (orp - 600) / 50
                    if free_chlorine < 0:
                        free_chlorine = 0
                    
                    # Update the UI if chemical_vars is initialized
                    if hasattr(self, 'chemical_vars') and 'free_chlorine' in self.chemical_vars:
                        self.chemical_vars['free_chlorine'].set(str(round(free_chlorine, 1)))
                    
                    return
                except ValueError:
                    pass
            
            # If we get here, try other formats
            
            # Format 1: "pH:7.2,Temp:78.5,ORP:650"
            if ":" in data and "," in data:
                values = {}
                for item in data.split(','):
                    if ":" in item:
                        parts = item.split(':')
                        if len(parts) == 2:
                            key, value = parts
                            try:
                                values[key] = float(value)
                            except ValueError:
                                # Skip values that can't be converted to float
                                pass
                
                # Update chemical parameters if available
                if 'pH' in values and hasattr(self, 'chemical_vars') and 'ph' in self.chemical_vars:
                    self.chemical_vars['ph'].set(str(values['pH']))
                
                if 'Temp' in values and hasattr(self, 'chemical_vars') and 'temperature' in self.chemical_vars:
                    self.chemical_vars['temperature'].set(str(values['Temp']))
                
                # ORP can be used to estimate free chlorine
                if 'ORP' in values and hasattr(self, 'chemical_vars') and 'free_chlorine' in self.chemical_vars:
                    # Rough estimation: ORP 650 mV \u2248 1.0 ppm free chlorine
                    free_chlorine = (values['ORP'] - 600) / 50
                    if free_chlorine < 0:
                        free_chlorine = 0
                    self.chemical_vars['free_chlorine'].set(str(round(free_chlorine, 1)))
            
            # Format 2: JSON-like format
            elif "{" in data and "}" in data:
                # Extract JSON part
                json_str = data[data.find("{"):data.find("}")+1]
                # Try to parse as JSON
                try:
                    # Replace single quotes with double quotes for proper JSON
                    json_str = json_str.replace("'", '"')
                    values = json.loads(json_str)
                    
                    # Update chemical parameters if available
                    if 'pH' in values and hasattr(self, 'chemical_vars') and 'ph' in self.chemical_vars:
                        self.chemical_vars['ph'].set(str(values['pH']))
                    
                    if 'Temp' in values and hasattr(self, 'chemical_vars') and 'temperature' in self.chemical_vars:
                        self.chemical_vars['temperature'].set(str(values['Temp']))
                    
                    if 'ORP' in values and hasattr(self, 'chemical_vars') and 'free_chlorine' in self.chemical_vars:
                        # Rough estimation: ORP 650 mV \u2248 1.0 ppm free chlorine
                        free_chlorine = (values['ORP'] - 600) / 50
                        if free_chlorine < 0:
                            free_chlorine = 0
                        self.chemical_vars['free_chlorine'].set(str(round(free_chlorine, 1)))
                except:
                    pass
            
            # Format 3: Try to extract numbers using regex
            else:
                # Look for patterns like "ORP: 650" or "pH: 7.2"
                orp_match = re.search(r'ORP[:\s]+(\d+)', data)
                if orp_match and hasattr(self, 'chemical_vars') and 'free_chlorine' in self.chemical_vars:
                    orp = float(orp_match.group(1))
                    # Rough estimation: ORP 650 mV \u2248 1.0 ppm free chlorine
                    free_chlorine = (orp - 600) / 50
                    if free_chlorine < 0:
                        free_chlorine = 0
                    self.chemical_vars['free_chlorine'].set(str(round(free_chlorine, 1)))
                
                ph_match = re.search(r'pH[:\s]+(\d+\.\d+)', data)
                if ph_match and hasattr(self, 'chemical_vars') and 'ph' in self.chemical_vars:
                    ph = float(ph_match.group(1))
                    self.chemical_vars['ph'].set(str(ph))
                
                temp_match = re.search(r'[Tt]emp(?:erature)?[:\s]+(\d+\.\d+)', data)
                if temp_match and hasattr(self, 'chemical_vars') and 'temperature' in self.chemical_vars:
                    temp = float(temp_match.group(1))
                    self.chemical_vars['temperature'].set(str(temp))
        
        except Exception as e:
            logger.error(f"Error parsing Arduino data: {e}")
    
    def simulate_arduino_data(self):
        """Simulate Arduino data for testing."""
        data = self.arduino_monitor.simulate_data()
        self.handle_arduino_data(data)
    
    def on_customer_selected(self, event):
        """Handle customer selection."""
        name = self.customer_var.get()
        for customer in self.db_service.get_all_customers():
            if customer['name'] == name:
                self.select_customer(customer)
                break
    
    def select_customer(self, customer):
        """
        Select a customer and update the UI.
        
        Args:
            customer: Customer dictionary
        """
        # Update customer details
        self.name_var.set(customer['name'])
        self.address_var.set(customer['address'])
        self.phone_var.set(customer['phone'])
        
        # Update pool details if available
        if customer.get('pools'):
            pool = customer['pools'][0]
            self.pool_type_var.set(pool['type'])
            self.pool_volume_var.set(f"{pool['volume']} {pool['volume_unit']}")
            self.volume_var.set(str(pool['volume']))
        else:
            self.pool_type_var.set("")
            self.pool_volume_var.set("")
        
        # Load latest reading
        reading = self.db_service.get_latest_reading(customer['id'])
        if reading:
            self.chemical_vars['ph'].set(str(reading['ph']))
            self.chemical_vars['free_chlorine'].set(str(reading['free_chlorine']))
            self.chemical_vars['total_alkalinity'].set(str(reading['total_alkalinity']))
            self.chemical_vars['calcium_hardness'].set(str(reading['calcium_hardness']))
            self.chemical_vars['cyanuric_acid'].set(str(reading['cyanuric_acid']))
            self.chemical_vars['salt'].set(str(reading['salt']))
            self.chemical_vars['temperature'].set(str(reading['temperature']))
        else:
            # Clear chemical parameters
            for var in self.chemical_vars.values():
                var.set("")
        
        # Update readings
        self.load_readings()
        
        # Update trends
        self.update_trends()
    
    def load_readings(self):
        """Load readings for the selected customer."""
        # Clear treeview
        for item in self.readings_tree.get_children():
            self.readings_tree.delete(item)
        
        # Get customer ID
        customer_name = self.customer_var.get()
        customer_id = None
        for customer in self.db_service.get_all_customers():
            if customer['name'] == customer_name:
                customer_id = customer['id']
                break
        
        if customer_id is None:
            return
        
        # Get readings
        readings = self.db_service.get_readings(customer_id)
        
        # Sort by date (newest first)
        readings.sort(key=lambda r: r.get("date", ""), reverse=True)
        
        # Add to treeview
        for reading in readings:
            self.readings_tree.insert("", tk.END, values=(
                reading.get("date", ""),
                reading.get("ph", ""),
                reading.get("free_chlorine", ""),
                reading.get("total_alkalinity", ""),
                reading.get("calcium_hardness", ""),
                reading.get("cyanuric_acid", ""),
                reading.get("salt", ""),
                reading.get("temperature", "")
            ))
    
    def update_weather(self):
        """Update weather information."""
        # Get ZIP code
        zip_code = self.zip_var.get()
        logger.info(f"Set default ZIP code to {zip_code}")
        
        # Get weather data
        weather = self.weather_service.get_weather(zip_code)
        
        # Update UI
        self.location_var.set(weather["location"])
        self.temp_var.set(f"{weather['temperature']}\u00b0F")
        self.conditions_var.set(weather["conditions"])
        self.humidity_var.set(f"{weather['humidity']}%")
        self.wind_var.set(f"{weather['wind_speed']} mph {weather['wind_direction']}")
        
        # Update forecast
        for i, forecast in enumerate(weather["forecast"]):
            if i < len(self.forecast_vars):
                day_var, high_var, low_var, cond_var = self.forecast_vars[i]
                day_var.set(forecast["day"])
                high_var.set(f"{forecast['high']}\u00b0F")
                low_var.set(f"{forecast['low']}\u00b0F")
                cond_var.set(forecast["conditions"])
        
        # Update impact text
        self.impact_text.config(state=tk.NORMAL)
        self.impact_text.delete(1.0, tk.END)
        
        # Generate impact text based on conditions
        impact_text = ""
        
        # Temperature impact
        if weather["temperature"] > 85:
            impact_text += "High temperatures can accelerate chlorine loss. Consider adding extra chlorine or using a stabilizer.\
"
        elif weather["temperature"] < 65:
            impact_text += "Low temperatures can slow chemical reactions. Adjust chemical dosages accordingly.\
"
        
        # Conditions impact
        if "Rain" in weather["conditions"]:
            impact_text += "Rain can dilute pool chemicals and affect pH. Check levels after rainfall.\
"
        elif "Sunny" in weather["conditions"]:
            impact_text += "Sunny conditions can deplete chlorine faster. Monitor levels more frequently.\
"
        
        # Wind impact
        if weather["wind_speed"] > 10:
            impact_text += "Windy conditions can introduce debris. Clean skimmer baskets and filters more often.\
"
        
        if not impact_text:
            impact_text = "Current weather conditions have minimal impact on pool chemistry."
        
        self.impact_text.insert(tk.END, impact_text)
        self.impact_text.config(state=tk.DISABLED)
    
    def save_reading(self):
        """Save the current chemical parameters as a new reading."""
        try:
            # Get customer ID
            customer_name = self.customer_var.get()
            customer_id = 1  # Default
            for customer in self.db_service.get_all_customers():
                if customer['name'] == customer_name:
                    customer_id = customer['id']
                    break
            
            # Get pool ID
            pool_id = 1  # Default
            
            # Get chemical parameters
            reading_data = {
                'customer_id': customer_id,
                'pool_id': pool_id
            }
            
            for name, var in self.chemical_vars.items():
                try:
                    value = float(var.get()) if var.get() else 0
                    reading_data[name] = value
                except ValueError:
                    messagebox.showerror("Invalid Input", f"Invalid value for {name}: {var.get()}")
                    return
            
            # Add reading
            self.db_service.add_reading(reading_data)
            
            # Show confirmation
            messagebox.showinfo("Success", "Reading saved successfully")
            
            # Update trends
            self.update_trends()
            
            # Update readings
            self.load_readings()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error saving reading: {e}")
            logger.error(f"Error saving reading: {e}")
    
    def get_recommendations(self):
        """Get recommendations based on chemical parameters."""
        try:
            # Get chemical parameters
            values = {}
            for name, var in self.chemical_vars.items():
                try:
                    value = float(var.get()) if var.get() else 0
                    values[name] = value
                except ValueError:
                    messagebox.showerror("Invalid Input", f"Invalid value for {name}: {var.get()}")
                    return
            
            # Update recommendations
            self.update_recommendations(values)
            
            # Show recommendations tab
            self.show_recommendations()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error getting recommendations: {e}")
            logger.error(f"Error getting recommendations: {e}")
    
    def update_recommendations(self, values):
        """
        Update recommendations based on chemical values.
        
        Args:
            values: Dictionary of chemical values
        """
        # Enable text widgets for editing
        self.recommendations_text.config(state=tk.NORMAL)
        self.warnings_text.config(state=tk.NORMAL)
        self.procedures_text.config(state=tk.NORMAL)
        
        # Clear text widgets
        self.recommendations_text.delete(1.0, tk.END)
        self.warnings_text.delete(1.0, tk.END)
        self.procedures_text.delete(1.0, tk.END)
        
        # Get pool volume
        try:
            volume = float(self.volume_var.get())
        except:
            volume = 20000  # Default
        
        # Analyze parameters
        results = self.chemical_service.analyze_parameters(values)
        
        # Update recommendations
        recommendations = []
        warnings = []
        procedures = []
        
        for param_name, result in results.items():
            # Add recommendation
            if result["status"] != "ok":
                recommendations.append(f"{param_name}: {result['recommendation']}")
            
            # Add warning
            if result["warning"]:
                warnings.append(f"{param_name}: {result['warning']}")
            
            # Add procedure
            if result["status"] == "low":
                if param_name == "pH":
                    procedures.append(f"1. Test pH with a reliable test kit\
2. Calculate the amount of pH increaser needed based on pool volume ({volume} gallons)\
3. Dissolve the pH increaser in a bucket of water\
4. Add the solution to the pool with the pump running\
5. Retest after 4-6 hours")
                elif param_name == "Free Chlorine":
                    procedures.append(f"1. Test chlorine with a reliable test kit\
2. Calculate the amount of chlorine needed based on pool volume ({volume} gallons)\
3. For liquid chlorine, add directly to the pool while the pump is running\
4. For granular chlorine, dissolve in a bucket of water first\
5. Retest after 4-6 hours")
        
        # Update text widgets
        if recommendations:
            self.recommendations_text.insert(tk.END, "\
\
".join(recommendations))
        else:
            self.recommendations_text.insert(tk.END, "All chemical parameters are within ideal ranges.")
        
        if warnings:
            self.warnings_text.insert(tk.END, "\
\
".join(warnings))
        else:
            self.warnings_text.insert(tk.END, "No warnings at this time.")
        
        if procedures:
            self.procedures_text.insert(tk.END, "\
\
".join(procedures))
        else:
            self.procedures_text.insert(tk.END, "No adjustment procedures needed at this time.")
        
        # Disable text widgets
        self.recommendations_text.config(state=tk.DISABLED)
        self.warnings_text.config(state=tk.DISABLED)
        self.procedures_text.config(state=tk.DISABLED)
    
    def show_recommendations(self):
        """Show the recommendations tab."""
        self.tab_control.select(self.recommendations_tab)
    
    def update_trends(self, event=None):
        """Update the trends chart."""
        # Clear the figure
        self.fig.clear()
        
        # Get time range
        time_range = self.time_range_var.get()
        days = 7
        if time_range == "30 Days":
            days = 30
        
        # Get parameter
        param = self.param_var.get()
        
        # Get customer ID
        customer_name = self.customer_var.get()
        customer_id = None
        for customer in self.db_service.get_all_customers():
            if customer['name'] == customer_name:
                customer_id = customer['id']
                break
        
        if customer_id is None:
            return
        
        # Get readings
        readings = self.db_service.get_readings(customer_id, days=days)
        
        # Sort by date
        readings.sort(key=lambda r: r.get("date", ""))
        
        # Extract data
        dates = []
        values = []
        
        for r in readings:
            if "date" in r and param in r:
                try:
                    date = datetime.strptime(r["date"], "%Y-%m-%d")
                    value = r[param]
                    dates.append(date)
                    values.append(value)
                except (ValueError, TypeError):
                    pass
        
        # Create subplot
        ax = self.fig.add_subplot(111)
        
        # Plot data if we have any
        if dates and values:
            ax.plot(dates, values, 'o-', color='blue')
            
            # Set labels
            param_name = param.replace('_', ' ').title()
            ax.set_xlabel('Date')
            ax.set_ylabel(param_name)
            ax.set_title(f'{param_name} Trend - Last {days} Days')
            
            # Format x-axis
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
            self.fig.autofmt_xdate()
            
            # Add grid
            ax.grid(True)
            
            # Add ideal range if available
            parameter = self.chemical_service.get_parameter(param)
            if parameter:
                min_val = parameter["ideal_range"]["min"]
                max_val = parameter["ideal_range"]["max"]
                ax.axhspan(min_val, max_val, alpha=0.2, color='green')
                ax.axhline(min_val, color='green', linestyle='--')
                ax.axhline(max_val, color='green', linestyle='--')
        else:
            ax.text(0.5, 0.5, "No data available for selected parameter and time range", 
                    horizontalalignment='center', verticalalignment='center', transform=ax.transAxes)
        
        # Draw canvas
        self.canvas.draw()
    
    def take_photo(self):
        """Simulate taking a photo with a camera."""
        messagebox.showinfo("Camera", "This feature would activate the camera to take a photo of a test strip.")
        # In a real application, this would activate the camera
        # For this simple version, we'll just call the upload function
        self.upload_test_strip()
    
    def upload_test_strip(self):
        """Simulate uploading a test strip image."""
        messagebox.showinfo("Upload", "This feature would allow uploading an image of a test strip.")
        # In a real application, this would open a file dialog
        # For this simple version, we'll just call the analyze function
        self.analyze_test_strip()
    
    def analyze_test_strip(self):
        """Analyze a test strip image."""
        # In a real application, this would analyze the uploaded image
        # For this simple version, we'll just simulate results
        results = self.test_strip_analyzer._simulate_results()
        
        # Update results labels
        for param, result in results.items():
            value_text = f"{result['value']} {result['unit']}"
            self.results_labels[param].config(text=value_text)
        
        # Store results for later use
        self.test_strip_results = results
        
        # Show confirmation
        messagebox.showinfo("Analysis Complete", "Test strip analysis complete.")
    
    def apply_test_strip_results(self):
        """Apply test strip results to chemical parameters."""
        if not hasattr(self, 'test_strip_results'):
            messagebox.showerror("Error", "No test strip results available.")
            return
        
        # Apply results to chemical parameters
        for name, var in self.chemical_vars.items():
            if name == "free_chlorine":
                var.set(str(self.test_strip_results["Free Chlorine"]["value"]))
            elif name == "ph":
                var.set(str(self.test_strip_results["pH"]["value"]))
            elif name == "total_alkalinity":
                var.set(str(self.test_strip_results["Total Alkalinity"]["value"]))
            elif name == "calcium_hardness":
                var.set(str(self.test_strip_results["Calcium Hardness"]["value"]))
            elif name == "cyanuric_acid":
                var.set(str(self.test_strip_results["Cyanuric Acid"]["value"]))
            elif name == "total_bromine":
                var.set(str(self.test_strip_results["Total Bromine"]["value"]))
        
        # Show confirmation
        messagebox.showinfo("Success", "Test strip results applied to chemical parameters.")
        
        # Switch to dashboard tab
        self.tab_control.select(self.dashboard_tab)
    
    def run(self):
        """Run the application."""
        self.root.mainloop()

if __name__ == "__main__":
    app = DeepBluePoolApp()
    app.run()
