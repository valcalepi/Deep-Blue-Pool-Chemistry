# pool_calculations.py
"""
Module for performing pool chemistry calculations.
"""
from typing import Dict, Tuple, Optional, Union
from constants import Constants
from utils.calculation_helpers import calculate_langelier_saturation_index, calculate_chemical_dosage
from exceptions import ChemicalCalculationError

class PoolCalculations:
    """
    Performs various calculations related to pool water chemistry.
    """
    
    @staticmethod
    def calculate_ph_adjustment(
        current_ph: float,
        pool_size_gallons: float,
        target_ph: Optional[float] = None
    ) -> Dict[str, Union[float, str]]:
        """
        Calculate pH adjustment needed.
        
        Args:
            current_ph: Current pH level
            pool_size_gallons: Pool size in gallons
            target_ph: Target pH level (defaults to ideal pH in Constants)
            
        Returns:
            Dictionary with adjustment details
        """
        if target_ph is None:
            target_ph = (Constants.IDEAL_PH_RANGE[0] + Constants.IDEAL_PH_RANGE[1]) / 2
            
        if current_ph < target_ph:
            # Need to increase pH
            adjustment = "increase"
            chemical = Constants.PH_INCREASER
            dosage = calculate_chemical_dosage(
                pool_size_gallons,
                current_ph,
                target_ph,
                Constants.PH_INCREASE_FACTOR
            )
        elif current_ph > target_ph:
            # Need to decrease pH
            adjustment = "decrease"
            chemical = Constants.PH_DECREASER
            dosage = calculate_chemical_dosage(
                pool_size_gallons,
                current_ph,
                target_ph,
                Constants.PH_DECREASE_FACTOR
            )
        else:
            # No adjustment needed
            adjustment = "none"
            chemical = None
            dosage = 0
            
        return {
            "current": current_ph,
            "target": target_ph,
            "adjustment": adjustment,
            "chemical": chemical,
            "dosage_oz": dosage,
            "dosage_lbs": dosage / 16 if dosage else 0
        }
        
    @staticmethod
    def calculate_chlorine_adjustment(
        current_chlorine: float,
        pool_size_gallons: float,
        target_chlorine: Optional[float] = None
    ) -> Dict[str, Union[float, str]]:
        """
        Calculate chlorine adjustment needed.
        
        Args:
            current_chlorine: Current free chlorine level in ppm
            pool_size_gallons: Pool size in gallons
            target_chlorine: Target chlorine level (defaults to ideal in Constants)
            
        Returns:
            Dictionary with adjustment details
        """
        if target_chlorine is None:
            target_chlorine = (Constants.IDEAL_CHLORINE_RANGE[0] + Constants.IDEAL_CHLORINE_RANGE[1]) / 2
            
        if current_chlorine < target_chlorine:
            # Need to increase chlorine
            adjustment = "increase"
            chemical = Constants.CHLORINE_INCREASER
            dosage = calculate_chemical_dosage(
                pool_size_gallons,
                current_chlorine,
                target_chlorine,
                Constants.CHLORINE_INCREASE_FACTOR
            )
        elif current_chlorine > Constants.IDEAL_CHLORINE_RANGE[1] * 1.5:
            # Chlorine too high - recommend dilution
            adjustment = "decrease"
            chemical = "Dilution with fresh water"
            dosage = 0  # No direct chemical to add
        else:
            # No adjustment needed
            adjustment = "none"
            chemical = None
            dosage = 0
            
        return {
            "current": current_chlorine,
            "target": target_chlorine,
            "adjustment": adjustment,
            "chemical": chemical,
            "dosage_oz": dosage,
            "dosage_lbs": dosage / 16 if dosage else 0
        }
        
    @staticmethod
    def calculate_alkalinity_adjustment(
        current_alkalinity: float,
        pool_size_gallons: float,
        target_alkalinity: Optional[float] = None
    ) -> Dict[str, Union[float, str]]:
        """
        Calculate alkalinity adjustment needed.
        
        Args:
            current_alkalinity: Current alkalinity level in ppm
            pool_size_gallons: Pool size in gallons
            target_alkalinity: Target alkalinity level (defaults to ideal in Constants)
            
        Returns:
            Dictionary with adjustment details
        """
        if target_alkalinity is None:
            target_alkalinity = (Constants.IDEAL_ALKALINITY_RANGE[0] + Constants.IDEAL_ALKALINITY_RANGE[1]) / 2
            
        if current_alkalinity < target_alkalinity:
            # Need to increase alkalinity
            adjustment = "increase"
            chemical = Constants.ALKALINITY_INCREASER
            dosage = calculate_chemical_dosage(
                pool_size_gallons,
                current_alkalinity,
                target_alkalinity,
                Constants.ALKALINITY_INCREASE_FACTOR
            )
        elif current_alkalinity > target_alkalinity:
            # Need to decrease alkalinity
            adjustment = "decrease"
            chemical = Constants.ALKALINITY_DECREASER
            dosage = calculate_chemical_dosage(
                pool_size_gallons,
                current_alkalinity,
                target_alkalinity,
                Constants.ALKALINITY_DECREASE_FACTOR
            )
        else:
            # No adjustment needed
            adjustment = "none"
            chemical = None
            dosage = 0
            
        return {
            "current": current_alkalinity,
            "target": target_alkalinity,
            "adjustment": adjustment,
            "chemical": chemical,
            "dosage_oz": dosage,
            "dosage_lbs": dosage / 16 if dosage else 0
        }
        
    @staticmethod
    def calculate_water_balance(
        ph: float,
        alkalinity: float,
        calcium_hardness: float,
        temperature: float,
        tds: Optional[float] = None
    ) -> Dict[str, Union[float, str]]:
        """
        Calculate water balance using Langelier Saturation Index.
        
        Args:
            ph: Water pH level
            alkalinity: Alkalinity level in ppm
            calcium_hardness: Calcium hardness in ppm
            temperature: Water temperature in degrees Fahrenheit
            tds: Total dissolved solids in ppm (optional)
            
        Returns:
            Dictionary with LSI and water balance status
        """
        try:
            lsi = calculate_langelier_saturation_index(
                ph=ph,
                temperature=temperature,
                calcium_hardness=calcium_hardness,
                total_alkalinity=alkalinity,
                total_dissolved_solids=tds
            )
            
            # Interpret LSI
            if -0.3 <= lsi <= 0.3:
                status = "Balanced"
            elif lsi < -0.3:
                status = "Corrosive"
            else:  # lsi > 0.3
                status = "Scaling"
                
            return {
                "lsi": lsi,
                "status": status,
                "balanced": status == "Balanced"
            }
            
        except Exception as e:
            raise ChemicalCalculationError(f"Error calculating water balance: {str(e)}")
