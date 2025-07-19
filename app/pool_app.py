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

# Import updated modules
from services.database_service import DatabaseService
from chemical_safety_database import ChemicalSafetyDatabase
from test_strip_analyzer import TestStripAnalyzer
from weather_service import WeatherService
from gui_controller import PoolChemistryController
from customer_management_integration import integrate_customer_management

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
        
        # Arduino connection
        self.arduino_serial = None
        self.arduino_thread = None
        self.arduino_running = False
        self.arduino_data = {
            "ph": [],
            "orp": [],
            "temperature": [],
            "tds": []
        }
        self.arduino_timestamps = []
    
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
                },
                "arduino": {
                    "baud_rate": 9600,
                    "timeout": 1.0,
                    "update_interval": 2.0
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
            root.geometry("1200x800")
            
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
            
            # Create dashboard content
            dashboard_content = ttk.Frame(dashboard_frame)
            dashboard_content.pack(fill=tk.BOTH, expand=True, pady=20)
            
            # Left column - Quick actions
            left_column = ttk.LabelFrame(dashboard_content, text="Quick Actions")
            left_column.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
            
            ttk.Button(left_column, text="Customer Management", 
                      command=lambda: notebook.select(1)).pack(pady=5, fill=tk.X)
            
            ttk.Button(left_column, text="Test Strip Analysis", 
                      command=lambda: notebook.select(2)).pack(pady=5, fill=tk.X)
            
            ttk.Button(left_column, text="Chemical Calculator", 
                      command=lambda: notebook.select(3)).pack(pady=5, fill=tk.X)
            
            ttk.Button(left_column, text="Arduino Sensors", 
                      command=lambda: notebook.select(4)).pack(pady=5, fill=tk.X)
            
            ttk.Button(left_column, text="Weather Impact", 
                      command=lambda: notebook.select(5)).pack(pady=5, fill=tk.X)
            
            # Right column - Recent activity and weather
            right_column = ttk.Frame(dashboard_content)
            right_column.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10)
            
            # Recent activity
            activity_frame = ttk.LabelFrame(right_column, text="Recent Activity")
            activity_frame.pack(fill=tk.BOTH, expand=True, pady=5)
            
            # Get recent readings
            try:
                readings = self.db_service.get_recent_readings(5)
                
                if readings:
                    for reading in readings:
                        timestamp = reading.get('timestamp', 'Unknown')
                        ph = reading.get('ph', 'N/A')
                        chlorine = reading.get('free_chlorine', 'N/A')
                        
                        if 'customer_id' in reading and reading['customer_id']:
                            try:
                                customer = self.db_service.get_customer(reading['customer_id'])
                                customer_name = f"{customer.get('first_name', '')} {customer.get('last_name', '')}"
                            except:
                                customer_name = f"Customer #{reading['customer_id']}"
                            
                            ttk.Label(activity_frame, text=f"{timestamp} - {customer_name} - pH: {ph}, Chlorine: {chlorine} ppm").pack(anchor=tk.W, pady=2)
                        else:
                            ttk.Label(activity_frame, text=f"{timestamp} - pH: {ph}, Chlorine: {chlorine} ppm").pack(anchor=tk.W, pady=2)
                else:
                    ttk.Label(activity_frame, text="No recent activity").pack(anchor=tk.W, pady=10)
            except Exception as e:
                logger.error(f"Error getting recent activity: {e}")
                ttk.Label(activity_frame, text=f"Error getting recent activity: {e}").pack(anchor=tk.W, pady=10)
            
            # Weather summary
            weather_frame = ttk.LabelFrame(right_column, text="Weather Summary")
            weather_frame.pack(fill=tk.BOTH, expand=True, pady=5)
            
            try:
                weather_data = self.weather_service.get_weather()
                
                ttk.Label(weather_frame, text=f"Location: {self.config['weather']['location']}").pack(anchor=tk.W, pady=2)
                ttk.Label(weather_frame, text=f"Temperature: {weather_data.get('temperature', 'Unknown')}\u00b0F").pack(anchor=tk.W, pady=2)
                ttk.Label(weather_frame, text=f"Conditions: {weather_data.get('conditions', 'Unknown')}").pack(anchor=tk.W, pady=2)
                
                # Get weather impact
                impact = self.weather_service.analyze_weather_impact(weather_data)
                
                ttk.Label(weather_frame, text=f"Chlorine Loss Rate: {impact.get('chlorine_loss_rate', 'Unknown')}% per day").pack(anchor=tk.W, pady=2)
                
                if weather_data.get('temperature', 0) > 85:
                    ttk.Label(weather_frame, text="Warning: High temperature may increase chlorine consumption").pack(anchor=tk.W, pady=2)
            except Exception as e:
                logger.error(f"Error getting weather summary: {e}")
                ttk.Label(weather_frame, text=f"Error getting weather summary: {e}").pack(anchor=tk.W, pady=10)
            
            # Create Customer Management tab
            customer_frame = ttk.Frame(notebook, padding=10)
            notebook.add(customer_frame, text="Customer Management")
            self._create_customer_management_tab(customer_frame)
            
            # Create Test Strip Analysis tab
            test_strip_frame = ttk.Frame(notebook, padding=10)
            notebook.add(test_strip_frame, text="Test Strip Analysis")
            self._create_test_strip_tab(test_strip_frame)
            
            # Create Chemical Calculator tab
            calculator_frame = ttk.Frame(notebook, padding=10)
            notebook.add(calculator_frame, text="Chemical Calculator")
            self._create_chemical_calculator_tab(calculator_frame)
            
            # Create Arduino Sensors tab
            arduino_frame = ttk.Frame(notebook, padding=10)
            notebook.add(arduino_frame, text="Arduino Sensors")
            self._create_arduino_tab(arduino_frame)
            
            # Create Weather Impact tab
            weather_frame = ttk.Frame(notebook, padding=10)
            notebook.add(weather_frame, text="Weather Impact")
            self._create_weather_tab(weather_frame)
            
            # Create exit button at the bottom
            exit_frame = ttk.Frame(root)
            exit_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=10, pady=10)
            ttk.Button(exit_frame, text="Exit", command=lambda: self._exit_application(root)).pack(side=tk.RIGHT)
            
            # Set up protocol for window close
            root.protocol("WM_DELETE_WINDOW", lambda: self._exit_application(root))
            
            # Start the main loop
            root.mainloop()
            
        except Exception as e:
            logger.error(f"Error in GUI application: {e}")
            import traceback
            logger.error(traceback.format_exc())
            raise RuntimeError(f"GUI application failed: {e}")
    
    def _exit_application(self, root: tk.Tk) -> None:
        """
        Exit the application cleanly.
        
        Args:
            root: Root window
        """
        # Stop Arduino monitoring if running
        if self.arduino_running:
            self.arduino_running = False
            if self.arduino_thread:
                self.arduino_thread.join(timeout=1.0)
            
            if self.arduino_serial:
                try:
                    self.arduino_serial.close()
                except:
                    pass
        
        # Clean up resources
        self.cleanup()
        
        # Destroy the root window
        root.destroy()
    
    def _create_customer_management_tab(self, parent: ttk.Frame) -> None:
        """
        Create the customer management tab.
        
        Args:
            parent: Parent frame
        """
        # Create notebook for sub-tabs
        notebook = ttk.Notebook(parent)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create Add Customer tab
        add_customer_frame = ttk.Frame(notebook, padding=20)
        notebook.add(add_customer_frame, text="Add Customer")
        
        # Create View Customers tab
        view_customers_frame = ttk.Frame(notebook, padding=20)
        notebook.add(view_customers_frame, text="View Customers")
        
        # Add Customer Form
        customer_form_frame = ttk.LabelFrame(add_customer_frame, text="Customer Information")
        customer_form_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Customer form fields
        ttk.Label(customer_form_frame, text="First Name:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        first_name_var = tk.StringVar()
        first_name_entry = ttk.Entry(customer_form_frame, textvariable=first_name_var, width=30)
        first_name_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        
        ttk.Label(customer_form_frame, text="Last Name:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        last_name_var = tk.StringVar()
        last_name_entry = ttk.Entry(customer_form_frame, textvariable=last_name_var, width=30)
        last_name_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        
        ttk.Label(customer_form_frame, text="Address:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        address_var = tk.StringVar()
        address_entry = ttk.Entry(customer_form_frame, textvariable=address_var, width=50)
        address_entry.grid(row=2, column=1, columnspan=3, padx=5, pady=5, sticky=tk.W)
        
        ttk.Label(customer_form_frame, text="City:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        city_var = tk.StringVar()
        city_entry = ttk.Entry(customer_form_frame, textvariable=city_var, width=30)
        city_entry.grid(row=3, column=1, padx=5, pady=5, sticky=tk.W)
        
        ttk.Label(customer_form_frame, text="State:").grid(row=3, column=2, padx=5, pady=5, sticky=tk.W)
        state_var = tk.StringVar()
        state_entry = ttk.Entry(customer_form_frame, textvariable=state_var, width=5)
        state_entry.grid(row=3, column=3, padx=5, pady=5, sticky=tk.W)
        
        ttk.Label(customer_form_frame, text="ZIP:").grid(row=3, column=4, padx=5, pady=5, sticky=tk.W)
        zip_var = tk.StringVar()
        zip_entry = ttk.Entry(customer_form_frame, textvariable=zip_var, width=10)
        zip_entry.grid(row=3, column=5, padx=5, pady=5, sticky=tk.W)
        
        ttk.Label(customer_form_frame, text="Phone:").grid(row=4, column=0, padx=5, pady=5, sticky=tk.W)
        phone_var = tk.StringVar()
        phone_entry = ttk.Entry(customer_form_frame, textvariable=phone_var, width=20)
        phone_entry.grid(row=4, column=1, padx=5, pady=5, sticky=tk.W)
        
        ttk.Label(customer_form_frame, text="Email:").grid(row=5, column=0, padx=5, pady=5, sticky=tk.W)
        email_var = tk.StringVar()
        email_entry = ttk.Entry(customer_form_frame, textvariable=email_var, width=40)
        email_entry.grid(row=5, column=1, columnspan=2, padx=5, pady=5, sticky=tk.W)
        
        # Pool Information
        pool_info_frame = ttk.LabelFrame(add_customer_frame, text="Pool Information")
        pool_info_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        ttk.Label(pool_info_frame, text="Pool Type:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        pool_type_var = tk.StringVar(value="Concrete/Gunite")
        pool_type_combo = ttk.Combobox(pool_info_frame, textvariable=pool_type_var, values=["Concrete/Gunite", "Vinyl", "Fiberglass"])
        pool_type_combo.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        
        ttk.Label(pool_info_frame, text="Pool Size (gallons):").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        pool_size_var = tk.StringVar(value=self.config["pool"]["size"])
        pool_size_entry = ttk.Entry(pool_info_frame, textvariable=pool_size_var)
        pool_size_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        
        ttk.Label(pool_info_frame, text="Service Day:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        service_day_var = tk.StringVar(value="Monday")
        service_day_combo = ttk.Combobox(pool_info_frame, textvariable=service_day_var, 
                                         values=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"])
        service_day_combo.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)
        
        ttk.Label(pool_info_frame, text="Notes:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.NW)
        notes_text = tk.Text(pool_info_frame, width=50, height=5)
        notes_text.grid(row=3, column=1, columnspan=3, padx=5, pady=5, sticky=tk.W)
        
        # Add buttons
        buttons_frame = ttk.Frame(add_customer_frame)
        buttons_frame.pack(fill=tk.X, pady=10)
        
        def save_customer():
            # Get customer data
            customer_data = {
                "first_name": first_name_var.get(),
                "last_name": last_name_var.get(),
                "address": address_var.get(),
                "city": city_var.get(),
                "state": state_var.get(),
                "zip": zip_var.get(),
                "phone": phone_var.get(),
                "email": email_var.get(),
                "pool_type": pool_type_var.get(),
                "pool_size": pool_size_var.get(),
                "service_day": service_day_var.get(),
                "notes": notes_text.get("1.0", tk.END).strip()
            }
            
            # Validate data
            if not customer_data["first_name"] or not customer_data["last_name"]:
                messagebox.showerror("Validation Error", "First name and last name are required.")
                return
            
            try:
                # Save customer data
                customer_id = self.db_service.insert_customer(customer_data)
                
                if customer_id:
                    messagebox.showinfo("Success", f"Customer {customer_data['first_name']} {customer_data['last_name']} added successfully with ID: {customer_id}")
                    
                    # Clear form
                    first_name_var.set("")
                    last_name_var.set("")
                    address_var.set("")
                    city_var.set("")
                    state_var.set("")
                    zip_var.set("")
                    phone_var.set("")
                    email_var.set("")
                    pool_type_var.set("Concrete/Gunite")
                    pool_size_var.set(self.config["pool"]["size"])
                    service_day_var.set("Monday")
                    notes_text.delete("1.0", tk.END)
                    
                    # Refresh customer list
                    refresh_customers()
                else:
                    messagebox.showerror("Error", "Failed to add customer.")
            except Exception as e:
                logger.error(f"Error saving customer: {e}")
                messagebox.showerror("Error", f"Failed to save customer: {e}")
        
        ttk.Button(buttons_frame, text="Save Customer", command=save_customer).pack(side=tk.RIGHT, padx=5)
        ttk.Button(buttons_frame, text="Clear Form", command=lambda: [
            first_name_var.set(""),
            last_name_var.set(""),
            address_var.set(""),
            city_var.set(""),
            state_var.set(""),
            zip_var.set(""),
            phone_var.set(""),
            email_var.set(""),
            pool_type_var.set("Concrete/Gunite"),
            pool_size_var.set(self.config["pool"]["size"]),
            service_day_var.set("Monday"),
            notes_text.delete("1.0", tk.END)
        ]).pack(side=tk.RIGHT, padx=5)
        
        # View Customers Tab
        # Create treeview for customers
        columns = ("id", "name", "phone", "email", "service_day")
        customer_tree = ttk.Treeview(view_customers_frame, columns=columns, show="headings")
        customer_tree.heading("id", text="ID")
        customer_tree.heading("name", text="Name")
        customer_tree.heading("phone", text="Phone")
        customer_tree.heading("email", text="Email")
        customer_tree.heading("service_day", text="Service Day")
        
        customer_tree.column("id", width=50)
        customer_tree.column("name", width=200)
        customer_tree.column("phone", width=150)
        customer_tree.column("email", width=200)
        customer_tree.column("service_day", width=100)
        
        customer_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(view_customers_frame, orient=tk.VERTICAL, command=customer_tree.yview)
        customer_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Function to refresh customer list
        def refresh_customers():
            # Clear existing items
            for item in customer_tree.get_children():
                customer_tree.delete(item)
            
            try:
                # Get customers from database
                customers = self.db_service.get_all_customers()
                
                # Add customers to treeview
                for customer in customers:
                    customer_tree.insert("", tk.END, values=(
                        customer.get("id", ""),
                        f"{customer.get('first_name', '')} {customer.get('last_name', '')}",
                        customer.get("phone", ""),
                        customer.get("email", ""),
                        customer.get("service_day", "")
                    ))
            except Exception as e:
                logger.error(f"Error refreshing customers: {e}")
                messagebox.showerror("Error", f"Failed to refresh customers: {e}")
        
        # Function to view customer details
        def view_customer_details():
            selected_items = customer_tree.selection()
            if not selected_items:
                messagebox.showinfo("Information", "Please select a customer to view.")
                return
            
            # Get selected customer ID
            customer_id = customer_tree.item(selected_items[0], "values")[0]
            
            try:
                # Get customer details
                customer = self.db_service.get_customer(customer_id)
                
                if customer:
                    # Create customer details dialog
                    details_dialog = tk.Toplevel(parent)
                    details_dialog.title(f"Customer Details: {customer.get('first_name', '')} {customer.get('last_name', '')}")
                    details_dialog.geometry("600x500")
                    details_dialog.transient(parent.winfo_toplevel())
                    details_dialog.grab_set()
                    
                    # Create frame
                    details_frame = ttk.Frame(details_dialog, padding=20)
                    details_frame.pack(fill=tk.BOTH, expand=True)
                    
                    # Add customer details
                    ttk.Label(details_frame, text=f"Customer Details: {customer.get('first_name', '')} {customer.get('last_name', '')}", 
                             font=("Arial", 16)).pack(pady=10)
                    
                    # Customer information
                    info_frame = ttk.LabelFrame(details_frame, text="Customer Information")
                    info_frame.pack(fill=tk.X, padx=10, pady=5)
                    
                    ttk.Label(info_frame, text=f"Name: {customer.get('first_name', '')} {customer.get('last_name', '')}").pack(anchor=tk.W, padx=5, pady=2)
                    ttk.Label(info_frame, text=f"Address: {customer.get('address', '')}, {customer.get('city', '')}, {customer.get('state', '')} {customer.get('zip', '')}").pack(anchor=tk.W, padx=5, pady=2)
                    ttk.Label(info_frame, text=f"Phone: {customer.get('phone', '')}").pack(anchor=tk.W, padx=5, pady=2)
                    ttk.Label(info_frame, text=f"Email: {customer.get('email', '')}").pack(anchor=tk.W, padx=5, pady=2)
                    
                    # Pool information
                    pool_frame = ttk.LabelFrame(details_frame, text="Pool Information")
                    pool_frame.pack(fill=tk.X, padx=10, pady=5)
                    
                    ttk.Label(pool_frame, text=f"Pool Type: {customer.get('pool_type', '')}").pack(anchor=tk.W, padx=5, pady=2)
                    ttk.Label(pool_frame, text=f"Pool Size: {customer.get('pool_size', '')} gallons").pack(anchor=tk.W, padx=5, pady=2)
                    ttk.Label(pool_frame, text=f"Service Day: {customer.get('service_day', '')}").pack(anchor=tk.W, padx=5, pady=2)
                    
                    # Notes
                    notes_frame = ttk.LabelFrame(details_frame, text="Notes")
                    notes_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
                    
                    notes_text = tk.Text(notes_frame, width=50, height=5, wrap=tk.WORD)
                    notes_text.insert(tk.END, customer.get("notes", ""))
                    notes_text.config(state=tk.DISABLED)
                    notes_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
                    
                    # Add close button
                    ttk.Button(details_frame, text="Close", command=details_dialog.destroy).pack(pady=10)
                else:
                    messagebox.showerror("Error", f"Customer with ID {customer_id} not found.")
            except Exception as e:
                logger.error(f"Error viewing customer details: {e}")
                messagebox.showerror("Error", f"Failed to view customer details: {e}")
        
        # Add buttons for customer management
        buttons_frame = ttk.Frame(view_customers_frame)
        buttons_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(buttons_frame, text="Refresh", command=refresh_customers).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="View Details", command=view_customer_details).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Edit Customer", command=lambda: messagebox.showinfo("Info", "Edit functionality not implemented yet.")).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Delete Customer", command=lambda: messagebox.showinfo("Info", "Delete functionality not implemented yet.")).pack(side=tk.LEFT, padx=5)
        
        # Load initial customer data
        refresh_customers()
    
    def _create_test_strip_tab(self, parent: ttk.Frame) -> None:
        """
        Create the test strip analysis tab.
        
        Args:
            parent: Parent frame
        """
        # Create main frame
        main_frame = ttk.Frame(parent)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Add title
        title = ttk.Label(main_frame, text="Test Strip Analysis", font=("Arial", 18))
        title.pack(pady=10)
        
        # Add instructions
        instructions = ttk.Label(main_frame, text="Capture or load an image of your test strip to analyze it.")
        instructions.pack(pady=5)
        
        # Create content frame
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Left side - Image and controls
        left_frame = ttk.Frame(content_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
        
        # Add image frame
        image_frame = ttk.LabelFrame(left_frame, text="Test Strip Image")
        image_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Add image label
        image_label = ttk.Label(image_frame, text="No image loaded")
        image_label.pack(fill=tk.BOTH, expand=True, padx=50, pady=50)
        
        # Add buttons frame
        buttons_frame = ttk.Frame(left_frame)
        buttons_frame.pack(fill=tk.X, pady=10)
        
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
        
        # Right side - Results
        right_frame = ttk.Frame(content_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10)
        
        # Add results frame
        results_frame = ttk.LabelFrame(right_frame, text="Analysis Results")
        results_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Add results text
        results_text = scrolledtext.ScrolledText(results_frame, width=40, height=15)
        results_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        results_text.insert(tk.END, "No analysis performed yet.")
        results_text.config(state=tk.DISABLED)
        
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
                    # Enable text widget for editing
                    results_text.config(state=tk.NORMAL)
                    results_text.delete(1.0, tk.END)
                    
                    # Add results
                    results_text.insert(tk.END, "Analysis Results:\n\n")
                    
                    for param, value in results.items():
                        param_name = param.replace("_", " ").title()
                        results_text.insert(tk.END, f"{param_name}: {value}\n")
                    
                    # Add recommendations
                    recommendations = self.test_strip_analyzer.get_recommendations(results)
                    
                    if recommendations:
                        results_text.insert(tk.END, "\nRecommendations:\n\n")
                        
                        for param, recommendation in recommendations.items():
                            param_name = param.replace("_", " ").title()
                            results_text.insert(tk.END, f"{param_name}: {recommendation}\n")
                    
                    # Disable text widget
                    results_text.config(state=tk.DISABLED)
                else:
                    messagebox.showerror("Error", "Analysis failed")
            except Exception as e:
                logger.error(f"Error analyzing image: {e}")
                messagebox.showerror("Error", f"Analysis failed: {e}")
        
        # Add buttons
        ttk.Button(buttons_frame, text="Capture Image", command=capture_image).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Load Image", command=load_image).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Analyze", command=analyze_image).pack(side=tk.LEFT, padx=5)
    
    def _create_chemical_calculator_tab(self, parent: ttk.Frame) -> None:
        """
        Create the chemical calculator tab.
        
        Args:
            parent: Parent frame
        """
        # Create main frame
        main_frame = ttk.Frame(parent)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Add title
        title = ttk.Label(main_frame, text="Chemical Calculator", font=("Arial", 18))
        title.pack(pady=10)
        
        # Add instructions
        instructions = ttk.Label(main_frame, text="Enter your pool information and test results to calculate chemical adjustments.")
        instructions.pack(pady=5)
        
        # Create content frame
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Left side - Input form
        left_frame = ttk.Frame(content_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
        
        # Add customer selection
        customer_frame = ttk.Frame(left_frame)
        customer_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(customer_frame, text="Customer:").pack(side=tk.LEFT, padx=5)
        
        # Get customers for dropdown
        try:
            customers = self.db_service.get_all_customers()
            customer_names = ["-- Select Customer --"] + [f"{c.get('first_name', '')} {c.get('last_name', '')} ({c.get('id', '')})" for c in customers]
            customer_ids = [""] + [c.get('id', '') for c in customers]
        except:
            customer_names = ["-- Select Customer --"]
            customer_ids = [""]
        
        customer_var = tk.StringVar(value=customer_names[0])
        customer_combo = ttk.Combobox(customer_frame, textvariable=customer_var, values=customer_names, width=40)
        customer_combo.pack(side=tk.LEFT, padx=5)
        
        # Add pool info frame
        pool_frame = ttk.LabelFrame(left_frame, text="Pool Information")
        pool_frame.pack(fill=tk.X, pady=5)
        
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
        test_frame = ttk.LabelFrame(left_frame, text="Test Results")
        test_frame.pack(fill=tk.X, pady=5)
        
        # Add test result fields
        ttk.Label(test_frame, text="pH:").grid(row=0, column=0, padx=5, pady=2, sticky=tk.W)
        ph_var = tk.StringVar(value="7.2")
        ph_entry = ttk.Entry(test_frame, textvariable=ph_var)
        ph_entry.grid(row=0, column=1, padx=5, pady=2, sticky=tk.W)
        
        ttk.Label(test_frame, text="Free Chlorine (ppm):").grid(row=0, column=2, padx=5, pady=2, sticky=tk.W)
        chlorine_var = tk.StringVar(value="1.5")
        chlorine_entry = ttk.Entry(test_frame, textvariable=chlorine_var)
        chlorine_entry.grid(row=0, column=3, padx=5, pady=2, sticky=tk.W)
        
        ttk.Label(test_frame, text="Total Chlorine (ppm):").grid(row=1, column=0, padx=5, pady=2, sticky=tk.W)
        total_chlorine_var = tk.StringVar(value="2.0")
        total_chlorine_entry = ttk.Entry(test_frame, textvariable=total_chlorine_var)
        total_chlorine_entry.grid(row=1, column=1, padx=5, pady=2, sticky=tk.W)
        
        ttk.Label(test_frame, text="Alkalinity (ppm):").grid(row=1, column=2, padx=5, pady=2, sticky=tk.W)
        alkalinity_var = tk.StringVar(value="100")
        alkalinity_entry = ttk.Entry(test_frame, textvariable=alkalinity_var)
        alkalinity_entry.grid(row=1, column=3, padx=5, pady=2, sticky=tk.W)
        
        ttk.Label(test_frame, text="Calcium Hardness (ppm):").grid(row=2, column=0, padx=5, pady=2, sticky=tk.W)
        calcium_var = tk.StringVar(value="250")
        calcium_entry = ttk.Entry(test_frame, textvariable=calcium_var)
        calcium_entry.grid(row=2, column=1, padx=5, pady=2, sticky=tk.W)
        
        ttk.Label(test_frame, text="Cyanuric Acid (ppm):").grid(row=2, column=2, padx=5, pady=2, sticky=tk.W)
        cyanuric_acid_var = tk.StringVar(value="30")
        cyanuric_acid_entry = ttk.Entry(test_frame, textvariable=cyanuric_acid_var)
        cyanuric_acid_entry.grid(row=2, column=3, padx=5, pady=2, sticky=tk.W)
        
        ttk.Label(test_frame, text="Salt (ppm):").grid(row=3, column=0, padx=5, pady=2, sticky=tk.W)
        salt_var = tk.StringVar(value="3000")
        salt_entry = ttk.Entry(test_frame, textvariable=salt_var)
        salt_entry.grid(row=3, column=1, padx=5, pady=2, sticky=tk.W)
        
        ttk.Label(test_frame, text="Temperature (\u00b0F):").grid(row=3, column=2, padx=5, pady=2, sticky=tk.W)
        temp_var = tk.StringVar(value="78")
        temp_entry = ttk.Entry(test_frame, textvariable=temp_var)
        temp_entry.grid(row=3, column=3, padx=5, pady=2, sticky=tk.W)
        
        # Function to load customer pool data
        def load_customer_data(*args):
            selected_index = customer_combo.current()
            if selected_index > 0:  # Skip the "Select Customer" option
                customer_id = customer_ids[selected_index]
                try:
                    customer = self.db_service.get_customer(customer_id)
                    if customer:
                        pool_type_var.set(customer.get('pool_type', 'Concrete/Gunite'))
                        pool_size_var.set(customer.get('pool_size', self.config["pool"]["size"]))
                except Exception as e:
                    logger.error(f"Error loading customer data: {e}")
        
        # Bind customer selection to load data
        customer_var.trace("w", load_customer_data)
        
        # Right side - Results and safety info
        right_frame = ttk.Frame(content_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10)
        
        # Create notebook for results tabs
        results_notebook = ttk.Notebook(right_frame)
        results_notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create tabs
        adjustments_frame = ttk.Frame(results_notebook)
        results_notebook.add(adjustments_frame, text="Adjustments")
        
        safety_frame = ttk.Frame(results_notebook)
        results_notebook.add(safety_frame, text="Safety Information")
        
        steps_frame = ttk.Frame(results_notebook)
        results_notebook.add(steps_frame, text="Treatment Steps")
        
        # Add results frame to adjustments tab
        results_frame = ttk.LabelFrame(adjustments_frame, text="Recommended Adjustments")
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Add result text
        results_text = scrolledtext.ScrolledText(results_frame, width=40, height=15)
        results_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        results_text.insert(tk.END, "No calculations performed yet.")
        results_text.config(state=tk.DISABLED)
        
        # Add safety info to safety tab
        safety_text = scrolledtext.ScrolledText(safety_frame, width=40, height=15)
        safety_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        safety_text.insert(tk.END, "Safety information will appear here after calculation.")
        safety_text.config(state=tk.DISABLED)
        
        # Add treatment steps to steps tab
        steps_text = scrolledtext.ScrolledText(steps_frame, width=40, height=15)
        steps_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        steps_text.insert(tk.END, "Treatment steps will appear here after calculation.")
        steps_text.config(state=tk.DISABLED)
        
        # Function to calculate chemicals
        def calculate():
            try:
                # Get values from fields
                pool_data = {
                    "pool_type": pool_type_var.get(),
                    "pool_size": pool_size_var.get(),
                    "ph": ph_var.get(),
                    "chlorine": chlorine_var.get(),
                    "total_chlorine": total_chlorine_var.get(),
                    "alkalinity": alkalinity_var.get(),
                    "calcium_hardness": calcium_var.get(),
                    "cyanuric_acid": cyanuric_acid_var.get(),
                    "salt": salt_var.get(),
                    "temperature": temp_var.get()
                }
                
                # Get customer ID if selected
                selected_index = customer_combo.current()
                if selected_index > 0:
                    pool_data["customer_id"] = customer_ids[selected_index]
                
                # Validate data
                errors = self.controller.validate_pool_data(pool_data)
                if errors:
                    error_message = "\n".join(errors)
                    messagebox.showerror("Validation Error", f"Please correct the following errors:\n\n{error_message}")
                    return
                
                # Calculate chemicals
                result = self.controller.calculate_chemicals(pool_data)
                
                # Update results tab
                results_text.config(state=tk.NORMAL)
                results_text.delete(1.0, tk.END)
                
                if "adjustments" in result:
                    adjustments = result["adjustments"]
                    
                    results_text.insert(tk.END, "Recommended Chemical Adjustments:\n\n")
                    
                    for chemical, amount in adjustments.items():
                        chemical_name = chemical.replace("_", " ").title()
                        results_text.insert(tk.END, f"{chemical_name}: {amount} oz\n")
                
                if "water_balance" in result:
                    balance = result["water_balance"]
                    results_text.insert(tk.END, f"\nWater Balance Index: {balance:.2f}\n")
                    
                    if balance < -0.5:
                        results_text.insert(tk.END, "Water is corrosive.\n")
                    elif balance > 0.5:
                        results_text.insert(tk.END, "Water is scale-forming.\n")
                    else:
                        results_text.insert(tk.END, "Water is balanced.\n")
                
                # Save test results
                test_id = self.controller.save_test_results(pool_data)
                if test_id:
                    results_text.insert(tk.END, f"\nTest results saved with ID: {test_id}\n")
                
                results_text.config(state=tk.DISABLED)
                
                # Update safety information tab
                safety_text.config(state=tk.NORMAL)
                safety_text.delete(1.0, tk.END)
                
                # Get chemicals used in adjustments
                chemicals_used = []
                if "adjustments" in result:
                    for chemical in result["adjustments"]:
                        if chemical == "ph_increaser":
                            chemicals_used.append("sodium_bicarbonate")
                        elif chemical == "ph_decreaser":
                            chemicals_used.append("muriatic_acid")
                        elif chemical == "alkalinity_increaser":
                            chemicals_used.append("sodium_bicarbonate")
                        elif chemical == "calcium_increaser":
                            chemicals_used.append("calcium_chloride")
                        elif chemical == "chlorine":
                            chemicals_used.append("chlorine")
                
                # Add safety information for each chemical
                safety_text.insert(tk.END, "CHEMICAL SAFETY INFORMATION\n\n")
                
                for chemical_id in chemicals_used:
                    try:
                        chemical_info = self.chemical_safety_db.get_chemical_safety_info(chemical_id)
                        
                        if chemical_info:
                            safety_text.insert(tk.END, f"--- {chemical_info.get('name', chemical_id)} ---\n\n")
                            safety_text.insert(tk.END, f"Hazard Rating: {chemical_info.get('hazard_rating', 'Unknown')}\n\n")
                            
                            safety_text.insert(tk.END, "Safety Precautions:\n")
                            if 'safety_precautions' in chemical_info and chemical_info['safety_precautions']:
                                for precaution in chemical_info['safety_precautions']:
                                    safety_text.insert(tk.END, f"• {precaution}\n")
                            else:
                                safety_text.insert(tk.END, "No safety precautions available\n")
                            
                            safety_text.insert(tk.END, f"\nStorage Guidelines: {chemical_info.get('storage_guidelines', 'No information available')}\n")
                            safety_text.insert(tk.END, f"\nEmergency Procedures: {chemical_info.get('emergency_procedures', 'No information available')}\n\n")
                            
                            # Add compatibility information
                            try:
                                compatibility = self.chemical_safety_db.get_compatibility(chemical_id)
                                
                                if compatibility:
                                    incompatible = [chem for chem, compat in compatibility.items() if not compat]
                                    
                                    if incompatible:
                                        safety_text.insert(tk.END, "WARNING - Incompatible with:\n")
                                        for chem in incompatible:
                                            chem_info = self.chemical_safety_db.get_chemical_safety_info(chem)
                                            chem_name = chem_info.get('name', chem)
                                            safety_text.insert(tk.END, f"• {chem_name}\n")
                                        safety_text.insert(tk.END, "\n")
                            except Exception as e:
                                logger.error(f"Error getting compatibility for {chemical_id}: {e}")
                    except Exception as e:
                        logger.error(f"Error getting safety info for {chemical_id}: {e}")
                
                safety_text.config(state=tk.DISABLED)
                
                # Update treatment steps tab
                steps_text.config(state=tk.NORMAL)
                steps_text.delete(1.0, tk.END)
                
                steps_text.insert(tk.END, "TREATMENT STEPS\n\n")
                steps_text.insert(tk.END, "Follow these steps in order to safely adjust your pool chemistry:\n\n")
                
                step_num = 1
                
                # Always adjust alkalinity first
                if "adjustments" in result and "alkalinity_increaser" in result["adjustments"]:
                    amount = result["adjustments"]["alkalinity_increaser"]
                    steps_text.insert(tk.END, f"{step_num}. Adjust Alkalinity:\n")
                    steps_text.insert(tk.END, f"   - Add {amount} oz of Alkalinity Increaser (Sodium Bicarbonate)\n")
                    steps_text.insert(tk.END, f"   - Broadcast over deep end of pool\n")
                    steps_text.insert(tk.END, f"   - Run circulation pump for at least 4 hours\n")
                    steps_text.insert(tk.END, f"   - Wait 24 hours before making other adjustments\n\n")
                    step_num += 1
                
                # Then adjust pH
                if "adjustments" in result:
                    if "ph_increaser" in result["adjustments"]:
                        amount = result["adjustments"]["ph_increaser"]
                        steps_text.insert(tk.END, f"{step_num}. Increase pH:\n")
                        steps_text.insert(tk.END, f"   - Add {amount} oz of pH Increaser (Sodium Carbonate)\n")
                        steps_text.insert(tk.END, f"   - Broadcast over deep end of pool\n")
                        steps_text.insert(tk.END, f"   - Run circulation pump for at least 4 hours\n")
                        steps_text.insert(tk.END, f"   - Wait 6 hours before making other adjustments\n\n")
                        step_num += 1
                    elif "ph_decreaser" in result["adjustments"]:
                        amount = result["adjustments"]["ph_decreaser"]
                        steps_text.insert(tk.END, f"{step_num}. Decrease pH:\n")
                        steps_text.insert(tk.END, f"   - CAUTION: Always add acid to water, never water to acid\n")
                        steps_text.insert(tk.END, f"   - Add {amount} oz of pH Decreaser (Muriatic Acid)\n")
                        steps_text.insert(tk.END, f"   - Pour slowly around the perimeter of the pool\n")
                        steps_text.insert(tk.END, f"   - Run circulation pump for at least 4 hours\n")
                        steps_text.insert(tk.END, f"   - Wait 6 hours before making other adjustments\n\n")
                        step_num += 1
                
                # Then adjust calcium hardness
                if "adjustments" in result and "calcium_increaser" in result["adjustments"]:
                    amount = result["adjustments"]["calcium_increaser"]
                    steps_text.insert(tk.END, f"{step_num}. Adjust Calcium Hardness:\n")
                    steps_text.insert(tk.END, f"   - Add {amount} oz of Calcium Hardness Increaser (Calcium Chloride)\n")
                    steps_text.insert(tk.END, f"   - Dissolve in a bucket of water before adding to pool\n")
                    steps_text.insert(tk.END, f"   - Pour solution around the perimeter of the pool\n")
                    steps_text.insert(tk.END, f"   - Run circulation pump for at least 4 hours\n\n")
                    step_num += 1
                
                # Then adjust cyanuric acid
                if "adjustments" in result and "cyanuric_acid" in result["adjustments"]:
                    amount = result["adjustments"]["cyanuric_acid"]
                    steps_text.insert(tk.END, f"{step_num}. Adjust Cyanuric Acid (Stabilizer):\n")
                    steps_text.insert(tk.END, f"   - Add {amount} oz of Cyanuric Acid\n")
                    steps_text.insert(tk.END, f"   - Pre-dissolve in warm water (dissolves slowly)\n")
                    steps_text.insert(tk.END, f"   - Pour solution around the perimeter of the pool\n")
                    steps_text.insert(tk.END, f"   - Run circulation pump for at least 24 hours\n\n")
                    step_num += 1
                
                # Then adjust salt
                if "adjustments" in result and "salt" in result["adjustments"]:
                    amount = result["adjustments"]["salt"]
                    steps_text.insert(tk.END, f"{step_num}. Adjust Salt Level:\n")
                    steps_text.insert(tk.END, f"   - Add {amount} oz of Pool Salt\n")
                    steps_text.insert(tk.END, f"   - Broadcast over shallow end of pool\n")
                    steps_text.insert(tk.END, f"   - Brush to help dissolve\n")
                    steps_text.insert(tk.END, f"   - Run circulation pump for at least 24 hours\n\n")
                    step_num += 1
                
                # Finally adjust chlorine
                if "adjustments" in result and "chlorine" in result["adjustments"]:
                    amount = result["adjustments"]["chlorine"]
                    steps_text.insert(tk.END, f"{step_num}. Adjust Chlorine Level:\n")
                    steps_text.insert(tk.END, f"   - Add {amount} oz of Chlorine\n")
                    steps_text.insert(tk.END, f"   - Add during evening hours to prevent UV degradation\n")
                    steps_text.insert(tk.END, f"   - Pour around the perimeter of the pool\n")
                    steps_text.insert(tk.END, f"   - Run circulation pump for at least 1 hour\n\n")
                    step_num += 1
                
                steps_text.insert(tk.END, "IMPORTANT NOTES:\n")
                steps_text.insert(tk.END, "• Always wear appropriate safety gear when handling chemicals\n")
                steps_text.insert(tk.END, "• Never mix chemicals together\n")
                steps_text.insert(tk.END, "• Store chemicals in a cool, dry place away from direct sunlight\n")
                steps_text.insert(tk.END, "• Keep chemicals out of reach of children\n")
                steps_text.insert(tk.END, "• Retest water after each adjustment\n")
                
                steps_text.config(state=tk.DISABLED)
                
                # Switch to the adjustments tab
                results_notebook.select(0)
                
            except Exception as e:
                logger.error(f"Error calculating chemicals: {e}")
                messagebox.showerror("Error", f"Calculation failed: {e}")
        
        # Add calculate button
        ttk.Button(left_frame, text="Calculate", command=calculate).pack(pady=10)
    
    def _create_arduino_tab(self, parent: ttk.Frame) -> None:
        """
        Create the Arduino sensors tab.
        
        Args:
            parent: Parent frame
        """
        # Create main frame
        main_frame = ttk.Frame(parent)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Add title
        title = ttk.Label(main_frame, text="Arduino Sensor Monitor", font=("Arial", 18))
        title.pack(pady=10)
        
        # Create content frame
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Left side - Connection and controls
        left_frame = ttk.Frame(content_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
        
        # Add connection frame
        connection_frame = ttk.LabelFrame(left_frame, text="Connection")
        connection_frame.pack(fill=tk.X, pady=5)
        
        # Add status message
        self.status_var = tk.StringVar(value="Arduino Monitor is not connected")
        status_label = ttk.Label(connection_frame, textvariable=self.status_var, font=("Arial", 12))
        status_label.pack(pady=5)
        
        # Add port selection
        port_frame = ttk.Frame(connection_frame)
        port_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(port_frame, text="Port:").pack(side=tk.LEFT, padx=5)
        self.port_var = tk.StringVar()
        self.port_combo = ttk.Combobox(port_frame, textvariable=self.port_var)
        self.port_combo.pack(side=tk.LEFT, padx=5)
        
        # Add refresh button
        ttk.Button(port_frame, text="Refresh Ports", command=self._refresh_arduino_ports).pack(side=tk.LEFT, padx=5)
        
        # Add connect button
        self.connect_button = ttk.Button(port_frame, text="Connect", command=self._connect_arduino)
        self.connect_button.pack(side=tk.LEFT, padx=5)
        
        # Add sensor data frame
        sensor_frame = ttk.LabelFrame(left_frame, text="Current Sensor Data")
        sensor_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Add sensor data display
        self.sensor_tree = ttk.Treeview(sensor_frame, columns=("value", "unit", "timestamp"), show="headings")
        self.sensor_tree.heading("value", text="Value")
        self.sensor_tree.heading("unit", text="Unit")
        self.sensor_tree.heading("timestamp", text="Timestamp")
        self.sensor_tree.column("value", width=100)
        self.sensor_tree.column("unit", width=100)
        self.sensor_tree.column("timestamp", width=200)
        self.sensor_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Add sensor items
        self.sensor_tree.insert("", tk.END, iid="ph", text="pH", values=("N/A", "pH", "N/A"))
        self.sensor_tree.insert("", tk.END, iid="orp", text="ORP", values=("N/A", "mV", "N/A"))
        self.sensor_tree.insert("", tk.END, iid="temperature", text="Temperature", values=("N/A", "°F", "N/A"))
        self.sensor_tree.insert("", tk.END, iid="tds", text="TDS", values=("N/A", "ppm", "N/A"))
        
        # Right side - Chart
        right_frame = ttk.Frame(content_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10)
        
        # Add chart frame
        chart_frame = ttk.LabelFrame(right_frame, text="Sensor Chart")
        chart_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Create figure and canvas
        self.fig = Figure(figsize=(5, 4), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=chart_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Initialize chart
        self._initialize_arduino_chart()
        
        # Add control frame
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=10)
        
        # Add start/stop button
        self.start_stop_var = tk.StringVar(value="Start Monitoring")
        self.start_stop_button = ttk.Button(control_frame, textvariable=self.start_stop_var, command=self._toggle_arduino_monitoring)
        self.start_stop_button.pack(side=tk.LEFT, padx=5)
        
        # Add export button
        ttk.Button(control_frame, text="Export Data", command=self._export_arduino_data).pack(side=tk.LEFT, padx=5)
        
        # Add clear button
        ttk.Button(control_frame, text="Clear Data", command=self._clear_arduino_data).pack(side=tk.LEFT, padx=5)
        
        # Refresh ports
        self._refresh_arduino_ports()
    
    def _refresh_arduino_ports(self) -> None:
        """Refresh available serial ports."""
        try:
            # Get list of available ports
            ports = []
            try:
                import serial.tools.list_ports
                ports = [port.device for port in serial.tools.list_ports.comports()]
            except:
                # Fallback to common port names
                ports = ["COM1", "COM2", "COM3", "COM4", "COM5", 
                         "/dev/ttyUSB0", "/dev/ttyUSB1", "/dev/ttyACM0", "/dev/ttyACM1"]
            
            self.port_combo["values"] = ports
            if ports:
                self.port_combo.current(0)
            logger.info(f"Found {len(ports)} serial ports")
        except Exception as e:
            logger.error(f"Error refreshing ports: {e}")
            messagebox.showerror("Error", f"Failed to refresh ports: {e}")
    
    def _connect_arduino(self) -> None:
        """Connect to the selected serial port."""
        port = self.port_var.get()
        if not port:
            messagebox.showerror("Error", "No port selected")
            return
        
        try:
            # If already connected, disconnect first
            if self.arduino_serial:
                self._disconnect_arduino()
            
            # Connect to the port
            import serial
            self.arduino_serial = serial.Serial(
                port=port,
                baudrate=self.config.get("arduino", {}).get("baud_rate", 9600),
                timeout=self.config.get("arduino", {}).get("timeout", 1.0)
            )
            
            # Update status
            self.status_var.set(f"Connected to {port}")
            self.connect_button.config(text="Disconnect", command=self._disconnect_arduino)
            logger.info(f"Connected to Arduino on {port}")
            messagebox.showinfo("Connected", f"Successfully connected to Arduino on {port}")
        except Exception as e:
            logger.error(f"Error connecting to Arduino on {port}: {e}")
            messagebox.showerror("Error", f"Failed to connect to Arduino: {e}")
    
    def _disconnect_arduino(self) -> None:
        """Disconnect from the serial port."""
        try:
            # Stop monitoring if running
            if self.arduino_running:
                self._toggle_arduino_monitoring()
            
            # Close the serial connection
            if self.arduino_serial:
                self.arduino_serial.close()
                self.arduino_serial = None
            
            # Update status
            self.status_var.set("Arduino Monitor is not connected")
            self.connect_button.config(text="Connect", command=self._connect_arduino)
            logger.info("Disconnected from Arduino")
        except Exception as e:
            logger.error(f"Error disconnecting from Arduino: {e}")
            messagebox.showerror("Error", f"Failed to disconnect from Arduino: {e}")
    
    def _initialize_arduino_chart(self) -> None:
        """Initialize the Arduino chart."""
        self.ax.clear()
        self.ax.set_title("Sensor Data")
        self.ax.set_xlabel("Time")
        self.ax.set_ylabel("Value")
        self.ax.grid(True)
        self.fig.tight_layout()
        self.canvas.draw()
    
    def _update_arduino_chart(self) -> None:
        """Update the Arduino chart with new data."""
        try:
            self.ax.clear()
            
            # Plot data if available
            if self.arduino_timestamps:
                # Convert timestamps to datetime objects
                times = [datetime.fromisoformat(ts) for ts in self.arduino_timestamps]
                
                # Plot each sensor
                if self.arduino_data["ph"]:
                    self.ax.plot(times, self.arduino_data["ph"], label="pH", marker="o")
                
                if self.arduino_data["temperature"]:
                    self.ax.plot(times, self.arduino_data["temperature"], label="Temperature", marker="s")
                
                if self.arduino_data["orp"]:
                    self.ax.plot(times, self.arduino_data["orp"], label="ORP", marker="^")
                
                if self.arduino_data["tds"]:
                    self.ax.plot(times, self.arduino_data["tds"], label="TDS", marker="x")
                
                # Format x-axis
                self.ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S"))
                plt.setp(self.ax.xaxis.get_majorticklabels(), rotation=45)
                
                # Add legend
                self.ax.legend()
            
            self.ax.set_title("Sensor Data")
            self.ax.set_xlabel("Time")
            self.ax.set_ylabel("Value")
            self.ax.grid(True)
            self.fig.tight_layout()
            self.canvas.draw()
        except Exception as e:
            logger.error(f"Error updating Arduino chart: {e}")
    
    def _toggle_arduino_monitoring(self) -> None:
        """Toggle Arduino sensor monitoring."""
        if not self.arduino_running:
            # Check if connected
            if not self.arduino_serial:
                messagebox.showerror("Error", "Not connected to Arduino")
                return
            
            # Start monitoring
            self.arduino_running = True
            self.start_stop_var.set("Stop Monitoring")
            self.arduino_thread = threading.Thread(target=self._monitor_arduino_sensors)
            self.arduino_thread.daemon = True
            self.arduino_thread.start()
            logger.info("Started Arduino monitoring")
        else:
            # Stop monitoring
            self.arduino_running = False
            self.start_stop_var.set("Start Monitoring")
            logger.info("Stopped Arduino monitoring")
    
    def _monitor_arduino_sensors(self) -> None:
        """Monitor Arduino sensors in a separate thread."""
        while self.arduino_running:
            try:
                # In a real implementation, we would read actual data from the Arduino
                # For now, we'll generate random data for demonstration
                
                # Generate timestamp
                timestamp = datetime.now().isoformat()
                
                # Generate random data
                ph = round(np.random.uniform(6.5, 8.0), 1)
                orp = round(np.random.uniform(650, 750))
                temperature = round(np.random.uniform(75, 85), 1)
                tds = round(np.random.uniform(300, 500))
                
                # Update data
                self.arduino_data["ph"].append(ph)
                self.arduino_data["orp"].append(orp)
                self.arduino_data["temperature"].append(temperature)
                self.arduino_data["tds"].append(tds)
                self.arduino_timestamps.append(timestamp)
                
                # Keep only the last 20 data points
                if len(self.arduino_timestamps) > 20:
                    self.arduino_data["ph"] = self.arduino_data["ph"][-20:]
                    self.arduino_data["orp"] = self.arduino_data["orp"][-20:]
                    self.arduino_data["temperature"] = self.arduino_data["temperature"][-20:]
                    self.arduino_data["tds"] = self.arduino_data["tds"][-20:]
                    self.arduino_timestamps = self.arduino_timestamps[-20:]
                
                # Update UI in the main thread
                # We need to use after() to schedule UI updates from a non-main thread
                if hasattr(self, 'sensor_tree') and hasattr(self, 'ax'):
                    # Get the root window
                    root = self.sensor_tree.winfo_toplevel()
                    if root:
                        root.after(0, self._update_arduino_ui, ph, orp, temperature, tds, timestamp)
                
                # Sleep for a bit
                time.sleep(self.config.get("arduino", {}).get("update_interval", 2.0))
            except Exception as e:
                logger.error(f"Error monitoring Arduino sensors: {e}")
                self.arduino_running = False
                break
    
    def _update_arduino_ui(self, ph: float, orp: int, temperature: float, tds: int, timestamp: str) -> None:
        """
        Update the Arduino UI with new sensor data.
        
        Args:
            ph: pH value
            orp: ORP value
            temperature: Temperature value
            tds: TDS value
            timestamp: Timestamp
        """
        try:
            # Update tree view
            self.sensor_tree.item("ph", values=(ph, "pH", timestamp))
            self.sensor_tree.item("orp", values=(orp, "mV", timestamp))
            self.sensor_tree.item("temperature", values=(temperature, "°F", timestamp))
            self.sensor_tree.item("tds", values=(tds, "ppm", timestamp))
            
            # Update chart
            self._update_arduino_chart()
        except Exception as e:
            logger.error(f"Error updating Arduino UI: {e}")
    
    def _export_arduino_data(self) -> None:
        """Export Arduino sensor data to a CSV file."""
        try:
            if not self.arduino_timestamps:
                messagebox.showinfo("Export", "No data to export")
                return
            
            # Ask for file location
            file_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                title="Export Sensor Data"
            )
            
            if not file_path:
                return
            
            # Write data to file
            with open(file_path, "w") as f:
                # Write header
                f.write("Timestamp,pH,ORP (mV),Temperature (°F),TDS (ppm)\n")
                
                # Write data
                for i in range(len(self.arduino_timestamps)):
                    f.write(f"{self.arduino_timestamps[i]},{self.arduino_data['ph'][i]},{self.arduino_data['orp'][i]},{self.arduino_data['temperature'][i]},{self.arduino_data['tds'][i]}\n")
            
            logger.info(f"Exported Arduino data to {file_path}")
            messagebox.showinfo("Export", f"Data exported to {file_path}")
        except Exception as e:
            logger.error(f"Error exporting Arduino data: {e}")
            messagebox.showerror("Error", f"Failed to export data: {e}")
    
    def _clear_arduino_data(self) -> None:
        """Clear all Arduino sensor data."""
        try:
            # Clear data
            self.arduino_data = {
                "ph": [],
                "orp": [],
                "temperature": [],
                "tds": []
            }
            self.arduino_timestamps = []
            
            # Update tree view
            self.sensor_tree.item("ph", values=("N/A", "pH", "N/A"))
            self.sensor_tree.item("orp", values=("N/A", "mV", "N/A"))
            self.sensor_tree.item("temperature", values=("N/A", "°F", "N/A"))
            self.sensor_tree.item("tds", values=("N/A", "ppm", "N/A"))
            
            # Update chart
            self._initialize_arduino_chart()
            
            logger.info("Cleared all Arduino data")
        except Exception as e:
            logger.error(f"Error clearing Arduino data: {e}")
            messagebox.showerror("Error", f"Failed to clear data: {e}")
    
    def _create_weather_tab(self, parent: ttk.Frame) -> None:
        """
        Create the weather impact tab.
        
        Args:
            parent: Parent frame
        """
        # Create main frame
        main_frame = ttk.Frame(parent)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Add title
        title = ttk.Label(main_frame, text="Weather Impact", font=("Arial", 18))
        title.pack(pady=10)
        
        # Create content frame
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        try:
            # Get weather data
            weather_data = self.weather_service.get_weather()
            
            # Left side - Current weather and forecast
            left_frame = ttk.Frame(content_frame)
            left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
            
            # Add current weather frame
            current_frame = ttk.LabelFrame(left_frame, text="Current Weather")
            current_frame.pack(fill=tk.X, pady=5)
            
            # Add current weather info
            ttk.Label(current_frame, text=f"Location: {self.config['weather']['location']}").grid(row=0, column=0, padx=5, pady=2, sticky=tk.W)
            ttk.Label(current_frame, text=f"Temperature: {weather_data.get('temperature', 'Unknown')}\u00b0F").grid(row=0, column=1, padx=5, pady=2, sticky=tk.W)
            ttk.Label(current_frame, text=f"Humidity: {weather_data.get('humidity', 'Unknown')}%").grid(row=1, column=0, padx=5, pady=2, sticky=tk.W)
            ttk.Label(current_frame, text=f"Conditions: {weather_data.get('conditions', 'Unknown')}").grid(row=1, column=1, padx=5, pady=2, sticky=tk.W)
            
            # Get forecast
            forecast = self.weather_service.get_forecast(3)
            
            # Add forecast frame
            forecast_frame = ttk.LabelFrame(left_frame, text="3-Day Forecast")
            forecast_frame.pack(fill=tk.X, pady=5)
            
            # Add forecast info
            for i, day in enumerate(forecast):
                ttk.Label(forecast_frame, text=f"Day {i+1}: {day.get('temperature', 'Unknown')}\u00b0F, {day.get('conditions', 'Unknown')}").pack(anchor=tk.W, padx=5, pady=2)
            
            # Right side - Impact on pool chemistry
            right_frame = ttk.Frame(content_frame)
            right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10)
            
            # Get weather impact
            impact = self.weather_service.analyze_weather_impact(weather_data)
            
            # Add impact frame
            impact_frame = ttk.LabelFrame(right_frame, text="Impact on Pool Chemistry")
            impact_frame.pack(fill=tk.BOTH, expand=True, pady=5)
            
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
            
            # Add recommendations frame
            recommendations_frame = ttk.LabelFrame(right_frame, text="Recommendations")
            recommendations_frame.pack(fill=tk.BOTH, expand=True, pady=5)
            
            # Add recommendations based on weather
            if weather_data.get('temperature', 0) > 85:
                ttk.Label(recommendations_frame, text="\u2022 Check chlorine levels more frequently").pack(anchor=tk.W, padx=5, pady=2)
                ttk.Label(recommendations_frame, text="\u2022 Consider adding additional chlorine in the evening").pack(anchor=tk.W, padx=5, pady=2)
            
            if weather_data.get('conditions', '').lower() in ['sunny', 'clear']:
                ttk.Label(recommendations_frame, text="\u2022 Ensure proper cyanuric acid levels to protect chlorine").pack(anchor=tk.W, padx=5, pady=2)
                ttk.Label(recommendations_frame, text="\u2022 Add chlorine in the evening to minimize UV degradation").pack(anchor=tk.W, padx=5, pady=2)
            
            if weather_data.get('conditions', '').lower() in ['rain', 'showers', 'thunderstorm']:
                ttk.Label(recommendations_frame, text="\u2022 Test water after rain to check for dilution").pack(anchor=tk.W, padx=5, pady=2)
                ttk.Label(recommendations_frame, text="\u2022 Check pH and alkalinity as rain can affect these levels").pack(anchor=tk.W, padx=5, pady=2)
            
            if impact.get('evaporation_rate', 0) > 0.25:
                ttk.Label(recommendations_frame, text="\u2022 Monitor water level and top up as needed").pack(anchor=tk.W, padx=5, pady=2)
                ttk.Label(recommendations_frame, text="\u2022 Check calcium hardness as evaporation can increase levels").pack(anchor=tk.W, padx=5, pady=2)
            
            # Add refresh button
            ttk.Button(main_frame, text="Refresh Weather Data", command=lambda: self._refresh_weather_data(parent)).pack(pady=10)
            
        except Exception as e:
            logger.error(f"Error getting weather data: {e}")
            ttk.Label(main_frame, text=f"Error getting weather data: {e}").pack(pady=10)
    
    def _refresh_weather_data(self, parent: ttk.Widget) -> None:
        """
        Refresh weather data and update the weather tab.
        
        Args:
            parent: Parent widget
        """
        try:
            # Clear weather cache
            self.weather_service.clear_cache()
            
            # Clear the parent widget
            for widget in parent.winfo_children():
                widget.destroy()
            
            # Recreate the weather tab
            self._create_weather_tab(parent)
            
            logger.info("Weather data refreshed")
        except Exception as e:
            logger.error(f"Error refreshing weather data: {e}")
            messagebox.showerror("Error", f"Failed to refresh weather data: {e}")
    
    def run_cli(self) -> None:
        """Run the application in CLI mode."""
        logger.info("Starting CLI application")
        
        # Get weather data
        weather_data = self.weather_service.get_weather()
        
        # Print welcome message
        print("\nDeep Blue Pool Chemistry CLI")
        print("===========================")
        print(f"Current Weather: {weather_data.get('conditions', 'Unknown')}, {weather_data.get('temperature', 'Unknown')}\u00b0F")
        
        # Main loop
        while True:
            # Print menu
            print("\nMenu:")
            print("1. Customer Management")
            print("2. Test Water Chemistry")
            print("3. View Recent Tests")
            print("4. Calculate Chemical Adjustments")
            print("5. Check Weather Impact")
            print("6. View Chemical Safety Information")
            print("7. Arduino Sensor Monitor")
            print("8. Exit")
            
            # Get user choice
            choice = input("\nEnter your choice (1-8): ")
            
            # Process choice
            if choice == "1":
                self._cli_customer_management()
            elif choice == "2":
                self._cli_test_water()
            elif choice == "3":
                self._cli_view_tests()
            elif choice == "4":
                self._cli_calculate_chemicals()
            elif choice == "5":
                self._cli_check_weather()
            elif choice == "6":
                self._cli_view_safety()
            elif choice == "7":
                self._cli_arduino_monitor()
            elif choice == "8":
                print("\nExiting Deep Blue Pool Chemistry. Goodbye!")
                break
            else:
                print("\nInvalid choice. Please try again.")
    
    def _cli_customer_management(self) -> None:
        """Customer management in CLI mode."""
        while True:
            print("\nCustomer Management")
            print("==================")
            print("1. Add New Customer")
            print("2. View All Customers")
            print("3. View Customer Details")
            print("4. Return to Main Menu")
            
            choice = input("\nEnter your choice (1-4): ")
            
            if choice == "1":
                # Add new customer
                print("\nAdd New Customer")
                print("--------------")
                
                first_name = input("First Name: ")
                last_name = input("Last Name: ")
                address = input("Address: ")
                city = input("City: ")
                state = input("State: ")
                zip_code = input("ZIP: ")
                phone = input("Phone: ")
                email = input("Email: ")
                
                print("\nPool Information")
                pool_type = input("Pool Type (Concrete/Gunite, Vinyl, Fiberglass): ")
                pool_size = input("Pool Size (gallons): ")
                service_day = input("Service Day (Monday-Friday): ")
                notes = input("Notes: ")
                
                # Create customer data
                customer_data = {
                    "first_name": first_name,
                    "last_name": last_name,
                    "address": address,
                    "city": city,
                    "state": state,
                    "zip": zip_code,
                    "phone": phone,
                    "email": email,
                    "pool_type": pool_type,
                    "pool_size": pool_size,
                    "service_day": service_day,
                    "notes": notes
                }
                
                try:
                    # Save customer data
                    customer_id = self.db_service.insert_customer(customer_data)
                    
                    if customer_id:
                        print(f"\nCustomer {first_name} {last_name} added successfully with ID: {customer_id}")
                    else:
                        print("\nFailed to add customer.")
                except Exception as e:
                    print(f"\nError saving customer: {e}")
            
            elif choice == "2":
                # View all customers
                print("\nAll Customers")
                print("------------")
                
                try:
                    customers = self.db_service.get_all_customers()
                    
                    if not customers:
                        print("No customers found.")
                    else:
                        print(f"{'ID':<5} {'Name':<30} {'Phone':<15} {'Email':<30} {'Service Day':<10}")
                        print("-" * 90)
                        
                        for customer in customers:
                            print(f"{customer.get('id', ''):<5} {customer.get('first_name', '')} {customer.get('last_name', ''):<30} {customer.get('phone', ''):<15} {customer.get('email', ''):<30} {customer.get('service_day', ''):<10}")
                except Exception as e:
                    print(f"\nError retrieving customers: {e}")
            
            elif choice == "3":
                # View customer details
                print("\nView Customer Details")
                print("-------------------")
                
                customer_id = input("Enter Customer ID: ")
                
                try:
                    customer = self.db_service.get_customer(customer_id)
                    
                    if customer:
                        print(f"\nCustomer Details: {customer.get('first_name', '')} {customer.get('last_name', '')}")
                        print("-" * 50)
                        print(f"Address: {customer.get('address', '')}, {customer.get('city', '')}, {customer.get('state', '')} {customer.get('zip', '')}")
                        print(f"Phone: {customer.get('phone', '')}")
                        print(f"Email: {customer.get('email', '')}")
                        print(f"\nPool Type: {customer.get('pool_type', '')}")
                        print(f"Pool Size: {customer.get('pool_size', '')} gallons")
                        print(f"Service Day: {customer.get('service_day', '')}")
                        print(f"\nNotes: {customer.get('notes', '')}")
                    else:
                        print(f"\nCustomer with ID {customer_id} not found.")
                except Exception as e:
                    print(f"\nError retrieving customer details: {e}")
            
            elif choice == "4":
                # Return to main menu
                break
            
            else:
                print("\nInvalid choice. Please try again.")
    
    def _cli_test_water(self) -> None:
        """Test water chemistry in CLI mode."""
        print("\nTest Water Chemistry")
        print("===================")
        
        # Get customer ID
        customer_id = input("Enter Customer ID (or leave blank for no customer): ")
        
        # Get test results
        print("\nEnter test results:")
        ph = input("pH: ")
        free_chlorine = input("Free Chlorine (ppm): ")
        total_chlorine = input("Total Chlorine (ppm): ")
        alkalinity = input("Alkalinity (ppm): ")
        calcium = input("Calcium Hardness (ppm): ")
        cyanuric_acid = input("Cyanuric Acid (ppm): ")
        salt = input("Salt (ppm): ")
        temperature = input("Temperature (\u00b0F): ")
        
        # Create test data
        test_data = {
            "ph": ph,
            "free_chlorine": free_chlorine,
            "total_chlorine": total_chlorine,
            "alkalinity": alkalinity,
            "calcium": calcium,
            "cyanuric_acid": cyanuric_acid,
            "salt": salt,
            "temperature": temperature,
            "source": "manual"
        }
        
        # Add customer ID if provided
        if customer_id:
            test_data["customer_id"] = customer_id
        
        # Save test results
        try:
            reading_id = self.db_service.insert_reading(test_data)
            print(f"\nTest results saved successfully with ID: {reading_id}")
        except Exception as e:
            print(f"\nError saving test results: {e}")
    
    def _cli_view_tests(self) -> None:
        """View recent tests in CLI mode."""
        print("\nRecent Tests")
        print("===========")
        
        # Get customer ID
        customer_id = input("Enter Customer ID (or leave blank for all tests): ")
        
        # Get recent readings
        try:
            if customer_id:
                readings = self.db_service.get_customer_readings(customer_id, 5)
            else:
                readings = self.db_service.get_recent_readings(5)
            
            if not readings:
                print("\nNo test results found.")
                return
            
            # Print readings
            for reading in readings:
                print(f"\nDate: {reading.get('timestamp', 'Unknown')}")
                if 'customer_id' in reading:
                    print(f"Customer ID: {reading.get('customer_id', 'Unknown')}")
                print(f"pH: {reading.get('ph', 'Unknown')}")
                print(f"Free Chlorine: {reading.get('free_chlorine', 'Unknown')} ppm")
                print(f"Total Chlorine: {reading.get('total_chlorine', 'Unknown')} ppm")
                print(f"Alkalinity: {reading.get('alkalinity', 'Unknown')} ppm")
                print(f"Calcium Hardness: {reading.get('calcium', 'Unknown')} ppm")
                print(f"Cyanuric Acid: {reading.get('cyanuric_acid', 'Unknown')} ppm")
                print(f"Salt: {reading.get('salt', 'Unknown')} ppm")
                print(f"Temperature: {reading.get('temperature', 'Unknown')}\u00b0F")
        except Exception as e:
            print(f"\nError retrieving test results: {e}")
    
    def _cli_calculate_chemicals(self) -> None:
        """Calculate chemical adjustments in CLI mode."""
        print("\nCalculate Chemical Adjustments")
        print("============================")
        
        # Get customer ID
        customer_id = input("Enter Customer ID (or leave blank for no customer): ")
        
        # Get pool information
        if customer_id:
            try:
                customer = self.db_service.get_customer(customer_id)
                if customer:
                    pool_type = customer.get('pool_type', '')
                    pool_size = customer.get('pool_size', '')
                    print(f"\nUsing pool information for customer {customer.get('first_name', '')} {customer.get('last_name', '')}:")
                    print(f"Pool Type: {pool_type}")
                    print(f"Pool Size: {pool_size} gallons")
                else:
                    print(f"\nCustomer with ID {customer_id} not found.")
                    pool_type = input("\nPool Type (Concrete/Gunite, Vinyl, Fiberglass): ")
                    pool_size = input("Pool Size (gallons): ")
            except Exception as e:
                print(f"\nError retrieving customer: {e}")
                pool_type = input("\nPool Type (Concrete/Gunite, Vinyl, Fiberglass): ")
                pool_size = input("Pool Size (gallons): ")
        else:
            print("\nEnter pool information:")
            pool_type = input("Pool Type (Concrete/Gunite, Vinyl, Fiberglass): ")
            pool_size = input("Pool Size (gallons): ")
        
        # Get test results
        print("\nEnter test results:")
        ph = input("pH: ")
        free_chlorine = input("Free Chlorine (ppm): ")
        total_chlorine = input("Total Chlorine (ppm): ")
        alkalinity = input("Alkalinity (ppm): ")
        calcium = input("Calcium Hardness (ppm): ")
        cyanuric_acid = input("Cyanuric Acid (ppm): ")
        salt = input("Salt (ppm): ")
        temperature = input("Temperature (\u00b0F): ")
        
        # Create pool data
        pool_data = {
            "pool_type": pool_type,
            "pool_size": pool_size,
            "ph": ph,
            "chlorine": free_chlorine,
            "total_chlorine": total_chlorine,
            "alkalinity": alkalinity,
            "calcium_hardness": calcium,
            "cyanuric_acid": cyanuric_acid,
            "salt": salt,
            "temperature": temperature
        }
        
        # Add customer ID if provided
        if customer_id:
            pool_data["customer_id"] = customer_id
        
        try:
            # Calculate chemicals
            result = self.controller.calculate_chemicals(pool_data)
            
            # Print results
            print("\nRecommended Adjustments:")
            
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
                
                if "cyanuric_acid" in adjustments:
                    print(f"Cyanuric Acid: {adjustments['cyanuric_acid']} oz")
                
                if "salt" in adjustments:
                    print(f"Salt: {adjustments['salt']} oz")
            
            if "water_balance" in result:
                print(f"\nWater Balance Index: {result['water_balance']:.2f}")
                
                if result["water_balance"] < -0.5:
                    print("Water is corrosive.")
                elif result["water_balance"] > 0.5:
                    print("Water is scale-forming.")
                else:
                    print("Water is balanced.")
            
            # Print safety information
            print("\nCHEMICAL SAFETY INFORMATION:")
            
            # Get chemicals used in adjustments
            chemicals_used = []
            if "adjustments" in result:
                for chemical in result["adjustments"]:
                    if chemical == "ph_increaser":
                        chemicals_used.append("sodium_bicarbonate")
                    elif chemical == "ph_decreaser":
                        chemicals_used.append("muriatic_acid")
                    elif chemical == "alkalinity_increaser":
                        chemicals_used.append("sodium_bicarbonate")
                    elif chemical == "calcium_increaser":
                        chemicals_used.append("calcium_chloride")
                    elif chemical == "chlorine":
                        chemicals_used.append("chlorine")
            
            # Print safety information for each chemical
            for chemical_id in chemicals_used:
                try:
                    chemical_info = self.chemical_safety_db.get_chemical_safety_info(chemical_id)
                    
                    if chemical_info:
                        print(f"\n--- {chemical_info.get('name', chemical_id)} ---")
                        print(f"Hazard Rating: {chemical_info.get('hazard_rating', 'Unknown')}")
                        
                        print("\nSafety Precautions:")
                        if 'safety_precautions' in chemical_info and chemical_info['safety_precautions']:
                            for precaution in chemical_info['safety_precautions']:
                                print(f"• {precaution}")
                        else:
                            print("No safety precautions available")
                        
                        print(f"\nStorage Guidelines: {chemical_info.get('storage_guidelines', 'No information available')}")
                        print(f"\nEmergency Procedures: {chemical_info.get('emergency_procedures', 'No information available')}")
                except Exception as e:
                    print(f"\nError getting safety info for {chemical_id}: {e}")
            
            # Print treatment steps
            print("\nTREATMENT STEPS:")
            print("\nFollow these steps in order to safely adjust your pool chemistry:")
            
            step_num = 1
            
            # Always adjust alkalinity first
            if "adjustments" in result and "alkalinity_increaser" in result["adjustments"]:
                amount = result["adjustments"]["alkalinity_increaser"]
                print(f"\n{step_num}. Adjust Alkalinity:")
                print(f"   - Add {amount} oz of Alkalinity Increaser (Sodium Bicarbonate)")
                print(f"   - Broadcast over deep end of pool")
                print(f"   - Run circulation pump for at least 4 hours")
                print(f"   - Wait 24 hours before making other adjustments")
                step_num += 1
            
            # Then adjust pH
            if "adjustments" in result:
                if "ph_increaser" in result["adjustments"]:
                    amount = result["adjustments"]["ph_increaser"]
                    print(f"\n{step_num}. Increase pH:")
                    print(f"   - Add {amount} oz of pH Increaser (Sodium Carbonate)")
                    print(f"   - Broadcast over deep end of pool")
                    print(f"   - Run circulation pump for at least 4 hours")
                    print(f"   - Wait 6 hours before making other adjustments")
                    step_num += 1
                elif "ph_decreaser" in result["adjustments"]:
                    amount = result["adjustments"]["ph_decreaser"]
                    print(f"\n{step_num}. Decrease pH:")
                    print(f"   - CAUTION: Always add acid to water, never water to acid")
                    print(f"   - Add {amount} oz of pH Decreaser (Muriatic Acid)")
                    print(f"   - Pour slowly around the perimeter of the pool")
                    print(f"   - Run circulation pump for at least 4 hours")
                    print(f"   - Wait 6 hours before making other adjustments")
                    step_num += 1
            
            # Then adjust calcium hardness
            if "adjustments" in result and "calcium_increaser" in result["adjustments"]:
                amount = result["adjustments"]["calcium_increaser"]
                print(f"\n{step_num}. Adjust Calcium Hardness:")
                print(f"   - Add {amount} oz of Calcium Hardness Increaser (Calcium Chloride)")
                print(f"   - Dissolve in a bucket of water before adding to pool")
                print(f"   - Pour solution around the perimeter of the pool")
                print(f"   - Run circulation pump for at least 4 hours")
                step_num += 1
            
            # Then adjust cyanuric acid
            if "adjustments" in result and "cyanuric_acid" in result["adjustments"]:
                amount = result["adjustments"]["cyanuric_acid"]
                print(f"\n{step_num}. Adjust Cyanuric Acid (Stabilizer):")
                print(f"   - Add {amount} oz of Cyanuric Acid")
                print(f"   - Pre-dissolve in warm water (dissolves slowly)")
                print(f"   - Pour solution around the perimeter of the pool")
                print(f"   - Run circulation pump for at least 24 hours")
                step_num += 1
            
            # Then adjust salt
            if "adjustments" in result and "salt" in result["adjustments"]:
                amount = result["adjustments"]["salt"]
                print(f"\n{step_num}. Adjust Salt Level:")
                print(f"   - Add {amount} oz of Pool Salt")
                print(f"   - Broadcast over shallow end of pool")
                print(f"   - Brush to help dissolve")
                print(f"   - Run circulation pump for at least 24 hours")
                step_num += 1
            
            # Finally adjust chlorine
            if "adjustments" in result and "chlorine" in result["adjustments"]:
                amount = result["adjustments"]["chlorine"]
                print(f"\n{step_num}. Adjust Chlorine Level:")
                print(f"   - Add {amount} oz of Chlorine")
                print(f"   - Add during evening hours to prevent UV degradation")
                print(f"   - Pour around the perimeter of the pool")
                print(f"   - Run circulation pump for at least 1 hour")
                step_num += 1
            
            print("\nIMPORTANT NOTES:")
            print("• Always wear appropriate safety gear when handling chemicals")
            print("• Never mix chemicals together")
            print("• Store chemicals in a cool, dry place away from direct sunlight")
            print("• Keep chemicals out of reach of children")
            print("• Retest water after each adjustment")
            
            # Save test results
            test_id = self.controller.save_test_results(pool_data)
            if test_id:
                print(f"\nTest results saved with ID: {test_id}")
        except Exception as e:
            print(f"\nError calculating chemicals: {e}")
    
    def _cli_check_weather(self) -> None:
        """Check weather impact in CLI mode."""
        print("\nWeather Impact")
        print("=============")
        
        try:
            # Get weather data
            weather_data = self.weather_service.get_weather()
            
            # Print weather data
            print(f"\nCurrent Weather:")
            print(f"Location: {self.config['weather']['location']}")
            print(f"Temperature: {weather_data.get('temperature', 'Unknown')}\u00b0F")
            print(f"Humidity: {weather_data.get('humidity', 'Unknown')}%")
            print(f"Conditions: {weather_data.get('conditions', 'Unknown')}")
            
            # Get forecast
            forecast = self.weather_service.get_forecast(3)
            
            # Print forecast
            print("\n3-Day Forecast:")
            for i, day in enumerate(forecast):
                print(f"Day {i+1}: {day.get('temperature', 'Unknown')}\u00b0F, {day.get('conditions', 'Unknown')}")
            
            # Get weather impact
            impact = self.weather_service.analyze_weather_impact(weather_data)
            
            # Print impact
            print("\nImpact on Pool Chemistry:")
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
            
            # Print recommendations
            print("\nRecommendations:")
            
            if weather_data.get('temperature', 0) > 85:
                print("\u2022 Check chlorine levels more frequently")
                print("\u2022 Consider adding additional chlorine in the evening")
            
            if weather_data.get('conditions', '').lower() in ['sunny', 'clear']:
                print("\u2022 Ensure proper cyanuric acid levels to protect chlorine")
                print("\u2022 Add chlorine in the evening to minimize UV degradation")
            
            if weather_data.get('conditions', '').lower() in ['rain', 'showers', 'thunderstorm']:
                print("\u2022 Test water after rain to check for dilution")
                print("\u2022 Check pH and alkalinity as rain can affect these levels")
            
            if impact.get('evaporation_rate', 0) > 0.25:
                print("\u2022 Monitor water level and top up as needed")
                print("\u2022 Check calcium hardness as evaporation can increase levels")
        except Exception as e:
            print(f"\nError getting weather data: {e}")
    
    def _cli_view_safety(self) -> None:
        """View chemical safety information in CLI mode."""
        print("\nChemical Safety Information")
        print("=========================")
        
        # Get all chemicals
        chemicals = self.chemical_safety_db.get_all_chemicals()
        
        # Print chemical list
        print("\nAvailable Chemicals:")
        chemical_ids = list(chemicals.keys())
        for i, chemical_id in enumerate(chemical_ids):
            chemical = self.chemical_safety_db.get_chemical_safety_info(chemical_id)
            chemical_name = chemical.get('name', chemical_id)
            print(f"{i+1}. {chemical_name}")
        
        # Get user choice
        choice = input("\nEnter chemical number to view details (or 0 to return): ")
        
        try:
            choice_num = int(choice)
            if choice_num == 0:
                return
            
            if choice_num < 1 or choice_num > len(chemicals):
                print("\nInvalid choice.")
                return
            
            # Get chemical details
            chemical_id = chemical_ids[choice_num - 1]
            chemical = self.chemical_safety_db.get_chemical_safety_info(chemical_id)
            
            # Print chemical details
            print(f"\nChemical: {chemical.get('name', chemical_id)}")
            print(f"Chemical Formula: {chemical.get('chemical_formula', 'N/A')}")
            print(f"Hazard Rating: {chemical.get('hazard_rating', 'N/A')}")
            
            print("\nSafety Precautions:")
            if 'safety_precautions' in chemical and chemical['safety_precautions']:
                for precaution in chemical['safety_precautions']:
                    print(f"\u2022 {precaution}")
            else:
                print("No safety precautions available")
            
            print(f"\nStorage Guidelines: {chemical.get('storage_guidelines', 'No storage guidelines available')}")
            print(f"Emergency Procedures: {chemical.get('emergency_procedures', 'No emergency procedures available')}")
            
            # Print compatibility
            print("\nCompatibility:")
            try:
                compatibility = self.chemical_safety_db.get_compatibility(chemical_id)
                
                print("Compatible with:")
                compatible = [chem for chem, compat in compatibility.items() if compat]
                if compatible:
                    for chem in compatible:
                        chem_info = self.chemical_safety_db.get_chemical_safety_info(chem)
                        chem_name = chem_info.get('name', chem)
                        print(f"\u2022 {chem_name}")
                else:
                    print("None")
                
                print("\nIncompatible with:")
                incompatible = [chem for chem, compat in compatibility.items() if not compat]
                if incompatible:
                    for chem in incompatible:
                        chem_info = self.chemical_safety_db.get_chemical_safety_info(chem)
                        chem_name = chem_info.get('name', chem)
                        print(f"\u2022 {chem_name}")
                else:
                    print("None")
            except Exception as e:
                print(f"\nError getting compatibility information: {e}")
        
        except (ValueError, IndexError):
            print("\nInvalid choice.")
    
    def _cli_arduino_monitor(self) -> None:
        """Arduino sensor monitor in CLI mode."""
        print("\nArduino Sensor Monitor")
        print("====================")
        
        # Get available ports
        try:
            import serial.tools.list_ports
            ports = [port.device for port in serial.tools.list_ports.comports()]
        except:
            # Fallback to common port names
            ports = ["COM1", "COM2", "COM3", "COM4", "COM5", 
                     "/dev/ttyUSB0", "/dev/ttyUSB1", "/dev/ttyACM0", "/dev/ttyACM1"]
        
        # Print available ports
        print("\nAvailable Ports:")
        for i, port in enumerate(ports):
            print(f"{i+1}. {port}")
        
        # Get port selection
        port_choice = input("\nSelect port number (or 0 to return): ")
        
        try:
            port_num = int(port_choice)
            if port_num == 0:
                return
            
            if port_num < 1 or port_num > len(ports):
                print("\nInvalid port selection.")
                return
            
            port = ports[port_num - 1]
            
            # Connect to port
            try:
                import serial
                arduino_serial = serial.Serial(
                    port=port,
                    baudrate=self.config.get("arduino", {}).get("baud_rate", 9600),
                    timeout=self.config.get("arduino", {}).get("timeout", 1.0)
                )
                
                print(f"\nConnected to Arduino on {port}")
                
                # Monitor for a specified duration
                duration = input("\nEnter monitoring duration in seconds (or 0 for continuous): ")
                try:
                    duration_sec = int(duration)
                    
                    # Set up monitoring
                    print("\nMonitoring Arduino sensors...")
                    print("\nPress Ctrl+C to stop monitoring")
                    
                    # Start time
                    start_time = time.time()
                    
                    # Monitor loop
                    try:
                        while True:
                            # Check if duration has elapsed
                            if duration_sec > 0 and time.time() - start_time >= duration_sec:
                                break
                            
                            # In a real implementation, we would read actual data from the Arduino
                            # For now, we'll generate random data for demonstration
                            
                            # Generate timestamp
                            timestamp = datetime.now().isoformat()
                            
                            # Generate random data
                            ph = round(np.random.uniform(6.5, 8.0), 1)
                            orp = round(np.random.uniform(650, 750))
                            temperature = round(np.random.uniform(75, 85), 1)
                            tds = round(np.random.uniform(300, 500))
                            
                            # Print data
                            print(f"\nTimestamp: {timestamp}")
                            print(f"pH: {ph}")
                            print(f"ORP: {orp} mV")
                            print(f"Temperature: {temperature} °F")
                            print(f"TDS: {tds} ppm")
                            
                            # Sleep for a bit
                            time.sleep(self.config.get("arduino", {}).get("update_interval", 2.0))
                    except KeyboardInterrupt:
                        print("\nMonitoring stopped by user")
                    
                    # Close the serial connection
                    arduino_serial.close()
                    print("\nDisconnected from Arduino")
                    
                except ValueError:
                    print("\nInvalid duration. Please enter a number.")
            except Exception as e:
                print(f"\nError connecting to Arduino: {e}")
        except ValueError:
            print("\nInvalid choice.")
    
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
        
        # Close Arduino connection
        if hasattr(self, 'arduino_serial') and self.arduino_serial:
            try:
                self.arduino_serial.close()
            except:
                pass
        
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