#!/usr/bin/env python3
"""
Chemical Safety Database for Deep Blue Pool Chemistry

This module provides a database of chemical safety information for pool chemicals.
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional

# Configure logging
logger = logging.getLogger(__name__)

class ChemicalSafetyDatabase:
    """
    Database of chemical safety information for pool chemicals.
    
    This class provides access to safety information for various pool chemicals,
    including hazard ratings, safety precautions, storage guidelines, and
    emergency procedures.
    
    Attributes:
        data_file: Path to the chemical safety data file
        chemicals: Dictionary of chemical safety information
    """
    
    def __init__(self, data_file: str = "data/chemical_safety_data.json"):
        """
        Initialize the chemical safety database.
        
        Args:
            data_file: Path to the chemical safety data file
        """
        self.data_file = data_file
        self.chemicals = {}
        self.logger = logging.getLogger("chemical_safety_database")
        self.logger.info("Initializing Chemical Safety Database")
        
        # Load chemical safety data
        self._load_data()
    
    def _load_data(self) -> None:
        """Load chemical safety data from file."""
        try:
            # Check if data file exists
            if not os.path.exists(self.data_file):
                self.logger.warning(f"Chemical safety data file not found at {self.data_file}")
                self._create_default_data()
                return
            
            # Load data from file
            with open(self.data_file, "r") as f:
                self.chemicals = json.load(f)
            
            self.logger.info(f"Loaded chemical safety data for {len(self.chemicals)} chemicals")
        except Exception as e:
            self.logger.error(f"Error loading chemical safety data: {e}")
            self._create_default_data()
    
    def _create_default_data(self) -> None:
        """Create default chemical safety data."""
        self.logger.info("Creating default chemical safety data")
        
        # Create default data
        self.chemicals = {
            "chlorine": {
                "name": "Chlorine",
                "chemical_formula": "Cl2",
                "hazard_rating": "High",
                "safety_precautions": [
                    "Wear gloves and eye protection",
                    "Use in well-ventilated area",
                    "Keep away from children",
                    "Do not mix with other chemicals"
                ],
                "storage_guidelines": "Store in a cool, dry place away from direct sunlight and other chemicals.",
                "emergency_procedures": "In case of contact with eyes, rinse immediately with plenty of water and seek medical advice."
            },
            "muriatic_acid": {
                "name": "Muriatic Acid",
                "chemical_formula": "HCl",
                "hazard_rating": "High",
                "safety_precautions": [
                    "Wear chemical-resistant gloves and eye protection",
                    "Use in well-ventilated area",
                    "Always add acid to water, never water to acid",
                    "Keep away from children",
                    "Do not mix with chlorine or other chemicals"
                ],
                "storage_guidelines": "Store in original container in a cool, dry place away from direct sunlight and other chemicals.",
                "emergency_procedures": "In case of contact with skin or eyes, rinse immediately with plenty of water for at least 15 minutes and seek medical advice."
            },
            "sodium_bicarbonate": {
                "name": "Sodium Bicarbonate",
                "chemical_formula": "NaHCO3",
                "hazard_rating": "Low",
                "safety_precautions": [
                    "Avoid contact with eyes",
                    "Keep away from children"
                ],
                "storage_guidelines": "Store in a cool, dry place.",
                "emergency_procedures": "In case of contact with eyes, rinse with water."
            },
            "calcium_chloride": {
                "name": "Calcium Chloride",
                "chemical_formula": "CaCl2",
                "hazard_rating": "Medium",
                "safety_precautions": [
                    "Wear gloves and eye protection",
                    "Avoid contact with skin and eyes",
                    "Keep away from children"
                ],
                "storage_guidelines": "Store in a cool, dry place away from direct sunlight.",
                "emergency_procedures": "In case of contact with skin or eyes, rinse with plenty of water."
            },
            "cyanuric_acid": {
                "name": "Cyanuric Acid",
                "chemical_formula": "C3H3N3O3",
                "hazard_rating": "Medium",
                "safety_precautions": [
                    "Wear gloves and eye protection",
                    "Avoid breathing dust",
                    "Keep away from children"
                ],
                "storage_guidelines": "Store in a cool, dry place away from direct sunlight.",
                "emergency_procedures": "In case of contact with skin or eyes, rinse with plenty of water."
            }
        }
        
        # Save data to file
        self._save_data()
    
    def _save_data(self) -> None:
        """Save chemical safety data to file."""
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
            
            # Save data to file
            with open(self.data_file, "w") as f:
                json.dump(self.chemicals, f, indent=4)
            
            self.logger.info(f"Saved chemical safety data to {self.data_file}")
        except Exception as e:
            self.logger.error(f"Error saving chemical safety data: {e}")
    
    def get_chemical_safety_info(self, chemical_id: str) -> Dict[str, Any]:
        """
        Get safety information for a chemical.
        
        Args:
            chemical_id: ID of the chemical
            
        Returns:
            Dictionary of safety information
        """
        if chemical_id in self.chemicals:
            return self.chemicals[chemical_id]
        else:
            self.logger.warning(f"Chemical {chemical_id} not found in safety database")
            return {}
    
    def get_all_chemicals(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all chemicals in the database.
        
        Returns:
            Dictionary of all chemicals
        """
        return self.chemicals
    
    def add_chemical(self, chemical_id: str, chemical_info: Dict[str, Any]) -> bool:
        """
        Add a chemical to the database.
        
        Args:
            chemical_id: ID of the chemical
            chemical_info: Dictionary of chemical information
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Add chemical to database
            self.chemicals[chemical_id] = chemical_info
            
            # Save data to file
            self._save_data()
            
            self.logger.info(f"Added chemical {chemical_id} to safety database")
            return True
        except Exception as e:
            self.logger.error(f"Error adding chemical {chemical_id}: {e}")
            return False
    
    def update_chemical(self, chemical_id: str, chemical_info: Dict[str, Any]) -> bool:
        """
        Update a chemical in the database.
        
        Args:
            chemical_id: ID of the chemical
            chemical_info: Dictionary of chemical information
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Check if chemical exists
            if chemical_id not in self.chemicals:
                self.logger.warning(f"Chemical {chemical_id} not found in safety database")
                return False
            
            # Update chemical in database
            self.chemicals[chemical_id] = chemical_info
            
            # Save data to file
            self._save_data()
            
            self.logger.info(f"Updated chemical {chemical_id} in safety database")
            return True
        except Exception as e:
            self.logger.error(f"Error updating chemical {chemical_id}: {e}")
            return False
    
    def delete_chemical(self, chemical_id: str) -> bool:
        """
        Delete a chemical from the database.
        
        Args:
            chemical_id: ID of the chemical
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Check if chemical exists
            if chemical_id not in self.chemicals:
                self.logger.warning(f"Chemical {chemical_id} not found in safety database")
                return False
            
            # Delete chemical from database
            del self.chemicals[chemical_id]
            
            # Save data to file
            self._save_data()
            
            self.logger.info(f"Deleted chemical {chemical_id} from safety database")
            return True
        except Exception as e:
            self.logger.error(f"Error deleting chemical {chemical_id}: {e}")
            return False
    
    def get_compatibility(self, chemical_id):
        """
        Get compatibility information for a chemical.
        
        Args:
            chemical_id: ID of the chemical
            
        Returns:
            Dictionary mapping chemical IDs to compatibility (True/False)
        """
        # Default implementation - return empty compatibility dict
        compatibility = {}
        
        try:
            # In a real implementation, this would query a database or lookup table
            # For now, we'll return some sample data
            all_chemicals = self.get_all_chemicals()
            
            # Remove the current chemical from the list
            other_chemicals = {cid: info for cid, info in all_chemicals.items() if cid != chemical_id}
            
            # For demonstration, we'll say chlorine is incompatible with acid
            if chemical_id == "chlorine":
                for cid, info in other_chemicals.items():
                    compatibility[cid] = "acid" not in info["name"].lower()
            # Acids are incompatible with chlorine and other acids
            elif "acid" in all_chemicals.get(chemical_id, {}).get("name", "").lower():
                for cid, info in other_chemicals.items():
                    compatibility[cid] = ("chlorine" != cid and 
                                         "acid" not in info["name"].lower())
            # For other chemicals, assume compatibility with everything
            else:
                for cid in other_chemicals:
                    compatibility[cid] = True
                    
        except Exception as e:
            self.logger.error(f"Error getting compatibility for chemical {chemical_id}: {e}")
        
        return compatibility

# For testing
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create chemical safety database
    db = ChemicalSafetyDatabase()
    
    # Print all chemicals
    chemicals = db.get_all_chemicals()
    print(f"Found {len(chemicals)} chemicals:")
    for chemical_id, chemical_info in chemicals.items():
        print(f"- {chemical_info['name']} ({chemical_id})")
    
    # Print safety information for chlorine
    chlorine_info = db.get_chemical_safety_info("chlorine")
    print("\nChlorine Safety Information:")
    print(f"Name: {chlorine_info['name']}")
    print(f"Chemical Formula: {chlorine_info['chemical_formula']}")
    print(f"Hazard Rating: {chlorine_info['hazard_rating']}")
    print("Safety Precautions:")
    for precaution in chlorine_info['safety_precautions']:
        print(f"- {precaution}")
    print(f"Storage Guidelines: {chlorine_info['storage_guidelines']}")
    print(f"Emergency Procedures: {chlorine_info['emergency_procedures']}")
    
    # Print compatibility information for chlorine
    compatibility = db.get_compatibility("chlorine")
    print("\nChlorine Compatibility:")
    for chemical_id, compatible in compatibility.items():
        chemical_name = db.get_chemical_safety_info(chemical_id)["name"]
        status = "Compatible" if compatible else "Incompatible"
        print(f"- {chemical_name}: {status}")
