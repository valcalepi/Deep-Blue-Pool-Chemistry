
#!/usr/bin/env python3
"""
Advanced Reporting System - Interactive Charts Module

This module provides interactive chart functionality for HTML exports.
"""

import os
import sys
import logging
import json
from datetime import datetime
from typing import Dict, Any, List, Optional, Union

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/reporting.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("Reporting.InteractiveCharts")

# Check for optional dependencies
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    logger.warning("pandas not installed. Some interactive chart features will be limited.")

class InteractiveChartGenerator:
    """
    Generator for interactive charts in HTML exports.
    """
    
    def __init__(self):
        """Initialize the interactive chart generator."""
        pass
    
    def generate_chart_html(self, chart_type: str, data: List[Dict[str, Any]], 
                           params: Dict[str, Any], title: str = "") -> str:
        """
        Generate HTML for an interactive chart.
        
        Args:
            chart_type: Type of chart to create
            data: Data for the chart
            params: Parameters for the chart
            title: Title for the chart
            
        Returns:
            HTML string for the interactive chart
        """
        if not data:
            return self._generate_empty_chart_html("No data available")
        
        try:
            if chart_type == "line":
                return self._generate_line_chart_html(data, params, title)
            elif chart_type == "bar":
                return self._generate_bar_chart_html(data, params, title)
            elif chart_type == "pie":
                return self._generate_pie_chart_html(data, params, title)
            elif chart_type == "scatter":
                return self._generate_scatter_chart_html(data, params, title)
            elif chart_type == "area":
                return self._generate_area_chart_html(data, params, title)
            elif chart_type == "stacked_bar":
                return self._generate_stacked_bar_chart_html(data, params, title)
            elif chart_type == "multi_line":
                return self._generate_multi_line_chart_html(data, params, title)
            else:
                logger.warning(f"Unknown chart type for interactive HTML: {chart_type}")
                return self._generate_empty_chart_html(f"Chart type '{chart_type}' not supported for interactive HTML")
        except Exception as e:
            logger.error(f"Error generating interactive chart HTML: {e}")
            return self._generate_empty_chart_html(f"Error generating chart: {str(e)}")
    
    def _generate_empty_chart_html(self, message: str) -> str:
        """Generate HTML for an empty chart with a message."""
        return f"""
        <div class="chart-container" style="width: 100%; height: 400px; background-color: #f9f9f9; 
                                           border: 1px solid #ddd; display: flex; align-items: center; 
                                           justify-content: center; margin: 15px 0;">
            <p style="color: #666; font-style: italic;">{message}</p>
        </div>
        """
    
    def _generate_chart_container(self, chart_id: str, height: str = "400px") -> str:
        """Generate a container div for a chart."""
        return f'<div id="{chart_id}" style="width: 100%; height: {height}; margin: 15px 0;"></div>'
    
    def _generate_chart_dependencies(self) -> str:
        """Generate HTML for chart dependencies."""
        return """
        <!-- Chart.js -->
        <script src="https://cdn.jsdelivr.net/npm/chart.js@3.7.1/dist/chart.min.js"></script>
        <!-- ApexCharts -->
        <script src="https://cdn.jsdelivr.net/npm/apexcharts@3.35.0/dist/apexcharts.min.js"></script>
        <!-- Plotly.js -->
        <script src="https://cdn.plot.ly/plotly-2.12.1.min.js"></script>
        """
    
    def _generate_line_chart_html(self, data: List[Dict[str, Any]], params: Dict[str, Any], title: str) -> str:
        """Generate HTML for an interactive line chart using Chart.js."""
        # Extract parameters
        x_field = params.get("x_field", "date")
        y_field = params.get("y_field", "value")
        
        # Extract data
        x_values = [item.get(x_field) for item in data]
        y_values = [item.get(y_field) for item in data]
        
        # Generate unique chart ID
        chart_id = f"line-chart-{hash(str(data))}"
        
        # Create HTML
        html = self._generate_chart_container(chart_id)
        
        # Add JavaScript for chart
        html += f"""
        <script>
        document.addEventListener('DOMContentLoaded', function() {{
            const ctx = document.getElementById('{chart_id}').getContext('2d');
            const chart = new Chart(ctx, {{
                type: 'line',
                data: {{
                    labels: {json.dumps(x_values)},
                    datasets: [{{
                        label: '{y_field.capitalize()}',
                        data: {json.dumps(y_values)},
                        borderColor: '{params.get("line_color", "rgb(75, 192, 192)")}',
                        backgroundColor: '{params.get("fill_color", "rgba(75, 192, 192, 0.2)")}',
                        borderWidth: {params.get("line_width", 2)},
                        tension: {params.get("tension", 0.1)},
                        fill: {str(params.get("fill", False)).lower()}
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        title: {{
                            display: true,
                            text: '{title}'
                        }},
                        tooltip: {{
                            mode: 'index',
                            intersect: false,
                        }}
                    }},
                    scales: {{
                        x: {{
                            title: {{
                                display: true,
                                text: '{params.get("x_label", x_field.capitalize())}'
                            }}
                        }},
                        y: {{
                            title: {{
                                display: true,
                                text: '{params.get("y_label", y_field.capitalize())}'
                            }},
                            beginAtZero: {str(params.get("begin_at_zero", True)).lower()}
                        }}
                    }}
                }}
            }});
        }});
        </script>
        """
        
        return html
    
    def _generate_bar_chart_html(self, data: List[Dict[str, Any]], params: Dict[str, Any], title: str) -> str:
        """Generate HTML for an interactive bar chart using Chart.js."""
        # Extract parameters
        x_field = params.get("x_field", "category")
        y_field = params.get("y_field", "value")
        
        # Extract data
        x_values = [item.get(x_field) for item in data]
        y_values = [item.get(y_field) for item in data]
        
        # Generate unique chart ID
        chart_id = f"bar-chart-{hash(str(data))}"
        
        # Create HTML
        html = self._generate_chart_container(chart_id)
        
        # Add JavaScript for chart
        html += f"""
        <script>
        document.addEventListener('DOMContentLoaded', function() {{
            const ctx = document.getElementById('{chart_id}').getContext('2d');
            const chart = new Chart(ctx, {{
                type: 'bar',
                data: {{
                    labels: {json.dumps(x_values)},
                    datasets: [{{
                        label: '{y_field.capitalize()}',
                        data: {json.dumps(y_values)},
                        backgroundColor: '{params.get("bar_color", "rgba(75, 192, 192, 0.7)")}',
                        borderColor: '{params.get("border_color", "rgba(75, 192, 192, 1)")}',
                        borderWidth: {params.get("border_width", 1)}
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        title: {{
                            display: true,
                            text: '{title}'
                        }},
                        tooltip: {{
                            mode: 'index',
                            intersect: false,
                        }}
                    }},
                    scales: {{
                        x: {{
                            title: {{
                                display: true,
                                text: '{params.get("x_label", x_field.capitalize())}'
                            }}
                        }},
                        y: {{
                            title: {{
                                display: true,
                                text: '{params.get("y_label", y_field.capitalize())}'
                            }},
                            beginAtZero: true
                        }}
                    }}
                }}
            }});
        }});
        </script>
        """
        
        return html
    
    def _generate_pie_chart_html(self, data: List[Dict[str, Any]], params: Dict[str, Any], title: str) -> str:
        """Generate HTML for an interactive pie chart using Chart.js."""
        # Extract parameters
        value_field = params.get("value_field", "value")
        label_field = params.get("label_field", "label")
        
        # Extract data
        values = [item.get(value_field) for item in data]
        labels = [item.get(label_field) for item in data]
        
        # Generate unique chart ID
        chart_id = f"pie-chart-{hash(str(data))}"
        
        # Create HTML
        html = self._generate_chart_container(chart_id)
        
        # Add JavaScript for chart
        html += f"""
        <script>
        document.addEventListener('DOMContentLoaded', function() {{
            const ctx = document.getElementById('{chart_id}').getContext('2d');
            const chart = new Chart(ctx, {{
                type: 'pie',
                data: {{
                    labels: {json.dumps(labels)},
                    datasets: [{{
                        data: {json.dumps(values)},
                        backgroundColor: [
                            'rgba(255, 99, 132, 0.7)',
                            'rgba(54, 162, 235, 0.7)',
                            'rgba(255, 206, 86, 0.7)',
                            'rgba(75, 192, 192, 0.7)',
                            'rgba(153, 102, 255, 0.7)',
                            'rgba(255, 159, 64, 0.7)',
                            'rgba(199, 199, 199, 0.7)',
                            'rgba(83, 102, 255, 0.7)',
                            'rgba(40, 159, 64, 0.7)',
                            'rgba(210, 199, 199, 0.7)'
                        ],
                        borderColor: [
                            'rgba(255, 99, 132, 1)',
                            'rgba(54, 162, 235, 1)',
                            'rgba(255, 206, 86, 1)',
                            'rgba(75, 192, 192, 1)',
                            'rgba(153, 102, 255, 1)',
                            'rgba(255, 159, 64, 1)',
                            'rgba(199, 199, 199, 1)',
                            'rgba(83, 102, 255, 1)',
                            'rgba(40, 159, 64, 1)',
                            'rgba(210, 199, 199, 1)'
                        ],
                        borderWidth: 1
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        title: {{
                            display: true,
                            text: '{title}'
                        }},
                        legend: {{
                            position: 'right',
                        }},
                        tooltip: {{
                            callbacks: {{
                                label: function(context) {{
                                    const label = context.label || '';
                                    const value = context.raw || 0;
                                    const total = context.chart.data.datasets[0].data.reduce((a, b) => a + b, 0);
                                    const percentage = Math.round((value / total) * 100);
                                    return `${label}: ${value} (${percentage}%)`;
                                }}
                            }}
                        }}
                    }}
                }}
            }});
        }});
        </script>
        """
        
        return html
    
    def _generate_scatter_chart_html(self, data: List[Dict[str, Any]], params: Dict[str, Any], title: str) -> str:
        """Generate HTML for an interactive scatter chart using Plotly.js."""
        # Extract parameters
        x_field = params.get("x_field", "x")
        y_field = params.get("y_field", "y")
        
        # Extract data
        x_values = [item.get(x_field) for item in data]
        y_values = [item.get(y_field) for item in data]
        
        # Generate unique chart ID
        chart_id = f"scatter-chart-{hash(str(data))}"
        
        # Create HTML
        html = self._generate_chart_container(chart_id)
        
        # Add JavaScript for chart
        html += f"""
        <script>
        document.addEventListener('DOMContentLoaded', function() {{
            const data = [{{
                x: {json.dumps(x_values)},
                y: {json.dumps(y_values)},
                mode: 'markers',
                type: 'scatter',
                marker: {{
                    size: 10,
                    color: '{params.get("marker_color", "rgba(75, 192, 192, 0.7)")}',
                    line: {{
                        color: '{params.get("marker_border_color", "rgba(75, 192, 192, 1)")}',
                        width: 1
                    }}
                }}
            }}];
            
            const layout = {{
                title: '{title}',
                xaxis: {{
                    title: '{params.get("x_label", x_field.capitalize())}'
                }},
                yaxis: {{
                    title: '{params.get("y_label", y_field.capitalize())}'
                }},
                height: 400,
                margin: {{ t: 50 }}
            }};
            
            Plotly.newPlot('{chart_id}', data, layout, {{responsive: true}});
        }});
        </script>
        """
        
        return html
    
    def _generate_area_chart_html(self, data: List[Dict[str, Any]], params: Dict[str, Any], title: str) -> str:
        """Generate HTML for an interactive area chart using ApexCharts."""
        # Extract parameters
        x_field = params.get("x_field", "date")
        y_field = params.get("y_field", "value")
        
        # Extract data
        x_values = [item.get(x_field) for item in data]
        y_values = [item.get(y_field) for item in data]
        
        # Generate unique chart ID
        chart_id = f"area-chart-{hash(str(data))}"
        
        # Create HTML
        html = self._generate_chart_container(chart_id)
        
        # Add JavaScript for chart
        html += f"""
        <script>
        document.addEventListener('DOMContentLoaded', function() {{
            const options = {{
                series: [{{
                    name: '{y_field.capitalize()}',
                    data: {json.dumps(y_values)}
                }}],
                chart: {{
                    type: 'area',
                    height: 400,
                    zoom: {{
                        enabled: true
                    }}
                }},
                dataLabels: {{
                    enabled: false
                }},
                stroke: {{
                    curve: 'smooth',
                    width: {params.get("line_width", 2)}
                }},
                title: {{
                    text: '{title}',
                    align: 'left'
                }},
                xaxis: {{
                    categories: {json.dumps(x_values)},
                    title: {{
                        text: '{params.get("x_label", x_field.capitalize())}'
                    }}
                }},
                yaxis: {{
                    title: {{
                        text: '{params.get("y_label", y_field.capitalize())}'
                    }}
                }},
                fill: {{
                    type: 'gradient',
                    gradient: {{
                        shadeIntensity: 1,
                        opacityFrom: 0.7,
                        opacityTo: 0.3
                    }}
                }},
                tooltip: {{
                    y: {{
                        formatter: function(val) {{
                            return val
                        }}
                    }}
                }}
            }};

            const chart = new ApexCharts(document.getElementById('{chart_id}'), options);
            chart.render();
        }});
        </script>
        """
        
        return html
    
    def _generate_stacked_bar_chart_html(self, data: List[Dict[str, Any]], params: Dict[str, Any], title: str) -> str:
        """Generate HTML for an interactive stacked bar chart using ApexCharts."""
        # Extract parameters
        category_field = params.get("category_field", "category")
        stack_field = params.get("stack_field", "stack")
        value_field = params.get("value_field", "value")
        
        # Process data for stacked bar chart
        categories = sorted(list(set(item.get(category_field) for item in data)))
        stacks = sorted(list(set(item.get(stack_field) for item in data)))
        
        # Create data structure for stacked bars
        series_data = []
        for stack in stacks:
            stack_values = []
            for category in categories:
                # Find value for this stack and category
                value = 0
                for item in data:
                    if item.get(stack_field) == stack and item.get(category_field) == category:
                        value = item.get(value_field, 0)
                        break
                stack_values.append(value)
            
            series_data.append({
                "name": stack,
                "data": stack_values
            })
        
        # Generate unique chart ID
        chart_id = f"stacked-bar-chart-{hash(str(data))}"
        
        # Create HTML
        html = self._generate_chart_container(chart_id)
        
        # Add JavaScript for chart
        html += f"""
        <script>
        document.addEventListener('DOMContentLoaded', function() {{
            const options = {{
                series: {json.dumps(series_data)},
                chart: {{
                    type: 'bar',
                    height: 400,
                    stacked: true,
                    toolbar: {{
                        show: true
                    }},
                    zoom: {{
                        enabled: true
                    }}
                }},
                responsive: [{{
                    breakpoint: 480,
                    options: {{
                        legend: {{
                            position: 'bottom',
                            offsetX: -10,
                            offsetY: 0
                        }}
                    }}
                }}],
                plotOptions: {{
                    bar: {{
                        horizontal: false,
                    }},
                }},
                xaxis: {{
                    categories: {json.dumps(categories)},
                    title: {{
                        text: '{params.get("x_label", category_field.capitalize())}'
                    }}
                }},
                yaxis: {{
                    title: {{
                        text: '{params.get("y_label", value_field.capitalize())}'
                    }}
                }},
                legend: {{
                    position: 'right',
                    offsetY: 40
                }},
                fill: {{
                    opacity: 1
                }},
                title: {{
                    text: '{title}',
                    align: 'left'
                }}
            }};

            const chart = new ApexCharts(document.getElementById('{chart_id}'), options);
            chart.render();
        }});
        </script>
        """
        
        return html
    
    def _generate_multi_line_chart_html(self, data: List[Dict[str, Any]], params: Dict[str, Any], title: str) -> str:
        """Generate HTML for an interactive multi-line chart using ApexCharts."""
        # Extract parameters
        x_field = params.get("x_field", "date")
        y_fields = params.get("y_fields", [])
        series_field = params.get("series_field")
        
        # Generate unique chart ID
        chart_id = f"multi-line-chart-{hash(str(data))}"
        
        # Create HTML
        html = self._generate_chart_container(chart_id)
        
        # Process data based on parameters
        if series_field:
            # Group data by series
            series_values = sorted(list(set(item.get(series_field) for item in data if series_field in item)))
            categories = sorted(list(set(item.get(x_field) for item in data)))
            
            series_data = []
            for series in series_values:
                # Filter data for this series
                series_data_points = []
                for category in categories:
                    # Find value for this series and category
                    value = 0
                    for item in data:
                        if item.get(series_field) == series and item.get(x_field) == category:
                            value = item.get(params.get("value_field", "value"), 0)
                            break
                    series_data_points.append(value)
                
                series_data.append({
                    "name": series,
                    "data": series_data_points
                })
            
            # Add JavaScript for chart
            html += f"""
            <script>
            document.addEventListener('DOMContentLoaded', function() {{
                const options = {{
                    series: {json.dumps(series_data)},
                    chart: {{
                        height: 400,
                        type: 'line',
                        zoom: {{
                            enabled: true
                        }}
                    }},
                    dataLabels: {{
                        enabled: false
                    }},
                    stroke: {{
                        curve: 'smooth',
                        width: 2
                    }},
                    title: {{
                        text: '{title}',
                        align: 'left'
                    }},
                    grid: {{
                        row: {{
                            colors: ['#f3f3f3', 'transparent'],
                            opacity: 0.5
                        }},
                    }},
                    xaxis: {{
                        categories: {json.dumps(categories)},
                        title: {{
                            text: '{params.get("x_label", x_field.capitalize())}'
                        }}
                    }},
                    yaxis: {{
                        title: {{
                            text: '{params.get("y_label", "Value")}'
                        }}
                    }},
                    legend: {{
                        position: 'top'
                    }}
                }};

                const chart = new ApexCharts(document.getElementById('{chart_id}'), options);
                chart.render();
            }});
            </script>
            """
        
        elif y_fields:
            # Multiple y fields in the same data
            # Sort data by x_field
            sorted_data = sorted(data, key=lambda x: x.get(x_field, 0))
            
            # Extract x values
            x_values = [item.get(x_field) for item in sorted_data]
            
            # Create series data
            series_data = []
            for field in y_fields:
                y_values = [item.get(field) for item in sorted_data]
                series_data.append({
                    "name": field.capitalize(),
                    "data": y_values
                })
            
            # Add JavaScript for chart
            html += f"""
            <script>
            document.addEventListener('DOMContentLoaded', function() {{
                const options = {{
                    series: {json.dumps(series_data)},
                    chart: {{
                        height: 400,
                        type: 'line',
                        zoom: {{
                            enabled: true
                        }}
                    }},
                    dataLabels: {{
                        enabled: false
                    }},
                    stroke: {{
                        curve: 'smooth',
                        width: 2
                    }},
                    title: {{
                        text: '{title}',
                        align: 'left'
                    }},
                    grid: {{
                        row: {{
                            colors: ['#f3f3f3', 'transparent'],
                            opacity: 0.5
                        }},
                    }},
                    xaxis: {{
                        categories: {json.dumps(x_values)},
                        title: {{
                            text: '{params.get("x_label", x_field.capitalize())}'
                        }}
                    }},
                    yaxis: {{
                        title: {{
                            text: '{params.get("y_label", "Value")}'
                        }}
                    }},
                    legend: {{
                        position: 'top'
                    }}
                }};

                const chart = new ApexCharts(document.getElementById('{chart_id}'), options);
                chart.render();
            }});
            </script>
            """
        
        else:
            # Default to single line chart
            return self._generate_line_chart_html(data, params, title)
        
        return html

class HTMLExporter:
    """
    HTML exporter with interactive charts.
    """
    
    def __init__(self):
        """Initialize the HTML exporter."""
        self.chart_generator = InteractiveChartGenerator()
    
    def generate_html_report(self, report_title: str, sections: List[Dict[str, Any]], 
                            data: Dict[str, Any]) -> str:
        """
        Generate a complete HTML report with interactive charts.
        
        Args:
            report_title: Title of the report
            sections: List of section definitions
            data: Report data
            
        Returns:
            Complete HTML document as a string
        """
        # Start HTML document
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{report_title}</title>
            <style>
                body {{ 
                    font-family: Arial, sans-serif; 
                    margin: 20px; 
                    line-height: 1.6;
                    color: #333;
                }}
                h1 {{ 
                    color: #2c3e50; 
                    border-bottom: 2px solid #3498db;
                    padding-bottom: 10px;
                }}
                h2 {{ 
                    color: #3498db; 
                    margin-top: 30px;
                    border-bottom: 1px solid #ddd;
                    padding-bottom: 5px;
                }}
                table {{ 
                    border-collapse: collapse; 
                    width: 100%; 
                    margin: 15px 0; 
                }}
                th, td {{ 
                    border: 1px solid #ddd; 
                    padding: 12px; 
                    text-align: left; 
                }}
                th {{ 
                    background-color: #f2f2f2; 
                    font-weight: bold;
                }}
                tr:nth-child(even) {{ 
                    background-color: #f9f9f9; 
                }}
                .chart-container {{ 
                    margin: 20px 0; 
                    border: 1px solid #eee;
                    padding: 15px;
                    border-radius: 5px;
                    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                }}
                .footer {{ 
                    margin-top: 50px; 
                    font-size: 0.8em; 
                    color: #7f8c8d; 
                    text-align: center;
                    border-top: 1px solid #eee;
                    padding-top: 20px;
                }}
                @media print {{
                    .chart-container {{ 
                        break-inside: avoid;
                        page-break-inside: avoid;
                    }}
                    h2 {{ 
                        break-after: avoid;
                        page-break-after: avoid;
                    }}
                    h1 {{ 
                        break-after: avoid;
                        page-break-after: avoid;
                    }}
                }}
            </style>
            <!-- Chart Dependencies -->
            <script src="https://cdn.jsdelivr.net/npm/chart.js@3.7.1/dist/chart.min.js"></script>
            <script src="https://cdn.jsdelivr.net/npm/apexcharts@3.35.0/dist/apexcharts.min.js"></script>
            <script src="https://cdn.plot.ly/plotly-2.12.1.min.js"></script>
        </head>
        <body>
            <h1>{report_title}</h1>
            <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
        """
        
        # Process each section
        for section in sections:
            html += f"<h2>{section['title']}</h2>"
            
            if section["type"] == "text":
                content = section.get("content", "")
                if "content" in data.get(section["title"].lower().replace(" ", "_"), {}):
                    content = data[section["title"].lower().replace(" ", "_")]["content"]
                html += f"<p>{content}</p>"
                
            elif section["type"] == "table":
                data_source = section.get("data_source", "")
                if data_source in data:
                    table_data = data[data_source]
                    if table_data and isinstance(table_data, list) and len(table_data) > 0:
                        # Create table header
                        html += "<table><thead><tr>"
                        for key in table_data[0].keys():
                            html += f"<th>{key}</th>"
                        html += "</tr></thead><tbody>"
                        
                        # Create table rows
                        for row in table_data:
                            html += "<tr>"
                            for value in row.values():
                                html += f"<td>{value}</td>"
                            html += "</tr>"
                        
                        html += "</tbody></table>"
                    else:
                        html += "<p>No data available for this table.</p>"
                else:
                    html += "<p>Data source not found.</p>"
                    
            elif section["type"] == "chart":
                chart_type = section.get("chart_type", "line")
                data_source = section.get("data_source", "")
                
                if data_source in data:
                    chart_data = data[data_source]
                    params = section.get("parameters", {})
                    
                    # Generate interactive chart
                    html += self.chart_generator.generate_chart_html(
                        chart_type, chart_data, params, section["title"]
                    )
                else:
                    html += self.chart_generator._generate_empty_chart_html(f"No data found for {data_source}")
                
            elif section["type"] == "analysis":
                analysis_type = section.get("analysis_type", "")
                if analysis_type in data:
                    analysis_data = data[analysis_type]
                    if "recommendations" in analysis_data:
                        html += "<h3>Recommendations</h3>"
                        html += "<ul>"
                        for rec in analysis_data["recommendations"]:
                            html += f"<li>{rec}</li>"
                        html += "</ul>"
                    if "analysis" in analysis_data:
                        html += f"<p>{analysis_data['analysis']}</p>"
                else:
                    html += f"<p>No analysis data available for {analysis_type}.</p>"
        
        # Add footer
        html += f"""
            <div class="footer">
                <p>Deep Blue Pool Chemistry Report - {datetime.now().strftime('%Y-%m-%d')}</p>
            </div>
        </body>
        </html>
        """
        
        return html
