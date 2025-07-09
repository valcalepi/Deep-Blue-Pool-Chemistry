# insert_test_results.py
import os
import logging
from datetime import datetime
import csv
from typing import Dict, List, Any, Optional, Tuple

# Configure logging
logger = logging.getLogger(__name__)

# Safe ranges for chemical parameters
SAFE_RANGES = {
    "pH": (7.2, 7.8),
    "Chlorine": (1.0, 3.0),
    "Alkalinity": (80, 120)
}

class ResultsManager:
    """
    Manager for handling pool test results (non-database version).
    """
    
    def __init__(self):
        """
        Initialize the results manager.
        """
        self.logger = logging.getLogger(__name__)
        self.tests = {}
        self.test_results = {}
        self.recommendations = {}
        self.logger.info("ResultsManager initialized")
    
    def insert_test(self, location_name: str) -> Optional[int]:
        """
        Create a new test record in memory.
        
        Args:
            location_name: Name of the pool location
            
        Returns:
            Optional[int]: ID of the inserted test, or None if failed
        """
        try:
            test_id = len(self.tests) + 1
            self.tests[test_id] = {
                "test_date": datetime.now(),
                "location_name": location_name
            }
            return test_id
        except Exception as e:
            self.logger.error(f"Error creating test: {str(e)}")
            return None
    
    def insert_test_result(self, test_id: int, parameter: str, value: float, unit: str) -> bool:
        """
        Store a test result in memory.
        
        Args:
            test_id: ID of the test
            parameter: Chemical parameter name
            value: Reading value
            unit: Unit of measurement
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if test_id not in self.test_results:
                self.test_results[test_id] = []
                
            self.test_results[test_id].append({
                "parameter": parameter,
                "value": value,
                "unit": unit
            })
            return True
        except Exception as e:
            self.logger.error(f"Error storing test result: {str(e)}")
            return False
    
    def insert_recommendation(self, test_id: int, parameter: str, value: float, 
                         recommendation: str) -> bool:
        """
        Store a recommendation in memory.
        
        Args:
            test_id: ID of the test
            parameter: Chemical parameter name
            value: Reading value
            recommendation: Recommendation text
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if test_id not in self.recommendations:
                self.recommendations[test_id] = []
                
            self.recommendations[test_id].append({
                "parameter": parameter,
                "value": value,
                "recommendation": recommendation
            })
            return True
        except Exception as e:
            self.logger.error(f"Error storing recommendation: {str(e)}")
            return False
    
    def export_to_csv(self, test_id: int, filename: str = "test_report.csv") -> bool:
        """
        Export test results and recommendations to CSV.
        
        Args:
            test_id: ID of the test
            filename: Output CSV filename
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Get test results and recommendations for this test
            results = self.test_results.get(test_id, [])
            recommendations = {r["parameter"]: r["recommendation"] for r in self.recommendations.get(test_id, [])}
            
            if not results:
                self.logger.warning(f"No results found for test ID {test_id}")
                return False
            
            # Write to CSV
            with open(filename, mode="w", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(["Parameter", "Value", "Unit", "Recommendation"])
                
                for result in results:
                    writer.writerow([
                        result["parameter"],
                        result["value"],
                        result["unit"],
                        recommendations.get(result["parameter"], "No recommendation")
                    ])
            
            self.logger.info(f"Test report exported to {filename}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error exporting to CSV: {str(e)}")
            return False
    
    def get_recommendation(self, parameter: str, value: float) -> str:
        """
        Get a recommendation based on parameter value.
        
        Args:
            parameter: Chemical parameter name
            value: Reading value
            
        Returns:
            str: Recommendation text
        """
        low, high = SAFE_RANGES.get(parameter, (None, None))
        
        if low is None:
            return "No recommendation available"
            
        if value < low:
            return f"Increase {parameter}"
        elif value > high:
            return f"Decrease {parameter}"
        else:
            return "OK"
