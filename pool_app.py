
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
from tkinter import ttk, messagebox, filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime

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
        self.test_strip_analyzer = TestStripAnalyzer(self.config["test_strip"])
        logger.info("Test strip analyzer initialized successfully")
        
        # Initialize weather service
        self.weather_service = WeatherService(self.config["weather"])
        logger.info("Weather service initialized successfully")
        
        # Initialize controller
        self.controller = PoolChemistryController(self.db_service)
        logger.info("Pool Chemistry Application initialized successfully")
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """
        Load configuration from file.
        
        Args:
            config_path: Path to the configuration file
        
        Returns:
            Configuration dictionary
        """
        try:
            with open(config_path, "r") as f:
                config = json.load(f)
            return config
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            # Use default configuration if loading fails
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
                },
                "pool": {
                    "size": "10000",
                    "type": "chlorine",
                    "test_strip_brand": "default"
                },
                "display": {
                    "theme": "light",
                    "font_size": "normal",
                    "chart_dpi": "100"
                }
            }
    
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
            
            # Add title to dashboard
            title = ttk.Label(dashboard_frame, text="Deep Blue Pool Chemistry", font=("Arial", 24))
            title.pack(pady=20)
            
            # Add subtitle
            subtitle = ttk.Label(dashboard_frame, text="Pool Chemistry Management System with Arduino Integration", font=("Arial", 14))
            subtitle.pack(pady=10)
            
            # Add buttons
            ttk.Button(dashboard_frame, text="Test Strip Analysis", 
                      command=lambda: self._show_test_strip_analyzer(root)).pack(pady=5)
            
            ttk.Button(dashboard_frame, text="Chemical Safety Information", 
                      command=lambda: self._show_chemical_safety(root)).pack(pady=5)
            
            ttk.Button(dashboard_frame, text="Weather Impact", 
                      command=lambda: self._show_weather_info(root)).pack(pady=5)
            
            ttk.Button(dashboard_frame, text="Calculate Chemicals", 
                      command=lambda: self._show_chemical_calculator(root)).pack(pady=5)
            
            # Create Arduino Monitor tab
            try:
                # Import the Arduino Monitor
                from app.arduino_monitor import ArduinoMonitorApp
                
                # Create Arduino Monitor tab
                arduino_frame = ttk.Frame(notebook)
                notebook.add(arduino_frame, text="Arduino Sensors")
                
                # Initialize Arduino Monitor in the tab
                arduino_monitor = ArduinoMonitorApp(arduino_frame)
                
                logger.info("Arduino Monitor initialized successfully")
            except Exception as e:
                logger.error(f"Error initializing Arduino Monitor: {e}")
                import traceback
                logger.error(traceback.format_exc())
                
                # Create a placeholder frame with error message
                arduino_frame = ttk.Frame(notebook, padding=20)
                notebook.add(arduino_frame, text="Arduino Sensors")
                
                ttk.Label(arduino_frame, text="Arduino Monitor could not be initialized", 
                         font=("Arial", 16)).pack(pady=20)
                ttk.Label(arduino_frame, text=f"Error: {str(e)}").pack(pady=10)
            
            # Create exit button at the bottom
            exit_frame = ttk.Frame(root)
            exit_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=10, pady=10)
            ttk.Button(exit_frame, text="Exit", command=root.destroy).pack(side=tk.RIGHT)
            
            # Start the main loop
            root.mainloop()
            
        except Exception as e:
            logger.error(f"Error in GUI application: {e}")
            import traceback
            logger.error(traceback.format_exc())
            raise RuntimeError(f"GUI application failed: {e}")
    
    def _show_test_strip_analyzer(self, parent: tk.Tk) -> None:
        """
        Show test strip analyzer dialog.
        
        Args:
            parent: Parent window
        """
        # Create dialog
        dialog = tk.Toplevel(parent)
        dialog.title("Test Strip Analyzer")
        dialog.geometry("600x500")
        dialog.transient(parent)
        dialog.grab_set()
        
        # Create frame
        frame = ttk.Frame(dialog, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Add title
        title = ttk.Label(frame, text="Test Strip Analyzer", font=("Arial", 18))
        title.pack(pady=10)
        
        # Add instructions
        instructions = ttk.Label(frame, text="Capture or load an image of your test strip to analyze it.")
        instructions.pack(pady=5)
        
        # Add image frame
        image_frame = ttk.LabelFrame(frame, text="Test Strip Image")
        image_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Add image label
        image_label = ttk.Label(image_frame, text="No image loaded")
        image_label.pack(fill=tk.BOTH, expand=True, padx=50, pady=50)
        
        # Add buttons frame
        buttons_frame = ttk.Frame(frame)
        buttons_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Image path variable
        image_path_var = tk.StringVar()
        
        # Function to load image
        def load_image():
            file_path = filedialog.askopenfilename(
                title="Select Test Strip Image",
                filetypes=[("Image files", "*.jpg *.jpeg *.png")]
            )
            if file_path:
                image_path_var.set(file_path)
                image_label.config(text=f"Image loaded: {os.path.basename(file_path)}")
                messagebox.showinfo("Image Loaded", f"Image loaded successfully: {os.path.basename(file_path)}")
        
        # Function to capture image
        def capture_image():
            try:
                image_path = self.test_strip_analyzer.capture_image()
                if image_path:
                    image_path_var.set(image_path)
                    image_label.config(text=f"Image captured: {os.path.basename(image_path)}")
                    messagebox.showinfo("Image Captured", f"Image captured successfully: {os.path.basename(image_path)}")
                else:
                    messagebox.showerror("Error", "Failed to capture image")
            except Exception as e:
                logger.error(f"Error capturing image: {e}")
                messagebox.showerror("Error", f"Failed to capture image: {e}")
        
        # Function to analyze image
        def analyze_image():
            if not image_path_var.get():
                messagebox.showerror("Error", "No image loaded or captured")
                return
            
            try:
                # Set the image path for the analyzer
                self.test_strip_analyzer.image_path = image_path_var.get()
                
                # Analyze the image
                results = self.test_strip_analyzer.analyze()
                
                if results:
                    # Create results dialog
                    results_dialog = tk.Toplevel(dialog)
                    results_dialog.title("Analysis Results")
                    results_dialog.geometry("400x400")
                    results_dialog.transient(dialog)
                    results_dialog.grab_set()
                    
                    # Create frame
                    results_frame = ttk.Frame(results_dialog, padding=20)
                    results_frame.pack(fill=tk.BOTH, expand=True)
                    
                    # Add title
                    results_title = ttk.Label(results_frame, text="Analysis Results", font=("Arial", 16))
                    results_title.pack(pady=10)
                    
                    # Add results
                    for param, value in results.items():
                        param_name = param.replace("_", " ").title()
                        ttk.Label(results_frame, text=f"{param_name}: {value}").pack(anchor=tk.W, pady=2)
                    
                    # Add recommendations
                    recommendations = self.test_strip_analyzer.get_recommendations(results)
                    
                    if recommendations:
                        ttk.Label(results_frame, text="\
Recommendations:", font=("Arial", 12, "bold")).pack(anchor=tk.W, pady=5)
                        
                        for param, recommendation in recommendations.items():
                            param_name = param.replace("_", " ").title()
                            ttk.Label(results_frame, text=f"{param_name}: {recommendation}").pack(anchor=tk.W, pady=2)
                    
                    # Add close button
                    ttk.Button(results_frame, text="Close", command=results_dialog.destroy).pack(pady=10)
                else:
                    messagebox.showerror("Error", "Analysis failed")
            except Exception as e:
                logger.error(f"Error analyzing image: {e}")
                messagebox.showerror("Error", f"Analysis failed: {e}")
        
        # Add buttons
        ttk.Button(buttons_frame, text="Capture Image", command=capture_image).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Load Image", command=load_image).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Analyze", command=analyze_image).pack(side=tk.LEFT, padx=5)
        
        # Add close button
        ttk.Button(frame, text="Close", command=dialog.destroy).pack(pady=10)
    
    def _show_weather_info(self, parent: tk.Tk) -> None:
        """
        Show weather information in a dialog.
        
        Args:
            parent: Parent window
        """
        # Create dialog
        dialog = tk.Toplevel(parent)
        dialog.title("Weather Impact")
        dialog.geometry("600x500")
        dialog.transient(parent)
        dialog.grab_set()
        
        # Create frame
        frame = ttk.Frame(dialog, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Add title
        title = ttk.Label(frame, text="Weather Impact", font=("Arial", 18))
        title.pack(pady=10)
        
        try:
            # Get weather data
            weather_data = self.weather_service.get_weather()
            
            # Add current weather frame
            current_frame = ttk.LabelFrame(frame, text="Current Weather")
            current_frame.pack(fill=tk.X, padx=10, pady=5)
            
            # Add current weather info
            ttk.Label(current_frame, text=f"Location: {self.config['weather']['location']}").grid(row=0, column=0, padx=5, pady=2, sticky=tk.W)
            ttk.Label(current_frame, text=f"Temperature: {weather_data.get('temperature', 'Unknown')}\u00b0F").grid(row=0, column=1, padx=5, pady=2, sticky=tk.W)
            ttk.Label(current_frame, text=f"Humidity: {weather_data.get('humidity', 'Unknown')}%").grid(row=1, column=0, padx=5, pady=2, sticky=tk.W)
            ttk.Label(current_frame, text=f"Conditions: {weather_data.get('conditions', 'Unknown')}").grid(row=1, column=1, padx=5, pady=2, sticky=tk.W)
            
            # Get forecast
            forecast = self.weather_service.get_forecast(3)
            
            # Add forecast frame
            forecast_frame = ttk.LabelFrame(frame, text="3-Day Forecast")
            forecast_frame.pack(fill=tk.X, padx=10, pady=5)
            
            # Add forecast info
            for i, day in enumerate(forecast):
                ttk.Label(forecast_frame, text=f"Day {i+1}: {day.get('temperature', 'Unknown')}\u00b0F, {day.get('conditions', 'Unknown')}").pack(anchor=tk.W, padx=5, pady=2)
            
            # Get weather impact
            impact = self.weather_service.analyze_weather_impact(weather_data)
            
            # Add impact frame
            impact_frame = ttk.LabelFrame(frame, text="Impact on Pool Chemistry")
            impact_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
            
            # Add impact info
            ttk.Label(impact_frame, text=f"\u2022 Evaporation Rate: {impact.get('evaporation_rate', 'Unknown')} inches per day").pack(anchor=tk.W, padx=5, pady=2)
            ttk.Label(impact_frame, text=f"\u2022 Chlorine Loss Rate: {impact.get('chlorine_loss_rate', 'Unknown')}% per day").pack(anchor=tk.W, padx=5, pady=2)
            
            if weather_data.get('temperature', 0) > 85:
                ttk.Label(impact_frame, text="\u2022 Higher temperatures may increase chlorine consumption").pack(anchor=tk.W, padx=5, pady=2)
            
            if weather_data.get('conditions', '').lower() in ['sunny', 'clear']:
                ttk.Label(impact_frame, text="\u2022 UV exposure will degrade chlorine faster").pack(anchor=tk.W, padx=5, pady=2)
            
            if weather_data.get('conditions', '').lower() in ['rain', 'showers', 'thunderstorm']:
                ttk.Label(impact_frame, text="\u2022 Rain may dilute chemicals and affect water balance").pack(anchor=tk.W, padx=5, pady=2)
            else:
                ttk.Label(impact_frame, text="\u2022 No rain expected, so no dilution of chemicals").pack(anchor=tk.W, padx=5, pady=2)
            
            # Add refresh button
            ttk.Button(frame, text="Refresh Weather Data", command=lambda: self._refresh_weather_data(dialog)).pack(pady=10)
            
        except Exception as e:
            logger.error(f"Error getting weather data: {e}")
            ttk.Label(frame, text=f"Error getting weather data: {e}").pack(pady=10)
        
        # Add close button
        ttk.Button(frame, text="Close", command=dialog.destroy).pack(pady=10)
    
    def _refresh_weather_data(self, dialog: tk.Toplevel) -> None:
        """
        Refresh weather data and update the dialog.
        
        Args:
            dialog: Weather dialog
        """
        # Close the current dialog
        dialog.destroy()
        
        # Clear weather cache
        self.weather_service.clear_cache()
        
        # Show weather info again
        self._show_weather_info(dialog.master)
    
    def _show_chemical_calculator(self, parent: tk.Tk) -> None:
        """
        Show chemical calculator dialog.
        
        Args:
            parent: Parent window
        """
        # Create dialog
        dialog = tk.Toplevel(parent)
        dialog.title("Chemical Calculator")
        dialog.geometry("600x500")
        dialog.transient(parent)
        dialog.grab_set()
        
        # Create frame
        frame = ttk.Frame(dialog, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Add title
        title = ttk.Label(frame, text="Chemical Calculator", font=("Arial", 18))
        title.pack(pady=10)
        
        # Add instructions
        instructions = ttk.Label(frame, text="Enter your pool information and test results to calculate chemical adjustments.")
        instructions.pack(pady=5)
        
        # Add pool info frame
        pool_frame = ttk.LabelFrame(frame, text="Pool Information")
        pool_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Add pool info fields
        ttk.Label(pool_frame, text="Pool Type:").grid(row=0, column=0, padx=5, pady=2, sticky=tk.W)
        pool_type_var = tk.StringVar(value="Concrete/Gunite")
        pool_type_combo = ttk.Combobox(pool_frame, textvariable=pool_type_var, values=["Concrete/Gunite", "Vinyl", "Fiberglass"])
        pool_type_combo.grid(row=0, column=1, padx=5, pady=2, sticky=tk.W)
        
        ttk.Label(pool_frame, text="Pool Size (gallons):").grid(row=1, column=0, padx=5, pady=2, sticky=tk.W)
        pool_size_var = tk.StringVar(value=self.config["pool"]["size"])
        pool_size_entry = ttk.Entry(pool_frame, textvariable=pool_size_var)
        pool_size_entry.grid(row=1, column=1, padx=5, pady=2, sticky=tk.W)
        
        # Add test results frame
        test_frame = ttk.LabelFrame(frame, text="Test Results")
        test_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Add test result fields
        ttk.Label(test_frame, text="pH:").grid(row=0, column=0, padx=5, pady=2, sticky=tk.W)
        ph_var = tk.StringVar(value="7.2")
        ph_entry = ttk.Entry(test_frame, textvariable=ph_var)
        ph_entry.grid(row=0, column=1, padx=5, pady=2, sticky=tk.W)
        
        ttk.Label(test_frame, text="Free Chlorine (ppm):").grid(row=0, column=2, padx=5, pady=2, sticky=tk.W)
        chlorine_var = tk.StringVar(value="1.5")
        chlorine_entry = ttk.Entry(test_frame, textvariable=chlorine_var)
        chlorine_entry.grid(row=0, column=3, padx=5, pady=2, sticky=tk.W)
        
        ttk.Label(test_frame, text="Alkalinity (ppm):").grid(row=1, column=0, padx=5, pady=2, sticky=tk.W)
        alkalinity_var = tk.StringVar(value="100")
        alkalinity_entry = ttk.Entry(test_frame, textvariable=alkalinity_var)
        alkalinity_entry.grid(row=1, column=1, padx=5, pady=2, sticky=tk.W)
        
        ttk.Label(test_frame, text="Calcium Hardness (ppm):").grid(row=1, column=2, padx=5, pady=2, sticky=tk.W)
        calcium_var = tk.StringVar(value="250")
        calcium_entry = ttk.Entry(test_frame, textvariable=calcium_var)
        calcium_entry.grid(row=1, column=3, padx=5, pady=2, sticky=tk.W)
        
        ttk.Label(test_frame, text="Temperature (\u00b0F):").grid(row=2, column=0, padx=5, pady=2, sticky=tk.W)
        temp_var = tk.StringVar(value="78")
        temp_entry = ttk.Entry(test_frame, textvariable=temp_var)
        temp_entry.grid(row=2, column=1, padx=5, pady=2, sticky=tk.W)
        
        # Add results frame
        results_frame = ttk.LabelFrame(frame, text="Recommended Adjustments")
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Add result labels
        results_label = ttk.Label(results_frame, text="No calculations performed yet.")
        results_label.pack(anchor=tk.W, padx=5, pady=2)
        
        # Function to calculate chemicals
        def calculate():
            try:
                # Get values from fields
                pool_data = {
                    "pool_type": pool_type_var.get(),
                    "pool_size": pool_size_var.get(),
                    "ph": ph_var.get(),
                    "chlorine": chlorine_var.get(),
                    "alkalinity": alkalinity_var.get(),
                    "calcium_hardness": calcium_var.get(),
                    "temperature": temp_var.get()
                }
                
                # Validate data
                errors = self.controller.validate_pool_data(pool_data)
                if errors:
                    error_message = "\
".join(errors)
                    messagebox.showerror("Validation Error", f"Please correct the following errors:\
\
{error_message}")
                    return
                
                # Calculate chemicals
                result = self.controller.calculate_chemicals(pool_data)
                
                # Clear results frame
                for widget in results_frame.winfo_children():
                    widget.destroy()
                
                # Add results
                if "adjustments" in result:
                    adjustments = result["adjustments"]
                    
                    for chemical, amount in adjustments.items():
                        chemical_name = chemical.replace("_", " ").title()
                        ttk.Label(results_frame, text=f"{chemical_name}: {amount} oz").pack(anchor=tk.W, padx=5, pady=2)
                
                if "water_balance" in result:
                    balance = result["water_balance"]
                    ttk.Label(results_frame, text=f"\
Water Balance Index: {balance:.2f}").pack(anchor=tk.W, padx=5, pady=2)
                    
                    if balance < -0.5:
                        ttk.Label(results_frame, text="Water is corrosive.").pack(anchor=tk.W, padx=5, pady=2)
                    elif balance > 0.5:
                        ttk.Label(results_frame, text="Water is scale-forming.").pack(anchor=tk.W, padx=5, pady=2)
                    else:
                        ttk.Label(results_frame, text="Water is balanced.").pack(anchor=tk.W, padx=5, pady=2)
                
                # Save test results
                test_id = self.controller.save_test_results(pool_data)
                if test_id:
                    ttk.Label(results_frame, text=f"\
Test results saved with ID: {test_id}").pack(anchor=tk.W, padx=5, pady=2)
                
            except Exception as e:
                logger.error(f"Error calculating chemicals: {e}")
                messagebox.showerror("Error", f"Calculation failed: {e}")
        
        # Add calculate button
        ttk.Button(frame, text="Calculate", command=calculate).pack(pady=10)
        ttk.Button(frame, text="Close", command=dialog.destroy).pack(pady=5)
    
    def _show_chemical_safety(self, parent: tk.Tk) -> None:
        """
        Show chemical safety information dialog.
        
        Args:
            parent: Parent window
        """
        # Create dialog
        dialog = tk.Toplevel(parent)
        dialog.title("Chemical Safety Information")
        dialog.geometry("600x500")
        dialog.transient(parent)
        dialog.grab_set()
        
        # Create frame
        frame = ttk.Frame(dialog, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Add title
        title = ttk.Label(frame, text="Chemical Safety Information", font=("Arial", 18))
        title.pack(pady=10)
        
        # Get all chemicals
        chemicals = self.chemical_safety_db.get_all_chemicals()
        
        # Add chemical selection frame
        selection_frame = ttk.Frame(frame)
        selection_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Add chemical selection
        ttk.Label(selection_frame, text="Select Chemical:").pack(side=tk.LEFT, padx=5)
        
        # Create list of chemical names
        chemical_names = []
        chemical_ids = []
        
        for chemical_id, chemical_info in chemicals.items():
            chemical_names.append(chemical_info["name"])
            chemical_ids.append(chemical_id)
        
        # Add combobox
        chemical_var = tk.StringVar()
        chemical_combo = ttk.Combobox(selection_frame, textvariable=chemical_var, values=chemical_names)
        chemical_combo.pack(side=tk.LEFT, padx=5)
        
        # Add safety info frame
        safety_frame = ttk.LabelFrame(frame, text="Safety Information")
        safety_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Function to update safety info
        def update_safety_info(*args):
            # Clear safety frame
            for widget in safety_frame.winfo_children():
                widget.destroy()
            
            # Get selected chemical
            selected_name = chemical_var.get()
            if not selected_name:
                return
            
            # Find chemical ID
            selected_id = None
            for i, name in enumerate(chemical_names):
                if name == selected_name:
                    selected_id = chemical_ids[i]
                    break
            
            if not selected_id:
                return
            
            # Get chemical info
            chemical = self.chemical_safety_db.get_chemical_safety_info(selected_id)
            
            # Add safety info
            ttk.Label(safety_frame, text=f"Chemical: {chemical['name']}").pack(anchor=tk.W, padx=5, pady=2)
            ttk.Label(safety_frame, text=f"Chemical Formula: {chemical['chemical_formula']}").pack(anchor=tk.W, padx=5, pady=2)
            ttk.Label(safety_frame, text=f"Hazard Rating: {chemical['hazard_rating']}").pack(anchor=tk.W, padx=5, pady=2)
            
            # Add safety precautions frame
            precautions_frame = ttk.LabelFrame(safety_frame, text="Safety Precautions")
            precautions_frame.pack(fill=tk.X, padx=5, pady=5)
            
            # Add safety precautions
            for precaution in chemical['safety_precautions']:
                ttk.Label(precautions_frame, text=f"\u2022 {precaution}").pack(anchor=tk.W, padx=5, pady=2)
            
            # Add storage guidelines frame
            storage_frame = ttk.LabelFrame(safety_frame, text="Storage Guidelines")
            storage_frame.pack(fill=tk.X, padx=5, pady=5)
            
            # Add storage guidelines
            ttk.Label(storage_frame, text=chemical['storage_guidelines']).pack(anchor=tk.W, padx=5, pady=2)
            
            # Add emergency procedures frame
            emergency_frame = ttk.LabelFrame(safety_frame, text="Emergency Procedures")
            emergency_frame.pack(fill=tk.X, padx=5, pady=5)
            
            # Add emergency procedures
            ttk.Label(emergency_frame, text=chemical['emergency_procedures']).pack(anchor=tk.W, padx=5, pady=2)
            
            # Add compatibility frame
            compatibility_frame = ttk.LabelFrame(safety_frame, text="Chemical Compatibility")
            compatibility_frame.pack(fill=tk.X, padx=5, pady=5)
            
            # Get compatibility
            compatibility = self.chemical_safety_db.get_compatibility(selected_id)
            
            # Add compatibility info
            ttk.Label(compatibility_frame, text="Compatible with:").pack(anchor=tk.W, padx=5, pady=2)
            
            compatible = [chem for chem, compat in compatibility.items() if compat]
            if compatible:
                for chem in compatible:
                    chem_info = self.chemical_safety_db.get_chemical_safety_info(chem)
                    ttk.Label(compatibility_frame, text=f"\u2022 {chem_info['name']}").pack(anchor=tk.W, padx=20, pady=2)
            else:
                ttk.Label(compatibility_frame, text="\u2022 None").pack(anchor=tk.W, padx=20, pady=2)
            
            ttk.Label(compatibility_frame, text="Incompatible with:").pack(anchor=tk.W, padx=5, pady=2)
            
            incompatible = [chem for chem, compat in compatibility.items() if not compat]
            if incompatible:
                for chem in incompatible:
                    chem_info = self.chemical_safety_db.get_chemical_safety_info(chem)
                    ttk.Label(compatibility_frame, text=f"\u2022 {chem_info['name']}").pack(anchor=tk.W, padx=20, pady=2)
            else:
                ttk.Label(compatibility_frame, text="\u2022 None").pack(anchor=tk.W, padx=20, pady=2)
        
        # Bind combobox to update function
        chemical_var.trace("w", update_safety_info)
        
        # Set default value
        if chemical_names:
            chemical_combo.current(0)
            update_safety_info()
        
        # Add close button
        ttk.Button(frame, text="Close", command=dialog.destroy).pack(pady=10)
    
    def run_cli(self) -> None:
        """Run the application in CLI mode."""
        logger.info("Starting CLI application")
        
        # Get weather data
        weather_data = self.weather_service.get_weather()
        
        # Print welcome message
        print("\
Deep Blue Pool Chemistry CLI")
        print("===========================")
        print(f"Current Weather: {weather_data.get('conditions', 'Unknown')}, {weather_data.get('temperature', 'Unknown')}\u00b0F")
        
        # Main loop
        while True:
            # Print menu
            print("\
Menu:")
            print("1. Test Water Chemistry")
            print("2. View Recent Tests")
            print("3. Calculate Chemical Adjustments")
            print("4. Check Weather Impact")
            print("5. View Chemical Safety Information")
            print("6. Exit")
            
            # Get user choice
            choice = input("\
Enter your choice (1-6): ")
            
            # Process choice
            if choice == "1":
                self._cli_test_water()
            elif choice == "2":
                self._cli_view_tests()
            elif choice == "3":
                self._cli_calculate_chemicals()
            elif choice == "4":
                self._cli_check_weather()
            elif choice == "5":
                self._cli_view_safety()
            elif choice == "6":
                print("\
Exiting Deep Blue Pool Chemistry. Goodbye!")
                break
            else:
                print("\
Invalid choice. Please try again.")
    
    def _cli_test_water(self) -> None:
        """Test water chemistry in CLI mode."""
        print("\
Test Water Chemistry")
        print("===================")
        
        # Get test results
        print("\
Enter test results:")
        ph = input("pH: ")
        free_chlorine = input("Free Chlorine (ppm): ")
        total_chlorine = input("Total Chlorine (ppm): ")
        alkalinity = input("Alkalinity (ppm): ")
        calcium = input("Calcium Hardness (ppm): ")
        cyanuric_acid = input("Cyanuric Acid (ppm): ")
        temperature = input("Temperature (\u00b0F): ")
        
        # Create test data
        test_data = {
            "pH": ph,
            "free_chlorine": free_chlorine,
            "total_chlorine": total_chlorine,
            "alkalinity": alkalinity,
            "calcium": calcium,
            "cyanuric_acid": cyanuric_acid,
            "temperature": temperature,
            "source": "manual"
        }
        
        # Save test results
        self.db_service.insert_reading(test_data)
        
        print("\
Test results saved successfully.")
    
    def _cli_view_tests(self) -> None:
        """View recent tests in CLI mode."""
        print("\
Recent Tests")
        print("===========")
        
        # Get recent readings
        readings = self.db_service.get_recent_readings(5)
        
        if not readings:
            print("\
No test results found.")
            return
        
        # Print readings
        for reading in readings:
            print(f"\
Date: {reading.get('timestamp', 'Unknown')}")
            print(f"pH: {reading.get('ph', 'Unknown')}")
            print(f"Free Chlorine: {reading.get('free_chlorine', 'Unknown')} ppm")
            print(f"Total Chlorine: {reading.get('total_chlorine', 'Unknown')} ppm")
            print(f"Alkalinity: {reading.get('alkalinity', 'Unknown')} ppm")
            print(f"Calcium Hardness: {reading.get('calcium', 'Unknown')} ppm")
            print(f"Cyanuric Acid: {reading.get('cyanuric_acid', 'Unknown')} ppm")
            print(f"Temperature: {reading.get('temperature', 'Unknown')}\u00b0F")
    
    def _cli_calculate_chemicals(self) -> None:
        """Calculate chemical adjustments in CLI mode."""
        print("\
Calculate Chemical Adjustments")
        print("============================")
        
        # Get pool information
        print("\
Enter pool information:")
        pool_type = input("Pool Type (Concrete/Gunite, Vinyl, Fiberglass): ")
        pool_size = input("Pool Size (gallons): ")
        
        # Get test results
        print("\
Enter test results:")
        ph = input("pH: ")
        free_chlorine = input("Free Chlorine (ppm): ")
        alkalinity = input("Alkalinity (ppm): ")
        calcium = input("Calcium Hardness (ppm): ")
        temperature = input("Temperature (\u00b0F): ")
        
        # Create pool data
        pool_data = {
            "pool_type": pool_type,
            "pool_size": pool_size,
            "ph": ph,
            "chlorine": free_chlorine,
            "alkalinity": alkalinity,
            "calcium_hardness": calcium,
            "temperature": temperature
        }
        
        # Calculate chemicals
        result = self.controller.calculate_chemicals(pool_data)
        
        # Print results
        print("\
Recommended Adjustments:")
        
        if "adjustments" in result:
            adjustments = result["adjustments"]
            
            if "ph_increaser" in adjustments:
                print(f"pH Increaser: {adjustments['ph_increaser']} oz")
            
            if "ph_decreaser" in adjustments:
                print(f"pH Decreaser: {adjustments['ph_decreaser']} oz")
            
            if "alkalinity_increaser" in adjustments:
                print(f"Alkalinity Increaser: {adjustments['alkalinity_increaser']} oz")
            
            if "calcium_increaser" in adjustments:
                print(f"Calcium Increaser: {adjustments['calcium_increaser']} oz")
            
            if "chlorine" in adjustments:
                print(f"Chlorine: {adjustments['chlorine']} oz")
        
        if "water_balance" in result:
            print(f"\
Water Balance Index: {result['water_balance']:.2f}")
            
            if result["water_balance"] < -0.5:
                print("Water is corrosive.")
            elif result["water_balance"] > 0.5:
                print("Water is scale-forming.")
            else:
                print("Water is balanced.")
    
    def _cli_check_weather(self) -> None:
        """Check weather impact in CLI mode."""
        print("\
Weather Impact")
        print("=============")
        
        # Get weather data
        weather_data = self.weather_service.get_weather()
        
        # Print weather data
        print(f"\
Current Weather:")
        print(f"Location: {self.config['weather']['location']}")
        print(f"Temperature: {weather_data.get('temperature', 'Unknown')}\u00b0F")
        print(f"Humidity: {weather_data.get('humidity', 'Unknown')}%")
        print(f"Conditions: {weather_data.get('conditions', 'Unknown')}")
        
        # Get forecast
        forecast = self.weather_service.get_forecast(3)
        
        # Print forecast
        print("\
3-Day Forecast:")
        for i, day in enumerate(forecast):
            print(f"Day {i+1}: {day.get('temperature', 'Unknown')}\u00b0F, {day.get('conditions', 'Unknown')}")
        
        # Get weather impact
        impact = self.weather_service.analyze_weather_impact(weather_data)
        
        # Print impact
        print("\
Impact on Pool Chemistry:")
        print(f"\u2022 Evaporation Rate: {impact.get('evaporation_rate', 'Unknown')} inches per day")
        print(f"\u2022 Chlorine Loss Rate: {impact.get('chlorine_loss_rate', 'Unknown')}% per day")
        
        if weather_data.get('temperature', 0) > 85:
            print("\u2022 Higher temperatures may increase chlorine consumption")
        
        if weather_data.get('conditions', '').lower() in ['sunny', 'clear']:
            print("\u2022 UV exposure will degrade chlorine faster")
        
        if weather_data.get('conditions', '').lower() in ['rain', 'showers', 'thunderstorm']:
            print("\u2022 Rain may dilute chemicals and affect water balance")
        else:
            print("\u2022 No rain expected, so no dilution of chemicals")
    
    def _cli_view_safety(self) -> None:
        """View chemical safety information in CLI mode."""
        print("\
Chemical Safety Information")
        print("=========================")
        
        # Get all chemicals
        chemicals = self.chemical_safety_db.get_all_chemicals()
        
        # Print chemical list
        print("\
Available Chemicals:")
        for i, chemical_id in enumerate(chemicals):
            chemical = self.chemical_safety_db.get_chemical_safety_info(chemical_id)
            print(f"{i+1}. {chemical['name']}")
        
        # Get user choice
        choice = input("\
Enter chemical number to view details (or 0 to return): ")
        
        try:
            choice_num = int(choice)
            if choice_num == 0:
                return
            
            if choice_num < 1 or choice_num > len(chemicals):
                print("\
Invalid choice.")
                return
            
            # Get chemical details
            chemical_id = list(chemicals.keys())[choice_num - 1]
            chemical = self.chemical_safety_db.get_chemical_safety_info(chemical_id)
            
            # Print chemical details
            print(f"\
Chemical: {chemical['name']}")
            print(f"Chemical Formula: {chemical['chemical_formula']}")
            print(f"Hazard Rating: {chemical['hazard_rating']}")
            
            print("\
Safety Precautions:")
            for precaution in chemical['safety_precautions']:
                print(f"\u2022 {precaution}")
            
            print(f"\
Storage Guidelines: {chemical['storage_guidelines']}")
            print(f"Emergency Procedures: {chemical['emergency_procedures']}")
            
            # Print compatibility
            print("\
Compatibility:")
            compatibility = self.chemical_safety_db.get_compatibility(chemical_id)
            
            print("Compatible with:")
            compatible = [chem for chem, compat in compatibility.items() if compat]
            for chem in compatible:
                chem_info = self.chemical_safety_db.get_chemical_safety_info(chem)
                print(f"\u2022 {chem_info['name']}")
            
            print("\
Incompatible with:")
            incompatible = [chem for chem, compat in compatibility.items() if not compat]
            for chem in incompatible:
                chem_info = self.chemical_safety_db.get_chemical_safety_info(chem)
                print(f"\u2022 {chem_info['name']}")
        
        except (ValueError, IndexError):
            print("\
Invalid choice.")
    
    def cleanup(self) -> None:
        """Clean up resources."""
        # Close database connections
        if hasattr(self, 'db_service'):
            self.db_service.close_all_connections()
        
        # Clear image cache
        if hasattr(self, 'test_strip_analyzer'):
            self.test_strip_analyzer.clear_cache()
        
        # Clear weather cache
        if hasattr(self, 'weather_service'):
            self.weather_service.clear_cache()
        
        logger.info("Application resources cleaned up")

if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Deep Blue Pool Chemistry Application")
    parser.add_argument("--config", default="config.json", help="Path to configuration file")
    parser.add_argument("--cli", action="store_true", help="Run in CLI mode")
    args = parser.parse_args()
    
    # Create and run application
    app = PoolChemistryApp(args.config)
    
    if args.cli:
        app.run_cli()
    else:
        app.run_gui()
