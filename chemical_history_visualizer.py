
#!/usr/bin/env python3
"""
Chemical History Visualizer for Deep Blue Pool Chemistry application.

This module provides functionality for visualizing historical chemical data.
"""

import os
import logging
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
import tkinter as tk
from tkinter import ttk

# Configure logger
logger = logging.getLogger(__name__)

class ChemicalHistoryVisualizer:
    """
    Chemical history visualizer for pool water chemistry.
    
    This class provides functionality for visualizing historical chemical data
    using matplotlib charts embedded in the Tkinter interface.
    
    Attributes:
        db_service: Database service for retrieving data
        parent: Parent Tkinter widget
    """
    
    def __init__(self, db_service, parent: Optional[tk.Widget] = None):
        """
        Initialize the chemical history visualizer.
        
        Args:
            db_service: Database service instance
            parent: Parent Tkinter widget
        """
        self.db_service = db_service
        self.parent = parent
        self.logger = logging.getLogger(__name__)
        self.logger.info("Chemical History Visualizer initialized")
        
        # Define ideal ranges
        self.ideal_ranges = {
            "pH": (7.2, 7.8),
            "free_chlorine": (1.0, 3.0),
            "total_chlorine": (1.0, 3.0),
            "alkalinity": (80, 120),
            "calcium": (200, 400),
            "cyanuric_acid": (30, 50),
            "temperature": (75, 85)
        }
        
        # Create main frame if parent is provided
        if parent:
            self.main_frame = ttk.Frame(parent)
            self.main_frame.pack(fill=tk.BOTH, expand=True)
            
            # Create controls frame
            self.controls_frame = ttk.Frame(self.main_frame)
            self.controls_frame.pack(fill=tk.X, padx=10, pady=5)
            
            # Add customer selection
            ttk.Label(self.controls_frame, text="Customer:").pack(side=tk.LEFT, padx=5)
            
            self.customer_var = tk.StringVar()
            self.customer_combo = ttk.Combobox(self.controls_frame, textvariable=self.customer_var, width=30)
            self.customer_combo.pack(side=tk.LEFT, padx=5)
            
            # Add time range selection
            ttk.Label(self.controls_frame, text="Time Range:").pack(side=tk.LEFT, padx=5)
            
            self.time_range_var = tk.StringVar(value="30 days")
            self.time_range_combo = ttk.Combobox(self.controls_frame, textvariable=self.time_range_var, 
                                               values=["7 days", "30 days", "90 days", "1 year"], width=10)
            self.time_range_combo.pack(side=tk.LEFT, padx=5)
            
            # Add parameter selection
            ttk.Label(self.controls_frame, text="Parameters:").pack(side=tk.LEFT, padx=5)
            
            self.ph_var = tk.BooleanVar(value=True)
            ttk.Checkbutton(self.controls_frame, text="pH", variable=self.ph_var).pack(side=tk.LEFT)
            
            self.chlorine_var = tk.BooleanVar(value=True)
            ttk.Checkbutton(self.controls_frame, text="Chlorine", variable=self.chlorine_var).pack(side=tk.LEFT)
            
            self.alkalinity_var = tk.BooleanVar(value=True)
            ttk.Checkbutton(self.controls_frame, text="Alkalinity", variable=self.alkalinity_var).pack(side=tk.LEFT)
            
            self.calcium_var = tk.BooleanVar(value=False)
            ttk.Checkbutton(self.controls_frame, text="Calcium", variable=self.calcium_var).pack(side=tk.LEFT)
            
            # Add refresh button
            ttk.Button(self.controls_frame, text="Refresh", command=self.refresh_chart).pack(side=tk.RIGHT, padx=5)
            
            # Add export button
            ttk.Button(self.controls_frame, text="Export Data", command=self.export_data).pack(side=tk.RIGHT, padx=5)
            
            # Create chart frame
            self.chart_frame = ttk.Frame(self.main_frame)
            self.chart_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # Create figure for chart
            self.fig = Figure(figsize=(8, 5), dpi=100)
            
            # Create canvas for chart
            self.canvas = FigureCanvasTkAgg(self.fig, master=self.chart_frame)
            self.canvas.draw()
            self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            
            # Initialize chart
            self.initialize_chart()
            
            # Populate customer combo
            self.populate_customer_combo()
            
            # Bind events
            self.customer_combo.bind("<<ComboboxSelected>>", lambda e: self.refresh_chart())
            self.time_range_combo.bind("<<ComboboxSelected>>", lambda e: self.refresh_chart())
            self.ph_var.trace("w", lambda *args: self.refresh_chart())
            self.chlorine_var.trace("w", lambda *args: self.refresh_chart())
            self.alkalinity_var.trace("w", lambda *args: self.refresh_chart())
            self.calcium_var.trace("w", lambda *args: self.refresh_chart())
    
    def populate_customer_combo(self):
        """Populate the customer combo box."""
        try:
            customers = self.db_service.get_all_customers()
            
            customer_options = ["All Customers"]
            for customer in customers:
                customer_options.append(f"{customer['id']}: {customer['name']}")
            
            self.customer_combo["values"] = customer_options
            self.customer_combo.current(0)
        except Exception as e:
            self.logger.error(f"Error populating customer combo: {e}")
    
    def initialize_chart(self):
        """Initialize the chart."""
        # Clear the figure
        self.fig.clear()
        
        # Create subplots with shared x-axis
        self.axes = []
        
        # pH subplot
        ax1 = self.fig.add_subplot(411)
        ax1.set_title("Chemical History")
        ax1.set_ylabel("pH")
        ax1.grid(True)
        self.axes.append(ax1)
        
        # Chlorine subplot
        ax2 = self.fig.add_subplot(412, sharex=ax1)
        ax2.set_ylabel("Chlorine (ppm)")
        ax2.grid(True)
        self.axes.append(ax2)
        
        # Alkalinity subplot
        ax3 = self.fig.add_subplot(413, sharex=ax1)
        ax3.set_ylabel("Alkalinity (ppm)")
        ax3.grid(True)
        self.axes.append(ax3)
        
        # Calcium subplot
        ax4 = self.fig.add_subplot(414, sharex=ax1)
        ax4.set_ylabel("Calcium (ppm)")
        ax4.set_xlabel("Date")
        ax4.grid(True)
        self.axes.append(ax4)
        
        # Format x-axis dates
        for ax in self.axes:
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
            ax.xaxis.set_major_locator(mdates.AutoDateLocator())
        
        # Adjust layout
        self.fig.tight_layout()
        self.canvas.draw()
    
    def refresh_chart(self):
        """Refresh the chart with current data."""
        try:
            # Get selected customer ID
            customer_id = None
            if self.customer_var.get() and self.customer_var.get() != "All Customers":
                try:
                    customer_id = int(self.customer_var.get().split(":")[0])
                except:
                    pass
            
            # Get selected time range
            time_range = self.time_range_var.get()
            days = 30  # Default
            
            if time_range == "7 days":
                days = 7
            elif time_range == "30 days":
                days = 30
            elif time_range == "90 days":
                days = 90
            elif time_range == "1 year":
                days = 365
            
            # Get historical data
            data = self.get_historical_data(customer_id, days)
            
            # Clear the figure
            self.fig.clear()
            
            # Create new axes based on selected parameters
            self.axes = []
            num_plots = sum([
                self.ph_var.get(),
                self.chlorine_var.get(),
                self.alkalinity_var.get(),
                self.calcium_var.get()
            ])
            
            if num_plots == 0:
                # No parameters selected, show message
                ax = self.fig.add_subplot(111)
                ax.text(0.5, 0.5, "No parameters selected", ha="center", va="center", fontsize=14)
                ax.axis("off")
                self.axes.append(ax)
            else:
                # Create subplots for selected parameters
                plot_index = 1
                
                if self.ph_var.get():
                    ax = self.fig.add_subplot(num_plots, 1, plot_index)
                    if plot_index == 1:
                        ax.set_title("Chemical History")
                    ax.set_ylabel("pH")
                    ax.grid(True)
                    
                    # Plot pH data
                    if data["dates"] and data["ph_values"]:
                        # Convert string dates to datetime objects
                        dates = [datetime.strptime(d, "%Y-%m-%d") for d in data["dates"]]
                        
                        # Plot data
                        ax.plot(dates, data["ph_values"], "b-", marker="o", label="pH")
                        
                        # Plot ideal range
                        ph_min, ph_max = self.ideal_ranges["pH"]
                        ax.axhspan(ph_min, ph_max, alpha=0.2, color="green")
                        
                        # Set y-axis limits
                        ax.set_ylim(min(6.0, min(data["ph_values"])) - 0.2, max(8.4, max(data["ph_values"])) + 0.2)
                    
                    self.axes.append(ax)
                    plot_index += 1
                
                if self.chlorine_var.get():
                    ax = self.fig.add_subplot(num_plots, 1, plot_index)
                    if plot_index == 1:
                        ax.set_title("Chemical History")
                    ax.set_ylabel("Chlorine (ppm)")
                    ax.grid(True)
                    
                    # Plot chlorine data
                    if data["dates"] and data["chlorine_values"]:
                        # Convert string dates to datetime objects
                        dates = [datetime.strptime(d, "%Y-%m-%d") for d in data["dates"]]
                        
                        # Plot data
                        ax.plot(dates, data["chlorine_values"], "g-", marker="o", label="Free Chlorine")
                        
                        # Plot ideal range
                        cl_min, cl_max = self.ideal_ranges["free_chlorine"]
                        ax.axhspan(cl_min, cl_max, alpha=0.2, color="green")
                        
                        # Set y-axis limits
                        ax.set_ylim(0, max(5.0, max(data["chlorine_values"])) + 0.5)
                    
                    self.axes.append(ax)
                    plot_index += 1
                
                if self.alkalinity_var.get():
                    ax = self.fig.add_subplot(num_plots, 1, plot_index)
                    if plot_index == 1:
                        ax.set_title("Chemical History")
                    ax.set_ylabel("Alkalinity (ppm)")
                    ax.grid(True)
                    
                    # Plot alkalinity data
                    if data["dates"] and data["alkalinity_values"]:
                        # Convert string dates to datetime objects
                        dates = [datetime.strptime(d, "%Y-%m-%d") for d in data["dates"]]
                        
                        # Plot data
                        ax.plot(dates, data["alkalinity_values"], "r-", marker="o", label="Alkalinity")
                        
                        # Plot ideal range
                        alk_min, alk_max = self.ideal_ranges["alkalinity"]
                        ax.axhspan(alk_min, alk_max, alpha=0.2, color="green")
                        
                        # Set y-axis limits
                        ax.set_ylim(min(60, min(data["alkalinity_values"])) - 10, max(180, max(data["alkalinity_values"])) + 10)
                    
                    self.axes.append(ax)
                    plot_index += 1
                
                if self.calcium_var.get():
                    ax = self.fig.add_subplot(num_plots, 1, plot_index)
                    if plot_index == 1:
                        ax.set_title("Chemical History")
                    ax.set_ylabel("Calcium (ppm)")
                    ax.grid(True)
                    
                    # Plot calcium data
                    if data["dates"] and data["calcium_values"]:
                        # Convert string dates to datetime objects
                        dates = [datetime.strptime(d, "%Y-%m-%d") for d in data["dates"]]
                        
                        # Plot data
                        ax.plot(dates, data["calcium_values"], "m-", marker="o", label="Calcium")
                        
                        # Plot ideal range
                        cal_min, cal_max = self.ideal_ranges["calcium"]
                        ax.axhspan(cal_min, cal_max, alpha=0.2, color="green")
                        
                        # Set y-axis limits
                        ax.set_ylim(min(150, min(data["calcium_values"])) - 20, max(450, max(data["calcium_values"])) + 20)
                    
                    self.axes.append(ax)
                    plot_index += 1
                
                # Set x-axis label on the bottom subplot
                if self.axes:
                    self.axes[-1].set_xlabel("Date")
                
                # Format x-axis dates on all subplots
                for ax in self.axes:
                    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
                    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
                    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha="right")
            
            # Adjust layout
            self.fig.tight_layout()
            self.canvas.draw()
        
        except Exception as e:
            self.logger.error(f"Error refreshing chart: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
    
    def get_historical_data(self, customer_id: Optional[int] = None, days: int = 30) -> Dict[str, Any]:
        """
        Get historical chemical data for visualization.
        
        Args:
            customer_id: Optional customer ID to filter data
            days: Number of days of history to retrieve
            
        Returns:
            Dictionary containing historical data for visualization
        """
        try:
            # Get readings from database
            if customer_id:
                readings = self.db_service.get_customer_readings(customer_id, limit=100)
            else:
                readings = self.db_service.get_recent_readings(limit=100)
            
            # Filter readings by date
            from datetime import datetime, timedelta
            cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            filtered_readings = [
                reading for reading in readings
                if reading.get("timestamp", "") >= cutoff_date
            ]
            
            # Extract data for visualization
            dates = []
            ph_values = []
            chlorine_values = []
            alkalinity_values = []
            calcium_values = []
            
            for reading in filtered_readings:
                # Parse timestamp
                try:
                    timestamp = datetime.fromisoformat(reading.get("timestamp", ""))
                    date_str = timestamp.strftime("%Y-%m-%d")
                    dates.append(date_str)
                except (ValueError, TypeError):
                    continue
                
                # Extract values
                try:
                    ph_values.append(float(reading.get("pH", 0)))
                except (ValueError, TypeError):
                    ph_values.append(None)
                
                try:
                    chlorine_values.append(float(reading.get("free_chlorine", 0)))
                except (ValueError, TypeError):
                    chlorine_values.append(None)
                
                try:
                    alkalinity_values.append(float(reading.get("alkalinity", 0)))
                except (ValueError, TypeError):
                    alkalinity_values.append(None)
                
                try:
                    calcium_values.append(float(reading.get("calcium", 0)))
                except (ValueError, TypeError):
                    calcium_values.append(None)
            
            # Create result dictionary
            result = {
                "dates": dates,
                "ph_values": ph_values,
                "chlorine_values": chlorine_values,
                "alkalinity_values": alkalinity_values,
                "calcium_values": calcium_values
            }
            
            return result
        except Exception as e:
            self.logger.error(f"Error getting historical data: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            return {
                "dates": [],
                "ph_values": [],
                "chlorine_values": [],
                "alkalinity_values": [],
                "calcium_values": []
            }
    
    def export_data(self):
        """Export data to CSV or JSON file."""
        try:
            # Get selected customer ID
            customer_id = None
            if self.customer_var.get() and self.customer_var.get() != "All Customers":
                try:
                    customer_id = int(self.customer_var.get().split(":")[0])
                except:
                    pass
            
            # Get selected time range
            time_range = self.time_range_var.get()
            days = 30  # Default
            
            if time_range == "7 days":
                days = 7
            elif time_range == "30 days":
                days = 30
            elif time_range == "90 days":
                days = 90
            elif time_range == "1 year":
                days = 365
            
            # Create export directory if it doesn't exist
            export_dir = "data/exports"
            os.makedirs(export_dir, exist_ok=True)
            
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            customer_str = f"_customer_{customer_id}" if customer_id else ""
            filename = f"{export_dir}/pool_data{customer_str}_{timestamp}.csv"
            
            # Get readings from database
            if customer_id:
                readings = self.db_service.get_customer_readings(customer_id, limit=1000)
                # Get customer info
                customer = self.db_service.get_customer(customer_id)
                customer_name = customer["name"] if customer else f"Customer {customer_id}"
            else:
                readings = self.db_service.get_recent_readings(limit=1000)
                customer_name = "All Customers"
            
            # Filter readings by date
            from datetime import datetime, timedelta
            cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            filtered_readings = [
                reading for reading in readings
                if reading.get("timestamp", "") >= cutoff_date
            ]
            
            # Export to CSV
            import csv
            
            with open(filename, "w", newline="") as f:
                # Define CSV headers
                headers = [
                    "Date", "Time", "Customer", "pH", "Free Chlorine", "Total Chlorine",
                    "Alkalinity", "Calcium", "Cyanuric Acid", "Temperature", "Source"
                ]
                
                writer = csv.writer(f)
                writer.writerow(headers)
                
                # Write data rows
                for reading in filtered_readings:
                    # Parse timestamp
                    try:
                        timestamp = datetime.fromisoformat(reading.get("timestamp", ""))
                        date_str = timestamp.strftime("%Y-%m-%d")
                        time_str = timestamp.strftime("%H:%M:%S")
                    except (ValueError, TypeError):
                        date_str = "Unknown"
                        time_str = "Unknown"
                    
                    # Write row
                    writer.writerow([
                        date_str,
                        time_str,
                        customer_name,
                        reading.get("pH", ""),
                        reading.get("free_chlorine", ""),
                        reading.get("total_chlorine", ""),
                        reading.get("alkalinity", ""),
                        reading.get("calcium", ""),
                        reading.get("cyanuric_acid", ""),
                        reading.get("temperature", ""),
                        reading.get("source", "")
                    ])
            
            # Show success message
            from tkinter import messagebox
            messagebox.showinfo("Export Successful", f"Data exported to {filename}")
            
            return filename
        except Exception as e:
            self.logger.error(f"Error exporting data: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            
            # Show error message
            from tkinter import messagebox
            messagebox.showerror("Export Failed", f"Failed to export data: {e}")
            
            return ""

# For testing
if __name__ == "__main__":
    # Create root window
    root = tk.Tk()
    root.title("Chemical History Visualizer Test")
    root.geometry("800x600")
    
    # Import database service
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from database_service import DatabaseService
    
    # Create database service
    db_service = DatabaseService("data/pool_data.db")
    
    # Create visualizer
    visualizer = ChemicalHistoryVisualizer(db_service, root)
    
    # Run the application
    root.mainloop()
