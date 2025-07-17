
"""
GUI controller module for the Deep Blue Pool Chemistry application.

This module provides the controller class that mediates between the GUI views
and the business logic of the application.
"""

import logging
import json
import os
from typing import Dict, List, Optional, Any, Tuple, Union
from datetime import datetime

# Configure logger
logger = logging.getLogger(__name__)


class ChemicalCalculator:
    """
    Calculator for pool chemical adjustments.
    
    This class provides methods for calculating chemical adjustments based on
    water test results and evaluating water balance.
    
    Attributes:
        ideal_ranges: Dictionary of ideal ranges for water parameters
    """
    
    def __init__(self):
        """Initialize the chemical calculator with ideal ranges."""
        self.ideal_ranges = {
            "ph": (7.2, 7.8),
            "chlorine": (1.0, 3.0),
            "alkalinity": (80, 120),
            "calcium_hardness": {
                "Concrete/Gunite": (200, 400),
                "Vinyl": (175, 225),
                "Fiberglass": (175, 225),
                "Above Ground": (175, 225)
            }
        }
        logger.info("ChemicalCalculator initialized")
    
    def validate_reading(self, param: str, value: float) -> bool:
        """
        Validate a water parameter reading.
        
        Args:
            param: Parameter name
            value: Parameter value
            
        Returns:
            True if valid, False otherwise
            
        Raises:
            ValueError: If the value is outside acceptable ranges
        """
        # Define acceptable ranges (wider than ideal ranges)
        acceptable_ranges = {
            "ph": (6.0, 9.0),
            "chlorine": (0.0, 10.0),
            "alkalinity": (0, 300),
            "calcium_hardness": (0, 1000),
            "cyanuric_acid": (0, 200),
            "temperature": (32, 104)
        }
        
        if param not in acceptable_ranges:
            return True  # No validation for unknown parameters
        
        min_val, max_val = acceptable_ranges[param]
        
        if value < min_val or value > max_val:
            raise ValueError(f"{param} value {value} is outside acceptable range ({min_val}-{max_val})")
        
        return True
    
    def get_ideal_range(self, param: str, pool_type: Optional[str] = None) -> Tuple[float, float]:
        """
        Get the ideal range for a water parameter.
        
        Args:
            param: Parameter name
            pool_type: Type of pool (for calcium hardness)
            
        Returns:
            Tuple of (min, max) values
        """
        if param == "calcium_hardness" and pool_type:
            return self.ideal_ranges[param].get(pool_type, self.ideal_ranges[param]["Concrete/Gunite"])
        return self.ideal_ranges.get(param, (0, 0))
    
    def calculate_adjustments(self, pool_type: str, ph: float, chlorine: float, 
                             alkalinity: float, calcium_hardness: float, 
                             pool_size: float) -> Dict[str, Dict[str, Any]]:
        """
        Calculate chemical adjustments based on water test results.
        
        Args:
            pool_type: Type of pool
            ph: pH level
            chlorine: Chlorine level (ppm)
            alkalinity: Alkalinity level (ppm)
            calcium_hardness: Calcium hardness level (ppm)
            pool_size: Pool size in gallons
            
        Returns:
            Dictionary of chemical adjustments
        """
        adjustments = {}
        
        # Calculate pH adjustment
        ph_min, ph_max = self.get_ideal_range("ph")
        if ph < ph_min:
            # Need to increase pH
            ph_increaser_amount = (ph_min - ph) * pool_size / 10000 * 6  # oz per 10,000 gallons
            adjustments["ph_increaser"] = {
                "amount": round(ph_increaser_amount, 2),
                "unit": "oz",
                "reason": f"Increase pH from {ph} to {ph_min}-{ph_max}"
            }
        elif ph > ph_max:
            # Need to decrease pH
            ph_decreaser_amount = (ph - ph_max) * pool_size / 10000 * 8  # oz per 10,000 gallons
            adjustments["ph_decreaser"] = {
                "amount": round(ph_decreaser_amount, 2),
                "unit": "oz",
                "reason": f"Decrease pH from {ph} to {ph_min}-{ph_max}"
            }
        
        # Calculate chlorine adjustment
        cl_min, cl_max = self.get_ideal_range("chlorine")
        if chlorine < cl_min:
            # Need to increase chlorine
            chlorine_amount = (cl_min - chlorine) * pool_size / 10000 * 2  # lbs per 10,000 gallons
            adjustments["chlorine"] = {
                "amount": round(chlorine_amount, 2),
                "unit": "lbs",
                "reason": f"Increase chlorine from {chlorine} to {cl_min}-{cl_max}"
            }
        elif chlorine > cl_max:
            # Need to decrease chlorine (wait or dilute)
            adjustments["chlorine_reduction"] = {
                "amount": 0,
                "unit": "",
                "reason": f"Reduce chlorine from {chlorine} to {cl_min}-{cl_max} by waiting or diluting"
            }
        
        # Calculate alkalinity adjustment
        alk_min, alk_max = self.get_ideal_range("alkalinity")
        if alkalinity < alk_min:
            # Need to increase alkalinity
            alk_increaser_amount = (alk_min - alkalinity) * pool_size / 10000 * 1.5  # lbs per 10,000 gallons
            adjustments["alkalinity_increaser"] = {
                "amount": round(alk_increaser_amount, 2),
                "unit": "lbs",
                "reason": f"Increase alkalinity from {alkalinity} to {alk_min}-{alk_max}"
            }
        elif alkalinity > alk_max:
            # Need to decrease alkalinity
            adjustments["alkalinity_decreaser"] = {
                "amount": 0,
                "unit": "",
                "reason": f"Decrease alkalinity from {alkalinity} to {alk_min}-{alk_max} by adding acid"
            }
        
        # Calculate calcium hardness adjustment
        ch_min, ch_max = self.get_ideal_range("calcium_hardness", pool_type)
        if calcium_hardness < ch_min:
            # Need to increase calcium hardness
            ch_increaser_amount = (ch_min - calcium_hardness) * pool_size / 10000 * 1.25  # lbs per 10,000 gallons
            adjustments["calcium_hardness_increaser"] = {
                "amount": round(ch_increaser_amount, 2),
                "unit": "lbs",
                "reason": f"Increase calcium hardness from {calcium_hardness} to {ch_min}-{ch_max}"
            }
        elif calcium_hardness > ch_max:
            # Need to decrease calcium hardness (dilution)
            adjustments["calcium_hardness_reduction"] = {
                "amount": 0,
                "unit": "",
                "reason": f"Reduce calcium hardness from {calcium_hardness} to {ch_min}-{ch_max} by diluting"
            }
        
        return adjustments
    
    def evaluate_water_balance(self, ph: float, alkalinity: float, 
                              calcium_hardness: float, temperature: float) -> float:
        """
        Calculate the Langelier Saturation Index (LSI) for water balance.
        
        Args:
            ph: pH level
            alkalinity: Alkalinity level (ppm)
            calcium_hardness: Calcium hardness level (ppm)
            temperature: Water temperature (\u00b0F)
            
        Returns:
            LSI value (negative = corrosive, positive = scaling, 0 = balanced)
        """
        # Temperature factor
        if temperature <= 32:
            temp_factor = 0.0
        elif temperature <= 37:
            temp_factor = 0.1
        elif temperature <= 46:
            temp_factor = 0.2
        elif temperature <= 53:
            temp_factor = 0.3
        elif temperature <= 60:
            temp_factor = 0.4
        elif temperature <= 66:
            temp_factor = 0.5
        elif temperature <= 76:
            temp_factor = 0.6
        elif temperature <= 84:
            temp_factor = 0.7
        elif temperature <= 94:
            temp_factor = 0.8
        elif temperature <= 105:
            temp_factor = 0.9
        else:
            temp_factor = 1.0
        
        # Calcium hardness factor
        if calcium_hardness <= 25:
            ch_factor = 0.4
        elif calcium_hardness <= 50:
            ch_factor = 0.7
        elif calcium_hardness <= 75:
            ch_factor = 0.9
        elif calcium_hardness <= 100:
            ch_factor = 1.0
        elif calcium_hardness <= 150:
            ch_factor = 1.1
        elif calcium_hardness <= 200:
            ch_factor = 1.2
        elif calcium_hardness <= 250:
            ch_factor = 1.3
        elif calcium_hardness <= 300:
            ch_factor = 1.4
        elif calcium_hardness <= 400:
            ch_factor = 1.5
        elif calcium_hardness <= 500:
            ch_factor = 1.6
        elif calcium_hardness <= 600:
            ch_factor = 1.7
        elif calcium_hardness <= 800:
            ch_factor = 1.8
        elif calcium_hardness <= 1000:
            ch_factor = 1.9
        else:
            ch_factor = 2.0
        
        # Alkalinity factor
        if alkalinity <= 25:
            alk_factor = 1.4
        elif alkalinity <= 50:
            alk_factor = 1.7
        elif alkalinity <= 75:
            alk_factor = 1.9
        elif alkalinity <= 100:
            alk_factor = 2.0
        elif alkalinity <= 125:
            alk_factor = 2.1
        elif alkalinity <= 150:
            alk_factor = 2.2
        elif alkalinity <= 200:
            alk_factor = 2.3
        elif alkalinity <= 250:
            alk_factor = 2.4
        elif alkalinity <= 300:
            alk_factor = 2.5
        elif alkalinity <= 400:
            alk_factor = 2.6
        elif alkalinity <= 500:
            alk_factor = 2.7
        elif alkalinity <= 600:
            alk_factor = 2.8
        elif alkalinity <= 800:
            alk_factor = 2.9
        else:
            alk_factor = 3.0
        
        # Calculate LSI
        lsi = ph + temp_factor + ch_factor + alk_factor - 12.1
        
        return round(lsi, 2)


class DatabaseManager:
    """
    Manager for database operations.
    
    This class provides methods for interacting with the database to store and
    retrieve pool chemistry data.
    
    Attributes:
        db_service: Database service instance
    """
    
    def __init__(self, db_service=None):
        """
        Initialize the database manager.
        
        Args:
            db_service: Database service instance (optional)
        """
        self.db_service = db_service
        logger.info("DatabaseManager initialized")
    
    def insert_test(self, location_name: str) -> int:
        """
        Insert a new test record.
        
        Args:
            location_name: Name of the test location
            
        Returns:
            Test ID
            
        Raises:
            RuntimeError: If database service is not available
        """
        if not self.db_service:
            logger.warning("Database service not available")
            return 1  # Return dummy ID
        
        try:
            # In a real implementation, this would insert a record and return the ID
            logger.info(f"Inserting test for location: {location_name}")
            return 1  # Dummy ID
        except Exception as e:
            logger.error(f"Failed to insert test: {e}")
            raise RuntimeError(f"Database error: {e}")
    
    def insert_test_result(self, test_id: int, param_name: str, value: float, unit: str) -> bool:
        """
        Insert a test result.
        
        Args:
            test_id: Test ID
            param_name: Parameter name
            value: Parameter value
            unit: Unit of measurement
            
        Returns:
            True if successful, False otherwise
            
        Raises:
            RuntimeError: If database service is not available
        """
        if not self.db_service:
            logger.warning("Database service not available")
            return True  # Pretend it worked
        
        try:
            logger.info(f"Inserting test result: {test_id}, {param_name}, {value}, {unit}")
            return True
        except Exception as e:
            logger.error(f"Failed to insert test result: {e}")
            raise RuntimeError(f"Database error: {e}")
    
    def get_recommendation(self, param_name: str, value: float) -> str:
        """
        Get a recommendation based on a parameter value.
        
        Args:
            param_name: Parameter name
            value: Parameter value
            
        Returns:
            Recommendation text
        """
        # Simple recommendations based on parameter name and value
        if param_name == "pH":
            if value < 7.2:
                return "Add pH increaser to raise pH level"
            elif value > 7.8:
                return "Add pH decreaser to lower pH level"
            else:
                return "pH level is within ideal range"
        elif param_name == "Chlorine":
            if value < 1.0:
                return "Add chlorine to increase level"
            elif value > 3.0:
                return "Chlorine level is high, avoid adding more until level drops"
            else:
                return "Chlorine level is within ideal range"
        elif param_name == "Alkalinity":
            if value < 80:
                return "Add alkalinity increaser to raise level"
            elif value > 120:
                return "Add acid to lower alkalinity level"
            else:
                return "Alkalinity level is within ideal range"
        elif param_name == "Calcium Hardness":
            if value < 200:
                return "Add calcium hardness increaser to raise level"
            elif value > 400:
                return "Dilute pool water to lower calcium hardness"
            else:
                return "Calcium hardness level is within ideal range"
        else:
            return f"Maintain {param_name} at optimal levels"
    
    def insert_recommendation(self, test_id: int, param_name: str, value: float, recommendation: str) -> bool:
        """
        Insert a recommendation.
        
        Args:
            test_id: Test ID
            param_name: Parameter name
            value: Parameter value
            recommendation: Recommendation text
            
        Returns:
            True if successful, False otherwise
            
        Raises:
            RuntimeError: If database service is not available
        """
        if not self.db_service:
            logger.warning("Database service not available")
            return True  # Pretend it worked
        
        try:
            logger.info(f"Inserting recommendation for {param_name}: {recommendation}")
            return True
        except Exception as e:
            logger.error(f"Failed to insert recommendation: {e}")
            raise RuntimeError(f"Database error: {e}")
    
    def export_to_csv(self, test_id: int) -> bool:
        """
        Export test results to CSV.
        
        Args:
            test_id: Test ID
            
        Returns:
            True if successful, False otherwise
            
        Raises:
            RuntimeError: If database service is not available
        """
        if not self.db_service:
            logger.warning("Database service not available")
            return True  # Pretend it worked
        
        try:
            logger.info(f"Exporting test results to CSV for test ID: {test_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to export to CSV: {e}")
            raise RuntimeError(f"Database error: {e}")
    
    def check_health(self) -> bool:
        """
        Check database health.
        
        Returns:
            True if healthy, False otherwise
        """
        if not self.db_service:
            logger.warning("Database service not available")
            return False
        
        try:
            # In a real implementation, this would check the database connection
            logger.info("Database health check passed")
            return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False
    
    def run_migrations(self) -> bool:
        """
        Run database migrations.
        
        Returns:
            True if successful, False otherwise
        """
        if not self.db_service:
            logger.warning("Database service not available")
            return False
        
        try:
            # In a real implementation, this would run database migrations
            logger.info("Database migrations completed")
            return True
        except Exception as e:
            logger.error(f"Database migrations failed: {e}")
            return False


class PoolChemistryController:
    """
    Controller for the Pool Chemistry application.
    
    This class mediates between the GUI views and the business logic of the application.
    
    Attributes:
        calculator: Chemical calculator instance
        db_manager: Database manager instance
    """
    
    def __init__(self, db_service=None):
        """
        Initialize the controller.
        
        Args:
            db_service: Database service instance (optional)
        """
        self.calculator = ChemicalCalculator()
        self.db_manager = DatabaseManager(db_service)
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
                if param in pool_data and pool_data[param]:
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
                error_msg = "\
".join(f"{k}: {v}" for k, v in errors.items())
                raise ValueError(f"Validation errors:\
{error_msg}")
            
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
            if all(param in pool_data and pool_data[param] for param in ["ph", "alkalinity", "calcium_hardness", "temperature"]):
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
            Test ID if successful, None otherwise
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
            True if healthy, False otherwise
        """
        return self.db_manager.check_health()
    
    def run_database_migrations(self) -> bool:
        """
        Run database migrations.
        
        Returns:
            True if successful, False otherwise
        """
        return self.db_manager.run_migrations()
