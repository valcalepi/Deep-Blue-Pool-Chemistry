
"""
Deep Blue Pool Chemistry Application - Fixed Version

This version fixes the import issues and TestStripAnalyzer initialization problem.
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
logger = logging.getLogger("PoolApp")

# Add the current directory to the path to help with imports
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Try different import approaches to be more robust
try:
    # First try importing from the services package
    try:
        from services.database_service import DatabaseService
        from services.chemical_safety_database import ChemicalSafetyDatabase
        from services.test_strip.test_strip_analyzer import TestStripAnalyzer
        from services.weather.weather_service import WeatherService
        logger.info("Successfully imported services from services package")
    except ImportError:
        # Then try importing directly
        try:
            from database_service import DatabaseService
            from chemical_safety_database import ChemicalSafetyDatabase
            from test_strip_analyzer import TestStripAnalyzer
            from weather_service import WeatherService
            logger.info("Successfully imported services directly")
        except ImportError:
            # Try importing from app directory
            try:
                from app.database_service import DatabaseService
                from app.chemical_safety_database import ChemicalSafetyDatabase
                from app.test_strip_analyzer import TestStripAnalyzer
                from app.weather_service import WeatherService
                logger.info("Successfully imported services from app package")
            except ImportError:
                # Try importing from app.services directory
                try:
                    from app.services.database_service import DatabaseService
                    from app.services.chemical_safety_database import ChemicalSafetyDatabase
                    from app.services.test_strip_analyzer import TestStripAnalyzer
                    from app.services.weather_service import WeatherService
                    logger.info("Successfully imported services from app.services package")
                except ImportError:
                    logger.error("Could not import required modules. Check your Python path and file structure.")
                    raise
except Exception as e:
    logger.error(f"Error during imports: {e}")
    raise

class PoolChemistryApp:
    """
    Main application class for the Deep Blue Pool Chemistry application.
    
    This class initializes and coordinates all the components of the application.
    
    Attributes:
        config: Configuration dictionary
        db_service: Database service instance
        chemical_safety_db: Chemical safety database instance
        test_strip_analyzer: Test strip analyzer instance
        weather_service: Weather service instance
        controller: Pool chemistry controller instance
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
        
        # Initialize test strip analyzer - FIX: Pass a dictionary instead of a string
        # The key issue was here - TestStripAnalyzer expects a dictionary, not a string
        try:
            # First try with a dictionary containing profiles_dir
            self.test_strip_analyzer = TestStripAnalyzer({
                "profiles_dir": self.config["test_strip"]["profiles_dir"]
            })
        except (ValueError, TypeError) as e:
            logger.warning(f"First attempt to initialize TestStripAnalyzer failed: {e}")
            try:
                # If that fails, try passing the string directly
                self.test_strip_analyzer = TestStripAnalyzer(
                    self.config["test_strip"]["profiles_dir"]
                )
            except Exception as e2:
                logger.warning(f"Second attempt to initialize TestStripAnalyzer failed: {e2}")
                # Last resort: create with empty config and set profiles_dir manually
                self.test_strip_analyzer = TestStripAnalyzer()
                if hasattr(self.test_strip_analyzer, 'set_profiles_dir'):
                    self.test_strip_analyzer.set_profiles_dir(
                        self.config["test_strip"]["profiles_dir"]
                    )
        
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
            
        Raises:
            FileNotFoundError: If the configuration file is not found
            json.JSONDecodeError: If the configuration file is not valid JSON
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
        """
        Run the GUI application.
        
        Raises:
            RuntimeError: If the GUI fails to initialize
        """
        try:
            logger.info("Starting GUI application")
            
            # Create the main window
            root = tk.Tk()
            
            # Import the tab-based UI
            try:
                # Try different import paths to be more robust
                try:
                    from ui.tab_based_ui import TabBasedUI
                except ImportError:
                    try:
                        from tab_based_ui import TabBasedUI
                    except ImportError:
                        try:
                            from app.ui.tab_based_ui import TabBasedUI
                        except ImportError:
                            try:
                                from app.tab_based_ui import TabBasedUI
                            except ImportError:
                                raise ImportError("Could not import TabBasedUI. Make sure it's in the ui directory or current directory.")
                
                # Initialize the tab-based UI
                ui = TabBasedUI(
                    root=root,
                    db_service=self.db_service,
                    chemical_safety_db=self.chemical_safety_db,
                    test_strip_analyzer=self.test_strip_analyzer,
                    weather_service=self.weather_service,
                    controller=self.controller
                )
                
                logger.info("Tab-based UI initialized successfully")
                
                # Start the main loop
                root.mainloop()
                
            except Exception as e:
                logger.error(f"Error initializing tab-based UI: {e}")
                import traceback
                logger.error(traceback.format_exc())
                
                # Fall back to basic UI
                root.title("Deep Blue Pool Chemistry")
                root.geometry("1000x700")
                
                # Set icon if available
                icon_path = os.path.join("assests", "chemistry.png")
                if os.path.exists(icon_path):
                    try:
                        icon = tk.PhotoImage(file=icon_path)
                        root.iconphoto(True, icon)
                    except Exception as e:
                        logger.warning(f"Failed to load icon: {e}")
                
                # Create notebook for tabs
                notebook = ttk.Notebook(root)
                notebook.pack(fill=tk.BOTH, expand=True)
                
                # Create main dashboard tab
                dashboard_frame = ttk.Frame(notebook, padding=20)
                notebook.add(dashboard_frame, text="Dashboard")
                
                # Add title
                title = ttk.Label(dashboard_frame, text="Deep Blue Pool Chemistry", font=("Arial", 24))
                title.pack(pady=20)
                
                # Add subtitle
                subtitle = ttk.Label(dashboard_frame, text="Pool Chemistry Management System with Arduino Integration", font=("Arial", 14))
                subtitle.pack(pady=10)
                
                # Add message
                message = ttk.Label(
                    dashboard_frame, 
                    text="The tab-based UI could not be initialized. Using basic UI instead.",
                    foreground="red"
                )
                message.pack(pady=20)
                
                # Add error details
                error_frame = ttk.LabelFrame(dashboard_frame, text="Error Details")
                error_frame.pack(fill=tk.BOTH, expand=True, pady=20)
                
                error_text = scrolledtext.ScrolledText(error_frame, height=10)
                error_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
                error_text.insert(tk.END, traceback.format_exc())
                error_text.config(state=tk.DISABLED)
                
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
