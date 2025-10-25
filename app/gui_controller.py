# app/gui_controller.py
import logging
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Any, Optional

from models.chemical_calculator import ChemicalCalculator
from database.insert_test_results import DatabaseManager

# Configure logging
logger = logging.getLogger(__name__)

class PoolChemistryController:
    """
    Controller class to mediate between GUI and business logic.
    """
    
    def __init__(self):
        """Initialize the controller with required components."""
        self.calculator = ChemicalCalculator()
        self.db_manager = DatabaseManager()
        logger.info("PoolChemistryController initialized")
    
    def validate_pool_data(self, pool_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Validate pool data from the GUI.
        
        Args:
            pool_data: Dictionary of pool data from GUI
            
        Returns:
            Dictionary of validation errors, empty if no errors
        """
        errors = {}
        
        # Validate required fields
        if not pool_data.get("pool_type"):
            errors["pool_type"] = "Pool type is required"
        
        # Validate pool size
        try:
            pool_size = float(pool_data.get("pool_size", 0))
            if pool_size <= 0:
                errors["pool_size"] = "Pool size must be greater than zero"
        except (ValueError, TypeError):
            errors["pool_size"] = "Pool size must be a numeric value"
        
        # Validate chemical readings
        for param in ["ph", "chlorine", "alkalinity", "calcium_hardness"]:
            try:
                if param in pool_data:
                    value = float(pool_data[param])
                    try:
                        self.calculator.validate_reading(param, value)
                    except ValueError as e:
                        errors[param] = str(e)
            except (ValueError, TypeError):
                errors[param] = f"{param} must be a numeric value"
        
        return errors
    
    def calculate_chemicals(self, pool_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate chemical adjustments based on pool data.
        
        Args:
            pool_data: Dictionary of pool data from GUI
            
        Returns:
            Dictionary with chemical adjustments and recommendations
            
        Raises:
            ValueError: If validation fails
        """
        try:
            # Validate pool data
            errors = self.validate_pool_data(pool_data)
            if errors:
                error_msg = "\n".join(f"{k}: {v}" for k, v in errors.items())
                raise ValueError(f"Validation errors:\n{error_msg}")
            
            # Extract data
            pool_type = pool_data["pool_type"]
            pool_size = float(pool_data["pool_size"])
            ph = float(pool_data.get("ph", 0))
            chlorine = float(pool_data.get("chlorine", 0))
            alkalinity = float(pool_data.get("alkalinity", 0))
            calcium_hardness = float(pool_data.get("calcium_hardness", 0))
            
            # Calculate adjustments
            adjustments = self.calculator.calculate_adjustments(
                pool_type, ph, chlorine, alkalinity, calcium_hardness, pool_size
            )
            
            # Calculate water balance if all required parameters are present
            water_balance = None
            if all(param in pool_data and pool_data[param] for param in ["ph", "alkalinity", "calcium_hardness"]):
                water_balance = self.calculator.evaluate_water_balance(
                    ph, alkalinity, calcium_hardness, 
                    float(pool_data.get("temperature", 78.0))
                )
            
            # Prepare result
            result = {
                "adjustments": adjustments,
                "water_balance": water_balance,
                "ideal_ranges": {
                    "ph": self.calculator.get_ideal_range("ph"),
                    "chlorine": self.calculator.get_ideal_range("chlorine"),
                    "alkalinity": self.calculator.get_ideal_range("alkalinity"),
                    "calcium_hardness": self.calculator.get_ideal_range("calcium_hardness", pool_type)
                }
            }
            
            logger.info(f"Calculated chemicals for {pool_type} pool")
            return result
            
        except Exception as e:
            logger.error(f"Error calculating chemicals: {str(e)}")
            raise
    
    def save_test_results(self, pool_data: Dict[str, Any]) -> Optional[int]:
        """
        Save test results to the database.
        
        Args:
            pool_data: Dictionary of pool data from GUI
            
        Returns:
            Optional[int]: Test ID if successful, None otherwise
        """
        try:
            # Insert test
            location_name = pool_data.get("location_name", "Unknown")
            test_id = self.db_manager.insert_test(location_name)
            
            if not test_id:
                logger.error("Failed to insert test")
                return None
            
            # Insert test results
            parameters = {
                "ph": "pH",
                "chlorine": "Chlorine",
                "alkalinity": "Alkalinity",
                "calcium_hardness": "Calcium Hardness",
                "cyanuric_acid": "Cyanuric Acid",
                "salt": "Salt"
            }
            
            for param_key, param_name in parameters.items():
                if param_key in pool_data and pool_data[param_key]:
                    try:
                        value = float(pool_data[param_key])
                        unit = "ppm" if param_key != "ph" else ""
                        
                        # Insert test result
                        self.db_manager.insert_test_result(test_id, param_name, value, unit)
                        
                        # Generate and insert recommendation
                        recommendation = self.db_manager.get_recommendation(param_name, value)
                        self.db_manager.insert_recommendation(test_id, param_name, value, recommendation)
                        
                    except (ValueError, TypeError) as e:
                        logger.warning(f"Skipping invalid {param_key} value: {str(e)}")
            
            # Export to CSV
            self.db_manager.export_to_csv(test_id)
            
            logger.info(f"Test results saved with ID {test_id}")
            return test_id
            
        except Exception as e:
            logger.error(f"Error saving test results: {str(e)}")
            return None
    
    def check_database_health(self) -> bool:
        """
        Check if the database connection is healthy.
        
        Returns:
            bool: True if healthy, False otherwise
        """
        return self.db_manager.check_health()
    
    def run_database_migrations(self) -> bool:
        """
        Run database migrations.
        
        Returns:
            bool: True if successful, False otherwise
        """
        return self.db_manager.run_migrations()
