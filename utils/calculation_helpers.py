# utils/calculation_helpers.py
"""
Utility functions for pool chemistry calculations.
"""
import math
from typing import Union, Optional


def calculate_langelier_saturation_index(
    pH: float,
    temperature: float,
    calcium_hardness: float,
    total_alkalinity: float,
    total_dissolved_solids: Optional[float] = None
) -> float:
    """
    Calculate the Langelier Saturation Index (LSI) for pool water.
    
    The LSI is used to determine if pool water is balanced.
    LSI between -0.3 and +0.3 indicates balanced water.
    LSI < -0.3 indicates corrosive water.
    LSI > +0.3 indicates scaling water.
    
    Args:
        pH: Water pH level
        temperature: Water temperature in degrees Fahrenheit
        calcium_hardness: Calcium hardness in ppm (parts per million)
        total_alkalinity: Total alkalinity in ppm
        total_dissolved_solids: Total dissolved solids in ppm (optional)
        
    Returns:
        float: The Langelier Saturation Index
    """
    # Temperature factor (TF) - convert from Fahrenheit to Celsius first if needed
    temp_celsius = (temperature - 32) * 5 / 9 if temperature > 50 else temperature
    if temp_celsius < 0:
        TF = 0.0
    elif temp_celsius <= 53:
        # Polynomial fit for temperature factor
        TF = -0.0000001*(temp_celsius**3) + 0.00002*(temp_celsius**2) + 0.0048*temp_celsius + 0.4
    else:
        TF = 0.8  # For temperatures above 53°C
    
    # Calcium hardness factor (CF)
    CF = math.log10(max(calcium_hardness, 1)) - 0.4
    
    # Alkalinity factor (AF)
    AF = math.log10(max(total_alkalinity, 1)) - 0.7
    
    # TDS factor (TDSF) - default to 12.1 if not provided
    if total_dissolved_solids and total_dissolved_solids > 1000:
        TDSF = 12.3 + math.log10(total_dissolved_solids / 1000)
    else:
        TDSF = 12.1
    
    # Calculate LSI
    LSI = pH + TF + CF + AF - TDSF
    
    return round(LSI, 2)


def calculate_chemical_dosage(
    pool_size_gallons: float,
    current_level: float, 
    target_level: float,
    chemical_factor: float
) -> float:
    """
    Calculate the amount of chemical needed to adjust a reading to a target level.
    
    Args:
        pool_size_gallons: Size of the pool in gallons
        current_level: Current chemical level
        target_level: Target chemical level
        chemical_factor: The amount of chemical needed to raise the level by 1.0 in a 10,000 gallon pool
        
    Returns:
        float: The amount of chemical in ounces needed
    """
    level_difference = target_level - current_level
    pool_factor = pool_size_gallons / 10000.0
    return round(level_difference * chemical_factor * pool_factor, 2)
