# chemistry.py
# Updated: July 04, 2025
# This file contains a WaterTester class for analyzing pool water chemistry and calculating chemical dosages.

from datetime import datetime, timedelta, date
from typing import List, Dict, Tuple, Optional, Any, Union

# Directly Define the Constants
CHEMICAL_RANGES = {
    "pH": (7.2, 7.8),
    "Free Chlorine": (1.0, 3.0),
    "Total Chlorine": (1.0, 3.0),
    "Bromine": (3.0, 5.0),
    "Alkalinity": (80, 120),
    "Hardness": (200, 400),
    "Cyanuric Acid": (30, 80),
    "Salt": (2700, 3400)
}

CHEMICAL_FACTORS = {
    "pH": {"increase_oz_per_0.1": 8, "decrease_oz_per_0.1": 8},
    "Free Chlorine": {"increase_oz_per_1_ppm": 13},
    "Alkalinity": {"increase_lbs_per_10_ppm": 1.5, "decrease_lbs_per_10_ppm": 1.2},
    "Hardness": {"increase_lbs_per_10_ppm": 0.6},
    "Cyanuric Acid": {"increase_lbs_per_10_ppm": 1.3},
    "Salt": {"increase_lbs_per_100_ppm": 8.3},
    "Bromine": {"increase_oz_per_1_ppm": 10}
}

INCREASE_CHEMICALS = {
    "pH": "Soda Ash",
    "Free Chlorine": "Liquid Chlorine",
    "Total Chlorine": "Shock Treatment",
    "Alkalinity": "Baking Soda",
    "Hardness": "Calcium Chloride",
    "Cyanuric Acid": "Stabilizer",
    "Salt": "Pool Salt",
    "Bromine": "Bromine Tablets"
}

DECREASE_CHEMICALS = {
    "pH": "Muriatic Acid",
    "Free Chlorine": "Sodium Thiosulfate",
    "Total Chlorine": "Sodium Thiosulfate",
    "Alkalinity": "Muriatic Acid",
    "Hardness": "Partial Water Change",
    "Cyanuric Acid": "Partial Water Change",
    "Salt": "Partial Water Change",
    "Bromine": "Partial Water Change"
}

class WaterTester:
    """
    Manages water testing and chemical dosage calculations for a pool.
    Provides analysis methods for various chemical parameters and suggests adjustments.
    """

    def __init__(self):
        """
        Initializes the WaterTester with industry standard ranges,
        chemical names for adjustments, and safety warnings.
        """
        self.pool_types = [
            "Chlorine Pool",
            "Salt Water Pool", 
            "Bromine Pool",
            "Concrete/Gunite",
            "Vinyl Liner",
            "Fiberglass",
            "Above Ground - Metal Wall",
            "Above Ground - Resin",
            "Infinity Pool",
            "Lap Pool",
            "Indoor Pool"
        ]

        # Use defined constants for chemical ranges
        self.ideal_levels = CHEMICAL_RANGES
        self.increase_chemicals = INCREASE_CHEMICALS
        self.decrease_chemicals = DECREASE_CHEMICALS
        self.chemical_factors = CHEMICAL_FACTORS

        # Initialize chemical warnings
        self.chemical_warnings = {
            "Free Chlorine": """
SAFETY WARNING: 
- Always add chlorine to water, never water to chlorine
- Wear protective gloves and eye protection
- Add during evening hours to prevent rapid dissipation
- Keep away from children and pets
- Never mix with other chemicals
- Ensure proper ventilation when handling
- Store in a cool, dry, well-ventilated area""",
            "Total Chlorine": """
SAFETY WARNING:
- Follow same precautions as Free Chlorine
- Monitor levels carefully after shock treatment
- Wait for levels to normalize before swimming""",
            "pH": """
SAFETY WARNING:
- Handle pH adjusters with care
- Add chemicals slowly and test frequently
- Avoid splashing and inhaling fumes
- Keep chemicals separate""",
            "Alkalinity": """
SAFETY WARNING:
- Add chemicals gradually
- Test frequently during adjustment
- Allow for proper mixing
- Maintain proper pH levels""",
            "Cyanuric Acid": """
SAFETY WARNING:
- Add through skimmer or pre-dissolve
- Avoid direct contact with pool surface
- Monitor levels carefully
- Do not exceed recommended levels""",
            "Salt": """
SAFETY WARNING:
- Add salt gradually
- Allow for complete dissolution
- Verify proper cell operation
- Monitor stabilizer levels"""
        }

        self.pool_volume = 0 # Initialize pool volume in gallons

    def set_pool_volume(self, volume: float) -> None:
        """
        Sets the pool volume for calculations.

        Args:
            volume: The pool volume in gallons

        Raises:
            ValueError: If volume is less than or equal to zero
        """
        if volume <= 0:
            raise ValueError("Pool volume must be greater than zero")
        self.pool_volume = volume

    def _calculate_dosage(self, chemical_name: str, difference: float, is_increase: bool) -> str:
        """
        Helper to calculate chemical dosage based on chemical type, difference, and pool volume.
        This model uses simplified factors. Real-world dosage calculations are more complex
        and depend on product concentration, water chemistry, and pool type.

        Args:
            chemical_name: The name of the chemical parameter (pH, Free Chlorine, etc.)
            difference: The difference between current and target levels
            is_increase: True if increasing level, False if decreasing

        Returns:
            A string representing the recommended dosage with units
        """
        if difference <= 0:
            return "No adjustment needed"

        # Validate that pool volume has been set
        if self.pool_volume <= 0:
            pool_volume_factor = 1.0
        else:
            pool_volume_factor = self.pool_volume / 10000.0 # Factor relative to 10,000 gallons

        dosage_oz = 0.0
        dosage_lbs = 0.0
        unit = "oz" # Default unit

        factors = self.chemical_factors.get(chemical_name)
        if not factors:
            return f"Dosage calculation not available for {chemical_name}"

        try:
            if chemical_name == "pH":
                factor_key = "increase_oz_per_0.1" if is_increase else "decrease_oz_per_0.1"
                dosage_oz = (difference * 10) * factors[factor_key] * pool_volume_factor
                unit = "oz"
            elif chemical_name in ["Free Chlorine", "Bromine"]:
                dosage_oz = difference * factors[f"increase_oz_per_1_ppm"] * pool_volume_factor
                unit = "oz"
            elif chemical_name in ["Alkalinity", "Hardness", "Cyanuric Acid"]:
                factor_key = f"increase_lbs_per_10_ppm" if is_increase else f"decrease_lbs_per_10_ppm"
                factor_lbs = factors.get(factor_key)
                if factor_lbs is None: # For chemicals only increased or decreased by water change
                    return "Partial water change recommended" if not is_increase else "Dosage calculation not available"
                dosage_lbs = (difference / 10) * factor_lbs * pool_volume_factor
                unit = "lbs"
            elif chemical_name == "Salt":
                dosage_lbs = (difference / 100) * factors["increase_lbs_per_100_ppm"] * pool_volume_factor
                unit = "lbs"
            else:
                return f"Dosage calculation not available for {chemical_name}"
        except KeyError as e:
            return f"Error in dosage calculation: missing factor key"
        except Exception as e:
            return f"Error in dosage calculation"

        # Format the result with appropriate units
        if unit == "lbs":
            return f"{dosage_lbs:.2f} lbs"
        else: # unit == "oz"
            return f"{dosage_oz:.1f} oz"

    def _analyze_parameter(self, parameter: str, current_value: float) -> Dict[str, Union[float, str]]:
        """
        Generic method to analyze any chemical parameter and calculate needed adjustments.

        Args:
            parameter: The name of the chemical parameter
            current_value: The current value of the parameter

        Returns:
            A dictionary containing analysis results
        """
        if parameter not in self.ideal_levels:
            return {
                "current": current_value,
                "ideal_range": (0, 0),
                "direction": "unknown",
                "adjustment": "none",
                "chemical": None,
                "dosage": "Parameter not recognized"
            }

        ideal_range = self.ideal_levels[parameter]

        if current_value < ideal_range[0]:
            direction = "low"
            adjustment = "increase"
            chemical = self.increase_chemicals.get(parameter)
            dosage = self._calculate_dosage(parameter, ideal_range[0] - current_value, True)
        elif current_value > ideal_range[1]:
            direction = "high"
            adjustment = "decrease"
            chemical = self.decrease_chemicals.get(parameter)

            # Special handling for chlorine
            if parameter == "Free Chlorine" and current_value <= ideal_range[1] * 1.5:
                direction = "normal" # Allow slightly higher chlorine
                adjustment = "none"
                chemical = None
                dosage = "No adjustment needed"
            else:
                # For parameters that require water change when high
                if chemical == "Partial Water Change":
                    dosage = "Partial water change recommended"
                else:
                    dosage = self._calculate_dosage(parameter, current_value - ideal_range[1], False)
        else:
            direction = "normal"
            adjustment = "none"
            chemical = None
            dosage = "No adjustment needed"

        return {
            "current": current_value,
            "ideal_range": ideal_range,
            "direction": direction,
            "adjustment": adjustment,
            "chemical": chemical,
            "dosage": dosage
        }

    def analyze_ph(self, current_ph: float) -> Dict[str, Union[float, str]]:
        """
        Analyzes pH level and calculates needed adjustments.

        Args:
            current_ph: The current pH level

        Returns:
            A dictionary containing analysis results
        """
        return self._analyze_parameter("pH", current_ph)

    def analyze_chlorine(self, current_chlorine: float) -> Dict[str, Union[float, str]]:
        """
        Analyzes free chlorine levels and calculates needed adjustments.

        Args:
            current_chlorine: The current free chlorine level in ppm

        Returns:
            A dictionary containing analysis results
        """
        return self._analyze_parameter("Free Chlorine", current_chlorine)

    def analyze_alkalinity(self, current_alkalinity: float) -> Dict[str, Union[float, str]]:
        """
        Analyzes total alkalinity levels and calculates needed adjustments.

        Args:
            current_alkalinity: The current alkalinity level in ppm

        Returns:
            A dictionary containing analysis results
        """
        return self._analyze_parameter("Alkalinity", current_alkalinity)

    def analyze_calcium_hardness(self, current_hardness: float) -> Dict[str, Union[float, str]]:
        """
        Analyzes calcium hardness levels and calculates needed adjustments.

        Args:
            current_hardness: The current calcium hardness level in ppm

        Returns:
            A dictionary containing analysis results
        """
        return self._analyze_parameter("Hardness", current_hardness)

    def analyze_cyanuric_acid(self, current_cya: float) -> Dict[str, Union[float, str]]:
        """
        Analyzes cyanuric acid (stabilizer) levels and calculates needed adjustments.

        Args:
            current_cya: The current cyanuric acid level in ppm

        Returns:
            A dictionary containing analysis results
        """
        return self._analyze_parameter("Cyanuric Acid", current_cya)

    def analyze_salt(self, current_salt: float) -> Dict[str, Union[float, str]]:
        """
        Analyzes salt levels and calculates needed adjustments for saltwater pools.

        Args:
            current_salt: The current salt level in ppm

        Returns:
            A dictionary containing analysis results
        """
        return self._analyze_parameter("Salt", current_salt)

    def analyze_bromine(self, current_bromine: float) -> Dict[str, Union[float, str]]:
        """
        Analyzes bromine levels and calculates needed adjustments for bromine pools.

        Args:
            current_bromine: The current bromine level in ppm

        Returns:
            A dictionary containing analysis results
        """
        return self._analyze_parameter("Bromine", current_bromine)

    def analyze_all(self, readings: Dict[str, float]) -> Dict[str, Dict[str, Union[float, str]]]:
        """
        Analyzes all provided chemical readings and returns recommendations for each.

        Args:
            readings: A dictionary mapping parameter names to their current values

        Returns:
            A dictionary mapping parameter names to their analysis results
        """
        results = {}

        for parameter, value in readings.items():
            if parameter == "pH":
                results[parameter] = self.analyze_ph(value)
            elif parameter == "Free Chlorine":
                results[parameter] = self.analyze_chlorine(value)
            elif parameter == "Alkalinity":
                results[parameter] = self.analyze_alkalinity(value)
            elif parameter == "Hardness":
                results[parameter] = self.analyze_calcium_hardness(value)
            elif parameter == "Cyanuric Acid":
                results[parameter] = self.analyze_cyanuric_acid(value)
            elif parameter == "Salt":
                results[parameter] = self.analyze_salt(value)
            elif parameter == "Bromine":
                results[parameter] = self.analyze_bromine(value)
            else:
                results[parameter] = self._analyze_parameter(parameter, value)

        return results

    def get_safety_warning(self, chemical: str) -> str:
        """
        Returns safety warnings for a specific chemical.

        Args:
            chemical: The name of the chemical

        Returns:
            A string containing safety warnings for the chemical
        """
        return self.chemical_warnings.get(chemical, "No specific safety warnings available for this chemical.")

    def get_supported_parameters(self) -> List[str]:
        """
        Returns a list of supported chemical parameters.

        Returns:
            A list of parameter names that can be analyzed
        """
        return list(self.ideal_levels.keys())
