# models/water_tester.py
"""
Model for handling water testing and chemical dosage calculations.
"""
from typing import Dict, Tuple, Optional, Union, List
import math
from exceptions import ChemicalCalculationError
from utils.calculation_helpers import calculate_chemical_dosage
from constants import Constants

class WaterTester:
    """
    Model for testing pool water and calculating chemical dosages.
    """
    def __init__(self):
        """Initialize with default values."""
        self.pool_volume = 0  # in gallons
        
    def set_pool_volume(self, volume: float) -> None:
        """
        Set the pool volume for calculations.
        
        Args:
            volume: Pool volume in gallons
        """
        if volume <= 0:
            raise ValueError("Pool volume must be greater than zero")
        self.pool_volume = volume
        
    def analyze_ph(self, current_ph: float) -> Dict[str, Union[float, str]]:
        """
        Analyze pH and calculate needed adjustments.
        
        Args:
            current_ph: Current pH reading
            
        Returns:
            Dictionary with analysis results and recommendations
        """
        ideal_range = Constants.IDEAL_PH_RANGE
        
        if current_ph < ideal_range[0]:
            direction = "low"
            adjustment = "increase"
            chemical = Constants.PH_INCREASER
            dosage = self._calculate_ph_dosage(ideal_range[0] - current_ph)
        elif current_ph > ideal_range[1]:
            direction = "high"
            adjustment = "decrease"
            chemical = Constants.PH_DECREASER
            dosage = self._calculate_ph_dosage(current_ph - ideal_range[1])
        else:
            direction = "normal"
            adjustment = "none"
            chemical = None
            dosage = "No adjustment needed"
            
        return {
            "current": current_ph,
            "ideal_range": ideal_range,
            "direction": direction,
            "adjustment": adjustment,
            "chemical": chemical,
            "dosage": dosage
        }
        
    def analyze_chlorine(self, current_chlorine: float) -> Dict[str, Union[float, str]]:
        """
        Analyze chlorine levels and calculate needed adjustments.
        
        Args:
            current_chlorine: Current free chlorine reading in ppm
            
        Returns:
            Dictionary with analysis results and recommendations
        """
        ideal_range = Constants.IDEAL_CHLORINE_RANGE
        
        if current_chlorine < ideal_range[0]:
            direction = "low"
            adjustment = "increase"
            chemical = Constants.CHLORINE_INCREASER
            dosage = self._calculate_chlorine_dosage(ideal_range[0] - current_chlorine)
        elif current_chlorine > ideal_range[1] * 1.5:  # Allow a bit higher than ideal before recommending reduction
            direction = "high"
            adjustment = "decrease"
            chemical = "None - Allow chlorine to dissipate naturally"
            dosage = "No chemical needed, reduce sun exposure or wait for levels to decrease naturally"
        else:
            direction = "normal"
            adjustment = "none"
            chemical = None
            dosage = "No adjustment needed"
            
        return {
            "current": current_chlorine,
            "ideal_range": ideal_range,
            "direction": direction,
            "adjustment": adjustment,
            "chemical": chemical,
            "dosage": dosage
        }
        
    def _calculate_ph_dosage(self, ph_difference: float) -> str:
        """
        Calculate pH adjustment dosage.
        
        Args:
            ph_difference: Difference between current and target pH
            
        Returns:
            String with dosage instructions
        """
        if ph_difference <= 0:
            return "No adjustment needed"
            
        # Calculate amount needed in ounces
        # Typical dosage: 16 oz (1 lb) raises pH by 0.2 in 10,000 gallons
        ounces_per_10k_gallons = (ph_difference / 0.2) * 16
        total_ounces = (self.pool_volume / 10000) * ounces_per_10k_gallons
        
        # Convert to pounds and ounces for display
        if total_ounces >= 16:
            pounds = total_ounces / 16
            return f"{pounds:.2f} lbs"
        else:
            return f"{total_ounces:.1f} oz"
            
    def _calculate_chlorine_dosage(self, chlorine_difference: float) -> str:
        """
        Calculate chlorine adjustment dosage.
        
        Args:
            chlorine_difference: Difference between current and target chlorine level in ppm
            
        Returns:
            String with dosage instructions
        """
        if chlorine_difference <= 0:
            return "No adjustment needed"
            
        # Calculate amount needed in ounces
        # Typical dosage for liquid chlorine: 12.8 fl oz raises chlorine by 1 ppm in 10,000 
