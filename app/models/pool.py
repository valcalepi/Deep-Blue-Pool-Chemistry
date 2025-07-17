# models/pool.py
"""
Pool parameters and chemical readings models.
"""
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class PoolParameters:
    """Parameters of a swimming pool."""
    pool_type: str  # Type of pool (e.g. "Residential", "Commercial", "Indoor", "Outdoor")
    size_gallons: float  # Size in gallons
    surface_material: Optional[str] = None  # Surface material, if known
    use_type: Optional[str] = None  # Use type (e.g. "Residential", "Commercial", "Public")
    indoor_outdoor: Optional[str] = None  # Whether the pool is indoor or outdoor
    salt_water: bool = False  # Whether the pool is saltwater


class ChemicalReadings:
    """Chemical readings from a pool water test."""
    
    def __init__(self):
        """Initialize with empty readings."""
        self._readings = {}
        
    def add_reading(self, name: str, value: float) -> None:
        """
        Add a reading to the collection.
        
        Args:
            name: Name of the chemical reading
            value: Value of the reading
        """
        self._readings[name.lower()] = value
        
    def get_reading(self, name: str) -> Optional[float]:
        """
        Get a reading by name.
        
        Args:
            name: Name of the chemical reading
            
        Returns:
            float: The reading value, or None if not present
        """
        return self._readings.get(name.lower())
    
    def has_reading(self, name: str) -> bool:
        """
        Check if a reading exists.
        
        Args:
            name: Name of the chemical reading
            
        Returns:
            bool: True if the reading exists, False otherwise
        """
        return name.lower() in self._readings
    
    def get_all_readings(self) -> Dict[str, float]:
        """
        Get all readings.
        
        Returns:
            dict: All readings
        """
        return self._readings.copy()
