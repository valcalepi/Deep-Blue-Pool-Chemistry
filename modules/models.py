"""
Reporting Models for Pool Chemistry System

Includes:
- ReportTemplate: Defines structure and chart options for export
- Report: Stores data and metadata for pool readings
"""

import json
import uuid
from typing import List, Dict, Any, Optional


class ReportTemplate:
    """
    Report template model for defining report structure and appearance.
    """

    BASIC_CHART_TYPES = ["line", "bar", "pie", "scatter"]
    ENHANCED_CHART_TYPES = [
        "area", "stacked_bar", "histogram", "box_plot",
        "heatmap", "radar", "bubble", "multi_line"
    ]

    def __init__(
        self,
        name: str,
        description: str,
        template_type: str,
        sections: List[Dict[str, Any]],
        chart_types: Optional[List[str]] = None,
        parameters: Optional[Dict[str, Any]] = None,
        template_id: Optional[str] = None
    ):
        self.name = name
        self.description = description
        self.template_type = template_type
        self.sections = sections
        self.chart_types = chart_types or self.BASIC_CHART_TYPES
        self.parameters = parameters or {}
        self.template_id = template_id or str(uuid.uuid4())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "template_id": self.template_id,
            "name": self.name,
            "description": self.description,
            "template_type": self.template_type,
            "sections": self.sections,
            "chart_types": self.chart_types,
            "parameters": self.parameters,
        }

    def save(self, filepath: str):
        with open(filepath, "w") as f:
            json.dump(self.to_dict(), f, indent=4)

    @classmethod
    def load(cls, filepath: str):
        with open(filepath, "r") as f:
            data = json.load(f)
        return cls(
            name=data["name"],
            description=data["description"],
            template_type=data["template_type"],
            sections=data["sections"],
            chart_types=data.get("chart_types"),
            parameters=data.get("parameters"),
            template_id=data.get("template_id")
        )


class Report:
    """
    Report data model for chemistry readings and metadata.
    """

    def __init__(
        self,
        title: str,
        date: str,
        customer_name: str,
        data: Dict[str, List[Dict[str, Any]]],
        notes: Optional[str] = "",
        report_id: Optional[str] = None
    ):
        self.title = title
        self.date = date
        self.customer_name = customer_name
        self.data = data
        self.notes = notes
        self.report_id = report_id or str(uuid.uuid4())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "report_id": self.report_id,
            "title": self.title,
            "date": self.date,
            "customer_name": self.customer_name,
            "data": self.data,
            "notes": self.notes
        }

    def save(self, filepath: str):
        with open(filepath, "w") as f:
            json.dump(self.to_dict(), f, indent=4)

    @classmethod
    def load(cls, filepath: str):
        with open(filepath, "r") as f:
            data = json.load(f)
        return cls(
            title=data["title"],
            date=data["date"],
            customer_name=data["customer_name"],
            data=data["data"],
            notes=data.get("notes", ""),
            report_id=data.get("report_id")
        )
