
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
import json
from datetime import datetime
from typing import Dict, Any, List, Optional

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.dates as mdates
import numpy as np

# Add parent directory to path to import from services
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.arduino.arduino_sensor_manager import ArduinoSensorManager

# Configure logging
logger = logging.getLogger("arduino_monitor")

class ArduinoMonitorApp:
    """
    GUI application for monitoring Arduino sensor data in real-time.
    """
    
    def __init__(self, root: Optional[tk.Tk] = None):
        """
        Initialize the Arduino Monitor application.
        
        Args:
            root: Tkinter root window. If None, a new window will be created.
        """
        # Initialize logger
        self.logger = logging.getLogger("arduino_monitor")
        
        # Create root window if not provided
        if root is None:
            self.root = tk.Tk()
            self.root.title("Deep Blue Pool Chemistry - Arduino Sensor Monitor")
            self.root.geometry("1000x700")
            self.standalone = True
        else:
            self.root = root
            self.standalone = False
        
        # Initialize Arduino sensor manager
        self.arduino = ArduinoSensorManager()
        
        # Initialize data storage
        self.data_history = {
            'timestamp': [],
            'pH': [],
            'temp': [],
            'orp': [],
            'tds': [],
            'turb': []
        }
        self.max_history_points = 100  # Maximum number of data points to store
        
        # Create GUI elements
        self._create_gui()
        
        # Register callbacks
        self.arduino.register_data_callback(self._on_data_received)
        self.arduino.register_connection_callback(self._on_connection_changed)
        
        # Update available ports
        self._update_port_list()
        
        # Start periodic UI updates
        self._start_ui_updates()
    
    def _create_gui(self):
        """Create the GUI elements."""
        # Create main frame
        self.main_frame = ttk.Frame(self.root, padding=10)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create connection frame
        self.connection_frame = ttk.LabelFrame(self.main_frame, text="Arduino Connection", padding=10)
        self.connection_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Port selection
        ttk.Label(self.connection_frame, text="Port:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.port_var = tk.StringVar()
        self.port_combo = ttk.Combobox(self.connection_frame, textvariable=self.port_var)
        self.port_combo.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        
        # Refresh ports button
        ttk.Button(self.connection_frame, text="Refresh", command=self._update_port_list).grid(
            row=0, column=2, padx=5, pady=5)
        
        # Connect/disconnect button
        self.connect_var = tk.StringVar(value="Connect")
        self.connect_button = ttk.Button(self.connection_frame, textvariable=self.connect_var, 
                                        command=self._toggle_connection)
        self.connect_button.grid(row=0, column=3, padx=5, pady=5)
        
        # Status indicator
        ttk.Label(self.connection_frame, text="Status:").grid(row=0, column=4, padx=5, pady=5)
        self.status_var = tk.StringVar(value="Disconnected")
        self.status_label = ttk.Label(self.connection_frame, textvariable=self.status_var)
        self.status_label.grid(row=0, column=5, padx=5, pady=5)
        
        # Create notebook for different views
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create dashboard tab
        self.dashboard_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.dashboard_frame, text="Dashboard")
        
        # Create graphs tab
        self.graphs_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.graphs_frame, text="Graphs")
        
        # Create calibration tab
        self.calibration_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.calibration_frame, text="Calibration")
        
        # Create settings tab
        self.settings_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.settings_frame, text="Settings")
        
        # Set up dashboard
        self._setup_dashboard()
        
        # Set up graphs
        self._setup_graphs()
        
        # Set up calibration
        self._setup_calibration()
        
        # Set up settings
        self._setup_settings()
        
        # Create status bar
        self.status_bar = ttk.Frame(self.root)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.status_message = tk.StringVar(value="Ready")
        ttk.Label(self.status_bar, textvariable=self.status_message).pack(side=tk.LEFT, padx=5)
        
        self.last_update_var = tk.StringVar(value="Last update: Never")
        ttk.Label(self.status_bar, textvariable=self.last_update_var).pack(side=tk.RIGHT, padx=5)
    
    def _setup_dashboard(self):
        """Set up the dashboard tab."""
        # Create frames for sensor readings
        self.readings_frame = ttk.LabelFrame(self.dashboard_frame, text="Current Readings", padding=10)
        self.readings_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create gauge frames
        gauge_frame_top = ttk.Frame(self.readings_frame)
        gauge_frame_top.pack(fill=tk.X, expand=True, padx=5, pady=5)
        
        gauge_frame_bottom = ttk.Frame(self.readings_frame)
        gauge_frame_bottom.pack(fill=tk.X, expand=True, padx=5, pady=5)
        
        # Create pH gauge
        self.ph_gauge_frame = ttk.LabelFrame(gauge_frame_top, text="pH", padding=10)
        self.ph_gauge_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.ph_value_var = tk.StringVar(value="--")
        self.ph_value_label = ttk.Label(self.ph_gauge_frame, textvariable=self.ph_value_var, 
                                       font=("Arial", 24))
        self.ph_value_label.pack(pady=10)
        
        self.ph_gauge = ttk.Progressbar(self.ph_gauge_frame, orient=tk.HORIZONTAL, length=200, 
                                       mode='determinate')
        self.ph_gauge.pack(fill=tk.X, padx=10, pady=5)
        
        self.ph_status_var = tk.StringVar(value="No data")
        ttk.Label(self.ph_gauge_frame, textvariable=self.ph_status_var).pack(pady=5)
        
        # Create temperature gauge
        self.temp_gauge_frame = ttk.LabelFrame(gauge_frame_top, text="Temperature (\u00b0C)", padding=10)
        self.temp_gauge_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.temp_value_var = tk.StringVar(value="--")
        self.temp_value_label = ttk.Label(self.temp_gauge_frame, textvariable=self.temp_value_var, 
                                         font=("Arial", 24))
        self.temp_value_label.pack(pady=10)
        
        self.temp_gauge = ttk.Progressbar(self.temp_gauge_frame, orient=tk.HORIZONTAL, length=200, 
                                         mode='determinate')
        self.temp_gauge.pack(fill=tk.X, padx=10, pady=5)
        
        self.temp_status_var = tk.StringVar(value="No data")
        ttk.Label(self.temp_gauge_frame, textvariable=self.temp_status_var).pack(pady=5)
        
        # Create ORP gauge
        self.orp_gauge_frame = ttk.LabelFrame(gauge_frame_top, text="ORP (mV)", padding=10)
        self.orp_gauge_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.orp_value_var = tk.StringVar(value="--")
        self.orp_value_label = ttk.Label(self.orp_gauge_frame, textvariable=self.orp_value_var, 
                                        font=("Arial", 24))
        self.orp_value_label.pack(pady=10)
        
        self.orp_gauge = ttk.Progressbar(self.orp_gauge_frame, orient=tk.HORIZONTAL, length=200, 
                                        mode='determinate')
        self.orp_gauge.pack(fill=tk.X, padx=10, pady=5)
        
        self.orp_status_var = tk.StringVar(value="No data")
        ttk.Label(self.orp_gauge_frame, textvariable=self.orp_status_var).pack(pady=5)
        
        # Create TDS gauge
        self.tds_gauge_frame = ttk.LabelFrame(gauge_frame_bottom, text="TDS (ppm)", padding=10)
        self.tds_gauge_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.tds_value_var = tk.StringVar(value="--")
        self.tds_value_label = ttk.Label(self.tds_gauge_frame, textvariable=self.tds_value_var, 
                                        font=("Arial", 24))
        self.tds_value_label.pack(pady=10)
        
        self.tds_gauge = ttk.Progressbar(self.tds_gauge_frame, orient=tk.HORIZONTAL, length=200, 
                                        mode='determinate')
        self.tds_gauge.pack(fill=tk.X, padx=10, pady=5)
        
        self.tds_status_var = tk.StringVar(value="No data")
        ttk.Label(self.tds_gauge_frame, textvariable=self.tds_status_var).pack(pady=5)
        
        # Create turbidity gauge
        self.turb_gauge_frame = ttk.LabelFrame(gauge_frame_bottom, text="Turbidity (NTU)", padding=10)
        self.turb_gauge_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.turb_value_var = tk.StringVar(value="--")
        self.turb_value_label = ttk.Label(self.turb_gauge_frame, textvariable=self.turb_value_var, 
                                         font=("Arial", 24))
        self.turb_value_label.pack(pady=10)
        
        self.turb_gauge = ttk.Progressbar(self.turb_gauge_frame, orient=tk.HORIZONTAL, length=200, 
                                         mode='determinate')
        self.turb_gauge.pack(fill=tk.X, padx=10, pady=5)
        
        self.turb_status_var = tk.StringVar(value="No data")
        ttk.Label(self.turb_gauge_frame, textvariable=self.turb_status_var).pack(pady=5)
        
        # Create recommendations frame
        self.recommendations_frame = ttk.LabelFrame(self.dashboard_frame, text="Recommendations", padding=10)
        self.recommendations_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.recommendations_text = tk.Text(self.recommendations_frame, height=5, wrap=tk.WORD)
        self.recommendations_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.recommendations_text.insert(tk.END, "Connect to Arduino to receive recommendations.")
        self.recommendations_text.config(state=tk.DISABLED)
    
    def _setup_graphs(self):
        """Set up the graphs tab."""
        # Create figure for plots
        self.fig = Figure(figsize=(10, 8), dpi=100)
        
        # Create subplots
        self.ax1 = self.fig.add_subplot(3, 2, 1)  # pH
        self.ax2 = self.fig.add_subplot(3, 2, 2)  # Temperature
        self.ax3 = self.fig.add_subplot(3, 2, 3)  # ORP
        self.ax4 = self.fig.add_subplot(3, 2, 4)  # TDS
        self.ax5 = self.fig.add_subplot(3, 2, 5)  # Turbidity
        
        # Set titles
        self.ax1.set_title("pH")
        self.ax2.set_title("Temperature (\u00b0C)")
        self.ax3.set_title("ORP (mV)")
        self.ax4.set_title("TDS (ppm)")
        self.ax5.set_title("Turbidity (NTU)")
        
        # Create empty plots
        self.ph_line, = self.ax1.plot([], [], 'b-')
        self.temp_line, = self.ax2.plot([], [], 'r-')
        self.orp_line, = self.ax3.plot([], [], 'g-')
        self.tds_line, = self.ax4.plot([], [], 'm-')
        self.turb_line, = self.ax5.plot([], [], 'c-')
        
        # Set y-axis limits
        self.ax1.set_ylim(0, 14)  # pH range
        self.ax2.set_ylim(0, 50)  # Temperature range
        self.ax3.set_ylim(0, 1000)  # ORP range
        self.ax4.set_ylim(0, 1000)  # TDS range
        self.ax5.set_ylim(0, 10)  # Turbidity range
        
        # Adjust layout
        self.fig.tight_layout()
        
        # Create canvas
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.graphs_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Create toolbar frame
        toolbar_frame = ttk.Frame(self.graphs_frame)
        toolbar_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Add controls
        ttk.Label(toolbar_frame, text="History size:").pack(side=tk.LEFT, padx=5)
        
        self.history_var = tk.StringVar(value=str(self.max_history_points))
        history_entry = ttk.Entry(toolbar_frame, textvariable=self.history_var, width=5)
        history_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(toolbar_frame, text="Apply", 
                  command=lambda: self._set_history_size(int(self.history_var.get()))).pack(
                      side=tk.LEFT, padx=5)
        
        ttk.Button(toolbar_frame, text="Clear History", 
                  command=self._clear_history).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(toolbar_frame, text="Export Data", 
                  command=self._export_data).pack(side=tk.LEFT, padx=5)
    
    def _setup_calibration(self):
        """Set up the calibration tab."""
        # Create calibration controls
        ttk.Label(self.calibration_frame, text="Sensor Calibration", 
                 font=("Arial", 14, "bold")).pack(pady=10)
        
        # Create calibration frames
        cal_frame = ttk.Frame(self.calibration_frame)
        cal_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # pH calibration
        ph_cal_frame = ttk.LabelFrame(cal_frame, text="pH Calibration", padding=10)
        ph_cal_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(ph_cal_frame, text="Known pH value:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.ph_cal_var = tk.StringVar(value="7.0")
        ttk.Entry(ph_cal_frame, textvariable=self.ph_cal_var, width=10).grid(
            row=0, column=1, padx=5, pady=5, sticky=tk.W)
        
        ttk.Button(ph_cal_frame, text="Calibrate", 
                  command=lambda: self._calibrate_sensor("pH", float(self.ph_cal_var.get()))).grid(
                      row=0, column=2, padx=5, pady=5)
        
        # ORP calibration
        orp_cal_frame = ttk.LabelFrame(cal_frame, text="ORP Calibration", padding=10)
        orp_cal_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(orp_cal_frame, text="Known ORP value (mV):").grid(
            row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.orp_cal_var = tk.StringVar(value="650")
        ttk.Entry(orp_cal_frame, textvariable=self.orp_cal_var, width=10).grid(
            row=0, column=1, padx=5, pady=5, sticky=tk.W)
        
        ttk.Button(orp_cal_frame, text="Calibrate", 
                  command=lambda: self._calibrate_sensor("orp", float(self.orp_cal_var.get()))).grid(
                      row=0, column=2, padx=5, pady=5)
        
        # TDS calibration
        tds_cal_frame = ttk.LabelFrame(cal_frame, text="TDS Calibration", padding=10)
        tds_cal_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(tds_cal_frame, text="Known TDS value (ppm):").grid(
            row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.tds_cal_var = tk.StringVar(value="500")
        ttk.Entry(tds_cal_frame, textvariable=self.tds_cal_var, width=10).grid(
            row=0, column=1, padx=5, pady=5, sticky=tk.W)
        
        ttk.Button(tds_cal_frame, text="Calibrate", 
                  command=lambda: self._calibrate_sensor("tds", float(self.tds_cal_var.get()))).grid(
                      row=0, column=2, padx=5, pady=5)
        
        # Calibration instructions
        instructions_frame = ttk.LabelFrame(self.calibration_frame, text="Instructions", padding=10)
        instructions_frame.pack(fill=tk.X, padx=5, pady=5)
        
        instructions_text = tk.Text(instructions_frame, height=6, wrap=tk.WORD)
        instructions_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        instructions_text.insert(tk.END, 
            "Calibration Instructions:\
\
"
            "1. Place the sensor in a solution with a known value\
"
            "2. Enter the known value in the appropriate field\
"
            "3. Click the 'Calibrate' button\
"
            "4. Wait for confirmation that calibration is complete\
\
"
            "Note: Calibration requires an active connection to the Arduino.")
        instructions_text.config(state=tk.DISABLED)
    
    def _setup_settings(self):
        """Set up the settings tab."""
        # Create settings controls
        ttk.Label(self.settings_frame, text="Arduino Settings", 
                 font=("Arial", 14, "bold")).pack(pady=10)
        
        # Create settings frame
        settings_frame = ttk.Frame(self.settings_frame)
        settings_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Update interval
        interval_frame = ttk.LabelFrame(settings_frame, text="Update Interval", padding=10)
        interval_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(interval_frame, text="Sensor reading interval (ms):").grid(
            row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.interval_var = tk.StringVar(value="2000")
        ttk.Entry(interval_frame, textvariable=self.interval_var, width=10).grid(
            row=0, column=1, padx=5, pady=5, sticky=tk.W)
        
        ttk.Button(interval_frame, text="Apply", 
                  command=lambda: self._set_update_interval(int(self.interval_var.get()))).grid(
                      row=0, column=2, padx=5, pady=5)
        
        # Data logging
        logging_frame = ttk.LabelFrame(settings_frame, text="Data Logging", padding=10)
        logging_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.logging_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(logging_frame, text="Enable data logging to file", 
                       variable=self.logging_var, command=self._toggle_logging).grid(
                           row=0, column=0, columnspan=2, padx=5, pady=5, sticky=tk.W)
        
        ttk.Label(logging_frame, text="Log file:").grid(
            row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.log_file_var = tk.StringVar(value="sensor_data.csv")
        ttk.Entry(logging_frame, textvariable=self.log_file_var, width=30).grid(
            row=1, column=1, padx=5, pady=5, sticky=tk.W)
        
        ttk.Button(logging_frame, text="Browse", 
                  command=self._browse_log_file).grid(row=1, column=2, padx=5, pady=5)
        
        # About section
        about_frame = ttk.LabelFrame(settings_frame, text="About", padding=10)
        about_frame.pack(fill=tk.X, padx=5, pady=5)
        
        about_text = tk.Text(about_frame, height=6, wrap=tk.WORD)
        about_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        about_text.insert(tk.END, 
            "Deep Blue Pool Chemistry - Arduino Sensor Monitor\
\
"
            "This application allows you to monitor and calibrate Arduino-based sensors "
            "for pool water quality monitoring. It provides real-time data visualization "
            "and recommendations based on sensor readings.\
\
"
            "Version: 1.0.0\
"
            "\u00a9 2025 NinjaTech AI")
        about_text.config(state=tk.DISABLED)
    
    def _update_port_list(self):
        """Update the list of available serial ports."""
        ports = self.arduino.list_available_ports()
        port_list = [port for port, desc in ports]
        self.port_combo['values'] = port_list
        
        if port_list and not self.port_var.get():
            self.port_var.set(port_list[0])
    
    def _toggle_connection(self):
        """Toggle the connection to the Arduino."""
        if not self.arduino.connected:
            # Connect
            port = self.port_var.get()
            if not port:
                messagebox.showerror("Error", "No port selected")
                return
            
            self.arduino.port = port
            if self.arduino.connect():
                self.arduino.start()
                self.connect_var.set("Disconnect")
                self.status_var.set("Connected")
                self.status_message.set(f"Connected to Arduino on port {port}")
            else:
                messagebox.showerror("Error", f"Failed to connect to Arduino on port {port}")
        else:
            # Disconnect
            self.arduino.stop()
            self.arduino.disconnect()
            self.connect_var.set("Connect")
            self.status_var.set("Disconnected")
            self.status_message.set("Disconnected from Arduino")
    
    def _on_connection_changed(self, connected):
        """Handle connection status changes."""
        if connected:
            self.connect_var.set("Disconnect")
            self.status_var.set("Connected")
            self.status_message.set(f"Connected to Arduino on port {self.arduino.port}")
        else:
            self.connect_var.set("Connect")
            self.status_var.set("Disconnected")
            self.status_message.set("Disconnected from Arduino")
    
    def _on_data_received(self, data):
        """Handle received sensor data."""
        # Store data in history
        timestamp = datetime.now()
        self.data_history['timestamp'].append(timestamp)
        self.data_history['pH'].append(data.get('pH', None))
        self.data_history['temp'].append(data.get('temp', None))
        self.data_history['orp'].append(data.get('orp', None))
        self.data_history['tds'].append(data.get('tds', None))
        self.data_history['turb'].append(data.get('turb', None))
        
        # Limit history size
        if len(self.data_history['timestamp']) > self.max_history_points:
            self.data_history['timestamp'] = self.data_history['timestamp'][-self.max_history_points:]
            self.data_history['pH'] = self.data_history['pH'][-self.max_history_points:]
            self.data_history['temp'] = self.data_history['temp'][-self.max_history_points:]
            self.data_history['orp'] = self.data_history['orp'][-self.max_history_points:]
            self.data_history['tds'] = self.data_history['tds'][-self.max_history_points:]
            self.data_history['turb'] = self.data_history['turb'][-self.max_history_points:]
        
        # Update last update time
        self.last_update_var.set(f"Last update: {timestamp.strftime('%H:%M:%S')}")
        
        # Generate recommendations based on data
        self._generate_recommendations(data)
        
        # Log data if enabled
        if hasattr(self, 'logging_enabled') and self.logging_enabled:
            self._log_data(timestamp, data)
    
    def _update_ui(self):
        """Update the UI with the latest data."""
        # Get the latest data
        data = self.arduino.get_latest_data()
        
        # Update dashboard
        if 'pH' in data:
            ph = data['pH']
            self.ph_value_var.set(f"{ph:.2f}")
            self.ph_gauge['value'] = (ph / 14.0) * 100
            
            if 6.8 <= ph <= 7.4:
                status = "Ideal"
                self.ph_value_label.config(foreground="green")
            elif 6.5 <= ph < 6.8 or 7.4 < ph <= 7.8:
                status = "Acceptable"
                self.ph_value_label.config(foreground="orange")
            else:
                status = "Out of range"
                self.ph_value_label.config(foreground="red")
            
            self.ph_status_var.set(status)
        
        if 'temp' in data:
            temp = data['temp']
            self.temp_value_var.set(f"{temp:.1f}")
            self.temp_gauge['value'] = (temp / 50.0) * 100
            
            if 24 <= temp <= 30:
                status = "Ideal"
                self.temp_value_label.config(foreground="green")
            elif 20 <= temp < 24 or 30 < temp <= 35:
                status = "Acceptable"
                self.temp_value_label.config(foreground="orange")
            else:
                status = "Out of range"
                self.temp_value_label.config(foreground="red")
            
            self.temp_status_var.set(status)
        
        if 'orp' in data:
            orp = data['orp']
            self.orp_value_var.set(f"{orp}")
            self.orp_gauge['value'] = (orp / 1000.0) * 100
            
            if 650 <= orp <= 750:
                status = "Ideal"
                self.orp_value_label.config(foreground="green")
            elif 600 <= orp < 650 or 750 < orp <= 800:
                status = "Acceptable"
                self.orp_value_label.config(foreground="orange")
            else:
                status = "Out of range"
                self.orp_value_label.config(foreground="red")
            
            self.orp_status_var.set(status)
        
        if 'tds' in data:
            tds = data['tds']
            self.tds_value_var.set(f"{tds}")
            self.tds_gauge['value'] = (tds / 1000.0) * 100
            
            if tds <= 500:
                status = "Ideal"
                self.tds_value_label.config(foreground="green")
            elif 500 < tds <= 800:
                status = "Acceptable"
                self.tds_value_label.config(foreground="orange")
            else:
                status = "High"
                self.tds_value_label.config(foreground="red")
            
            self.tds_status_var.set(status)
        
        if 'turb' in data:
            turb = data['turb']
            self.turb_value_var.set(f"{turb:.2f}")
            self.turb_gauge['value'] = (turb / 10.0) * 100
            
            if turb <= 1.0:
                status = "Ideal"
                self.turb_value_label.config(foreground="green")
            elif 1.0 < turb <= 3.0:
                status = "Acceptable"
                self.turb_value_label.config(foreground="orange")
            else:
                status = "High"
                self.turb_value_label.config(foreground="red")
            
            self.turb_status_var.set(status)
        
        # Update graphs if we have data
        if self.data_history['timestamp']:
            self._update_graphs()
    
    def _update_graphs(self):
        """Update the graphs with the latest data."""
        # Convert timestamps to matplotlib format
        dates = mdates.date2num(self.data_history['timestamp'])
        
        # Update each plot
        self.ph_line.set_data(dates, self.data_history['pH'])
        self.temp_line.set_data(dates, self.data_history['temp'])
        self.orp_line.set_data(dates, self.data_history['orp'])
        self.tds_line.set_data(dates, self.data_history['tds'])
        self.turb_line.set_data(dates, self.data_history['turb'])
        
        # Update x-axis limits
        for ax in [self.ax1, self.ax2, self.ax3, self.ax4, self.ax5]:
            ax.set_xlim(min(dates), max(dates))
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
            ax.xaxis.set_major_locator(mdates.AutoDateLocator())
            for label in ax.get_xticklabels():
                label.set_rotation(45)
        
        # Redraw the figure
        self.fig.tight_layout()
        self.canvas.draw()
    
    def _generate_recommendations(self, data):
        """Generate recommendations based on sensor data."""
        if not data:
            return
        
        recommendations = []
        
        # pH recommendations
        if 'pH' in data:
            ph = data['pH']
            if ph < 6.5:
                recommendations.append(f"pH is low ({ph:.2f}). Add pH increaser.")
            elif ph > 7.8:
                recommendations.append(f"pH is high ({ph:.2f}). Add pH decreaser.")
            else:
                recommendations.append(f"pH is good ({ph:.2f}).")
        
        # ORP recommendations
        if 'orp' in data:
            orp = data['orp']
            if orp < 600:
                recommendations.append(f"ORP is low ({orp} mV). Add chlorine or other sanitizer.")
            elif orp > 800:
                recommendations.append(f"ORP is high ({orp} mV). Reduce sanitizer level.")
            else:
                recommendations.append(f"ORP is good ({orp} mV).")
        
        # TDS recommendations
        if 'tds' in data:
            tds = data['tds']
            if tds > 800:
                recommendations.append(f"TDS is high ({tds} ppm). Consider partial water replacement.")
            else:
                recommendations.append(f"TDS is acceptable ({tds} ppm).")
        
        # Turbidity recommendations
        if 'turb' in data:
            turb = data['turb']
            if turb > 3.0:
                recommendations.append(f"Water is cloudy ({turb:.2f} NTU). Check filtration and add clarifier.")
            else:
                recommendations.append(f"Water clarity is good ({turb:.2f} NTU).")
        
        # Update recommendations text
        if recommendations:
            self.recommendations_text.config(state=tk.NORMAL)
            self.recommendations_text.delete(1.0, tk.END)
            self.recommendations_text.insert(tk.END, "\
".join(recommendations))
            self.recommendations_text.config(state=tk.DISABLED)
    
    def _set_history_size(self, size):
        """Set the maximum history size."""
        if size < 10:
            messagebox.showwarning("Warning", "History size must be at least 10 points")
            self.history_var.set("10")
            size = 10
        
        self.max_history_points = size
        
        # Trim history if needed
        if len(self.data_history['timestamp']) > size:
            self.data_history['timestamp'] = self.data_history['timestamp'][-size:]
            self.data_history['pH'] = self.data_history['pH'][-size:]
            self.data_history['temp'] = self.data_history['temp'][-size:]
            self.data_history['orp'] = self.data_history['orp'][-size:]
            self.data_history['tds'] = self.data_history['tds'][-size:]
            self.data_history['turb'] = self.data_history['turb'][-size:]
        
        self.status_message.set(f"History size set to {size} points")
    
    def _clear_history(self):
        """Clear the data history."""
        self.data_history = {
            'timestamp': [],
            'pH': [],
            'temp': [],
            'orp': [],
            'tds': [],
            'turb': []
        }
        
        # Clear plots
        self.ph_line.set_data([], [])
        self.temp_line.set_data([], [])
        self.orp_line.set_data([], [])
        self.tds_line.set_data([], [])
        self.turb_line.set_data([], [])
        
        # Redraw the figure
        self.canvas.draw()
        
        self.status_message.set("History cleared")
    
    def _export_data(self):
        """Export the data history to a CSV file."""
        if not self.data_history['timestamp']:
            messagebox.showwarning("Warning", "No data to export")
            return
        
        # Ask for file location
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Export Data"
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, 'w') as f:
                # Write header
                f.write("Timestamp,pH,Temperature,ORP,TDS,Turbidity\
")
                
                # Write data
                for i in range(len(self.data_history['timestamp'])):
                    timestamp = self.data_history['timestamp'][i].strftime('%Y-%m-%d %H:%M:%S')
                    ph = self.data_history['pH'][i] if self.data_history['pH'][i] is not None else ""
                    temp = self.data_history['temp'][i] if self.data_history['temp'][i] is not None else ""
                    orp = self.data_history['orp'][i] if self.data_history['orp'][i] is not None else ""
                    tds = self.data_history['tds'][i] if self.data_history['tds'][i] is not None else ""
                    turb = self.data_history['turb'][i] if self.data_history['turb'][i] is not None else ""
                    
                    f.write(f"{timestamp},{ph},{temp},{orp},{tds},{turb}\
")
            
            self.status_message.set(f"Data exported to {file_path}")
            messagebox.showinfo("Export Successful", f"Data exported to {file_path}")
        except Exception as e:
            self.logger.error(f"Error exporting data: {e}")
            messagebox.showerror("Export Error", f"Error exporting data: {e}")
    
    def _calibrate_sensor(self, sensor, value):
        """Calibrate a sensor."""
        if not self.arduino.connected:
            messagebox.showerror("Error", "Arduino not connected")
            return
        
        if self.arduino.calibrate_sensor(sensor, value):
            self.status_message.set(f"Calibrating {sensor} sensor to {value}")
            messagebox.showinfo("Calibration", f"Calibrating {sensor} sensor to {value}")
        else:
            messagebox.showerror("Error", f"Failed to calibrate {sensor} sensor")
    
    def _set_update_interval(self, interval):
        """Set the update interval for sensor readings."""
        if not self.arduino.connected:
            messagebox.showerror("Error", "Arduino not connected")
            return
        
        if interval < 100:
            messagebox.showwarning("Warning", "Interval must be at least 100 ms")
            self.interval_var.set("100")
            interval = 100
        
        if self.arduino.set_update_interval(interval):
            self.status_message.set(f"Update interval set to {interval} ms")
        else:
            messagebox.showerror("Error", "Failed to set update interval")
    
    def _toggle_logging(self):
        """Toggle data logging to file."""
        self.logging_enabled = self.logging_var.get()
        
        if self.logging_enabled:
            self.log_file = self.log_file_var.get()
            
            # Create log file with header if it doesn't exist
            if not os.path.exists(self.log_file):
                try:
                    with open(self.log_file, 'w') as f:
                        f.write("Timestamp,pH,Temperature,ORP,TDS,Turbidity\
")
                except Exception as e:
                    self.logger.error(f"Error creating log file: {e}")
                    messagebox.showerror("Error", f"Error creating log file: {e}")
                    self.logging_var.set(False)
                    self.logging_enabled = False
                    return
            
            self.status_message.set(f"Logging enabled to {self.log_file}")
        else:
            self.status_message.set("Logging disabled")
    
    def _log_data(self, timestamp, data):
        """Log data to file."""
        if not hasattr(self, 'log_file'):
            return
        
        try:
            with open(self.log_file, 'a') as f:
                timestamp_str = timestamp.strftime('%Y-%m-%d %H:%M:%S')
                ph = data.get('pH', "")
                temp = data.get('temp', "")
                orp = data.get('orp', "")
                tds = data.get('tds', "")
                turb = data.get('turb', "")
                
                f.write(f"{timestamp_str},{ph},{temp},{orp},{tds},{turb}\
")
        except Exception as e:
            self.logger.error(f"Error logging data: {e}")
            # Disable logging on error
            self.logging_var.set(False)
            self.logging_enabled = False
            messagebox.showerror("Error", f"Error logging data: {e}")
    
    def _browse_log_file(self):
        """Browse for log file location."""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Select Log File"
        )
        
        if file_path:
            self.log_file_var.set(file_path)
    
    def _start_ui_updates(self):
        """Start periodic UI updates."""
        def update_loop():
            while True:
                try:
                    # Update UI
                    self._update_ui()
                    
                    # Sleep for a short time
                    time.sleep(0.5)
                except Exception as e:
                    self.logger.error(f"Error in UI update loop: {e}")
        
        # Start update thread
        self.update_thread = threading.Thread(target=update_loop)
        self.update_thread.daemon = True
        self.update_thread.start()
    
    def run(self):
        """Run the application."""
        if self.standalone:
            self.root.mainloop()


# Example usage
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create and run the application
    app = ArduinoMonitorApp()
    app.run()
