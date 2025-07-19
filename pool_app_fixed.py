"""
Consolidated Pool Chemistry Application.

This module brings together all the updated components of the Deep Blue Pool Chemistry
application into a single, cohesive application.
"""

import logging
import os
import sys
import json
import argparse
import serial
import serial.tools.list_ports
from typing import Dict, Any, Optional, List, Tuple
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

# Import service modules with standardized paths
from services.database_service import DatabaseService
from services.chemical_safety_database import ChemicalSafetyDatabase
from services.test_strip import TestStripAnalyzer
from services.weather import WeatherService

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
        
        # Initialize test strip analyzer
        self.test_strip_analyzer = TestStripAnalyzer(
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
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
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
            
            # Create configuration file - FIX: Check if path is valid before creating directories
            if config_path and os.path.dirname(config_path):
                os.makedirs(os.path.dirname(config_path), exist_ok=True)
                with open(config_path, 'w') as f:
                    json.dump(config, f, indent=4)
            else:
                # If config_path is empty or has no directory part, write to current directory
                with open("config.json", 'w') as f:
                    json.dump(config, f, indent=4)
            
            return config
        except json.JSONDecodeError:
            logger.error(f"Configuration file {config_path} is not valid JSON.")
            raise
    
    def run_gui(self) -> None:
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
                
                # Try to initialize Arduino Monitor
                try:
                    # Try different import paths to be more robust
                    try:
                        from services.arduino_monitor_app import ArduinoMonitorApp
                    except ImportError:
                        try:
                            from arduino_monitor_app import ArduinoMonitorApp
                        except ImportError:
                            raise ImportError("Could not import ArduinoMonitorApp")
                    
                    # Create Arduino Monitor tab
                    arduino_frame = ttk.Frame(notebook)
                    notebook.add(arduino_frame, text="Arduino Sensors")
                    
                    # Initialize Arduino Monitor in the tab
                    arduino_monitor = ArduinoMonitorApp(arduino_frame)
                    
                    logger.info("Arduino Monitor initialized successfully")
                except Exception as e:
                    logger.error(f"Error initializing Arduino Monitor: {e}")
                    
                    # Create Arduino Monitor tab with error message
                    arduino_frame = ttk.Frame(notebook, padding=20)
                    notebook.add(arduino_frame, text="Arduino Sensors")
                    
                    ttk.Label(arduino_frame, text="Arduino Monitor could not be initialized", 
                             foreground="red").pack(pady=20)
                    ttk.Label(arduino_frame, text=f"Error: {str(e)}").pack(pady=10)
                
                # Start the main loop
                root.mainloop()
        
        except Exception as e:
            logger.error(f"Error running GUI: {e}")
            import traceback
            logger.error(traceback.format_exc())
            raise RuntimeError(f"Failed to initialize GUI: {e}")
    
    def run_cli(self) -> None:
        """Run the CLI application."""
        logger.info("Starting CLI application")
        
        # TODO: Implement CLI application
        print("CLI application not implemented yet.")
    
    def run(self, mode: str = "gui") -> None:
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