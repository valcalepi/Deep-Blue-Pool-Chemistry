
"""
Simple Pool Chemistry Application.

This is a simplified version of the Deep Blue Pool Chemistry application
that works with a flat directory structure.
"""

import logging
import os
import sys
import json
import argparse
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import threading
import time
import numpy as np

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("pool_chemistry.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("SimplePoolApp")

# Simple TestStripAnalyzer class that doesn't rely on external imports
class TestStripAnalyzer:
    """Simple TestStripAnalyzer class."""
    
    def __init__(self, config=None):
        """Initialize the analyzer."""
        logger.info("Initializing Simple Test Strip Analyzer")
        self.config = {"profiles_dir": "data/strip_profiles"}
        
        if config is not None:
            if isinstance(config, dict):
                self.config.update(config)
            elif isinstance(config, str):
                self.config["profiles_dir"] = config
        
        # Create profiles directory if it doesn't exist
        os.makedirs(self.config["profiles_dir"], exist_ok=True)
    
    def analyze_image(self, image_path):
        """Analyze a test strip image."""
        logger.info(f"Analyzing image: {image_path}")
        # Return dummy data
        return {
            "Free Chlorine": {"value": 3.0, "unit": "ppm"},
            "pH": {"value": 7.2, "unit": ""},
            "Total Alkalinity": {"value": 120, "unit": "ppm"},
            "Total Hardness": {"value": 250, "unit": "ppm"},
            "Cyanuric Acid": {"value": 50, "unit": "ppm"},
            "Total Bromine": {"value": 5, "unit": "ppm"}
        }

# Simple DatabaseService class
class DatabaseService:
    """Simple DatabaseService class."""
    
    def __init__(self, db_path):
        """Initialize the database service."""
        logger.info(f"Initializing Simple Database Service with path: {db_path}")
        self.db_path = db_path
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    def get_all_readings(self):
        """Get all readings."""
        # Return dummy data
        return [
            {
                "id": 1,
                "timestamp": datetime.now() - timedelta(days=7),
                "free_chlorine": 3.0,
                "ph": 7.2,
                "total_alkalinity": 120,
                "total_hardness": 250,
                "cyanuric_acid": 50,
                "total_bromine": 5
            },
            {
                "id": 2,
                "timestamp": datetime.now() - timedelta(days=5),
                "free_chlorine": 2.5,
                "ph": 7.4,
                "total_alkalinity": 110,
                "total_hardness": 240,
                "cyanuric_acid": 45,
                "total_bromine": 4
            },
            {
                "id": 3,
                "timestamp": datetime.now() - timedelta(days=3),
                "free_chlorine": 2.0,
                "ph": 7.6,
                "total_alkalinity": 100,
                "total_hardness": 230,
                "cyanuric_acid": 40,
                "total_bromine": 3
            },
            {
                "id": 4,
                "timestamp": datetime.now() - timedelta(days=1),
                "free_chlorine": 1.5,
                "ph": 7.8,
                "total_alkalinity": 90,
                "total_hardness": 220,
                "cyanuric_acid": 35,
                "total_bromine": 2
            }
        ]
    
    def get_all_customers(self):
        """Get all customers."""
        # Return dummy data
        return [
            {
                "id": 1,
                "name": "John Doe",
                "email": "john@example.com",
                "phone": "555-1234",
                "address": "123 Main St",
                "created_at": datetime.now() - timedelta(days=30),
                "updated_at": datetime.now() - timedelta(days=5)
            },
            {
                "id": 2,
                "name": "Jane Smith",
                "email": "jane@example.com",
                "phone": "555-5678",
                "address": "456 Oak Ave",
                "created_at": datetime.now() - timedelta(days=20),
                "updated_at": datetime.now() - timedelta(days=2)
            }
        ]

# Simple ChemicalSafetyDatabase class
class ChemicalSafetyDatabase:
    """Simple ChemicalSafetyDatabase class."""
    
    def __init__(self, data_file):
        """Initialize the chemical safety database."""
        logger.info(f"Initializing Simple Chemical Safety Database with file: {data_file}")
        self.data_file = data_file
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(data_file), exist_ok=True)
    
    def get_chemical_info(self, chemical_name):
        """Get information about a chemical."""
        # Return dummy data
        chemicals = {
            "chlorine": {
                "name": "Chlorine",
                "formula": "Cl",
                "safety_info": "Handle with care. Avoid contact with skin and eyes.",
                "ideal_range": {"min": 1.0, "max": 3.0, "unit": "ppm"}
            },
            "ph": {
                "name": "pH",
                "formula": "N/A",
                "safety_info": "N/A",
                "ideal_range": {"min": 7.2, "max": 7.8, "unit": ""}
            },
            "alkalinity": {
                "name": "Total Alkalinity",
                "formula": "N/A",
                "safety_info": "N/A",
                "ideal_range": {"min": 80, "max": 120, "unit": "ppm"}
            }
        }
        
        return chemicals.get(chemical_name.lower(), {
            "name": chemical_name,
            "formula": "Unknown",
            "safety_info": "No safety information available.",
            "ideal_range": {"min": 0, "max": 0, "unit": ""}
        })

# Simple WeatherService class
class WeatherService:
    """Simple WeatherService class."""
    
    def __init__(self, api_key, default_location):
        """Initialize the weather service."""
        logger.info(f"Initializing Simple Weather Service for location: {default_location}")
        self.api_key = api_key
        self.default_location = default_location
    
    def get_current_weather(self, location=None):
        """Get current weather for a location."""
        if location is None:
            location = self.default_location
        
        # Return dummy data
        return {
            "location": location,
            "temperature": 75,
            "humidity": 50,
            "conditions": "Partly Cloudy",
            "wind_speed": 5,
            "wind_direction": "NE",
            "pressure": 1015,
            "timestamp": datetime.now()
        }

class SimpleTabBasedUI:
    """
    Simple implementation of the TabBasedUI class.
    """
    
    def __init__(self, root, db_service, chemical_safety_db, test_strip_analyzer, weather_service, controller=None):
        """
        Initialize the simple tab-based UI.
        
        Args:
            root: The root Tkinter window
            db_service: Database service instance
            chemical_safety_db: Chemical safety database instance
            test_strip_analyzer: Test strip analyzer instance
            weather_service: Weather service instance
            controller: Controller instance (optional)
        """
        self.root = root
        self.db_service = db_service
        self.chemical_safety_db = chemical_safety_db
        self.test_strip_analyzer = test_strip_analyzer
        self.weather_service = weather_service
        self.controller = controller
        
        # Set up the UI
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the UI components."""
        self.root.title("Deep Blue Pool Chemistry")
        self.root.geometry("1200x800")
        
        # Create menu bar
        self.menu_bar = tk.Menu(self.root)
        self.root.config(menu=self.menu_bar)
        
        # Create file menu
        file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Create help menu
        help_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create tabs
        self.create_dashboard_tab()
        self.create_readings_tab()
        self.create_test_strip_tab()
        self.create_customer_management_tab()
        self.create_settings_tab()
    
    def create_dashboard_tab(self):
        """Create the dashboard tab."""
        dashboard_frame = ttk.Frame(self.notebook, padding=20)
        self.notebook.add(dashboard_frame, text="Dashboard")
        
        # Add title
        title = ttk.Label(dashboard_frame, text="Deep Blue Pool Chemistry", font=("Arial", 24))
        title.pack(pady=20)
        
        # Add subtitle
        subtitle = ttk.Label(
            dashboard_frame, 
            text="Pool Chemistry Management System",
            font=("Arial", 14)
        )
        subtitle.pack(pady=10)
        
        # Add weather information
        weather_frame = ttk.LabelFrame(dashboard_frame, text="Current Weather")
        weather_frame.pack(fill=tk.X, pady=20)
        
        weather = self.weather_service.get_current_weather()
        
        weather_info = f"Location: {weather['location']}\
"
        weather_info += f"Temperature: {weather['temperature']}\u00b0F\
"
        weather_info += f"Humidity: {weather['humidity']}%\
"
        weather_info += f"Conditions: {weather['conditions']}"
        
        weather_label = ttk.Label(weather_frame, text=weather_info, padding=10)
        weather_label.pack()
        
        # Add recent readings
        readings_frame = ttk.LabelFrame(dashboard_frame, text="Recent Readings")
        readings_frame.pack(fill=tk.BOTH, expand=True, pady=20)
        
        readings = self.db_service.get_all_readings()
        if readings:
            latest = readings[-1]
            
            readings_info = f"Free Chlorine: {latest['free_chlorine']} ppm\
"
            readings_info += f"pH: {latest['ph']}\
"
            readings_info += f"Total Alkalinity: {latest['total_alkalinity']} ppm\
"
            readings_info += f"Total Hardness: {latest['total_hardness']} ppm\
"
            readings_info += f"Cyanuric Acid: {latest['cyanuric_acid']} ppm\
"
            readings_info += f"Total Bromine: {latest['total_bromine']} ppm\
"
            readings_info += f"\
Last Updated: {latest['timestamp'].strftime('%Y-%m-%d %H:%M')}"
            
            readings_label = ttk.Label(readings_frame, text=readings_info, padding=10)
            readings_label.pack()
            
            # Add a simple chart
            fig = Figure(figsize=(8, 4), dpi=100)
            ax = fig.add_subplot(111)
            
            dates = [r['timestamp'] for r in readings]
            ph_values = [r['ph'] for r in readings]
            
            ax.plot(dates, ph_values, 'b-')
            ax.set_title('pH Trend')
            ax.set_ylabel('pH')
            ax.set_xlabel('Date')
            ax.grid(True)
            
            canvas = FigureCanvasTkAgg(fig, master=readings_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        else:
            no_readings = ttk.Label(readings_frame, text="No readings available")
            no_readings.pack(pady=20)
    
    def create_readings_tab(self):
        """Create the readings tab."""
        readings_frame = ttk.Frame(self.notebook, padding=20)
        self.notebook.add(readings_frame, text="Readings")
        
        # Add title
        title = ttk.Label(readings_frame, text="Chemical Readings", font=("Arial", 18))
        title.pack(pady=10)
        
        # Add readings table
        table_frame = ttk.Frame(readings_frame)
        table_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Create treeview
        columns = ("Date", "Free Chlorine", "pH", "Alkalinity", "Hardness", "Cyanuric Acid", "Bromine")
        self.readings_tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        
        # Set column headings
        for col in columns:
            self.readings_tree.heading(col, text=col)
            self.readings_tree.column(col, width=100)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.readings_tree.yview)
        self.readings_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack treeview and scrollbar
        self.readings_tree.pack(side="left", fill=tk.BOTH, expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Add data to treeview
        readings = self.db_service.get_all_readings()
        for reading in readings:
            self.readings_tree.insert("", "end", values=(
                reading['timestamp'].strftime('%Y-%m-%d'),
                reading['free_chlorine'],
                reading['ph'],
                reading['total_alkalinity'],
                reading['total_hardness'],
                reading['cyanuric_acid'],
                reading['total_bromine']
            ))
        
        # Add buttons
        button_frame = ttk.Frame(readings_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(button_frame, text="Add Reading").pack(side="left", padx=5)
        ttk.Button(button_frame, text="Edit Reading").pack(side="left", padx=5)
        ttk.Button(button_frame, text="Delete Reading").pack(side="left", padx=5)
        ttk.Button(button_frame, text="Export Data").pack(side="right", padx=5)
    
    def create_test_strip_tab(self):
        """Create the test strip tab."""
        test_strip_frame = ttk.Frame(self.notebook, padding=20)
        self.notebook.add(test_strip_frame, text="Test Strip")
        
        # Add title
        title = ttk.Label(test_strip_frame, text="Test Strip Analysis", font=("Arial", 18))
        title.pack(pady=10)
        
        # Add instructions
        instructions = ttk.Label(
            test_strip_frame,
            text="Upload an image of your test strip to analyze the chemical levels.",
            wraplength=600
        )
        instructions.pack(pady=10)
        
        # Add upload button
        upload_button = ttk.Button(
            test_strip_frame,
            text="Upload Test Strip Image",
            command=self.upload_test_strip
        )
        upload_button.pack(pady=20)
        
        # Add results frame
        self.results_frame = ttk.LabelFrame(test_strip_frame, text="Analysis Results")
        self.results_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Add placeholder text
        placeholder = ttk.Label(
            self.results_frame,
            text="Upload a test strip image to see the analysis results.",
            padding=20
        )
        placeholder.pack()
    
    def create_customer_management_tab(self):
        """Create the customer management tab."""
        customer_frame = ttk.Frame(self.notebook, padding=20)
        self.notebook.add(customer_frame, text="Customer Management")
        
        # Add title
        title = ttk.Label(customer_frame, text="Customer Management", font=("Arial", 18))
        title.pack(pady=10)
        
        # Create split view with customer list on left and details on right
        split_frame = ttk.Frame(customer_frame)
        split_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Customer list frame (left side)
        list_frame = ttk.LabelFrame(split_frame, text="Customers")
        list_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        # Search frame
        search_frame = ttk.Frame(list_frame)
        search_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT)
        search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=search_var)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        ttk.Button(search_frame, text="Search").pack(side=tk.LEFT)
        
        # Customer treeview
        self.customer_tree = ttk.Treeview(list_frame, columns=("ID", "Name", "Phone"), show="headings")
        self.customer_tree.heading("ID", text="ID")
        self.customer_tree.heading("Name", text="Name")
        self.customer_tree.heading("Phone", text="Phone")
        
        self.customer_tree.column("ID", width=50)
        self.customer_tree.column("Name", width=150)
        self.customer_tree.column("Phone", width=100)
        
        self.customer_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Add scrollbar to treeview
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.customer_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.customer_tree.configure(yscrollcommand=scrollbar.set)
        
        # Customer buttons
        button_frame = ttk.Frame(list_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(button_frame, text="Add Customer").pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Edit Customer").pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Delete Customer").pack(side=tk.LEFT, padx=5)
        
        # Customer details frame (right side)
        details_frame = ttk.LabelFrame(split_frame, text="Customer Details")
        details_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)
        
        # Placeholder for customer details
        details_placeholder = ttk.Label(details_frame, text="Select a customer to view details")
        details_placeholder.pack(pady=20)
        
        # Add data to treeview
        customers = self.db_service.get_all_customers()
        for customer in customers:
            self.customer_tree.insert("", "end", values=(
                customer['id'],
                customer['name'],
                customer['phone']
            ))
    
    def create_settings_tab(self):
        """Create the settings tab."""
        settings_frame = ttk.Frame(self.notebook, padding=20)
        self.notebook.add(settings_frame, text="Settings")
        
        # Add title
        title = ttk.Label(settings_frame, text="Settings", font=("Arial", 18))
        title.pack(pady=10)
        
        # Add settings sections
        general_frame = ttk.LabelFrame(settings_frame, text="General Settings")
        general_frame.pack(fill=tk.X, pady=10)
        
        # Theme setting
        theme_frame = ttk.Frame(general_frame)
        theme_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(theme_frame, text="Theme:").pack(side=tk.LEFT)
        theme_combo = ttk.Combobox(theme_frame, values=["Light", "Dark"])
        theme_combo.current(0)
        theme_combo.pack(side=tk.LEFT, padx=10)
        
        # Units setting
        units_frame = ttk.Frame(general_frame)
        units_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(units_frame, text="Units:").pack(side=tk.LEFT)
        units_combo = ttk.Combobox(units_frame, values=["US", "Metric"])
        units_combo.current(0)
        units_combo.pack(side=tk.LEFT, padx=10)
        
        # Notification settings
        notification_frame = ttk.LabelFrame(settings_frame, text="Notification Settings")
        notification_frame.pack(fill=tk.X, pady=10)
        
        # Email notifications
        email_var = tk.BooleanVar(value=True)
        email_check = ttk.Checkbutton(
            notification_frame,
            text="Enable email notifications",
            variable=email_var
        )
        email_check.pack(anchor="w", padx=10, pady=5)
        
        # SMS notifications
        sms_var = tk.BooleanVar(value=False)
        sms_check = ttk.Checkbutton(
            notification_frame,
            text="Enable SMS notifications",
            variable=sms_var
        )
        sms_check.pack(anchor="w", padx=10, pady=5)
        
        # Save button
        save_button = ttk.Button(settings_frame, text="Save Settings")
        save_button.pack(pady=20)
    
    def upload_test_strip(self):
        """Handle test strip image upload."""
        # In a real application, this would open a file dialog
        # For this simple version, we'll just simulate the analysis
        
        # Clear the results frame
        for widget in self.results_frame.winfo_children():
            widget.destroy()
        
        # Show "analyzing" message
        analyzing_label = ttk.Label(
            self.results_frame,
            text="Analyzing test strip...",
            padding=20
        )
        analyzing_label.pack()
        self.root.update()
        
        # Simulate analysis delay
        time.sleep(1)
        
        # Remove analyzing message
        analyzing_label.destroy()
        
        # Get dummy analysis results
        results = self.test_strip_analyzer.analyze_image("dummy_image.jpg")
        
        # Display results
        results_text = ""
        for chemical, data in results.items():
            results_text += f"{chemical}: {data['value']} {data['unit']}\
"
        
        results_label = ttk.Label(
            self.results_frame,
            text=results_text,
            padding=20
        )
        results_label.pack()
        
        # Add a "Save Results" button
        save_button = ttk.Button(
            self.results_frame,
            text="Save Results"
        )
        save_button.pack(pady=10)
    
    def show_about(self):
        """Show the about dialog."""
        messagebox.showinfo(
            "About",
            "Deep Blue Pool Chemistry\
\
"
            "Version 1.0\
\
"
            "A comprehensive pool chemistry management system."
        )

class PoolChemistryApp:
    """
    Main application class for the Deep Blue Pool Chemistry application.
    
    This class initializes and coordinates all the components of the application.
    """
    
    def __init__(self, config_path: str = "config.json"):
        """
        Initialize the application.
        
        Args:
            config_path: Path to the configuration file
        """
        # Load configuration
        self.config = self._load_config(config_path)
        logger.info(f"Configuration loaded from {config_path}")
        
        logger.info("Initializing Pool Chemistry Application")
        
        # Initialize database service
        self.db_service = DatabaseService(self.config["database"]["path"])
        logger.info("Database service initialized successfully")
        
        # Initialize chemical safety database
        self.chemical_safety_db = ChemicalSafetyDatabase(
            self.config["chemical_safety"]["data_file"]
        )
        logger.info("Chemical safety database initialized successfully")
        
        # Initialize test strip analyzer
        self.test_strip_analyzer = TestStripAnalyzer({
            "profiles_dir": self.config["test_strip"]["profiles_dir"]
        })
        logger.info("Test strip analyzer initialized successfully")
        
        # Initialize weather service
        self.weather_service = WeatherService(
            self.config["weather"]["api_key"],
            self.config["weather"]["default_location"]
        )
        logger.info("Weather service initialized successfully")
        
        # Initialize controller
        self.controller = None  # Will be initialized in run_gui
        
        logger.info("Pool Chemistry Application initialized successfully")
    
    def _load_config(self, config_path: str):
        """
        Load configuration from a JSON file.
        
        Args:
            config_path: Path to the configuration file
            
        Returns:
            Configuration dictionary
        """
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            # Set default values for missing configuration
            if "database" not in config:
                config["database"] = {"path": "data/pool_data.db"}
            
            if "chemical_safety" not in config:
                config["chemical_safety"] = {"data_file": "data/chemical_safety.json"}
            
            if "test_strip" not in config:
                config["test_strip"] = {"profiles_dir": "data/strip_profiles"}
            
            if "weather" not in config:
                config["weather"] = {
                    "api_key": "",
                    "default_location": "New York, US"
                }
            
            return config
        except FileNotFoundError:
            logger.warning(f"Configuration file {config_path} not found. Using default configuration.")
            
            # Create default configuration
            config = {
                "database": {"path": "data/pool_data.db"},
                "chemical_safety": {"data_file": "data/chemical_safety.json"},
                "test_strip": {"profiles_dir": "data/strip_profiles"},
                "weather": {
                    "api_key": "",
                    "default_location": "New York, US"
                }
            }
            
            # Create configuration file
            try:
                if config_path and os.path.dirname(config_path):
                    os.makedirs(os.path.dirname(config_path), exist_ok=True)
                with open(config_path, 'w') as f:
                    json.dump(config, f, indent=4)
            except Exception as e:
                logger.warning(f"Could not create configuration file: {e}")
            
            return config
        except json.JSONDecodeError:
            logger.error(f"Configuration file {config_path} is not valid JSON.")
            raise
    
    def run_gui(self):
        """Run the GUI application."""
        try:
            logger.info("Starting GUI application")
            
            # Create the main window
            root = tk.Tk()
            
            # Initialize the simple tab-based UI
            ui = SimpleTabBasedUI(
                root=root,
                db_service=self.db_service,
                chemical_safety_db=self.chemical_safety_db,
                test_strip_analyzer=self.test_strip_analyzer,
                weather_service=self.weather_service,
                controller=self.controller
            )
            
            logger.info("Simple Tab-based UI initialized successfully")
            
            # Start the main loop
            root.mainloop()
            
        except Exception as e:
            logger.error(f"Error running GUI: {e}")
            import traceback
            logger.error(traceback.format_exc())
            raise RuntimeError(f"Failed to initialize GUI: {e}")
    
    def run_cli(self):
        """Run the CLI application."""
        logger.info("Starting CLI application")
        
        # TODO: Implement CLI application
        print("CLI application not implemented yet.")
    
    def run(self, mode: str = "gui"):
        """
        Run the application in the specified mode.
        
        Args:
            mode: Application mode (gui or cli)
        """
        if mode == "gui":
            self.run_gui()
        elif mode == "cli":
            self.run_cli()
        else:
            logger.error(f"Invalid mode: {mode}")
            raise ValueError(f"Invalid mode: {mode}. Must be 'gui' or 'cli'.")

def main():
    """Main entry point for the application."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Deep Blue Pool Chemistry Application")
    parser.add_argument(
        "--mode", 
        choices=["gui", "cli"], 
        default="gui",
        help="Application mode (gui or cli)"
    )
    parser.add_argument(
        "--config", 
        default="config.json",
        help="Path to configuration file"
    )
    args = parser.parse_args()
    
    # Initialize and run the application
    app = PoolChemistryApp(config_path=args.config)
    app.run(mode=args.mode)

if __name__ == "__main__":
    main()
