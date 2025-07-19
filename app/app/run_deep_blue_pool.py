
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
import serial
import serial.tools.list_ports

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
os.makedirs("data/strip_profiles", exist_ok=True)
os.makedirs("data/customers", exist_ok=True)
os.makedirs("logs", exist_ok=True)

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
    
    def update_available_ports(self):
        """Update the list of available serial ports."""
        self.available_ports = [port.device for port in serial.tools.list_ports.comports()]
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
                if self.serial_port.in_waiting > 0:
                    line = self.serial_port.readline().decode('utf-8').strip()
                    if line and self.data_callback:
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
        
        data = f"pH:{ph},Temp:{temp},ORP:{orp}"
        
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
        self.forecast_cache = {}
        self.last_update = None
    
    def get_current_weather(self, zip_code=None):
        """
        Get current weather for a ZIP code.
        
        Args:
            zip_code: ZIP code (default: use default_zip)
        
        Returns:
            Weather data dictionary
        """
        if zip_code is None:
            zip_code = self.default_zip
        
        # In a real application, this would call a weather API
        # For this example, we'll return simulated data
        return {
            "location": f"{zip_code}",
            "temperature": round(random.uniform(70, 85), 1),
            "humidity": round(random.uniform(40, 60)),
            "conditions": random.choice(["Sunny", "Partly Cloudy", "Cloudy", "Light Rain"]),
            "wind_speed": round(random.uniform(0, 15)),
            "wind_direction": random.choice(["N", "NE", "E", "SE", "S", "SW", "W", "NW"]),
            "pressure": round(random.uniform(1000, 1020)),
            "timestamp": datetime.now()
        }
    
    def get_forecast(self, zip_code=None, days=5):
        """
        Get weather forecast for a ZIP code.
        
        Args:
            zip_code: ZIP code (default: use default_zip)
            days: Number of days to forecast
        
        Returns:
            List of forecast data dictionaries
        """
        if zip_code is None:
            zip_code = self.default_zip
        
        # Check cache
        cache_key = f"{zip_code}_{days}"
        if (cache_key in self.forecast_cache and 
            self.last_update and 
            (datetime.now() - self.last_update).total_seconds() < 3600):
            return self.forecast_cache[cache_key]
        
        # In a real application, this would call a weather API
        # For this example, we'll return simulated data
        forecast = []
        for i in range(days):
            day = datetime.now() + timedelta(days=i)
            forecast.append({
                "date": day,
                "high_temp": round(random.uniform(75, 90), 1),
                "low_temp": round(random.uniform(60, 75), 1),
                "conditions": random.choice(["Sunny", "Partly Cloudy", "Cloudy", "Light Rain"]),
                "humidity": round(random.uniform(40, 60)),
                "wind_speed": round(random.uniform(0, 15)),
                "precipitation": round(random.uniform(0, 30))
            })
        
        # Update cache
        self.forecast_cache[cache_key] = forecast
        self.last_update = datetime.now()
        
        return forecast
    
    def set_default_zip(self, zip_code):
        """
        Set the default ZIP code.
        
        Args:
            zip_code: ZIP code
        """
        self.default_zip = zip_code
        logger.info(f"Set default ZIP code to {zip_code}")

class DatabaseService:
    """Database service for storing and retrieving data."""
    
    def __init__(self, db_path):
        """
        Initialize the database service.
        
        Args:
            db_path: Path to the database file
        """
        logger.info(f"Initializing Database Service with path: {db_path}")
        self.db_path = db_path
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # Load or create customers data
        self.customers_file = os.path.join(os.path.dirname(db_path), "customers.json")
        if os.path.exists(self.customers_file):
            try:
                with open(self.customers_file, 'r') as f:
                    self.customers = json.load(f)
                    # Convert string dates back to datetime objects
                    for customer in self.customers:
                        customer['created_at'] = datetime.fromisoformat(customer['created_at'])
                        customer['updated_at'] = datetime.fromisoformat(customer['updated_at'])
            except Exception as e:
                logger.error(f"Error loading customers data: {e}")
                self.customers = self._create_default_customers()
        else:
            self.customers = self._create_default_customers()
            self._save_customers()
        
        # Load or create readings data
        self.readings_file = os.path.join(os.path.dirname(db_path), "readings.json")
        if os.path.exists(self.readings_file):
            try:
                with open(self.readings_file, 'r') as f:
                    self.readings = json.load(f)
                    # Convert string dates back to datetime objects
                    for reading in self.readings:
                        reading['timestamp'] = datetime.fromisoformat(reading['timestamp'])
            except Exception as e:
                logger.error(f"Error loading readings data: {e}")
                self.readings = self._create_default_readings()
        else:
            self.readings = self._create_default_readings()
            self._save_readings()
    
    def _create_default_customers(self):
        """Create default customers data."""
        return [
            {
                "id": 1,
                "name": "John Doe",
                "email": "john@example.com",
                "phone": "555-123-4567",
                "address": "123 Main Street, Anytown, CA",
                "created_at": datetime.now() - timedelta(days=30),
                "updated_at": datetime.now() - timedelta(days=5),
                "pools": [
                    {
                        "id": 1,
                        "name": "Main Pool",
                        "type": "In-ground",
                        "volume": 20000,
                        "volume_unit": "gal",
                        "surface": "Plaster",
                        "sanitizer": "Chlorine"
                    }
                ]
            }
        ]
    
    def _create_default_readings(self):
        """Create default readings data."""
        readings = []
        for i in range(7):
            day = datetime.now() - timedelta(days=i)
            readings.append({
                "id": i + 1,
                "customer_id": 1,
                "pool_id": 1,
                "timestamp": day,
                "free_chlorine": round(random.uniform(1.0, 3.0), 1),
                "ph": round(random.uniform(7.2, 7.8), 1),
                "total_alkalinity": round(random.uniform(80, 120)),
                "calcium_hardness": round(random.uniform(200, 400)),
                "cyanuric_acid": round(random.uniform(30, 50)),
                "total_bromine": round(random.uniform(2, 6), 1),
                "salt": round(random.uniform(2700, 3400)),
                "temperature": round(random.uniform(75, 85), 1)
            })
        return readings
    
    def _save_customers(self):
        """Save customers data to file."""
        try:
            # Convert datetime objects to strings for JSON serialization
            customers_json = []
            for customer in self.customers:
                customer_copy = customer.copy()
                customer_copy['created_at'] = customer['created_at'].isoformat()
                customer_copy['updated_at'] = customer['updated_at'].isoformat()
                customers_json.append(customer_copy)
            
            with open(self.customers_file, 'w') as f:
                json.dump(customers_json, f, indent=2)
            logger.info(f"Saved customers data to {self.customers_file}")
        except Exception as e:
            logger.error(f"Error saving customers data: {e}")
    
    def _save_readings(self):
        """Save readings data to file."""
        try:
            # Convert datetime objects to strings for JSON serialization
            readings_json = []
            for reading in self.readings:
                reading_copy = reading.copy()
                reading_copy['timestamp'] = reading['timestamp'].isoformat()
                readings_json.append(reading_copy)
            
            with open(self.readings_file, 'w') as f:
                json.dump(readings_json, f, indent=2)
            logger.info(f"Saved readings data to {self.readings_file}")
        except Exception as e:
            logger.error(f"Error saving readings data: {e}")
    
    def get_all_customers(self):
        """Get all customers."""
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
            if customer['id'] == customer_id:
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
        # Generate a new ID
        new_id = max([c['id'] for c in self.customers], default=0) + 1
        
        # Create the new customer
        new_customer = {
            "id": new_id,
            "name": customer_data.get('name', ''),
            "email": customer_data.get('email', ''),
            "phone": customer_data.get('phone', ''),
            "address": customer_data.get('address', ''),
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "pools": []
        }
        
        # Add pool if provided
        if 'pool' in customer_data:
            pool_id = 1
            if self.customers:
                # Find the highest pool ID across all customers
                pool_id = max([p['id'] for c in self.customers for p in c.get('pools', [])], default=0) + 1
            
            new_customer['pools'].append({
                "id": pool_id,
                "name": customer_data['pool'].get('name', 'Main Pool'),
                "type": customer_data['pool'].get('type', 'In-ground'),
                "volume": float(customer_data['pool'].get('volume', 10000)),
                "volume_unit": customer_data['pool'].get('volume_unit', 'gal'),
                "surface": customer_data['pool'].get('surface', 'Plaster'),
                "sanitizer": customer_data['pool'].get('sanitizer', 'Chlorine')
            })
        
        # Add to the list
        self.customers.append(new_customer)
        
        # Save to file
        self._save_customers()
        
        return new_customer
    
    def update_customer(self, customer_id, customer_data):
        """
        Update an existing customer.
        
        Args:
            customer_id: Customer ID
            customer_data: Customer data dictionary
        
        Returns:
            Updated customer dictionary or None if not found
        """
        # Find the customer
        for i, customer in enumerate(self.customers):
            if customer['id'] == customer_id:
                # Update the customer
                self.customers[i].update({
                    "name": customer_data.get('name', customer['name']),
                    "email": customer_data.get('email', customer['email']),
                    "phone": customer_data.get('phone', customer['phone']),
                    "address": customer_data.get('address', customer['address']),
                    "updated_at": datetime.now()
                })
                
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
        # Find the customer
        for i, customer in enumerate(self.customers):
            if customer['id'] == customer_id:
                # Remove the customer
                del self.customers[i]
                
                # Save to file
                self._save_customers()
                
                return True
        
        return False
    
    def get_all_readings(self, customer_id=None, pool_id=None, days=None):
        """
        Get all readings, optionally filtered.
        
        Args:
            customer_id: Filter by customer ID
            pool_id: Filter by pool ID
            days: Filter by number of days back
        
        Returns:
            List of reading dictionaries
        """
        filtered_readings = self.readings
        
        # Filter by customer ID
        if customer_id is not None:
            filtered_readings = [r for r in filtered_readings if r.get('customer_id') == customer_id]
        
        # Filter by pool ID
        if pool_id is not None:
            filtered_readings = [r for r in filtered_readings if r.get('pool_id') == pool_id]
        
        # Filter by days
        if days is not None:
            cutoff_date = datetime.now() - timedelta(days=days)
            filtered_readings = [r for r in filtered_readings if r['timestamp'] >= cutoff_date]
        
        # Sort by timestamp (newest first)
        filtered_readings.sort(key=lambda r: r['timestamp'], reverse=True)
        
        return filtered_readings
    
    def get_latest_reading(self, customer_id=None, pool_id=None):
        """
        Get the latest reading.
        
        Args:
            customer_id: Filter by customer ID
            pool_id: Filter by pool ID
        
        Returns:
            Latest reading dictionary or None if no readings
        """
        readings = self.get_all_readings(customer_id, pool_id)
        if readings:
            return readings[0]
        return None
    
    def add_reading(self, reading_data):
        """
        Add a new reading.
        
        Args:
            reading_data: Reading data dictionary
        
        Returns:
            New reading dictionary
        """
        # Generate a new ID
        new_id = max([r['id'] for r in self.readings], default=0) + 1
        
        # Create the new reading
        new_reading = {
            "id": new_id,
            "customer_id": reading_data.get('customer_id', 1),
            "pool_id": reading_data.get('pool_id', 1),
            "timestamp": datetime.now(),
            "free_chlorine": float(reading_data.get('free_chlorine', 0)),
            "ph": float(reading_data.get('ph', 7.0)),
            "total_alkalinity": float(reading_data.get('total_alkalinity', 0)),
            "calcium_hardness": float(reading_data.get('calcium_hardness', 0)),
            "cyanuric_acid": float(reading_data.get('cyanuric_acid', 0)),
            "total_bromine": float(reading_data.get('total_bromine', 0)),
            "salt": float(reading_data.get('salt', 0)),
            "temperature": float(reading_data.get('temperature', 0))
        }
        
        # Add to the list
        self.readings.append(new_reading)
        
        # Save to file
        self._save_readings()
        
        return new_reading

class ChemicalParameters:
    """Chemical parameters and ideal ranges."""
    
    def __init__(self):
        """Initialize chemical parameters."""
        self.parameters = {
            "free_chlorine": {
                "name": "Free Chlorine",
                "unit": "ppm",
                "ideal_range": {"min": 1.0, "max": 3.0},
                "recommendations": {
                    "low": "Add chlorine to increase the level. Consider using liquid chlorine or chlorine tablets.",
                    "high": "Stop adding chlorine and allow levels to decrease naturally. Consider partial water replacement if levels are extremely high.",
                    "ok": "Chlorine levels are good. Continue regular maintenance."
                },
                "warnings": {
                    "low": "Low chlorine levels may lead to bacterial growth and algae formation.",
                    "high": "High chlorine levels can cause skin and eye irritation, and may damage pool equipment."
                }
            },
            "ph": {
                "name": "pH",
                "unit": "",
                "ideal_range": {"min": 7.2, "max": 7.8},
                "recommendations": {
                    "low": "Add pH increaser (sodium carbonate) to raise the pH level.",
                    "high": "Add pH decreaser (sodium bisulfate) to lower the pH level.",
                    "ok": "pH levels are good. Continue regular maintenance."
                },
                "warnings": {
                    "low": "Low pH can cause eye and skin irritation, corrosion of metal components, and damage to pool surfaces.",
                    "high": "High pH can reduce chlorine effectiveness, cause cloudy water, and lead to scale formation."
                }
            },
            "total_alkalinity": {
                "name": "Total Alkalinity",
                "unit": "ppm",
                "ideal_range": {"min": 80, "max": 120},
                "recommendations": {
                    "low": "Add alkalinity increaser (sodium bicarbonate) to raise the alkalinity level.",
                    "high": "Add pH decreaser (sodium bisulfate) to lower the alkalinity level.",
                    "ok": "Alkalinity levels are good. Continue regular maintenance."
                },
                "warnings": {
                    "low": "Low alkalinity can cause pH bounce, corrosion, and damage to pool surfaces.",
                    "high": "High alkalinity can lead to high pH, cloudy water, and scale formation."
                }
            },
            "calcium_hardness": {
                "name": "Calcium Hardness",
                "unit": "ppm",
                "ideal_range": {"min": 200, "max": 400},
                "recommendations": {
                    "low": "Add calcium hardness increaser to raise the hardness level.",
                    "high": "Partially drain and refill the pool with fresh water to dilute the hardness level.",
                    "ok": "Hardness levels are good. Continue regular maintenance."
                },
                "warnings": {
                    "low": "Low hardness can cause corrosion of pool surfaces and equipment.",
                    "high": "High hardness can lead to cloudy water and scale formation."
                }
            },
            "cyanuric_acid": {
                "name": "Cyanuric Acid",
                "unit": "ppm",
                "ideal_range": {"min": 30, "max": 50},
                "recommendations": {
                    "low": "Add cyanuric acid stabilizer to increase the level.",
                    "high": "Partially drain and refill the pool with fresh water to dilute the cyanuric acid level.",
                    "ok": "Cyanuric acid levels are good. Continue regular maintenance."
                },
                "warnings": {
                    "low": "Low cyanuric acid levels can lead to rapid chlorine depletion due to sunlight.",
                    "high": "High cyanuric acid levels can reduce chlorine effectiveness (chlorine lock)."
                }
            },
            "total_bromine": {
                "name": "Total Bromine",
                "unit": "ppm",
                "ideal_range": {"min": 3.0, "max": 5.0},
                "recommendations": {
                    "low": "Add bromine tablets or granules to increase the level.",
                    "high": "Stop adding bromine and allow levels to decrease naturally.",
                    "ok": "Bromine levels are good. Continue regular maintenance."
                },
                "warnings": {
                    "low": "Low bromine levels may lead to bacterial growth and algae formation.",
                    "high": "High bromine levels can cause skin and eye irritation."
                }
            },
            "salt": {
                "name": "Salt",
                "unit": "ppm",
                "ideal_range": {"min": 2700, "max": 3400},
                "recommendations": {
                    "low": "Add salt to increase the level according to your salt system manufacturer's recommendations.",
                    "high": "Partially drain and refill the pool with fresh water to dilute the salt level.",
                    "ok": "Salt levels are good. Continue regular maintenance."
                },
                "warnings": {
                    "low": "Low salt levels can reduce the effectiveness of salt chlorine generators.",
                    "high": "High salt levels can damage pool equipment and lead to corrosion."
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
        """Get all parameters."""
        return self.parameters
    
    def get_status(self, name, value):
        """
        Get the status of a parameter based on its value.
        
        Args:
            name: Parameter name
            value: Parameter value
        
        Returns:
            Status string: "low", "high", or "ok"
        """
        parameter = self.get_parameter(name)
        if not parameter:
            return "unknown"
        
        ideal_range = parameter['ideal_range']
        if value < ideal_range['min']:
            return "low"
        elif value > ideal_range['max']:
            return "high"
        else:
            return "ok"
    
    def get_recommendation(self, name, value):
        """
        Get a recommendation for a parameter based on its value.
        
        Args:
            name: Parameter name
            value: Parameter value
        
        Returns:
            Recommendation string
        """
        parameter = self.get_parameter(name)
        if not parameter or 'recommendations' not in parameter:
            return "No recommendation available."
        
        status = self.get_status(name, value)
        return parameter['recommendations'].get(status, "No recommendation available.")
    
    def get_warning(self, name, value):
        """
        Get a warning for a parameter based on its value.
        
        Args:
            name: Parameter name
            value: Parameter value
        
        Returns:
            Warning string
        """
        parameter = self.get_parameter(name)
        if not parameter or 'warnings' not in parameter:
            return "No warning available."
        
        status = self.get_status(name, value)
        if status == "ok":
            return "No warnings. Chemical levels are within the ideal range."
        
        return parameter['warnings'].get(status, "No warning available.")

class DeepBluePoolApp:
    """Main application class for Deep Blue Pool Chemistry."""
    
    def __init__(self):
        """Initialize the application."""
        logger.info("Initializing Deep Blue Pool Chemistry Application")
        
        # Initialize services
        self.db_service = DatabaseService("data/pool_data.db")
        self.chemical_parameters = ChemicalParameters()
        self.arduino_monitor = ArduinoMonitor()
        self.weather_service = WeatherService()
        
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
        self.nav_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Create navigation buttons
        self.nav_buttons = []
        nav_options = [
            ("Customer Information", self.show_customer_info),
            ("Recommendations", self.show_recommendations),
            ("Test Strip Analysis", self.show_test_strip),
            ("Trends & History", self.show_trends)
        ]
        
        for text, command in nav_options:
            button = ttk.Button(self.nav_frame, text=text, command=command)
            button.pack(side=tk.LEFT, padx=5)
            self.nav_buttons.append(button)
        
        # Create content frame
        self.content_frame = ttk.Frame(self.main_frame)
        self.content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create frames for each section
        self.customer_frame = ttk.Frame(self.content_frame)
        self.recommendations_frame = ttk.Frame(self.content_frame)
        self.test_strip_frame = ttk.Frame(self.content_frame)
        self.trends_frame = ttk.Frame(self.content_frame)
        
        # Initialize customer information section
        self.setup_customer_info()
        
        # Initialize weather forecast section
        self.setup_weather_forecast()
        
        # Initialize recommendations section
        self.setup_recommendations()
        
        # Initialize test strip section
        self.setup_test_strip()
        
        # Initialize trends section
        self.setup_trends()
        
        # Show customer information by default
        self.show_customer_info()
        
        # Set up Arduino data handling
        self.arduino_data_var = tk.StringVar(value="Not connected")
        self.setup_arduino_monitor()
        
        # Update weather every 30 minutes
        self.update_weather()
        self.root.after(1800000, self.update_weather)
    
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
        
        ttk.Label(customer_select_frame, text="Customer:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        
        # Get all customers
        customers = self.db_service.get_all_customers()
        customer_names = [c['name'] for c in customers]
        
        self.customer_var = tk.StringVar()
        if customer_names:
            self.customer_var.set(customer_names[0])
        
        customer_combo = ttk.Combobox(customer_select_frame, textvariable=self.customer_var, values=customer_names)
        customer_combo.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        customer_combo.bind("<<ComboboxSelected>>", self.on_customer_selected)
        
        # Customer details
        details_frame = ttk.Frame(customer_select_frame)
        details_frame.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
        
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
        
        # Pool type
        ttk.Label(details_frame, text="Pool Type:").grid(row=3, column=0, padx=5, pady=2, sticky="w")
        self.pool_type_var = tk.StringVar()
        ttk.Label(details_frame, textvariable=self.pool_type_var).grid(row=3, column=1, padx=5, pady=2, sticky="w")
        
        # Pool volume
        ttk.Label(details_frame, text="Pool Volume:").grid(row=4, column=0, padx=5, pady=2, sticky="w")
        self.pool_volume_var = tk.StringVar()
        ttk.Label(details_frame, textvariable=self.pool_volume_var).grid(row=4, column=1, padx=5, pady=2, sticky="w")
        
        # Pool volume input frame
        volume_frame = ttk.LabelFrame(left_frame, text="Pool Volume")
        volume_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(volume_frame, text="Pool Volume (gallons):").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.volume_var = tk.StringVar()
        volume_entry = ttk.Entry(volume_frame, textvariable=self.volume_var)
        volume_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        # Chemical parameters frame
        chem_frame = ttk.LabelFrame(left_frame, text="Chemical Parameters")
        chem_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create chemical parameter inputs
        self.chemical_vars = {}
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
        
        # Buttons
        button_frame = ttk.Frame(chem_frame)
        button_frame.grid(row=6, column=0, columnspan=3, padx=5, pady=10)
        
        ttk.Button(button_frame, text="Save Reading", command=self.save_reading).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Get Recommendations", command=self.get_recommendations).pack(side=tk.LEFT, padx=5)
        
        # If we have customers, select the first one
        if customers:
            self.select_customer(customers[0])
    
    def setup_weather_forecast(self):
        """Set up the weather forecast section."""
        # Create weather frame
        self.weather_frame = ttk.LabelFrame(self.customer_frame, text="Weather Analysis & Forecast")
        self.weather_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # ZIP code input
        zip_frame = ttk.Frame(self.weather_frame)
        zip_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(zip_frame, text="ZIP Code:").pack(side=tk.LEFT, padx=5)
        self.zip_var = tk.StringVar(value="10001")
        zip_entry = ttk.Entry(zip_frame, textvariable=self.zip_var, width=10)
        zip_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(zip_frame, text="Update Weather", command=self.update_weather).pack(side=tk.LEFT, padx=5)
        
        # Create forecast frame
        forecast_frame = ttk.Frame(self.weather_frame)
        forecast_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create day frames
        self.day_frames = []
        for i in range(5):
            day_frame = ttk.LabelFrame(forecast_frame, text=f"Day {i+1}")
            day_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=2)
            
            # Date
            self.day_frames.append({
                "date": ttk.Label(day_frame, text=""),
                "temp_high": ttk.Label(day_frame, text=""),
                "temp_low": ttk.Label(day_frame, text=""),
                "conditions": ttk.Label(day_frame, text=""),
                "humidity": ttk.Label(day_frame, text=""),
                "precip": ttk.Label(day_frame, text="")
            })
            
            self.day_frames[i]["date"].pack(pady=2)
            self.day_frames[i]["temp_high"].pack(pady=2)
            self.day_frames[i]["temp_low"].pack(pady=2)
            self.day_frames[i]["conditions"].pack(pady=2)
            self.day_frames[i]["humidity"].pack(pady=2)
            self.day_frames[i]["precip"].pack(pady=2)
    
    def setup_recommendations(self):
        """Set up the recommendations section."""
        # Create recommendations frame
        recommendations_frame = ttk.Frame(self.recommendations_frame)
        recommendations_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create left and right frames
        left_frame = ttk.Frame(recommendations_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        right_frame = ttk.Frame(recommendations_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # Create recommendations text
        recommendations_label = ttk.LabelFrame(left_frame, text="Recommendations")
        recommendations_label.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        
        self.recommendations_text = scrolledtext.ScrolledText(recommendations_label, wrap=tk.WORD)
        self.recommendations_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.recommendations_text.insert(tk.END, "Enter chemical parameters and click 'Get Recommendations' to see recommendations.")
        self.recommendations_text.config(state=tk.DISABLED)
        
        # Create warnings text
        warnings_label = ttk.LabelFrame(right_frame, text="Warnings & Precautions")
        warnings_label.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        
        self.warnings_text = scrolledtext.ScrolledText(warnings_label, wrap=tk.WORD)
        self.warnings_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.warnings_text.insert(tk.END, "Enter chemical parameters and click 'Get Recommendations' to see warnings.")
        self.warnings_text.config(state=tk.DISABLED)
        
        # Create procedures text
        procedures_label = ttk.LabelFrame(recommendations_frame, text="Procedures")
        procedures_label.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
        
        self.procedures_text = scrolledtext.ScrolledText(procedures_label, wrap=tk.WORD)
        self.procedures_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.procedures_text.insert(tk.END, "Enter chemical parameters and click 'Get Recommendations' to see procedures.")
        self.procedures_text.config(state=tk.DISABLED)
    
    def setup_test_strip(self):
        """Set up the test strip section."""
        # Create test strip frame
        test_strip_frame = ttk.Frame(self.test_strip_frame)
        test_strip_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create left and right frames
        left_frame = ttk.Frame(test_strip_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        right_frame = ttk.Frame(test_strip_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # Create upload frame
        upload_frame = ttk.LabelFrame(left_frame, text="Test Strip Analysis")
        upload_frame.pack(fill=tk.BOTH, expand=True)
        
        # Add instructions
        instructions = ttk.Label(
            upload_frame,
            text="Upload an image of your test strip to analyze the chemical levels.",
            wraplength=400
        )
        instructions.pack(pady=10)
        
        # Add upload button
        upload_button = ttk.Button(
            upload_frame,
            text="Upload Test Strip Image",
            command=self.upload_test_strip
        )
        upload_button.pack(pady=10)
        
        # Add camera button
        camera_button = ttk.Button(
            upload_frame,
            text="Take Photo with Camera",
            command=self.take_photo
        )
        camera_button.pack(pady=10)
        
        # Add test strip type selection
        type_frame = ttk.Frame(upload_frame)
        type_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(type_frame, text="Test Strip Type:").pack(side=tk.LEFT, padx=5)
        strip_type = ttk.Combobox(type_frame, values=["Standard 6-in-1", "Chlorine Only", "pH Only", "Bromine"])
        strip_type.current(0)
        strip_type.pack(side=tk.LEFT, padx=5)
        
        # Create results frame
        results_frame = ttk.LabelFrame(right_frame, text="Analysis Results")
        results_frame.pack(fill=tk.BOTH, expand=True)
        
        # Add placeholder text
        self.results_text = scrolledtext.ScrolledText(results_frame, wrap=tk.WORD)
        self.results_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.results_text.insert(tk.END, "Upload a test strip image to see the analysis results.")
        self.results_text.config(state=tk.DISABLED)
        
        # Create visualization frame
        viz_frame = ttk.LabelFrame(test_strip_frame, text="Test Strip Visualization")
        viz_frame.pack(fill=tk.X, pady=10)
        
        # Create a canvas for the test strip visualization
        self.strip_canvas = tk.Canvas(viz_frame, width=600, height=100)
        self.strip_canvas.pack(fill=tk.X, padx=10, pady=10)
        
        # Draw empty test strip
        self.draw_empty_test_strip()
    
    def setup_trends(self):
        """Set up the trends section."""
        # Create trends frame
        trends_frame = ttk.Frame(self.trends_frame)
        trends_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create chart frame
        chart_frame = ttk.LabelFrame(trends_frame, text="Chemical Trends")
        chart_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Create figure for charts
        self.fig = Figure(figsize=(10, 6), dpi=100)
        
        # Create canvas for figure
        self.canvas = FigureCanvasTkAgg(self.fig, master=chart_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Create controls frame
        controls_frame = ttk.Frame(trends_frame)
        controls_frame.pack(fill=tk.X)
        
        # Create time range selection
        ttk.Label(controls_frame, text="Time Range:").pack(side=tk.LEFT, padx=5)
        self.time_range_var = tk.StringVar(value="7 Days")
        time_range = ttk.Combobox(controls_frame, textvariable=self.time_range_var, 
                                 values=["7 Days", "30 Days", "90 Days", "1 Year"])
        time_range.pack(side=tk.LEFT, padx=5)
        time_range.bind("<<ComboboxSelected>>", self.update_trends)
        
        # Create parameter selection
        ttk.Label(controls_frame, text="Parameter:").pack(side=tk.LEFT, padx=5)
        self.parameter_var = tk.StringVar(value="pH")
        parameter = ttk.Combobox(controls_frame, textvariable=self.parameter_var, 
                               values=["pH", "Free Chlorine", "Total Alkalinity", "Calcium Hardness", 
                                      "Cyanuric Acid", "Salt", "Temperature"])
        parameter.pack(side=tk.LEFT, padx=5)
        parameter.bind("<<ComboboxSelected>>", self.update_trends)
        
        # Create update button
        ttk.Button(controls_frame, text="Update Chart", command=self.update_trends).pack(side=tk.LEFT, padx=5)
    
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
            # Expected format: "pH:7.2,Temp:78.5,ORP:650"
            values = {}
            for item in data.split(','):
                key, value = item.split(':')
                values[key] = float(value)
            
            # Update chemical parameters if available
            if 'pH' in values:
                self.chemical_vars['ph'].set(str(values['pH']))
            
            if 'Temp' in values:
                self.chemical_vars['temperature'].set(str(values['Temp']))
            
            # ORP can be used to estimate free chlorine
            if 'ORP' in values:
                # Rough estimation: ORP 650 mV \u2248 1.0 ppm free chlorine
                free_chlorine = (values['ORP'] - 600) / 50
                if free_chlorine < 0:
                    free_chlorine = 0
                self.chemical_vars['free_chlorine'].set(str(round(free_chlorine, 1)))
        
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
            self.volume_var.set("")
        
        # Get latest reading for this customer
        reading = self.db_service.get_latest_reading(customer['id'])
        if reading:
            # Update chemical parameters
            self.chemical_vars['ph'].set(str(reading['ph']))
            self.chemical_vars['free_chlorine'].set(str(reading['free_chlorine']))
            self.chemical_vars['total_alkalinity'].set(str(reading['total_alkalinity']))
            self.chemical_vars['calcium_hardness'].set(str(reading['calcium_hardness']))
            self.chemical_vars['cyanuric_acid'].set(str(reading['cyanuric_acid']))
            self.chemical_vars['salt'].set(str(reading['salt']))
        else:
            # Clear chemical parameters
            for var in self.chemical_vars.values():
                var.set("")
    
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
        
        # Get recommendations and warnings
        recommendations = []
        warnings = []
        procedures = []
        
        for field, value in values.items():
            # Skip empty values
            if value == 0:
                continue
                
            # Get parameter info
            parameter = self.chemical_parameters.get_parameter(field)
            if not parameter:
                continue
                
            name = parameter['name']
            
            # Get status
            status = self.chemical_parameters.get_status(field, value)
            
            # Get recommendation
            recommendation = self.chemical_parameters.get_recommendation(field, value)
            if recommendation:
                recommendations.append(f"{name}: {recommendation}")
            
            # Get warning
            warning = self.chemical_parameters.get_warning(field, value)
            if warning and status != "ok":
                warnings.append(f"{name}: {warning}")
        
        # Add general procedures
        if values.get('ph', 0) < 7.2:
            procedures.append("1. Test the pH and total alkalinity.")
            procedures.append("2. Add pH increaser (sodium carbonate) according to the product instructions.")
            procedures.append("3. Run the circulation system for at least 4 hours.")
            procedures.append("4. Retest the pH and adjust if necessary.")
        elif values.get('ph', 0) > 7.8:
            procedures.append("1. Test the pH and total alkalinity.")
            procedures.append("2. Add pH decreaser (sodium bisulfate) according to the product instructions.")
            procedures.append("3. Run the circulation system for at least 4 hours.")
            procedures.append("4. Retest the pH and adjust if necessary.")
        
        if values.get('free_chlorine', 0) < 1.0:
            procedures.append("1. Test the free chlorine level.")
            procedures.append("2. Add chlorine (liquid chlorine or chlorine tablets) according to the product instructions.")
            procedures.append("3. Run the circulation system for at least 4 hours.")
            procedures.append("4. Retest the free chlorine level and adjust if necessary.")
        elif values.get('free_chlorine', 0) > 3.0:
            procedures.append("1. Stop adding chlorine.")
            procedures.append("2. Leave the pool uncovered and exposed to sunlight.")
            procedures.append("3. Run the circulation system for at least 4 hours.")
            procedures.append("4. Retest the free chlorine level after 24 hours.")
        
        # Insert recommendations, warnings, and procedures
        if recommendations:
            self.recommendations_text.insert(tk.END, "\
".join(recommendations))
        else:
            self.recommendations_text.insert(tk.END, "All chemical levels are within the ideal range. Continue regular maintenance.")
        
        if warnings:
            self.warnings_text.insert(tk.END, "\
".join(warnings))
        else:
            self.warnings_text.insert(tk.END, "No warnings. All chemical levels are within the ideal range.")
        
        if procedures:
            self.procedures_text.insert(tk.END, "\
".join(procedures))
        else:
            self.procedures_text.insert(tk.END, "No specific procedures needed. Continue regular maintenance.")
        
        # Disable text widgets
        self.recommendations_text.config(state=tk.DISABLED)
        self.warnings_text.config(state=tk.DISABLED)
        self.procedures_text.config(state=tk.DISABLED)
    
    def draw_empty_test_strip(self):
        """Draw an empty test strip on the canvas."""
        # Clear canvas
        self.strip_canvas.delete("all")
        
        # Draw strip background
        self.strip_canvas.create_rectangle(50, 20, 550, 80, fill="white", outline="black")
        
        # Draw pads
        pad_width = 60
        pad_spacing = 20
        pad_names = ["Free Cl", "pH", "Alk", "Hard", "CYA", "Br"]
        
        for i, name in enumerate(pad_names):
            x = 70 + i * (pad_width + pad_spacing)
            self.strip_canvas.create_rectangle(x, 30, x + pad_width, 70, fill="lightgray", outline="black")
            self.strip_canvas.create_text(x + pad_width/2, 85, text=name)
    
    def draw_test_strip_results(self, results):
        """
        Draw test strip results on the canvas.
        
        Args:
            results: Dictionary of test results
        """
        # Clear canvas
        self.strip_canvas.delete("all")
        
        # Draw strip background
        self.strip_canvas.create_rectangle(50, 20, 550, 80, fill="white", outline="black")
        
        # Draw pads
        pad_width = 60
        pad_spacing = 20
        pad_data = [
            ("Free Chlorine", "free_chlorine"),
            ("pH", "ph"),
            ("Total Alkalinity", "total_alkalinity"),
            ("Calcium Hardness", "calcium_hardness"),
            ("Cyanuric Acid", "cyanuric_acid"),
            ("Total Bromine", "total_bromine")
        ]
        
        for i, (name, key) in enumerate(pad_data):
            x = 70 + i * (pad_width + pad_spacing)
            
            # Get value and status
            value = results[name]["value"]
            chemical_key = key.lower()
            status = self.chemical_parameters.get_status(chemical_key, value)
            
            # Determine color
            color = "green" if status == "ok" else "red" if status == "high" else "yellow"
            
            # Draw pad
            self.strip_canvas.create_rectangle(x, 30, x + pad_width, 70, fill=color, outline="black")
            self.strip_canvas.create_text(x + pad_width/2, 50, text=str(value))
            self.strip_canvas.create_text(x + pad_width/2, 85, text=name.split()[0])
    
    def upload_test_strip(self):
        """Handle test strip image upload."""
        # In a real application, this would open a file dialog
        # For this simple version, we'll just simulate the analysis
        
        # Clear the results text
        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, "Analyzing test strip...")
        self.results_text.config(state=tk.DISABLED)
        self.root.update()
        
        # Simulate analysis delay
        time.sleep(1)
        
        # Generate random results
        results = {
            "Free Chlorine": {"value": round(random.uniform(1.0, 3.0), 1), "unit": "ppm"},
            "pH": {"value": round(random.uniform(7.0, 8.0), 1), "unit": ""},
            "Total Alkalinity": {"value": round(random.uniform(80, 120)), "unit": "ppm"},
            "Calcium Hardness": {"value": round(random.uniform(200, 400)), "unit": "ppm"},
            "Cyanuric Acid": {"value": round(random.uniform(30, 50)), "unit": "ppm"},
            "Total Bromine": {"value": round(random.uniform(3, 5), 1), "unit": "ppm"}
        }
        
        # Update results text
        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete(1.0, tk.END)
        
        for name, data in results.items():
            status = self.chemical_parameters.get_status(name.lower().replace(" ", "_"), data["value"])
            status_text = "OK" if status == "ok" else "HIGH" if status == "high" else "LOW"
            self.results_text.insert(tk.END, f"{name}: {data['value']} {data['unit']} - {status_text}\
")
        
        # Add save button text
        self.results_text.insert(tk.END, "\
")
        self.results_text.insert(tk.END, "Click 'Save Results' to save these readings.")
        
        self.results_text.config(state=tk.DISABLED)
        
        # Draw test strip visualization
        self.draw_test_strip_results(results)
        
        # Add save button
        save_button = ttk.Button(
            self.test_strip_frame,
            text="Save Results",
            command=lambda: self.save_test_strip_results(results)
        )
        save_button.pack(pady=10)
    
    def save_test_strip_results(self, results):
        """
        Save test strip results as a new reading.
        
        Args:
            results: Dictionary of test results
        """
        # Convert results to reading data
        reading_data = {
            "customer_id": 1,  # Default
            "pool_id": 1,  # Default
            "free_chlorine": results["Free Chlorine"]["value"],
            "ph": results["pH"]["value"],
            "total_alkalinity": results["Total Alkalinity"]["value"],
            "calcium_hardness": results["Calcium Hardness"]["value"],
            "cyanuric_acid": results["Cyanuric Acid"]["value"],
            "total_bromine": results["Total Bromine"]["value"]
        }
        
        # Add reading
        self.db_service.add_reading(reading_data)
        
        # Show confirmation
        messagebox.showinfo("Success", "Test strip results saved as a new reading.")
        
        # Update trends
        self.update_trends()
        
        # Update chemical parameters
        for name, var in self.chemical_vars.items():
            if name == "free_chlorine":
                var.set(str(results["Free Chlorine"]["value"]))
            elif name == "ph":
                var.set(str(results["pH"]["value"]))
            elif name == "total_alkalinity":
                var.set(str(results["Total Alkalinity"]["value"]))
            elif name == "calcium_hardness":
                var.set(str(results["Calcium Hardness"]["value"]))
            elif name == "cyanuric_acid":
                var.set(str(results["Cyanuric Acid"]["value"]))
            elif name == "total_bromine":
                var.set(str(results["Total Bromine"]["value"]))
    
    def take_photo(self):
        """Simulate taking a photo with a camera."""
        messagebox.showinfo("Camera", "This feature would activate the camera to take a photo of a test strip.")
        # In a real application, this would activate the camera
        # For this simple version, we'll just call the upload function
        self.upload_test_strip()
    
    def update_trends(self, event=None):
        """Update the trends chart."""
        # Clear the figure
        self.fig.clear()
        
        # Get time range
        time_range = self.time_range_var.get()
        days = 7
        if time_range == "30 Days":
            days = 30
        elif time_range == "90 Days":
            days = 90
        elif time_range == "1 Year":
            days = 365
        
        # Get parameter
        parameter = self.parameter_var.get()
        param_key = parameter.lower().replace(" ", "_")
        
        # Get readings
        readings = self.db_service.get_all_readings(days=days)
        
        if not readings:
            # No data
            ax = self.fig.add_subplot(111)
            ax.text(0.5, 0.5, "No data available", ha="center", va="center")
            self.canvas.draw()
            return
        
        # Extract data
        dates = [r['timestamp'] for r in readings]
        values = [r.get(param_key, 0) for r in readings]
        
        # Create subplot
        ax = self.fig.add_subplot(111)
        
        # Plot data
        ax.plot(dates, values, 'b-')
        
        # Get parameter info
        param_info = self.chemical_parameters.get_parameter(param_key)
        if param_info:
            # Add ideal range
            ideal_min = param_info['ideal_range']['min']
            ideal_max = param_info['ideal_range']['max']
            ax.axhspan(ideal_min, ideal_max, alpha=0.2, color='green')
            
            # Set y-axis limits
            y_min = min(min(values), ideal_min) * 0.9
            y_max = max(max(values), ideal_max) * 1.1
            ax.set_ylim(y_min, y_max)
            
            # Add unit to y-axis label
            unit = param_info['unit']
            if unit:
                ax.set_ylabel(f"{parameter} ({unit})")
            else:
                ax.set_ylabel(parameter)
        else:
            ax.set_ylabel(parameter)
        
        # Format x-axis
        ax.set_xlabel("Date")
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        ax.xaxis.set_major_locator(mdates.DayLocator(interval=max(1, days // 10)))
        self.fig.autofmt_xdate()
        
        # Add grid
        ax.grid(True)
        
        # Add title
        ax.set_title(f"{parameter} Trend - Last {days} Days")
        
        # Draw the canvas
        self.canvas.draw()
    
    def update_weather(self):
        """Update the weather forecast."""
        try:
            # Get ZIP code
            zip_code = self.zip_var.get()
            
            # Update weather service default ZIP
            self.weather_service.set_default_zip(zip_code)
            
            # Get forecast
            forecast = self.weather_service.get_forecast(zip_code)
            
            # Update day frames
            for i, day in enumerate(forecast[:5]):
                date_str = day['date'].strftime('%a, %b %d')
                self.day_frames[i]["date"].config(text=date_str)
                self.day_frames[i]["temp_high"].config(text=f"Temperature: {day['high_temp']}\u00b0F")
                self.day_frames[i]["temp_low"].config(text=f"Low: {day['low_temp']}\u00b0F")
                self.day_frames[i]["conditions"].config(text=f"Conditions: {day['conditions']}")
                self.day_frames[i]["humidity"].config(text=f"Humidity: {day['humidity']}%")
                self.day_frames[i]["precip"].config(text=f"Precip: {day['precipitation']}%")
            
        except Exception as e:
            messagebox.showerror("Weather Error", f"Error updating weather: {e}")
            logger.error(f"Error updating weather: {e}")
    
    def show_customer_info(self):
        """Show the customer information section."""
        self.customer_frame.pack(fill=tk.BOTH, expand=True)
        self.recommendations_frame.pack_forget()
        self.test_strip_frame.pack_forget()
        self.trends_frame.pack_forget()
    
    def show_recommendations(self):
        """Show the recommendations section."""
        self.customer_frame.pack_forget()
        self.recommendations_frame.pack(fill=tk.BOTH, expand=True)
        self.test_strip_frame.pack_forget()
        self.trends_frame.pack_forget()
    
    def show_test_strip(self):
        """Show the test strip section."""
        self.customer_frame.pack_forget()
        self.recommendations_frame.pack_forget()
        self.test_strip_frame.pack(fill=tk.BOTH, expand=True)
        self.trends_frame.pack_forget()
    
    def show_trends(self):
        """Show the trends section."""
        self.customer_frame.pack_forget()
        self.recommendations_frame.pack_forget()
        self.test_strip_frame.pack_forget()
        self.trends_frame.pack(fill=tk.BOTH, expand=True)
        
        # Update trends
        self.update_trends()
    
    def run(self):
        """Run the application."""
        self.root.mainloop()

def main():
    """Main entry point for the application."""
    app = DeepBluePoolApp()
    app.run()

if __name__ == "__main__":
    main()
