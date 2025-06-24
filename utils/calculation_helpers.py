# utils/calculation_helpers.py
from typing import Dict, Tuple, List, Optional, Union, Any
import math
import logging

def calculate_langelier_saturation_index(
    pH: float,
    temperature: float,
    calcium_hardness: float,
    total_alkalinity: float,
    total_dissolved_solids: float = 0
) -> float:
    """
    Calculate the Langelier Saturation Index (LSI) for pool water.
    
    The LSI is a measure of the water's balance. An index of 0 indicates
    perfectly balanced water. Negative values indicate corrosive water,
    while positive values indicate scaling water.
    
    Args:
        pH: Current pH level of the water (typically 6.5-8.5)
        temperature: Water temperature in Fahrenheit
        calcium_hardness: Calcium hardness level in ppm
        total_alkalinity: Total alkalinity level in ppm
        total_dissolved_solids: TDS in ppm (default 0, will estimate if not provided)
            
    Returns:
        float: LSI value. Positive value indicates scaling tendency,
              negative value indicates corrosive tendency,
              value near zero indicates balanced water
              
    Raises:
        ValueError: If input parameters are outside reasonable ranges
        
    Example:
        >>> calculate_langelier_saturation_index(7.4, 78, 275, 100)
        0.12
    """
    # Validate parameters
    if not 6.0 <= pH <= 9.0:
        raise ValueError(f"pH must be between 6.0 and 9.0, got {pH}")
    if not 32 <= temperature <= 105:
        raise ValueError(f"Temperature must be between 32F and 105F, got {temperature}")
    if calcium_hardness <= 0:
        raise ValueError(f"Calcium hardness must be positive, got {calcium_hardness}")
    if total_alkalinity <= 0:
        raise ValueError(f"Total alkalinity must be positive, got {total_alkalinity}")
    
    try:
        # Temperature factor
        if temperature <= 32:
            tf = 0.0
        elif temperature <= 37:
            tf = 0.1
        elif temperature <= 46:
            tf = 0.2
        elif temperature <= 53:
            tf = 0.3
        elif temperature <= 60:
            tf = 0.4
        elif temperature <= 66:
            tf = 0.5
        elif temperature <= 76:
            tf = 0.6
        elif temperature <= 84:
            tf = 0.7
        elif temperature <= 94:
            tf = 0.8
        elif temperature <= 105:
            tf = 0.9
        else:
            tf = 1.0
            
        # Calcium hardness factor
        cf = math.log10(calcium_hardness) - 3.0
        
        # Alkalinity factor
        af = math.log10(total_alkalinity) - 3.0
        
        # For salt water pools, estimate TDS if not provided
        if total_dissolved_solids <= 0:
            # Estimate TDS based on average readings or use a default
            total_dissolved_solids = 1000  # Default estimate
        
        # TDS factor
        tds_factor = (math.log10(total_dissolved_solids) - 3.0) / 10
        
        # Calculate LSI
        lsi = pH + tf + cf + af + tds_factor - 12.1
        
        logger.debug(f"Calculated LSI: {lsi:.2f} (pH={pH}, temp={temperature}F, "
                   f"hardness={calcium_hardness}, alkalinity={total_alkalinity})")
        return lsi
        
    except Exception as e:
        logger.error(f"Error calculating LSI: {str(e)}")
        raise ValueError(f"Failed to calculate LSI: {str(e)}") from e
