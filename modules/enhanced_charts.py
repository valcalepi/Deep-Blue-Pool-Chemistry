
#!/usr/bin/env python3
"""
Advanced Reporting System - Enhanced Charts Module

This module provides additional chart types and visualization options for the reporting system.
"""

import os
import sys
import logging
import json
from datetime import datetime
from typing import Dict, Any, List, Optional, Union, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/reporting.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("Reporting.EnhancedCharts")

# Check for matplotlib
try:
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_pdf import PdfPages
    import numpy as np
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    logger.warning("matplotlib not installed. Enhanced charts will not be available.")

class ChartGenerator:
    """
    Enhanced chart generator for the reporting system.
    """
    
    def __init__(self):
        """Initialize the chart generator."""
        if not MATPLOTLIB_AVAILABLE:
            logger.error("matplotlib is required for chart generation")
            raise ImportError("matplotlib is required for chart generation")
    
    def create_chart(self, chart_type: str, data: List[Dict[str, Any]], 
                    params: Dict[str, Any], title: str = "") -> Figure:
        """
        Create a chart based on the specified type and data.
        
        Args:
            chart_type: Type of chart to create
            data: Data for the chart
            params: Parameters for the chart
            title: Title for the chart
            
        Returns:
            matplotlib Figure object
        """
        if not data:
            return self._create_empty_chart(f"No data available for {title}")
        
        # Create figure with appropriate size
        fig = plt.figure(figsize=(8.5, 5))
        
        # Extract common parameters
        x_field = params.get("x_field", "date")
        y_field = params.get("y_field", "value")
        
        # Create chart based on type
        try:
            if chart_type == "line":
                self._create_line_chart(fig, data, x_field, y_field, params, title)
            elif chart_type == "bar":
                self._create_bar_chart(fig, data, x_field, y_field, params, title)
            elif chart_type == "pie":
                self._create_pie_chart(fig, data, params, title)
            elif chart_type == "scatter":
                self._create_scatter_chart(fig, data, x_field, y_field, params, title)
            elif chart_type == "area":
                self._create_area_chart(fig, data, x_field, y_field, params, title)
            elif chart_type == "stacked_bar":
                self._create_stacked_bar_chart(fig, data, params, title)
            elif chart_type == "histogram":
                self._create_histogram_chart(fig, data, y_field, params, title)
            elif chart_type == "box_plot":
                self._create_box_plot(fig, data, params, title)
            elif chart_type == "heatmap":
                self._create_heatmap(fig, data, params, title)
            elif chart_type == "radar":
                self._create_radar_chart(fig, data, params, title)
            elif chart_type == "bubble":
                self._create_bubble_chart(fig, data, params, title)
            elif chart_type == "multi_line":
                self._create_multi_line_chart(fig, data, params, title)
            else:
                logger.warning(f"Unknown chart type: {chart_type}, defaulting to line chart")
                self._create_line_chart(fig, data, x_field, y_field, params, title)
        except Exception as e:
            logger.error(f"Error creating {chart_type} chart: {e}")
            plt.close(fig)
            return self._create_empty_chart(f"Error creating {chart_type} chart: {str(e)}")
        
        return fig
    
    def _create_empty_chart(self, message: str) -> Figure:
        """Create an empty chart with a message."""
        fig = plt.figure(figsize=(8.5, 5))
        plt.figtext(0.5, 0.5, message, ha="center", va="center", fontsize=12)
        plt.axis('off')
        return fig
    
    def _create_line_chart(self, fig: Figure, data: List[Dict[str, Any]], 
                          x_field: str, y_field: str, params: Dict[str, Any], title: str):
        """Create a line chart."""
        ax = fig.add_subplot(111)
        
        # Extract data
        x_values = [item.get(x_field) for item in data]
        y_values = [item.get(y_field) for item in data]
        
        # Plot line
        ax.plot(x_values, y_values, marker='o', linestyle='-', 
                color=params.get("line_color", "blue"), 
                linewidth=params.get("line_width", 2),
                markersize=params.get("marker_size", 5))
        
        # Add ideal range if specified
        ideal_range = params.get("ideal_range")
        if ideal_range and len(ideal_range) == 2:
            ax.axhspan(ideal_range[0], ideal_range[1], alpha=0.2, color='green')
            ax.axhline(y=ideal_range[0], color='green', linestyle='--', alpha=0.7)
            ax.axhline(y=ideal_range[1], color='green', linestyle='--', alpha=0.7)
        
        # Add labels and title
        ax.set_title(title)
        ax.set_xlabel(params.get("x_label", x_field.capitalize()))
        ax.set_ylabel(params.get("y_label", y_field.capitalize()))
        
        # Add grid
        ax.grid(True, linestyle='--', alpha=0.7)
        
        # Format dates if x_field contains date values
        if x_values and isinstance(x_values[0], (datetime, str)) and "date" in x_field.lower():
            fig.autofmt_xdate()
            if isinstance(x_values[0], str):
                try:
                    # Try to convert string dates to datetime objects
                    import dateutil.parser
                    x_values = [dateutil.parser.parse(x) for x in x_values if x]
                    ax.plot(x_values, y_values, marker='o')
                    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
                except:
                    pass
        
        # Add annotations if specified
        if params.get("show_values", False):
            for x, y in zip(x_values, y_values):
                ax.annotate(f"{y:.1f}", (x, y), textcoords="offset points", 
                           xytext=(0, 10), ha='center')
    
    def _create_bar_chart(self, fig: Figure, data: List[Dict[str, Any]], 
                         x_field: str, y_field: str, params: Dict[str, Any], title: str):
        """Create a bar chart."""
        ax = fig.add_subplot(111)
        
        # Extract data
        x_values = [item.get(x_field) for item in data]
        y_values = [item.get(y_field) for item in data]
        
        # Plot bars
        bars = ax.bar(x_values, y_values, 
                     color=params.get("bar_color", "skyblue"),
                     edgecolor=params.get("edge_color", "black"),
                     alpha=params.get("alpha", 0.7),
                     width=params.get("bar_width", 0.8))
        
        # Add labels and title
        ax.set_title(title)
        ax.set_xlabel(params.get("x_label", x_field.capitalize()))
        ax.set_ylabel(params.get("y_label", y_field.capitalize()))
        
        # Add grid
        ax.grid(True, axis='y', linestyle='--', alpha=0.7)
        
        # Rotate x labels if there are many bars
        if len(x_values) > 5:
            plt.xticks(rotation=45, ha='right')
        
        # Add value labels on top of bars if specified
        if params.get("show_values", False):
            for bar in bars:
                height = bar.get_height()
                ax.annotate(f"{height:.1f}", 
                           xy=(bar.get_x() + bar.get_width() / 2, height),
                           xytext=(0, 3),  # 3 points vertical offset
                           textcoords="offset points",
                           ha='center', va='bottom')
        
        fig.tight_layout()
    
    def _create_pie_chart(self, fig: Figure, data: List[Dict[str, Any]], 
                         params: Dict[str, Any], title: str):
        """Create a pie chart."""
        ax = fig.add_subplot(111)
        
        # Extract parameters
        value_field = params.get("value_field", "value")
        label_field = params.get("label_field", "label")
        
        # Extract data
        values = [item.get(value_field) for item in data]
        labels = [item.get(label_field) for item in data]
        
        # Plot pie chart
        wedges, texts, autotexts = ax.pie(
            values, 
            labels=labels if not params.get("legend", True) else None,
            autopct=params.get("percentage_format", '%1.1f%%'),
            startangle=params.get("start_angle", 90),
            shadow=params.get("shadow", False),
            explode=params.get("explode", None),
            colors=params.get("colors", None)
        )
        
        # Customize text
        for autotext in autotexts:
            autotext.set_color(params.get("percentage_color", "white"))
            autotext.set_fontsize(params.get("percentage_fontsize", 10))
        
        # Add title
        ax.set_title(title)
        
        # Equal aspect ratio ensures that pie is drawn as a circle
        ax.axis('equal')
        
        # Add legend if specified
        if params.get("legend", True):
            ax.legend(
                wedges, labels,
                title=params.get("legend_title", "Categories"),
                loc=params.get("legend_location", "center left"),
                bbox_to_anchor=params.get("legend_position", (1, 0, 0.5, 1))
            )
    
    def _create_scatter_chart(self, fig: Figure, data: List[Dict[str, Any]], 
                             x_field: str, y_field: str, params: Dict[str, Any], title: str):
        """Create a scatter plot."""
        ax = fig.add_subplot(111)
        
        # Extract data
        x_values = [item.get(x_field) for item in data]
        y_values = [item.get(y_field) for item in data]
        
        # Extract optional parameters
        color_field = params.get("color_field")
        size_field = params.get("size_field")
        
        # Determine colors and sizes if specified
        colors = None
        sizes = None
        
        if color_field and color_field in data[0]:
            colors = [item.get(color_field) for item in data]
        
        if size_field and size_field in data[0]:
            sizes = [item.get(size_field) for item in data]
            # Scale sizes to reasonable values
            if sizes:
                min_size = params.get("min_size", 20)
                max_size = params.get("max_size", 200)
                sizes = [min_size + (max_size - min_size) * (s - min(sizes)) / (max(sizes) - min(sizes)) if max(sizes) != min(sizes) else min_size for s in sizes]
        
        # Plot scatter
        scatter = ax.scatter(
            x_values, y_values,
            c=colors,
            s=sizes,
            alpha=params.get("alpha", 0.7),
            edgecolors=params.get("edge_color", "black"),
            cmap=params.get("colormap", "viridis")
        )
        
        # Add colorbar if using colors
        if colors and params.get("show_colorbar", True):
            cbar = fig.colorbar(scatter, ax=ax)
            cbar.set_label(color_field.capitalize())
        
        # Add labels and title
        ax.set_title(title)
        ax.set_xlabel(params.get("x_label", x_field.capitalize()))
        ax.set_ylabel(params.get("y_label", y_field.capitalize()))
        
        # Add grid
        ax.grid(True, linestyle='--', alpha=0.7)
        
        # Add trend line if specified
        if params.get("trend_line", False) and len(x_values) > 1:
            try:
                # Convert to numeric if needed
                x_numeric = x_values
                if not all(isinstance(x, (int, float)) for x in x_values):
                    x_numeric = list(range(len(x_values)))
                
                z = np.polyfit(x_numeric, y_values, 1)
                p = np.poly1d(z)
                ax.plot(x_values, p(x_numeric), "r--", alpha=0.8)
            except Exception as e:
                logger.warning(f"Could not add trend line: {e}")
    
    def _create_area_chart(self, fig: Figure, data: List[Dict[str, Any]], 
                          x_field: str, y_field: str, params: Dict[str, Any], title: str):
        """Create an area chart."""
        ax = fig.add_subplot(111)
        
        # Extract data
        x_values = [item.get(x_field) for item in data]
        y_values = [item.get(y_field) for item in data]
        
        # Plot area
        ax.fill_between(
            x_values, y_values, 
            color=params.get("fill_color", "skyblue"),
            alpha=params.get("alpha", 0.4)
        )
        
        # Add line on top
        ax.plot(
            x_values, y_values,
            color=params.get("line_color", "blue"),
            linewidth=params.get("line_width", 2)
        )
        
        # Add labels and title
        ax.set_title(title)
        ax.set_xlabel(params.get("x_label", x_field.capitalize()))
        ax.set_ylabel(params.get("y_label", y_field.capitalize()))
        
        # Add grid
        ax.grid(True, linestyle='--', alpha=0.7)
        
        # Format dates if x_field contains date values
        if x_values and isinstance(x_values[0], (datetime, str)) and "date" in x_field.lower():
            fig.autofmt_xdate()
    
    def _create_stacked_bar_chart(self, fig: Figure, data: List[Dict[str, Any]], 
                                 params: Dict[str, Any], title: str):
        """Create a stacked bar chart."""
        ax = fig.add_subplot(111)
        
        # Extract parameters
        category_field = params.get("category_field", "category")
        stack_field = params.get("stack_field", "stack")
        value_field = params.get("value_field", "value")
        
        # Process data for stacked bar chart
        categories = sorted(list(set(item.get(category_field) for item in data)))
        stacks = sorted(list(set(item.get(stack_field) for item in data)))
        
        # Create data structure for stacked bars
        data_dict = {category: {stack: 0 for stack in stacks} for category in categories}
        for item in data:
            cat = item.get(category_field)
            stack = item.get(stack_field)
            val = item.get(value_field, 0)
            if cat in data_dict and stack in data_dict[cat]:
                data_dict[cat][stack] = val
        
        # Plot stacked bars
        bottom = np.zeros(len(categories))
        for stack in stacks:
            values = [data_dict[cat][stack] for cat in categories]
            ax.bar(
                categories, values, 
                bottom=bottom,
                label=stack,
                alpha=params.get("alpha", 0.7)
            )
            bottom += values
        
        # Add labels and title
        ax.set_title(title)
        ax.set_xlabel(params.get("x_label", category_field.capitalize()))
        ax.set_ylabel(params.get("y_label", value_field.capitalize()))
        
        # Add legend
        ax.legend(title=params.get("legend_title", stack_field.capitalize()))
        
        # Add grid
        ax.grid(True, axis='y', linestyle='--', alpha=0.7)
        
        # Rotate x labels if there are many categories
        if len(categories) > 5:
            plt.xticks(rotation=45, ha='right')
        
        fig.tight_layout()
    
    def _create_histogram_chart(self, fig: Figure, data: List[Dict[str, Any]], 
                               value_field: str, params: Dict[str, Any], title: str):
        """Create a histogram."""
        ax = fig.add_subplot(111)
        
        # Extract data
        values = [item.get(value_field) for item in data if item.get(value_field) is not None]
        
        # Plot histogram
        n, bins, patches = ax.hist(
            values,
            bins=params.get("bins", 10),
            color=params.get("color", "skyblue"),
            edgecolor=params.get("edge_color", "black"),
            alpha=params.get("alpha", 0.7)
        )
        
        # Add labels and title
        ax.set_title(title)
        ax.set_xlabel(params.get("x_label", value_field.capitalize()))
        ax.set_ylabel(params.get("y_label", "Frequency"))
        
        # Add grid
        ax.grid(True, axis='y', linestyle='--', alpha=0.7)
        
        # Add mean line if specified
        if params.get("show_mean", False) and values:
            mean_val = sum(values) / len(values)
            ax.axvline(mean_val, color='red', linestyle='dashed', linewidth=1)
            ax.text(mean_val, ax.get_ylim()[1]*0.9, f'Mean: {mean_val:.2f}', 
                   horizontalalignment='center', color='red')
    
    def _create_box_plot(self, fig: Figure, data: List[Dict[str, Any]], 
                        params: Dict[str, Any], title: str):
        """Create a box plot."""
        ax = fig.add_subplot(111)
        
        # Extract parameters
        category_field = params.get("category_field", "category")
        value_field = params.get("value_field", "value")
        
        # Process data for box plot
        categories = sorted(list(set(item.get(category_field) for item in data)))
        box_data = []
        
        for category in categories:
            values = [item.get(value_field) for item in data if item.get(category_field) == category]
            box_data.append(values)
        
        # Plot box plot
        ax.boxplot(
            box_data,
            labels=categories,
            patch_artist=True,
            boxprops=dict(facecolor=params.get("box_color", "skyblue")),
            medianprops=dict(color=params.get("median_color", "red")),
            flierprops=dict(marker=params.get("outlier_marker", "o"), 
                           markerfacecolor=params.get("outlier_color", "red"))
        )
        
        # Add labels and title
        ax.set_title(title)
        ax.set_xlabel(params.get("x_label", category_field.capitalize()))
        ax.set_ylabel(params.get("y_label", value_field.capitalize()))
        
        # Add grid
        ax.grid(True, axis='y', linestyle='--', alpha=0.7)
        
        # Rotate x labels if there are many categories
        if len(categories) > 5:
            plt.xticks(rotation=45, ha='right')
        
        fig.tight_layout()
    
    def _create_heatmap(self, fig: Figure, data: List[Dict[str, Any]], 
                       params: Dict[str, Any], title: str):
        """Create a heatmap."""
        ax = fig.add_subplot(111)
        
        # Extract parameters
        x_field = params.get("x_field", "x")
        y_field = params.get("y_field", "y")
        value_field = params.get("value_field", "value")
        
        # Process data for heatmap
        x_values = sorted(list(set(item.get(x_field) for item in data)))
        y_values = sorted(list(set(item.get(y_field) for item in data)))
        
        # Create matrix for heatmap
        matrix = np.zeros((len(y_values), len(x_values)))
        
        for item in data:
            x = item.get(x_field)
            y = item.get(y_field)
            value = item.get(value_field, 0)
            
            if x in x_values and y in y_values:
                x_idx = x_values.index(x)
                y_idx = y_values.index(y)
                matrix[y_idx, x_idx] = value
        
        # Plot heatmap
        im = ax.imshow(
            matrix,
            cmap=params.get("colormap", "viridis"),
            interpolation=params.get("interpolation", "nearest"),
            aspect=params.get("aspect", "auto")
        )
        
        # Add colorbar
        cbar = fig.colorbar(im, ax=ax)
        cbar.set_label(value_field.capitalize())
        
        # Set ticks and labels
        ax.set_xticks(np.arange(len(x_values)))
        ax.set_yticks(np.arange(len(y_values)))
        ax.set_xticklabels(x_values)
        ax.set_yticklabels(y_values)
        
        # Rotate x labels if needed
        if len(x_values) > 5:
            plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
        
        # Add labels and title
        ax.set_title(title)
        ax.set_xlabel(params.get("x_label", x_field.capitalize()))
        ax.set_ylabel(params.get("y_label", y_field.capitalize()))
        
        # Add text annotations if specified
        if params.get("show_values", False):
            for i in range(len(y_values)):
                for j in range(len(x_values)):
                    text = ax.text(j, i, f"{matrix[i, j]:.1f}",
                                  ha="center", va="center", color="w")
        
        fig.tight_layout()
    
    def _create_radar_chart(self, fig: Figure, data: List[Dict[str, Any]], 
                           params: Dict[str, Any], title: str):
        """Create a radar chart."""
        # Create polar axes
        ax = fig.add_subplot(111, polar=True)
        
        # Extract parameters
        category_field = params.get("category_field", "category")
        value_field = params.get("value_field", "value")
        group_field = params.get("group_field")
        
        # Process data for radar chart
        categories = sorted(list(set(item.get(category_field) for item in data)))
        num_categories = len(categories)
        
        if num_categories < 3:
            logger.warning("Radar chart requires at least 3 categories")
            plt.figtext(0.5, 0.5, "Radar chart requires at least 3 categories", 
                       ha="center", va="center", fontsize=12)
            return
        
        # Set angles for each category
        angles = np.linspace(0, 2*np.pi, num_categories, endpoint=False).tolist()
        angles += angles[:1]  # Close the loop
        
        # If grouping is specified
        if group_field and any(group_field in item for item in data):
            groups = sorted(list(set(item.get(group_field) for item in data if group_field in item)))
            
            for group in groups:
                values = []
                for category in categories:
                    # Find value for this group and category
                    value = 0
                    for item in data:
                        if item.get(group_field) == group and item.get(category_field) == category:
                            value = item.get(value_field, 0)
                            break
                    values.append(value)
                
                # Close the loop
                values += values[:1]
                
                # Plot the radar
                ax.plot(angles, values, linewidth=2, label=group)
                ax.fill(angles, values, alpha=0.25)
        else:
            # Simple radar chart with one series
            values = []
            for category in categories:
                # Find value for this category
                value = 0
                for item in data:
                    if item.get(category_field) == category:
                        value = item.get(value_field, 0)
                        break
                values.append(value)
            
            # Close the loop
            values += values[:1]
            categories += categories[:1]
            
            # Plot the radar
            ax.plot(angles, values, linewidth=2)
            ax.fill(angles, values, alpha=0.25)
        
        # Set category labels
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories[:-1])
        
        # Add title
        ax.set_title(title)
        
        # Add legend if grouping is used
        if group_field and len(groups) > 1:
            ax.legend(loc='upper right', bbox_to_anchor=(0.1, 0.1))
    
    def _create_bubble_chart(self, fig: Figure, data: List[Dict[str, Any]], 
                            params: Dict[str, Any], title: str):
        """Create a bubble chart."""
        ax = fig.add_subplot(111)
        
        # Extract parameters
        x_field = params.get("x_field", "x")
        y_field = params.get("y_field", "y")
        size_field = params.get("size_field", "size")
        color_field = params.get("color_field")
        
        # Extract data
        x_values = [item.get(x_field) for item in data]
        y_values = [item.get(y_field) for item in data]
        sizes = [item.get(size_field, 100) for item in data]
        
        # Scale sizes to reasonable values
        if sizes:
            min_size = params.get("min_size", 20)
            max_size = params.get("max_size", 500)
            if max(sizes) != min(sizes):
                sizes = [min_size + (max_size - min_size) * (s - min(sizes)) / (max(sizes) - min(sizes)) for s in sizes]
            else:
                sizes = [min_size for _ in sizes]
        
        # Determine colors if specified
        colors = None
        if color_field and color_field in data[0]:
            colors = [item.get(color_field) for item in data]
        
        # Plot bubbles
        scatter = ax.scatter(
            x_values, y_values, s=sizes,
            c=colors,
            alpha=params.get("alpha", 0.6),
            edgecolors=params.get("edge_color", "black"),
            cmap=params.get("colormap", "viridis")
        )
        
        # Add colorbar if using colors
        if colors and params.get("show_colorbar", True):
            cbar = fig.colorbar(scatter, ax=ax)
            cbar.set_label(color_field.capitalize())
        
        # Add labels and title
        ax.set_title(title)
        ax.set_xlabel(params.get("x_label", x_field.capitalize()))
        ax.set_ylabel(params.get("y_label", y_field.capitalize()))
        
        # Add grid
        ax.grid(True, linestyle='--', alpha=0.7)
        
        # Add labels for bubbles if specified
        if params.get("show_labels", False) and "label_field" in params:
            label_field = params.get("label_field")
            for i, item in enumerate(data):
                if label_field in item:
                    ax.annotate(
                        item.get(label_field),
                        (x_values[i], y_values[i]),
                        xytext=(5, 5),
                        textcoords="offset points"
                    )
    
    def _create_multi_line_chart(self, fig: Figure, data: List[Dict[str, Any]], 
                               params: Dict[str, Any], title: str):
        """Create a multi-line chart."""
        ax = fig.add_subplot(111)
        
        # Extract parameters
        x_field = params.get("x_field", "date")
        y_fields = params.get("y_fields", [])
        series_field = params.get("series_field")
        
        if series_field:
            # Group data by series
            series_values = sorted(list(set(item.get(series_field) for item in data if series_field in item)))
            
            for series in series_values:
                # Filter data for this series
                series_data = [item for item in data if item.get(series_field) == series]
                
                # Sort by x_field
                series_data.sort(key=lambda x: x.get(x_field, 0))
                
                # Extract x and y values
                x_values = [item.get(x_field) for item in series_data]
                y_values = [item.get(params.get("value_field", "value")) for item in series_data]
                
                # Plot line
                ax.plot(x_values, y_values, marker='o', linestyle='-', label=series)
        
        elif y_fields:
            # Multiple y fields in the same data
            # Sort data by x_field
            sorted_data = sorted(data, key=lambda x: x.get(x_field, 0))
            
            # Extract x values
            x_values = [item.get(x_field) for item in sorted_data]
            
            # Plot each y field
            for field in y_fields:
                y_values = [item.get(field) for item in sorted_data]
                ax.plot(x_values, y_values, marker='o', linestyle='-', label=field.capitalize())
        
        else:
            # Default to single line chart
            self._create_line_chart(fig, data, x_field, params.get("value_field", "value"), params, title)
            return
        
        # Add labels and title
        ax.set_title(title)
        ax.set_xlabel(params.get("x_label", x_field.capitalize()))
        ax.set_ylabel(params.get("y_label", "Value"))
        
        # Add grid
        ax.grid(True, linestyle='--', alpha=0.7)
        
        # Add legend
        ax.legend()
        
        # Format dates if x_field contains date values
        if x_values and isinstance(x_values[0], (datetime, str)) and "date" in x_field.lower():
            fig.autofmt_xdate()
