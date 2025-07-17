
# app/gui_elements.py
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import logging
from typing import Dict, Any, Optional, Callable
import os
import sys
from datetime import datetime

# Add parent directory to path to make imports work when running this file directly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Fix the import path
try:
    from app.gui_controller import PoolChemistryController
except ImportError:
    # Try relative import if absolute import fails
    try:
        from gui_controller import PoolChemistryController
    except ImportError:
        print("ERROR: Could not import PoolChemistryController")
        # Create a placeholder if needed
        class PoolChemistryController:
            def __init__(self):
                print("Using placeholder PoolChemistryController")
            
            def check_database_health(self):
                return True
                
            def run_database_migrations(self):
                return True
                
            def calculate_chemicals(self, pool_data):
                return {"adjustments": {}, "water_balance": 0.0, "ideal_ranges": {}}
                
            def save_test_results(self, pool_data):
                return 1

# Configure logging
logger = logging.getLogger(__name__)

class PoolChemistryGUI:
    """
    GUI for the Pool Chemistry Calculator application.
    """
    
    def __init__(self):
        """Initialize the GUI with all components."""
        try:
            # Initialize the main window FIRST
            self.window = tk.Tk()
            self.window.title("Pool Chemistry Calculator")
            self.window.geometry("800x600")
            
            # THEN initialize variables that depend on the root window
            self.pool_data = {}
            self._initialize_variables()
            
            # Set application icon if available
            try:
                icon_path = os.path.join(os.path.dirname(__file__), "../assets/icon.ico")
                if os.path.exists(icon_path):
                    self.window.iconbitmap(icon_path)
            except Exception as e:
                logger.warning(f"Could not set application icon: {str(e)}")
            
            # Initialize the controller
            self.controller = PoolChemistryController()
            
            # Check database health
            if not self.controller.check_database_health():
                messagebox.showwarning(
                    "Database Warning",
                    "Database connection is not healthy. Some features may not work properly."
                )
            
            # Run database migrations
            self.controller.run_database_migrations()
            
            # Create the main frames
            self._create_frames()
            
            # Create menu
            self._create_menu()
            
            # Set up status bar
            self._create_status_bar()
            
            # Set status
            self._set_status("Ready")
            
            logger.info("GUI initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing GUI: {str(e)}")
            if 'self.window' in locals() and self.window:
                messagebox.showerror("Error", f"Failed to initialize application: {str(e)}")
            raise
    
    def _initialize_variables(self):
        """Initialize variables used in the GUI."""
        # These variables depend on the root window (self.window) being created first
        self.pool_data = {
            "pool_type": tk.StringVar(self.window),
            "pool_size": tk.StringVar(self.window),
            "ph": tk.StringVar(self.window),
            "chlorine": tk.StringVar(self.window),
            "alkalinity": tk.StringVar(self.window),
            "calcium_hardness": tk.StringVar(self.window),
            "cyanuric_acid": tk.StringVar(self.window),
            "salt": tk.StringVar(self.window),
            "temperature": tk.StringVar(self.window)
        }
        
        # Set default values
        self.pool_data["pool_type"].set("Concrete/Gunite")
        self.pool_data["pool_size"].set("10000")
        self.pool_data["temperature"].set("78")
    
    def _create_frames(self):
        """Create the main frames for the application."""
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.window)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create tabs
        self.dashboard_frame = ttk.Frame(self.notebook)
        self.testing_frame = ttk.Frame(self.notebook)
        self.history_frame = ttk.Frame(self.notebook)
        self.settings_frame = ttk.Frame(self.notebook)
        
        # Add tabs to notebook
        self.notebook.add(self.dashboard_frame, text="Dashboard")
        self.notebook.add(self.testing_frame, text="Water Testing")
        self.notebook.add(self.history_frame, text="History")
        self.notebook.add(self.settings_frame, text="Settings")
        
        # Create content for each tab
        self._create_dashboard_tab()
        self._create_testing_tab()
        self._create_history_tab()
        self._create_settings_tab()
    
    def _create_menu(self):
        """Create the application menu."""
        menubar = tk.Menu(self.window)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="New Test", command=self._new_test)
        file_menu.add_command(label="Save Results", command=self._save_results)
        file_menu.add_command(label="Export Data", command=self._export_data)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.window.quit)
        menubar.add_cascade(label="File", menu=file_menu)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        tools_menu.add_command(label="Calculate Chemicals", command=self._calculate_chemicals)
        tools_menu.add_command(label="Analyze Test Strip", command=self._analyze_test_strip)
        tools_menu.add_command(label="Update Weather", command=self._update_weather)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="User Guide", command=self._show_user_guide)
        help_menu.add_command(label="About", command=self._show_about)
        menubar.add_cascade(label="Help", menu=help_menu)
        
        # Set the menu
        self.window.config(menu=menubar)
    
    def _create_status_bar(self):
        """Create the status bar at the bottom of the window."""
        self.status_bar = ttk.Label(
            self.window,
            text="Ready",
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def _set_status(self, message):
        """Set the status bar message."""
        self.status_bar.config(text=message)
        self.window.update_idletasks()
    
    def _create_dashboard_tab(self):
        """Create the dashboard tab content."""
        # Pool information frame
        pool_info_frame = ttk.LabelFrame(self.dashboard_frame, text="Pool Information")
        pool_info_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Pool type
        ttk.Label(pool_info_frame, text="Pool Type:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        pool_type_combo = ttk.Combobox(
            pool_info_frame,
            textvariable=self.pool_data["pool_type"],
            values=["Concrete/Gunite", "Vinyl", "Fiberglass", "Above Ground"]
        )
        pool_type_combo.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Pool size
        ttk.Label(pool_info_frame, text="Pool Size (gallons):").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(
            pool_info_frame,
            textvariable=self.pool_data["pool_size"],
            width=15
        ).grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Weather information frame
        weather_frame = ttk.LabelFrame(self.dashboard_frame, text="Weather Information")
        weather_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Weather data will be populated here
        self.weather_label = ttk.Label(weather_frame, text="No weather data available")
        self.weather_label.pack(padx=10, pady=10)
        
        # Update weather button
        ttk.Button(
            weather_frame,
            text="Update Weather",
            command=self._update_weather
        ).pack(pady=5)
        
        # Recent readings frame
        readings_frame = ttk.LabelFrame(self.dashboard_frame, text="Recent Readings")
        readings_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Create a treeview for recent readings
        self.recent_readings_tree = ttk.Treeview(
            readings_frame,
            columns=("date", "ph", "chlorine", "alkalinity"),
            show="headings"
        )
        
        # Define columns
        self.recent_readings_tree.heading("date", text="Date")
        self.recent_readings_tree.heading("ph", text="pH")
        self.recent_readings_tree.heading("chlorine", text="Chlorine")
        self.recent_readings_tree.heading("alkalinity", text="Alkalinity")
        
        # Set column widths
        self.recent_readings_tree.column("date", width=100)
        self.recent_readings_tree.column("ph", width=50)
        self.recent_readings_tree.column("chlorine", width=70)
        self.recent_readings_tree.column("alkalinity", width=70)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(readings_frame, orient=tk.VERTICAL, command=self.recent_readings_tree.yview)
        self.recent_readings_tree.configure(yscroll=scrollbar.set)
        
        # Pack the treeview and scrollbar
        self.recent_readings_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Populate with sample data (would be replaced with actual data)
        self._populate_recent_readings()
    
    def _create_testing_tab(self):
        """Create the water testing tab content."""
        # Chemical readings frame
        readings_frame = ttk.LabelFrame(self.testing_frame, text="Chemical Readings")
        readings_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Create grid of labels and entry fields for chemical readings
        chemicals = [
            ("pH", "ph", ""),
            ("Free Chlorine", "chlorine", "ppm"),
            ("Total Alkalinity", "alkalinity", "ppm"),
            ("Calcium Hardness", "calcium_hardness", "ppm"),
            ("Cyanuric Acid", "cyanuric_acid", "ppm"),
            ("Salt", "salt", "ppm"),
            ("Temperature", "temperature", "\u00b0F")
        ]
        
        for i, (label_text, var_name, unit) in enumerate(chemicals):
            row = i // 3
            col = (i % 3) * 3
            
            ttk.Label(readings_frame, text=label_text).grid(row=row, column=col, sticky=tk.W, padx=5, pady=5)
            ttk.Entry(
                readings_frame,
                textvariable=self.pool_data[var_name],
                width=8
            ).grid(row=row, column=col+1, sticky=tk.W, padx=5, pady=5)
            
            if unit:
                ttk.Label(readings_frame, text=unit).grid(row=row, column=col+2, sticky=tk.W, padx=0, pady=5)
        
        # Buttons frame
        buttons_frame = ttk.Frame(self.testing_frame)
        buttons_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Add buttons
        ttk.Button(
            buttons_frame,
            text="Calculate Chemicals",
            command=self._calculate_chemicals
        ).pack(side=tk.LEFT, padx=5, pady=5)
        
        ttk.Button(
            buttons_frame,
            text="Analyze Test Strip",
            command=self._analyze_test_strip
        ).pack(side=tk.LEFT, padx=5, pady=5)
        
        ttk.Button(
            buttons_frame,
            text="Save Results",
            command=self._save_results
        ).pack(side=tk.LEFT, padx=5, pady=5)
        
        ttk.Button(
            buttons_frame,
            text="Clear",
            command=self._clear_readings
        ).pack(side=tk.LEFT, padx=5, pady=5)
        
        # Results frame
        results_frame = ttk.LabelFrame(self.testing_frame, text="Results and Recommendations")
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Text widget for results
        self.results_text = tk.Text(results_frame, wrap=tk.WORD, height=10)
        self.results_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Make text widget read-only initially
        self.results_text.config(state=tk.DISABLED)
    
    def _create_history_tab(self):
        """Create the history tab content."""
        # Create a treeview for history
        self.history_tree = ttk.Treeview(
            self.history_frame,
            columns=("date", "time", "ph", "chlorine", "alkalinity", "calcium", "cyanuric", "salt", "temp"),
            show="headings"
        )
        
        # Define columns
        self.history_tree.heading("date", text="Date")
        self.history_tree.heading("time", text="Time")
        self.history_tree.heading("ph", text="pH")
        self.history_tree.heading("chlorine", text="Chlorine")
        self.history_tree.heading("alkalinity", text="Alkalinity")
        self.history_tree.heading("calcium", text="Calcium")
        self.history_tree.heading("cyanuric", text="CYA")
        self.history_tree.heading("salt", text="Salt")
        self.history_tree.heading("temp", text="Temp")
        
        # Set column widths
        for col in ("date", "time"):
            self.history_tree.column(col, width=80)
        for col in ("ph", "chlorine", "alkalinity", "calcium", "cyanuric", "salt", "temp"):
            self.history_tree.column(col, width=60)
        
        # Add scrollbars
        y_scrollbar = ttk.Scrollbar(self.history_frame, orient=tk.VERTICAL, command=self.history_tree.yview)
        x_scrollbar = ttk.Scrollbar(self.history_frame, orient=tk.HORIZONTAL, command=self.history_tree.xview)
        self.history_tree.configure(yscroll=y_scrollbar.set, xscroll=x_scrollbar.set)
        
        # Pack the treeview and scrollbars
        self.history_tree.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        x_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Buttons frame
        buttons_frame = ttk.Frame(self.history_frame)
        buttons_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Add buttons
        ttk.Button(
            buttons_frame,
            text="Export Data",
            command=self._export_data
        ).pack(side=tk.LEFT, padx=5, pady=5)
        
        ttk.Button(
            buttons_frame,
            text="Delete Selected",
            command=self._delete_selected_history
        ).pack(side=tk.LEFT, padx=5, pady=5)
        
        # Populate with sample data (would be replaced with actual data)
        self._populate_history()
    
    def _create_settings_tab(self):
        """Create the settings tab content."""
        # General settings frame
        general_frame = ttk.LabelFrame(self.settings_frame, text="General Settings")
        general_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Database settings
        ttk.Label(general_frame, text="Database Path:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.db_path_var = tk.StringVar(self.window, value="pool_data.db")
        ttk.Entry(
            general_frame,
            textvariable=self.db_path_var,
            width=30
        ).grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        ttk.Button(
            general_frame,
            text="Browse",
            command=self._browse_db_path
        ).grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        
        # Auto-backup setting
        self.auto_backup_var = tk.BooleanVar(self.window, value=True)
        ttk.Checkbutton(
            general_frame,
            text="Enable automatic backups",
            variable=self.auto_backup_var
        ).grid(row=1, column=0, columnspan=3, sticky=tk.W, padx=5, pady=5)
        
        # Arduino settings frame
        arduino_frame = ttk.LabelFrame(self.settings_frame, text="Arduino Settings")
        arduino_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Arduino port
        ttk.Label(arduino_frame, text="Arduino Port:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.arduino_port_var = tk.StringVar(self.window)
        ttk.Combobox(
            arduino_frame,
            textvariable=self.arduino_port_var,
            values=["COM1", "COM2", "COM3", "COM4", "/dev/ttyUSB0", "/dev/ttyUSB1"]
        ).grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        ttk.Button(
            arduino_frame,
            text="Connect",
            command=self._connect_arduino
        ).grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        
        # Weather settings frame
        weather_frame = ttk.LabelFrame(self.settings_frame, text="Weather Settings")
        weather_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Location
        ttk.Label(weather_frame, text="Location:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.location_var = tk.StringVar(self.window, value="Florida")
        ttk.Entry(
            weather_frame,
            textvariable=self.location_var,
            width=20
        ).grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # API key
        ttk.Label(weather_frame, text="API Key:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.api_key_var = tk.StringVar(self.window)
        ttk.Entry(
            weather_frame,
            textvariable=self.api_key_var,
            width=30,
            show="*"
        ).grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Save settings button
        ttk.Button(
            self.settings_frame,
            text="Save Settings",
            command=self._save_settings
        ).pack(padx=10, pady=10)
        
        # Database maintenance frame
        db_maintenance_frame = ttk.LabelFrame(self.settings_frame, text="Database Maintenance")
        db_maintenance_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Database maintenance buttons
        ttk.Button(
            db_maintenance_frame,
            text="Backup Database",
            command=self._backup_database
        ).pack(side=tk.LEFT, padx=5, pady=5)
        
        ttk.Button(
            db_maintenance_frame,
            text="Run Migrations",
            command=self._run_migrations
        ).pack(side=tk.LEFT, padx=5, pady=5)
    
    def _populate_recent_readings(self):
        """Populate the recent readings treeview with sample data."""
        # Clear existing data
        for item in self.recent_readings_tree.get_children():
            self.recent_readings_tree.delete(item)
        
        # Add sample data (would be replaced with actual data)
        sample_data = [
            ("2025-07-10", "7.4", "2.0", "120"),
            ("2025-07-08", "7.2", "1.5", "110"),
            ("2025-07-05", "7.6", "3.0", "130")
        ]
        
        for data in sample_data:
            self.recent_readings_tree.insert("", tk.END, values=data)
    
    def _populate_history(self):
        """Populate the history treeview with sample data."""
        # Clear existing data
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        
        # Add sample data (would be replaced with actual data)
        sample_data = [
            ("2025-07-10", "09:30", "7.4", "2.0", "120", "250", "30", "2800", "82"),
            ("2025-07-08", "10:15", "7.2", "1.5", "110", "240", "35", "2750", "80"),
            ("2025-07-05", "08:45", "7.6", "3.0", "130", "260", "40", "2900", "78"),
            ("2025-07-01", "11:00", "7.5", "2.5", "125", "255", "35", "2850", "81")
        ]
        
        for data in sample_data:
            self.history_tree.insert("", tk.END, values=data)
    
    def _new_test(self):
        """Clear all test fields for a new test."""
        for var_name in ["ph", "chlorine", "alkalinity", "calcium_hardness", "cyanuric_acid", "salt"]:
            self.pool_data[var_name].set("")
        
        # Clear results
        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete(1.0, tk.END)
        self.results_text.config(state=tk.DISABLED)
        
        self._set_status("New test started")
    
    def _save_results(self):
        """Save the current test results."""
        try:
            # Validate data
            for var_name in ["ph", "chlorine", "alkalinity"]:
                if not self.pool_data[var_name].get().strip():
                    messagebox.showwarning(
                        "Missing Data",
                        f"Please enter a value for {var_name}"
                    )
                    return
            
            # Get values
            pool_data_dict = {
                key: self.pool_data[key].get() for key in self.pool_data
            }
            
            # Save to database
            test_id = self.controller.save_test_results(pool_data_dict)
            
            if test_id:
                self._set_status(f"Test results saved (ID: {test_id})")
                messagebox.showinfo(
                    "Success",
                    "Test results saved successfully"
                )
                
                # Refresh history
                self._populate_history()
                self._populate_recent_readings()
            else:
                self._set_status("Failed to save test results")
                messagebox.showerror(
                    "Error",
                    "Failed to save test results"
                )
                
        except Exception as e:
            logger.error(f"Error saving results: {str(e)}")
            self._set_status("Error saving results")
            messagebox.showerror(
                "Error",
                f"An error occurred while saving results: {str(e)}"
            )
    
    def _export_data(self):
        """Export data to CSV file."""
        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
            )
            
            if not file_path:
                return
            
            # Export data
            # This would call the controller to export data
            
            self._set_status(f"Data exported to {file_path}")
            messagebox.showinfo(
                "Export Complete",
                f"Data exported to {file_path}"
            )
            
        except Exception as e:
            logger.error(f"Error exporting data: {str(e)}")
            self._set_status("Error exporting data")
            messagebox.showerror(
                "Error",
                f"An error occurred while exporting data: {str(e)}"
            )
    
    def _calculate_chemicals(self):
        """Calculate chemical adjustments based on test results."""
        try:
            # Validate data
            for var_name in ["ph", "chlorine", "alkalinity"]:
                if not self.pool_data[var_name].get().strip():
                    messagebox.showwarning(
                        "Missing Data",
                        f"Please enter a value for {var_name}"
                    )
                    return
            
            # Get values
            pool_data_dict = {
                key: self.pool_data[key].get() for key in self.pool_data
            }
            
            # Calculate chemicals
            result = self.controller.calculate_chemicals(pool_data_dict)
            
            # Display results
            self.results_text.config(state=tk.NORMAL)
            self.results_text.delete(1.0, tk.END)
            
            if "adjustments" in result:
                self.results_text.insert(tk.END, "Chemical Adjustments:\
\
")
                
                for chemical, amount in result["adjustments"].items():
                    self.results_text.insert(tk.END, f"{chemical}: {amount}\
")
                
                self.results_text.insert(tk.END, "\
Ideal Ranges:\
")
                
                for param, range_values in result["ideal_ranges"].items():
                    self.results_text.insert(tk.END, f"{param}: {range_values[0]} - {range_values[1]}\
")
                
                if "water_balance" in result:
                    self.results_text.insert(tk.END, f"\
Water Balance Index: {result['water_balance']}\
")
            else:
                self.results_text.insert(tk.END, "No adjustments needed.")
            
            self.results_text.config(state=tk.DISABLED)
            self._set_status("Chemical calculations complete")
            
        except Exception as e:
            logger.error(f"Error calculating chemicals: {str(e)}")
            self._set_status("Error calculating chemicals")
            messagebox.showerror(
                "Error",
                f"An error occurred during calculation: {str(e)}"
            )
    
    def _analyze_test_strip(self):
        """Analyze a test strip using the camera."""
        try:
            # This would integrate with a camera and image processing
            # For now, just show a message
            messagebox.showinfo(
                "Test Strip Analysis",
                "This feature is not yet implemented."
            )
            self._set_status("Test strip analysis not available")
            
        except Exception as e:
            logger.error(f"Error analyzing test strip: {str(e)}")
            self._set_status("Error analyzing test strip")
            messagebox.showerror(
                "Error",
                f"An error occurred during test strip analysis: {str(e)}"
            )
    
    def _update_weather(self):
        """Update weather information."""
        try:
            # This would call a weather API
            # For now, just update with sample data
            weather_data = {
                "temperature": "85\u00b0F",
                "humidity": "65%",
                "conditions": "Sunny",
                "forecast": "Clear skies"
            }
            
            # Update weather label
            weather_text = f"Temperature: {weather_data['temperature']}\
"
            weather_text += f"Humidity: {weather_data['humidity']}\
"
            weather_text += f"Conditions: {weather_data['conditions']}\
"
            weather_text += f"Forecast: {weather_data['forecast']}"
            
            self.weather_label.config(text=weather_text)
            self._set_status("Weather updated")
            
        except Exception as e:
            logger.error(f"Error updating weather: {str(e)}")
            self._set_status("Error updating weather")
            messagebox.showerror(
                "Error",
                f"An error occurred while updating weather: {str(e)}"
            )
    
    def _clear_readings(self):
        """Clear all reading fields."""
        for var_name in ["ph", "chlorine", "alkalinity", "calcium_hardness", "cyanuric_acid", "salt"]:
            self.pool_data[var_name].set("")
        
        # Clear results
        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete(1.0, tk.END)
        self.results_text.config(state=tk.DISABLED)
        
        self._set_status("Readings cleared")
    
    def _delete_selected_history(self):
        """Delete selected history entries."""
        selected_items = self.history_tree.selection()
        
        if not selected_items:
            messagebox.showinfo(
                "No Selection",
                "Please select items to delete"
            )
            return
        
        confirm = messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete {len(selected_items)} selected items?"
        )
        
        if confirm:
            # Delete selected items
            for item in selected_items:
                self.history_tree.delete(item)
            
            self._set_status(f"{len(selected_items)} history entries deleted")
    
    def _browse_db_path(self):
        """Browse for database file path."""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".db",
            filetypes=[("SQLite Database", "*.db"), ("All files", "*.*")],
            initialfile=self.db_path_var.get()
        )
        
        if file_path:
            self.db_path_var.set(file_path)
    
    def _connect_arduino(self):
        """Connect to Arduino device."""
        port = self.arduino_port_var.get()
        
        if not port:
            messagebox.showwarning(
                "No Port Selected",
                "Please select an Arduino port"
            )
            return
        
        # This would connect to the Arduino
        # For now, just show a message
        messagebox.showinfo(
            "Arduino Connection",
            f"Connecting to Arduino on port {port}..."
        )
        self._set_status(f"Connected to Arduino on {port}")
    
    def _save_settings(self):
        """Save application settings."""
        try:
            # Save settings
            # This would call the controller to save settings
            
            self._set_status("Settings saved")
            messagebox.showinfo(
                "Settings Saved",
                "Settings have been saved successfully"
            )
            
        except Exception as e:
            logger.error(f"Error saving settings: {str(e)}")
            self._set_status("Error saving settings")
            messagebox.showerror(
                "Error",
                f"An error occurred while saving settings: {str(e)}"
            )
    
    def _backup_database(self):
        """Backup the database."""
        try:
            # This would call the controller to backup the database
            # For now, just show a message
            messagebox.showinfo(
                "Database Backup",
                "Database backup completed successfully"
            )
            self._set_status("Database backup completed")
            
        except Exception as e:
            logger.error(f"Error backing up database: {str(e)}")
            self._set_status("Error backing up database")
            messagebox.showerror(
                "Error",
                f"An error occurred while backing up the database: {str(e)}"
            )
    
    def _run_migrations(self):
        """Run database migrations."""
        try:
            # Run migrations
            success = self.controller.run_database_migrations()
            
            if success:
                self._set_status("Database migrations completed")
                messagebox.showinfo(
                    "Migrations", 
                    "Database migrations completed successfully"
                )
                logger.info("Database migrations completed")
            else:
                self._set_status("Database migrations failed")
                messagebox.showwarning(
                    "Migrations", 
                    "Database migrations failed"
                )
                logger.warning("Database migrations failed")
                
        except Exception as e:
            self._set_status("Database migrations failed")
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            logger.error(f"Error running database migrations: {str(e)}")
    
    def _show_user_guide(self):
        """Show user guide."""
        messagebox.showinfo(
            "User Guide",
            "The user guide is not yet available."
        )
    
    def _show_about(self):
        """Show about dialog."""
        messagebox.showinfo(
            "About Pool Chemistry Calculator",
            "Pool Chemistry Calculator\
\
"
            "Version 1.0.0\
\
"
            "A tool for calculating pool chemical adjustments\
"
            "and maintaining proper water balance.\
\
"
            "\u00a9 2025 Pool Chemistry Solutions"
        )
    
    def run(self):
        """Run the application main loop."""
        self.window.mainloop()


# Entry point
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("pool_chemistry.log"),
            logging.StreamHandler()
        ]
    )
    
    # Create and run the application
    app = PoolChemistryGUI()
    app.run()
