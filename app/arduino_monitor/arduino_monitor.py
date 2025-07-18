
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
        
        # Add connection frame
        connection_frame = ttk.LabelFrame(self.main_frame, text="Connection")
        connection_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Add port selection
        ttk.Label(connection_frame, text="Port:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.port_var = tk.StringVar()
        self.port_combo = ttk.Combobox(connection_frame, textvariable=self.port_var)
        self.port_combo.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        
        # Add refresh button
        ttk.Button(connection_frame, text="Refresh Ports", command=self.refresh_ports).grid(row=0, column=2, padx=5, pady=5)
        
        # Add connect button
        self.connect_button = ttk.Button(connection_frame, text="Connect", command=self.connect)
        self.connect_button.grid(row=0, column=3, padx=5, pady=5)
        
        # Add sensor data frame
        sensor_frame = ttk.LabelFrame(self.main_frame, text="Sensor Data")
        sensor_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
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
        self.sensor_tree.insert("", tk.END, iid="temperature", text="Temperature", values=("N/A", "\u00b0F", "N/A"))
        self.sensor_tree.insert("", tk.END, iid="tds", text="TDS", values=("N/A", "ppm", "N/A"))
        
        # Add chart frame
        chart_frame = ttk.LabelFrame(self.main_frame, text="Sensor Chart")
        chart_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Create figure and canvas
        self.fig = Figure(figsize=(5, 4), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=chart_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Initialize chart
        self.initialize_chart()
        
        # Add control frame
        control_frame = ttk.Frame(self.main_frame)
        control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Add start/stop button
        self.running = False
        self.start_stop_var = tk.StringVar(value="Start Monitoring")
        self.start_stop_button = ttk.Button(control_frame, textvariable=self.start_stop_var, command=self.toggle_monitoring)
        self.start_stop_button.pack(side=tk.LEFT, padx=5)
        
        # Add export button
        ttk.Button(control_frame, text="Export Data", command=self.export_data).pack(side=tk.LEFT, padx=5)
        
        # Add clear button
        ttk.Button(control_frame, text="Clear Data", command=self.clear_data).pack(side=tk.LEFT, padx=5)
        
        # Initialize data
        self.data = {
            "ph": [],
            "orp": [],
            "temperature": [],
            "tds": []
        }
        self.timestamps = []
        
        # Refresh ports
        self.refresh_ports()
        
        self.logger.info("Arduino Monitor initialized")
    
    def refresh_ports(self):
        """Refresh available serial ports."""
        try:
            # This is a placeholder - in a real implementation, we would use serial.tools.list_ports
            # to get the actual list of available ports
            ports = ["COM1", "COM2", "COM3", "/dev/ttyUSB0", "/dev/ttyUSB1"]
            self.port_combo["values"] = ports
            if ports:
                self.port_combo.current(0)
            self.logger.info(f"Found {len(ports)} serial ports")
        except Exception as e:
            self.logger.error(f"Error refreshing ports: {e}")
            messagebox.showerror("Error", f"Failed to refresh ports: {e}")
    
    def connect(self):
        """Connect to the selected serial port."""
        port = self.port_var.get()
        if not port:
            messagebox.showerror("Error", "No port selected")
            return
        
        try:
            # This is a placeholder - in a real implementation, we would use serial.Serial
            # to connect to the actual port
            self.status_var.set(f"Connected to {port}")
            self.connect_button.config(text="Disconnect", command=self.disconnect)
            self.logger.info(f"Connected to {port}")
            messagebox.showinfo("Connected", f"Successfully connected to {port}")
        except Exception as e:
            self.logger.error(f"Error connecting to {port}: {e}")
            messagebox.showerror("Error", f"Failed to connect to {port}: {e}")
    
    def disconnect(self):
        """Disconnect from the serial port."""
        try:
            # This is a placeholder - in a real implementation, we would close the serial connection
            self.status_var.set("Arduino Monitor is not connected")
            self.connect_button.config(text="Connect", command=self.connect)
            self.logger.info("Disconnected")
            
            # Stop monitoring if running
            if self.running:
                self.toggle_monitoring()
        except Exception as e:
            self.logger.error(f"Error disconnecting: {e}")
            messagebox.showerror("Error", f"Failed to disconnect: {e}")
    
    def initialize_chart(self):
        """Initialize the chart."""
        self.ax.clear()
        self.ax.set_title("Sensor Data")
        self.ax.set_xlabel("Time")
        self.ax.set_ylabel("Value")
        self.ax.grid(True)
        self.fig.tight_layout()
        self.canvas.draw()
    
    def update_chart(self):
        """Update the chart with new data."""
        try:
            self.ax.clear()
            
            # Plot data if available
            if self.timestamps:
                # Convert timestamps to datetime objects
                times = [datetime.fromisoformat(ts) for ts in self.timestamps]
                
                # Plot each sensor
                if self.data["ph"]:
                    self.ax.plot(times, self.data["ph"], label="pH", marker="o")
                
                if self.data["temperature"]:
                    self.ax.plot(times, self.data["temperature"], label="Temperature", marker="s")
                
                if self.data["orp"]:
                    self.ax.plot(times, self.data["orp"], label="ORP", marker="^")
                
                if self.data["tds"]:
                    self.ax.plot(times, self.data["tds"], label="TDS", marker="x")
                
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
            self.logger.error(f"Error updating chart: {e}")
    
    def toggle_monitoring(self):
        """Toggle sensor monitoring."""
        if not self.running:
            # Start monitoring
            self.running = True
            self.start_stop_var.set("Stop Monitoring")
            self.monitoring_thread = threading.Thread(target=self.monitor_sensors)
            self.monitoring_thread.daemon = True
            self.monitoring_thread.start()
            self.logger.info("Started monitoring")
        else:
            # Stop monitoring
            self.running = False
            self.start_stop_var.set("Start Monitoring")
            self.logger.info("Stopped monitoring")
    
    def monitor_sensors(self):
        """Monitor sensors in a separate thread."""
        while self.running:
            try:
                # This is a placeholder - in a real implementation, we would read actual data from the serial port
                # Generate some random data for demonstration
                timestamp = datetime.now().isoformat()
                ph = round(np.random.uniform(6.5, 8.0), 1)
                orp = round(np.random.uniform(650, 750))
                temperature = round(np.random.uniform(75, 85), 1)
                tds = round(np.random.uniform(300, 500))
                
                # Update data
                self.data["ph"].append(ph)
                self.data["orp"].append(orp)
                self.data["temperature"].append(temperature)
                self.data["tds"].append(tds)
                self.timestamps.append(timestamp)
                
                # Keep only the last 20 data points
                if len(self.timestamps) > 20:
                    self.data["ph"] = self.data["ph"][-20:]
                    self.data["orp"] = self.data["orp"][-20:]
                    self.data["temperature"] = self.data["temperature"][-20:]
                    self.data["tds"] = self.data["tds"][-20:]
                    self.timestamps = self.timestamps[-20:]
                
                # Update UI in the main thread
                self.parent.after(0, self.update_ui, ph, orp, temperature, tds, timestamp)
                
                # Sleep for a bit
                time.sleep(2)
            except Exception as e:
                self.logger.error(f"Error monitoring sensors: {e}")
                self.running = False
                break
    
    def update_ui(self, ph, orp, temperature, tds, timestamp):
        """Update the UI with new sensor data."""
        try:
            # Update tree view
            self.sensor_tree.item("ph", values=(ph, "pH", timestamp))
            self.sensor_tree.item("orp", values=(orp, "mV", timestamp))
            self.sensor_tree.item("temperature", values=(temperature, "\u00b0F", timestamp))
            self.sensor_tree.item("tds", values=(tds, "ppm", timestamp))
            
            # Update chart
            self.update_chart()
        except Exception as e:
            self.logger.error(f"Error updating UI: {e}")
    
    def export_data(self):
        """Export sensor data to a CSV file."""
        try:
            if not self.timestamps:
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
                f.write("Timestamp,pH,ORP (mV),Temperature (\u00b0F),TDS (ppm)\
")
                
                # Write data
                for i in range(len(self.timestamps)):
                    f.write(f"{self.timestamps[i]},{self.data['ph'][i]},{self.data['orp'][i]},{self.data['temperature'][i]},{self.data['tds'][i]}\
")
            
            self.logger.info(f"Exported data to {file_path}")
            messagebox.showinfo("Export", f"Data exported to {file_path}")
        except Exception as e:
            self.logger.error(f"Error exporting data: {e}")
            messagebox.showerror("Error", f"Failed to export data: {e}")
    
    def clear_data(self):
        """Clear all sensor data."""
        try:
            # Clear data
            self.data = {
                "ph": [],
                "orp": [],
                "temperature": [],
                "tds": []
            }
            self.timestamps = []
            
            # Update tree view
            self.sensor_tree.item("ph", values=("N/A", "pH", "N/A"))
            self.sensor_tree.item("orp", values=("N/A", "mV", "N/A"))
            self.sensor_tree.item("temperature", values=("N/A", "\u00b0F", "N/A"))
            self.sensor_tree.item("tds", values=("N/A", "ppm", "N/A"))
            
            # Update chart
            self.initialize_chart()
            
            self.logger.info("Cleared all data")
        except Exception as e:
            self.logger.error(f"Error clearing data: {e}")
            messagebox.showerror("Error", f"Failed to clear data: {e}")

# For testing as standalone
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Arduino Sensor Monitor")
    root.geometry("800x600")
    app = ArduinoMonitorApp(root)
    root.mainloop()
