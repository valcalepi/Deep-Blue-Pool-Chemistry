
#!/usr/bin/env python3
"""
Data Visualization Module for Deep Blue Pool Chemistry.

This module provides tools for visualizing pool chemistry data over time,
including time-series graphs, trend analysis, and statistical summaries.
It supports exporting data to various formats and generating reports.

Features:
- Time-series graphs for all chemical parameters
- Date range selection and filtering
- Trend analysis and statistics
- Data export to CSV and PDF
- Interactive visualization options
"""

import os
import csv
import json
import logging
import tempfile
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Union, Callable

import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.ticker import MaxNLocator

# Configure logging
logger = logging.getLogger(__name__)

class DataVisualization:
    """
    Data visualization for pool chemistry data.
    
    This class provides methods for creating visualizations of pool chemistry
    data, including time-series graphs, trend analysis, and statistical summaries.
    
    Attributes:
        db_service: Database service for retrieving data
        output_dir: Directory for saving output files
        default_dpi: Default DPI for saved images
        theme: Visual theme for plots ('light', 'dark', or 'blue')
    """
    
    # Parameter display names and units
    PARAMETER_INFO = {
        "ph": {"name": "pH", "unit": "", "color": "#FF5733"},
        "free_chlorine": {"name": "Free Chlorine", "unit": "ppm", "color": "#33FF57"},
        "total_chlorine": {"name": "Total Chlorine", "unit": "ppm", "color": "#5733FF"},
        "total_alkalinity": {"name": "Total Alkalinity", "unit": "ppm", "color": "#33FFFF"},
        "calcium_hardness": {"name": "Calcium Hardness", "unit": "ppm", "color": "#FF33FF"},
        "cyanuric_acid": {"name": "Cyanuric Acid", "unit": "ppm", "color": "#FFFF33"},
        "total_bromine": {"name": "Total Bromine", "unit": "ppm", "color": "#FF9933"},
        "salt": {"name": "Salt", "unit": "ppm", "color": "#9933FF"},
        "temperature": {"name": "Temperature", "unit": "\u00b0F", "color": "#33FFFF"}
    }
    
    # Theme definitions
    THEMES = {
        "light": {
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "axes.edgecolor": "black",
            "axes.labelcolor": "black",
            "axes.grid": True,
            "grid.color": "#CCCCCC",
            "text.color": "black",
            "xtick.color": "black",
            "ytick.color": "black",
            "figure.titleweight": "bold",
            "figure.titlesize": 16,
            "axes.titleweight": "bold",
            "axes.titlesize": 14,
            "axes.labelweight": "bold",
            "axes.labelsize": 12
        },
        "dark": {
            "figure.facecolor": "#222222",
            "axes.facecolor": "#222222",
            "axes.edgecolor": "white",
            "axes.labelcolor": "white",
            "axes.grid": True,
            "grid.color": "#444444",
            "text.color": "white",
            "xtick.color": "white",
            "ytick.color": "white",
            "figure.titleweight": "bold",
            "figure.titlesize": 16,
            "axes.titleweight": "bold",
            "axes.titlesize": 14,
            "axes.labelweight": "bold",
            "axes.labelsize": 12
        },
        "blue": {
            "figure.facecolor": "#1A2B3C",
            "axes.facecolor": "#1A2B3C",
            "axes.edgecolor": "#AABBCC",
            "axes.labelcolor": "#FFFFFF",
            "axes.grid": True,
            "grid.color": "#2A3B4C",
            "text.color": "#FFFFFF",
            "xtick.color": "#AABBCC",
            "ytick.color": "#AABBCC",
            "figure.titleweight": "bold",
            "figure.titlesize": 16,
            "axes.titleweight": "bold",
            "axes.titlesize": 14,
            "axes.labelweight": "bold",
            "axes.labelsize": 12
        }
    }
    
    def __init__(
        self,
        db_service: Any,
        output_dir: str = "data/visualizations",
        default_dpi: int = 100,
        theme: str = "light"
    ):
        """
        Initialize the DataVisualization.
        
        Args:
            db_service: Database service for retrieving data.
            output_dir: Directory for saving output files.
            default_dpi: Default DPI for saved images.
            theme: Visual theme for plots ('light', 'dark', or 'blue').
        """
        self.db_service = db_service
        self.output_dir = output_dir
        self.default_dpi = default_dpi
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Set the theme
        self.set_theme(theme)
    
    def set_theme(self, theme: str) -> None:
        """
        Set the visual theme for plots.
        
        Args:
            theme: Theme name ('light', 'dark', or 'blue').
        """
        if theme not in self.THEMES:
            logger.warning(f"Unknown theme: {theme}. Using 'light' theme.")
            theme = "light"
        
        self.theme = theme
        
        # Apply theme settings to matplotlib
        for key, value in self.THEMES[theme].items():
            plt.rcParams[key] = value
    
    def create_time_series_graph(
        self,
        parameters: List[str],
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        title: Optional[str] = None,
        figsize: Tuple[int, int] = (10, 6),
        dpi: Optional[int] = None,
        show_ideal_ranges: bool = True,
        show_trend_line: bool = True,
        output_file: Optional[str] = None
    ) -> str:
        """
        Create a time series graph for one or more parameters.
        
        Args:
            parameters: List of parameter names to include in the graph.
            start_date: Start date for the graph (ISO format).
            end_date: End date for the graph (ISO format).
            title: Title for the graph.
            figsize: Figure size (width, height) in inches.
            dpi: DPI for the output image.
            show_ideal_ranges: Whether to show ideal ranges on the graph.
            show_trend_line: Whether to show trend lines.
            output_file: Path to save the graph image.
            
        Returns:
            Path to the saved graph image.
        """
        # Validate parameters
        valid_parameters = [p for p in parameters if p in self.PARAMETER_INFO]
        if not valid_parameters:
            logger.error(f"No valid parameters provided: {parameters}")
            raise ValueError(f"No valid parameters provided: {parameters}")
        
        # Get data from database
        data = self._get_sensor_data(start_date, end_date)
        if not data:
            logger.error("No data available for the specified date range")
            raise ValueError("No data available for the specified date range")
        
        # Create figure and axes
        fig, ax = plt.subplots(figsize=figsize, dpi=dpi or self.default_dpi)
        
        # Parse timestamps and sort data by date
        for item in data:
            item['datetime'] = datetime.fromisoformat(item['timestamp'])
        
        data.sort(key=lambda x: x['datetime'])
        
        # Plot each parameter
        for param in valid_parameters:
            param_info = self.PARAMETER_INFO[param]
            param_name = param_info["name"]
            param_unit = param_info["unit"]
            param_color = param_info["color"]
            
            # Extract data for this parameter
            x_data = [item['datetime'] for item in data if param in item and item[param] is not None]
            y_data = [item[param] for item in data if param in item and item[param] is not None]
            
            if not x_data or not y_data:
                logger.warning(f"No data available for parameter: {param}")
                continue
            
            # Plot the parameter
            ax.plot(x_data, y_data, 'o-', label=f"{param_name}", color=param_color, linewidth=2, markersize=5)
            
            # Add trend line if requested
            if show_trend_line and len(x_data) > 1:
                # Convert dates to numbers for linear regression
                x_num = mdates.date2num(x_data)
                z = np.polyfit(x_num, y_data, 1)
                p = np.poly1d(z)
                
                # Plot trend line
                ax.plot(x_data, p(x_num), '--', color=param_color, alpha=0.7, linewidth=1.5)
        
        # Configure axes
        ax.set_xlabel('Date')
        
        # Set y-axis label based on parameters
        if len(valid_parameters) == 1:
            param = valid_parameters[0]
            param_info = self.PARAMETER_INFO[param]
            y_label = f"{param_info['name']}"
            if param_info['unit']:
                y_label += f" ({param_info['unit']})"
            ax.set_ylabel(y_label)
        else:
            ax.set_ylabel('Value')
        
        # Format x-axis dates
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        fig.autofmt_xdate()
        
        # Add grid
        ax.grid(True, linestyle='--', alpha=0.7)
        
        # Add legend
        ax.legend(loc='best')
        
        # Set title
        if title:
            ax.set_title(title)
        else:
            if len(valid_parameters) == 1:
                param = valid_parameters[0]
                param_info = self.PARAMETER_INFO[param]
                ax.set_title(f"{param_info['name']} Over Time")
            else:
                ax.set_title("Pool Chemistry Over Time")
        
        # Adjust layout
        fig.tight_layout()
        
        # Save the figure
        if output_file:
            save_path = output_file
        else:
            # Generate a filename based on parameters and date
            param_str = "_".join(valid_parameters)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            save_path = os.path.join(self.output_dir, f"time_series_{param_str}_{timestamp}.png")
        
        fig.savefig(save_path, dpi=dpi or self.default_dpi)
        plt.close(fig)
        
        return save_path
    
    def create_multi_parameter_dashboard(
        self,
        parameters: List[str],
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        figsize: Tuple[int, int] = (12, 10),
        dpi: Optional[int] = None,
        output_file: Optional[str] = None
    ) -> str:
        """
        Create a dashboard with multiple parameters in separate subplots.
        
        Args:
            parameters: List of parameter names to include in the dashboard.
            start_date: Start date for the graphs (ISO format).
            end_date: End date for the graphs (ISO format).
            figsize: Figure size (width, height) in inches.
            dpi: DPI for the output image.
            output_file: Path to save the dashboard image.
            
        Returns:
            Path to the saved dashboard image.
        """
        # Validate parameters
        valid_parameters = [p for p in parameters if p in self.PARAMETER_INFO]
        if not valid_parameters:
            logger.error(f"No valid parameters provided: {parameters}")
            raise ValueError(f"No valid parameters provided: {parameters}")
        
        # Get data from database
        data = self._get_sensor_data(start_date, end_date)
        if not data:
            logger.error("No data available for the specified date range")
            raise ValueError("No data available for the specified date range")
        
        # Parse timestamps and sort data by date
        for item in data:
            item['datetime'] = datetime.fromisoformat(item['timestamp'])
        
        data.sort(key=lambda x: x['datetime'])
        
        # Create figure with subplots
        n_params = len(valid_parameters)
        fig, axes = plt.subplots(n_params, 1, figsize=figsize, dpi=dpi or self.default_dpi, sharex=True)
        
        # Handle case with only one parameter
        if n_params == 1:
            axes = [axes]
        
        # Plot each parameter in its own subplot
        for i, param in enumerate(valid_parameters):
            param_info = self.PARAMETER_INFO[param]
            param_name = param_info["name"]
            param_unit = param_info["unit"]
            param_color = param_info["color"]
            
            ax = axes[i]
            
            # Extract data for this parameter
            x_data = [item['datetime'] for item in data if param in item and item[param] is not None]
            y_data = [item[param] for item in data if param in item and item[param] is not None]
            
            if not x_data or not y_data:
                logger.warning(f"No data available for parameter: {param}")
                ax.text(0.5, 0.5, f"No data available for {param_name}", 
                        horizontalalignment='center', verticalalignment='center',
                        transform=ax.transAxes)
                continue
            
            # Plot the parameter
            ax.plot(x_data, y_data, 'o-', color=param_color, linewidth=2, markersize=5)
            
            # Add trend line
            if len(x_data) > 1:
                # Convert dates to numbers for linear regression
                x_num = mdates.date2num(x_data)
                z = np.polyfit(x_num, y_data, 1)
                p = np.poly1d(z)
                
                # Plot trend line
                ax.plot(x_data, p(x_num), '--', color=param_color, alpha=0.7, linewidth=1.5)
            
            # Set y-axis label
            y_label = param_name
            if param_unit:
                y_label += f" ({param_unit})"
            ax.set_ylabel(y_label)
            
            # Add grid
            ax.grid(True, linestyle='--', alpha=0.7)
            
            # Format y-axis to avoid too many decimal places
            ax.yaxis.set_major_locator(MaxNLocator(nbins=5, integer=False))
            
            # Add horizontal lines for ideal ranges if applicable
            # This would require knowledge of ideal ranges for each parameter
        
        # Format x-axis dates on the bottom subplot
        axes[-1].set_xlabel('Date')
        axes[-1].xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        fig.autofmt_xdate()
        
        # Set title for the entire figure
        date_range_str = ""
        if start_date and end_date:
            date_range_str = f" ({start_date} to {end_date})"
        elif start_date:
            date_range_str = f" (from {start_date})"
        elif end_date:
            date_range_str = f" (until {end_date})"
        
        fig.suptitle(f"Pool Chemistry Dashboard{date_range_str}", fontsize=16)
        
        # Adjust layout
        fig.tight_layout()
        fig.subplots_adjust(top=0.95)  # Make room for the title
        
        # Save the figure
        if output_file:
            save_path = output_file
        else:
            # Generate a filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            save_path = os.path.join(self.output_dir, f"dashboard_{timestamp}.png")
        
        fig.savefig(save_path, dpi=dpi or self.default_dpi)
        plt.close(fig)
        
        return save_path
    
    def create_statistical_summary(
        self,
        parameters: List[str],
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        figsize: Tuple[int, int] = (12, 8),
        dpi: Optional[int] = None,
        output_file: Optional[str] = None
    ) -> str:
        """
        Create a statistical summary visualization for parameters.
        
        Args:
            parameters: List of parameter names to include.
            start_date: Start date for the data (ISO format).
            end_date: End date for the data (ISO format).
            figsize: Figure size (width, height) in inches.
            dpi: DPI for the output image.
            output_file: Path to save the summary image.
            
        Returns:
            Path to the saved summary image.
        """
        # Validate parameters
        valid_parameters = [p for p in parameters if p in self.PARAMETER_INFO]
        if not valid_parameters:
            logger.error(f"No valid parameters provided: {parameters}")
            raise ValueError(f"No valid parameters provided: {parameters}")
        
        # Get data from database
        data = self._get_sensor_data(start_date, end_date)
        if not data:
            logger.error("No data available for the specified date range")
            raise ValueError("No data available for the specified date range")
        
        # Create figure with subplots - one row for each parameter
        n_params = len(valid_parameters)
        fig, axes = plt.subplots(n_params, 2, figsize=figsize, dpi=dpi or self.default_dpi, 
                                gridspec_kw={'width_ratios': [2, 1]})
        
        # Handle case with only one parameter
        if n_params == 1:
            axes = [axes]
        
        # For each parameter, create a time series and a box plot
        for i, param in enumerate(valid_parameters):
            param_info = self.PARAMETER_INFO[param]
            param_name = param_info["name"]
            param_unit = param_info["unit"]
            param_color = param_info["color"]
            
            # Extract data for this parameter
            param_data = [item[param] for item in data if param in item and item[param] is not None]
            timestamps = [datetime.fromisoformat(item['timestamp']) for item in data 
                         if param in item and item[param] is not None]
            
            if not param_data or not timestamps:
                logger.warning(f"No data available for parameter: {param}")
                axes[i][0].text(0.5, 0.5, f"No data available for {param_name}", 
                               horizontalalignment='center', verticalalignment='center',
                               transform=axes[i][0].transAxes)
                axes[i][1].text(0.5, 0.5, f"No data available for {param_name}", 
                               horizontalalignment='center', verticalalignment='center',
                               transform=axes[i][1].transAxes)
                continue
            
            # Time series plot
            axes[i][0].plot(timestamps, param_data, 'o-', color=param_color, linewidth=2, markersize=5)
            axes[i][0].set_title(f"{param_name} Time Series")
            axes[i][0].set_ylabel(f"{param_name}" + (f" ({param_unit})" if param_unit else ""))
            axes[i][0].grid(True, linestyle='--', alpha=0.7)
            
            # Format x-axis dates
            axes[i][0].xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
            
            # Box plot
            axes[i][1].boxplot(param_data, patch_artist=True, 
                              boxprops=dict(facecolor=param_color, color='black'),
                              whiskerprops=dict(color='black'),
                              capprops=dict(color='black'),
                              medianprops=dict(color='black'))
            
            axes[i][1].set_title(f"{param_name} Distribution")
            axes[i][1].set_ylabel(f"{param_name}" + (f" ({param_unit})" if param_unit else ""))
            axes[i][1].grid(True, linestyle='--', alpha=0.7)
            
            # Remove x-tick labels from box plot
            axes[i][1].set_xticks([])
            
            # Add statistics as text
            stats_text = (
                f"Min: {min(param_data):.2f}\
"
                f"Max: {max(param_data):.2f}\
"
                f"Avg: {sum(param_data)/len(param_data):.2f}\
"
                f"Median: {sorted(param_data)[len(param_data)//2]:.2f}\
"
                f"Count: {len(param_data)}"
            )
            
            axes[i][1].text(1.45, 0.5, stats_text, 
                           transform=axes[i][1].transAxes,
                           bbox=dict(facecolor='white', alpha=0.8, boxstyle='round,pad=0.5'))
        
        # Set title for the entire figure
        date_range_str = ""
        if start_date and end_date:
            date_range_str = f" ({start_date} to {end_date})"
        elif start_date:
            date_range_str = f" (from {start_date})"
        elif end_date:
            date_range_str = f" (until {end_date})"
        
        fig.suptitle(f"Pool Chemistry Statistical Summary{date_range_str}", fontsize=16)
        
        # Adjust layout
        fig.tight_layout()
        fig.subplots_adjust(top=0.95)  # Make room for the title
        
        # Save the figure
        if output_file:
            save_path = output_file
        else:
            # Generate a filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            save_path = os.path.join(self.output_dir, f"stats_summary_{timestamp}.png")
        
        fig.savefig(save_path, dpi=dpi or self.default_dpi)
        plt.close(fig)
        
        return save_path
    
    def create_correlation_matrix(
        self,
        parameters: List[str],
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        figsize: Tuple[int, int] = (10, 8),
        dpi: Optional[int] = None,
        output_file: Optional[str] = None
    ) -> str:
        """
        Create a correlation matrix visualization for parameters.
        
        Args:
            parameters: List of parameter names to include.
            start_date: Start date for the data (ISO format).
            end_date: End date for the data (ISO format).
            figsize: Figure size (width, height) in inches.
            dpi: DPI for the output image.
            output_file: Path to save the matrix image.
            
        Returns:
            Path to the saved matrix image.
        """
        # Validate parameters
        valid_parameters = [p for p in parameters if p in self.PARAMETER_INFO]
        if len(valid_parameters) < 2:
            logger.error(f"At least 2 valid parameters are required for correlation matrix")
            raise ValueError(f"At least 2 valid parameters are required for correlation matrix")
        
        # Get data from database
        data = self._get_sensor_data(start_date, end_date)
        if not data:
            logger.error("No data available for the specified date range")
            raise ValueError("No data available for the specified date range")
        
        # Extract data for each parameter
        param_data = {}
        for param in valid_parameters:
            param_data[param] = [item[param] for item in data if param in item and item[param] is not None]
        
        # Check if we have data for all parameters
        for param, values in param_data.items():
            if not values:
                logger.error(f"No data available for parameter: {param}")
                raise ValueError(f"No data available for parameter: {param}")
        
        # Find the minimum length across all parameters
        min_length = min(len(values) for values in param_data.values())
        
        # Truncate all arrays to the same length
        for param in param_data:
            param_data[param] = param_data[param][:min_length]
        
        # Create correlation matrix
        corr_matrix = np.zeros((len(valid_parameters), len(valid_parameters)))
        for i, param1 in enumerate(valid_parameters):
            for j, param2 in enumerate(valid_parameters):
                if i == j:
                    corr_matrix[i, j] = 1.0
                else:
                    corr = np.corrcoef(param_data[param1], param_data[param2])[0, 1]
                    corr_matrix[i, j] = corr
        
        # Create figure
        fig, ax = plt.subplots(figsize=figsize, dpi=dpi or self.default_dpi)
        
        # Create heatmap
        cmap = plt.cm.RdBu_r
        im = ax.imshow(corr_matrix, cmap=cmap, vmin=-1, vmax=1)
        
        # Add colorbar
        cbar = fig.colorbar(im, ax=ax)
        cbar.set_label('Correlation Coefficient')
        
        # Set ticks and labels
        param_names = [self.PARAMETER_INFO[p]["name"] for p in valid_parameters]
        ax.set_xticks(np.arange(len(param_names)))
        ax.set_yticks(np.arange(len(param_names)))
        ax.set_xticklabels(param_names)
        ax.set_yticklabels(param_names)
        
        # Rotate x-axis labels
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
        
        # Add correlation values in each cell
        for i in range(len(valid_parameters)):
            for j in range(len(valid_parameters)):
                text_color = "black" if abs(corr_matrix[i, j]) < 0.7 else "white"
                ax.text(j, i, f"{corr_matrix[i, j]:.2f}", 
                       ha="center", va="center", color=text_color)
        
        # Set title
        date_range_str = ""
        if start_date and end_date:
            date_range_str = f" ({start_date} to {end_date})"
        elif start_date:
            date_range_str = f" (from {start_date})"
        elif end_date:
            date_range_str = f" (until {end_date})"
        
        ax.set_title(f"Parameter Correlation Matrix{date_range_str}")
        
        # Adjust layout
        fig.tight_layout()
        
        # Save the figure
        if output_file:
            save_path = output_file
        else:
            # Generate a filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            save_path = os.path.join(self.output_dir, f"correlation_matrix_{timestamp}.png")
        
        fig.savefig(save_path, dpi=dpi or self.default_dpi)
        plt.close(fig)
        
        return save_path
    
    def export_data_to_csv(
        self,
        parameters: List[str],
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        output_file: Optional[str] = None
    ) -> str:
        """
        Export data to a CSV file.
        
        Args:
            parameters: List of parameter names to include.
            start_date: Start date for the data (ISO format).
            end_date: End date for the data (ISO format).
            output_file: Path to save the CSV file.
            
        Returns:
            Path to the saved CSV file.
        """
        # Validate parameters
        valid_parameters = [p for p in parameters if p in self.PARAMETER_INFO]
        if not valid_parameters:
            logger.error(f"No valid parameters provided: {parameters}")
            raise ValueError(f"No valid parameters provided: {parameters}")
        
        # Get data from database
        data = self._get_sensor_data(start_date, end_date)
        if not data:
            logger.error("No data available for the specified date range")
            raise ValueError("No data available for the specified date range")
        
        # Sort data by timestamp
        data.sort(key=lambda x: x['timestamp'])
        
        # Determine the output file path
        if output_file:
            save_path = output_file
        else:
            # Generate a filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            save_path = os.path.join(self.output_dir, f"pool_data_{timestamp}.csv")
        
        # Write data to CSV
        with open(save_path, 'w', newline='') as csvfile:
            # Determine the fieldnames (columns)
            fieldnames = ['timestamp']
            for param in valid_parameters:
                fieldnames.append(param)
            
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for item in data:
                row = {'timestamp': item['timestamp']}
                for param in valid_parameters:
                    if param in item:
                        row[param] = item[param]
                    else:
                        row[param] = None
                writer.writerow(row)
        
        return save_path
    
    def generate_pdf_report(
        self,
        parameters: List[str],
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        output_file: Optional[str] = None
    ) -> str:
        """
        Generate a comprehensive PDF report with visualizations and statistics.
        
        Args:
            parameters: List of parameter names to include.
            start_date: Start date for the data (ISO format).
            end_date: End date for the data (ISO format).
            output_file: Path to save the PDF report.
            
        Returns:
            Path to the saved PDF report.
        """
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.lib import colors
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
        except ImportError:
            logger.error("reportlab package is required for PDF generation")
            raise ImportError("reportlab package is required for PDF generation")
        
        # Validate parameters
        valid_parameters = [p for p in parameters if p in self.PARAMETER_INFO]
        if not valid_parameters:
            logger.error(f"No valid parameters provided: {parameters}")
            raise ValueError(f"No valid parameters provided: {parameters}")
        
        # Get data from database
        data = self._get_sensor_data(start_date, end_date)
        if not data:
            logger.error("No data available for the specified date range")
            raise ValueError("No data available for the specified date range")
        
        # Determine the output file path
        if output_file:
            save_path = output_file
        else:
            # Generate a filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            save_path = os.path.join(self.output_dir, f"pool_report_{timestamp}.pdf")
        
        # Create temporary directory for images
        with tempfile.TemporaryDirectory() as temp_dir:
            # Generate visualizations
            dashboard_path = self.create_multi_parameter_dashboard(
                valid_parameters, start_date, end_date,
                figsize=(8, 10), output_file=os.path.join(temp_dir, "dashboard.png")
            )
            
            stats_path = self.create_statistical_summary(
                valid_parameters, start_date, end_date,
                figsize=(8, 10), output_file=os.path.join(temp_dir, "stats.png")
            )
            
            if len(valid_parameters) >= 2:
                corr_path = self.create_correlation_matrix(
                    valid_parameters, start_date, end_date,
                    figsize=(8, 8), output_file=os.path.join(temp_dir, "correlation.png")
                )
            
            # Create PDF document
            doc = SimpleDocTemplate(save_path, pagesize=letter)
            styles = getSampleStyleSheet()
            
            # Create custom styles
            title_style = ParagraphStyle(
                'Title',
                parent=styles['Title'],
                fontSize=24,
                spaceAfter=12
            )
            
            heading_style = ParagraphStyle(
                'Heading',
                parent=styles['Heading1'],
                fontSize=18,
                spaceAfter=6
            )
            
            subheading_style = ParagraphStyle(
                'Subheading',
                parent=styles['Heading2'],
                fontSize=14,
                spaceAfter=6
            )
            
            normal_style = ParagraphStyle(
                'Normal',
                parent=styles['Normal'],
                fontSize=12,
                spaceAfter=6
            )
            
            # Build the document content
            content = []
            
            # Title
            date_range_str = ""
            if start_date and end_date:
                date_range_str = f"{start_date} to {end_date}"
            elif start_date:
                date_range_str = f"From {start_date}"
            elif end_date:
                date_range_str = f"Until {end_date}"
            
            content.append(Paragraph("Pool Chemistry Report", title_style))
            if date_range_str:
                content.append(Paragraph(f"Date Range: {date_range_str}", normal_style))
            content.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", normal_style))
            content.append(Spacer(1, 0.25*inch))
            
            # Dashboard section
            content.append(Paragraph("Pool Chemistry Dashboard", heading_style))
            content.append(Paragraph("The dashboard below shows the trends of all monitored parameters over time.", normal_style))
            content.append(Image(dashboard_path, width=7*inch, height=8.75*inch))
            content.append(Spacer(1, 0.25*inch))
            
            # Statistics section
            content.append(Paragraph("Statistical Summary", heading_style))
            content.append(Paragraph("This section provides statistical analysis of each parameter.", normal_style))
            content.append(Image(stats_path, width=7*inch, height=8.75*inch))
            content.append(Spacer(1, 0.25*inch))
            
            # Correlation section (if applicable)
            if len(valid_parameters) >= 2:
                content.append(Paragraph("Parameter Correlations", heading_style))
                content.append(Paragraph("This matrix shows how different parameters correlate with each other.", normal_style))
                content.append(Image(corr_path, width=7*inch, height=7*inch))
                content.append(Spacer(1, 0.25*inch))
            
            # Data table section
            content.append(Paragraph("Recent Measurements", heading_style))
            content.append(Paragraph("The table below shows the most recent measurements.", normal_style))
            
            # Create a table with the most recent data (up to 10 entries)
            recent_data = sorted(data, key=lambda x: x['timestamp'], reverse=True)[:10]
            
            # Prepare table data
            table_data = []
            
            # Header row
            header = ['Date']
            for param in valid_parameters:
                param_info = self.PARAMETER_INFO[param]
                header.append(f"{param_info['name']}\
({param_info['unit']})" if param_info['unit'] else param_info['name'])
            table_data.append(header)
            
            # Data rows
            for item in recent_data:
                row = [datetime.fromisoformat(item['timestamp']).strftime('%Y-%m-%d')]
                for param in valid_parameters:
                    if param in item and item[param] is not None:
                        row.append(f"{item[param]:.2f}")
                    else:
                        row.append("N/A")
                table_data.append(row)
            
            # Create the table
            table = Table(table_data)
            
            # Style the table
            table_style = TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ])
            
            # Add alternating row colors
            for i in range(1, len(table_data)):
                if i % 2 == 0:
                    table_style.add('BACKGROUND', (0, i), (-1, i), colors.lightgrey)
            
            table.setStyle(table_style)
            content.append(table)
            
            # Build the PDF
            doc.build(content)
        
        return save_path
    
    def _get_sensor_data(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get sensor data from the database.
        
        Args:
            start_date: Start date for the data (ISO format).
            end_date: End date for the data (ISO format).
            
        Returns:
            List of dictionaries containing sensor data.
        """
        try:
            # Get data from database service
            data = self.db_service.get_sensor_data()
            
            # Filter by date if specified
            if start_date or end_date:
                filtered_data = []
                
                for item in data:
                    timestamp = item['timestamp']
                    include = True
                    
                    if start_date and timestamp < start_date:
                        include = False
                    
                    if end_date and timestamp > end_date:
                        include = False
                    
                    if include:
                        filtered_data.append(item)
                
                return filtered_data
            
            return data
        except Exception as e:
            logger.error(f"Error retrieving sensor data: {e}")
            return []
