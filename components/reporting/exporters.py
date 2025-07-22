#!/usr/bin/env python3
"""
Advanced Reporting System – Unified Export & Visualization

Exports pool chemistry reports in multiple formats including:
- PDF (with charts)
- CSV
- Excel
- HTML (with interactive options)

Supports enhanced charts and fallback to basic matplotlib rendering.
"""

import os
import sys
import logging
import json
import csv
import tempfile
from datetime import datetime
from typing import Dict, Any, List, Optional, Union

# Internal models
from components.reporting.models import Report, ReportTemplate

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/reporting.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("Reporting.Exporters")

# Dependency checks
try:
    from components.reporting.enhanced_charts import ChartGenerator
    ENHANCED_CHARTS_AVAILABLE = True
except ImportError:
    ENHANCED_CHARTS_AVAILABLE = False
    logger.warning("Enhanced charts module not available.")

try:
    from components.reporting.interactive_charts import HTMLExporter
    INTERACTIVE_CHARTS_AVAILABLE = True
except ImportError:
    INTERACTIVE_CHARTS_AVAILABLE = False
    logger.warning("Interactive charts module not available.")

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    logger.warning("pandas not installed. Excel export will be limited.")

try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_pdf import PdfPages
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    logger.warning("matplotlib not installed. PDF export will be limited.")

try:
    import pdfkit
    PDFKIT_AVAILABLE = True
except ImportError:
    PDFKIT_AVAILABLE = False
    logger.warning("pdfkit not installed. HTML to PDF conversion disabled.")

# Ensure export folders
for folder in ["pdf", "csv", "excel", "html"]:
    os.makedirs(f"data/exports/{folder}", exist_ok=True)

# PDF chart generator
def _add_chart_to_pdf(report: Report, section: Dict[str, Any], pdf, chart_generator: Optional[ChartGenerator] = None):
    """Render a chart section into the PDF."""
    try:
        data_source = section.get("data_source", "")
        if data_source not in report.data:
            raise ValueError(f"No data available for source: {data_source}")
        
        chart_data = report.data[data_source]
        params = section.get("parameters", {})
        chart_type = section.get("chart_type", "line")

        # Enhanced chart generator
        if chart_generator and ENHANCED_CHARTS_AVAILABLE:
            try:
                fig = chart_generator.create_chart(chart_type, chart_data, params, section["title"])
                pdf.savefig(fig)
                plt.close(fig)
                return
            except Exception as e:
                logger.error(f"Enhanced chart failed: {e}")

        # Basic chart rendering
        fig = plt.figure(figsize=(8.5, 5))
        x_field = params.get("x_field", "date")
        y_field = params.get("y_field", "value")
        ideal_range = params.get("ideal_range")

        x_vals = [item.get(x_field) for item in chart_data]
        y_vals = [item.get(y_field) for item in chart_data]

        if chart_type == "line":
            plt.plot(x_vals, y_vals, marker='o')
            if ideal_range and len(ideal_range) == 2:
                plt.axhspan(ideal_range[0], ideal_range[1], alpha=0.2, color='green')
        elif chart_type == "bar":
            plt.bar(x_vals, y_vals)
        elif chart_type == "pie":
            labels = [item.get(params.get("label_field", "label")) for item in chart_data]
            values = [item.get(params.get("value_field", "value")) for item in chart_data]
            plt.pie(values, labels=labels, autopct='%1.1f%%')
            plt.axis('equal')
        elif chart_type == "scatter":
            plt.scatter(x_vals, y_vals)
        elif chart_type == "area":
            plt.fill_between(x_vals, y_vals, alpha=0.4)
            plt.plot(x_vals, y_vals)
        else:
            plt.plot(x_vals, y_vals, marker='o')

        plt.title(section.get("title", "Chart"))
        plt.xlabel(params.get("x_label", x_field.capitalize()))
        plt.ylabel(params.get("y_label", y_field.capitalize()))
        plt.grid(True, linestyle='--', alpha=0.7)
        pdf.savefig(fig)
        plt.close(fig)

    except Exception as e:
        logger.error(f"Chart generation error: {e}")
        fig = plt.figure(figsize=(8.5, 5))
        plt.figtext(0.5, 0.5, f"Error: {str(e)}", ha="center", va="center", fontsize=12)
        pdf.savefig(fig)
        plt.close(fig)

# Main PDF exporter
def export_report_to_pdf(report: Report, output_path: str, template: ReportTemplate):
    """Create a full PDF report with charts."""
    chart_gen = ChartGenerator() if ENHANCED_CHARTS_AVAILABLE else None
    with PdfPages(output_path) as pdf:
        for section in template.sections:
            _add_chart_to_pdf(report, section, pdf, chart_gen)

# CLI entry point
if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python export.py <report_path.json> <output_path.pdf>")
        sys.exit(1)
    
    report_path = sys.argv[1]
    output_path = sys.argv[2]
    
    try:
        report = Report.load(report_path)
        template = ReportTemplate.load("components/reporting/templates/default_template.json")
        export_report_to_pdf(report, output_path, template)
        print(f"Report exported successfully to {output_path}")
    except Exception as e:
        logger.error(f"Export failed: {e}")
        sys.exit(1)
