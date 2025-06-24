# models/pool.py
from dataclasses import dataclass
from typing import Dict, Optional, List, Tuple

@dataclass
class PoolParameters:
    """Data model for pool parameters."""
    pool_type: str
    size_gallons: float
    surface_type: str = "plaster"
    
    def __post_init__(self):
        """Validate attributes after initialization."""
        if not self.pool_type:
            raise ValueError("Pool type cannot be empty")
        if self.size_gallons <= 0:
            raise ValueError("Pool size must be positive")

@dataclass
class ChemicalReading:
    """Data model for a single chemical reading."""
    chemical_name: str
    value: float
    timestamp: Optional[float] = None
    
    def __post_init__(self):
        """Validate attributes after initialization."""
        if self.value < 0:
            raise ValueError(f"Chemical reading cannot be negative: {self.chemical_name}")
            
class ChemicalReadings:
    """Collection of chemical readings."""
    
    def __init__(self):
        self.readings: Dict[str, float] = {}
        self.history: Dict[str, List[Tuple[float, float]]] = {}
        
    def add_reading(self, chemical: str, value: float, timestamp: Optional[float] = None):
        """
        Add a new chemical reading.
        
        Args:
            chemical (str): Chemical name
            value (float): Reading value
            timestamp (float, optional): Reading timestamp
        """
        if chemical not in self.history:
            self.history[chemical] = []
            
        self.readings[chemical] = value
        if timestamp:
            self.history[chemical].append((timestamp, value))
            
    def get_reading(self, chemical: str) -> Optional[float]:
        """Get the most recent reading for a chemical."""
        return self.readings.get(chemical)
