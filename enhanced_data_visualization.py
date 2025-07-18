
#!/usr/bin/env python3
"""
Enhanced Data Visualization for Deep Blue Pool Chemistry application.

This module provides enhanced data visualization capabilities with more chart types,
interactive filtering options, and trend analysis for chemical readings.
"""

import os
import sys
import logging
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import matplotlib.dates as mdates
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import json

# Configure logger
logger = logging.getLogger(__name__)

class EnhancedDataVisualization:
    """
    Enhanced data visualization for pool water chemistry.
    
    This class provides enhanced data visualization capabilities with:
    - Multiple chart types (line, bar, scatter, heatmap)
    - Interactive filtering options
    - Trend analysis for chemical readings
    - Printable reports
    
    Attributes:
        db_service: Database service for retrieving data
        parent: Parent Tkinter widget
    """
    
    def __init__(self, db_service, parent: Optional[tk.Widget] = None):
        """
        Initialize the enhanced data visualization.
        
        Args:
            db_service: Database service instance
            parent: Parent Tkinter widget
        """
        self.db_service = db_service
        self.parent = parent
        self.logger = logging.getLogger(__name__)
        self.logger.info("Enhanced Data Visualization initialized")
        
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
            self.create_ui()
    
    def create_ui(self):
        """Create the user interface."""
        self.main_frame = ttk.Frame(self.parent)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create controls frame
        self.controls_frame = ttk.Frame(self.main_frame)
        self.controls_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Create left controls (customer and time range)
        left_controls = ttk.Frame(self.controls_frame)
        left_controls.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Add customer selection
        ttk.Label(left_controls, text="Customer:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        
        self.customer_var = tk.StringVar()
        self.customer_combo = ttk.Combobox(left_controls, textvariable=self.customer_var, width=30)
        self.customer_combo.grid(row=0, column=1, sticky="ew", padx=5, pady=2)
        
        # Add time range selection
        ttk.Label(left_controls, text="Time Range:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        
        self.time_range_var = tk.StringVar(value="30 days")
        self.time_range_combo = ttk.Combobox(left_controls, textvariable=self.time_range_var, 
                                           values=["7 days", "30 days", "90 days", "1 year", "Custom"], width=15)
        self.time_range_combo.grid(row=1, column=1, sticky="ew", padx=5, pady=2)
        
        # Add custom date range (initially hidden)
        self.custom_dates_frame = ttk.Frame(left_controls)
        
        ttk.Label(self.custom_dates_frame, text="Start Date:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.start_date_var = tk.StringVar(value=(datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"))
        ttk.Entry(self.custom_dates_frame, textvariable=self.start_date_var, width=12).grid(row=0, column=1, sticky="ew", padx=5, pady=2)
        
        ttk.Label(self.custom_dates_frame, text="End Date:").grid(row=0, column=2, sticky="w", padx=5, pady=2)
        self.end_date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        ttk.Entry(self.custom_dates_frame, textvariable=self.end_date_var, width=12).grid(row=0, column=3, sticky="ew", padx=5, pady=2)
        
        # Create right controls (chart type and parameters)
        right_controls = ttk.Frame(self.controls_frame)
        right_controls.pack(side=tk.RIGHT, fill=tk.X)
        
        # Add chart type selection
        ttk.Label(right_controls, text="Chart Type:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        
        self.chart_type_var = tk.StringVar(value="Line Chart")
        self.chart_type_combo = ttk.Combobox(right_controls, textvariable=self.chart_type_var, 
                                           values=["Line Chart", "Bar Chart", "Scatter Plot", "Heatmap"], width=15)
        self.chart_type_combo.grid(row=0, column=1, sticky="ew", padx=5, pady=2)
        
        # Add parameter selection
        params_frame = ttk.LabelFrame(self.controls_frame, text="Parameters")
        params_frame.pack(side=tk.TOP, fill=tk.X, pady=5)
        
        self.ph_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(params_frame, text="pH", variable=self.ph_var).pack(side=tk.LEFT, padx=10)
        
        self.chlorine_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(params_frame, text="Chlorine", variable=self.chlorine_var).pack(side=tk.LEFT, padx=10)
        
        self.alkalinity_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(params_frame, text="Alkalinity", variable=self.alkalinity_var).pack(side=tk.LEFT, padx=10)
        
        self.calcium_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(params_frame, text="Calcium", variable=self.calcium_var).pack(side=tk.LEFT, padx=10)
        
        self.cyanuric_acid_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(params_frame, text="Cyanuric Acid", variable=self.cyanuric_acid_var).pack(side=tk.LEFT, padx=10)
        
        self.temperature_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(params_frame, text="Temperature", variable=self.temperature_var).pack(side=tk.LEFT, padx=10)
        
        # Add trend analysis option
        self.trend_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(params_frame, text="Show Trends", variable=self.trend_var).pack(side=tk.LEFT, padx=10)
        
        # Add buttons frame
        buttons_frame = ttk.Frame(self.controls_frame)
        buttons_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=5)
        
        # Add refresh button
        ttk.Button(buttons_frame, text="Refresh", command=self.refresh_chart).pack(side=tk.LEFT, padx=5)
        
        # Add export buttons
        ttk.Button(buttons_frame, text="Export Data", command=self.export_data).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Export Chart", command=self.export_chart).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Print Report", command=self.print_report).pack(side=tk.LEFT, padx=5)
        
        # Create notebook for different views
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Create chart tab
        self.chart_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.chart_frame, text="Chart View")
        
        # Create figure for chart
        self.fig = Figure(figsize=(8, 5), dpi=100)
        
        # Create canvas for chart
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.chart_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Add navigation toolbar
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.chart_frame)
        self.toolbar.update()
        
        # Create table tab
        self.table_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.table_frame, text="Table View")
        
        # Create treeview for table
        self.table = ttk.Treeview(self.table_frame)
        self.table.pack(fill=tk.BOTH, expand=True)
        
        # Add scrollbars to table
        table_y_scrollbar = ttk.Scrollbar(self.table, orient="vertical", command=self.table.yview)
        table_y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.table.configure(yscrollcommand=table_y_scrollbar.set)
        
        table_x_scrollbar = ttk.Scrollbar(self.table_frame, orient="horizontal", command=self.table.xview)
        table_x_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.table.configure(xscrollcommand=table_x_scrollbar.set)
        
        # Create statistics tab
        self.stats_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.stats_frame, text="Statistics")
        
        # Create trend analysis tab
        self.trend_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.trend_frame, text="Trend Analysis")
        
        # Populate customer combo
        self.populate_customer_combo()
        
        # Bind events
        self.customer_combo.bind("<<ComboboxSelected>>", lambda e: self.refresh_chart())
        self.time_range_combo.bind("<<ComboboxSelected>>", self.on_time_range_change)
        self.chart_type_combo.bind("<<ComboboxSelected>>", lambda e: self.refresh_chart())
        self.ph_var.trace("w", lambda *args: self.refresh_chart())
        self.chlorine_var.trace("w", lambda *args: self.refresh_chart())
        self.alkalinity_var.trace("w", lambda *args: self.refresh_chart())
        self.calcium_var.trace("w", lambda *args: self.refresh_chart())
        self.cyanuric_acid_var.trace("w", lambda *args: self.refresh_chart())
        self.temperature_var.trace("w", lambda *args: self.refresh_chart())
        self.trend_var.trace("w", lambda *args: self.refresh_chart())
        
        # Initialize chart
        self.refresh_chart()
    
    def on_time_range_change(self, event):
        """Handle time range selection change."""
        if self.time_range_var.get() == "Custom":
            self.custom_dates_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=5, pady=2)
        else:
            self.custom_dates_frame.grid_forget()
        
        self.refresh_chart()
    
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
    
    def get_date_range(self):
        """Get the selected date range."""
        time_range = self.time_range_var.get()
        
        if time_range == "Custom":
            try:
                start_date = datetime.strptime(self.start_date_var.get(), "%Y-%m-%d")
                end_date = datetime.strptime(self.end_date_var.get(), "%Y-%m-%d")
                return start_date, end_date
            except ValueError:
                messagebox.showerror("Invalid Date", "Please enter dates in YYYY-MM-DD format")
                return datetime.now() - timedelta(days=30), datetime.now()
        else:
            end_date = datetime.now()
            
            if time_range == "7 days":
                start_date = end_date - timedelta(days=7)
            elif time_range == "30 days":
                start_date = end_date - timedelta(days=30)
            elif time_range == "90 days":
                start_date = end_date - timedelta(days=90)
            elif time_range == "1 year":
                start_date = end_date - timedelta(days=365)
            else:
                start_date = end_date - timedelta(days=30)
            
            return start_date, end_date
    
    def get_historical_data(self):
        """Get historical chemical data for visualization."""
        try:
            # Get selected customer ID
            customer_id = None
            if self.customer_var.get() and self.customer_var.get() != "All Customers":
                try:
                    customer_id = int(self.customer_var.get().split(":")[0])
                except:
                    pass
            
            # Get date range
            start_date, end_date = self.get_date_range()
            
            # Get readings from database
            if customer_id:
                readings = self.db_service.get_customer_readings(customer_id, limit=1000)
            else:
                readings = self.db_service.get_recent_readings(limit=1000)
            
            # Filter readings by date
            filtered_readings = [
                reading for reading in readings
                if start_date.isoformat() <= reading.get("timestamp", "") <= end_date.isoformat()
            ]
            
            # Extract data for visualization
            dates = []
            ph_values = []
            chlorine_values = []
            alkalinity_values = []
            calcium_values = []
            cyanuric_acid_values = []
            temperature_values = []
            
            for reading in filtered_readings:
                # Parse timestamp
                try:
                    timestamp = datetime.fromisoformat(reading.get("timestamp", ""))
                    dates.append(timestamp)
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
                
                try:
                    cyanuric_acid_values.append(float(reading.get("cyanuric_acid", 0)))
                except (ValueError, TypeError):
                    cyanuric_acid_values.append(None)
                
                try:
                    temperature_values.append(float(reading.get("temperature", 0)))
                except (ValueError, TypeError):
                    temperature_values.append(None)
            
            # Create result dictionary
            result = {
                "dates": dates,
                "ph_values": ph_values,
                "chlorine_values": chlorine_values,
                "alkalinity_values": alkalinity_values,
                "calcium_values": calcium_values,
                "cyanuric_acid_values": cyanuric_acid_values,
                "temperature_values": temperature_values,
                "readings": filtered_readings
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
                "calcium_values": [],
                "cyanuric_acid_values": [],
                "temperature_values": [],
                "readings": []
            }
    
    def refresh_chart(self):
        """Refresh the chart with current data."""
        try:
            # Get historical data
            data = self.get_historical_data()
            
            # Clear the figure
            self.fig.clear()
            
            # Get selected parameters
            selected_params = []
            if self.ph_var.get():
                selected_params.append(("pH", data["ph_values"], "blue", self.ideal_ranges["pH"]))
            if self.chlorine_var.get():
                selected_params.append(("Chlorine", data["chlorine_values"], "green", self.ideal_ranges["free_chlorine"]))
            if self.alkalinity_var.get():
                selected_params.append(("Alkalinity", data["alkalinity_values"], "red", self.ideal_ranges["alkalinity"]))
            if self.calcium_var.get():
                selected_params.append(("Calcium", data["calcium_values"], "purple", self.ideal_ranges["calcium"]))
            if self.cyanuric_acid_var.get():
                selected_params.append(("Cyanuric Acid", data["cyanuric_acid_values"], "orange", self.ideal_ranges["cyanuric_acid"]))
            if self.temperature_var.get():
                selected_params.append(("Temperature", data["temperature_values"], "brown", self.ideal_ranges["temperature"]))
            
            # Get chart type
            chart_type = self.chart_type_var.get()
            
            if not selected_params:
                # No parameters selected, show message
                ax = self.fig.add_subplot(111)
                ax.text(0.5, 0.5, "No parameters selected", ha="center", va="center", fontsize=14)
                ax.axis("off")
            elif chart_type == "Heatmap":
                # Create heatmap
                self.create_heatmap(data, selected_params)
            else:
                # Create subplots for selected parameters
                num_params = len(selected_params)
                
                for i, (param_name, param_values, color, ideal_range) in enumerate(selected_params):
                    ax = self.fig.add_subplot(num_params, 1, i+1)
                    
                    if i == 0:
                        ax.set_title("Chemical History")
                    
                    ax.set_ylabel(param_name)
                    ax.grid(True)
                    
                    if data["dates"]:
                        if chart_type == "Line Chart":
                            # Line chart
                            ax.plot(data["dates"], param_values, f"{color}-", marker="o", label=param_name)
                            
                            # Add trend line if requested
                            if self.trend_var.get():
                                self.add_trend_line(ax, data["dates"], param_values, color)
                        
                        elif chart_type == "Bar Chart":
                            # Bar chart
                            ax.bar(data["dates"], param_values, color=color, alpha=0.7, label=param_name)
                        
                        elif chart_type == "Scatter Plot":
                            # Scatter plot
                            ax.scatter(data["dates"], param_values, color=color, label=param_name)
                            
                            # Add trend line if requested
                            if self.trend_var.get():
                                self.add_trend_line(ax, data["dates"], param_values, color)
                        
                        # Add ideal range
                        min_val, max_val = ideal_range
                        ax.axhspan(min_val, max_val, alpha=0.2, color="green")
                        
                        # Format x-axis dates
                        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
                        ax.xaxis.set_major_locator(mdates.AutoDateLocator())
                        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha="right")
                    
                    # Set y-axis limits based on parameter
                    if param_name == "pH":
                        ax.set_ylim(min(6.0, min(param_values) if param_values else 6.0) - 0.2, 
                                   max(8.4, max(param_values) if param_values else 8.4) + 0.2)
                    elif param_name == "Chlorine":
                        ax.set_ylim(0, max(5.0, max(param_values) if param_values else 5.0) + 0.5)
                    elif param_name == "Alkalinity":
                        ax.set_ylim(min(60, min(param_values) if param_values else 60) - 10, 
                                   max(180, max(param_values) if param_values else 180) + 10)
                    elif param_name == "Calcium":
                        ax.set_ylim(min(150, min(param_values) if param_values else 150) - 20, 
                                   max(450, max(param_values) if param_values else 450) + 20)
                    elif param_name == "Cyanuric Acid":
                        ax.set_ylim(0, max(100, max(param_values) if param_values else 100) + 10)
                    elif param_name == "Temperature":
                        ax.set_ylim(min(60, min(param_values) if param_values else 60) - 5, 
                                   max(95, max(param_values) if param_values else 95) + 5)
                
                # Set x-axis label on the bottom subplot
                if selected_params:
                    self.fig.axes[-1].set_xlabel("Date")
            
            # Update table view
            self.update_table_view(data)
            
            # Update statistics view
            self.update_statistics_view(data)
            
            # Update trend analysis view
            self.update_trend_analysis_view(data)
            
            # Adjust layout
            self.fig.tight_layout()
            self.canvas.draw()
        
        except Exception as e:
            self.logger.error(f"Error refreshing chart: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
    
    def create_heatmap(self, data, selected_params):
        """Create a heatmap visualization."""
        if not data["dates"] or not selected_params:
            ax = self.fig.add_subplot(111)
            ax.text(0.5, 0.5, "No data available for heatmap", ha="center", va="center", fontsize=14)
            ax.axis("off")
            return
        
        # Create heatmap data
        param_names = [param[0] for param in selected_params]
        param_values = [param[1] for param in selected_params]
        ideal_ranges = [param[3] for param in selected_params]
        
        # Normalize values to 0-1 range for heatmap
        normalized_values = []
        for values, (min_range, max_range) in zip(param_values, ideal_ranges):
            # Replace None values with NaN
            values = [v if v is not None else float('nan') for v in values]
            
            # Calculate normalized values
            # 0.5 = ideal (middle of range)
            # 0 = too low, 1 = too high
            normalized = []
            for v in values:
                if np.isnan(v):
                    normalized.append(np.nan)
                elif v < min_range:
                    # Too low - normalize from 0 to 0.4
                    norm_val = 0.4 * (v / min_range)
                    normalized.append(norm_val)
                elif v > max_range:
                    # Too high - normalize from 0.6 to 1
                    norm_val = 0.6 + 0.4 * ((v - max_range) / max_range)
                    normalized.append(norm_val)
                else:
                    # Within range - normalize from 0.4 to 0.6
                    norm_val = 0.4 + 0.2 * ((v - min_range) / (max_range - min_range))
                    normalized.append(norm_val)
            
            normalized_values.append(normalized)
        
        # Create heatmap
        ax = self.fig.add_subplot(111)
        
        # Convert dates to strings for display
        date_strings = [d.strftime("%Y-%m-%d") for d in data["dates"]]
        
        # Create heatmap data array
        heatmap_data = np.array(normalized_values)
        
        # Create heatmap
        im = ax.imshow(heatmap_data, aspect='auto', cmap='RdYlGn_r', vmin=0, vmax=1)
        
        # Set labels
        ax.set_yticks(range(len(param_names)))
        ax.set_yticklabels(param_names)
        
        # Set x-axis labels (dates)
        num_dates = len(date_strings)
        if num_dates > 10:
            # Show fewer date labels if there are many dates
            step = num_dates // 10
            ax.set_xticks(range(0, num_dates, step))
            ax.set_xticklabels([date_strings[i] for i in range(0, num_dates, step)], rotation=45, ha="right")
        else:
            ax.set_xticks(range(num_dates))
            ax.set_xticklabels(date_strings, rotation=45, ha="right")
        
        # Add colorbar
        cbar = self.fig.colorbar(im, ax=ax)
        cbar.set_label('Parameter Status')
        
        # Add custom ticks to colorbar
        cbar.set_ticks([0, 0.25, 0.5, 0.75, 1])
        cbar.set_ticklabels(['Too Low', 'Low', 'Ideal', 'High', 'Too High'])
        
        # Add title
        ax.set_title("Chemical Parameters Heatmap")
    
    def add_trend_line(self, ax, dates, values, color):
        """Add a trend line to the chart."""
        # Convert dates to numeric values for trend calculation
        date_nums = mdates.date2num(dates)
        
        # Remove None values
        valid_indices = [i for i, v in enumerate(values) if v is not None]
        if not valid_indices:
            return
        
        valid_dates = [date_nums[i] for i in valid_indices]
        valid_values = [values[i] for i in valid_indices]
        
        # Calculate trend line
        z = np.polyfit(valid_dates, valid_values, 1)
        p = np.poly1d(z)
        
        # Add trend line
        ax.plot(dates, p(date_nums), f"{color}--", linewidth=2, label="Trend")
        
        # Add trend equation
        slope = z[0]
        intercept = z[1]
        
        # Calculate R-squared
        y_mean = np.mean(valid_values)
        ss_tot = sum((y - y_mean) ** 2 for y in valid_values)
        ss_res = sum((y - p(x)) ** 2 for x, y in zip(valid_dates, valid_values))
        r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
        
        # Add trend info to legend
        trend_direction = "increasing" if slope > 0 else "decreasing"
        ax.text(0.02, 0.95, f"Trend: {trend_direction} (R\u00b2 = {r_squared:.2f})", 
                transform=ax.transAxes, fontsize=9, verticalalignment='top')
    
    def update_table_view(self, data):
        """Update the table view with current data."""
        # Clear existing table
        for item in self.table.get_children():
            self.table.delete(item)
        
        # Configure columns
        columns = ["Date", "Time"]
        
        if self.ph_var.get():
            columns.append("pH")
        if self.chlorine_var.get():
            columns.append("Chlorine")
        if self.alkalinity_var.get():
            columns.append("Alkalinity")
        if self.calcium_var.get():
            columns.append("Calcium")
        if self.cyanuric_acid_var.get():
            columns.append("Cyanuric Acid")
        if self.temperature_var.get():
            columns.append("Temperature")
        
        # Configure table columns
        self.table["columns"] = columns
        self.table["show"] = "headings"
        
        for col in columns:
            self.table.heading(col, text=col)
            self.table.column(col, width=100)
        
        # Add data to table
        for i, date in enumerate(data["dates"]):
            row_values = [
                date.strftime("%Y-%m-%d"),
                date.strftime("%H:%M:%S")
            ]
            
            if self.ph_var.get():
                row_values.append(data["ph_values"][i] if data["ph_values"][i] is not None else "")
            if self.chlorine_var.get():
                row_values.append(data["chlorine_values"][i] if data["chlorine_values"][i] is not None else "")
            if self.alkalinity_var.get():
                row_values.append(data["alkalinity_values"][i] if data["alkalinity_values"][i] is not None else "")
            if self.calcium_var.get():
                row_values.append(data["calcium_values"][i] if data["calcium_values"][i] is not None else "")
            if self.cyanuric_acid_var.get():
                row_values.append(data["cyanuric_acid_values"][i] if data["cyanuric_acid_values"][i] is not None else "")
            if self.temperature_var.get():
                row_values.append(data["temperature_values"][i] if data["temperature_values"][i] is not None else "")
            
            self.table.insert("", "end", values=row_values)
    
    def update_statistics_view(self, data):
        """Update the statistics view with current data."""
        # Clear existing statistics
        for widget in self.stats_frame.winfo_children():
            widget.destroy()
        
        # Create statistics table
        stats_table = ttk.Treeview(self.stats_frame, columns=("Parameter", "Min", "Max", "Average", "Ideal Range", "Status"), show="headings")
        stats_table.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Configure columns
        for col in stats_table["columns"]:
            stats_table.heading(col, text=col)
            stats_table.column(col, width=100)
        
        # Calculate statistics
        stats = []
        
        if self.ph_var.get():
            stats.append(self.calculate_statistics("pH", data["ph_values"], self.ideal_ranges["pH"]))
        if self.chlorine_var.get():
            stats.append(self.calculate_statistics("Chlorine", data["chlorine_values"], self.ideal_ranges["free_chlorine"]))
        if self.alkalinity_var.get():
            stats.append(self.calculate_statistics("Alkalinity", data["alkalinity_values"], self.ideal_ranges["alkalinity"]))
        if self.calcium_var.get():
            stats.append(self.calculate_statistics("Calcium", data["calcium_values"], self.ideal_ranges["calcium"]))
        if self.cyanuric_acid_var.get():
            stats.append(self.calculate_statistics("Cyanuric Acid", data["cyanuric_acid_values"], self.ideal_ranges["cyanuric_acid"]))
        if self.temperature_var.get():
            stats.append(self.calculate_statistics("Temperature", data["temperature_values"], self.ideal_ranges["temperature"]))
        
        # Add statistics to table
        for stat in stats:
            stats_table.insert("", "end", values=(
                stat["parameter"],
                f"{stat['min']:.2f}" if stat["min"] is not None else "N/A",
                f"{stat['max']:.2f}" if stat["max"] is not None else "N/A",
                f"{stat['avg']:.2f}" if stat["avg"] is not None else "N/A",
                f"{stat['ideal_min']:.1f} - {stat['ideal_max']:.1f}",
                stat["status"]
            ))
        
        # Add summary text
        summary_frame = ttk.LabelFrame(self.stats_frame, text="Summary")
        summary_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Create summary text
        summary_text = "Overall Water Quality: "
        
        # Count parameters in range
        in_range_count = sum(1 for stat in stats if stat["status"] == "In Range")
        total_params = len(stats)
        
        if total_params == 0:
            summary_text += "No data available"
        elif in_range_count == total_params:
            summary_text += "Excellent - All parameters in ideal range"
        elif in_range_count >= total_params * 0.75:
            summary_text += "Good - Most parameters in ideal range"
        elif in_range_count >= total_params * 0.5:
            summary_text += "Fair - Some parameters need adjustment"
        else:
            summary_text += "Poor - Multiple parameters out of range"
        
        ttk.Label(summary_frame, text=summary_text, font=("Arial", 12)).pack(anchor=tk.W, padx=10, pady=5)
        
        # Add recommendations
        if stats:
            recommendations = []
            
            for stat in stats:
                if stat["status"] != "In Range":
                    if stat["avg"] < stat["ideal_min"]:
                        recommendations.append(f"Increase {stat['parameter']} level (currently too low)")
                    elif stat["avg"] > stat["ideal_max"]:
                        recommendations.append(f"Decrease {stat['parameter']} level (currently too high)")
            
            if recommendations:
                ttk.Label(summary_frame, text="Recommendations:", font=("Arial", 12)).pack(anchor=tk.W, padx=10, pady=5)
                
                for i, recommendation in enumerate(recommendations):
                    ttk.Label(summary_frame, text=f"{i+1}. {recommendation}").pack(anchor=tk.W, padx=20, pady=2)
    
    def calculate_statistics(self, parameter, values, ideal_range):
        """Calculate statistics for a parameter."""
        # Filter out None values
        filtered_values = [v for v in values if v is not None]
        
        if not filtered_values:
            return {
                "parameter": parameter,
                "min": None,
                "max": None,
                "avg": None,
                "ideal_min": ideal_range[0],
                "ideal_max": ideal_range[1],
                "status": "No Data"
            }
        
        min_val = min(filtered_values)
        max_val = max(filtered_values)
        avg_val = sum(filtered_values) / len(filtered_values)
        
        # Determine status
        if avg_val < ideal_range[0]:
            status = "Too Low"
        elif avg_val > ideal_range[1]:
            status = "Too High"
        else:
            status = "In Range"
        
        return {
            "parameter": parameter,
            "min": min_val,
            "max": max_val,
            "avg": avg_val,
            "ideal_min": ideal_range[0],
            "ideal_max": ideal_range[1],
            "status": status
        }
    
    def update_trend_analysis_view(self, data):
        """Update the trend analysis view with current data."""
        # Clear existing trend analysis
        for widget in self.trend_frame.winfo_children():
            widget.destroy()
        
        # Create trend analysis table
        trend_table = ttk.Treeview(self.trend_frame, columns=("Parameter", "Trend", "R-squared", "Prediction (7 days)"), show="headings")
        trend_table.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Configure columns
        for col in trend_table["columns"]:
            trend_table.heading(col, text=col)
            trend_table.column(col, width=100)
        
        # Calculate trends
        trends = []
        
        if self.ph_var.get() and data["dates"]:
            trends.append(self.calculate_trend("pH", data["dates"], data["ph_values"], self.ideal_ranges["pH"]))
        if self.chlorine_var.get() and data["dates"]:
            trends.append(self.calculate_trend("Chlorine", data["dates"], data["chlorine_values"], self.ideal_ranges["free_chlorine"]))
        if self.alkalinity_var.get() and data["dates"]:
            trends.append(self.calculate_trend("Alkalinity", data["dates"], data["alkalinity_values"], self.ideal_ranges["alkalinity"]))
        if self.calcium_var.get() and data["dates"]:
            trends.append(self.calculate_trend("Calcium", data["dates"], data["calcium_values"], self.ideal_ranges["calcium"]))
        if self.cyanuric_acid_var.get() and data["dates"]:
            trends.append(self.calculate_trend("Cyanuric Acid", data["dates"], data["cyanuric_acid_values"], self.ideal_ranges["cyanuric_acid"]))
        if self.temperature_var.get() and data["dates"]:
            trends.append(self.calculate_trend("Temperature", data["dates"], data["temperature_values"], self.ideal_ranges["temperature"]))
        
        # Add trends to table
        for trend in trends:
            trend_table.insert("", "end", values=(
                trend["parameter"],
                trend["trend"],
                f"{trend['r_squared']:.3f}" if trend["r_squared"] is not None else "N/A",
                f"{trend['prediction']:.2f}" if trend["prediction"] is not None else "N/A"
            ))
        
        # Add trend summary
        summary_frame = ttk.LabelFrame(self.trend_frame, text="Trend Summary")
        summary_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Create trend summary text
        if not trends:
            ttk.Label(summary_frame, text="No trend data available", font=("Arial", 12)).pack(anchor=tk.W, padx=10, pady=5)
        else:
            # Count concerning trends
            concerning_trends = []
            
            for trend in trends:
                if trend["concern"]:
                    concerning_trends.append(f"{trend['parameter']} is {trend['trend'].lower()} and predicted to be {trend['concern']}")
            
            if concerning_trends:
                ttk.Label(summary_frame, text="Concerning Trends:", font=("Arial", 12)).pack(anchor=tk.W, padx=10, pady=5)
                
                for i, concern in enumerate(concerning_trends):
                    ttk.Label(summary_frame, text=f"{i+1}. {concern}").pack(anchor=tk.W, padx=20, pady=2)
            else:
                ttk.Label(summary_frame, text="No concerning trends detected", font=("Arial", 12)).pack(anchor=tk.W, padx=10, pady=5)
    
    def calculate_trend(self, parameter, dates, values, ideal_range):
        """Calculate trend for a parameter."""
        # Convert dates to numeric values for trend calculation
        date_nums = mdates.date2num(dates)
        
        # Remove None values
        valid_indices = [i for i, v in enumerate(values) if v is not None]
        if not valid_indices:
            return {
                "parameter": parameter,
                "trend": "No Data",
                "r_squared": None,
                "prediction": None,
                "concern": None
            }
        
        valid_dates = [date_nums[i] for i in valid_indices]
        valid_values = [values[i] for i in valid_indices]
        
        # Calculate trend line
        z = np.polyfit(valid_dates, valid_values, 1)
        p = np.poly1d(z)
        
        # Calculate R-squared
        y_mean = np.mean(valid_values)
        ss_tot = sum((y - y_mean) ** 2 for y in valid_values)
        ss_res = sum((y - p(x)) ** 2 for x, y in zip(valid_dates, valid_values))
        r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
        
        # Determine trend direction
        slope = z[0]
        if abs(slope) < 0.001:  # Very small slope
            trend = "Stable"
        elif slope > 0:
            trend = "Increasing"
        else:
            trend = "Decreasing"
        
        # Predict value in 7 days
        future_date = date_nums[-1] + 7  # 7 days in the future
        prediction = p(future_date)
        
        # Determine if prediction is concerning
        min_val, max_val = ideal_range
        concern = None
        
        if prediction < min_val:
            concern = f"too low ({prediction:.2f} vs. ideal minimum {min_val})"
        elif prediction > max_val:
            concern = f"too high ({prediction:.2f} vs. ideal maximum {max_val})"
        
        return {
            "parameter": parameter,
            "trend": trend,
            "r_squared": r_squared,
            "prediction": prediction,
            "concern": concern
        }
    
    def export_data(self):
        """Export data to CSV or JSON file."""
        try:
            # Get data
            data = self.get_historical_data()
            
            # Ask for file type
            file_types = [("CSV Files", "*.csv"), ("JSON Files", "*.json")]
            file_path = filedialog.asksaveasfilename(
                title="Export Data",
                filetypes=file_types,
                defaultextension=".csv"
            )
            
            if not file_path:
                return
            
            # Get selected customer name
            customer_name = "All Customers"
            if self.customer_var.get() and self.customer_var.get() != "All Customers":
                customer_name = self.customer_var.get().split(":", 1)[1].strip()
            
            # Get date range
            start_date, end_date = self.get_date_range()
            
            # Export data
            if file_path.endswith(".csv"):
                # Export to CSV
                import csv
                
                with open(file_path, "w", newline="") as f:
                    # Define CSV headers
                    headers = ["Date", "Time", "Customer"]
                    
                    if self.ph_var.get():
                        headers.append("pH")
                    if self.chlorine_var.get():
                        headers.append("Free Chlorine")
                    if self.alkalinity_var.get():
                        headers.append("Alkalinity")
                    if self.calcium_var.get():
                        headers.append("Calcium")
                    if self.cyanuric_acid_var.get():
                        headers.append("Cyanuric Acid")
                    if self.temperature_var.get():
                        headers.append("Temperature")
                    
                    writer = csv.writer(f)
                    writer.writerow(headers)
                    
                    # Write data rows
                    for i, date in enumerate(data["dates"]):
                        row = [
                            date.strftime("%Y-%m-%d"),
                            date.strftime("%H:%M:%S"),
                            customer_name
                        ]
                        
                        if self.ph_var.get():
                            row.append(data["ph_values"][i] if data["ph_values"][i] is not None else "")
                        if self.chlorine_var.get():
                            row.append(data["chlorine_values"][i] if data["chlorine_values"][i] is not None else "")
                        if self.alkalinity_var.get():
                            row.append(data["alkalinity_values"][i] if data["alkalinity_values"][i] is not None else "")
                        if self.calcium_var.get():
                            row.append(data["calcium_values"][i] if data["calcium_values"][i] is not None else "")
                        if self.cyanuric_acid_var.get():
                            row.append(data["cyanuric_acid_values"][i] if data["cyanuric_acid_values"][i] is not None else "")
                        if self.temperature_var.get():
                            row.append(data["temperature_values"][i] if data["temperature_values"][i] is not None else "")
                        
                        writer.writerow(row)
            
            elif file_path.endswith(".json"):
                # Export to JSON
                export_data = {
                    "export_date": datetime.now().isoformat(),
                    "customer": customer_name,
                    "date_range": {
                        "start": start_date.isoformat(),
                        "end": end_date.isoformat()
                    },
                    "data": []
                }
                
                # Add data points
                for i, date in enumerate(data["dates"]):
                    point = {
                        "date": date.isoformat()
                    }
                    
                    if self.ph_var.get():
                        point["pH"] = data["ph_values"][i]
                    if self.chlorine_var.get():
                        point["free_chlorine"] = data["chlorine_values"][i]
                    if self.alkalinity_var.get():
                        point["alkalinity"] = data["alkalinity_values"][i]
                    if self.calcium_var.get():
                        point["calcium"] = data["calcium_values"][i]
                    if self.cyanuric_acid_var.get():
                        point["cyanuric_acid"] = data["cyanuric_acid_values"][i]
                    if self.temperature_var.get():
                        point["temperature"] = data["temperature_values"][i]
                    
                    export_data["data"].append(point)
                
                # Write to file
                with open(file_path, "w") as f:
                    json.dump(export_data, f, indent=2)
            
            messagebox.showinfo("Export Successful", f"Data exported to {file_path}")
            
            return file_path
        except Exception as e:
            self.logger.error(f"Error exporting data: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            
            messagebox.showerror("Export Failed", f"Failed to export data: {e}")
            
            return ""
    
    def export_chart(self):
        """Export chart to image file."""
        try:
            # Ask for file type
            file_types = [("PNG Files", "*.png"), ("PDF Files", "*.pdf"), ("SVG Files", "*.svg")]
            file_path = filedialog.asksaveasfilename(
                title="Export Chart",
                filetypes=file_types,
                defaultextension=".png"
            )
            
            if not file_path:
                return
            
            # Save figure
            self.fig.savefig(file_path, dpi=300, bbox_inches="tight")
            
            messagebox.showinfo("Export Successful", f"Chart exported to {file_path}")
            
            return file_path
        except Exception as e:
            self.logger.error(f"Error exporting chart: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            
            messagebox.showerror("Export Failed", f"Failed to export chart: {e}")
            
            return ""
    
    def print_report(self):
        """Generate and print a report."""
        try:
            # Create a temporary directory for report files
            import tempfile
            import os
            
            temp_dir = tempfile.mkdtemp()
            
            # Get data
            data = self.get_historical_data()
            
            # Get selected customer name
            customer_name = "All Customers"
            if self.customer_var.get() and self.customer_var.get() != "All Customers":
                customer_name = self.customer_var.get().split(":", 1)[1].strip()
            
            # Get date range
            start_date, end_date = self.get_date_range()
            
            # Export chart to temporary file
            chart_path = os.path.join(temp_dir, "chart.png")
            self.fig.savefig(chart_path, dpi=300, bbox_inches="tight")
            
            # Create HTML report
            html_path = os.path.join(temp_dir, "report.html")
            
            with open(html_path, "w") as f:
                f.write(f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Pool Chemistry Report</title>
                    <style>
                        body {{ font-family: Arial, sans-serif; margin: 20px; }}
                        h1, h2 {{ color: #2c3e50; }}
                        table {{ border-collapse: collapse; width: 100%; margin-bottom: 20px; }}
                        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                        th {{ background-color: #f2f2f2; }}
                        tr:nth-child(even) {{ background-color: #f9f9f9; }}
                        .chart {{ max-width: 100%; margin: 20px 0; }}
                        .footer {{ margin-top: 30px; font-size: 0.8em; color: #7f8c8d; }}
                        @media print {{
                            body {{ margin: 0.5in; }}
                            .no-print {{ display: none; }}
                            .page-break {{ page-break-before: always; }}
                        }}
                    </style>
                </head>
                <body>
                    <h1>Pool Chemistry Report</h1>
                    <p><strong>Customer:</strong> {customer_name}</p>
                    <p><strong>Date Range:</strong> {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}</p>
                    <p><strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                    
                    <h2>Chemical History Chart</h2>
                    <img src="chart.png" alt="Chemical History Chart" class="chart">
                    
                    <h2>Statistics</h2>
                    <table>
                        <tr>
                            <th>Parameter</th>
                            <th>Minimum</th>
                            <th>Maximum</th>
                            <th>Average</th>
                            <th>Ideal Range</th>
                            <th>Status</th>
                        </tr>
                """)
                
                # Add statistics rows
                parameters = []
                if self.ph_var.get():
                    parameters.append(("pH", data["ph_values"], self.ideal_ranges["pH"]))
                if self.chlorine_var.get():
                    parameters.append(("Chlorine", data["chlorine_values"], self.ideal_ranges["free_chlorine"]))
                if self.alkalinity_var.get():
                    parameters.append(("Alkalinity", data["alkalinity_values"], self.ideal_ranges["alkalinity"]))
                if self.calcium_var.get():
                    parameters.append(("Calcium", data["calcium_values"], self.ideal_ranges["calcium"]))
                if self.cyanuric_acid_var.get():
                    parameters.append(("Cyanuric Acid", data["cyanuric_acid_values"], self.ideal_ranges["cyanuric_acid"]))
                if self.temperature_var.get():
                    parameters.append(("Temperature", data["temperature_values"], self.ideal_ranges["temperature"]))
                
                for param_name, param_values, ideal_range in parameters:
                    stat = self.calculate_statistics(param_name, param_values, ideal_range)
                    
                    f.write(f"""
                        <tr>
                            <td>{stat['parameter']}</td>
                            <td>{stat['min']:.2f if stat['min'] is not None else 'N/A'}</td>
                            <td>{stat['max']:.2f if stat['max'] is not None else 'N/A'}</td>
                            <td>{stat['avg']:.2f if stat['avg'] is not None else 'N/A'}</td>
                            <td>{stat['ideal_min']:.1f} - {stat['ideal_max']:.1f}</td>
                            <td>{stat['status']}</td>
                        </tr>
                    """)
                
                f.write("""
                    </table>
                    
                    <h2>Trend Analysis</h2>
                    <table>
                        <tr>
                            <th>Parameter</th>
                            <th>Trend</th>
                            <th>R-squared</th>
                            <th>Prediction (7 days)</th>
                        </tr>
                """)
                
                # Add trend rows
                for param_name, param_values, ideal_range in parameters:
                    if data["dates"]:
                        trend = self.calculate_trend(param_name, data["dates"], param_values, ideal_range)
                        
                        f.write(f"""
                            <tr>
                                <td>{trend['parameter']}</td>
                                <td>{trend['trend']}</td>
                                <td>{trend['r_squared']:.3f if trend['r_squared'] is not None else 'N/A'}</td>
                                <td>{trend['prediction']:.2f if trend['prediction'] is not None else 'N/A'}</td>
                            </tr>
                        """)
                
                f.write("""
                    </table>
                    
                    <h2>Recommendations</h2>
                """)
                
                # Add recommendations
                recommendations = []
                for param_name, param_values, ideal_range in parameters:
                    stat = self.calculate_statistics(param_name, param_values, ideal_range)
                    if stat["status"] != "In Range" and stat["status"] != "No Data":
                        if stat["avg"] < stat["ideal_min"]:
                            recommendations.append(f"Increase {stat['parameter']} level (currently too low)")
                        elif stat["avg"] > stat["ideal_max"]:
                            recommendations.append(f"Decrease {stat['parameter']} level (currently too high)")
                
                if recommendations:
                    f.write("<ul>")
                    for recommendation in recommendations:
                        f.write(f"<li>{recommendation}</li>")
                    f.write("</ul>")
                else:
                    f.write("<p>No specific recommendations at this time.</p>")
                
                # Add data table (page break before)
                f.write("""
                    <div class="page-break"></div>
                    <h2>Data Table</h2>
                    <table>
                        <tr>
                            <th>Date</th>
                            <th>Time</th>
                """)
                
                # Add parameter columns
                for param_name, _, _ in parameters:
                    f.write(f"<th>{param_name}</th>")
                
                f.write("</tr>")
                
                # Add data rows
                for i, date in enumerate(data["dates"]):
                    f.write(f"""
                        <tr>
                            <td>{date.strftime('%Y-%m-%d')}</td>
                            <td>{date.strftime('%H:%M:%S')}</td>
                    """)
                    
                    for _, param_values, _ in parameters:
                        value = param_values[i]
                        f.write(f"<td>{value:.2f if value is not None else ''}</td>")
                    
                    f.write("</tr>")
                
                f.write("""
                    </table>
                    
                    <div class="footer">
                        <p>Generated by Deep Blue Pool Chemistry Application</p>
                    </div>
                </body>
                </html>
                """)
            
            # Convert HTML to PDF
            pdf_path = os.path.join(temp_dir, "report.pdf")
            
            try:
                import subprocess
                subprocess.run(["wkhtmltopdf", html_path, pdf_path], check=True)
                
                # Ask user where to save the PDF
                save_path = filedialog.asksaveasfilename(
                    title="Save Report",
                    filetypes=[("PDF Files", "*.pdf")],
                    defaultextension=".pdf"
                )
                
                if save_path:
                    # Copy the PDF to the save location
                    import shutil
                    shutil.copy2(pdf_path, save_path)
                    
                    # Open the PDF
                    if os.name == 'nt':  # Windows
                        os.startfile(save_path)
                    elif os.name == 'posix':  # macOS or Linux
                        subprocess.run(["xdg-open", save_path], check=True)
                    
                    messagebox.showinfo("Report Generated", f"Report saved to {save_path}")
            except Exception as e:
                self.logger.error(f"Error generating PDF: {e}")
                
                # Fallback to opening HTML in browser
                import webbrowser
                webbrowser.open(f"file://{html_path}")
                
                messagebox.showinfo("Report Generated", 
                                   f"PDF generation failed. HTML report opened in browser.\
\
HTML file: {html_path}")
            
            return True
        except Exception as e:
            self.logger.error(f"Error generating report: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            
            messagebox.showerror("Report Generation Failed", f"Failed to generate report: {e}")
            
            return False

# For testing
if __name__ == "__main__":
    # Create root window
    root = tk.Tk()
    root.title("Enhanced Data Visualization Test")
    root.geometry("1000x800")
    
    # Import database service
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from database_service import DatabaseService
    
    # Create database service
    db_service = DatabaseService("data/pool_data.db")
    
    # Create visualizer
    visualizer = EnhancedDataVisualization(db_service, root)
    
    # Run the application
    root.mainloop()
