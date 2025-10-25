# models/chemical_calculator.py
import math
import logging
from typing import Dict, Tuple, Optional, Union, Any
from contextlib import contextmanager

# Configure logging
logger = logging.getLogger(__name__)

class ChemicalCalculator:
    """
    Calculator for pool chemical adjustments and water balance.
    
    This class provides methods to calculate chemical adjustments needed
    for maintaining proper pool chemistry, including pH, chlorine,
    alkalinity, and calcium hardness levels.
    """
    
    def __init__(self):
        """Initialize the chemical calculator with ideal ranges for different parameters."""
        # Define ideal ranges for different parameters
        self.ideal_ranges = {
            "ph": (7.2, 7.8),
            "chlorine": (1.0, 3.0),
            "alkalinity": (80, 120),
            "calcium_hardness": {
                "Concrete": (200, 400),
                "Vinyl": (175, 225),
                "Fiberglass": (150, 250)
            }
        }
        
        # Define valid value ranges for validation
        self.valid_ranges = {
            "ph": (6.0, 9.0),
            "chlorine": (0.0, 10.0),
            "alkalinity": (0, 240),
            "calcium_hardness": (0, 1000)
        }
        
        # Chemical adjustment factors (amount needed per unit change per 10,000 gallons)
        self.adjustment_factors = {
            "ph_increase": 6.0,  # oz of pH increaser per 0.1 pH increase
            "ph_decrease": 8.0,  # oz of pH decreaser per 0.1 pH decrease
            "chlorine_increase": 4.0,  # oz of chlorine per 1.0 ppm increase
            "alkalinity_increase": 1.5,  # lbs of alkalinity increaser per 10 ppm increase
            "alkalinity_decrease": 1.2,  # lbs of pH decreaser per 10 ppm decrease
            "calcium_increase": 1.0  # lbs of calcium hardness increaser per 10 ppm increase
        }
        
        self.current_pool_type = None
        logger.info("ChemicalCalculator initialized with default parameters")
    
    def set_pool_type(self, pool_type: str) -> None:
        """
        Set the current pool type for calculations.
        
        Args:
            pool_type: Type of pool (Concrete, Vinyl, Fiberglass)
            
        Raises:
            ValueError: If the pool type is not recognized
        """
        if pool_type in self.ideal_ranges["calcium_hardness"]:
            self.current_pool_type = pool_type
            logger.info(f"Pool type set to: {pool_type}")
        else:
            error_msg = f"Unknown pool type: {pool_type}"
            logger.error(error_msg)
            raise ValueError(error_msg)
    
    def validate_reading(self, parameter: str, value: float) -> float:
        """
        Validate a chemical reading to ensure it's within reasonable ranges.
        
        Args:
            parameter: The chemical parameter name
            value: The reading value
            
        Returns:
            The validated value
            
        Raises:
            ValueError: If the value is outside reasonable ranges
        """
        try:
            # Check if parameter exists in valid ranges
            if parameter not in self.valid_ranges:
                logger.warning(f"No validation range defined for {parameter}, skipping validation")
                return value
                
            min_val, max_val = self.valid_ranges[parameter]
            
            # Check if value is within valid range
            if value < min_val:
                logger.warning(f"{parameter} value {value} is below minimum {min_val}")
            elif value > max_val:
                logger.warning(f"{parameter} value {value} is above maximum {max_val}")
                
            return value
            
        except Exception as e:
            error_msg = f"Error validating {parameter} value {value}: {str(e)}"
            logger.error(error_msg)
            raise ValueError(error_msg)
    
    def calculate_adjustments(self, pool_type: str, ph: float, chlorine: float, 
                             alkalinity: float, calcium_hardness: float, 
                             pool_volume_gallons: float = 10000) -> Dict[str, str]:
        """
        Calculate chemical adjustments needed based on current readings.
        
        Args:
            pool_type: Type of pool (Concrete, Vinyl, Fiberglass)
            ph: Current pH level
            chlorine: Current chlorine level (ppm)
            alkalinity: Current alkalinity level (ppm)
            calcium_hardness: Current calcium hardness level (ppm)
            pool_volume_gallons: Pool volume in gallons (default: 10,000)
            
        Returns:
            Dictionary with adjustment recommendations for each parameter
            
        Raises:
            ValueError: If pool type is not recognized or values are invalid
        """
        try:
            # Validate pool type
            if pool_type not in self.ideal_ranges["calcium_hardness"]:
                raise ValueError(f"Unknown pool type: {pool_type}")
            
            # Set current pool type
            self.current_pool_type = pool_type
            
            # Validate input parameters
            ph = self.validate_reading("ph", ph)
            chlorine = self.validate_reading("chlorine", chlorine)
            alkalinity = self.validate_reading("alkalinity", alkalinity)
            calcium_hardness = self.validate_reading("calcium_hardness", calcium_hardness)
            
            # Calculate volume factor (relative to 10,000 gallons)
            volume_factor = pool_volume_gallons / 10000.0
            
            # Initialize adjustments dictionary
            adjustments = {}
            
            # Calculate pH adjustment
            adjustments["pH"] = self._calculate_ph_adjustment(ph, volume_factor)
            
            # Calculate chlorine adjustment
            adjustments["Chlorine"] = self._calculate_chlorine_adjustment(chlorine, volume_factor)
            
            # Calculate alkalinity adjustment
            adjustments["Alkalinity"] = self._calculate_alkalinity_adjustment(alkalinity, volume_factor)
            
            # Calculate calcium hardness adjustment
            adjustments["Calcium Hardness"] = self._calculate_calcium_adjustment(
                calcium_hardness, pool_type, volume_factor
            )
            
            logger.info(f"Calculated adjustments for {pool_type} pool")
            return adjustments
            
        except Exception as e:
            error_msg = f"Error calculating adjustments: {str(e)}"
            logger.error(error_msg)
            raise ValueError(error_msg)
    
    def _calculate_ph_adjustment(self, ph: float, volume_factor: float) -> str:
        """
        Calculate pH adjustment needed.
        
        Args:
            ph: Current pH level
            volume_factor: Pool volume factor (relative to 10,000 gallons)
            
        Returns:
            String with adjustment recommendation
        """
        ph_low, ph_high = self.ideal_ranges["ph"]
        
        if ph < ph_low:
            # Calculate amount of pH increaser needed
            ph_diff = ph_low - ph
            oz_needed = self._calculate_ph_increase(ph_diff, volume_factor)
            return f"Increase by {oz_needed} oz of pH increaser"
            
        elif ph > ph_high:
            # Calculate amount of pH decreaser needed
            ph_diff = ph - ph_high
            oz_needed = self._calculate_ph_decrease(ph_diff, volume_factor)
            return f"Decrease by {oz_needed} oz of pH reducer"
            
        else:
            return "No adjustment needed"
    
    def _calculate_chlorine_adjustment(self, chlorine: float, volume_factor: float) -> str:
        """
        Calculate chlorine adjustment needed.
        
        Args:
            chlorine: Current chlorine level (ppm)
            volume_factor: Pool volume factor (relative to 10,000 gallons)
            
        Returns:
            String with adjustment recommendation
        """
        cl_low, cl_high = self.ideal_ranges["chlorine"]
        
        if chlorine < cl_low:
            # Calculate amount of chlorine needed
            cl_diff = cl_low - chlorine
            oz_needed = self._calculate_chlorine_increase(cl_diff, volume_factor)
            return f"Add {oz_needed} oz of chlorine"
            
        elif chlorine > cl_high:
            return "Allow chlorine levels to decrease naturally"
            
        else:
            return "No adjustment needed"
    
    def _calculate_alkalinity_adjustment(self, alkalinity: float, volume_factor: float) -> str:
        """
        Calculate alkalinity adjustment needed.
        
        Args:
            alkalinity: Current alkalinity level (ppm)
            volume_factor: Pool volume factor (relative to 10,000 gallons)
            
        Returns:
            String with adjustment recommendation
        """
        alk_low, alk_high = self.ideal_ranges["alkalinity"]
        
        if alkalinity < alk_low:
            # Calculate amount of alkalinity increaser needed
            alk_diff = alk_low - alkalinity
            oz_needed = self._calculate_alkalinity_increase(alk_diff, volume_factor)
            return f"Add {oz_needed} oz of alkalinity increaser"
            
        elif alkalinity > alk_high:
            # Calculate amount of pH reducer needed to decrease alkalinity
            alk_diff = alkalinity - alk_high
            oz_needed = self._calculate_alkalinity_decrease(alk_diff, volume_factor)
            return f"Add {oz_needed} oz of pH reducer"
            
        else:
            return "No adjustment needed"
    
    def _calculate_calcium_adjustment(self, calcium_hardness: float, pool_type: str, 
                                     volume_factor: float) -> str:
        """
        Calculate calcium hardness adjustment needed.
        
        Args:
            calcium_hardness: Current calcium hardness level (ppm)
            pool_type: Type of pool
            volume_factor: Pool volume factor (relative to 10,000 gallons)
            
        Returns:
            String with adjustment recommendation
        """
        ch_low, ch_high = self.ideal_ranges["calcium_hardness"][pool_type]
        
        if calcium_hardness < ch_low:
            # Calculate amount of calcium hardness increaser needed
            ch_diff = ch_low - calcium_hardness
            oz_needed = self._calculate_calcium_increase(ch_diff, volume_factor)
            return f"Add {oz_needed} oz of calcium hardness increaser"
            
        elif calcium_hardness > ch_high:
            return "Partially drain and refill pool with fresh water"
            
        else:
            return "No adjustment needed"
    
    def _calculate_ph_increase(self, ph_diff: float, volume_factor: float) -> float:
        """
        Calculate amount of pH increaser needed.
        
        The formula is based on the fact that approximately 6 oz of pH increaser
        is needed to raise the pH by 0.1 in a 10,000 gallon pool.
        
        Args:
            ph_diff: Difference between current and target pH
            volume_factor: Pool volume factor (relative to 10,000 gallons)
            
        Returns:
            Amount of pH increaser needed in ounces
        """
        # Convert pH difference to number of 0.1 increments
        increments = ph_diff * 10
        
        # Calculate ounces needed
        oz_needed = increments * self.adjustment_factors["ph_increase"] * volume_factor
        
        return round(oz_needed, 1)
    
    def _calculate_ph_decrease(self, ph_diff: float, volume_factor: float) -> float:
        """
        Calculate amount of pH decreaser needed.
        
        The formula is based on the fact that approximately 8 oz of pH decreaser
        is needed to lower the pH by 0.1 in a 10,000 gallon pool.
        
        Args:
            ph_diff: Difference between current and target pH
            volume_factor: Pool volume factor (relative to 10,000 gallons)
            
        Returns:
            Amount of pH decreaser needed in ounces
        """
        # Convert pH difference to number of 0.1 increments
        increments = ph_diff * 10
        
        # Calculate ounces needed
        oz_needed = increments * self.adjustment_factors["ph_decrease"] * volume_factor
        
        return round(oz_needed, 1)
    
    def _calculate_chlorine_increase(self, cl_diff: float, volume_factor: float) -> float:
        """
        Calculate amount of chlorine needed.
        
        The formula is based on the fact that approximately 4 oz of liquid chlorine
        is needed to raise the chlorine level by 1.0 ppm in a 10,000 gallon pool.
        
        Args:
            cl_diff: Difference between current and target chlorine level
            volume_factor: Pool volume factor (relative to 10,000 gallons)
            
        Returns:
            Amount of chlorine needed in ounces
        """
        # Calculate ounces needed
        oz_needed = cl_diff * self.adjustment_factors["chlorine_increase"] * volume_factor
        
        return round(oz_needed, 1)
    
    def _calculate_alkalinity_increase(self, alk_diff: float, volume_factor: float) -> float:
        """
        Calculate amount of alkalinity increaser needed.
        
        The formula is based on the fact that approximately 1.5 lbs of alkalinity increaser
        is needed to raise the alkalinity by 10 ppm in a 10,000 gallon pool.
        
        Args:
            alk_diff: Difference between current and target alkalinity level
            volume_factor: Pool volume factor (relative to 10,000 gallons)
            
        Returns:
            Amount of alkalinity increaser needed in ounces
        """
        # Convert alkalinity difference to number of 10 ppm increments
        increments = alk_diff / 10
        
        # Calculate pounds needed
        lbs_needed = increments * self.adjustment_factors["alkalinity_increase"] * volume_factor
        
        # Convert to ounces (1 lb = 16 oz)
        oz_needed = lbs_needed * 16
        
        return round(oz_needed, 1)
    
    def _calculate_alkalinity_decrease(self, alk_diff: float, volume_factor: float) -> float:
        """
        Calculate amount of pH reducer needed to decrease alkalinity.
        
        The formula is based on the fact that approximately 1.2 lbs of pH reducer
        is needed to lower the alkalinity by 10 ppm in a 10,000 gallon pool.
        
        Args:
            alk_diff: Difference between current and target alkalinity level
            volume_factor: Pool volume factor (relative to 10,000 gallons)
            
        Returns:
            Amount of pH reducer needed in ounces
        """
        # Convert alkalinity difference to number of 10 ppm increments
        increments = alk_diff / 10
        
        # Calculate pounds needed
        lbs_needed = increments * self.adjustment_factors["alkalinity_decrease"] * volume_factor
        
        # Convert to ounces (1 lb = 16 oz)
        oz_needed = lbs_needed * 16
        
        return round(oz_needed, 1)
    
    def _calculate_calcium_increase(self, ch_diff: float, volume_factor: float) -> float:
        """
        Calculate amount of calcium hardness increaser needed.
        
        The formula is based on the fact that approximately 1 lb of calcium hardness increaser
        is needed to raise the calcium hardness by 10 ppm in a 10,000 gallon pool.
        
        Args:
            ch_diff: Difference between current and target calcium hardness level
            volume_factor: Pool volume factor (relative to 10,000 gallons)
            
        Returns:
            Amount of calcium hardness increaser needed in ounces
        """
        # Convert calcium hardness difference to number of 10 ppm increments
        increments = ch_diff / 10
        
        # Calculate pounds needed
        lbs_needed = increments * self.adjustment_factors["calcium_increase"] * volume_factor
        
        # Convert to ounces (1 lb = 16 oz)
        oz_needed = lbs_needed * 16
        
        return round(oz_needed, 1)
    
    def get_ideal_range(self, parameter: str, pool_type: Optional[str] = None) -> Tuple[float, float]:
        """
        Get the ideal range for a specific parameter.
        
        Args:
            parameter: Chemical parameter name
            pool_type: Optional pool type (uses current if not provided)
            
        Returns:
            Tuple of (min, max) values
            
        Raises:
            ValueError: If pool type is not set for calcium hardness
        """
        try:
            if parameter == "calcium_hardness":
                if not pool_type and not self.current_pool_type:
                    error_msg = "Pool type must be specified for calcium hardness"
                    logger.error(error_msg)
                    raise ValueError(error_msg)
                    
                selected_pool_type = pool_type or self.current_pool_type
                return self.ideal_ranges[parameter][selected_pool_type]
            else:
                if parameter not in self.ideal_ranges:
                    logger.warning(f"No ideal range defined for {parameter}, returning (0, 0)")
                    return (0, 0)
                    
                return self.ideal_ranges[parameter]
                
        except Exception as e:
            if not isinstance(e, ValueError):
                error_msg = f"Error getting ideal range for {parameter}: {str(e)}"
                logger.error(error_msg)
                raise ValueError(error_msg)
            raise
    
    def evaluate_water_balance(self, ph: float, alkalinity: float, calcium_hardness: float, 
                              temperature_f: float = 78.0) -> Dict[str, Any]:
        """
        Calculate Langelier Saturation Index (LSI) for water balance.
        
        The LSI is used to determine if water is balanced, corrosive, or scaling.
        LSI = pH + TF + CF + AF - 12.1
        
        Where:
        - TF = Temperature Factor
        - CF = Calcium Hardness Factor
        - AF = Alkalinity Factor
        - 12.1 = Constant for TDS at average levels
        
        Args:
            ph: Current pH level
            alkalinity: Current alkalinity level (ppm)
            calcium_hardness: Current calcium hardness level (ppm)
            temperature_f: Water temperature in Fahrenheit (default: 78.0)
            
        Returns:
            Dictionary with LSI value, status, and recommendation
            
        Raises:
            ValueError: If input values are invalid
        """
        try:
            # Validate input parameters
            ph = self.validate_reading("ph", ph)
            alkalinity = self.validate_reading("alkalinity", alkalinity)
            calcium_hardness = self.validate_reading("calcium_hardness", calcium_hardness)
            
            if temperature_f < 32 or temperature_f > 105:
                logger.warning(f"Temperature {temperature_f}°F is outside normal range (32-105°F)")
            
            # Convert Fahrenheit to Celsius
            temperature_c = (temperature_f - 32) * 5/9
            
            # Calculate temperature factor
            temp_factor = self._calculate_temperature_factor(temperature_c)
            
            # Calculate calcium hardness factor
            ch_factor = self._calculate_ch_factor(calcium_hardness)
            
            # Calculate alkalinity factor
            alk_factor = self._calculate_alk_factor(alkalinity)
            
            # Calculate LSI
            # The constant 12.1 represents the TDS factor for average TDS levels
            lsi = ph + temp_factor + ch_factor + alk_factor - 12.1
            
            # Round LSI to 2 decimal places
            lsi = round(lsi, 2)
            
            # Interpret LSI
            if lsi < -0.3:
                status = "Corrosive"
                recommendation = "Increase pH, alkalinity, or calcium hardness"
            elif lsi > 0.3:
                status = "Scaling"
                recommendation = "Decrease pH, alkalinity, or calcium hardness"
            else:
                status = "Balanced"
                recommendation = "Maintain current levels"
            
            logger.info(f"Water balance evaluation: LSI={lsi}, Status={status}")
            
            return {
                "lsi": lsi,
                "status": status,
                "recommendation": recommendation,
                "factors": {
                    "pH": ph,
                    "temperature_factor": round(temp_factor, 2),
                    "calcium_factor": round(ch_factor, 2),
                    "alkalinity_factor": round(alk_factor, 2)
                }
            }
            
        except Exception as e:
            error_msg = f"Error evaluating water balance: {str(e)}"
            logger.error(error_msg)
            raise ValueError(error_msg)
    
    def _calculate_temperature_factor(self, temperature_c: float) -> float:
        """
        Calculate temperature factor for LSI.
        
        The temperature factor increases as temperature increases,
        reflecting the fact that calcium carbonate becomes less soluble
        at higher temperatures.
        
        Args:
            temperature_c: Water temperature in Celsius
            
        Returns:
            Temperature factor for LSI calculation
        """
        if temperature_c < 0:
            return 0.0
        elif temperature_c <= 28:
            # Linear approximation for common temperature range
            return 0.2 * (temperature_c / 6)
        else:
            # For higher temperatures
            return 0.8 + (0.2 * (temperature_c - 28) / 50)
    
    def _calculate_ch_factor(self, calcium_hardness: float) -> float:
        """
        Calculate calcium hardness factor for LSI.
        
        The formula is log10(calcium hardness) - 0.4,
        where 0.4 is a constant derived from the solubility of calcium carbonate.
        
        Args:
            calcium_hardness: Calcium hardness level in ppm
            
        Returns:
            Calcium hardness factor for LSI calculation
        """
        if calcium_hardness <= 0:
            logger.warning("Calcium hardness must be greater than 0, using minimum value")
            calcium_hardness = 1
            
        try:
            return math.log10(calcium_hardness) - 0.4
        except (ValueError, TypeError) as e:
            error_msg = f"Error calculating calcium hardness factor: {str(e)}"
            logger.error(error_msg)
            raise ValueError(error_msg)
    
    def _calculate_alk_factor(self, alkalinity: float) -> float:
        """
        Calculate alkalinity factor for LSI.
        
        The formula is log10(alkalinity) - 0.7,
        where 0.7 is a constant derived from the relationship between
        alkalinity and carbonate availability.
        
        Args:
            alkalinity: Alkalinity level in ppm
            
        Returns:
            Alkalinity factor for LSI calculation
        """
        if alkalinity <= 0:
            logger.warning("Alkalinity must be greater than 0, using minimum value")
            alkalinity = 1
            
        try:
            return math.log10(alkalinity) - 0.7
        except (ValueError, TypeError) as e:
            error_msg = f"Error calculating alkalinity factor: {str(e)}"
            logger.error(error_msg)
            raise ValueError(error_msg)
