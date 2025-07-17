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
from typing import Dict, Any, Optional
import tkinter as tk
from tkinter import ttk, messagebox

# Import updated modules
from database_service import DatabaseService
from chemical_safety_database import ChemicalSafetyDatabase
from test_strip_analyzer import TestStripAnalyzer
from weather_service import WeatherService
from gui_controller import PoolChemistryController

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
        self.config = self._load_config(config_path)
        logger.info("Initializing Pool Chemistry Application")
        
        # Create data directory if it doesn't exist
        os.makedirs("data", exist_ok=True)
        
        # Initialize services
        self.db_service = self._init_database_service()
        self.chemical_safety_db = self._init_chemical_safety_database()
        self.test_strip_analyzer = self._init_test_strip_analyzer()
        self.weather_service = self._init_weather_service()
        
        # Initialize controller
        self.controller = PoolChemistryController(self.db_service)
        
        logger.info("Pool Chemistry Application initialized successfully")
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """
        Load configuration from a JSON file.
        
        Args:
            config_path: Path to the configuration file
            
        Returns:
            Configuration dictionary
            
        Raises:
            FileNotFoundError: If the configuration file doesn't exist
            json.JSONDecodeError: If the configuration file contains invalid JSON
        """
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            logger.info(f"Configuration loaded from {config_path}")
            return config
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.warning(f"Failed to load configuration from {config_path}: {e}")
            logger.info("Using default configuration")
            return {
                "database": {
                    "path": "data/pool_data.db"
                },
                "chemical_safety": {
                    "data_file": "data/chemical_safety_data.json"
                },
                "test_strip": {
                    "brand": "default",
                    "calibration_file": "data/calibration.json"
                },
                "weather": {
                    "location": "Florida",
                    "update_interval": 3600,
                    "cache_file": "data/weather_cache.json"
                }
            }
    
    def _init_database_service(self) -> DatabaseService:
        """
        Initialize the database service.
        
        Returns:
            Database service instance
            
        Raises:
            RuntimeError: If the database service fails to initialize
        """
        try:
            db_path = self.config.get("database", {}).get("path", "data/pool_data.db")
            db_service = DatabaseService(db_path)
            logger.info("Database service initialized successfully")
            return db_service
        except Exception as e:
            logger.error(f"Failed to initialize database service: {e}")
            raise RuntimeError(f"Database initialization error: {e}")
    
    def _init_chemical_safety_database(self) -> ChemicalSafetyDatabase:
        """
        Initialize the chemical safety database.
        
        Returns:
            Chemical safety database instance
            
        Raises:
            RuntimeError: If the chemical safety database fails to initialize
        """
        try:
            data_file = self.config.get("chemical_safety", {}).get("data_file", "data/chemical_safety_data.json")
            chemical_safety_db = ChemicalSafetyDatabase(data_file)
            logger.info("Chemical safety database initialized successfully")
            return chemical_safety_db
        except Exception as e:
            logger.error(f"Failed to initialize chemical safety database: {e}")
            raise RuntimeError(f"Chemical safety database initialization error: {e}")
    
    def _init_test_strip_analyzer(self) -> TestStripAnalyzer:
        """
        Initialize the test strip analyzer.
        
        Returns:
            Test strip analyzer instance
            
        Raises:
            RuntimeError: If the test strip analyzer fails to initialize
        """
        try:
            test_strip_config = self.config.get("test_strip", {})
            test_strip_analyzer = TestStripAnalyzer(test_strip_config)
            logger.info("Test strip analyzer initialized successfully")
            return test_strip_analyzer
        except Exception as e:
            logger.error(f"Failed to initialize test strip analyzer: {e}")
            raise RuntimeError(f"Test strip analyzer initialization error: {e}")
    
    def _init_weather_service(self) -> WeatherService:
        """
        Initialize the weather service.
        
        Returns:
            Weather service instance
            
        Raises:
            RuntimeError: If the weather service fails to initialize
        """
        try:
            weather_config = self.config.get("weather", {})
            weather_service = WeatherService(weather_config)
            logger.info("Weather service initialized successfully")
            return weather_service
        except Exception as e:
            logger.error(f"Failed to initialize weather service: {e}")
            raise RuntimeError(f"Weather service initialization error: {e}")
    
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
            root.title("Deep Blue Pool Chemistry")
            root.geometry("800x600")
            
            # Create a simple UI for demonstration
            frame = ttk.Frame(root, padding="10")
            frame.pack(fill=tk.BOTH, expand=True)
            
            ttk.Label(frame, text="Deep Blue Pool Chemistry", font=("Arial", 16)).pack(pady=10)
            ttk.Label(frame, text="All services initialized successfully").pack(pady=5)
            
            # Add buttons for different features
            ttk.Button(frame, text="Test Strip Analysis", 
                      command=lambda: messagebox.showinfo("Info", "Test Strip Analysis feature selected")).pack(pady=5)
            
            ttk.Button(frame, text="Chemical Safety Information", 
                      command=lambda: messagebox.showinfo("Info", "Chemical Safety Information feature selected")).pack(pady=5)
            
            ttk.Button(frame, text="Weather Impact", 
                      command=lambda: self._show_weather_info(root)).pack(pady=5)
            
            ttk.Button(frame, text="Calculate Chemicals", 
                      command=lambda: self._show_chemical_calculator(root)).pack(pady=5)
            
            ttk.Button(frame, text="Exit", command=root.destroy).pack(pady=20)
            
            # Start the main loop
            root.mainloop()
            
            logger.info("GUI application closed")
        except Exception as e:
            logger.error(f"Error running GUI application: {e}")
            raise RuntimeError(f"GUI error: {e}")
    
    def _show_weather_info(self, parent: tk.Tk) -> None:
        """
        Show weather information in a dialog.
        
        Args:
            parent: Parent window
        """
        try:
            weather_data = self.weather_service.get_weather_with_impact()
            
            # Create a dialog window
            dialog = tk.Toplevel(parent)
            dialog.title("Weather Information")
            dialog.geometry("400x300")
            
            frame = ttk.Frame(dialog, padding="10")
            frame.pack(fill=tk.BOTH, expand=True)
            
            # Display weather information
            weather = weather_data["weather"]
            impact = weather_data["impact"]
            
            ttk.Label(frame, text="Current Weather", font=("Arial", 14)).pack(pady=5)
            ttk.Label(frame, text=f"Temperature: {weather['temperature']}°F").pack(anchor="w")
            ttk.Label(frame, text=f"Conditions: {weather['conditions']}").pack(anchor="w")
            ttk.Label(frame, text=f"Humidity: {weather['humidity']}%").pack(anchor="w")
            ttk.Label(frame, text=f"UV Index: {weather['uv_index']}").pack(anchor="w")
            
            ttk.Separator(frame, orient="horizontal").pack(fill="x", pady=10)
            
            ttk.Label(frame, text="Pool Impact", font=("Arial", 14)).pack(pady=5)
            ttk.Label(frame, text=f"Evaporation Rate: {impact['evaporation_rate']} inches/day").pack(anchor="w")
            ttk.Label(frame, text=f"Chlorine Loss Rate: {impact['chlorine_loss_rate']} ppm/day").pack(anchor="w")
            ttk.Label(frame, text=f"Algae Growth Risk: {impact['algae_growth_risk']}").pack(anchor="w")
            
            if impact["recommendations"]:
                ttk.Separator(frame, orient="horizontal").pack(fill="x", pady=10)
                ttk.Label(frame, text="Recommendations", font=("Arial", 14)).pack(pady=5)
                for rec in impact["recommendations"]:
                    ttk.Label(frame, text=f"• {rec}").pack(anchor="w")
            
            ttk.Button(frame, text="Close", command=dialog.destroy).pack(pady=10)
            
        except Exception as e:
            logger.error(f"Error showing weather information: {e}")
            messagebox.showerror("Error", f"Failed to retrieve weather information: {e}")
    
    def _show_chemical_calculator(self, parent: tk.Tk) -> None:
        """
        Show chemical calculator dialog.
        
        Args:
            parent: Parent window
        """
        try:
            # Create a dialog window
            dialog = tk.Toplevel(parent)
            dialog.title("Chemical Calculator")
            dialog.geometry("500x400")
            
            frame = ttk.Frame(dialog, padding="10")
            frame.pack(fill=tk.BOTH, expand=True)
            
            ttk.Label(frame, text="Pool Chemistry Calculator", font=("Arial", 14)).pack(pady=5)
            
            # Create input fields
            input_frame = ttk.Frame(frame)
            input_frame.pack(fill="x", pady=10)
            
            # Pool type
            ttk.Label(input_frame, text="Pool Type:").grid(row=0, column=0, sticky="w", pady=2)
            pool_type_var = tk.StringVar(value="Concrete/Gunite")
            pool_type_combo = ttk.Combobox(input_frame, textvariable=pool_type_var)
            pool_type_combo["values"] = ("Concrete/Gunite", "Vinyl", "Fiberglass", "Above Ground")
            pool_type_combo.grid(row=0, column=1, sticky="ew", pady=2)
            
            # Pool size
            ttk.Label(input_frame, text="Pool Size (gallons):").grid(row=1, column=0, sticky="w", pady=2)
            pool_size_var = tk.StringVar(value="10000")
            ttk.Entry(input_frame, textvariable=pool_size_var).grid(row=1, column=1, sticky="ew", pady=2)
            
            # pH
            ttk.Label(input_frame, text="pH:").grid(row=2, column=0, sticky="w", pady=2)
            ph_var = tk.StringVar(value="7.2")
            ttk.Entry(input_frame, textvariable=ph_var).grid(row=2, column=1, sticky="ew", pady=2)
            
            # Chlorine
            ttk.Label(input_frame, text="Chlorine (ppm):").grid(row=3, column=0, sticky="w", pady=2)
            chlorine_var = tk.StringVar(value="1.5")
            ttk.Entry(input_frame, textvariable=chlorine_var).grid(row=3, column=1, sticky="ew", pady=2)
            
            # Alkalinity
            ttk.Label(input_frame, text="Alkalinity (ppm):").grid(row=4, column=0, sticky="w", pady=2)
            alkalinity_var = tk.StringVar(value="100")
            ttk.Entry(input_frame, textvariable=alkalinity_var).grid(row=4, column=1, sticky="ew", pady=2)
            
            # Calcium hardness
            ttk.Label(input_frame, text="Calcium Hardness (ppm):").grid(row=5, column=0, sticky="w", pady=2)
            calcium_var = tk.StringVar(value="250")
            ttk.Entry(input_frame, textvariable=calcium_var).grid(row=5, column=1, sticky="ew", pady=2)
            
            # Temperature
            ttk.Label(input_frame, text="Temperature (°F):").grid(row=6, column=0, sticky="w", pady=2)
            temp_var = tk.StringVar(value="78")
            ttk.Entry(input_frame, textvariable=temp_var).grid(row=6, column=1, sticky="ew", pady=2)
            
            # Results text area
            ttk.Label(frame, text="Results:").pack(anchor="w", pady=(10, 2))
            results_text = tk.Text(frame, height=10, width=50)
            results_text.pack(fill="both", expand=True)
            results_text.config(state="disabled")
            
            # Calculate button
            def calculate():
                try:
                    pool_data = {
                        "pool_type": pool_type_var.get(),
                        "pool_size": pool_size_var.get(),
                        "ph": ph_var.get(),
                        "chlorine": chlorine_var.get(),
                        "alkalinity": alkalinity_var.get(),
                        "calcium_hardness": calcium_var.get(),
                        "temperature": temp_var.get()
                    }
                    
                    result = self.controller.calculate_chemicals(pool_data)
                    
                    # Display results
                    results_text.config(state="normal")
                    results_text.delete(1.0, tk.END)
                    
                    # Water balance
                    if result["water_balance"] is not None:
                        results_text.insert(tk.END, f"Water Balance Index: {result['water_balance']}\n")
                        if result["water_balance"] < -0.3:
                            results_text.insert(tk.END, "Water is corrosive. Adjust chemistry.\n")
                        elif result["water_balance"] > 0.3:
                            results_text.insert(tk.END, "Water is scaling. Adjust chemistry.\n")
                        else:
                            results_text.insert(tk.END, "Water is balanced.\n")
                    
                    results_text.insert(tk.END, "\nRecommended Adjustments:\n")
                    
                    # Adjustments
                    if not result["adjustments"]:
                        results_text.insert(tk.END, "No adjustments needed. Water chemistry is good!\n")
                    else:
                        for chem, adj in result["adjustments"].items():
                            results_text.insert(tk.END, f"{chem}: {adj['amount']} {adj['unit']} - {adj['reason']}\n")
                    
                    results_text.config(state="disabled")
                    
                except Exception as e:
                    results_text.config(state="normal")
                    results_text.delete(1.0, tk.END)
                    results_text.insert(tk.END, f"Error: {str(e)}")
                    results_text.config(state="disabled")
                    logger.error(f"Error calculating chemicals: {e}")
            
            ttk.Button(frame, text="Calculate", command=calculate).pack(pady=10)
            ttk.Button(frame, text="Close", command=dialog.destroy).pack(pady=5)
            
        except Exception as e:
            logger.error(f"Error showing chemical calculator: {e}")
            messagebox.showerror("Error", f"Failed to open chemical calculator: {e}")
    
    def run_cli(self) -> None:
        """
        Run the command-line interface.
        
        Raises:
            RuntimeError: If the CLI fails to run
        """
        try:
            logger.info("Starting CLI application")
            
            print("Deep Blue Pool Chemistry CLI")
            print("===========================")
            
            # Get weather information
            weather_data = self.weather_service.get_weather_with_impact()
            weather = weather_data["weather"]
            impact = weather_data["impact"]
            
            print("\nCurrent Weather:")
            print(f"Temperature: {weather['temperature']}°F")
            print(f"Conditions: {weather['conditions']}")
            print(f"Humidity: {weather['humidity']}%")
            print(f"UV Index: {weather['uv_index']}")
            
            print("\nPool Impact:")
            print(f"Evaporation Rate: {impact['evaporation_rate']} inches/day")
            print(f"Chlorine Loss Rate: {impact['chlorine_loss_rate']} ppm/day")
            print(f"Algae Growth Risk: {impact['algae_growth_risk']}")
            
            if impact["recommendations"]:
                print("\nRecommendations:")
                for rec in impact["recommendations"]:
                    print(f"• {rec}")
            
            # Get user input for chemical calculation
            print("\nChemical Calculator")
            print("-----------------")
            
            pool_types = ["Concrete/Gunite", "Vinyl", "Fiberglass", "Above Ground"]
            print("Pool Types:")
            for i, pt in enumerate(pool_types):
                print(f"{i+1}. {pt}")
            
            try:
                pool_type_idx = int(input("\nSelect pool type (1-4): ")) - 1
                pool_type = pool_types[pool_type_idx]
            except (ValueError, IndexError):
                pool_type = "Concrete/Gunite"
                print(f"Invalid selection, using default: {pool_type}")
            
            try:
                pool_size = float(input("Pool size (gallons): "))
            except ValueError:
                pool_size = 10000
                print(f"Invalid input, using default: {pool_size}")
            
            try:
                ph = float(input("pH level: "))
            except ValueError:
                ph = 7.2
                print(f"Invalid input, using default: {ph}")
            
            try:
                chlorine = float(input("Chlorine level (ppm): "))
            except ValueError:
                chlorine = 1.5
                print(f"Invalid input, using default: {chlorine}")
            
            try:
                alkalinity = float(input("Alkalinity level (ppm): "))
            except ValueError:
                alkalinity = 100
                print(f"Invalid input, using default: {alkalinity}")
            
            try:
                calcium = float(input("Calcium hardness level (ppm): "))
            except ValueError:
                calcium = 250
                print(f"Invalid input, using default: {calcium}")
            
            try:
                temperature = float(input("Water temperature (°F): "))
            except ValueError:
                temperature = 78
                print(f"Invalid input, using default: {temperature}")
            
            # Calculate chemicals
            pool_data = {
                "pool_type": pool_type,
                "pool_size": str(pool_size),
                "ph": str(ph),
                "chlorine": str(chlorine),
                "alkalinity": str(alkalinity),
                "calcium_hardness": str(calcium),
                "temperature": str(temperature)
            }
            
            try:
                result = self.controller.calculate_chemicals(pool_data)
                
                print("\nResults:")
                
                # Water balance
                if result["water_balance"] is not None:
                    print(f"Water Balance Index: {result['water_balance']}")
                    if result["water_balance"] < -0.3:
                        print("Water is corrosive. Adjust chemistry.")
                    elif result["water_balance"] > 0.3:
                        print("Water is scaling. Adjust chemistry.")
                    else:
                        print("Water is balanced.")
                
                print("\nRecommended Adjustments:")
                
                # Adjustments
                if not result["adjustments"]:
                    print("No adjustments needed. Water chemistry is good!")
                else:
                    for chem, adj in result["adjustments"].items():
                        print(f"{chem}: {adj['amount']} {adj['unit']} - {adj['reason']}")
                
            except Exception as e:
                print(f"Error calculating chemicals: {e}")
            
            logger.info("CLI application completed")
        except Exception as e:
            logger.error(f"Error running CLI application: {e}")
            raise RuntimeError(f"CLI error: {e}")
    
    def cleanup(self) -> None:
        """
        Clean up resources before exiting.
        """
        try:
            # Close database connections
            if hasattr(self, 'db_service'):
                self.db_service.close_all_connections()
            
            # Clear caches
            if hasattr(self, 'test_strip_analyzer'):
                self.test_strip_analyzer.clear_cache()
            
            if hasattr(self, 'weather_service'):
                self.weather_service.clear_cache()
            
            logger.info("Application resources cleaned up")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")


def parse_args():
    """
    Parse command line arguments.
    
    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(description="Deep Blue Pool Chemistry Application")
    parser.add_argument("--gui", action="store_true", help="Run in GUI mode (default)")
    parser.add_argument("--cli", action="store_true", help="Run in CLI mode")
    parser.add_argument("--config", type=str, default="config.json", help="Path to configuration file")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    return parser.parse_args()


def main():
    """
    Main entry point for the application.
    """
    # Parse command line arguments
    args = parse_args()
    
    # Set log level
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Debug logging enabled")
    
    # Create and run the application
    app = None
    try:
        app = PoolChemistryApp(args.config)
        
        # Run in CLI or GUI mode
        if args.cli:
            app.run_cli()
        else:
            app.run_gui()
        
        return 0
    except Exception as e:
        logger.error(f"Application error: {e}")
        return 1
    finally:
        # Clean up resources
        if app:
            app.cleanup()


if __name__ == "__main__":
    sys.exit(main())