
#!/usr/bin/env python3
"""
Chemical Calculator for Deep Blue Pool Chemistry.

This module provides precise chemical dosage calculations based on
pool parameters and test results. It supports all 8 key metrics and
provides detailed recommendations with safety precautions and
step-by-step application instructions.

Features:
- Precise chemical dosage calculations
- Support for all 8 key water chemistry metrics
- Safety warnings and precautions
- Step-by-step application instructions
- Compatibility checks between chemicals
"""

import logging
from typing import Dict, List, Optional, Any, Tuple, Union
from datetime import datetime, timedelta

# Configure logging
logger = logging.getLogger(__name__)

class ChemicalCalculator:
    """
    Chemical calculator for precise pool chemical dosage recommendations.
    
    This class provides methods for calculating exact chemical amounts
    needed to balance pool chemistry, along with safety precautions and
    application instructions.
    
    Attributes:
        pool_volume: Pool volume in gallons
        pool_type: Type of pool (e.g., chlorine, saltwater, bromine)
        chemical_data: Dictionary containing chemical information
    """
    
    # Pool types
    POOL_TYPE_CHLORINE = "chlorine"
    POOL_TYPE_SALTWATER = "saltwater"
    POOL_TYPE_BROMINE = "bromine"
    
    # Ideal ranges for different pool types
    IDEAL_RANGES = {
        POOL_TYPE_CHLORINE: {
            "free_chlorine": (1.0, 3.0),
            "total_chlorine": (1.0, 3.0),
            "ph": (7.4, 7.6),
            "total_alkalinity": (80, 120),
            "calcium_hardness": (200, 400),
            "cyanuric_acid": (30, 50),
            "total_bromine": (0, 0),
            "salt": (0, 1000)
        },
        POOL_TYPE_SALTWATER: {
            "free_chlorine": (1.0, 3.0),
            "total_chlorine": (1.0, 3.0),
            "ph": (7.4, 7.6),
            "total_alkalinity": (80, 120),
            "calcium_hardness": (200, 400),
            "cyanuric_acid": (60, 80),
            "total_bromine": (0, 0),
            "salt": (2500, 3500)
        },
        POOL_TYPE_BROMINE: {
            "free_chlorine": (0, 0),
            "total_chlorine": (0, 0),
            "ph": (7.4, 7.6),
            "total_alkalinity": (80, 120),
            "calcium_hardness": (200, 400),
            "cyanuric_acid": (0, 0),
            "total_bromine": (3.0, 5.0),
            "salt": (0, 1000)
        }
    }
    
    # Chemical information
    CHEMICALS = {
        "liquid_chlorine": {
            "name": "Liquid Chlorine (Sodium Hypochlorite)",
            "concentration": 0.125,  # 12.5% available chlorine
            "unit": "gallon",
            "raises": ["free_chlorine", "total_chlorine"],
            "lowers": [],
            "safety": [
                "Wear chemical-resistant gloves and eye protection",
                "Add to water, never add water to chemical",
                "Do not mix with other chemicals, especially acids",
                "Store in cool, dry place away from direct sunlight",
                "Keep out of reach of children"
            ],
            "application": [
                "Pre-dilute in a bucket of pool water",
                "Pour slowly around the perimeter of the pool",
                "Run the pump for at least 4 hours after adding",
                "Wait at least 4 hours before swimming"
            ],
            "incompatible_with": ["muriatic_acid", "ph_decreaser", "ph_increaser"]
        },
        "chlorine_tablets": {
            "name": "Chlorine Tablets (Trichlor)",
            "concentration": 0.90,  # 90% available chlorine
            "unit": "tablet",
            "weight_oz": 3,  # 3 oz tablets
            "raises": ["free_chlorine", "total_chlorine", "cyanuric_acid"],
            "lowers": ["ph"],
            "safety": [
                "Wear chemical-resistant gloves and eye protection",
                "Do not handle with bare hands",
                "Do not mix with other chemicals",
                "Store in cool, dry place in original container",
                "Keep out of reach of children"
            ],
            "application": [
                "Place tablets in skimmer basket, floater, or automatic feeder",
                "Never throw tablets directly into pool",
                "Add one tablet per 5,000 gallons per week",
                "Run the pump at least 8 hours per day"
            ],
            "incompatible_with": ["muriatic_acid", "ph_decreaser", "ph_increaser"]
        },
        "chlorine_granules": {
            "name": "Chlorine Granules (Dichlor)",
            "concentration": 0.56,  # 56% available chlorine
            "unit": "pound",
            "raises": ["free_chlorine", "total_chlorine", "cyanuric_acid"],
            "lowers": [],
            "safety": [
                "Wear chemical-resistant gloves and eye protection",
                "Do not inhale dust or fumes",
                "Do not mix with other chemicals",
                "Store in cool, dry place in original container",
                "Keep out of reach of children"
            ],
            "application": [
                "Pre-dissolve in a bucket of pool water",
                "Pour slowly around the perimeter of the pool",
                "Run the pump for at least 4 hours after adding",
                "Wait at least 1 hour before swimming"
            ],
            "incompatible_with": ["muriatic_acid", "ph_decreaser", "ph_increaser"]
        },
        "calcium_hypochlorite": {
            "name": "Calcium Hypochlorite (Cal-Hypo)",
            "concentration": 0.65,  # 65% available chlorine
            "unit": "pound",
            "raises": ["free_chlorine", "total_chlorine", "calcium_hardness"],
            "lowers": [],
            "safety": [
                "Wear chemical-resistant gloves and eye protection",
                "Do not inhale dust or fumes",
                "Do not mix with other chemicals",
                "Store in cool, dry place in original container",
                "Keep out of reach of children"
            ],
            "application": [
                "Pre-dissolve in a bucket of pool water",
                "Pour slowly around the perimeter of the pool",
                "Run the pump for at least 4 hours after adding",
                "Wait at least 4 hours before swimming"
            ],
            "incompatible_with": ["muriatic_acid", "ph_decreaser", "ph_increaser"]
        },
        "non_chlorine_shock": {
            "name": "Non-Chlorine Shock (Potassium Monopersulfate)",
            "concentration": 1.0,  # 100% active ingredient
            "unit": "pound",
            "raises": ["total_chlorine"],
            "lowers": [],
            "safety": [
                "Wear chemical-resistant gloves and eye protection",
                "Do not inhale dust or fumes",
                "Do not mix with other chemicals",
                "Store in cool, dry place in original container",
                "Keep out of reach of children"
            ],
            "application": [
                "Pre-dissolve in a bucket of pool water",
                "Pour slowly around the perimeter of the pool",
                "Run the pump for at least 2 hours after adding",
                "Can swim after 15 minutes"
            ],
            "incompatible_with": []
        },
        "muriatic_acid": {
            "name": "Muriatic Acid (Hydrochloric Acid)",
            "concentration": 0.317,  # 31.7% HCl
            "unit": "quart",
            "raises": [],
            "lowers": ["ph", "total_alkalinity"],
            "safety": [
                "DANGER: Highly corrosive",
                "Wear chemical-resistant gloves, eye protection, and protective clothing",
                "Always add acid to water, never water to acid",
                "Do not mix with other chemicals, especially chlorine",
                "Work in well-ventilated area",
                "Keep out of reach of children"
            ],
            "application": [
                "Pre-dilute by adding acid to a 5-gallon bucket of pool water",
                "Pour slowly around the deep end of the pool",
                "Stay away from the area while adding",
                "Run the pump for at least 4 hours after adding",
                "Wait at least 4 hours before swimming"
            ],
            "incompatible_with": ["liquid_chlorine", "chlorine_tablets", "chlorine_granules", "calcium_hypochlorite"]
        },
        "ph_decreaser": {
            "name": "pH Decreaser (Sodium Bisulfate)",
            "concentration": 0.95,  # 95% sodium bisulfate
            "unit": "pound",
            "raises": [],
            "lowers": ["ph"],
            "safety": [
                "Wear chemical-resistant gloves and eye protection",
                "Do not inhale dust or fumes",
                "Do not mix with other chemicals",
                "Store in cool, dry place in original container",
                "Keep out of reach of children"
            ],
            "application": [
                "Pre-dissolve in a bucket of pool water",
                "Pour slowly around the perimeter of the pool",
                "Run the pump for at least 2 hours after adding",
                "Wait at least 1 hour before swimming"
            ],
            "incompatible_with": ["liquid_chlorine", "chlorine_tablets", "chlorine_granules", "calcium_hypochlorite"]
        },
        "ph_increaser": {
            "name": "pH Increaser (Sodium Carbonate)",
            "concentration": 0.99,  # 99% sodium carbonate
            "unit": "pound",
            "raises": ["ph"],
            "lowers": [],
            "safety": [
                "Wear chemical-resistant gloves and eye protection",
                "Do not inhale dust or fumes",
                "Do not mix with other chemicals",
                "Store in cool, dry place in original container",
                "Keep out of reach of children"
            ],
            "application": [
                "Pre-dissolve in a bucket of pool water",
                "Pour slowly around the perimeter of the pool",
                "Run the pump for at least 2 hours after adding",
                "Wait at least 1 hour before swimming"
            ],
            "incompatible_with": ["liquid_chlorine", "chlorine_tablets", "chlorine_granules", "calcium_hypochlorite"]
        },
        "alkalinity_increaser": {
            "name": "Alkalinity Increaser (Sodium Bicarbonate)",
            "concentration": 0.99,  # 99% sodium bicarbonate
            "unit": "pound",
            "raises": ["total_alkalinity"],
            "lowers": [],
            "safety": [
                "Wear chemical-resistant gloves and eye protection",
                "Do not inhale dust or fumes",
                "Store in cool, dry place in original container",
                "Keep out of reach of children"
            ],
            "application": [
                "Pre-dissolve in a bucket of pool water",
                "Pour slowly around the perimeter of the pool",
                "Run the pump for at least 2 hours after adding",
                "Wait at least 1 hour before swimming"
            ],
            "incompatible_with": []
        },
        "calcium_increaser": {
            "name": "Calcium Hardness Increaser (Calcium Chloride)",
            "concentration": 0.99,  # 99% calcium chloride
            "unit": "pound",
            "raises": ["calcium_hardness"],
            "lowers": [],
            "safety": [
                "Wear chemical-resistant gloves and eye protection",
                "Do not inhale dust or fumes",
                "Store in cool, dry place in original container",
                "Keep out of reach of children"
            ],
            "application": [
                "Pre-dissolve in a bucket of pool water",
                "Pour slowly around the perimeter of the pool",
                "Run the pump for at least 2 hours after adding",
                "Wait at least 1 hour before swimming"
            ],
            "incompatible_with": []
        },
        "cyanuric_acid": {
            "name": "Cyanuric Acid (Stabilizer)",
            "concentration": 0.99,  # 99% cyanuric acid
            "unit": "pound",
            "raises": ["cyanuric_acid"],
            "lowers": [],
            "safety": [
                "Wear chemical-resistant gloves and eye protection",
                "Do not inhale dust or fumes",
                "Store in cool, dry place in original container",
                "Keep out of reach of children"
            ],
            "application": [
                "Pre-dissolve in a bucket of warm water (dissolves slowly)",
                "Pour slowly around the perimeter of the pool",
                "Run the pump for at least 24 hours after adding",
                "Wait at least 24 hours before swimming"
            ],
            "incompatible_with": []
        },
        "salt": {
            "name": "Pool Salt (Sodium Chloride)",
            "concentration": 0.99,  # 99% sodium chloride
            "unit": "pound",
            "raises": ["salt"],
            "lowers": [],
            "safety": [
                "Wear gloves to protect hands from abrasion",
                "Store in cool, dry place in original container",
                "Keep out of reach of children"
            ],
            "application": [
                "Broadcast salt evenly across the deep end of the pool",
                "Brush any undissolved salt to prevent staining",
                "Run the pump for at least 24 hours after adding",
                "Wait until salt is fully dissolved before swimming"
            ],
            "incompatible_with": []
        },
        "bromine_tablets": {
            "name": "Bromine Tablets",
            "concentration": 0.98,  # 98% available bromine
            "unit": "tablet",
            "weight_oz": 1,  # 1 oz tablets
            "raises": ["total_bromine"],
            "lowers": [],
            "safety": [
                "Wear chemical-resistant gloves and eye protection",
                "Do not handle with bare hands",
                "Do not mix with other chemicals",
                "Store in cool, dry place in original container",
                "Keep out of reach of children"
            ],
            "application": [
                "Place tablets in floating dispenser or automatic feeder",
                "Never throw tablets directly into pool",
                "Add one tablet per 2,000 gallons per week",
                "Run the pump at least 8 hours per day"
            ],
            "incompatible_with": []
        }
    }
    
    def __init__(
        self,
        pool_volume: float,
        pool_type: str = POOL_TYPE_CHLORINE,
        chemical_data: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize the ChemicalCalculator.
        
        Args:
            pool_volume: Pool volume in gallons.
            pool_type: Type of pool (chlorine, saltwater, bromine).
            chemical_data: Optional dictionary containing chemical information.
                If None, the default CHEMICALS dictionary will be used.
        """
        self.pool_volume = pool_volume
        
        if pool_type not in [self.POOL_TYPE_CHLORINE, self.POOL_TYPE_SALTWATER, self.POOL_TYPE_BROMINE]:
            logger.warning(f"Unknown pool type: {pool_type}. Using chlorine pool type.")
            self.pool_type = self.POOL_TYPE_CHLORINE
        else:
            self.pool_type = pool_type
        
        self.chemical_data = chemical_data or self.CHEMICALS
    
    def get_ideal_ranges(self) -> Dict[str, Tuple[float, float]]:
        """
        Get the ideal ranges for the current pool type.
        
        Returns:
            Dictionary containing ideal ranges for each parameter.
        """
        return self.IDEAL_RANGES[self.pool_type]
    
    def calculate_adjustments(
        self,
        current_levels: Dict[str, float]
    ) -> Dict[str, Dict[str, Any]]:
        """
        Calculate chemical adjustments needed to balance pool chemistry.
        
        Args:
            current_levels: Dictionary containing current levels of each parameter.
                Should include keys: free_chlorine, total_chlorine, ph, total_alkalinity,
                calcium_hardness, cyanuric_acid, total_bromine, salt.
        
        Returns:
            Dictionary containing recommended adjustments for each parameter.
        """
        ideal_ranges = self.get_ideal_ranges()
        adjustments = {}
        
        # Check each parameter
        for param, (min_val, max_val) in ideal_ranges.items():
            if param not in current_levels:
                logger.warning(f"Missing parameter: {param}")
                continue
            
            current = current_levels[param]
            
            if current < min_val:
                # Parameter is too low
                adjustment = {
                    "status": "low",
                    "current": current,
                    "ideal_range": (min_val, max_val),
                    "adjustment_needed": min_val - current,
                    "chemicals": self._get_chemicals_to_raise(param, min_val - current),
                    "warnings": self._get_warnings_for_low(param, current),
                    "priority": self._get_priority(param, current, min_val, max_val)
                }
                adjustments[param] = adjustment
            elif current > max_val:
                # Parameter is too high
                adjustment = {
                    "status": "high",
                    "current": current,
                    "ideal_range": (min_val, max_val),
                    "adjustment_needed": current - max_val,
                    "chemicals": self._get_chemicals_to_lower(param, current - max_val),
                    "warnings": self._get_warnings_for_high(param, current),
                    "priority": self._get_priority(param, current, min_val, max_val)
                }
                adjustments[param] = adjustment
            else:
                # Parameter is in range
                adjustment = {
                    "status": "ok",
                    "current": current,
                    "ideal_range": (min_val, max_val),
                    "adjustment_needed": 0,
                    "chemicals": [],
                    "warnings": [],
                    "priority": 0
                }
                adjustments[param] = adjustment
        
        return adjustments
    
    def _get_chemicals_to_raise(self, param: str, amount: float) -> List[Dict[str, Any]]:
        """
        Get chemicals that can raise a parameter and calculate amounts needed.
        
        Args:
            param: Parameter to raise.
            amount: Amount to raise the parameter by.
            
        Returns:
            List of dictionaries containing chemical recommendations.
        """
        chemicals = []
        
        for chem_id, chem_info in self.chemical_data.items():
            if param in chem_info["raises"]:
                # Calculate amount needed
                if param == "free_chlorine" or param == "total_chlorine":
                    # Calculate pounds of available chlorine needed
                    lbs_needed = (amount * self.pool_volume) / 10000
                    
                    # Convert to amount of product
                    product_amount = lbs_needed / chem_info["concentration"]
                    
                    if "weight_oz" in chem_info:
                        # Convert to number of tablets
                        tablets_needed = (product_amount * 16) / chem_info["weight_oz"]
                        chemicals.append({
                            "id": chem_id,
                            "name": chem_info["name"],
                            "amount": round(tablets_needed, 1),
                            "unit": chem_info["unit"],
                            "safety": chem_info["safety"],
                            "application": chem_info["application"],
                            "raises": chem_info["raises"],
                            "lowers": chem_info["lowers"],
                            "incompatible_with": chem_info["incompatible_with"]
                        })
                    else:
                        # Use the product's unit
                        chemicals.append({
                            "id": chem_id,
                            "name": chem_info["name"],
                            "amount": round(product_amount, 2),
                            "unit": chem_info["unit"],
                            "safety": chem_info["safety"],
                            "application": chem_info["application"],
                            "raises": chem_info["raises"],
                            "lowers": chem_info["lowers"],
                            "incompatible_with": chem_info["incompatible_with"]
                        })
                
                elif param == "total_bromine":
                    # Calculate pounds of available bromine needed
                    lbs_needed = (amount * self.pool_volume) / 10000
                    
                    # Convert to amount of product
                    product_amount = lbs_needed / chem_info["concentration"]
                    
                    if "weight_oz" in chem_info:
                        # Convert to number of tablets
                        tablets_needed = (product_amount * 16) / chem_info["weight_oz"]
                        chemicals.append({
                            "id": chem_id,
                            "name": chem_info["name"],
                            "amount": round(tablets_needed, 1),
                            "unit": chem_info["unit"],
                            "safety": chem_info["safety"],
                            "application": chem_info["application"],
                            "raises": chem_info["raises"],
                            "lowers": chem_info["lowers"],
                            "incompatible_with": chem_info["incompatible_with"]
                        })
                    else:
                        # Use the product's unit
                        chemicals.append({
                            "id": chem_id,
                            "name": chem_info["name"],
                            "amount": round(product_amount, 2),
                            "unit": chem_info["unit"],
                            "safety": chem_info["safety"],
                            "application": chem_info["application"],
                            "raises": chem_info["raises"],
                            "lowers": chem_info["lowers"],
                            "incompatible_with": chem_info["incompatible_with"]
                        })
                
                elif param == "ph":
                    # pH increaser (sodium carbonate)
                    # 6 oz per 10,000 gallons raises pH by approximately 0.2
                    oz_needed = (amount / 0.2) * (self.pool_volume / 10000) * 6
                    lbs_needed = oz_needed / 16
                    
                    chemicals.append({
                        "id": chem_id,
                        "name": chem_info["name"],
                        "amount": round(lbs_needed, 2),
                        "unit": chem_info["unit"],
                        "safety": chem_info["safety"],
                        "application": chem_info["application"],
                        "raises": chem_info["raises"],
                        "lowers": chem_info["lowers"],
                        "incompatible_with": chem_info["incompatible_with"]
                    })
                
                elif param == "total_alkalinity":
                    # Alkalinity increaser (sodium bicarbonate)
                    # 1.5 lbs per 10,000 gallons raises alkalinity by approximately 10 ppm
                    lbs_needed = (amount / 10) * (self.pool_volume / 10000) * 1.5
                    
                    chemicals.append({
                        "id": chem_id,
                        "name": chem_info["name"],
                        "amount": round(lbs_needed, 2),
                        "unit": chem_info["unit"],
                        "safety": chem_info["safety"],
                        "application": chem_info["application"],
                        "raises": chem_info["raises"],
                        "lowers": chem_info["lowers"],
                        "incompatible_with": chem_info["incompatible_with"]
                    })
                
                elif param == "calcium_hardness":
                    # Calcium hardness increaser (calcium chloride)
                    # 1 lb per 10,000 gallons raises calcium hardness by approximately 10 ppm
                    lbs_needed = (amount / 10) * (self.pool_volume / 10000)
                    
                    chemicals.append({
                        "id": chem_id,
                        "name": chem_info["name"],
                        "amount": round(lbs_needed, 2),
                        "unit": chem_info["unit"],
                        "safety": chem_info["safety"],
                        "application": chem_info["application"],
                        "raises": chem_info["raises"],
                        "lowers": chem_info["lowers"],
                        "incompatible_with": chem_info["incompatible_with"]
                    })
                
                elif param == "cyanuric_acid":
                    # Cyanuric acid
                    # 1 lb per 10,000 gallons raises cyanuric acid by approximately 10 ppm
                    lbs_needed = (amount / 10) * (self.pool_volume / 10000)
                    
                    chemicals.append({
                        "id": chem_id,
                        "name": chem_info["name"],
                        "amount": round(lbs_needed, 2),
                        "unit": chem_info["unit"],
                        "safety": chem_info["safety"],
                        "application": chem_info["application"],
                        "raises": chem_info["raises"],
                        "lowers": chem_info["lowers"],
                        "incompatible_with": chem_info["incompatible_with"]
                    })
                
                elif param == "salt":
                    # Salt
                    # 1 lb per 100 gallons raises salt by approximately 12 ppm
                    lbs_needed = (amount / 12) * (self.pool_volume / 100)
                    
                    chemicals.append({
                        "id": chem_id,
                        "name": chem_info["name"],
                        "amount": round(lbs_needed, 0),
                        "unit": chem_info["unit"],
                        "safety": chem_info["safety"],
                        "application": chem_info["application"],
                        "raises": chem_info["raises"],
                        "lowers": chem_info["lowers"],
                        "incompatible_with": chem_info["incompatible_with"]
                    })
        
        return chemicals
    
    def _get_chemicals_to_lower(self, param: str, amount: float) -> List[Dict[str, Any]]:
        """
        Get chemicals that can lower a parameter and calculate amounts needed.
        
        Args:
            param: Parameter to lower.
            amount: Amount to lower the parameter by.
            
        Returns:
            List of dictionaries containing chemical recommendations.
        """
        chemicals = []
        
        for chem_id, chem_info in self.chemical_data.items():
            if param in chem_info["lowers"]:
                # Calculate amount needed
                if param == "ph":
                    # pH decreaser (sodium bisulfate)
                    # 6 oz per 10,000 gallons lowers pH by approximately 0.2
                    oz_needed = (amount / 0.2) * (self.pool_volume / 10000) * 6
                    lbs_needed = oz_needed / 16
                    
                    chemicals.append({
                        "id": chem_id,
                        "name": chem_info["name"],
                        "amount": round(lbs_needed, 2),
                        "unit": chem_info["unit"],
                        "safety": chem_info["safety"],
                        "application": chem_info["application"],
                        "raises": chem_info["raises"],
                        "lowers": chem_info["lowers"],
                        "incompatible_with": chem_info["incompatible_with"]
                    })
                
                elif param == "total_alkalinity":
                    # Muriatic acid
                    # 1 quart per 10,000 gallons lowers alkalinity by approximately 10 ppm
                    quarts_needed = (amount / 10) * (self.pool_volume / 10000)
                    
                    chemicals.append({
                        "id": chem_id,
                        "name": chem_info["name"],
                        "amount": round(quarts_needed, 2),
                        "unit": chem_info["unit"],
                        "safety": chem_info["safety"],
                        "application": chem_info["application"],
                        "raises": chem_info["raises"],
                        "lowers": chem_info["lowers"],
                        "incompatible_with": chem_info["incompatible_with"]
                    })
        
        # Special case for parameters that can't be directly lowered
        if param == "free_chlorine" or param == "total_chlorine":
            chemicals.append({
                "id": "natural_dissipation",
                "name": "Natural Dissipation",
                "amount": 0,
                "unit": "none",
                "safety": [],
                "application": [
                    "Turn off chlorine generator or feeder",
                    "Remove chlorine tablets from dispensers",
                    "Keep the pool uncovered and exposed to sunlight",
                    "Run the pump to accelerate dissipation",
                    "Test chlorine levels daily until they return to normal"
                ],
                "raises": [],
                "lowers": ["free_chlorine", "total_chlorine"],
                "incompatible_with": []
            })
        
        elif param == "calcium_hardness":
            chemicals.append({
                "id": "partial_drain",
                "name": "Partial Drain and Refill",
                "amount": round(self.pool_volume * 0.25),  # 25% water replacement
                "unit": "gallon",
                "safety": [],
                "application": [
                    "Drain approximately 25% of the pool water",
                    "Refill with fresh water that has lower calcium hardness",
                    "Balance other chemicals after refilling",
                    "Repeat if necessary until calcium hardness is in range"
                ],
                "raises": [],
                "lowers": ["calcium_hardness", "cyanuric_acid", "salt"],
                "incompatible_with": []
            })
        
        elif param == "cyanuric_acid":
            chemicals.append({
                "id": "partial_drain",
                "name": "Partial Drain and Refill",
                "amount": round(self.pool_volume * 0.25),  # 25% water replacement
                "unit": "gallon",
                "safety": [],
                "application": [
                    "Drain approximately 25% of the pool water",
                    "Refill with fresh water",
                    "Balance other chemicals after refilling",
                    "Repeat if necessary until cyanuric acid is in range"
                ],
                "raises": [],
                "lowers": ["cyanuric_acid", "calcium_hardness", "salt"],
                "incompatible_with": []
            })
        
        elif param == "salt":
            chemicals.append({
                "id": "partial_drain",
                "name": "Partial Drain and Refill",
                "amount": round(self.pool_volume * 0.25),  # 25% water replacement
                "unit": "gallon",
                "safety": [],
                "application": [
                    "Drain approximately 25% of the pool water",
                    "Refill with fresh water",
                    "Balance other chemicals after refilling",
                    "Repeat if necessary until salt level is in range"
                ],
                "raises": [],
                "lowers": ["salt", "calcium_hardness", "cyanuric_acid"],
                "incompatible_with": []
            })
        
        elif param == "total_bromine":
            chemicals.append({
                "id": "natural_dissipation",
                "name": "Natural Dissipation",
                "amount": 0,
                "unit": "none",
                "safety": [],
                "application": [
                    "Remove bromine tablets from dispensers",
                    "Keep the pool uncovered and exposed to sunlight",
                    "Run the pump to accelerate dissipation",
                    "Test bromine levels daily until they return to normal"
                ],
                "raises": [],
                "lowers": ["total_bromine"],
                "incompatible_with": []
            })
        
        return chemicals
    
    def _get_warnings_for_low(self, param: str, current: float) -> List[str]:
        """
        Get warnings for low parameter levels.
        
        Args:
            param: Parameter that is low.
            current: Current level of the parameter.
            
        Returns:
            List of warning messages.
        """
        warnings = []
        
        if param == "free_chlorine":
            warnings.append(
                f"Low free chlorine ({current} ppm) may lead to algae growth and cloudy water."
            )
            warnings.append(
                "Bacteria and other pathogens may thrive in water with insufficient chlorine."
            )
            if current < 0.5:
                warnings.append(
                    "HEALTH HAZARD: Extremely low chlorine levels. Do not swim until corrected."
                )
        
        elif param == "total_chlorine":
            warnings.append(
                f"Low total chlorine ({current} ppm) indicates insufficient sanitizer in the water."
            )
        
        elif param == "ph":
            warnings.append(
                f"Low pH ({current}) can cause eye and skin irritation."
            )
            warnings.append(
                "Low pH can damage pool equipment and surfaces through corrosion."
            )
            warnings.append(
                "Low pH causes chlorine to dissipate more quickly, reducing effectiveness."
            )
            if current < 7.0:
                warnings.append(
                    "EQUIPMENT RISK: pH below 7.0 can cause serious damage to pool equipment."
                )
        
        elif param == "total_alkalinity":
            warnings.append(
                f"Low total alkalinity ({current} ppm) can cause pH to fluctuate rapidly."
            )
            warnings.append(
                "Low alkalinity can lead to corrosion of pool surfaces and equipment."
            )
        
        elif param == "calcium_hardness":
            warnings.append(
                f"Low calcium hardness ({current} ppm) can cause etching of plaster and grout."
            )
            warnings.append(
                "Low calcium hardness can lead to corrosion of metal components."
            )
            if current < 150:
                warnings.append(
                    "SURFACE RISK: Calcium hardness below 150 ppm can damage pool surfaces."
                )
        
        elif param == "cyanuric_acid":
            if self.pool_type == self.POOL_TYPE_CHLORINE:
                warnings.append(
                    f"Low cyanuric acid ({current} ppm) provides insufficient protection for chlorine against UV rays."
                )
                warnings.append(
                    "Chlorine will dissipate quickly in sunlight without adequate cyanuric acid."
                )
        
        elif param == "salt" and self.pool_type == self.POOL_TYPE_SALTWATER:
            warnings.append(
                f"Low salt level ({current} ppm) may prevent chlorine generator from functioning properly."
            )
            warnings.append(
                "Check salt cell and generator for proper operation."
            )
        
        elif param == "total_bromine" and self.pool_type == self.POOL_TYPE_BROMINE:
            warnings.append(
                f"Low bromine level ({current} ppm) provides insufficient sanitization."
            )
            warnings.append(
                "Bacteria and other pathogens may thrive in water with insufficient bromine."
            )
            if current < 1.0:
                warnings.append(
                    "HEALTH HAZARD: Extremely low bromine levels. Do not swim until corrected."
                )
        
        return warnings
    
    def _get_warnings_for_high(self, param: str, current: float) -> List[str]:
        """
        Get warnings for high parameter levels.
        
        Args:
            param: Parameter that is high.
            current: Current level of the parameter.
            
        Returns:
            List of warning messages.
        """
        warnings = []
        
        if param == "free_chlorine":
            warnings.append(
                f"High free chlorine ({current} ppm) can cause eye and skin irritation."
            )
            warnings.append(
                "High chlorine levels can bleach swimwear and pool liners."
            )
            if current > 5.0:
                warnings.append(
                    "HEALTH HAZARD: Chlorine levels above 5.0 ppm. Do not swim until levels decrease."
                )
        
        elif param == "total_chlorine":
            combined_chlorine = current - self._get_free_chlorine_from_total(current)
            if combined_chlorine > 0.5:
                warnings.append(
                    f"High combined chlorine ({combined_chlorine:.1f} ppm) indicates presence of chloramines."
                )
                warnings.append(
                    "Chloramines cause strong chlorine odor and eye irritation."
                )
                warnings.append(
                    "Shock treatment recommended to eliminate chloramines."
                )
        
        elif param == "ph":
            warnings.append(
                f"High pH ({current}) can cause cloudy water and reduced chlorine effectiveness."
            )
            warnings.append(
                "High pH can cause scale formation on pool surfaces and equipment."
            )
            if current > 8.0:
                warnings.append(
                    "SANITIZER RISK: pH above 8.0 significantly reduces chlorine effectiveness."
                )
        
        elif param == "total_alkalinity":
            warnings.append(
                f"High total alkalinity ({current} ppm) can make pH adjustment difficult."
            )
            warnings.append(
                "High alkalinity can contribute to cloudy water and scale formation."
            )
        
        elif param == "calcium_hardness":
            warnings.append(
                f"High calcium hardness ({current} ppm) can cause scale formation on surfaces and equipment."
            )
            warnings.append(
                "High calcium hardness can contribute to cloudy water."
            )
            if current > 500:
                warnings.append(
                    "EQUIPMENT RISK: Calcium hardness above 500 ppm can cause severe scaling."
                )
        
        elif param == "cyanuric_acid":
            warnings.append(
                f"High cyanuric acid ({current} ppm) can reduce chlorine effectiveness."
            )
            if current > 100:
                warnings.append(
                    "SANITIZER RISK: Cyanuric acid above 100 ppm significantly locks up chlorine, "
                    "reducing its ability to sanitize (chlorine lock)."
                )
                warnings.append(
                    "Partial drain and refill is the only way to reduce cyanuric acid levels."
                )
        
        elif param == "salt" and self.pool_type == self.POOL_TYPE_SALTWATER:
            warnings.append(
                f"High salt level ({current} ppm) can damage pool equipment and surfaces."
            )
            if current > 4000:
                warnings.append(
                    "EQUIPMENT RISK: Salt levels above 4000 ppm can damage salt cell and other equipment."
                )
        
        elif param == "total_bromine" and self.pool_type == self.POOL_TYPE_BROMINE:
            warnings.append(
                f"High bromine level ({current} ppm) can cause skin and eye irritation."
            )
            if current > 10.0:
                warnings.append(
                    "HEALTH HAZARD: Bromine levels above 10.0 ppm. Do not swim until levels decrease."
                )
        
        return warnings
    
    def _get_priority(self, param: str, current: float, min_val: float, max_val: float) -> int:
        """
        Get priority level for a parameter adjustment.
        
        Args:
            param: Parameter to adjust.
            current: Current level of the parameter.
            min_val: Minimum acceptable value.
            max_val: Maximum acceptable value.
            
        Returns:
            Priority level (0-10, where 10 is highest priority).
        """
        # Parameters in order of adjustment priority
        priority_order = [
            "ph",
            "total_alkalinity",
            "calcium_hardness",
            "cyanuric_acid",
            "free_chlorine",
            "total_chlorine",
            "salt",
            "total_bromine"
        ]
        
        # Base priority based on parameter type
        base_priority = 10 - priority_order.index(param) if param in priority_order else 5
        
        # Calculate how far out of range the parameter is
        if current < min_val:
            percent_off = (min_val - current) / min_val * 100
        elif current > max_val:
            percent_off = (current - max_val) / max_val * 100
        else:
            percent_off = 0
        
        # Adjust priority based on how far out of range
        if percent_off > 50:
            priority_adjustment = 3
        elif percent_off > 25:
            priority_adjustment = 2
        elif percent_off > 10:
            priority_adjustment = 1
        else:
            priority_adjustment = 0
        
        # Special cases for critical parameters
        if param == "ph" and (current < 7.0 or current > 8.0):
            priority_adjustment += 2
        
        if param == "free_chlorine" and current < 0.5:
            priority_adjustment += 3
        
        if param == "total_bromine" and self.pool_type == self.POOL_TYPE_BROMINE and current < 1.0:
            priority_adjustment += 3
        
        return min(10, base_priority + priority_adjustment)
    
    def _get_free_chlorine_from_total(self, total_chlorine: float) -> float:
        """
        Estimate free chlorine based on total chlorine.
        
        Args:
            total_chlorine: Total chlorine level.
            
        Returns:
            Estimated free chlorine level.
        """
        # This is a rough estimate - in reality, you would need both measurements
        return max(0, total_chlorine - 0.5)
    
    def get_adjustment_plan(
        self,
        adjustments: Dict[str, Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Create a step-by-step adjustment plan based on calculated adjustments.
        
        Args:
            adjustments: Dictionary containing recommended adjustments for each parameter.
                Output from calculate_adjustments().
        
        Returns:
            List of steps to follow in order of priority.
        """
        # Sort adjustments by priority
        sorted_params = sorted(
            [param for param, adj in adjustments.items() if adj["status"] != "ok"],
            key=lambda p: adjustments[p]["priority"],
            reverse=True
        )
        
        plan = []
        
        # Add steps for each parameter that needs adjustment
        for param in sorted_params:
            adj = adjustments[param]
            
            # Skip parameters that are in range
            if adj["status"] == "ok":
                continue
            
            # Create a step for this parameter
            step = {
                "parameter": param,
                "status": adj["status"],
                "current": adj["current"],
                "ideal_range": adj["ideal_range"],
                "adjustment_needed": adj["adjustment_needed"],
                "priority": adj["priority"],
                "warnings": adj["warnings"],
                "chemicals": adj["chemicals"],
                "instructions": self._get_instructions_for_parameter(param, adj)
            }
            
            plan.append(step)
        
        return plan
    
    def _get_instructions_for_parameter(
        self,
        param: str,
        adjustment: Dict[str, Any]
    ) -> List[str]:
        """
        Get detailed instructions for adjusting a parameter.
        
        Args:
            param: Parameter to adjust.
            adjustment: Adjustment information for the parameter.
            
        Returns:
            List of instruction steps.
        """
        instructions = []
        
        # Add parameter-specific instructions
        if param == "ph":
            if adjustment["status"] == "low":
                instructions.append(
                    f"Increase pH from {adjustment['current']} to {adjustment['ideal_range'][0]}-{adjustment['ideal_range'][1]}."
                )
                instructions.append(
                    "Adjust pH first before making other chemical adjustments."
                )
                instructions.append(
                    "Test pH again 4 hours after adjustment."
                )
            else:  # high
                instructions.append(
                    f"Decrease pH from {adjustment['current']} to {adjustment['ideal_range'][0]}-{adjustment['ideal_range'][1]}."
                )
                instructions.append(
                    "Adjust pH first before making other chemical adjustments."
                )
                instructions.append(
                    "Test pH again 4 hours after adjustment."
                )
        
        elif param == "total_alkalinity":
            if adjustment["status"] == "low":
                instructions.append(
                    f"Increase total alkalinity from {adjustment['current']} ppm to {adjustment['ideal_range'][0]}-{adjustment['ideal_range'][1]} ppm."
                )
                instructions.append(
                    "Adjust total alkalinity before adjusting calcium hardness."
                )
                instructions.append(
                    "Test total alkalinity again 24 hours after adjustment."
                )
            else:  # high
                instructions.append(
                    f"Decrease total alkalinity from {adjustment['current']} ppm to {adjustment['ideal_range'][0]}-{adjustment['ideal_range'][1]} ppm."
                )
                instructions.append(
                    "Lower total alkalinity gradually to avoid large pH fluctuations."
                )
                instructions.append(
                    "Test total alkalinity again 24 hours after adjustment."
                )
        
        elif param == "free_chlorine":
            if adjustment["status"] == "low":
                instructions.append(
                    f"Increase free chlorine from {adjustment['current']} ppm to {adjustment['ideal_range'][0]}-{adjustment['ideal_range'][1]} ppm."
                )
                instructions.append(
                    "Ensure pH is in range before adding chlorine for maximum effectiveness."
                )
                instructions.append(
                    "Test free chlorine again 4 hours after adjustment."
                )
            else:  # high
                instructions.append(
                    f"Decrease free chlorine from {adjustment['current']} ppm to {adjustment['ideal_range'][0]}-{adjustment['ideal_range'][1]} ppm."
                )
                instructions.append(
                    "Do not swim until chlorine levels return to safe range."
                )
                instructions.append(
                    "Test free chlorine daily until levels return to normal."
                )
        
        elif param == "calcium_hardness":
            if adjustment["status"] == "low":
                instructions.append(
                    f"Increase calcium hardness from {adjustment['current']} ppm to {adjustment['ideal_range'][0]}-{adjustment['ideal_range'][1]} ppm."
                )
                instructions.append(
                    "Adjust calcium hardness after pH and alkalinity are in range."
                )
                instructions.append(
                    "Test calcium hardness again 24 hours after adjustment."
                )
            else:  # high
                instructions.append(
                    f"Decrease calcium hardness from {adjustment['current']} ppm to {adjustment['ideal_range'][0]}-{adjustment['ideal_range'][1]} ppm."
                )
                instructions.append(
                    "Partial drain and refill is the only effective way to reduce calcium hardness."
                )
                instructions.append(
                    "Test calcium hardness again after refilling."
                )
        
        elif param == "cyanuric_acid":
            if adjustment["status"] == "low":
                instructions.append(
                    f"Increase cyanuric acid from {adjustment['current']} ppm to {adjustment['ideal_range'][0]}-{adjustment['ideal_range'][1]} ppm."
                )
                instructions.append(
                    "Cyanuric acid dissolves very slowly. Broadcast directly into the pool or pre-dissolve in hot water."
                )
                instructions.append(
                    "Test cyanuric acid again 24-48 hours after adjustment."
                )
            else:  # high
                instructions.append(
                    f"Decrease cyanuric acid from {adjustment['current']} ppm to {adjustment['ideal_range'][0]}-{adjustment['ideal_range'][1]} ppm."
                )
                instructions.append(
                    "Partial drain and refill is the only effective way to reduce cyanuric acid."
                )
                instructions.append(
                    "Test cyanuric acid again after refilling."
                )
        
        elif param == "salt" and self.pool_type == self.POOL_TYPE_SALTWATER:
            if adjustment["status"] == "low":
                instructions.append(
                    f"Increase salt level from {adjustment['current']} ppm to {adjustment['ideal_range'][0]}-{adjustment['ideal_range'][1]} ppm."
                )
                instructions.append(
                    "Broadcast salt across the deep end of the pool and brush to distribute."
                )
                instructions.append(
                    "Run the pump continuously for 24 hours after adding salt."
                )
                instructions.append(
                    "Test salt level again 24 hours after adjustment."
                )
            else:  # high
                instructions.append(
                    f"Decrease salt level from {adjustment['current']} ppm to {adjustment['ideal_range'][0]}-{adjustment['ideal_range'][1]} ppm."
                )
                instructions.append(
                    "Partial drain and refill is the only effective way to reduce salt level."
                )
                instructions.append(
                    "Test salt level again after refilling."
                )
        
        elif param == "total_bromine" and self.pool_type == self.POOL_TYPE_BROMINE:
            if adjustment["status"] == "low":
                instructions.append(
                    f"Increase bromine level from {adjustment['current']} ppm to {adjustment['ideal_range'][0]}-{adjustment['ideal_range'][1]} ppm."
                )
                instructions.append(
                    "Ensure pH is in range before adding bromine for maximum effectiveness."
                )
                instructions.append(
                    "Test bromine again 4 hours after adjustment."
                )
            else:  # high
                instructions.append(
                    f"Decrease bromine level from {adjustment['current']} ppm to {adjustment['ideal_range'][0]}-{adjustment['ideal_range'][1]} ppm."
                )
                instructions.append(
                    "Do not swim until bromine levels return to safe range."
                )
                instructions.append(
                    "Test bromine daily until levels return to normal."
                )
        
        return instructions
    
    def check_chemical_compatibility(
        self,
        chemicals: List[str]
    ) -> Dict[str, List[str]]:
        """
        Check compatibility between multiple chemicals.
        
        Args:
            chemicals: List of chemical IDs to check.
            
        Returns:
            Dictionary of incompatible chemical pairs.
        """
        incompatibilities = {}
        
        # Check each pair of chemicals
        for i, chem1 in enumerate(chemicals):
            if chem1 not in self.chemical_data:
                continue
                
            for chem2 in chemicals[i+1:]:
                if chem2 not in self.chemical_data:
                    continue
                    
                # Check if either chemical lists the other as incompatible
                if chem2 in self.chemical_data[chem1]["incompatible_with"] or \
                   chem1 in self.chemical_data[chem2]["incompatible_with"]:
                    
                    if chem1 not in incompatibilities:
                        incompatibilities[chem1] = []
                    
                    incompatibilities[chem1].append(chem2)
        
        return incompatibilities
    
    def get_sequential_addition_plan(
        self,
        adjustment_plan: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Create a sequential plan for adding chemicals safely.
        
        Args:
            adjustment_plan: List of adjustment steps from get_adjustment_plan().
            
        Returns:
            List of chemical addition steps with timing information.
        """
        sequential_plan = []
        current_time = datetime.now()
        
        for step in adjustment_plan:
            # Skip steps with no chemicals
            if not step["chemicals"]:
                continue
            
            for chemical in step["chemicals"]:
                # Skip non-chemical solutions like "natural dissipation"
                if chemical["id"] == "natural_dissipation" or chemical["id"] == "partial_drain":
                    sequential_plan.append({
                        "time": current_time.strftime("%I:%M %p"),
                        "parameter": step["parameter"],
                        "chemical": chemical["name"],
                        "amount": chemical["amount"],
                        "unit": chemical["unit"],
                        "instructions": chemical["application"],
                        "safety": chemical["safety"],
                        "wait_time": 0  # No waiting time for these actions
                    })
                    continue
                
                # Add this chemical to the plan
                sequential_plan.append({
                    "time": current_time.strftime("%I:%M %p"),
                    "parameter": step["parameter"],
                    "chemical": chemical["name"],
                    "amount": chemical["amount"],
                    "unit": chemical["unit"],
                    "instructions": chemical["application"],
                    "safety": chemical["safety"],
                    "wait_time": self._get_wait_time(chemical["id"])
                })
                
                # Update the time for the next chemical
                current_time += timedelta(hours=self._get_wait_time(chemical["id"]))
        
        return sequential_plan
    
    def _get_wait_time(self, chemical_id: str) -> int:
        """
        Get the recommended wait time between adding different chemicals.
        
        Args:
            chemical_id: ID of the chemical being added.
            
        Returns:
            Recommended wait time in hours.
        """
        # Define wait times for different chemical types
        wait_times = {
            "liquid_chlorine": 4,
            "chlorine_tablets": 4,
            "chlorine_granules": 4,
            "calcium_hypochlorite": 4,
            "non_chlorine_shock": 1,
            "muriatic_acid": 4,
            "ph_decreaser": 4,
            "ph_increaser": 4,
            "alkalinity_increaser": 6,
            "calcium_increaser": 6,
            "cyanuric_acid": 24,
            "salt": 24,
            "bromine_tablets": 4
        }
        
        return wait_times.get(chemical_id, 4)  # Default to 4 hours if not specified
