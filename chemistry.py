# chemistry.py
import logging
import math
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import json
import os

logger = logging.getLogger(__name__)

class ChemicalHistory:
    """Class for managing historical chemical data"""
    
    def __init__(self, storage_file: str = "chemical_history.json"):
        """Initialize chemical history manager"""
        self.storage_file = storage_file
        self.history: Dict[str, List[Tuple[datetime, float]]] = {}
        self.load_history()
        
    def add_reading(self, chemical: str, value: float, timestamp: Optional[datetime] = None):
        """
        Add a chemical reading to history
        
        Args:
            chemical: Chemical parameter name
            value: Reading value
            timestamp: Reading timestamp (defaults to current time)
        """
        if timestamp is None:
            timestamp = datetime.now()
            
        if chemical not in self.history:
            self.history[chemical] = []
            
        # Add the new reading as a tuple of (timestamp, value)
        self.history[chemical].append((timestamp, value))
        
        # Keep history size reasonable (e.g., last 100 readings)
        if len(self.history[chemical]) > 100:
            self.history[chemical] = self.history[chemical][-100:]
            
        # Save to file
        self.save_history()
        
    def get_readings(self, chemical: str, days: int = 30) -> List[Tuple[datetime, float]]:
        """
        Get historical readings for a specific chemical
        
        Args:
            chemical: Chemical parameter name
            days: Number of days to look back (default: 30)
            
        Returns:
            List of (timestamp, value) tuples
        """
        if chemical not in self.history:
            return []
            
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # Filter readings within the time range
        filtered_readings = [
            (timestamp, value) 
            for timestamp, value in self.history[chemical] 
            if timestamp >= cutoff_date
        ]
        
        return sorted(filtered_readings, key=lambda x: x[0])
        
    def get_average(self, chemical: str, days: int = 7) -> float:
        """
        Get average reading for a specific chemical over a time period
        
        Args:
            chemical: Chemical parameter name
            days: Number of days to look back (default: 7)
            
        Returns:
            float: Average value
        """
        readings = self.get_readings(chemical, days)
        
        if not readings:
            return 0
            
        values = [value for _,
