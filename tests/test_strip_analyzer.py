"""
Test strip analyzer for Deep Blue Pool Chemistry Management System.

This module provides functionality for analyzing pool test strips,
interpreting the results, and providing recommendations for chemical adjustments.
"""

import logging
import json
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from enum import Enum

from utils.exceptions import AnalysisError


class ChemicalParameter(str, Enum):
    """Enumeration of chemical parameters measurable with test strips."""
    
    FREE_CHLORINE = "free_chlorine"
    TOTAL_CHLORINE = "total_chlorine"
    PH = "ph"
    TOTAL_ALKALINITY = "total_alkalinity"
    CALCIUM_HARDNESS = "calcium_hardness"
    CYANURIC_ACID = "cyanuric_acid"
    TOTAL_BROMINE = "total_bromine"
    SALT = "salt"


class TestStripAnalyzer:
    """Analyzer for pool chemical test strips."""
    
    # Reference ranges for each parameter (ideal ranges)
    IDEAL_RANGES = {
        ChemicalParameter.FREE_CHLORINE: (1.0, 3.0),    # ppm
        ChemicalParameter.TOTAL_CHLORINE: (1.0, 3.0),   # ppm
        ChemicalParameter.PH: (7.2, 7.8),               # pH scale
        ChemicalParameter.TOTAL_ALKALINITY: (80, 120),  # ppm
        ChemicalParameter.CALCIUM_HARDNESS: (200, 400), # ppm
        ChemicalParameter.CYANURIC_ACID: (30, 50),      # ppm
        ChemicalParameter.TOTAL_BROMINE: (2.0, 4.0),    # ppm
        ChemicalParameter.SALT: (2700, 3400)            # ppm
    }
    
    def __init__(self, color_thresholds: Optional[Dict] = None):
        """
        Initialize test strip analyzer with optional custom color thresholds.
        
        Args:
            color_thresholds: Optional dictionary with custom color thresholds for analysis
        """
        self.logger = logging.getLogger(__name__)
        self.color_thresholds = color_thresholds or {}
        
    def analyze_image(self, image_path: str) -> Dict[str, Any]:
        """
        Analyze an image of a test strip and extract chemical readings.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Dictionary with chemical parameter readings
            
        Raises:
            AnalysisError: If the image cannot be analyzed
        """
        try:
            self.logger.info(f"Analyzing test strip image: {image_path}")
            
            # In a real implementation, this would use image processing and machine learning
            # to analyze the test strip colors and determine chemical levels
            
            # This is a placeholder implementation
            self.logger.warning("Using placeholder image analysis - not actual results")
            
            # Mock analysis results
            results = {
                ChemicalParameter.FREE_CHLORINE: 2.0,
                ChemicalParameter.PH: 7.4,
                ChemicalParameter.TOTAL_ALKALINITY: 90,
                ChemicalParameter.CALCIUM_HARDNESS: 250,
                ChemicalParameter.CYANURIC_ACID: 40
            }
            
            self.logger.info("Test strip image analysis completed")
            return self._format_results(results)
            
        except Exception as e:
            self.logger.error(f"Error analyzing test strip image: {e}")
            raise AnalysisError(f"Failed to analyze test strip image: {e}")
            
    def analyze_manual_readings(self, readings: Dict[str, float]) -> Dict[str, Any]:
        """
        Analyze manually entered chemical readings.
        
        Args:
            readings: Dictionary with chemical parameter readings
            
        Returns:
            Dictionary with analysis results including status and recommendations
            
        Raises:
            AnalysisError: If the readings cannot be analyzed
        """
        try:
            self.logger.info("Analyzing manual chemical readings")
            
            # Validate the readings
            validated_readings = {}
            for param_name, value in readings.items():
                try:
                    param = ChemicalParameter(param_name)
                    validated_readings[param] = float(value)
                except (ValueError, TypeError) as e:
                    self.logger.warning(f"Invalid parameter or value: {param_name}={value}")
            
            return self._format_results(validated_readings)
            
        except Exception as e:
            self.logger.error(f"Error analyzing manual readings: {e}")
            raise AnalysisError(f"Failed to analyze manual readings: {e}")
    
    def _format_results(self, readings: Dict[ChemicalParameter, float]) -> Dict[str, Any]:
        """
        Format the analysis results with status indicators and recommendations.
        
        Args:
            readings: Dictionary with chemical parameter readings
            
        Returns:
            Dictionary with formatted results
        """
        results = {
            "timestamp": datetime.now().isoformat(),
            "readings": {},
            "status": "normal",
            "recommendations": []
        }
        
        # Process each reading
        for param, value in readings.items():
            status = self._get_parameter_status(param, value)
            
            results["readings"][param] = {
                "value": value,
                "unit": self._get_parameter_unit(param),
                "status": status,
                "ideal_range": self.IDEAL_RANGES.get(param, (None, None))
            }
            
            # If any parameter is not ideal, update overall status
            if status != "ideal":
                results["status"] = "needs_adjustment"
                
            # Generate recommendation if needed
            recommendation = self._get_recommendation(param, value, status)
            if recommendation:
                results["recommendations"].append(recommendation)
                
        return results
    
    def _get_parameter_status(self, param: ChemicalParameter, value: float) -> str:
        """
        Determine the status of a parameter value.
        
        Args:
            param: Chemical parameter
            value: Measured value
            
        Returns:
            Status string: "low", "ideal", "high"
        """
        if param not in self.IDEAL_RANGES:
            return "unknown"
            
        low_threshold, high_threshold = self.IDEAL_RANGES[param]
        
        if value < low_threshold:
            return "low"
        elif value > high_threshold:
            return "high"
        else:
            return "ideal"
    
    def _get_parameter_unit(self, param: ChemicalParameter) -> str:
        """
        Get the unit of measurement for a parameter.
        
        Args:
            param: Chemical parameter
            
        Returns:
            Unit string
        """
        if param == ChemicalParameter.PH:
            return "pH"
        else:
            return "ppm"
            
    def _get_recommendation(self, param: ChemicalParameter, value: float, status: str) -> Optional[Dict[str, str]]:
        """
        Generate a recommendation based on parameter status.
        
        Args:
            param: Chemical parameter
            value: Measured value
            status: Parameter status
            
        Returns:
            Recommendation dictionary or None if no recommendation
        """
        if status == "ideal":
            return None
            
        ideal_low, ideal_high = self.IDEAL_RANGES.get(param, (None, None))
        
        if status == "low":
            if param == ChemicalParameter.FREE_CHLORINE:
                return {
                    "parameter": str(param),
                    "action": "increase",
                    "message": f"Add chlorine to bring level from {value} ppm to {ideal_low}-{ideal_high} ppm"
                }
            elif param == ChemicalParameter.PH:
                return {
                    "parameter": str(param),
                    "action": "increase",
                    "message": f"Add pH increaser to bring pH from {value} to {ideal_low}-{ideal_high}"
                }
            elif param == ChemicalParameter.TOTAL_ALKALINITY:
                return {
                    "parameter": str(param),
                    "action": "increase",
                    "message": f"Add alkalinity increaser to bring level from {value} ppm to {ideal_low}-{ideal_high} ppm"
                }
            elif param == ChemicalParameter.CALCIUM_HARDNESS:
                return {
                    "parameter": str(param),
                    "action": "increase",
                    "message": f"Add calcium chloride to bring hardness from {value} ppm to {ideal_low}-{ideal_high} ppm"
                }
            elif param == ChemicalParameter.CYANURIC_ACID:
                return {
                    "parameter": str(param),
                    "action": "increase",
                    "message": f"Add cyanuric acid to bring level from {value} ppm to {ideal_low}-{ideal_high} ppm"
                }
        elif status == "high":
            if param == ChemicalParameter.FREE_CHLORINE:
                return {
                    "parameter": str(param),
                    "action": "decrease",
                    "message": f"Allow chlorine to dissipate or use chlorine neutralizer to bring level from {value} ppm down to {ideal_low}-{ideal_high} ppm"
                }
            elif param == ChemicalParameter.PH:
                return {
                    "parameter": str(param),
                    "action": "decrease",
                    "message": f"Add pH decreaser to bring pH from {value} down to {ideal_low}-{ideal_high}"
                }
            elif param == ChemicalParameter.TOTAL_ALKALINITY:
                return {
                    "parameter": str(param),
                    "action": "decrease",
                    "message": f"Add pH decreaser to bring alkalinity from {value} ppm down to {ideal_low}-{ideal_high} ppm"
                }
            elif param == ChemicalParameter.CALCIUM_HARDNESS:
                return {
                    "parameter": str(param),
                    "action": "decrease",
                    "message": f"Partially drain and refill pool to bring hardness from {value} ppm down to {ideal_low}-{ideal_high} ppm"
                }
            elif param == ChemicalParameter.CYANURIC_ACID:
                return {
                    "parameter": str(param),
                    "action": "decrease",
                    "message": f"Partially drain and refill pool to bring cyanuric acid from {value} ppm down to {ideal_low}-{ideal_high} ppm"
                }
                
        # Generic recommendation for other parameters
        return {
            "parameter": str(param),
            "action": status,
            "message": f"Adjust {param.value} - current value {value} is {status}"
        }
