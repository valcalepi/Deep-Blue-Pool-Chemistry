# modules/business_logic.py
"""
Business Logic Module
Contains core business logic for the Pool Chemistry Manager
"""

import logging
from datetime import datetime

class ChemicalCalculator:
    """Chemical calculator for pool chemistry management"""
    
    def __init__(self, config):
        """Initialize the chemical calculator"""
        self.logger = logging.getLogger(__name__)
        self.config = config
    
    def calculate_chemical_recommendations(self, pool_size, current, target):
        """Calculate chemical recommendations based on current and target values"""
        try:
            recommendations = []
            recommendations.append("CHEMICAL ADDITION RECOMMENDATIONS")
            recommendations.append("=" * 50)
            recommendations.append(f"Pool Size: {pool_size:,.0f} gallons")
            recommendations.append("")
            
            # pH adjustment
            ph_diff = target.get('ph', 0) - current.get('ph', 0)
            if abs(ph_diff) > 0.1:
                if ph_diff > 0:
                    # Need to raise pH
                    chemical = self.config["chemicals"]["ph_increaser"]
                    amount = abs(ph_diff) * pool_size * 0.00013  # Rough calculation
                    recommendations.append(f"pH ADJUSTMENT (Current: {current.get('ph', 0):.1f}, Target: {target.get('ph', 0):.1f})")
                    recommendations.append(f"Add {amount:.1f} lbs of {chemical}")
                    recommendations.append("Wait 4 hours before retesting")
                else:
                    # Need to lower pH
                    chemical = self.config["chemicals"]["ph_decreaser"]
                    amount = abs(ph_diff) * pool_size * 0.00008  # Rough calculation
                    recommendations.append(f"pH ADJUSTMENT (Current: {current.get('ph', 0):.1f}, Target: {target.get('ph', 0):.1f})")
                    recommendations.append(f"Add {amount:.1f} lbs of {chemical}")
                    recommendations.append("Wait 4 hours before retesting")
            else:
                recommendations.append("pH: No adjustment needed")
            
            recommendations.append("")
            
            # Chlorine adjustment
            cl_diff = target.get('chlorine', 0) - current.get('chlorine', 0)
            if abs(cl_diff) > 0.2:
                if cl_diff > 0:
                    chemical = self.config["chemicals"]["chlorine_type"]
                    if "Liquid" in chemical:
                        amount = cl_diff * pool_size * 0.00013  # gallons
                        recommendations.append(f"CHLORINE ADJUSTMENT (Current: {current.get('chlorine', 0):.1f} ppm, Target: {target.get('chlorine', 0):.1f} ppm)")
                        recommendations.append(f"Add {amount:.2f} gallons of {chemical}")
                    else:
                        amount = cl_diff * pool_size * 0.00002  # lbs
                        recommendations.append(f"CHLORINE ADJUSTMENT (Current: {current.get('chlorine', 0):.1f} ppm, Target: {target.get('chlorine', 0):.1f} ppm)")
                        recommendations.append(f"Add {amount:.2f} lbs of {chemical}")
                    recommendations.append("Wait 2 hours before retesting")
            else:
                recommendations.append("Chlorine: No adjustment needed")
            
            recommendations.append("")
            
            # Alkalinity adjustment
            alk_diff = target.get('alkalinity', 0) - current.get('alkalinity', 0)
            if abs(alk_diff) > 10:
                if alk_diff > 0:
                    chemical = self.config["chemicals"]["alkalinity_increaser"]
                    amount = alk_diff * pool_size * 0.0000125  # lbs
                    recommendations.append(f"ALKALINITY ADJUSTMENT (Current: {current.get('alkalinity', 0):.0f} ppm, Target: {target.get('alkalinity', 0):.0f} ppm)")
                    recommendations.append(f"Add {amount:.1f} lbs of {chemical}")
                    recommendations.append("Wait 6 hours before retesting")
            else:
                recommendations.append("Total Alkalinity: No adjustment needed")
            
            recommendations.append("")
            recommendations.append("SAFETY REMINDERS:")
            recommendations.append("- Never mix chemicals directly")
            recommendations.append("- Add chemicals to water, not water to chemicals")
            recommendations.append("- Wait recommended time between additions")
            recommendations.append("- Always wear protective equipment")
            recommendations.append("- Test water before swimming")
            
            return "\n".join(recommendations)
        except Exception as e:
            self.logger.error(f"Error calculating chemical recommendations: {e}")
            return "Error calculating recommendations. Please check your input values."

class TestStripAnalyzer:
    """Analyzer for test strips"""
    
    def __init__(self):
        """Initialize the test strip analyzer"""
        self.logger = logging.getLogger(__name__)
    
    def analyze_image(self, image_path):
        """
        Analyze a test strip image
        
        In a real implementation, this would use computer vision to analyze the image.
        For now, it's a placeholder that would be expanded with actual image processing.
        """
        self.logger.info(f"Analyzing test strip image: {image_path}")
        
        # This is a placeholder for actual image analysis
        # In a real implementation, this would use OpenCV or similar libraries
        
        # Return simulated results
        return {
            "ph": 7.2,
            "chlorine": 1.5,
            "alkalinity": 100,
            "hardness": 250,
            "cyanuric_acid": 40
        }
