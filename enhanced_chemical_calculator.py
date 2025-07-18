
#!/usr/bin/env python3
"""
Enhanced Chemical Calculator for Deep Blue Pool Chemistry application.

This module provides enhanced chemical calculation functionality with detailed
recommendations, warnings, precautions, and administration instructions.
"""

import logging
import json
import os
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime

# Configure logger
logger = logging.getLogger(__name__)

class EnhancedChemicalCalculator:
    """
    Enhanced chemical calculator with detailed recommendations and safety information.
    
    This class extends the basic chemical calculator functionality with:
    - Detailed treatment recommendations
    - Safety warnings and precautions
    - Step-by-step administration instructions
    - Historical data tracking and visualization
    
    Attributes:
        db_service: Database service for storing and retrieving data
        chemical_safety_db: Chemical safety database for safety information
    """
    
    def __init__(self, db_service, chemical_safety_db):
        """
        Initialize the enhanced chemical calculator.
        
        Args:
            db_service: Database service instance
            chemical_safety_db: Chemical safety database instance
        """
        self.db_service = db_service
        self.chemical_safety_db = chemical_safety_db
        self.logger = logging.getLogger(__name__)
        self.logger.info("Enhanced Chemical Calculator initialized")
        
        # Load ideal ranges
        self.ideal_ranges = {
            "pH": (7.2, 7.8),
            "free_chlorine": (1.0, 3.0),
            "total_chlorine": (1.0, 3.0),
            "alkalinity": (80, 120),
            "calcium_hardness": (200, 400),
            "cyanuric_acid": (30, 50),
            "temperature": (75, 85)
        }
        
        # Load chemical dosage rates
        self.dosage_rates = {
            "ph_increaser": {
                "chemical": "sodium_bicarbonate",
                "rate": 1.5,  # oz per 0.2 pH increase per 10,000 gallons
                "max_dose": 4.0  # oz per 10,000 gallons per treatment
            },
            "ph_decreaser": {
                "chemical": "muriatic_acid",
                "rate": 1.0,  # oz per 0.2 pH decrease per 10,000 gallons
                "max_dose": 3.0  # oz per 10,000 gallons per treatment
            },
            "alkalinity_increaser": {
                "chemical": "sodium_bicarbonate",
                "rate": 1.5,  # oz per 10 ppm increase per 10,000 gallons
                "max_dose": 8.0  # oz per 10,000 gallons per treatment
            },
            "calcium_increaser": {
                "chemical": "calcium_chloride",
                "rate": 1.25,  # oz per 10 ppm increase per 10,000 gallons
                "max_dose": 6.0  # oz per 10,000 gallons per treatment
            },
            "chlorine": {
                "chemical": "chlorine",
                "rate": 1.0,  # oz per 1 ppm increase per 10,000 gallons
                "max_dose": 4.0  # oz per 10,000 gallons per treatment
            },
            "cyanuric_acid": {
                "chemical": "cyanuric_acid",
                "rate": 1.3,  # oz per 10 ppm increase per 10,000 gallons
                "max_dose": 5.0  # oz per 10,000 gallons per treatment
            }
        }
    
    def calculate_chemicals(self, pool_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate chemical adjustments with enhanced recommendations.
        
        Args:
            pool_data: Dictionary containing pool information and test results
            
        Returns:
            Dictionary containing adjustments, recommendations, warnings, and instructions
        """
        try:
            # Extract pool data
            pool_size = float(pool_data.get("pool_size", "10000"))
            pool_type = pool_data.get("pool_type", "Concrete/Gunite")
            
            # Extract test results
            ph = float(pool_data.get("ph", "7.2"))
            chlorine = float(pool_data.get("chlorine", "1.5"))
            alkalinity = float(pool_data.get("alkalinity", "100"))
            calcium = float(pool_data.get("calcium_hardness", "250"))
            temperature = float(pool_data.get("temperature", "78"))
            cyanuric_acid = float(pool_data.get("cyanuric_acid", "30")) if "cyanuric_acid" in pool_data else 30
            
            # Calculate adjustments
            adjustments = {}
            
            # pH adjustment
            ph_min, ph_max = self.ideal_ranges["pH"]
            if ph < ph_min:
                # Calculate pH increaser amount
                ph_diff = ph_min - ph
                ph_increaser = self._calculate_dosage("ph_increaser", ph_diff * 5, pool_size)
                adjustments["ph_increaser"] = round(ph_increaser, 2)
            elif ph > ph_max:
                # Calculate pH decreaser amount
                ph_diff = ph - ph_max
                ph_decreaser = self._calculate_dosage("ph_decreaser", ph_diff * 5, pool_size)
                adjustments["ph_decreaser"] = round(ph_decreaser, 2)
            
            # Alkalinity adjustment
            alk_min, alk_max = self.ideal_ranges["alkalinity"]
            if alkalinity < alk_min:
                # Calculate alkalinity increaser amount
                alk_diff = alk_min - alkalinity
                alk_increaser = self._calculate_dosage("alkalinity_increaser", alk_diff, pool_size)
                adjustments["alkalinity_increaser"] = round(alk_increaser, 2)
            
            # Calcium adjustment
            cal_min, cal_max = self.ideal_ranges["calcium_hardness"]
            if calcium < cal_min:
                # Calculate calcium increaser amount
                cal_diff = cal_min - calcium
                cal_increaser = self._calculate_dosage("calcium_increaser", cal_diff, pool_size)
                adjustments["calcium_increaser"] = round(cal_increaser, 2)
            
            # Chlorine adjustment
            cl_min, cl_max = self.ideal_ranges["free_chlorine"]
            if chlorine < cl_min:
                # Calculate chlorine amount
                cl_diff = cl_min - chlorine
                cl_amount = self._calculate_dosage("chlorine", cl_diff, pool_size)
                adjustments["chlorine"] = round(cl_amount, 2)
            
            # Cyanuric acid adjustment
            cya_min, cya_max = self.ideal_ranges["cyanuric_acid"]
            if cyanuric_acid < cya_min:
                # Calculate cyanuric acid amount
                cya_diff = cya_min - cyanuric_acid
                cya_amount = self._calculate_dosage("cyanuric_acid", cya_diff, pool_size)
                adjustments["cyanuric_acid"] = round(cya_amount, 2)
            
            # Calculate water balance index
            water_balance = self._calculate_water_balance(ph, alkalinity, calcium, temperature)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(
                ph, chlorine, alkalinity, calcium, cyanuric_acid, temperature, water_balance
            )
            
            # Generate warnings
            warnings = self._generate_warnings(
                ph, chlorine, alkalinity, calcium, cyanuric_acid, temperature, water_balance, adjustments
            )
            
            # Generate precautions
            precautions = self._generate_precautions(adjustments)
            
            # Generate administration instructions
            instructions = self._generate_instructions(adjustments, pool_size, pool_type)
            
            # Create result dictionary
            result = {
                "adjustments": adjustments,
                "water_balance": water_balance,
                "recommendations": recommendations,
                "warnings": warnings,
                "precautions": precautions,
                "instructions": instructions
            }
            
            return result
        except Exception as e:
            self.logger.error(f"Error calculating chemicals: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            return {"error": str(e)}
    
    def _calculate_dosage(self, chemical: str, diff: float, pool_size: float) -> float:
        """
        Calculate chemical dosage based on difference and pool size.
        
        Args:
            chemical: Chemical type
            diff: Difference from ideal range
            pool_size: Pool size in gallons
            
        Returns:
            Dosage in ounces
        """
        if chemical not in self.dosage_rates:
            return 0.0
        
        rate = self.dosage_rates[chemical]["rate"]
        max_dose = self.dosage_rates[chemical]["max_dose"]
        
        # Calculate base dosage
        if chemical in ["ph_increaser", "ph_decreaser"]:
            # pH adjusters use 0.2 pH units as the base
            dosage = (diff / 0.2) * rate * (pool_size / 10000)
        elif chemical in ["alkalinity_increaser", "calcium_increaser", "cyanuric_acid"]:
            # These use 10 ppm as the base
            dosage = (diff / 10) * rate * (pool_size / 10000)
        else:
            # Chlorine uses 1 ppm as the base
            dosage = diff * rate * (pool_size / 10000)
        
        # Limit to maximum dose
        max_total_dose = max_dose * (pool_size / 10000)
        return min(dosage, max_total_dose)
    
    def _calculate_water_balance(self, ph: float, alkalinity: float, calcium: float, temperature: float) -> float:
        """
        Calculate the Langelier Saturation Index (water balance).
        
        Args:
            ph: pH level
            alkalinity: Total alkalinity in ppm
            calcium: Calcium hardness in ppm
            temperature: Water temperature in \u00b0F
            
        Returns:
            Water balance index
        """
        # Calculate temperature factor
        if temperature <= 32:
            temp_factor = 0.0
        elif temperature <= 37:
            temp_factor = 0.1
        elif temperature <= 46:
            temp_factor = 0.2
        elif temperature <= 53:
            temp_factor = 0.3
        elif temperature <= 60:
            temp_factor = 0.4
        elif temperature <= 66:
            temp_factor = 0.5
        elif temperature <= 76:
            temp_factor = 0.6
        elif temperature <= 84:
            temp_factor = 0.7
        elif temperature <= 94:
            temp_factor = 0.8
        elif temperature <= 105:
            temp_factor = 0.9
        else:
            temp_factor = 1.0
        
        # Calculate calcium factor
        if calcium <= 25:
            calcium_factor = 0.0
        elif calcium <= 50:
            calcium_factor = 0.3
        elif calcium <= 75:
            calcium_factor = 0.5
        elif calcium <= 100:
            calcium_factor = 0.6
        elif calcium <= 150:
            calcium_factor = 0.7
        elif calcium <= 200:
            calcium_factor = 0.8
        elif calcium <= 300:
            calcium_factor = 0.9
        elif calcium <= 400:
            calcium_factor = 1.0
        elif calcium <= 800:
            calcium_factor = 1.1
        else:
            calcium_factor = 1.2
        
        # Calculate alkalinity factor
        if alkalinity <= 25:
            alkalinity_factor = 0.7
        elif alkalinity <= 50:
            alkalinity_factor = 1.4
        elif alkalinity <= 75:
            alkalinity_factor = 1.7
        elif alkalinity <= 100:
            alkalinity_factor = 1.9
        elif alkalinity <= 150:
            alkalinity_factor = 2.0
        elif alkalinity <= 200:
            alkalinity_factor = 2.2
        elif alkalinity <= 300:
            alkalinity_factor = 2.5
        else:
            alkalinity_factor = 2.7
        
        # Calculate water balance index
        water_balance = ph - 7.5 + temp_factor + calcium_factor - alkalinity_factor
        
        return round(water_balance, 2)
    
    def _generate_recommendations(self, ph: float, chlorine: float, alkalinity: float, 
                                calcium: float, cyanuric_acid: float, temperature: float,
                                water_balance: float) -> Dict[str, str]:
        """
        Generate recommendations based on test results.
        
        Args:
            ph: pH level
            chlorine: Free chlorine level in ppm
            alkalinity: Total alkalinity in ppm
            calcium: Calcium hardness in ppm
            cyanuric_acid: Cyanuric acid level in ppm
            temperature: Water temperature in \u00b0F
            water_balance: Water balance index
            
        Returns:
            Dictionary of recommendations for each parameter
        """
        recommendations = {}
        
        # pH recommendations
        ph_min, ph_max = self.ideal_ranges["pH"]
        if ph < ph_min:
            recommendations["pH"] = f"pH is too low ({ph}). Add pH increaser to raise pH to {ph_min}-{ph_max}."
        elif ph > ph_max:
            recommendations["pH"] = f"pH is too high ({ph}). Add pH decreaser to lower pH to {ph_min}-{ph_max}."
        else:
            recommendations["pH"] = f"pH is in the ideal range ({ph})."
        
        # Chlorine recommendations
        cl_min, cl_max = self.ideal_ranges["free_chlorine"]
        if chlorine < cl_min:
            recommendations["chlorine"] = f"Chlorine is too low ({chlorine} ppm). Add chlorine to raise level to {cl_min}-{cl_max} ppm."
        elif chlorine > cl_max:
            recommendations["chlorine"] = f"Chlorine is too high ({chlorine} ppm). Stop adding chlorine and wait for levels to decrease to {cl_min}-{cl_max} ppm."
        else:
            recommendations["chlorine"] = f"Chlorine is in the ideal range ({chlorine} ppm)."
        
        # Alkalinity recommendations
        alk_min, alk_max = self.ideal_ranges["alkalinity"]
        if alkalinity < alk_min:
            recommendations["alkalinity"] = f"Alkalinity is too low ({alkalinity} ppm). Add alkalinity increaser to raise level to {alk_min}-{alk_max} ppm."
        elif alkalinity > alk_max:
            recommendations["alkalinity"] = f"Alkalinity is too high ({alkalinity} ppm). Add pH decreaser to lower alkalinity to {alk_min}-{alk_max} ppm."
        else:
            recommendations["alkalinity"] = f"Alkalinity is in the ideal range ({alkalinity} ppm)."
        
        # Calcium recommendations
        cal_min, cal_max = self.ideal_ranges["calcium_hardness"]
        if calcium < cal_min:
            recommendations["calcium"] = f"Calcium hardness is too low ({calcium} ppm). Add calcium hardness increaser to raise level to {cal_min}-{cal_max} ppm."
        elif calcium > cal_max:
            recommendations["calcium"] = f"Calcium hardness is too high ({calcium} ppm). Dilute with fresh water to lower calcium to {cal_min}-{cal_max} ppm."
        else:
            recommendations["calcium"] = f"Calcium hardness is in the ideal range ({calcium} ppm)."
        
        # Cyanuric acid recommendations
        cya_min, cya_max = self.ideal_ranges["cyanuric_acid"]
        if cyanuric_acid < cya_min:
            recommendations["cyanuric_acid"] = f"Cyanuric acid is too low ({cyanuric_acid} ppm). Add cyanuric acid to raise level to {cya_min}-{cya_max} ppm."
        elif cyanuric_acid > cya_max:
            recommendations["cyanuric_acid"] = f"Cyanuric acid is too high ({cyanuric_acid} ppm). Dilute with fresh water to lower cyanuric acid to {cya_min}-{cya_max} ppm."
        else:
            recommendations["cyanuric_acid"] = f"Cyanuric acid is in the ideal range ({cyanuric_acid} ppm)."
        
        # Temperature recommendations
        temp_min, temp_max = self.ideal_ranges["temperature"]
        if temperature < temp_min:
            recommendations["temperature"] = f"Water temperature is low ({temperature}\u00b0F). Consider heating the pool for comfort."
        elif temperature > temp_max:
            recommendations["temperature"] = f"Water temperature is high ({temperature}\u00b0F). Monitor chlorine levels more frequently as higher temperatures increase chlorine consumption."
        else:
            recommendations["temperature"] = f"Water temperature is in the ideal range ({temperature}\u00b0F)."
        
        # Water balance recommendations
        if water_balance < -0.5:
            recommendations["water_balance"] = f"Water is corrosive (LSI: {water_balance}). Adjust pH and alkalinity to balance water."
        elif water_balance > 0.5:
            recommendations["water_balance"] = f"Water is scale-forming (LSI: {water_balance}). Adjust pH and alkalinity to balance water."
        else:
            recommendations["water_balance"] = f"Water is balanced (LSI: {water_balance})."
        
        return recommendations
    
    def _generate_warnings(self, ph: float, chlorine: float, alkalinity: float, 
                         calcium: float, cyanuric_acid: float, temperature: float,
                         water_balance: float, adjustments: Dict[str, float]) -> List[str]:
        """
        Generate warnings based on test results and adjustments.
        
        Args:
            ph: pH level
            chlorine: Free chlorine level in ppm
            alkalinity: Total alkalinity in ppm
            calcium: Calcium hardness in ppm
            cyanuric_acid: Cyanuric acid level in ppm
            temperature: Water temperature in \u00b0F
            water_balance: Water balance index
            adjustments: Dictionary of chemical adjustments
            
        Returns:
            List of warnings
        """
        warnings = []
        
        # Extreme pH warnings
        if ph < 6.8:
            warnings.append("WARNING: Very low pH can cause eye and skin irritation, corrosion of pool equipment, and damage to pool surfaces.")
        elif ph > 8.0:
            warnings.append("WARNING: Very high pH can cause cloudy water, reduced chlorine effectiveness, and scale formation.")
        
        # Extreme chlorine warnings
        if chlorine < 0.5:
            warnings.append("WARNING: Very low chlorine levels can lead to algae growth and unsafe swimming conditions.")
        elif chlorine > 5.0:
            warnings.append("WARNING: Very high chlorine levels can cause eye and skin irritation, bleaching of swimwear, and damage to pool equipment.")
        
        # Extreme alkalinity warnings
        if alkalinity < 60:
            warnings.append("WARNING: Very low alkalinity can cause pH bounce, corrosion, and staining.")
        elif alkalinity > 180:
            warnings.append("WARNING: Very high alkalinity can cause cloudy water, scale formation, and difficulty adjusting pH.")
        
        # Extreme calcium warnings
        if calcium < 150:
            warnings.append("WARNING: Very low calcium hardness can cause etching of plaster and corrosion of metal components.")
        elif calcium > 500:
            warnings.append("WARNING: Very high calcium hardness can cause scale formation, cloudy water, and clogged filters.")
        
        # Extreme cyanuric acid warnings
        if cyanuric_acid > 100:
            warnings.append("WARNING: Very high cyanuric acid levels can reduce chlorine effectiveness and may require partial or complete water replacement.")
        
        # Water balance warnings
        if water_balance < -1.0:
            warnings.append("WARNING: Highly corrosive water can damage pool surfaces and equipment. Address immediately.")
        elif water_balance > 1.0:
            warnings.append("WARNING: Highly scale-forming water can cause deposits and damage to equipment. Address immediately.")
        
        # Chemical addition warnings
        if "ph_increaser" in adjustments and "alkalinity_increaser" in adjustments:
            warnings.append("NOTE: Both pH increaser and alkalinity increaser are recommended. Add alkalinity increaser first, then wait 24 hours before adding pH increaser.")
        
        if "ph_decreaser" in adjustments and adjustments["ph_decreaser"] > 4.0:
            warnings.append("WARNING: Large amount of pH decreaser recommended. Add in multiple smaller doses over several days to avoid over-correction.")
        
        if "chlorine" in adjustments and adjustments["chlorine"] > 5.0:
            warnings.append("WARNING: Large amount of chlorine recommended. Add in multiple smaller doses and retest frequently to avoid over-chlorination.")
        
        return warnings
    
    def _generate_precautions(self, adjustments: Dict[str, float]) -> Dict[str, List[str]]:
        """
        Generate safety precautions for each chemical.
        
        Args:
            adjustments: Dictionary of chemical adjustments
            
        Returns:
            Dictionary of safety precautions for each chemical
        """
        precautions = {}
        
        # Map adjustment types to chemical IDs
        chemical_map = {
            "ph_increaser": "sodium_bicarbonate",
            "ph_decreaser": "muriatic_acid",
            "alkalinity_increaser": "sodium_bicarbonate",
            "calcium_increaser": "calcium_chloride",
            "chlorine": "chlorine",
            "cyanuric_acid": "cyanuric_acid"
        }
        
        # Generate precautions for each chemical
        for adjustment, amount in adjustments.items():
            if adjustment in chemical_map:
                chemical_id = chemical_map[adjustment]
                
                # Get safety info from chemical safety database
                try:
                    safety_info = self.chemical_safety_db.get_chemical_safety_info(chemical_id)
                    if safety_info:
                        precautions[adjustment] = safety_info["safety_precautions"]
                    else:
                        # Default precautions if chemical not found
                        precautions[adjustment] = [
                            "Wear appropriate protective equipment",
                            "Follow manufacturer's instructions",
                            "Keep out of reach of children",
                            "Store in a cool, dry place"
                        ]
                except Exception as e:
                    self.logger.error(f"Error getting safety info for {chemical_id}: {e}")
                    # Default precautions if error occurs
                    precautions[adjustment] = [
                        "Wear appropriate protective equipment",
                        "Follow manufacturer's instructions",
                        "Keep out of reach of children",
                        "Store in a cool, dry place"
                    ]
        
        return precautions
    
    def _generate_instructions(self, adjustments: Dict[str, float], pool_size: float, pool_type: str) -> List[Dict[str, Any]]:
        """
        Generate step-by-step administration instructions.
        
        Args:
            adjustments: Dictionary of chemical adjustments
            pool_size: Pool size in gallons
            pool_type: Type of pool
            
        Returns:
            List of instruction steps
        """
        instructions = []
        
        # Order of chemical additions
        chemical_order = [
            "alkalinity_increaser",
            "ph_decreaser",
            "ph_increaser",
            "calcium_increaser",
            "cyanuric_acid",
            "chlorine"
        ]
        
        # Generate instructions in the correct order
        step_number = 1
        for chemical in chemical_order:
            if chemical in adjustments and adjustments[chemical] > 0:
                # Get chemical name
                chemical_name = chemical.replace("_", " ").title()
                
                # Get amount
                amount = adjustments[chemical]
                
                # Create instruction step
                step = {
                    "step": step_number,
                    "chemical": chemical_name,
                    "amount": f"{amount} oz",
                    "instructions": []
                }
                
                # Add specific instructions based on chemical
                if chemical == "alkalinity_increaser":
                    step["instructions"] = [
                        f"Pre-dissolve {amount} oz of alkalinity increaser in a bucket of water",
                        "Broadcast the solution around the perimeter of the pool",
                        "Run the circulation pump for at least 4 hours",
                        "Wait 24 hours before adding other chemicals or retesting"
                    ]
                elif chemical == "ph_decreaser":
                    step["instructions"] = [
                        f"Dilute {amount} oz of pH decreaser in a bucket of water (always add acid to water, never water to acid)",
                        "Slowly pour the solution around the perimeter of the pool, avoiding the walls and steps",
                        "Run the circulation pump for at least 2 hours",
                        "Wait 4-6 hours before retesting or adding other chemicals"
                    ]
                elif chemical == "ph_increaser":
                    step["instructions"] = [
                        f"Pre-dissolve {amount} oz of pH increaser in a bucket of water",
                        "Broadcast the solution around the perimeter of the pool",
                        "Run the circulation pump for at least 2 hours",
                        "Wait 4-6 hours before retesting or adding other chemicals"
                    ]
                elif chemical == "calcium_increaser":
                    step["instructions"] = [
                        f"Pre-dissolve {amount} oz of calcium increaser in a bucket of water",
                        "Broadcast the solution around the perimeter of the pool",
                        "Run the circulation pump for at least 4 hours",
                        "Wait 24 hours before retesting"
                    ]
                elif chemical == "cyanuric_acid":
                    step["instructions"] = [
                        f"Pre-dissolve {amount} oz of cyanuric acid in a bucket of water",
                        "Slowly pour the solution around the perimeter of the pool",
                        "Run the circulation pump for at least 8 hours",
                        "Wait 24-48 hours before retesting"
                    ]
                elif chemical == "chlorine":
                    step["instructions"] = [
                        f"Add {amount} oz of chlorine according to product instructions",
                        "For liquid chlorine: Dilute with water and pour around the perimeter of the pool",
                        "For granular chlorine: Pre-dissolve in water and broadcast around the pool",
                        "For tablets: Add to skimmer basket or chlorinator",
                        "Run the circulation pump for at least 2 hours",
                        "Wait 4-6 hours before swimming"
                    ]
                
                # Add general instructions based on pool type
                if pool_type == "Vinyl":
                    step["instructions"].append("Note: For vinyl pools, always pre-dissolve chemicals to avoid damage to the liner")
                elif pool_type == "Fiberglass":
                    step["instructions"].append("Note: For fiberglass pools, maintain proper water balance to prevent damage to the gel coat")
                
                # Add the step to instructions
                instructions.append(step)
                step_number += 1
        
        # Add final instructions
        if instructions:
            instructions.append({
                "step": step_number,
                "chemical": "Final Steps",
                "amount": "",
                "instructions": [
                    "Run the circulation pump for at least 8 hours after adding all chemicals",
                    "Retest the water after 24 hours to verify chemical levels",
                    "Adjust chemicals as needed based on new test results",
                    "Keep a log of all chemical additions and test results"
                ]
            })
        
        return instructions
    
    def get_historical_data(self, customer_id: Optional[int] = None, days: int = 30) -> Dict[str, Any]:
        """
        Get historical chemical data for visualization.
        
        Args:
            customer_id: Optional customer ID to filter data
            days: Number of days of history to retrieve
            
        Returns:
            Dictionary containing historical data for visualization
        """
        try:
            # Get readings from database
            if customer_id:
                readings = self.db_service.get_customer_readings(customer_id, limit=100)
            else:
                readings = self.db_service.get_recent_readings(limit=100)
            
            # Filter readings by date
            from datetime import datetime, timedelta
            cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            filtered_readings = [
                reading for reading in readings
                if reading.get("timestamp", "") >= cutoff_date
            ]
            
            # Extract data for visualization
            dates = []
            ph_values = []
            chlorine_values = []
            alkalinity_values = []
            calcium_values = []
            
            for reading in filtered_readings:
                # Parse timestamp
                try:
                    timestamp = datetime.fromisoformat(reading.get("timestamp", ""))
                    date_str = timestamp.strftime("%Y-%m-%d")
                    dates.append(date_str)
                except (ValueError, TypeError):
                    continue
                
                # Extract values
                try:
                    ph_values.append(float(reading.get("pH", 0)))
                except (ValueError, TypeError):
                    ph_values.append(None)
                
                try:
                    chlorine_values.append(float(reading.get("free_chlorine", 0)))
                except (ValueError, TypeError):
                    chlorine_values.append(None)
                
                try:
                    alkalinity_values.append(float(reading.get("alkalinity", 0)))
                except (ValueError, TypeError):
                    alkalinity_values.append(None)
                
                try:
                    calcium_values.append(float(reading.get("calcium", 0)))
                except (ValueError, TypeError):
                    calcium_values.append(None)
            
            # Create result dictionary
            result = {
                "dates": dates,
                "ph_values": ph_values,
                "chlorine_values": chlorine_values,
                "alkalinity_values": alkalinity_values,
                "calcium_values": calcium_values,
                "ideal_ranges": self.ideal_ranges
            }
            
            return result
        except Exception as e:
            self.logger.error(f"Error getting historical data: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            return {"error": str(e)}
    
    def export_data(self, customer_id: Optional[int] = None, format: str = "csv", days: int = 30) -> str:
        """
        Export chemical data to a file.
        
        Args:
            customer_id: Optional customer ID to filter data
            format: Export format (csv or json)
            days: Number of days of history to export
            
        Returns:
            Path to the exported file
        """
        try:
            # Create export directory if it doesn't exist
            export_dir = "data/exports"
            os.makedirs(export_dir, exist_ok=True)
            
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            customer_str = f"_customer_{customer_id}" if customer_id else ""
            filename = f"{export_dir}/pool_data{customer_str}_{timestamp}.{format}"
            
            # Get readings from database
            if customer_id:
                readings = self.db_service.get_customer_readings(customer_id, limit=1000)
                # Get customer info
                customer = self.db_service.get_customer(customer_id)
                customer_name = customer["name"] if customer else f"Customer {customer_id}"
            else:
                readings = self.db_service.get_recent_readings(limit=1000)
                customer_name = "All Customers"
            
            # Filter readings by date
            from datetime import datetime, timedelta
            cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            filtered_readings = [
                reading for reading in readings
                if reading.get("timestamp", "") >= cutoff_date
            ]
            
            # Export data
            if format.lower() == "csv":
                import csv
                
                with open(filename, "w", newline="") as f:
                    # Define CSV headers
                    headers = [
                        "Date", "Time", "Customer", "pH", "Free Chlorine", "Total Chlorine",
                        "Alkalinity", "Calcium", "Cyanuric Acid", "Temperature", "Source"
                    ]
                    
                    writer = csv.writer(f)
                    writer.writerow(headers)
                    
                    # Write data rows
                    for reading in filtered_readings:
                        # Parse timestamp
                        try:
                            timestamp = datetime.fromisoformat(reading.get("timestamp", ""))
                            date_str = timestamp.strftime("%Y-%m-%d")
                            time_str = timestamp.strftime("%H:%M:%S")
                        except (ValueError, TypeError):
                            date_str = "Unknown"
                            time_str = "Unknown"
                        
                        # Write row
                        writer.writerow([
                            date_str,
                            time_str,
                            customer_name,
                            reading.get("pH", ""),
                            reading.get("free_chlorine", ""),
                            reading.get("total_chlorine", ""),
                            reading.get("alkalinity", ""),
                            reading.get("calcium", ""),
                            reading.get("cyanuric_acid", ""),
                            reading.get("temperature", ""),
                            reading.get("source", "")
                        ])
            
            elif format.lower() == "json":
                import json
                
                # Create export data structure
                export_data = {
                    "export_date": datetime.now().isoformat(),
                    "customer": customer_name,
                    "days": days,
                    "readings": filtered_readings
                }
                
                # Write to file
                with open(filename, "w") as f:
                    json.dump(export_data, f, indent=2)
            
            else:
                raise ValueError(f"Unsupported export format: {format}")
            
            self.logger.info(f"Data exported to {filename}")
            return filename
        
        except Exception as e:
            self.logger.error(f"Error exporting data: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            return ""
