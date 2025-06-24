# controllers/pool_controller.py
from typing import Dict, Any
import logging
from models.chemical_calculator import ChemicalCalculator
from models.pool import PoolParameters, ChemicalReadings
from utils.validators import validate_numeric_input
from exceptions import DataValidationError
from config import Config

class PoolController:
    """Controller for pool chemistry operations."""
    
    def __init__(self):
        """Initialize the controller."""
        self.calculator = ChemicalCalculator()
        
    def calculate_chemical_metrics(self, pool_type: str, pool_size: float,
                                 pH: float, chlorine: float, bromine: float,
                                 alkalinity: float, cyanuric_acid: float,
                                 calcium_hardness: float, stabilizer: float,
                                 salt: float) -> Dict[str, Any]:
        """
        Calculate chemical metrics based on pool parameters.
        
        Args:
            pool_type (str): Type of pool
            pool_size (float): Size of pool in gallons
            pH (float): pH level
            chlorine (float): Chlorine level in ppm
            bromine (float): Bromine level in ppm
            alkalinity (float): Alkalinity level in ppm
            cyanuric_acid (float): Cyanuric acid level in ppm
            calcium_hardness (float): Calcium hardness level in ppm
            stabilizer (float): Stabilizer level in ppm
            salt (float): Salt level in ppm
            
        Returns:
            dict: Chemical metrics and recommendations
            
        Raises:
            DataValidationError: If any input validation fails
        """
        try:
            # Create data models
            pool_params = PoolParameters(pool_type=pool_type, size_gallons=pool_size)
            
            # Create chemical readings
            readings = ChemicalReadings()
            readings.add_reading("pH", pH)
            readings.add_reading("chlorine", chlorine)
            readings.add_reading("bromine", bromine)
            readings.add_reading("alkalinity", alkalinity)
            readings.add_reading("cyanuric_acid", cyanuric_acid)
            readings.add_reading("calcium_hardness", calcium_hardness)
            readings.add_reading("stabilizer", stabilizer)
            readings.add_reading("salt", salt)
            
            # Calculate metrics
            return self.calculator.calculate_metrics(pool_params, readings)
            
        except ValueError as e:
            # Convert generic ValueError to DataValidationError
            raise DataValidationError(str(e))
        except Exception as e:
            logging.error(f"Error in chemical metrics calculation: {e}", exc_info=True)
            raise
