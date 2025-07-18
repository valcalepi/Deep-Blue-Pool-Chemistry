"""
Enhanced GUI Controller for Deep Blue Pool Chemistry (Part 2).

This file continues the implementation of the enhanced GUI controller,
focusing on the weather impact analysis, historical data visualization,
maintenance log, settings interface, and AI & predictive analytics.
"""

# Add necessary imports
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, timedelta
import json
import logging
from PIL import Image, ImageTk
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Get logger
logger = logging.getLogger(__name__)

# This continues from the previous implementation

def _create_weather_impact_card(self, parent):
    """
    Create a card for weather impact analysis.
    
    Args:
        parent: Parent widget.
    """
    # Create the card
    card, content_frame, _ = self._create_card(
        parent=parent,
        title="Weather Impact Analysis",
        description="See how weather conditions affect your pool chemistry"
    )
    
    try:
        # Create instructions
        instructions_label = tk.Label(
            content_frame,
            text="Weather conditions can significantly impact your pool chemistry. "
                 "This analysis shows how recent and forecasted weather may affect your pool.",
            wraplength=600,
            justify="left",
            bg=self.COLORS["background"],
            fg=self.COLORS["text"],
            font=(self.FONT_FAMILY, self.FONT_SIZE_NORMAL)
        )
        instructions_label.pack(pady=(0, 10), fill="x")
        
        # Get weather impact data
        weather_impact = self.weather_service.get_weather_impact()
        
        if weather_impact and "daily_impact" in weather_impact:
            # Create a frame for the impact cards
            impact_frame = tk.Frame(content_frame, bg=self.COLORS["background"])
            impact_frame.pack(fill="both", expand=True, pady=10)
            
            # Create a canvas with scrollbar for the impact cards
            canvas_frame = tk.Frame(impact_frame, bg=self.COLORS["background"])
            canvas_frame.pack(fill="both", expand=True)
            
            canvas = tk.Canvas(
                canvas_frame,
                bg=self.COLORS["background"],
                highlightthickness=0
            )
            canvas.pack(side="left", fill="both", expand=True)
            
            scrollbar = ttk.Scrollbar(
                canvas_frame,
                orient="vertical",
                command=canvas.yview
            )
            scrollbar.pack(side="right", fill="y")
            
            canvas.configure(yscrollcommand=scrollbar.set)
            canvas.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )
            
            # Create a frame inside the canvas for the content
            content_frame = tk.Frame(canvas, bg=self.COLORS["background"])
            canvas.create_window((0, 0), window=content_frame, anchor="nw")
            
            # Add impact cards for each day
            for day_impact in weather_impact["daily_impact"]:
                day_frame = tk.Frame(content_frame, bg=self.COLORS["background"])
                day_frame.pack(fill="x", pady=5, padx=10)
                
                # Format date
                date_obj = datetime.fromisoformat(day_impact['date'])
                date_str = date_obj.strftime("%A, %b %d")
                
                # Determine severity color
                severity = day_impact["severity"]
                if severity == "high":
                    severity_color = self.COLORS["error"]
                    severity_text = "High Impact"
                elif severity == "medium":
                    severity_color = self.COLORS["warning"]
                    severity_text = "Medium Impact"
                else:
                    severity_color = self.COLORS["success"]
                    severity_text = "Low Impact"
                
                # Create header frame with colored background
                header_frame = tk.Frame(day_frame, bg=severity_color)
                header_frame.pack(fill="x", pady=(0, 5))
                
                day_label = tk.Label(
                    header_frame,
                    text=date_str,
                    font=(self.FONT_FAMILY, self.FONT_SIZE_NORMAL, "bold"),
                    bg=severity_color,
                    fg="white",
                    padx=10,
                    pady=5
                )
                day_label.pack(side="left")
                
                severity_label = tk.Label(
                    header_frame,
                    text=severity_text,
                    font=(self.FONT_FAMILY, self.FONT_SIZE_NORMAL),
                    bg=severity_color,
                    fg="white",
                    padx=10,
                    pady=5
                )
                severity_label.pack(side="right")
                
                # Create details frame
                details_frame = tk.Frame(day_frame, bg=self.COLORS["background"])
                details_frame.pack(fill="x", padx=10)
                
                # Add summary
                summary_frame = tk.Frame(details_frame, bg=self.COLORS["background"])
                summary_frame.pack(fill="x", pady=5)
                
                summary_label = tk.Label(
                    summary_frame,
                    text=day_impact["summary"],
                    wraplength=550,
                    justify="left",
                    bg=self.COLORS["background"],
                    fg=self.COLORS["text"],
                    font=(self.FONT_FAMILY, self.FONT_SIZE_NORMAL)
                )
                summary_label.pack(fill="x")
                
                # Add parameter impacts
                if "parameters" in day_impact:
                    for param, impact in day_impact["parameters"].items():
                        if not impact["messages"]:
                            continue
                            
                        param_frame = tk.Frame(details_frame, bg=self.COLORS["background"])
                        param_frame.pack(fill="x", pady=5)
                        
                        # Format parameter name
                        param_name = param.replace("_", " ").title()
                        
                        # Create parameter label
                        param_label = tk.Label(
                            param_frame,
                            text=f"{param_name}:",
                            font=(self.FONT_FAMILY, self.FONT_SIZE_NORMAL, "bold"),
                            bg=self.COLORS["background"],
                            fg=self.COLORS["text"],
                            anchor="w"
                        )
                        param_label.pack(fill="x")
                        
                        # Add impact messages
                        for message in impact["messages"]:
                            message_frame = tk.Frame(param_frame, bg=self.COLORS["background"])
                            message_frame.pack(fill="x", padx=20)
                            
                            message_label = tk.Label(
                                message_frame,
                                text=f"• {message}",
                                wraplength=500,
                                justify="left",
                                bg=self.COLORS["background"],
                                fg=self.COLORS["text"],
                                font=(self.FONT_FAMILY, self.FONT_SIZE_NORMAL),
                                anchor="w"
                            )
                            message_label.pack(fill="x", pady=2)
        else:
            # No impact data available
            error_label = tk.Label(
                content_frame,
                text="Weather impact data is not available. Please check your weather service configuration.",
                wraplength=600,
                justify="center",
                bg=self.COLORS["background"],
                fg=self.COLORS["error"],
                font=(self.FONT_FAMILY, self.FONT_SIZE_NORMAL)
            )
            error_label.pack(pady=20)
    except Exception as e:
        logger.error(f"Error creating impact card: {e}")
        
        # Show error message
        error_label = tk.Label(
            content_frame,
            text=f"An error occurred while creating the weather impact analysis: {str(e)}",
            wraplength=600,
            justify="center",
            bg=self.COLORS["background"],
            fg=self.COLORS["error"],
            font=(self.FONT_FAMILY, self.FONT_SIZE_NORMAL)
        )
        error_label.pack(pady=20)
    
    # Add update location button
    update_button = ttk.Button(
        content_frame,
        text="Update Weather Location",
        command=self._update_weather_location
    )
    update_button.pack(pady=10)
    
    return card

def _update_weather_location(self):
    """Update the weather location."""
    try:
        # Show dialog to update location
        messagebox.showwarning(
            "Update Weather Location",
            "This feature is not fully implemented yet. "
            "Please update the location in the settings tab."
        )
        
        # In a real implementation, you would show a dialog to enter a new location
        # and then update the weather service with the new location
        
        # For now, just update the config with a hardcoded location
        if "weather" not in self.config:
            self.config["weather"] = {}
        
        self.config["weather"]["location"] = "Miami, FL"
        self.config["weather"]["zip_code"] = "33101"
        
        # Save the config
        self._save_config()
        
        # Show success message
        messagebox.showinfo(
            "Weather Location Updated",
            f"Weather location has been updated to {self.config['weather']['location']}."
        )
    except Exception as e:
        logger.error(f"Error updating weather location: {e}")
        messagebox.showerror(
            "Error",
            f"An error occurred while updating the weather location: {str(e)}"
        )

def _save_config(self):
    """Save the configuration to file."""
    try:
        with open("config.json", "w") as f:
            json.dump(self.config, f, indent=2)
    except Exception as e:
        logger.error(f"Error saving config: {e}")
        # In a real implementation, you would show an error message to the user

def show_historical_data(self):
    """Show historical data visualization."""
    # Clear the content frame
    self._clear_content_frame()
    
    # Set the active tab
    self._set_active_tab("historical")
    
    # Create the main frame
    historical_frame = tk.Frame(self.content_frame, bg=self.COLORS["background"])
    historical_frame.pack(fill="both", expand=True, padx=20, pady=20)
    
    # Add title and description
    self._add_page_title(
        historical_frame,
        "Historical Data Analysis",
        "Visualize and analyze your pool chemistry data over time"
    )
    
    # Create visualization frame
    visualization_frame = tk.Frame(historical_frame, bg=self.COLORS["background"])
    visualization_frame.pack(fill="both", expand=True, pady=10)
    
    # Create controls card
    controls_card = self._create_historical_controls_card(visualization_frame)
    controls_card.pack(fill="x", pady=10)
    
    # Create visualization card
    visualization_card = self._create_historical_visualization_card(visualization_frame)
    visualization_card.pack(fill="both", expand=True, pady=10)

def _create_historical_controls_card(self, parent):
    """
    Create controls for historical data visualization.
    
    Args:
        parent: Parent widget
        
    Returns:
        Card frame
    """
    # Create the card
    card, content_frame, _ = self._create_card(
        parent=parent,
        title="Visualization Controls",
        description="Select parameters and date range to visualize"
    )
    
    # Create controls frame
    controls_frame = tk.Frame(content_frame, bg=self.COLORS["background"])
    controls_frame.pack(fill="x", pady=10)
    
    # Parameter selection
    param_frame = tk.Frame(controls_frame, bg=self.COLORS["background"])
    param_frame.pack(fill="x", pady=5)
    
    param_label = tk.Label(
        param_frame,
        text="Parameters:",
        font=(self.FONT_FAMILY, self.FONT_SIZE_NORMAL, "bold"),
        bg=self.COLORS["background"],
        fg=self.COLORS["text"],
        anchor="w"
    )
    param_label.pack(fill="x")
    
    # Parameter checkboxes
    parameters = [
        {"id": "ph", "name": "pH"},
        {"id": "free_chlorine", "name": "Free Chlorine"},
        {"id": "total_chlorine", "name": "Total Chlorine"},
        {"id": "combined_chlorine", "name": "Combined Chlorine"},
        {"id": "alkalinity", "name": "Total Alkalinity"},
        {"id": "calcium_hardness", "name": "Calcium Hardness"},
        {"id": "cyanuric_acid", "name": "Cyanuric Acid"},
        {"id": "total_dissolved_solids", "name": "TDS"},
        {"id": "temperature", "name": "Temperature"}
    ]
    
    # Store parameter variables in data cache
    if "historical_params" not in self.data_cache:
        self.data_cache["historical_params"] = {}
    
    # Create checkboxes
    for param in parameters:
        param_id = param["id"]
        param_name = param["name"]
        
        # Create variable and store in cache
        var = tk.BooleanVar(value=param_id in ["ph", "free_chlorine", "total_alkalinity"])
        self.data_cache["historical_params"][param_id] = var
        
        checkbox = ttk.Checkbutton(
            param_frame,
            text=param_name,
            variable=var,
            onvalue=True,
            offvalue=False
        )
        checkbox.pack(side="left", padx=10)
    
    # Date range selection
    date_frame = tk.Frame(controls_frame, bg=self.COLORS["background"])
    date_frame.pack(fill="x", pady=10)
    
    date_label = tk.Label(
        date_frame,
        text="Date Range:",
        font=(self.FONT_FAMILY, self.FONT_SIZE_NORMAL, "bold"),
        bg=self.COLORS["background"],
        fg=self.COLORS["text"],
        anchor="w"
    )
    date_label.pack(fill="x")
    
    # Date range options
    date_ranges = [
        {"id": "week", "name": "Last 7 Days"},
        {"id": "month", "name": "Last 30 Days"},
        {"id": "quarter", "name": "Last 90 Days"},
        {"id": "year", "name": "Last 365 Days"},
        {"id": "all", "name": "All Time"}
    ]
    
    # Create variable and store in cache
    date_var = tk.StringVar(value="month")
    self.data_cache["historical_date_range"] = date_var
    
    # Create radio buttons
    for date_range in date_ranges:
        radio = ttk.Radiobutton(
            date_frame,
            text=date_range["name"],
            variable=date_var,
            value=date_range["id"]
        )
        radio.pack(side="left", padx=10)
    
    # Update button
    update_button = ttk.Button(
        controls_frame,
        text="Update Visualization",
        command=self._update_historical_visualization
    )
    update_button.pack(pady=10)
    
    return card

def _create_historical_visualization_card(self, parent):
    """
    Create card for historical data visualization.
    
    Args:
        parent: Parent widget
        
    Returns:
        Card frame
    """
    # Create the card
    card, content_frame, _ = self._create_card(
        parent=parent,
        title="Data Visualization",
        description="Visual representation of your pool chemistry data"
    )
    
    # Create a notebook for different visualization types
    notebook = ttk.Notebook(content_frame)
    notebook.pack(fill="both", expand=True, pady=10)
    
    # Create tabs for different visualization types
    time_series_tab = ttk.Frame(notebook)
    notebook.add(time_series_tab, text="Time Series")
    
    dashboard_tab = ttk.Frame(notebook)
    notebook.add(dashboard_tab, text="Dashboard")
    
    statistics_tab = ttk.Frame(notebook)
    notebook.add(statistics_tab, text="Statistics")
    
    correlation_tab = ttk.Frame(notebook)
    notebook.add(correlation_tab, text="Correlations")
    
    predictions_tab = ttk.Frame(notebook)
    notebook.add(predictions_tab, text="Predictions")
    
    # Create frames for each tab
    time_series_frame = tk.Frame(time_series_tab, bg=self.COLORS["background"])
    time_series_frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    dashboard_frame = tk.Frame(dashboard_tab, bg=self.COLORS["background"])
    dashboard_frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    statistics_frame = tk.Frame(statistics_tab, bg=self.COLORS["background"])
    statistics_frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    correlation_frame = tk.Frame(correlation_tab, bg=self.COLORS["background"])
    correlation_frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    predictions_frame = tk.Frame(predictions_tab, bg=self.COLORS["background"])
    predictions_frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    # Store frames in data cache for later access
    self.data_cache["visualization_frames"] = {
        "time_series": time_series_frame,
        "dashboard": dashboard_frame,
        "statistics": statistics_frame,
        "correlation": correlation_frame,
        "predictions": predictions_frame
    }
    
    # Add placeholder content to each tab
    for name, frame in self.data_cache["visualization_frames"].items():
        placeholder_label = tk.Label(
            frame,
            text=f"Click 'Update Visualization' to generate {name} visualization",
            font=(self.FONT_FAMILY, self.FONT_SIZE_NORMAL),
            bg=self.COLORS["background"],
            fg=self.COLORS["text"]
        )
        placeholder_label.pack(pady=50)
    
    # Create export options
    export_frame = tk.Frame(content_frame, bg=self.COLORS["background"])
    export_frame.pack(fill="x", pady=10)
    
    export_csv_button = ttk.Button(
        export_frame,
        text="Export to CSV",
        command=self._export_historical_data_csv
    )
    export_csv_button.pack(side="left", padx=10)
    
    export_pdf_button = ttk.Button(
        export_frame,
        text="Export to PDF",
        command=self._export_historical_data_pdf
    )
    export_pdf_button.pack(side="left", padx=10)
    
    return card

def _update_historical_visualization(self):
    """Update the historical data visualization."""
    # Check if we have any parameters selected
    selected_params = []
    for param_id, var in self.data_cache.get("historical_params", {}).items():
        if var.get():
            selected_params.append(param_id)
    
    if not selected_params:
        messagebox.showwarning(
            "No Parameters Selected",
            "Please select at least one parameter to visualize."
        )
        return
    
    # Get date range
    date_range = self.data_cache.get("historical_date_range", tk.StringVar()).get()
    
    # Calculate start and end dates
    end_date = datetime.now().isoformat()
    start_date = None
    
    if date_range == "week":
        start_date = (datetime.now() - timedelta(days=7)).isoformat()
    elif date_range == "month":
        start_date = (datetime.now() - timedelta(days=30)).isoformat()
    elif date_range == "quarter":
        start_date = (datetime.now() - timedelta(days=90)).isoformat()
    elif date_range == "year":
        start_date = (datetime.now() - timedelta(days=365)).isoformat()
    elif date_range == "all":
        messagebox.showinfo(
            "All Time Range",
            "Showing all available data. This may take a moment to load."
        )
        start_date = (datetime.now() - timedelta(days=30)).isoformat()
    
    try:
        # In a real implementation, you would fetch data from the database
        # For now, we'll generate some sample data
        data = self._generate_sample_historical_data(selected_params, start_date, end_date)
        
        # Update each visualization
        self._update_time_series_chart(data, selected_params)
        self._update_dashboard_chart(data, selected_params)
        self._update_statistics_chart(data, selected_params)
        self._update_correlation_chart(data, selected_params)
        self._update_predictions_chart(data, selected_params)
        
        # Show success message if no data
        if not data:
            for name, frame in self.data_cache["visualization_frames"].items():
                # Clear frame
                for widget in frame.winfo_children():
                    widget.destroy()
                
                # Add message
                message_label = tk.Label(
                    frame,
                    text="No data available for the selected parameters and date range.",
                    font=(self.FONT_FAMILY, self.FONT_SIZE_NORMAL),
                    bg=self.COLORS["background"],
                    fg=self.COLORS["text"]
                )
                message_label.pack(pady=50)
    except Exception as e:
        logger.error(f"Error updating historical visualization: {e}")
        messagebox.showerror(
            "Error",
            f"An error occurred while updating the visualization: {str(e)}"
        )

def _generate_sample_historical_data(self, parameters, start_date, end_date):
    """
    Generate sample historical data for visualization.
    
    Args:
        parameters: List of parameter IDs
        start_date: Start date in ISO format
        end_date: End date in ISO format
        
    Returns:
        Dictionary of parameter data
    """
    # In a real implementation, you would fetch data from the database
    # For now, we'll generate some sample data
    
    # This is just a placeholder implementation
    # In a real application, you would query your database for actual data
    
    # Return sample data
    return {
        "ph": [
            {"timestamp": "2023-01-01T12:00:00", "value": 7.2},
            {"timestamp": "2023-01-02T12:00:00", "value": 7.4},
            {"timestamp": "2023-01-03T12:00:00", "value": 7.3},
            {"timestamp": "2023-01-04T12:00:00", "value": 7.5},
            {"timestamp": "2023-01-05T12:00:00", "value": 7.6}
        ],
        "free_chlorine": [
            {"timestamp": "2023-01-01T12:00:00", "value": 1.5},
            {"timestamp": "2023-01-02T12:00:00", "value": 1.2},
            {"timestamp": "2023-01-03T12:00:00", "value": 1.8},
            {"timestamp": "2023-01-04T12:00:00", "value": 2.0},
            {"timestamp": "2023-01-05T12:00:00", "value": 1.7}
        ],
        "total_alkalinity": [
            {"timestamp": "2023-01-01T12:00:00", "value": 90},
            {"timestamp": "2023-01-02T12:00:00", "value": 95},
            {"timestamp": "2023-01-03T12:00:00", "value": 100},
            {"timestamp": "2023-01-04T12:00:00", "value": 105},
            {"timestamp": "2023-01-05T12:00:00", "value": 100}
        ]
    }

def _update_time_series_chart(self, data, selected_params):
    """
    Update the time series chart.
    
    Args:
        data: Dictionary of parameter data
        selected_params: List of selected parameter IDs
    """
    # Get the frame
    frame = self.data_cache["visualization_frames"]["time_series"]
    
    # Clear frame
    for widget in frame.winfo_children():
        widget.destroy()
    
    try:
        # Create a chart (in a real implementation, you would use matplotlib)
        # For now, we'll just create a placeholder image
        chart_path = "time_series_chart.png"
        
        # In a real implementation, you would generate the chart here
        # For now, we'll just use a placeholder image
        
        # Load the image
        chart_image = Image.open(chart_path)
        chart_photo = ImageTk.PhotoImage(chart_image)
        
        # Display the image
        chart_label = tk.Label(
            frame,
            image=chart_photo,
            bg=self.COLORS["background"]
        )
        chart_label.image = chart_photo  # Keep a reference to prevent garbage collection
        chart_label.pack(pady=10)
    except Exception as e:
        logger.error(f"Error creating time series chart: {e}")
        
        error_label = tk.Label(
            frame,
            text=f"Error creating time series chart: {str(e)}",
            font=(self.FONT_FAMILY, self.FONT_SIZE_NORMAL),
            bg=self.COLORS["background"],
            fg=self.COLORS["error"]
        )
        error_label.pack(pady=50)

def _update_dashboard_chart(self, data, selected_params):
    """
    Update the dashboard chart.
    
    Args:
        data: Dictionary of parameter data
        selected_params: List of selected parameter IDs
    """
    # Get the frame
    frame = self.data_cache["visualization_frames"]["dashboard"]
    
    # Clear frame
    for widget in frame.winfo_children():
        widget.destroy()
    
    try:
        # Create a chart (in a real implementation, you would use matplotlib)
        # For now, we'll just create a placeholder image
        chart_path = "dashboard_chart.png"
        
        # In a real implementation, you would generate the chart here
        # For now, we'll just use a placeholder image
        
        # Load the image
        chart_image = Image.open(chart_path)
        chart_photo = ImageTk.PhotoImage(chart_image)
        
        # Display the image
        chart_label = tk.Label(
            frame,
            image=chart_photo,
            bg=self.COLORS["background"]
        )
        chart_label.image = chart_photo  # Keep a reference to prevent garbage collection
        chart_label.pack(pady=10)
    except Exception as e:
        logger.error(f"Error creating dashboard chart: {e}")
        
        error_label = tk.Label(
            frame,
            text=f"Error creating dashboard chart: {str(e)}",
            font=(self.FONT_FAMILY, self.FONT_SIZE_NORMAL),
            bg=self.COLORS["background"],
            fg=self.COLORS["error"]
        )
        error_label.pack(pady=50)

def _update_statistics_chart(self, data, selected_params):
    """
    Update the statistics chart.
    
    Args:
        data: Dictionary of parameter data
        selected_params: List of selected parameter IDs
    """
    # Get the frame
    frame = self.data_cache["visualization_frames"]["statistics"]
    
    # Clear frame
    for widget in frame.winfo_children():
        widget.destroy()
    
    try:
        # Create a chart (in a real implementation, you would use matplotlib)
        # For now, we'll just create a placeholder image
        chart_path = "statistics_chart.png"
        
        # In a real implementation, you would generate the chart here
        # For now, we'll just use a placeholder image
        
        # Load the image
        chart_image = Image.open(chart_path)
        chart_photo = ImageTk.PhotoImage(chart_image)
        
        # Display the image
        chart_label = tk.Label(
            frame,
            image=chart_photo,
            bg=self.COLORS["background"]
        )
        chart_label.image = chart_photo  # Keep a reference to prevent garbage collection
        chart_label.pack(pady=10)
    except Exception as e:
        logger.error(f"Error creating statistics chart: {e}")
        
        error_label = tk.Label(
            frame,
            text=f"Error creating statistics chart: {str(e)}",
            font=(self.FONT_FAMILY, self.FONT_SIZE_NORMAL),
            bg=self.COLORS["background"],
            fg=self.COLORS["error"]
        )
        error_label.pack(pady=50)

def _update_correlation_chart(self, data, selected_params):
    """
    Update the correlation chart.
    
    Args:
        data: Dictionary of parameter data
        selected_params: List of selected parameter IDs
    """
    # Get the frame
    frame = self.data_cache["visualization_frames"]["correlation"]
    
    # Clear frame
    for widget in frame.winfo_children():
        widget.destroy()
    
    try:
        # Create a chart (in a real implementation, you would use matplotlib)
        # For now, we'll just create a placeholder image
        chart_path = "correlation_chart.png"
        
        # In a real implementation, you would generate the chart here
        # For now, we'll just use a placeholder image
        
        # Load the image
        chart_image = Image.open(chart_path)
        chart_photo = ImageTk.PhotoImage(chart_image)
        
        # Display the image
        chart_label = tk.Label(
            frame,
            image=chart_photo,
            bg=self.COLORS["background"]
        )
        chart_label.image = chart_photo  # Keep a reference to prevent garbage collection
        chart_label.pack(pady=10)
    except Exception as e:
        logger.error(f"Error creating correlation chart: {e}")
        
        error_label = tk.Label(
            frame,
            text=f"Error creating correlation chart: {str(e)}",
            font=(self.FONT_FAMILY, self.FONT_SIZE_NORMAL),
            bg=self.COLORS["background"],
            fg=self.COLORS["error"]
        )
        error_label.pack(pady=50)

def _update_predictions_chart(self, data, selected_params):
    """
    Update the predictions chart and insights.
    
    Args:
        data: Dictionary of parameter data
        selected_params: List of selected parameter IDs
    """
    # Get the frame
    frame = self.data_cache["visualization_frames"]["predictions"]
    
    # Clear frame
    for widget in frame.winfo_children():
        widget.destroy()
    
    try:
        # Create a scrollable canvas for predictions
        canvas_frame = tk.Frame(frame, bg=self.COLORS["background"])
        canvas_frame.pack(fill="both", expand=True)
        
        canvas = tk.Canvas(
            canvas_frame,
            bg=self.COLORS["background"],
            highlightthickness=0
        )
        canvas.pack(side="left", fill="both", expand=True)
        
        scrollbar = ttk.Scrollbar(
            canvas_frame,
            orient="vertical",
            command=canvas.yview
        )
        scrollbar.pack(side="right", fill="y")
        
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        # Create a frame inside the canvas for the content
        content_frame = tk.Frame(canvas, bg=self.COLORS["background"])
        canvas.create_window((0, 0), window=content_frame, anchor="nw")
        
        # Add header
        header_label = tk.Label(
            content_frame,
            text="AI-Powered Predictions and Insights",
            font=(self.FONT_FAMILY, self.FONT_SIZE_LARGE, "bold"),
            bg=self.COLORS["background"],
            fg=self.COLORS["primary"],
            anchor="w"
        )
        header_label.pack(fill="x", pady=(0, 10))
        
        # Add description
        description_label = tk.Label(
            content_frame,
            text="Based on your historical data, our AI system has generated the following predictions and insights for your pool chemistry. These predictions can help you anticipate changes and take proactive measures to maintain optimal water quality.",
            wraplength=600,
            justify="left",
            bg=self.COLORS["background"],
            fg=self.COLORS["text"],
            font=(self.FONT_FAMILY, self.FONT_SIZE_NORMAL),
            anchor="w"
        )
        description_label.pack(fill="x", pady=(0, 20))
        
        # Check if we have enough data for predictions
        if data and all(len(data.get(param, [])) >= 3 for param in selected_params):
            # Process data for predictions
            processed_data = {}
            for param in selected_params:
                if param in data:
                    processed_data[param] = []
                    for item in data[param]:
                        processed_data[param].append({
                            "timestamp": datetime.fromisoformat(item["timestamp"]),
                            "value": item["value"]
                        })
            
            # Generate predictions for each parameter
            predictions = {}
            for param in selected_params:
                if param in processed_data and len(processed_data[param]) >= 3:
                    # In a real implementation, you would use a proper prediction algorithm
                    # For now, we'll just use a simple linear extrapolation
                    
                    # Get the last few data points
                    last_points = processed_data[param][-3:]
                    
                    # Calculate average change
                    changes = []
                    for i in range(1, len(last_points)):
                        changes.append(last_points[i]["value"] - last_points[i-1]["value"])
                    
                    avg_change = sum(changes) / len(changes)
                    
                    # Generate predictions for the next 7 days
                    predictions[param] = []
                    last_value = last_points[-1]["value"]
                    last_date = last_points[-1]["timestamp"]
                    
                    for i in range(1, 8):
                        next_date = last_date + timedelta(days=i)
                        next_value = last_value + (avg_change * i)
                        
                        # Add some randomness to make it more realistic
                        import random
                        next_value += random.uniform(-0.1, 0.1)
                        
                        predictions[param].append({
                            "timestamp": next_date,
                            "value": next_value
                        })
            
            # Display predictions for each parameter
            for param in selected_params:
                if param in predictions:
                    # Create a frame for this parameter
                    param_content = ttk.LabelFrame(
                        content_frame,
                        text=param.replace("_", " ").title(),
                        padding=10
                    )
                    param_content.pack(fill="x", pady=10)
                    
                    # Add trend visualization
                    trend_frame = tk.Frame(param_content, bg=self.COLORS["background"])
                    trend_frame.pack(fill="x", pady=5)
                    
                    trend_label = tk.Label(
                        trend_frame,
                        text="Trend Analysis:",
                        font=(self.FONT_FAMILY, self.FONT_SIZE_NORMAL, "bold"),
                        bg=self.COLORS["background"],
                        fg=self.COLORS["text"],
                        anchor="w"
                    )
                    trend_label.pack(fill="x")
                    
                    # In a real implementation, you would create a proper trend visualization
                    # For now, we'll just use a simple canvas
                    trend_canvas = tk.Canvas(
                        trend_frame,
                        width=600,
                        height=100,
                        bg="white"
                    )
                    trend_canvas.pack(fill="x", pady=5)
                    
                    # Draw a simple trend line
                    # In a real implementation, you would use matplotlib or another charting library
                    trend_canvas.create_line(
                        50, 50,
                        550, 30,
                        fill=self.COLORS["primary"],
                        width=2
                    )
                    
                    # Add table of predicted values
                    table_frame = tk.Frame(param_content, bg=self.COLORS["background"])
                    table_frame.pack(fill="x", pady=10)
                    
                    # Create header row
                    header_frame = tk.Frame(table_frame, bg=self.COLORS["primary_light"])
                    header_frame.pack(fill="x")
                    
                    date_header = tk.Label(
                        header_frame,
                        text="Date",
                        font=(self.FONT_FAMILY, self.FONT_SIZE_NORMAL, "bold"),
                        bg=self.COLORS["primary_light"],
                        fg=self.COLORS["text"],
                        width=15,
                        anchor="w",
                        padx=5,
                        pady=5
                    )
                    date_header.pack(side="left")
                    
                    value_header = tk.Label(
                        header_frame,
                        text="Predicted Value",
                        font=(self.FONT_FAMILY, self.FONT_SIZE_NORMAL, "bold"),
                        bg=self.COLORS["primary_light"],
                        fg=self.COLORS["text"],
                        width=15,
                        anchor="w",
                        padx=5,
                        pady=5
                    )
                    value_header.pack(side="left")
                    
                    # Add data rows
                    for i, pred in enumerate(predictions[param]):
                        row_frame = tk.Frame(
                            table_frame,
                            bg=self.COLORS["background"] if i % 2 == 0 else self.COLORS["secondary_light"]
                        )
                        row_frame.pack(fill="x")
                        
                        date_label = tk.Label(
                            row_frame,
                            text=pred["timestamp"].strftime("%Y-%m-%d"),
                            font=(self.FONT_FAMILY, self.FONT_SIZE_NORMAL),
                            bg=row_frame["bg"],
                            fg=self.COLORS["text"],
                            width=15,
                            anchor="w",
                            padx=5,
                            pady=5
                        )
                        date_label.pack(side="left")
                        
                        value_label = tk.Label(
                            row_frame,
                            text=f"{pred['value']:.2f}",
                            font=(self.FONT_FAMILY, self.FONT_SIZE_NORMAL),
                            bg=row_frame["bg"],
                            fg=self.COLORS["text"],
                            width=15,
                            anchor="w",
                            padx=5,
                            pady=5
                        )
                        value_label.pack(side="left")
                    
                    # Add insights
                    insights_frame = tk.Frame(param_content, bg=self.COLORS["background"])
                    insights_frame.pack(fill="x", pady=10)
                    
                    insights_label = tk.Label(
                        insights_frame,
                        text="AI Insights:",
                        font=(self.FONT_FAMILY, self.FONT_SIZE_NORMAL, "bold"),
                        bg=self.COLORS["background"],
                        fg=self.COLORS["text"],
                        anchor="w"
                    )
                    insights_label.pack(fill="x")
                    
                    # Generate insights based on the predictions
                    insights = []
                    
                    # Check for trends
                    first_val = predictions[param][0]["value"]
                    last_val = predictions[param][-1]["value"]
                    
                    if last_val > first_val * 1.1:
                        insights.append(f"The {param.replace('_', ' ')} is predicted to increase significantly over the next week.")
                    elif last_val < first_val * 0.9:
                        insights.append(f"The {param.replace('_', ' ')} is predicted to decrease significantly over the next week.")
                    else:
                        insights.append(f"The {param.replace('_', ' ')} is predicted to remain relatively stable over the next week.")
                    
                    # Check for ideal ranges
                    # In a real implementation, you would use the actual ideal ranges for each parameter
                    if param == "ph":
                        if last_val < 7.2:
                            insights.append("The pH is predicted to fall below the ideal range. Consider adding pH increaser.")
                        elif last_val > 7.8:
                            insights.append("The pH is predicted to rise above the ideal range. Consider adding pH decreaser.")
                    elif param == "free_chlorine":
                        if last_val < 1.0:
                            insights.append("The free chlorine is predicted to fall below the ideal range. Consider adding chlorine.")
                        elif last_val > 3.0:
                            insights.append("The free chlorine is predicted to rise above the ideal range. Consider reducing chlorine addition.")
                    
                    # Add insights to the frame
                    for insight in insights:
                        insight_label = tk.Label(
                            insights_frame,
                            text=f"• {insight}",
                            wraplength=550,
                            justify="left",
                            bg=self.COLORS["background"],
                            fg=self.COLORS["text"],
                            font=(self.FONT_FAMILY, self.FONT_SIZE_NORMAL),
                            anchor="w"
                        )
                        insight_label.pack(fill="x", pady=2)
                else:
                    # Not enough data for this parameter
                    not_enough_label = tk.Label(
                        content_frame,
                        text=f"Not enough data for {param.replace('_', ' ')} predictions.",
                        font=(self.FONT_FAMILY, self.FONT_SIZE_NORMAL),
                        bg=self.COLORS["background"],
                        fg=self.COLORS["warning"],
                        anchor="w"
                    )
                    not_enough_label.pack(fill="x", pady=5)
            
            # Add overall recommendations
            recommendations_label = tk.Label(
                content_frame,
                text="Overall Recommendations:",
                font=(self.FONT_FAMILY, self.FONT_SIZE_NORMAL, "bold"),
                bg=self.COLORS["background"],
                fg=self.COLORS["text"],
                anchor="w"
            )
            recommendations_label.pack(fill="x", pady=(20, 5))
            
            # In a real implementation, you would generate recommendations based on the predictions
            # For now, we'll just use some generic recommendations
            recommendations = [
                "Monitor your pool chemistry regularly to ensure it stays within ideal ranges.",
                "Consider adjusting your chemical addition schedule based on the predicted trends.",
                "Weather changes may impact your pool chemistry. Be prepared to make adjustments as needed.",
                "Regular maintenance will help prevent issues before they become problems."
            ]
            
            # Add recommendations to the frame
            recommendations_content = ttk.LabelFrame(content_frame, text="Recommendations", padding=10)
            recommendations_content.pack(fill="x", pady=10)
            
            for rec in recommendations:
                rec_frame = tk.Frame(recommendations_content, bg=self.COLORS["background"])
                rec_frame.pack(fill="x", pady=2)
                
                rec_label = tk.Label(
                    rec_frame,
                    text=f"• {rec}",
                    wraplength=550,
                    justify="left",
                    bg=self.COLORS["background"],
                    fg=self.COLORS["text"],
                    font=(self.FONT_FAMILY, self.FONT_SIZE_NORMAL),
                    anchor="w"
                )
                rec_label.pack(fill="x")
        else:
            # Not enough data for predictions
            not_enough_label = tk.Label(
                content_frame,
                text="Not enough data for AI predictions. Please ensure you have at least 3 data points for each selected parameter.",
                wraplength=600,
                justify="center",
                bg=self.COLORS["background"],
                fg=self.COLORS["warning"],
                font=(self.FONT_FAMILY, self.FONT_SIZE_NORMAL)
            )
            not_enough_label.pack(pady=50)
    except Exception as e:
        logger.error(f"Error generating AI predictions: {e}")
        
        error_label = tk.Label(
            frame,
            text=f"Error generating AI predictions: {str(e)}",
            font=(self.FONT_FAMILY, self.FONT_SIZE_NORMAL),
            bg=self.COLORS["background"],
            fg=self.COLORS["error"]
        )
        error_label.pack(pady=50)

def _export_historical_data_csv(self):
    """Export historical data to CSV."""
    # Check if we have any parameters selected
    selected_params = []
    for param_id, var in self.data_cache.get("historical_params", {}).items():
        if var.get():
            selected_params.append(param_id)
    
    if not selected_params:
        messagebox.showwarning(
            "No Parameters Selected",
            "Please select at least one parameter to export."
        )
        return
    
    # Get date range
    date_range = self.data_cache.get("historical_date_range", tk.StringVar()).get()
    
    # Calculate start and end dates
    end_date = datetime.now().isoformat()
    start_date = None
    
    if date_range == "week":
        start_date = (datetime.now() - timedelta(days=7)).isoformat()
    elif date_range == "month":
        start_date = (datetime.now() - timedelta(days=30)).isoformat()
    elif date_range == "quarter":
        start_date = (datetime.now() - timedelta(days=90)).isoformat()
    elif date_range == "year":
        start_date = (datetime.now() - timedelta(days=365)).isoformat()
    
    # Ask for save location
    file_path = filedialog.asksaveasfilename(
        defaultextension=".csv",
        filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")],
        title="Save CSV File"
    )
    
    if not file_path:
        return
    
    try:
        # In a real implementation, you would fetch data from the database and write it to CSV
        # For now, we'll just create a placeholder file
        with open(file_path, "w") as f:
            # Write header
            f.write("Date,Parameter,Value\n")
            
            # Write sample data
            f.write("2023-01-01,pH,7.2\n")
            f.write("2023-01-02,pH,7.4\n")
            f.write("2023-01-01,Free Chlorine,1.5\n")
            f.write("2023-01-02,Free Chlorine,1.2\n")
        
        # Show success message
        messagebox.showinfo(
            "Export Successful",
            f"Data has been exported to {file_path}"
        )
    except Exception as e:
        logger.error(f"Error exporting data to CSV: {e}")
        messagebox.showerror(
            "Export Error",
            f"An error occurred while exporting data: {str(e)}"
        )

def _export_historical_data_pdf(self):
    """Export historical data to PDF."""
    # Check if we have any parameters selected
    selected_params = []
    for param_id, var in self.data_cache.get("historical_params", {}).items():
        if var.get():
            selected_params.append(param_id)
    
    if not selected_params:
        messagebox.showwarning(
            "No Parameters Selected",
            "Please select at least one parameter to export."
        )
        return
    
    # Get date range
    date_range = self.data_cache.get("historical_date_range", tk.StringVar()).get()
    
    # Calculate start and end dates
    end_date = datetime.now().isoformat()
    start_date = None
    
    if date_range == "week":
        start_date = (datetime.now() - timedelta(days=7)).isoformat()
    elif date_range == "month":
        start_date = (datetime.now() - timedelta(days=30)).isoformat()
    elif date_range == "quarter":
        start_date = (datetime.now() - timedelta(days=90)).isoformat()
    elif date_range == "year":
        start_date = (datetime.now() - timedelta(days=365)).isoformat()
    
    # Ask for save location
    file_path = filedialog.asksaveasfilename(
        defaultextension=".pdf",
        filetypes=[("PDF Files", "*.pdf"), ("All Files", "*.*")],
        title="Save PDF File"
    )
    
    if not file_path:
        return
    
    try:
        # In a real implementation, you would generate a PDF with the data and charts
        # For now, we'll just create a placeholder file
        with open(file_path, "w") as f:
            f.write("This is a placeholder PDF file.\n")
            f.write("In a real implementation, this would contain formatted data and charts.\n")
        
        # Show success message
        messagebox.showinfo(
            "Export Successful",
            f"Data has been exported to {file_path}"
        )
    except Exception as e:
        logger.error(f"Error exporting data to PDF: {e}")
        messagebox.showerror(
            "Export Error",
            f"An error occurred while exporting data: {str(e)}"
        )

def show_maintenance_log(self):
    """Show maintenance log interface."""
    # Clear the content frame
    self._clear_content_frame()
    
    # Set the active tab
    self._set_active_tab("maintenance")
    
    # Create the main frame
    maintenance_frame = tk.Frame(self.content_frame, bg=self.COLORS["background"])
    maintenance_frame.pack(fill="both", expand=True, padx=20, pady=20)
    
    # Add title and description
    self._add_page_title(
        maintenance_frame,
        "Maintenance Log",
        "Track and manage your pool maintenance activities"
    )
    
    # Create log list frame
    log_frame = tk.Frame(maintenance_frame, bg=self.COLORS["background"])
    log_frame.pack(fill="both", expand=True, side="left", padx=(0, 10))
    
    # Create form frame
    form_frame = tk.Frame(maintenance_frame, bg=self.COLORS["background"])
    form_frame.pack(fill="y", side="right", padx=(10, 0))
    
    # Create log list card
    log_list_card = self._create_maintenance_log_list_card(log_frame)
    log_list_card.pack(fill="both", expand=True)
    
    # Create form card
    form_card = self._create_maintenance_form_card(form_frame)
    form_card.pack(fill="both")

def _create_maintenance_log_list_card(self, parent):
    """
    Create card for maintenance log list.
    
    Args:
        parent: Parent widget
        
    Returns:
        Card frame
    """
    # Create the card
    card, content_frame, _ = self._create_card(
        parent=parent,
        title="Maintenance History",
        description="View and manage your maintenance activities"
    )
    
    # Create controls frame
    controls_frame = tk.Frame(content_frame, bg=self.COLORS["background"])
    controls_frame.pack(fill="x", pady=10)
    
    # Add search controls
    # In a real implementation, you would add search functionality
    # For now, we'll just add placeholder controls
    
    # Add search button
    search_button = ttk.Button(
        controls_frame,
        text="Search Logs",
        command=lambda: None  # Placeholder
    )
    search_button.pack(side="left", padx=5)
    
    # Add add button
    add_button = ttk.Button(
        controls_frame,
        text="Add New Entry",
        command=self._show_maintenance_form
    )
    add_button.pack(side="right", padx=5)
    
    # Create log list frame
    log_list_frame = tk.Frame(content_frame, bg=self.COLORS["background"])
    log_list_frame.pack(fill="both", expand=True, pady=10)
    
    # Create a scrollable canvas for the log list
    canvas_frame = tk.Frame(log_list_frame, bg=self.COLORS["background"])
    canvas_frame.pack(fill="both", expand=True)
    
    canvas = tk.Canvas(
        canvas_frame,
        bg=self.COLORS["background"],
        highlightthickness=0
    )
    canvas.pack(side="left", fill="both", expand=True)
    
    scrollbar = ttk.Scrollbar(
        canvas_frame,
        orient="vertical",
        command=canvas.yview
    )
    scrollbar.pack(side="right", fill="y")
    
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    
    # Create a frame inside the canvas for the content
    entries_frame = tk.Frame(canvas, bg=self.COLORS["background"])
    canvas.create_window((0, 0), window=entries_frame, anchor="nw")
    
    # Store the entries frame in the data cache
    self.data_cache["maintenance_entries_frame"] = entries_frame
    
    # Load maintenance logs
    self._load_maintenance_logs()
    
    return card

def _create_maintenance_form_card(self, parent):
    """
    Create card for maintenance form.
    
    Args:
        parent: Parent widget
        
    Returns:
        Card frame
    """
    # Create the card
    card, content_frame, card_title = self._create_card(
        parent=parent,
        title="Add Maintenance Entry",
        description="Record a new maintenance activity"
    )
    
    # Store the card title in the data cache
    self.data_cache["maintenance_form_title"] = card_title
    
    # Create form frame
    form_frame = tk.Frame(content_frame, bg=self.COLORS["background"])
    form_frame.pack(fill="both", expand=True, pady=10)
    
    # Date field
    date_frame = tk.Frame(form_frame, bg=self.COLORS["background"])
    date_frame.pack(fill="x", pady=5)
    
    date_label = tk.Label(
        date_frame,
        text="Date:",
        font=(self.FONT_FAMILY, self.FONT_SIZE_NORMAL, "bold"),
        bg=self.COLORS["background"],
        fg=self.COLORS["text"],
        anchor="w",
        width=15
    )
    date_label.pack(side="left")
    
    # Get current date
    current_date = datetime.now().strftime("%Y-%m-%d")
    date_var = tk.StringVar(value=current_date)
    
    date_entry = ttk.Entry(
        date_frame,
        textvariable=date_var,
        width=20
    )
    date_entry.pack(side="left", padx=5)
    
    # Store the date variable in the data cache
    self.data_cache["maintenance_date"] = date_var
    
    # Action field
    action_frame = tk.Frame(form_frame, bg=self.COLORS["background"])
    action_frame.pack(fill="x", pady=5)
    
    action_label = tk.Label(
        action_frame,
        text="Action:",
        font=(self.FONT_FAMILY, self.FONT_SIZE_NORMAL, "bold"),
        bg=self.COLORS["background"],
        fg=self.COLORS["text"],
        anchor="w",
        width=15
    )
    action_label.pack(side="left")
    
    action_var = tk.StringVar()
    
    # Define common maintenance actions
    actions = [
        "Filter Cleaning",
        "Filter Replacement",
        "Chemical Addition",
        "Water Testing",
        "Skimming",
        "Vacuuming",
        "Pump Maintenance",
        "Heater Maintenance",
        "Other"
    ]
    
    action_combo = ttk.Combobox(
        action_frame,
        textvariable=action_var,
        values=actions,
        width=20
    )
    action_combo.pack(side="left", padx=5)
    
    # Store the action variable in the data cache
    self.data_cache["maintenance_action"] = action_var
    
    # Details field
    details_frame = tk.Frame(form_frame, bg=self.COLORS["background"])
    details_frame.pack(fill="x", pady=5)
    
    details_label = tk.Label(
        details_frame,
        text="Details:",
        font=(self.FONT_FAMILY, self.FONT_SIZE_NORMAL, "bold"),
        bg=self.COLORS["background"],
        fg=self.COLORS["text"],
        anchor="w",
        width=15
    )
    details_label.pack(side="left", anchor="n")
    
    details_var = tk.StringVar()
    
    details_entry = tk.Text(
        details_frame,
        width=30,
        height=5
    )
    details_entry.pack(side="left", padx=5)
    
    # Store the details entry in the data cache
    self.data_cache["maintenance_details"] = details_entry
    
    # Performed by field
    performed_frame = tk.Frame(form_frame, bg=self.COLORS["background"])
    performed_frame.pack(fill="x", pady=5)
    
    performed_label = tk.Label(
        performed_frame,
        text="Performed By:",
        font=(self.FONT_FAMILY, self.FONT_SIZE_NORMAL, "bold"),
        bg=self.COLORS["background"],
        fg=self.COLORS["text"],
        anchor="w",
        width=15
    )
    performed_label.pack(side="left")
    
    performed_var = tk.StringVar()
    
    performed_entry = ttk.Entry(
        performed_frame,
        textvariable=performed_var,
        width=20
    )
    performed_entry.pack(side="left", padx=5)
    
    # Store the performed by variable in the data cache
    self.data_cache["maintenance_performed_by"] = performed_var
    
    # Buttons
    button_frame = tk.Frame(form_frame, bg=self.COLORS["background"])
    button_frame.pack(fill="x", pady=10)
    
    cancel_button = ttk.Button(
        button_frame,
        text="Cancel",
        command=self._clear_maintenance_form
    )
    cancel_button.pack(side="left", padx=5)
    
    save_button = ttk.Button(
        button_frame,
        text="Save",
        command=self._save_maintenance_entry
    )
    save_button.pack(side="right", padx=5)
    
    # Store the entry ID for editing
    self.data_cache["maintenance_entry_id"] = None
    
    return card

def _load_maintenance_logs(self):
    """Load maintenance logs from the database."""
    try:
        # Get the entries frame
        entries_frame = self.data_cache.get("maintenance_entries_frame")
        
        if not entries_frame:
            return
        
        # Clear the frame
        for widget in entries_frame.winfo_children():
            widget.destroy()
        
        # In a real implementation, you would fetch logs from the database
        # For now, we'll just create some sample logs
        logs = self.data_cache.get("maintenance_logs", [])
        
        if not logs:
            # Create sample logs if none exist
            logs = [
                {
                    "id": "1",
                    "timestamp": "2023-01-01T10:00:00",
                    "action": "Filter Cleaning",
                    "details": "Cleaned filter with hose and filter cleaner solution.",
                    "performed_by": "John Doe"
                },
                {
                    "id": "2",
                    "timestamp": "2023-01-15T14:30:00",
                    "action": "Chemical Addition",
                    "details": "Added 2 cups of chlorine and 1 cup of pH increaser.",
                    "performed_by": "Jane Smith"
                }
            ]
            self.data_cache["maintenance_logs"] = logs
        
        if not logs:
            # No logs available
            no_logs_label = tk.Label(
                entries_frame,
                text="No maintenance logs available.",
                font=(self.FONT_FAMILY, self.FONT_SIZE_NORMAL),
                bg=self.COLORS["background"],
                fg=self.COLORS["text"]
            )
            no_logs_label.pack(pady=50)
            return
        
        # Display logs
        self._display_maintenance_logs(logs)
    except Exception as e:
        # Handle error
        self._handle_maintenance_log_error(e)

def _display_maintenance_logs(self, logs):
    """
    Display maintenance logs in the entries frame.
    
    Args:
        logs: List of maintenance log dictionaries
    """
    try:
        # Get the entries frame
        entries_frame = self.data_cache.get("maintenance_entries_frame")
        
        if not entries_frame:
            return
        
        # Clear the frame
        for widget in entries_frame.winfo_children():
            widget.destroy()
        
        if not logs:
            # No logs available
            no_logs_label = tk.Label(
                entries_frame,
                text="No maintenance logs available.",
                font=(self.FONT_FAMILY, self.FONT_SIZE_NORMAL),
                bg=self.COLORS["background"],
                fg=self.COLORS["text"]
            )
            no_logs_label.pack(pady=50)
            return
        
        # Display each log
        for log in logs:
            # Create a frame for this log
            log_frame = tk.Frame(
                entries_frame,
                bg=self.COLORS["background"],
                bd=1,
                relief="solid",
                padx=10,
                pady=10
            )
            log_frame.pack(fill="x", pady=5, padx=5)
            
            # Format timestamp
            timestamp = datetime.fromisoformat(log["timestamp"])
            date_str = timestamp.strftime("%Y-%m-%d %H:%M")
            
            # Create header frame
            header_frame = tk.Frame(log_frame, bg=self.COLORS["primary_light"])
            header_frame.pack(fill="x", pady=(0, 5))
            
            date_label = tk.Label(
                header_frame,
                text=date_str,
                font=(self.FONT_FAMILY, self.FONT_SIZE_NORMAL, "bold"),
                bg=header_frame["bg"],
                fg=self.COLORS["text"],
                padx=5,
                pady=5
            )
            date_label.pack(side="left")
            
            action_label = tk.Label(
                header_frame,
                text=log["action"],
                font=(self.FONT_FAMILY, self.FONT_SIZE_NORMAL, "bold"),
                bg=header_frame["bg"],
                fg=self.COLORS["text"],
                padx=5,
                pady=5
            )
            action_label.pack(side="right")
            
            # Add details if available
            if log.get("details"):
                details_frame = tk.Frame(log_frame, bg=log_frame["bg"])
                details_frame.pack(fill="x", pady=5)
                
                details_label = tk.Label(
                    details_frame,
                    text=log["details"],
                    wraplength=500,
                    justify="left",
                    bg=details_frame["bg"],
                    fg=self.COLORS["text"],
                    font=(self.FONT_FAMILY, self.FONT_SIZE_NORMAL),
                    anchor="w"
                )
                details_label.pack(fill="x")
            
            # Add footer with performed by and buttons
            footer_frame = tk.Frame(log_frame, bg=log_frame["bg"])
            footer_frame.pack(fill="x", pady=5)
            
            if log.get("performed_by"):
                performed_label = tk.Label(
                    footer_frame,
                    text=f"Performed by: {log['performed_by']}",
                    font=(self.FONT_FAMILY, self.FONT_SIZE_NORMAL, "italic"),
                    bg=footer_frame["bg"],
                    fg=self.COLORS["text"],
                    anchor="w"
                )
                performed_label.pack(side="left")
            
            # Add edit button
            edit_button = ttk.Button(
                footer_frame,
                text="Edit",
                command=lambda log_id=log["id"]: self._edit_maintenance_entry(log_id)
            )
            edit_button.pack(side="right", padx=5)
            
            # Add delete button
            delete_button = ttk.Button(
                footer_frame,
                text="Delete",
                command=lambda log_id=log["id"]: self._delete_maintenance_entry(log_id)
            )
            delete_button.pack(side="right", padx=5)
    except Exception as e:
        # Handle error
        self._handle_maintenance_log_error(e)

def _handle_maintenance_log_error(self, error):
    """
    Handle errors in maintenance log operations.
    
    Args:
        error: The exception that occurred
    """
    logger.error(f"Error loading maintenance logs: {error}")
    
    # Get the entries frame
    entries_frame = self.data_cache.get("maintenance_entries_frame")
    
    if entries_frame:
        # Clear the frame
        for widget in entries_frame.winfo_children():
            widget.destroy()
        
        # Show error message
        error_label = tk.Label(
            entries_frame,
            text=f"An error occurred: {str(error)}",
            font=(self.FONT_FAMILY, self.FONT_SIZE_NORMAL),
            bg=self.COLORS["background"],
            fg=self.COLORS["error"]
        )
        error_label.pack(pady=50)

def _show_maintenance_form(self):
    """Show the maintenance form for adding a new entry."""
    # Update the form title
    card_title = self.data_cache.get("maintenance_form_title")
    
    if isinstance(card_title, tk.Label):
        card_title.config(text="Add Maintenance Entry")
    
    # Clear the form
    self._clear_maintenance_form()
    
    # Reset the entry ID
    self.data_cache["maintenance_entry_id"] = None

def _edit_maintenance_entry(self, entry_id):
    """
    Edit a maintenance entry.
    
    Args:
        entry_id: ID of the entry to edit
    """
    try:
        # Find the entry in the logs
        logs = self.data_cache.get("maintenance_logs", [])
        log_entry = None
        
        for log in logs:
            if log["id"] == entry_id:
                log_entry = log
                break
        
        if not log_entry:
            messagebox.showerror(
                "Error",
                f"Entry with ID {entry_id} not found."
            )
            return
        
        # Update the form title
        card_title = self.data_cache.get("maintenance_form_title")
        
        if isinstance(card_title, tk.Label):
            card_title.config(text="Edit Maintenance Entry")
        
        # Fill the form with the entry data
        timestamp = datetime.fromisoformat(log_entry["timestamp"])
        date_str = timestamp.strftime("%Y-%m-%d")
        
        self.data_cache["maintenance_date"].set(date_str)
        self.data_cache["maintenance_action"].set(log_entry["action"])
        self.data_cache["maintenance_details"].delete("1.0", "end")
        self.data_cache["maintenance_details"].insert("1.0", log_entry.get("details", ""))
        self.data_cache["maintenance_performed_by"].set(log_entry.get("performed_by", ""))
        
        # Set the entry ID for saving
        self.data_cache["maintenance_entry_id"] = entry_id
    except Exception as e:
        logger.error(f"Error editing maintenance entry: {e}")
        messagebox.showerror(
            "Error",
            f"An error occurred while editing the entry: {str(e)}"
        )

def _delete_maintenance_entry(self, entry_id):
    """
    Delete a maintenance entry.
    
    Args:
        entry_id: ID of the entry to delete
    """
    try:
        # Ask for confirmation
        confirm = messagebox.askyesno(
            "Confirm Delete",
            "Are you sure you want to delete this maintenance entry?"
        )
        
        if not confirm:
            return
        
        # Find and remove the entry from the logs
        logs = self.data_cache.get("maintenance_logs", [])
        new_logs = [log for log in logs if log["id"] != entry_id]
        
        # Update the logs in the data cache
        self.data_cache["maintenance_logs"] = new_logs
        
        # Reload the logs
        self._load_maintenance_logs()
        
        # Show success message
        messagebox.showinfo(
            "Success",
            "Maintenance entry deleted successfully."
        )
    except Exception as e:
        logger.error(f"Error deleting maintenance entry: {e}")
        messagebox.showerror(
            "Error",
            f"An error occurred while deleting the entry: {str(e)}"
        )

def _clear_maintenance_form(self):
    """Clear the maintenance form."""
    # Get current date
    date_var = self.data_cache.get("maintenance_date")
    if date_var:
        date_var.set(datetime.now().strftime("%Y-%m-%d"))
    
    # Clear other fields
    action_var = self.data_cache.get("maintenance_action")
    if action_var:
        action_var.set("")
    
    details_entry = self.data_cache.get("maintenance_details")
    if details_entry:
        details_entry.delete("1.0", "end")
    
    performed_var = self.data_cache.get("maintenance_performed_by")
    if performed_var:
        performed_var.set("")
    
    # Reset the entry ID
    self.data_cache["maintenance_entry_id"] = None

def _save_maintenance_entry(self):
    """Save the maintenance entry."""
    try:
        # Validate form data
        date = self.data_cache.get("maintenance_date").get()
        action = self.data_cache.get("maintenance_action").get()
        details = self.data_cache.get("maintenance_details").get("1.0", "end-1c")
        performed_by = self.data_cache.get("maintenance_performed_by").get()
        
        # Validate date
        if not date:
            messagebox.showerror(
                "Validation Error",
                "Please enter a date."
            )
            return
        
        # Validate action
        if not action:
            messagebox.showerror(
                "Validation Error",
                "Please select an action."
            )
            return
        
        # Convert date to timestamp
        try:
            timestamp = datetime.strptime(date, "%Y-%m-%d").isoformat()
        except ValueError:
            messagebox.showerror(
                "Validation Error",
                "Invalid date format. Please use YYYY-MM-DD."
            )
            return
        
        # Get the entry ID
        entry_id = self.data_cache.get("maintenance_entry_id")
        
        # Get the logs
        logs = self.data_cache.get("maintenance_logs", [])
        
        if entry_id:
            # Update existing entry
            for log in logs:
                if log["id"] == entry_id:
                    log["timestamp"] = timestamp
                    log["action"] = action
                    log["details"] = details
                    log["performed_by"] = performed_by
                    break
            
            # Show success message
            messagebox.showinfo(
                "Success",
                "Maintenance entry updated successfully."
            )
        else:
            # Create new entry
            new_id = str(len(logs) + 1)
            logs.append({
                "id": new_id,
                "timestamp": timestamp,
                "action": action,
                "details": details,
                "performed_by": performed_by
            })
            
            # Show success message
            messagebox.showinfo(
                "Success",
                "Maintenance entry added successfully."
            )
        
        # Update the logs in the data cache
        self.data_cache["maintenance_logs"] = logs
        
        # Reload the logs
        self._load_maintenance_logs()
        
        # Clear the form
        self._clear_maintenance_form()
    except Exception as e:
        logger.error(f"Error saving maintenance entry: {e}")
        messagebox.showerror(
            "Error",
            f"An error occurred while saving the entry: {str(e)}"
        )

def show_settings(self):
    """Show settings interface."""
    # Clear the content frame
    self._clear_content_frame()
    
    # Set the active tab
    self._set_active_tab("settings")
    
    # Create the main frame
    settings_frame = tk.Frame(self.content_frame, bg=self.COLORS["background"])
    settings_frame.pack(fill="both", expand=True, padx=20, pady=20)
    
    # Add title and description
    self._add_page_title(
        settings_frame,
        "Settings",
        "Configure application settings and preferences"
    )
    
    # Create settings notebook
    self._create_settings_notebook(settings_frame)
    
    # Create button frame
    button_frame = tk.Frame(settings_frame, bg=self.COLORS["background"])
    button_frame.pack(fill="x", pady=10)
    
    save_button = ttk.Button(
        button_frame,
        text="Save All Settings",
        command=self._save_all_settings
    )
    save_button.pack(side="right", padx=10)

def _create_settings_notebook(self, parent):
    """
    Create settings notebook with tabs for different settings categories.
    
    Args:
        parent: Parent widget
    """
    # Create notebook
    notebook = ttk.Notebook(parent)
    notebook.pack(fill="both", expand=True, pady=10)
    
    # Create tabs
    general_tab = ttk.Frame(notebook)
    notebook.add(general_tab, text="General")
    
    pool_tab = ttk.Frame(notebook)
    notebook.add(pool_tab, text="Pool")
    
    weather_tab = ttk.Frame(notebook)
    notebook.add(weather_tab, text="Weather")
    
    display_tab = ttk.Frame(notebook)
    notebook.add(display_tab, text="Display")
    
    # Create settings frames
    self._create_general_settings(general_tab)
    self._create_pool_settings(pool_tab)
    self._create_weather_settings(weather_tab)
    self._create_display_settings(display_tab)

def _create_general_settings(self, parent):
    """
    Create general settings frame.
    
    Args:
        parent: Parent widget
    """
    # Create settings frame
    settings_frame = tk.Frame(parent, bg=self.COLORS["background"])
    settings_frame.pack(fill="both", expand=True, padx=20, pady=20)
    
    # User name field
    user_name_frame = ttk.LabelFrame(settings_frame, text="User Information", padding=10)
    user_name_frame.pack(fill="x", pady=10)
    
    user_name_label = ttk.Label(user_name_label, text="Your Name:")
    user_name_label.pack(side="left", padx=5)
    
    user_name_var = tk.StringVar(value=self.config.get("general", {}).get("user_name", ""))
    user_name_entry = ttk.Entry(user_name_frame, textvariable=user_name_var, width=30)
    user_name_entry.pack(side="left", padx=5)
    
    # Store in data cache
    self.data_cache["settings_user_name"] = user_name_var
    
    # Data directory field
    data_dir_frame = ttk.LabelFrame(settings_frame, text="Data Storage", padding=10)
    data_dir_frame.pack(fill="x", pady=10)
    
    data_dir_label = ttk.Label(data_dir_frame, text="Data Directory:")
    data_dir_label.pack(side="left", padx=5)
    
    data_dir_var = tk.StringVar(value=self.config.get("general", {}).get("data_directory", "data"))
    data_dir_entry = ttk.Entry(data_dir_frame, textvariable=data_dir_var, width=30)
    data_dir_entry.pack(side="left", padx=5)
    
    browse_button = ttk.Button(
        data_dir_frame,
        text="Browse...",
        command=self._browse_data_directory
    )
    browse_button.pack(side="left", padx=5)
    
    # Store in data cache
    self.data_cache["settings_data_directory"] = data_dir_var
    
    # Auto backup field
    backup_frame = tk.Frame(settings_frame, bg=self.COLORS["background"])
    backup_frame.pack(fill="x", pady=10)
    
    backup_label = tk.Label(
        backup_frame,
        text="Automatic Backup:",
        font=(self.FONT_FAMILY, self.FONT_SIZE_NORMAL),
        bg=self.COLORS["background"],
        fg=self.COLORS["text"]
    )
    backup_label.pack(side="left", padx=5)
    
    backup_var = tk.BooleanVar(value=self.config.get("general", {}).get("auto_backup", False))
    
    backup_check = ttk.Checkbutton(
        backup_frame,
        text="Enable automatic backup of data",
        variable=backup_var
    )
    backup_check.pack(side="left", padx=5)
    
    # Store in data cache
    self.data_cache["settings_auto_backup"] = backup_var

def _create_pool_settings(self, parent):
    """
    Create pool settings frame.
    
    Args:
        parent: Parent widget
    """
    # Create settings frame
    settings_frame = tk.Frame(parent, bg=self.COLORS["background"])
    settings_frame.pack(fill="both", expand=True, padx=20, pady=20)
    
    # Pool size field
    size_frame = ttk.LabelFrame(settings_frame, text="Pool Information", padding=10)
    size_frame.pack(fill="x", pady=10)
    
    size_label = ttk.Label(size_frame, text="Pool Size (gallons):")
    size_label.pack(side="left", padx=5)
    
    size_var = tk.StringVar(value=self.config.get("pool", {}).get("size", "10000"))
    size_entry = ttk.Entry(size_frame, textvariable=size_var, width=10)
    size_entry.pack(side="left", padx=5)
    
    # Store in data cache
    self.data_cache["settings_pool_size"] = size_var
    
    # Pool type field
    type_frame = tk.Frame(settings_frame, bg=self.COLORS["background"])
    type_frame.pack(fill="x", pady=10)
    
    type_label = tk.Label(
        type_frame,
        text="Pool Type:",
        font=(self.FONT_FAMILY, self.FONT_SIZE_NORMAL),
        bg=self.COLORS["background"],
        fg=self.COLORS["text"]
    )
    type_label.pack(side="left", padx=5)
    
    type_var = tk.StringVar(value=self.config.get("pool", {}).get("type", "chlorine"))
    
    # Pool types
    pool_types = ["chlorine", "saltwater", "bromine"]
    
    type_combo = ttk.Combobox(
        type_frame,
        textvariable=type_var,
        values=pool_types,
        width=15
    )
    type_combo.pack(side="left", padx=5)
    
    # Store in data cache
    self.data_cache["settings_pool_type"] = type_var
    
    # Test strip brand field
    brand_frame = tk.Frame(settings_frame, bg=self.COLORS["background"])
    brand_frame.pack(fill="x", pady=10)
    
    brand_label = tk.Label(
        brand_frame,
        text="Test Strip Brand:",
        font=(self.FONT_FAMILY, self.FONT_SIZE_NORMAL),
        bg=self.COLORS["background"],
        fg=self.COLORS["text"]
    )
    brand_label.pack(side="left", padx=5)
    
    brand_var = tk.StringVar(value=self.config.get("pool", {}).get("test_strip_brand", "default"))
    
    # Test strip brands
    brands = ["default", "aquacheck", "clorox", "taylor", "hach"]
    
    brand_combo = ttk.Combobox(
        brand_frame,
        textvariable=brand_var,
        values=brands,
        width=15
    )
    brand_combo.pack(side="left", padx=5)
    
    # Store in data cache
    self.data_cache["settings_test_strip_brand"] = brand_var

def _create_weather_settings(self, parent):
    """
    Create weather settings frame.
    
    Args:
        parent: Parent widget
    """
    # Create settings frame
    settings_frame = tk.Frame(parent, bg=self.COLORS["background"])
    settings_frame.pack(fill="both", expand=True, padx=20, pady=20)
    
    # Weather location field
    location_frame = ttk.LabelFrame(settings_frame, text="Weather Location", padding=10)
    location_frame.pack(fill="x", pady=10)
    
    zip_label = ttk.Label(location_frame, text="ZIP Code:")
    zip_label.pack(side="left", padx=5)
    
    zip_var = tk.StringVar(value=self.config.get("weather", {}).get("zip_code", "33101"))
    zip_entry = ttk.Entry(location_frame, textvariable=zip_var, width=10)
    zip_entry.pack(side="left", padx=5)
    
    # Store in data cache
    self.data_cache["settings_zip_code"] = zip_var
    
    # Update interval field
    interval_frame = ttk.LabelFrame(settings_frame, text="Update Settings", padding=10)
    interval_frame.pack(fill="x", pady=10)
    
    interval_label = ttk.Label(interval_frame, text="Update Interval (seconds):")
    interval_label.pack(side="left", padx=5)
    
    interval_var = tk.StringVar(value=str(self.config.get("weather", {}).get("update_interval", 3600)))
    interval_entry = ttk.Entry(interval_frame, textvariable=interval_var, width=10)
    interval_entry.pack(side="left", padx=5)
    
    # Store in data cache
    self.data_cache["settings_update_interval"] = interval_var
    
    # API key field
    api_frame = ttk.LabelFrame(settings_frame, text="API Settings", padding=10)
    api_frame.pack(fill="x", pady=10)
    
    api_label = ttk.Label(api_frame, text="Weather API Key:")
    api_label.pack(side="left", padx=5)
    
    api_var = tk.StringVar(value=self.config.get("weather", {}).get("api_key", ""))
    api_entry = ttk.Entry(api_frame, textvariable=api_var, width=30, show="*")
    api_entry.pack(side="left", padx=5)
    
    # Store in data cache
    self.data_cache["settings_api_key"] = api_var

def _create_display_settings(self, parent):
    """
    Create display settings frame.
    
    Args:
        parent: Parent widget
    """
    # Create settings frame
    settings_frame = tk.Frame(parent, bg=self.COLORS["background"])
    settings_frame.pack(fill="both", expand=True, padx=20, pady=20)
    
    # Theme field
    theme_frame = tk.Frame(settings_frame, bg=self.COLORS["background"])
    theme_frame.pack(fill="x", pady=10)
    
    theme_label = tk.Label(
        theme_frame,
        text="Theme:",
        font=(self.FONT_FAMILY, self.FONT_SIZE_NORMAL),
        bg=self.COLORS["background"],
        fg=self.COLORS["text"]
    )
    theme_label.pack(side="left", padx=5)
    
    theme_var = tk.StringVar(value=self.config.get("display", {}).get("theme", "light"))
    
    # Themes
    themes = ["light", "dark", "blue", "green"]
    
    theme_combo = ttk.Combobox(
        theme_frame,
        textvariable=theme_var,
        values=themes,
        width=15
    )
    theme_combo.pack(side="left", padx=5)
    
    # Preview button
    preview_button = ttk.Button(
        theme_frame,
        text="Preview Theme",
        command=self._preview_theme
    )
    preview_button.pack(side="left", padx=10)
    
    # Font size field
    font_frame = tk.Frame(settings_frame, bg=self.COLORS["background"])
    font_frame.pack(fill="x", pady=10)
    
    font_label = tk.Label(
        font_frame,
        text="Font Size:",
        font=(self.FONT_FAMILY, self.FONT_SIZE_NORMAL),
        bg=self.COLORS["background"],
        fg=self.COLORS["text"]
    )
    font_label.pack(side="left", padx=5)
    
    font_var = tk.StringVar(value=self.config.get("display", {}).get("font_size", "normal"))
    
    # Font sizes
    font_sizes = ["small", "normal", "large", "extra-large"]
    
    font_combo = ttk.Combobox(
        font_frame,
        textvariable=font_var,
        values=font_sizes,
        width=15
    )
    font_combo.pack(side="left", padx=5)
    
    # Store in data cache
    self.data_cache["settings_theme"] = theme_var
    self.data_cache["settings_font_size"] = font_var
    
    # Chart DPI field
    dpi_frame = ttk.LabelFrame(settings_frame, text="Chart Settings", padding=10)
    dpi_frame.pack(fill="x", pady=10)
    
    dpi_label = ttk.Label(dpi_frame, text="Chart DPI:")
    dpi_label.pack(side="left", padx=5)
    
    dpi_var = tk.StringVar(value=self.config.get("display", {}).get("chart_dpi", "100"))
    dpi_entry = ttk.Entry(dpi_frame, textvariable=dpi_var, width=10)
    dpi_entry.pack(side="left", padx=5)
    
    # Store in data cache
    self.data_cache["settings_chart_dpi"] = dpi_var

def _browse_data_directory(self):
    """Browse for data directory."""
    try:
        directory = filedialog.askdirectory(
            title="Select Data Directory",
            initialdir=self.data_cache.get("settings_data_directory", tk.StringVar()).get()
        )
        
        if directory:
            self.data_cache.get("settings_data_directory", tk.StringVar()).set(directory)
    except Exception as e:
        # Handle error
        pass

def _preview_theme(self):
    """Preview the selected theme."""
    try:
        # Show a message box with the theme preview
        messagebox.showinfo(
            "Theme Preview",
            f"This is a preview of the {self.data_cache.get('settings_theme', tk.StringVar()).get()} theme."
        )
    except Exception as e:
        logger.error(f"Error previewing theme: {e}")
        messagebox.showerror(
            "Error",
            f"An error occurred while previewing the theme: {str(e)}"
        )

def _save_all_settings(self):
    """Save all settings."""
    try:
        # Update general settings
        if "general" not in self.config:
            self.config["general"] = {}
        
        self.config["general"].update({
            "user_name": self.data_cache.get("settings_user_name", tk.StringVar()).get(),
            "data_directory": self.data_cache.get("settings_data_directory", tk.StringVar()).get(),
            "auto_backup": self.data_cache.get("settings_auto_backup", tk.BooleanVar()).get()
        })
        
        # Update pool settings
        if "pool" not in self.config:
            self.config["pool"] = {}
        
        self.config["pool"].update({
            "size": self.data_cache.get("settings_pool_size", tk.StringVar()).get(),
            "type": self.data_cache.get("settings_pool_type", tk.StringVar()).get(),
            "test_strip_brand": self.data_cache.get("settings_test_strip_brand", tk.StringVar()).get()
        })
        
        # Update weather settings
        if "weather" not in self.config:
            self.config["weather"] = {}
        
        self.config["weather"].update({
            "zip_code": self.data_cache.get("settings_zip_code", tk.StringVar()).get(),
            "update_interval": self.data_cache.get("settings_update_interval", tk.StringVar()).get(),
            "api_key": self.data_cache.get("settings_api_key", tk.StringVar()).get()
        })
        
        # Update display settings
        if "display" not in self.config:
            self.config["display"] = {}
        
        self.config["display"].update({
            "theme": self.data_cache.get("settings_theme", tk.StringVar()).get(),
            "font_size": self.data_cache.get("settings_font_size", tk.StringVar()).get(),
            "chart_dpi": self.data_cache.get("settings_chart_dpi", tk.StringVar()).get()
        })
        
        # Save the config
        self._save_config()
        
        # Show success message
        messagebox.showinfo(
            "Settings Saved",
            "All settings have been saved successfully. Some changes may require restarting the application."
        )
        
        # In a real implementation, you would apply the settings immediately where possible
        # For example, updating the theme or font size
    except Exception as e:
        logger.error(f"Error saving settings: {e}")
        messagebox.showerror(
            "Error",
            f"An error occurred while saving settings: {str(e)}"
        )