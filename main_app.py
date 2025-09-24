# main_app.py

import os
import sys
import json
import time
import logging
import threading
from datetime import datetime, timedelta
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import urllib3
import requests
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image, ImageTk
import csv
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.utils import formatdate
import openpyxl
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import zipfile
import uuid

# --- START: Environment Variable Loading ---
from dotenv import load_dotenv

dotenv_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=dotenv_path)
# --- END: Environment Variable Loading ---

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Constants (with fallbacks)
DEFAULT_WINDOW_SIZE = (1400, 1000)
MIN_WINDOW_SIZE = (800, 600)
WEATHER_API_KEY_NAME = os.environ.get("WEATHER_API_KEY")
COLOR_SCHEME = {
    'primary': "#2196F3",
    'secondary': "#BBDEFB",
    'success': "#4CAF50",
    'warning': "#FFC107",
    'danger': "#F44336",
    'info': "#03A9F4",
    'background': "#F5F5F5"
}

# Utility Functions (with fallbacks)
def generate_key():
    """Fallback key generation function"""
    import os
    return os.urandom(32)

def encrypt_data(data, key):
    """Fallback encryption function"""
    print("Warning: Using fallback encryption (no actual encryption)")
    return data

def decrypt_data(data, key):
    """Fallback decryption function"""
    print("Warning: Using fallback decryption (no actual decryption)")
    return data

def save_json(data, file_path):
    """Fallback JSON save function"""
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=4)
        return True
    except Exception as e:
        print(f"Error saving JSON: {e}")
        return False

def load_json(file_path, default=None):
    """Fallback JSON load function"""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception:
        return default or {}

def create_backup(source_path, backup_dir):
    """Fallback backup function"""
    try:
        import shutil
        os.makedirs(backup_dir, exist_ok=True)
        backup_file = os.path.join(backup_dir, os.path.basename(source_path))
        shutil.copy2(source_path, backup_file)
        return backup_file
    except Exception as e:
        print(f"Error creating backup: {e}")
        return None

# Import other modules (with fallbacks)

class WaterTester:  # Fallback WaterTester
    def __init__(self):
        self.pool_volume = 10000

    def set_pool_volume(self, volume):
        self.pool_volume = volume

    def analyze_ph(self, ph):
        if ph < 7.2:
            return {
                "current": ph,
                "ideal_range": (7.2, 7.8),
                "direction": "low",
                "adjustment": "increase",
                "chemical": "Soda Ash",
                "dosage": f"{(7.2 - ph) * 20:.1f} oz"
            }
        elif ph > 7.8:
            return {
                "current": ph,
                "ideal_range": (7.2, 7.8),
                "direction": "high",
                "adjustment": "decrease",
                "chemical": "Muriatic Acid",
                "dosage": f"{(ph - 7.8) * 20:.1f} oz"
            }
        else:
            return {
                "current": ph,
                "ideal_range": (7.2, 7.8),
                "direction": "normal",
                "adjustment": "none",
                "chemical": None,
                "dosage": "No adjustment needed"
            }

    def analyze_chlorine(self, chlorine):
        if chlorine < 1.0:
            return {
                "current": chlorine,
                "ideal_range": (1.0, 3.0),
                "direction": "low",
                "adjustment": "increase",
                "chemical": "Liquid Chlorine",
                "dosage": f"{(1.0 - chlorine) * 30:.1f} oz"
            }
        elif chlorine > 3.0:
            return {
                "current": chlorine,
                "ideal_range": (1.0, 3.0),
                "direction": "high",
                "adjustment": "decrease",
                "chemical": None,
                "dosage": "Allow chlorine to dissipate naturally"
            }
        else:
            return {
                "current": chlorine,
                "ideal_range": (1.0, 3.0),
                "direction": "normal",
                "adjustment": "none",
                "chemical": None,
                "dosage": "No adjustment needed"
            }

class DataManager:  # Fallback DataManager
    def __init__(self, database_name):
        self.database_name = database_name

    def insert_reading(self, temperature, potential_hydrogen, chlorine):
        print(f"Inserting reading: temp={temperature}, pH={potential_hydrogen}, chlorine={chlorine}")

    def close_connection(self):
        pass

class WeatherAPI:
    def __init__(self, api_key):
        self.api_key = api_key
        print("Using WeatherAPI with key:", api_key)

    def get_weather_data(self, zip_code):
        import requests
        import json
        import os
        import time
        from pathlib import Path
        
        # Create a cache directory if it doesn't exist
        cache_dir = Path("cache")
        cache_dir.mkdir(exist_ok=True)
        
        # Create a cache file name based on the zip code
        cache_file = cache_dir / f"weather_{zip_code}.json"
        cache_max_age = 3600  # 1 hour in seconds
        
        # Check if we have a valid cache
        if cache_file.exists():
            file_age = time.time() - cache_file.stat().st_mtime
            if file_age < cache_max_age:
                try:
                    with open(cache_file, 'r') as f:
                        cached_data = json.load(f)
                        logger.info(f"Using cached weather data for {zip_code}")
                        return cached_data
                except Exception as e:
                    logger.warning(f"Failed to load cached weather data: {e}")
        
        # No valid cache, make the API request
        base_url = "https://api.weatherapi.com/v1/current.json"
        params = {
            "key": self.api_key,
            "q": zip_code,
            "aqi": "no"
        }
        
        try:
            response = requests.get(base_url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                # Cache the successful response
                try:
                    with open(cache_file, 'w') as f:
                        json.dump(data, f)
                except Exception as e:
                    logger.warning(f"Failed to cache weather data: {e}")
                return data
            else:
                # If we have an expired cache, better to use it than nothing
                if cache_file.exists():
                    try:
                        with open(cache_file, 'r') as f:
                            cached_data = json.load(f)
                            logger.warning(f"Using expired cached weather data for {zip_code}")
                            cached_data["cached"] = True
                            cached_data["cache_warning"] = "Using outdated weather data"
                            return cached_data
                    except Exception:
                        pass
                        
                try:
                    error_details = response.json()
                    return {"error": f"API Error: {response.status_code} - {error_details.get('error', {}).get('message', 'Unknown error')}"}
                except json.JSONDecodeError:
                    return {"error": f"Invalid response format. Status code: {response.status_code}"}
                    
        except requests.RequestException as e:
            # Try to use cached data as fallback
            if cache_file.exists():
                try:
                    with open(cache_file, 'r') as f:
                        cached_data = json.load(f)
                        logger.warning(f"Network error, using cached weather data for {zip_code}")
                        cached_data["cached"] = True
                        cached_data["cache_warning"] = "Using cached data due to network error"
                        return cached_data
                except Exception:
                    pass
                    
            return {"error": f"Network error: {str(e)}"}

class ArduinoInterface:  # Fallback ArduinoInterface
    def __init__(self):
        print("Warning: Using dummy ArduinoInterface (import failed)")
    def connect(self):
        return False

class ConfigurationError(Exception): pass
class APIError(Exception): pass

# Version information
__version__ = "2.0.0"
__author__ = "Virtual Control LLC"
__copyright__ = "Copyright © 2025 Virtual Control LLC"

# Configure logging
def setup_logging():
    """Configure application logging"""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=os.environ.get("APP_LOG_LEVEL", "INFO").upper(),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / 'pool_app.log'),
            logging.StreamHandler()
        ]
    )
    
    if os.environ.get("APP_DEBUG", "false").lower() == "true":
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    return logging.getLogger(__name__)

logger = setup_logging()

class PoolApp(tk.Tk):
    def __init__(self):
        """Initialize the application"""
        logger.debug("Initializing PoolApp")
        print("Initializing PoolApp")
        try:
            # Initialize Tk
            super().__init__()
            print("Tk initialized")

            # Set window properties
            self.title(f"Deep Blue Chemistry Pool Management System v{__version__}")
            self.geometry(f"{DEFAULT_WINDOW_SIZE[0]}x{DEFAULT_WINDOW_SIZE[1]}")
            self.minsize(MIN_WINDOW_SIZE[0], MIN_WINDOW_SIZE[1])
            self.center_window()  # Call center_window AFTER super().__init__()
            print("Window size and position set")
            
            try:
                icon_path = os.path.join(os.path.dirname(__file__), "assets", "icon.ico")
                if os.path.exists(icon_path):
                    self.iconbitmap(icon_path)
                else:
                    logger.warning(f"Application icon not found at: {icon_path}")
                    print(f"Application icon not found at: {icon_path}")
            except Exception as e:
                logger.warning(f"Error setting application icon: {e}")
                print(f"Error setting application icon: {e}")

            # Initialize core components
            self.water_tester = WaterTester()
            self.data_manager = DataManager("pool_data.db")
            weather_api_key = os.environ.get("WEATHER_API_KEY")
            if weather_api_key:
                self.weather_api = WeatherAPI(weather_api_key)
                logger.info("WeatherAPI initialized with API key.")
            else:
                logger.error("Weather API key not found in environment variables.")
                raise ConfigurationError("Weather API key not found. Please set WEATHER_API_KEY environment variable.")



            self._initialize_variables()
            self._configure_colors()
            self._configure_styles()
            self._create_header()
            self._create_main_content()
            self._create_footer()
            self._load_data()

            self.arduino = None
            self._setup_arduino_communication()
            self._start_periodic_updates()
            self.protocol("WM_DELETE_WINDOW", self._on_close)

            logger.info("PoolApp initialization completed successfully")
            print("PoolApp initialization completed successfully")

        except ConfigurationError as e:
            logger.critical(f"Configuration Error: {str(e)}", exc_info=True)
            messagebox.showerror("Configuration Error", f"Application cannot start due to configuration issue: {str(e)}")
            sys.exit(1)
        except Exception as e:
            logger.critical(f"Error initializing application: {str(e)}", exc_info=True)
            print(f"Error initializing application: {str(e)}")
            messagebox.showerror(
                "Initialization Error",
                f"Failed to initialize application: {str(e)}"
            )
            sys.exit(1)

    def center_window(self):
        """Center the window on the screen."""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

    def _initialize_variables(self):
        """Initialize application variables."""
        self.customer_info = {}
        self.chemical_readings = []
        self.entries = {}
        self.labels = {}
        self.buttons = {}
        self.frames = {}
        self.status_var = tk.StringVar(value="Ready")
        self.data_dir = Path("data")
        self.data_dir.mkdir(exist_ok=True)
        self.customer_file = self.data_dir / "customer_info.json"
        self.readings_file = self.data_dir / "readings.json"  # Use JSON file for readings
        self.settings_file = self.data_dir / "settings.json"
        self._stop_threads = threading.Event()
        self.serial_conn = None
        self.arduino_thread = None
        self.weather_data = None
        self.zip_code = tk.StringVar(value="")
        self.weather_update_id = None
        self.datetime_update_id = None
        self.task_check_id = None
        self.alert_check_id = None
        self.backup_id = None
        self.fig = None
        self.ax = None
        self.canvas = None
        self.auto_backup_var = tk.BooleanVar(value=True)

    def _configure_colors(self):
        """Configure color scheme."""
        self.colors = COLOR_SCHEME

    def _configure_styles(self):
        """Configure ttk styles."""
        self.style = ttk.Style()
        self.style.configure("TLabel", font=("Helvetica", 10), padding=5)
        self.style.configure("Header.TLabel", font=("Helvetica", 16, "bold"), foreground=self.colors['primary'])
        self.style.configure("Subheader.TLabel", font=("Helvetica", 12, "bold"), foreground=self.colors['primary'])
        self.style.configure("Bold.TLabel", font=("Helvetica", 10, "bold"))
        self.style.configure("Success.TLabel", foreground=self.colors['success'])
        self.style.configure("Warning.TLabel", foreground=self.colors['warning'])
        self.style.configure("Danger.TLabel", foreground=self.colors['danger'])
        self.style.configure("Title.TLabel", font=("Helvetica", 14, "bold"))
        self.style.configure("TButton", padding=6)
        self.style.configure("TMenubutton", padding=6)
        self.style.configure("TCheckbutton", padding=6)
        self.style.configure("TRadiobutton", padding=6)
        self.style.configure("TCombobox", padding=6)
        self.style.configure("TSpinbox", padding=6)
        self.style.configure("TNotebook.Tab", padding=10)
        self.style.configure("TFrame", background=self.colors['background'])

    def _create_header(self):
        """Create the application header."""
        header_frame = ttk.Frame(self)
        header_frame.pack(fill="x", padx=10, pady=5)

        title_label = ttk.Label(
            header_frame,
            text="Deep Blue Chemistry",
            style="Header.TLabel"
        )
        title_label.pack(side="left")

        self.datetime_label = ttk.Label(header_frame, text=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        self.datetime_label.pack(side="right")

    def _create_main_content(self):
        """Create the main content area."""
        main_frame = ttk.Frame(self)
        main_frame.pack(fill="both", expand=True, padx=10, pady=5)

        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill="both", expand=True)

        self.dashboard_tab = ttk.Frame(notebook)
        self.readings_tab = ttk.Frame(notebook)
        self.history_tab = ttk.Frame(notebook)
        self.settings_tab = ttk.Frame(notebook)

        notebook.add(self.dashboard_tab, text="Dashboard")
        notebook.add(self.readings_tab, text="Water Testing")
        notebook.add(self.history_tab, text="History")
        notebook.add(self.settings_tab, text="Settings")

        self._create_dashboard_tab()
        self._create_readings_tab()
        self._create_history_tab()
        self._create_settings_tab()
    
    def _create_dashboard_tab(self):
        """Create the dashboard tab content"""
        # Customer info section
        customer_frame = ttk.LabelFrame(self.dashboard_tab, text="Customer Information")
        customer_frame.pack(fill="x", padx=5, pady=5)
        
        # Customer name
        ttk.Label(customer_frame, text="Name:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.customer_name_entry = ttk.Entry(customer_frame, width=30)
        self.customer_name_entry.grid(row=0, column=1, sticky="w", padx=5, pady=2)
        self.entries["customer_name"] = self.customer_name_entry

        # --- START: Address Fields (No Verification) ---
        # These fields are still present in the UI for data entry, but no API verification is performed.
        ttk.Label(customer_frame, text="Address Line 1:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.address1_entry = ttk.Entry(customer_frame, width=30)
        self.address1_entry.grid(row=1, column=1, sticky="w", padx=5, pady=2)

        ttk.Label(customer_frame, text="Address Line 2:").grid(row=2, column=0, sticky="w", padx=5, pady=2)
        self.address2_entry = ttk.Entry(customer_frame, width=30)
        self.address2_entry.grid(row=2, column=1, sticky="w", padx=5, pady=2)

        ttk.Label(customer_frame, text="City:").grid(row=1, column=2, sticky="w", padx=5, pady=2)
        self.city_entry = ttk.Entry(customer_frame, width=20)
        self.city_entry.grid(row=1, column=3, sticky="w", padx=5, pady=2)

        ttk.Label(customer_frame, text="State:").grid(row=2, column=2, sticky="w", padx=5, pady=2)
        self.state_entry = ttk.Entry(customer_frame, width=10)
        self.state_entry.grid(row=2, column=3, sticky="w", padx=5, pady=2)

        ttk.Label(customer_frame, text="Postal Code:").grid(row=1, column=4, sticky="w", padx=5, pady=2)
        self.postal_code_entry = ttk.Entry(customer_frame, width=10)
        self.postal_code_entry.grid(row=1, column=5, sticky="w", padx=5, pady=2)

        ttk.Label(customer_frame, text="Country:").grid(row=2, column=4, sticky="w", padx=5, pady=2)
        self.country_entry = ttk.Entry(customer_frame, width=10)
        self.country_entry.insert(0, "US") # Default to US
        self.country_entry.grid(row=2, column=5, sticky="w", padx=5, pady=2)

        # REMOVED: self.verify_address_button and self.address_verification_status_label
        # --- END: Address Fields (No Verification) ---
        
        # Pool info section
        pool_frame = ttk.LabelFrame(self.dashboard_tab, text="Pool Information")
        pool_frame.pack(fill="x", padx=5, pady=5)
        
        # Pool type
        ttk.Label(pool_frame, text="Pool Type:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.pool_type_var = tk.StringVar()
        self.pool_type_combo = ttk.Combobox(
            pool_frame, 
            textvariable=self.pool_type_var,
            values=["Concrete/Gunite", "Vinyl", "Fiberglass", "Above Ground"]
        )
        self.pool_type_combo.grid(row=0, column=1, sticky="w", padx=5, pady=2)
        
        # Pool size
        ttk.Label(pool_frame, text="Size (gallons):").grid(row=0, column=2, sticky="w", padx=5, pady=2)
        self.pool_size_entry = ttk.Entry(pool_frame, width=10)
        self.pool_size_entry.grid(row=0, column=3, sticky="w", padx=5, pady=2)
        
        # Weather section
        weather_frame = ttk.LabelFrame(self.dashboard_tab, text="Weather Information")
        weather_frame.pack(fill="x", padx=5, pady=5)
        
        # ZIP code entry
        ttk.Label(weather_frame, text="ZIP Code:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.zip_entry = ttk.Entry(weather_frame, width=10, textvariable=self.zip_code)
        self.zip_entry.grid(row=0, column=1, sticky="w", padx=5, pady=2)
        
        # Weather update button
        self.weather_button = ttk.Button(
            weather_frame, 
            text="Update Weather",
            command=lambda: self._update_weather() # FIX: Use lambda to defer method call
        )
        self.weather_button.grid(row=0, column=2, sticky="w", padx=5, pady=2)
        
        # Weather display
        self.weather_display_frame = ttk.Frame(weather_frame)
        self.weather_display_frame.grid(row=1, column=0, columnspan=3, sticky="w", padx=5, pady=5)
        
        # Status section
        status_frame = ttk.LabelFrame(self.dashboard_tab, text="System Status")
        status_frame.pack(fill="x", padx=5, pady=5)
        
        # Status label
        self.status_label = ttk.Label(status_frame, textvariable=self.status_var)
        self.status_label.pack(padx=5, pady=5)
    
    # REMOVED: _verify_customer_address method
    
    def _create_readings_tab(self):
        """Create the water testing tab content"""
        # Chemical readings frame
        readings_frame = ttk.LabelFrame(self.readings_tab, text="Chemical Readings")
        readings_frame.pack(fill="x", padx=5, pady=5)
        
        # Create a grid of chemical reading inputs
        chemicals = [
            ("pH", "ph", ""),
            ("Free Chlorine", "free_chlorine", "ppm"),
            ("Total Chlorine", "total_chlorine", "ppm"),
            ("Alkalinity", "alkalinity", "ppm"),
            ("Calcium Hardness", "calcium_hardness", "ppm"),
            ("Cyanuric Acid", "cyanuric_acid", "ppm"),
            ("Salt", "salt", "ppm"),
            ("Bromine", "bromine", "ppm"),
            ("Temperature", "temperature", "°F")
        ]
        
        # Create the entries
        for i, (label_text, field_name, unit) in enumerate(chemicals):
            row = i // 4  # Calculate row for grid layout
            col = (i % 4) * 3  # Calculate column for grid layout
            
            # Label
            ttk.Label(readings_frame, text=label_text).grid(
                row=row, column=col, sticky="w", padx=5, pady=2
            )
            
            # Entry
            entry = ttk.Entry(readings_frame, width=8)
            entry.grid(row=row, column=col+1, sticky="w", padx=5, pady=2)
            self.entries[field_name] = entry
            
            # Unit label
            if unit:
                ttk.Label(readings_frame, text=unit).grid(
                    row=row, column=col+2, sticky="w", padx=0, pady=2
                )
        
        # Buttons frame
        buttons_frame = ttk.Frame(self.readings_tab)
        buttons_frame.pack(fill="x", padx=5, pady=10)
        
        # Calculate button
        self.calculate_button = ttk.Button(
            buttons_frame,
            text="Calculate Adjustments",
            command=self._calculate_adjustments
        )
        self.calculate_button.pack(side="left", padx=5)
        
        # Save button
        self.save_button = ttk.Button(
            buttons_frame,
            text="Save Readings",
            command=self._save_readings
        )
        self.save_button.pack(side="left", padx=5)
        
        # Clear button
        self.clear_button = ttk.Button(
            buttons_frame,
            text="Clear",
            command=self._clear_readings
        )
        self.clear_button.pack(side="left", padx=5)
        
        # Results frame
        results_frame = ttk.LabelFrame(self.readings_tab, text="Recommendations")
        results_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Results text
        self.results_text = tk.Text(results_frame, height=10, wrap="word")
        self.results_text.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Make text read-only initially
        self.results_text.config(state="disabled")

    def _create_history_tab(self):
        """Create the history tab content"""
        print("Creating history tab...")
        
        # History controls frame
        controls_frame = ttk.Frame(self.history_tab)
        controls_frame.pack(fill="x", padx=5, pady=5)
        
        # Date range selection
        ttk.Label(controls_frame, text="Date Range:").pack(side="left", padx=5)
        self.date_range_var = tk.StringVar(value="Last 7 Days")
        date_range_combo = ttk.Combobox(
            controls_frame,
            textvariable=self.date_range_var,
            values=["Last 7 Days", "Last 30 Days", "Last 90 Days", "All Time"]
        )
        date_range_combo.pack(side="left", padx=5)
        date_range_combo.bind("<<ComboboxSelected>>", self._update_history_graph)

        # Refresh button
        refresh_button = ttk.Button(
            controls_frame,
            text="Refresh",
            command=self._refresh_history
        )
        refresh_button.pack(side="left", padx=5)
        
        # Export button
        export_button = ttk.Button(
            controls_frame,
            text="Export Data",
            command=self._export_history
        )
        export_button.pack(side="left", padx=5)
        
        # History data frame
        data_frame = ttk.Frame(self.history_tab)
        data_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Create a treeview for history data
        print("Creating history treeview...")
        self.history_tree = ttk.Treeview(
            data_frame,
            columns=("date", "ph", "chlorine", "alkalinity", "hardness"),
            show="headings"
        )
        
        # Define headings
        self.history_tree.heading("date", text="Date")
        self.history_tree.heading("ph", text="pH")
        self.history_tree.heading("chlorine", text="Chlorine")
        self.history_tree.heading("alkalinity", text="Alkalinity")
        self.history_tree.heading("hardness", text="Hardness")
        
        # Define columns
        self.history_tree.column("date", width=120)
        self.history_tree.column("ph", width=80)
        self.history_tree.column("chlorine", width=80)
        self.history_tree.column("alkalinity", width=80)
        self.history_tree.column("hardness", width=80)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(data_frame, orient="vertical", command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack the treeview and scrollbar
        self.history_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        print("Creating graph frame...")
        # Graph frame
        graph_frame = ttk.LabelFrame(self.history_tab, text="Trends")
        graph_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Create matplotlib figure and canvas
        print("Creating matplotlib figure...")
        try:
            self.fig = Figure(figsize=(6, 4), dpi=100)
            self.ax = self.fig.add_subplot(111)
            print("Creating FigureCanvasTkAgg...")
            self.canvas = FigureCanvasTkAgg(self.fig, master=graph_frame)
            print("Drawing canvas...")
            self.canvas.draw()
            print("Packing canvas widget...")
            self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=5, pady=5)
            print("History tab creation complete")

            # Initial graph update (after creating the canvas)
            self._update_history_graph()
        except Exception as e:
            print(f"Error creating matplotlib components: {e}")
            import traceback
            traceback.print_exc()
            # Create a label instead of the matplotlib canvas
            ttk.Label(
                graph_frame,
                text="Graph display not available",
                foreground="red"
            ).pack(padx=5, pady=20)
    
    def _create_settings_tab(self):
        """Create the settings tab content"""
        # Settings frame
        self.settings_frame = ttk.Frame(self.settings_tab)
        self.settings_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Theme selection
        ttk.Label(self.settings_frame, text="Theme:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.theme_var = tk.StringVar(value="clam")
        theme_combo = ttk.Combobox(
            self.settings_frame,
            textvariable=self.theme_var,
            values=["clam", "alt", "default", "classic", "vista", "xpnative", "winxpblue"]
        )
        theme_combo.grid(row=0, column=1, sticky="w", padx=5, pady=2)

        # Auto backup toggle
        ttk.Label(self.settings_frame, text="Auto Backup:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.auto_backup_var = tk.BooleanVar(value=True)
        auto_backup_checkbox = ttk.Checkbutton(
            self.settings_frame,
            variable=self.auto_backup_var,
            onvalue=True,
            offvalue=False
        )
        auto_backup_checkbox.grid(row=1, column=1, sticky="w", padx=5, pady=2)

        # Save settings button
        save_settings_button = ttk.Button(
            self.settings_frame,
            text="Save Settings",
            command=self._save_settings
        )
        save_settings_button.grid(row=2, column=0, columnspan=2, sticky="w", padx=5, pady=2)

    def _create_footer(self):
        """Create the application footer"""
        # Footer frame
        self.footer_frame = ttk.Frame(self)
        self.footer_frame.pack(fill="x", padx=10, pady=5)

        # Status bar
        self.status_bar = ttk.Label(
            self.footer_frame,
            text="Ready",
            relief="sunken",
            anchor="w"
        )
        self.status_bar.pack(fill="x")

    def _load_data(self):
        """Load saved data"""
        try:
            if self.customer_file.exists():
                self.customer_info = load_json(self.customer_file)
                self._populate_customer_info(self.customer_info)

            if self.readings_file.exists():
                readings_data = load_json(self.readings_file)
                if "readings" in readings_data:
                    self.chemical_readings = readings_data["readings"]
                    self._refresh_history()

            logger.info("Data loaded successfully")
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            messagebox.showwarning("Error", f"Error loading data: {e}")

    def _populate_customer_info(self, customer_info):
        """Populate customer information fields"""
        self.customer_name_entry.delete(0, tk.END)
        self.customer_name_entry.insert(0, customer_info.get("name", ""))
        self.pool_type_var.set(customer_info.get("pool_type", ""))

        pool_size = customer_info.get("pool_size")
        self.pool_size_entry.delete(0, tk.END)
        if pool_size:
            self.pool_size_entry.insert(0, str(pool_size))

        self.address1_entry.delete(0, tk.END)
        self.address1_entry.insert(0, customer_info.get("address_line1", ""))
        self.address2_entry.delete(0, tk.END)
        self.address2_entry.insert(0, customer_info.get("address_line2", ""))
        self.city_entry.delete(0, tk.END)
        self.city_entry.insert(0, customer_info.get("city", ""))
        self.state_entry.delete(0, tk.END)
        self.state_entry.insert(0, customer_info.get("state", ""))
        self.postal_code_entry.delete(0, tk.END)
        self.postal_code_entry.insert(0, customer_info.get("postal_code", ""))
        self.country_entry.delete(0, tk.END)
        self.country_entry.insert(0, customer_info.get("country", "US"))


    def _setup_arduino_communication(self):
        """Set up communication with Arduino if available"""
        try:
            try:
                import serial.tools.list_ports
                ports = list(serial.tools.list_ports.comports())
                arduino_port = next((p.device for p in ports if "Arduino" in p.description), None)
                if arduino_port:
                    self.arduino = ArduinoInterface(port=arduino_port)
                    if self.arduino.connect():
                        logger.info(f"Connected to Arduino on {arduino_port}")
                        self.arduino_thread = threading.Thread(target=self._arduino_communication_loop, daemon=True)
                        self.arduino_thread.start()
                    else:
                        logger.warning(f"Failed to connect to Arduino on {arduino_port}")
                else:
                    logger.info("No Arduino found")
            except ImportError:
                logger.info("pyserial not installed. Arduino communication disabled.")
        except Exception as e:
            logger.error(f"Error setting up Arduino: {e}")

    def _arduino_communication_loop(self):
        """Background thread for Arduino communication"""
        while not self._stop_threads.is_set():
            try:
                data = self.arduino.read_data()
                if data:
                    readings = {}
                    for item in data.split(','):
                        if ':' in item:
                            key, value = item.split(':')
                            try:
                                readings[key.strip()] = float(value.strip())
                            except ValueError:
                                pass
                    if readings:
                        self.after(0, lambda: self._update_readings_from_arduino(readings))
            except Exception as e:
                logger.error(f"Arduino communication error: {e}")
            time.sleep(1)

    def _update_readings_from_arduino(self, readings):
        """Update UI with readings from Arduino"""
        try:
            for key, value in readings.items():
                normalized_key = key.lower().replace(" ", "_")
                if normalized_key in self.entries:
                    self.entries[normalized_key].delete(0, tk.END)
                    self.entries[normalized_key].insert(0, str(value))
        except Exception as e:
            logger.error(f"Error updating readings from Arduino: {e}")


    def _start_periodic_updates(self):
        """Start periodic update tasks"""
        self._update_datetime()
        if self.zip_code.get():
            self._update_weather()
        if self.auto_backup_var.get():
            if self.backup_id:
                self.after_cancel(self.backup_id)
            self.backup_id = self.after(3600000, self._backup_data)  # Every hour (3600000 ms)
            logger.info("Next automatic backup scheduled.")

    def _update_datetime(self):
        """Update the date/time display"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.datetime_label.config(text=current_time)
        self.datetime_update_id = self.after(1000, self._update_datetime)

    def _update_weather(self):
        """Update weather information"""
        zip_code = self.zip_code.get()
        if not zip_code:
            self.status_var.set("Enter a ZIP code for weather updates.")
            self.status_bar.config(text="Enter a ZIP code for weather updates.")
            return

        try:
            self.status_var.set("Updating weather...")
            self.status_bar.config(text="Updating weather...")
            
            # Add a timeout to prevent the application from hanging
            weather_data = self.weather_api.get_weather_data(zip_code)

            if "error" in weather_data:
                logger.warning(f"Weather API error: {weather_data['error']}")
                self.status_var.set(f"Weather update failed: {weather_data['error']}")
                self.status_bar.config(text=f"Weather update failed: {weather_data['error']}")
                
                # Use cached weather data if available
                if hasattr(self, 'weather_data') and self.weather_data and "error" not in self.weather_data:
                    logger.info("Using cached weather data")
                    self.status_var.set("Using cached weather data")
                    return
                else:
                    # Show a graceful error message in the UI
                    self._display_weather_error(weather_data['error'])
                    return

            self.weather_data = weather_data
            self.after(0, lambda: self._display_weather(weather_data))
            self.status_var.set("Weather updated successfully")
            self.status_bar.config(text="Weather updated successfully")
            self.weather_update_id = self.after(1800000, self._update_weather)  # 30 minutes
        except Exception as e:
            logger.error(f"Error updating weather: {str(e)}", exc_info=True)
            self.status_var.set("Weather update failed")
            self.status_bar.config(text="Weather update failed")
            # Display error in UI
            self._display_weather_error(str(e))

    def _display_weather_error(self, error_message):
        """Display a weather error in the UI"""
        for widget in self.weather_display_frame.winfo_children():
            widget.destroy()
        ttk.Label(
            self.weather_display_frame,
            text=f"Weather update failed: {error_message}",
            foreground="red"
        ).grid(row=0, column=0, sticky="w", padx=5, pady=2)
        ttk.Label(
            self.weather_display_frame,
            text="Using default values for calculations",
            foreground="blue"
        ).grid(row=1, column=0, sticky="w", padx=5, pady=2)


    def _display_weather(self, weather_data):
        """Display weather information in the UI"""
        try:
            for widget in self.weather_display_frame.winfo_children():
                widget.destroy()

            if "error" in weather_data:
                ttk.Label(self.weather_display_frame, text=f"Error: {weather_data['error']}", 
                         foreground="red").grid(row=0, column=0, sticky="w", padx=5, pady=2)
                return

            # For WeatherAPI.com, the response structure is different
            current = weather_data.get("current", {})
            location = weather_data.get("location", {})
            
            ttk.Label(self.weather_display_frame, 
                     text=f"Location: {location.get('name', 'N/A')}, {location.get('region', 'N/A')}").grid(
                     row=0, column=0, sticky="w", padx=5, pady=2)
            
            ttk.Label(self.weather_display_frame, 
                     text=f"Temperature: {current.get('temp_f', 'N/A')}°F (Feels like: {current.get('feelslike_f', 'N/A')}°F)").grid(
                     row=1, column=0, sticky="w", padx=5, pady=2)
            
            ttk.Label(self.weather_display_frame, 
                     text=f"Humidity: {current.get('humidity', 'N/A')}%").grid(
                     row=2, column=0, sticky="w", padx=5, pady=2)
            
            condition = current.get('condition', {})
            ttk.Label(self.weather_display_frame, 
                     text=f"Condition: {condition.get('text', 'N/A')}").grid(
                     row=3, column=0, sticky="w", padx=5, pady=2)

            impact = self._calculate_weather_impact(current)
            impact_label = ttk.Label(self.weather_display_frame, text=f"Pool Impact: {impact}")
            impact_label.grid(row=4, column=0, sticky="w", padx=5, pady=2)
        except Exception as e:
            logger.error(f"Error displaying weather: {e}")
            ttk.Label(self.weather_display_frame, 
                     text=f"Error displaying weather information: {str(e)}", 
                     foreground="red").grid(row=0, column=0, sticky="w", padx=5, pady=2)


    def _calculate_weather_impact(self, weather_data):
        """Calculate the impact of weather on pool chemistry"""
        try:
            temp = weather_data.get('temp_f', 75)
            humidity = weather_data.get('humidity', 50)
            conditions = weather_data.get('condition', {}).get('text', '').lower()
            
            impact = "Low"
            
            # Higher temperatures increase chlorine demand
            if temp > 85:
                impact = "High"
            elif temp > 75:
                impact = "Medium"
                
            # Rain can affect pH and dilute chemicals
            if any(term in conditions for term in ['rain', 'shower', 'drizzle', 'precipitation']):
                impact = "High"
                
            # High humidity can reduce water evaporation
            if humidity > 80 and impact != "High":
                impact = "Medium"
                
            # Store impact for later calculations
            self.weather_impact = impact
            return impact
        except Exception as e:
            logger.error(f"Error calculating weather impact: {e}")
            return "Unknown"


    def _calculate_adjustments(self):
        """Calculate chemical adjustments based on readings"""
        try:
            readings = self._get_readings_from_form()
            if not readings:
                return None
                
            adjustments = {}
            
            # Calculate chlorine adjustment
            target_chlorine = 3.0  # ppm
            current_chlorine = readings.get('free_chlorine', 0)
            pool_size = float(self.pool_size_entry.get()) if self.pool_size_entry.get() else 10000
            
            if current_chlorine < target_chlorine:
                chlorine_needed = (target_chlorine - current_chlorine) * pool_size / 10000
                adjustments['chlorine'] = {
                    'action': 'add',
                    'amount': round(chlorine_needed, 2),
                    'unit': 'oz'
                }
            elif current_chlorine > target_chlorine + 1:
                adjustments['chlorine'] = {
                    'action': 'reduce',
                    'amount': 0,
                    'unit': '',
                    'message': 'Let chlorine levels naturally reduce or partially drain and refill'
                }
            
            # Calculate pH adjustment
            target_ph_min = 7.2
            target_ph_max = 7.6
            current_ph = readings.get('ph', 7.4)
            
            if current_ph < target_ph_min:
                ph_adjustment = (target_ph_min - current_ph) * pool_size / 10000
                adjustments['ph'] = {
                    'action': 'increase',
                    'amount': round(ph_adjustment * 2, 2),
                    'unit': 'oz',
                    'chemical': 'soda ash'
                }
            elif current_ph > target_ph_max:
                ph_adjustment = (current_ph - target_ph_max) * pool_size / 10000
                adjustments['ph'] = {
                    'action': 'decrease',
                    'amount': round(ph_adjustment * 3, 2),
                    'unit': 'oz',
                    'chemical': 'muriatic acid'
                }
            
            # Calculate alkalinity adjustment
            target_alk_min = 80
            target_alk_max = 120
            current_alk = readings.get('alkalinity', 0)
            
            if current_alk < target_alk_min:
                alk_needed = (target_alk_min - current_alk) * pool_size / 10000
                adjustments['alkalinity'] = {
                    'action': 'increase',
                    'amount': round(alk_needed * 1.5, 2),
                    'unit': 'oz',
                    'chemical': 'sodium bicarbonate'
                }
            elif current_alk > target_alk_max:
                alk_adjustment = (current_alk - target_alk_max) * pool_size / 10000
                adjustments['alkalinity'] = {
                    'action': 'decrease',
                    'amount': round(alk_adjustment * 2, 2),
                    'unit': 'oz',
                    'chemical': 'muriatic acid'
                }
                
            # Weather impact can affect dosage
            if hasattr(self, 'weather_impact'):
                if self.weather_impact == "High":
                    for key in adjustments:
                        if 'amount' in adjustments[key]:
                            adjustments[key]['amount'] *= 1.2
                            adjustments[key]['weather_factor'] = "Increased due to weather conditions"
            
            self._display_adjustments(adjustments)
            return adjustments
        except Exception as e:
            logger.error(f"Error calculating adjustments: {e}")
            messagebox.showerror("Calculation Error", f"An error occurred: {e}")
            return None

    def _get_readings_from_form(self):
        """Get chemical readings from form inputs"""
        try:
            readings = {}
            
            # Validate and collect readings from entry fields
            for param, entry in self.entries.items():
                value = entry.get().strip()
                if value:
                    try:
                        readings[param] = float(value)
                    except ValueError:
                        messagebox.showwarning(
                            "Invalid Input", 
                            f"The value for {param.replace('_', ' ').title()} must be a number."
                        )
                        entry.delete(0, tk.END)
                        entry.focus_set()
                        return None
            
            # Ensure required readings are present
            required_params = ['ph', 'free_chlorine']
            missing = [param.replace('_', ' ').title() for param in required_params if param not in readings]
            
            if missing:
                messagebox.showwarning(
                    "Missing Readings",
                    f"Please enter values for: {', '.join(missing)}"
                )
                return None
                
            return readings
        except Exception as e:
            logger.error(f"Error getting readings from form: {e}")
            messagebox.showerror("Input Error", f"An error occurred: {e}")
            return None

    def _display_adjustments(self, adjustments):
        """Display chemical adjustment recommendations"""
        try:
            # Clear any previous adjustment displays
            for widget in self.adjustments_frame.winfo_children():
                widget.destroy()
                
            if not adjustments:
                ttk.Label(
                    self.adjustments_frame, 
                    text="No adjustments needed. Your pool chemistry is balanced.",
                    style="Success.TLabel"
                ).pack(pady=10)
                return
                
            # Create header
            ttk.Label(
                self.adjustments_frame,
                text="Recommended Chemical Adjustments",
                font=("Arial", 12, "bold")
            ).pack(pady=(10, 5))
            
            # Create a frame for each adjustment
            row = 0
            for chemical, data in adjustments.items():
                frame = ttk.Frame(self.adjustments_frame, relief="raised", borderwidth=1)
                frame.pack(fill="x", padx=10, pady=5)
                
                # Create header for this chemical
                ttk.Label(
                    frame,
                    text=chemical.replace('_', ' ').title(),
                    font=("Arial", 10, "bold")
                ).grid(row=0, column=0, columnspan=2, sticky="w", padx=5, pady=2)
                
                # Action
                ttk.Label(frame, text="Action:").grid(row=1, column=0, sticky="w", padx=5)
                action_text = f"{data['action'].title()}"
                if 'chemical' in data:
                    action_text += f" using {data['chemical']}"
                ttk.Label(frame, text=action_text).grid(row=1, column=1, sticky="w", padx=5)
                
                # Amount (if applicable)
                if 'amount' in data and data['amount'] > 0:
                    ttk.Label(frame, text="Amount:").grid(row=2, column=0, sticky="w", padx=5)
                    ttk.Label(frame, text=f"{data['amount']} {data['unit']}").grid(row=2, column=1, sticky="w", padx=5)
                
                # Message (if applicable)
                if 'message' in data:
                    ttk.Label(frame, text="Note:").grid(row=3, column=0, sticky="w", padx=5)
                    ttk.Label(frame, text=data['message']).grid(row=3, column=1, sticky="w", padx=5)
                    
                # Weather factor (if applicable)
                if 'weather_factor' in data:
                    ttk.Label(frame, text="Weather Impact:").grid(row=4, column=0, sticky="w", padx=5)
                    ttk.Label(frame, text=data['weather_factor']).grid(row=4, column=1, sticky="w", padx=5)
                    
                row += 1
                
            # Add save readings button
            ttk.Button(
                self.adjustments_frame, 
                text="Save These Readings", 
                command=self._save_readings
            ).pack(pady=10)
            
        except Exception as e:
            logger.error(f"Error displaying adjustments: {e}")
            messagebox.showerror("Display Error", f"An error occurred: {e}")


    def _save_readings(self):
        """Save current readings to history"""
        try:
            readings = self._get_readings_from_form()
            if not readings:
                return

            timestamp = datetime.now().isoformat()
            readings['timestamp'] = timestamp

            self.chemical_readings.append(readings)

            save_data = {'timestamp': timestamp, 'readings': self.chemical_readings}

            if save_json(save_data, self.readings_file):
                self.status_var.set("Readings saved successfully")
                self.status_bar.config(text="Readings saved successfully")
                self._refresh_history()
                self._save_to_database(readings)
            else:
                self.status_var.set("Failed to save readings")
                self.status_bar.config(text="Failed to save readings")

        except Exception as e:
            logger.error(f"Error saving readings: {str(e)}")
            messagebox.showerror("Save Error", f"An error occurred: {str(e)}")
            self.status_var.set("Save failed")
            self.status_bar.config(text="Save failed")


    def _save_to_database(self, readings):
        """Save readings to database"""
        try:
            temperature = readings.get('temperature', 0)
            ph = readings.get('ph', 0)
            chlorine = readings.get('free_chlorine', 0)  # Or total_chlorine as needed
            self.data_manager.insert_reading(temperature, ph, chlorine)
            logger.info("Readings saved to database")
        except Exception as e:
            logger.error(f"Error saving to database: {str(e)}")
            messagebox.showerror("Database Error", f"An error occurred saving to the database: {str(e)}")


    def _clear_readings(self):
        """Clear all reading inputs"""
        for field, entry in self.entries.items():
            if field not in ['customer_name', 'pool_size']:
                entry.delete(0, "end")
        self.results_text.config(state="normal")
        self.results_text.delete(1.0, "end")
        self.results_text.config(state="disabled")
        self.status_var.set("Readings cleared")
        self.status_bar.config(text="Readings cleared")


    def _refresh_history(self):
        """Refresh the history display"""
        try:
            for item in self.history_tree.get_children():
                self.history_tree.delete(item)
            if not self.chemical_readings:  # Check if there are any readings
                return
            for reading in self.chemical_readings:
                timestamp = reading.get('timestamp', '')
                try:
                    date_obj = datetime.fromisoformat(timestamp)
                    date_str = date_obj.strftime('%Y-%m-%d %H:%M')
                except (ValueError, TypeError): # Handle missing/invalid timestamps
                    date_str = "Invalid Timestamp"
                self.history_tree.insert("", "end", values=(
                    date_str,
                    reading.get('ph', ''),
                    reading.get('free_chlorine', ''),
                    reading.get('alkalinity', ''),
                    reading.get('calcium_hardness', '')
                ))
            self._update_history_graph()  # Update the graph after refreshing history
        except Exception as e:
            logger.error(f"Error refreshing history: {str(e)}")
            messagebox.showerror("Refresh Error", f"An error occurred: {str(e)}")


    def _update_history_graph(self, event=None):
        """Update the history graph"""
        try:
            if not (self.chemical_readings and self.fig and self.ax and self.canvas):
                return
            self.ax.clear()
            dates, ph_values, chlorine_values = [], [], []
            for reading in self.chemical_readings:
                try:
                    date_obj = datetime.fromisoformat(reading['timestamp'])
                    dates.append(date_obj)
                    ph_values.append(reading.get('ph'))
                    chlorine_values.append(reading.get('free_chlorine'))
                except (KeyError, ValueError, TypeError):
                    pass  # Skip readings with missing or invalid data
            if dates and (ph_values or chlorine_values):
                if ph_values:
                    self.ax.plot(dates, ph_values, 'b-', label='pH')
                if chlorine_values:
                    self.ax.plot(dates, chlorine_values, 'g-', label='Free Chlorine')
                self.ax.set_xlabel('Date')
                self.ax.set_ylabel('Value')
                self.ax.set_title('Chemical Readings History')
                self.ax.legend()
                self.fig.autofmt_xdate()
                self.ax.grid(True)
                self.canvas.draw()  
        except Exception as e:
            logger.error(f"Error updating history graph: {str(e)}")
            messagebox.showerror("Graph Error", f"An error occurred updating the graph: {str(e)}")


    def _export_history(self):
        """Export history data to CSV"""
        try:
            if not self.chemical_readings:
                messagebox.showinfo("Export", "No data to export")
                return
            file_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                title="Export History Data"
            )
            if not file_path:
                return
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['timestamp', 'ph', 'free_chlorine', 'total_chlorine', 
                             'alkalinity', 'calcium_hardness', 'cyanuric_acid', 
                             'salt', 'temperature']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(self.chemical_readings)
            self.status_var.set(f"Data exported to {file_path}")
            self.status_bar.config(text=f"Data exported to {file_path}")
            messagebox.showinfo("Export", f"Data exported successfully to {file_path}")
        except Exception as e:
            logger.error(f"Error exporting history: {str(e)}")
            messagebox.showerror("Export Error", f"An error occurred: {str(e)}")


    def _change_theme(self, event):
        """Change the application theme"""
        try:
            theme = self.theme_var.get()
            self.style.theme_use(theme)
            self.status_var.set(f"Theme changed to {theme}")
            self.status_bar.config(text=f"Theme changed to {theme}")
        except Exception as e:
            logger.error(f"Error changing theme: {str(e)}")
            messagebox.showerror("Theme Error", f"An error occurred: {str(e)}")


    def _save_settings(self):
        """Save application settings"""
        try:
            settings = {
                'theme': self.theme_var.get(),
                'auto_backup': self.auto_backup_var.get()
            }
            save_json(settings, self.settings_file)
            self.status_var.set("Settings saved successfully")
            self.status_bar.config(text="Settings saved successfully")
        except Exception as e:
            logger.error(f"Error saving settings: {str(e)}")
            messagebox.showerror("Save Error", f"An error occurred: {str(e)}")


    def _backup_data(self):
        """Create a backup of all data files"""
        try:
            backup_dir = self.data_dir / "backups"
            backup_dir.mkdir(exist_ok=True)
            backup_file = backup_dir / f"backup_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.zip"
            with zipfile.ZipFile(backup_file, 'w') as zip_file:
                for file in self.data_dir.glob('*'):
                    if file.is_file():
                        zip_file.write(file, arcname=file.name)
            self.status_var.set(f"Backup created at {backup_file}")
            self.status_bar.config(text=f"Backup created at {backup_file}")
            logger.info(f"Backup created at {backup_file}")
        except Exception as e:
            logger.error(f"Error creating backup: {str(e)}")
            messagebox.showerror("Backup Error", f"An error occurred: {str(e)}")


    def _on_close(self):
        """Handle application close event"""
        try:
            self._stop_threads.set()
            if self.arduino_thread:
                self.arduino_thread.join()
            self._cleanup()
            self.destroy()
        except Exception as e:
            logger.error(f"Error on close: {str(e)}")


    def _cleanup(self):
        """Clean up resources before exit"""
        try:
            if self.data_manager:
                self.data_manager.close_connection()
            if self.arduino:
                self.arduino.disconnect()
        except Exception as e:
            logger.error(f"Error cleaning up: {str(e)}")


## Main function to run the application
def main():
    """Main entry point for the application"""
    app = PoolApp()
    app.mainloop()

# Entry point
if __name__ == "__main__":
    main()
