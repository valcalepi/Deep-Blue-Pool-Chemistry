
#!/usr/bin/env python3
"""
Arduino Sensor Monitor GUI for Deep Blue Pool Chemistry

This module provides a GUI for monitoring Arduino sensor data in real-time.
"""

import os
import sys
import time
import logging
import threading
from datetime import datetime
from typing import Dict, Any, List, Optional

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.dates as mdates
import numpy as np

# Configure logging
logger = logging.getLogger("arduino_monitor")

class ArduinoMonitorApp:
    """
    GUI application for monitoring Arduino sensor data in real-time.
    """
    
    def __init__(self, parent: Optional[tk.Widget] = None):
        """
        Initialize the Arduino Monitor application.
        
        Args:
            parent: Parent widget. If None, a new window will be created.
        """
        # Initialize logger
        self.logger = logging.getLogger("arduino_monitor")
        self.logger.info("Initializing Arduino Monitor")
        
        # Store parent widget
        self.parent = parent
        
        # Create main frame
        self.main_frame = ttk.Frame(parent)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Add title
        title = ttk.Label(self.main_frame, text="Arduino Sensor Monitor", font=("Arial", 18))
        title.pack(pady=10)
        
        # Add status message
        self.status_var = tk.StringVar(value="Arduino Monitor is not connected")
        status_label = ttk.Label(self.main_frame, textvariable=self.status_var, font=("Arial", 12))
        status_label.pack(pady=5)
        
        # Create connection frame
        connection_frame = ttk.Frame(self.main_frame)
        connection_frame.pack(fill=tk.X, pady=10)
        
        # Add port selection
        ttk.Label(connection_frame, text="Port:").pack(side=tk.LEFT, padx=5)
        
        self.port_var = tk.StringVar()
        self.port_combo = ttk.Combobox(connection_frame, textvariable=self.port_var, width=20)
        self.port_combo.pack(side=tk.LEFT, padx=5)
        
        # Add refresh ports button
        ttk.Button(connection_frame, text="Refresh Ports", 
                  command=self.refresh_ports).pack(side=tk.LEFT, padx=5)
        
        # Add connect button
        self.connect_button = ttk.Button(connection_frame, text="Connect", 
                                       command=self.connect_arduino)
        self.connect_button.pack(side=tk.LEFT, padx=5)
        
        # Create sensor data frame
        sensor_frame = ttk.LabelFrame(self.main_frame, text="Sensor Data")
        sensor_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Create chart frame
        chart_frame = ttk.Frame(sensor_frame)
        chart_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create figure for chart
        self.fig = plt.Figure(figsize=(5, 4), dpi=100)
        self.ax = self.fig.add_subplot(111)
        
        # Create canvas for chart
        self.canvas = FigureCanvasTkAgg(self.fig, master=chart_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Initialize chart
        self.initialize_chart()
        
        # Create data frame
        data_frame = ttk.Frame(sensor_frame)
        data_frame.pack(fill=tk.X, pady=10)
        
        # Create sensor value labels
        self.ph_value = self.create_sensor_value_label(data_frame, "pH", 0)
        self.temp_value = self.create_sensor_value_label(data_frame, "Temperature", 1)
        self.orp_value = self.create_sensor_value_label(data_frame, "ORP", 2)
        self.tds_value = self.create_sensor_value_label(data_frame, "TDS", 3)
        
        # Try to import ArduinoSensorManager
        try:
            # First try to import from the services directory
            sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'services', 'arduino'))
            from arduino_sensor_manager import ArduinoSensorManager
            self.arduino_manager = ArduinoSensorManager()
            
            # Register callbacks
            self.arduino_manager.register_data_callback(self.on_arduino_data)
            self.arduino_manager.register_connection_callback(self.on_arduino_connection)
            
            # Refresh ports
            self.refresh_ports()
            
            logger.info("Arduino Sensor Manager initialized successfully")
        except ImportError:
            # If that fails, try to import from the root directory
            try:
                from arduino_sensor_manager import ArduinoSensorManager
                self.arduino_manager = ArduinoSensorManager()
                
                # Register callbacks
                self.arduino_manager.register_data_callback(self.on_arduino_data)
                self.arduino_manager.register_connection_callback(self.on_arduino_connection)
                
                # Refresh ports
                self.refresh_ports()
                
                logger.info("Arduino Sensor Manager initialized successfully")
            except ImportError:
                logger.error("Failed to import ArduinoSensorManager")
                self.arduino_manager = None
                self.status_var.set("Arduino Sensor Manager not available")
        except Exception as e:
            logger.error(f"Error initializing Arduino Sensor Manager: {e}")
            self.arduino_manager = None
            self.status_var.set(f"Error: {str(e)}")
        
        self.logger.info("Arduino Monitor initialized")
    
    def create_sensor_value_label(self, parent, name, column):
        """Create a sensor value label."""
        frame = ttk.Frame(parent)
        frame.grid(row=0, column=column, padx=10)
        
        ttk.Label(frame, text=f"{name}:").pack(anchor=tk.W)
        
        value_var = tk.StringVar(value="N/A")
        value_label = ttk.Label(frame, textvariable=value_var, font=("Arial", 14, "bold"))
        value_label.pack(anchor=tk.W)
        
        return value_var
    
    def initialize_chart(self):
        """Initialize the chart."""
        self.ax.clear()
        self.ax.set_title("Sensor Data")
        self.ax.set_xlabel("Time")
        self.ax.set_ylabel("Value")
        self.ax.grid(True)
        
        # Create empty data
        self.times = []
        self.ph_data = []
        self.temp_data = []
        
        # Create lines
        self.ph_line, = self.ax.plot(self.times, self.ph_data, 'b-', label='pH')
        self.temp_line, = self.ax.plot(self.times, self.temp_data, 'r-', label='Temp (\u00b0F)')
        
        self.ax.legend()
        self.fig.tight_layout()
        self.canvas.draw()
    
    def refresh_ports(self):
        """Refresh the list of available ports."""
        if hasattr(self, 'arduino_manager') and self.arduino_manager:
            try:
                ports = self.arduino_manager.list_available_ports()
                
                port_options = []
                for port, desc in ports:
                    port_options.append(f"{port}: {desc}")
                
                self.port_combo["values"] = port_options
                
                if port_options:
                    self.port_combo.current(0)
            except Exception as e:
                logger.error(f"Error refreshing ports: {e}")
                self.status_var.set(f"Error refreshing ports: {str(e)}")
    
    def connect_arduino(self):
        """Connect to the Arduino."""
        if not hasattr(self, 'arduino_manager') or not self.arduino_manager:
            messagebox.showerror("Error", "Arduino Sensor Manager not initialized")
            return
        
        try:
            if self.arduino_manager.connected:
                # Disconnect
                self.arduino_manager.disconnect()
                self.connect_button.config(text="Connect")
                self.status_var.set("Arduino Monitor is not connected")
            else:
                # Connect
                port = self.port_var.get().split(":")[0] if self.port_var.get() else None
                
                if port:
                    self.arduino_manager.port = port
                    
                    if self.arduino_manager.connect():
                        self.arduino_manager.start()
                        self.connect_button.config(text="Disconnect")
                        self.status_var.set("Arduino Monitor is connected")
                    else:
                        messagebox.showerror("Error", "Failed to connect to Arduino")
                else:
                    messagebox.showerror("Error", "No port selected")
        except Exception as e:
            logger.error(f"Error connecting to Arduino: {e}")
            messagebox.showerror("Error", f"Failed to connect to Arduino: {e}")
    
    def on_arduino_connection(self, connected):
        """Handle Arduino connection status change."""
        if connected:
            self.status_var.set("Arduino Monitor is connected")
            self.connect_button.config(text="Disconnect")
        else:
            self.status_var.set("Arduino Monitor is not connected")
            self.connect_button.config(text="Connect")
    
    def on_arduino_data(self, data):
        """Handle Arduino data."""
        # Update sensor value labels
        if "pH" in data:
            self.ph_value.set(f"{data['pH']}")
        
        if "temp" in data:
            self.temp_value.set(f"{data['temp']}\u00b0F")
        
        if "orp" in data:
            self.orp_value.set(f"{data['orp']} mV")
        
        if "tds" in data:
            self.tds_value.set(f"{data['tds']} ppm")
        
        # Update chart
        if "pH" in data and "temp" in data:
            # Add current time
            current_time = datetime.now().strftime("%H:%M:%S")
            
            # Add data to lists
            self.times.append(current_time)
            self.ph_data.append(float(data["pH"]))
            self.temp_data.append(float(data["temp"]))
            
            # Keep only last 20 points
            if len(self.times) > 20:
                self.times = self.times[-20:]
                self.ph_data = self.ph_data[-20:]
                self.temp_data = self.temp_data[-20:]
            
            # Update lines
            self.ph_line.set_data(range(len(self.times)), self.ph_data)
            self.temp_line.set_data(range(len(self.times)), self.temp_data)
            
            # Update axes
            self.ax.set_xlim(0, len(self.times) - 1)
            self.ax.set_xticks(range(len(self.times)))
            self.ax.set_xticklabels(self.times, rotation=45)
            
            # Update y limits
            ph_min = min(self.ph_data) - 0.5 if self.ph_data else 6.5
            ph_max = max(self.ph_data) + 0.5 if self.ph_data else 8.5
            temp_min = min(self.temp_data) - 5 if self.temp_data else 70
            temp_max = max(self.temp_data) + 5 if self.temp_data else 90
            
            self.ax.set_ylim(min(ph_min, temp_min/10), max(ph_max, temp_max/10))
            
            # Draw
            self.fig.tight_layout()
            self.canvas.draw()

# For testing
if __name__ == "__main__":
    # Create root window
    root = tk.Tk()
    root.title("Arduino Monitor Test")
    root.geometry("800x600")
    
    # Create Arduino Monitor
    app = ArduinoMonitorApp(root)
    
    # Run the application
    root.mainloop()
