# pool_manager.py
"""
Module for managing pool operations and recommendations.
"""
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from models.pool import PoolParameters, ChemicalReadings
from models.water_tester import WaterTester
from pool_calculations import PoolCalculations
from constants import Constants

class PoolManager:
    """
    Manages pool operations, testing, and recommendations.
    """
    def __init__(self, water_tester: Optional[WaterTester] = None):
        self.logger = logging.getLogger(__name__)
        self.water_tester = water_tester if water_tester else WaterTester()
        self.pool_calculations = PoolCalculations()
        self.current_pool = None
        self.current_readings = ChemicalReadings()
        
    def set_pool_parameters(self, pool_params: PoolParameters) -> None:
        """
        Set the current pool parameters.
        
        Args:
            pool_params: Pool parameters object
        """
        self.current_pool = pool_params
        self.water_tester.set_pool_volume(pool_params.size_gallons)
        self.logger.info(f"Pool parameters set: {pool_params.size_gallons} gallons, {pool_params.pool_type} type")
        
    def add_chemical_reading(self, name: str, value: float) -> None:
        """
        Add a chemical reading.
        
        Args:
            name: Chemical name
            value: Reading value
        """
        self.current_readings.add_reading(name, value)
        self.logger.debug(f"Added chemical reading: {name}={value}")
        
    def add_readings_from_dict(self, readings: Dict[str, float]) -> None:
        """
        Add multiple chemical readings from a dictionary.
        
        Args:
            readings: Dictionary of chemical readings
        """
        for name, value in readings.items():
            self.add_chemical_reading(name, value)
            
    def get_all_recommendations(self) -> Dict[str, Any]:
        """
        Get recommendations for all chemicals based on current readings.
        
        Returns:
            Dictionary with recommendations for each chemical
        """
        if not self.current_pool:
            self.logger.warning("No pool parameters set. Cannot generate recommendations.")
            return {"error": "No pool parameters set"}
            
        recommendations = {}
        readings = self.current_readings.get_all_readings()
        
        # Calculate pH adjustment if we have a pH reading
        if "ph" in readings:
            recommendations["ph"] = self.pool_calculations.calculate_ph_adjustment(
                readings["ph"], 
                self.current_pool.size_gallons
            )
            
        # Calculate chlorine adjustment if we have a chlorine reading
        if "chlorine" in readings or "free_chlorine" in readings:
            chlorine = readings.get("free_chlorine", readings.get("chlorine", 0))
            recommendations["chlorine"] = self.pool_calculations.calculate_chlorine_adjustment(
                chlorine,
                self.current_pool.size_gallons
            )
            
        # Calculate alkalinity adjustment if we have an alkalinity reading
        if "alkalinity" in readings or "total_alkalinity" in readings:
            alkalinity = readings.get("total_alkalinity", readings.get("alkalinity", 0))
            recommendations["alkalinity"] = self.pool_calculations.calculate_alkalinity_adjustment(
                alkalinity,
                self.current_pool.size_gallons
            )
            
        # Calculate water balance if we have all necessary readings
        required_keys = ["ph", "temperature"]
        alkalinity_key = next((k for k in ["total_alkalinity", "alkalinity"] if k in readings), None)
        calcium_key = next((k for k in ["calcium_hardness", "calcium"] if k in readings), None)
        
        if all(k in readings for k in required_keys) and alkalinity_key and calcium_key:
            recommendations["water_balance"] = self.pool_calculations.calculate_water_balance(
                ph=readings["ph"],
                alkalinity=readings[alkalinity_key],
                calcium_hardness=readings[calcium_key],
                temperature=readings["temperature"],
                tds=readings.get("tds", None)
            )
        
        return recommendations
        
    def manage_pool(
        self,
        pool_type: str,
        pool_size: float,
        ph: float,
        chlorine: float,
        alkalinity: float,
        calcium_hardness: float,
        temperature: float = 78.0,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Convenience method to set pool parameters, add readings, and get recommendations in one call.
        
        Args:
            pool_type: Type of pool
            pool_size: Size in gallons
            ph: Current pH level
            chlorine: Current chlorine level
            alkalinity: Current alkalinity level
            calcium_hardness: Current calcium hardness level
            temperature: Current water temperature
            **kwargs: Additional chemical readings
            
        Returns:
            Dictionary with recommendations for each chemical
        """
        # Set pool parameters
        self.set_pool_parameters(PoolParameters(
            pool_type=pool_type,
            size_gallons=pool_size,
            surface_material=kwargs.get("surface_material", None),
            use_type=kwargs.get("use_type", "Residential"),
            indoor_outdoor=kwargs.get("indoor_outdoor", "Outdoor"),
            salt_water=kwargs.get("salt_water", False)
        ))
        
        # Add readings
        self.add_chemical_reading("ph", ph)
        self.add_chemical_reading("chlorine", chlorine)
        self.add_chemical_reading("alkalinity", alkalinity)
        self.add_chemical_reading("calcium_hardness", calcium_hardness)
        self.add_chemical_reading("temperature", temperature)
        
        # Add any additional readings
        for name, value in kwargs.items():
            if name not in ["surface_material", "use_type", "indoor_outdoor", "salt_water"]:
                self.add_chemical_reading(name, value)
                
        # Get recommendations
        return self.get_all_recommendations()
        
    def save_to_file(self, filename: str) -> bool:
        """
        Save current pool parameters and readings to a JSON file.
        
        Args:
            filename: Path to save the file
            
        Returns:
            bool: True if saved successfully, False otherwise
        """
        try:
            if not self.current_pool:
                self.logger.warning("No pool parameters to save")
                return False
                
            data = {
                "pool_parameters": {
                    "pool_type": self.current_pool.pool_type,
                    "size_gallons": self.current_pool.size_gallons,
                    "surface_material": self.current_pool.surface_material,
                    "use_type": self.current_pool.use_type,
                    "indoor_outdoor": self.current_pool.indoor_outdoor,
                    "salt_water": self.current_pool.salt_water
                },
                "chemical_readings": self.current_readings.get_all_readings()
            }
            
            with open(filename, 'w') as f:
                json.dump(data, f, indent=4)
                
            self.logger.info(f"Pool data saved to {filename}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving pool data: {str(e)}")
            return False
            
    def load_from_file(self, filename: str) -> bool:
        """
        Load pool parameters and readings from a JSON file.
        
        Args:
            filename: Path to the file to load
            
        Returns:
            bool: True if loaded successfully, False otherwise
        """
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
                
            pool_params = data.get("pool_parameters", {})
            self.current_pool = PoolParameters(
                pool_type=pool_params.get("pool_type", "Unknown"),
                size_gallons=pool_params.get("size_gallons", 0),
                surface_material=pool_params.get("surface_material"),
                use_type=pool_params.get("use_type"),
                indoor_outdoor=pool_params.get("indoor_outdoor"),
                salt_water=pool_params.get("salt_water", False)
            )
            
            self.water_tester.set_pool_volume(self.current_pool.size_gallons)
            
            self.current_readings = ChemicalReadings()
            for name, value in data.get("chemical_readings", {}).items():
                self.current_readings.add_reading(name, value)
                
            self.logger.info(f"Pool data loaded from {filename}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error loading pool data: {str(e)}")
            return False
