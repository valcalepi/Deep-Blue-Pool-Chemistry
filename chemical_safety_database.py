"""
Chemical safety database module for the Deep Blue Pool Chemistry application.

This module provides a database for pool chemical safety information, handling storage
and retrieval of safety data sheets, compatibility information, and handling guidelines.
"""

import logging
import json
import os
from typing import Dict, List, Optional, Any, Tuple

# Configure logger
logger = logging.getLogger(__name__)


class ChemicalSafetyDatabase:
    """
    Database for pool chemical safety information.
    
    This class handles storage and retrieval of safety data sheets, compatibility
    information, and handling guidelines for pool chemicals.
    
    Attributes:
        data_file_path: Path to the JSON file containing chemical safety data
        chemicals_data: Dictionary of chemical safety information
        compatibility_matrix: Matrix of chemical compatibility information
    """
    
    def __init__(self, data_file_path: str = "data/chemical_safety_data.json"):
        """
        Initialize the chemical safety database.
        
        Args:
            data_file_path: Path to the JSON file containing chemical safety data
        """
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initializing Chemical Safety Database")
        self.data_file_path = data_file_path
        self.chemicals_data = {}
        self.compatibility_matrix = {}
        self._load_data()
    
    def _load_data(self) -> None:
        """
        Load chemical safety data from the data file.
        
        If the data file doesn't exist, creates default data.
        
        Raises:
            IOError: If there's an error reading the data file
            json.JSONDecodeError: If the data file contains invalid JSON
        """
        try:
            if os.path.exists(self.data_file_path):
                with open(self.data_file_path, 'r') as file:
                    data = json.load(file)
                    self.chemicals_data = data.get('chemicals', {})
                    self.compatibility_matrix = data.get('compatibility', {})
                self.logger.info(f"Loaded chemical safety data for {len(self.chemicals_data)} chemicals")
            else:
                self.logger.warning(f"Chemical safety data file not found at {self.data_file_path}")
                self._create_default_data()
        except (IOError, json.JSONDecodeError) as e:
            self.logger.error(f"Error loading chemical safety data: {str(e)}")
            self._create_default_data()
    
    def _create_default_data(self) -> None:
        """
        Create default chemical safety data for common pool chemicals.
        
        This is used when the data file doesn't exist or can't be loaded.
        """
        self.logger.info("Creating default chemical safety data")
        
        # Common pool chemicals with safety information
        self.chemicals_data = {
            "chlorine": {
                "name": "Chlorine",
                "chemical_formula": "Cl₂",
                "hazard_rating": 3,
                "safety_precautions": [
                    "Wear protective gloves and eye protection",
                    "Use in well-ventilated areas",
                    "Keep away from acids to prevent chlorine gas formation"
                ],
                "storage_guidelines": "Store in cool, dry place away from direct sunlight and incompatible materials",
                "emergency_procedures": "In case of exposure, move to fresh air and seek medical attention"
            },
            "muriatic_acid": {
                "name": "Muriatic Acid (Hydrochloric Acid)",
                "chemical_formula": "HCl",
                "hazard_rating": 3,
                "safety_precautions": [
                    "Always add acid to water, never water to acid",
                    "Wear chemical-resistant gloves, goggles, and protective clothing",
                    "Use in well-ventilated areas"
                ],
                "storage_guidelines": "Store in original container in cool, well-ventilated area away from bases",
                "emergency_procedures": "For skin contact, flush with water for 15 minutes and seek medical attention"
            },
            "sodium_bicarbonate": {
                "name": "Sodium Bicarbonate (Baking Soda)",
                "chemical_formula": "NaHCO₃",
                "hazard_rating": 1,
                "safety_precautions": [
                    "Minimal safety equipment required",
                    "Avoid generating dust"
                ],
                "storage_guidelines": "Store in dry area in sealed container",
                "emergency_procedures": "If in eyes, rinse with water"
            },
            "calcium_hypochlorite": {
                "name": "Calcium Hypochlorite",
                "chemical_formula": "Ca(ClO)₂",
                "hazard_rating": 3,
                "safety_precautions": [
                    "Wear protective gloves, clothing, and eye protection",
                    "Keep away from heat and combustible materials",
                    "Never mix with acids or ammonia"
                ],
                "storage_guidelines": "Store in cool, dry place away from acids and organic materials",
                "emergency_procedures": "In case of fire, use water spray. For exposure, seek medical attention"
            },
            "cyanuric_acid": {
                "name": "Cyanuric Acid",
                "chemical_formula": "C₃H₃N₃O₃",
                "hazard_rating": 1,
                "safety_precautions": [
                    "Avoid dust formation",
                    "Use with adequate ventilation"
                ],
                "storage_guidelines": "Store in dry, cool place in closed containers",
                "emergency_procedures": "If inhaled, move to fresh air"
            }
        }
        
        # Chemical compatibility matrix (1 = compatible, 0 = incompatible)
        self.compatibility_matrix = {
            "chlorine": {
                "muriatic_acid": 0,
                "sodium_bicarbonate": 1,
                "calcium_hypochlorite": 1,
                "cyanuric_acid": 1
            },
            "muriatic_acid": {
                "chlorine": 0,
                "sodium_bicarbonate": 0,
                "calcium_hypochlorite": 0,
                "cyanuric_acid": 1
            },
            "sodium_bicarbonate": {
                "chlorine": 1,
                "muriatic_acid": 0,
                "calcium_hypochlorite": 1,
                "cyanuric_acid": 1
            },
            "calcium_hypochlorite": {
                "chlorine": 1,
                "muriatic_acid": 0,
                "sodium_bicarbonate": 1,
                "cyanuric_acid": 1
            },
            "cyanuric_acid": {
                "chlorine": 1,
                "muriatic_acid": 1,
                "sodium_bicarbonate": 1,
                "calcium_hypochlorite": 1
            }
        }
        
        # Save default data
        self._save_data()
    
    def _save_data(self) -> None:
        """
        Save chemical safety data to the data file.
        
        Creates the directory if it doesn't exist.
        
        Raises:
            IOError: If there's an error writing to the data file
            OSError: If there's an error creating the directory
        """
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.data_file_path), exist_ok=True)
            
            data = {
                "chemicals": self.chemicals_data,
                "compatibility": self.compatibility_matrix
            }
            
            with open(self.data_file_path, 'w') as file:
                json.dump(data, file, indent=4)
            
            self.logger.info(f"Saved chemical safety data to {self.data_file_path}")
        except (IOError, OSError) as e:
            self.logger.error(f"Error saving chemical safety data: {str(e)}")
            raise
    
    def get_chemical_safety_info(self, chemical_id: str) -> Optional[Dict[str, Any]]:
        """
        Get safety information for a specific chemical.
        
        Args:
            chemical_id: Identifier for the chemical
            
        Returns:
            Dictionary containing safety information or None if not found
        """
        return self.chemicals_data.get(chemical_id.lower())
    
    def get_all_chemicals(self) -> Dict[str, Dict[str, Any]]:
        """
        Get information for all chemicals in the database.
        
        Returns:
            Dictionary containing all chemical safety information
        """
        return self.chemicals_data
    
    def check_compatibility(self, chemical1: str, chemical2: str) -> bool:
        """
        Check if two chemicals are compatible for storage or mixing.
        
        Args:
            chemical1: First chemical identifier
            chemical2: Second chemical identifier
            
        Returns:
            True if chemicals are compatible, False otherwise
        """
        chemical1 = chemical1.lower()
        chemical2 = chemical2.lower()
        
        # Check if both chemicals exist in the database
        if chemical1 not in self.compatibility_matrix or chemical2 not in self.compatibility_matrix:
            self.logger.warning("Compatibility check failed: One or both chemicals not in database")
            return False
        
        # Check compatibility (if same chemical, they're compatible)
        if chemical1 == chemical2:
            return True
            
        return bool(self.compatibility_matrix.get(chemical1, {}).get(chemical2, 0))
    
    def get_safety_guidelines(self, chemical_id: str) -> List[str]:
        """
        Get safety guidelines for handling a specific chemical.
        
        Args:
            chemical_id: Identifier for the chemical
            
        Returns:
            List of safety guidelines
        """
        chemical_info = self.get_chemical_safety_info(chemical_id)
        if not chemical_info:
            return []
        return chemical_info.get("safety_precautions", [])
    
    def add_chemical(self, chemical_id: str, chemical_data: Dict[str, Any]) -> bool:
        """
        Add a new chemical to the safety database.
        
        Args:
            chemical_id: Identifier for the chemical
            chemical_data: Dictionary containing chemical safety information
            
        Returns:
            True if successful, False otherwise
            
        Raises:
            ValueError: If the chemical data is invalid
        """
        try:
            # Validate required fields
            required_fields = ["name", "hazard_rating", "safety_precautions"]
            for field in required_fields:
                if field not in chemical_data:
                    raise ValueError(f"Missing required field: {field}")
            
            chemical_id = chemical_id.lower()
            self.chemicals_data[chemical_id] = chemical_data
            self._save_data()
            self.logger.info(f"Added chemical {chemical_id} to safety database")
            return True
        except Exception as e:
            self.logger.error(f"Error adding chemical {chemical_id}: {str(e)}")
            return False
    
    def update_chemical(self, chemical_id: str, chemical_data: Dict[str, Any]) -> bool:
        """
        Update information for an existing chemical.
        
        Args:
            chemical_id: Identifier for the chemical
            chemical_data: Dictionary containing updated chemical safety information
            
        Returns:
            True if successful, False otherwise
            
        Raises:
            ValueError: If the chemical doesn't exist or the data is invalid
        """
        chemical_id = chemical_id.lower()
        if chemical_id not in self.chemicals_data:
            self.logger.warning(f"Cannot update chemical {chemical_id}: Not found in database")
            return False
            
        try:
            # Validate required fields
            required_fields = ["name", "hazard_rating", "safety_precautions"]
            for field in required_fields:
                if field not in chemical_data:
                    raise ValueError(f"Missing required field: {field}")
            
            self.chemicals_data[chemical_id] = chemical_data
            self._save_data()
            self.logger.info(f"Updated chemical {chemical_id} in safety database")
            return True
        except Exception as e:
            self.logger.error(f"Error updating chemical {chemical_id}: {str(e)}")
            return False
    
    def set_compatibility(self, chemical1: str, chemical2: str, compatible: bool) -> bool:
        """
        Set compatibility between two chemicals.
        
        Args:
            chemical1: First chemical identifier
            chemical2: Second chemical identifier
            compatible: True if chemicals are compatible, False otherwise
            
        Returns:
            True if successful, False otherwise
            
        Raises:
            ValueError: If either chemical doesn't exist in the database
        """
        chemical1 = chemical1.lower()
        chemical2 = chemical2.lower()
        
        # Check if both chemicals exist in the database
        if chemical1 not in self.chemicals_data or chemical2 not in self.chemicals_data:
            self.logger.warning("Cannot set compatibility: One or both chemicals not in database")
            return False
            
        try:
            # Ensure compatibility matrix entries exist
            if chemical1 not in self.compatibility_matrix:
                self.compatibility_matrix[chemical1] = {}
            if chemical2 not in self.compatibility_matrix:
                self.compatibility_matrix[chemical2] = {}
                
            # Set bidirectional compatibility
            self.compatibility_matrix[chemical1][chemical2] = 1 if compatible else 0
            self.compatibility_matrix[chemical2][chemical1] = 1 if compatible else 0
            
            self._save_data()
            self.logger.info(f"Set compatibility between {chemical1} and {chemical2} to {compatible}")
            return True
        except Exception as e:
            self.logger.error(f"Error setting compatibility: {str(e)}")
            return False
    
    def get_hazard_rating(self, chemical_id: str) -> Optional[int]:
        """
        Get the hazard rating for a specific chemical.
        
        Args:
            chemical_id: Identifier for the chemical
            
        Returns:
            Hazard rating (1-4) or None if not found
        """
        chemical_info = self.get_chemical_safety_info(chemical_id)
        if not chemical_info:
            return None
        return chemical_info.get("hazard_rating")
    
    def get_emergency_procedures(self, chemical_id: str) -> Optional[str]:
        """
        Get emergency procedures for a specific chemical.
        
        Args:
            chemical_id: Identifier for the chemical
            
        Returns:
            Emergency procedures or None if not found
        """
        chemical_info = self.get_chemical_safety_info(chemical_id)
        if not chemical_info:
            return None
        return chemical_info.get("emergency_procedures")
    
    def get_storage_guidelines(self, chemical_id: str) -> Optional[str]:
        """
        Get storage guidelines for a specific chemical.
        
        Args:
            chemical_id: Identifier for the chemical
            
        Returns:
            Storage guidelines or None if not found
        """
        chemical_info = self.get_chemical_safety_info(chemical_id)
        if not chemical_info:
            return None
        return chemical_info.get("storage_guidelines")
    
    def get_chemical_formula(self, chemical_id: str) -> Optional[str]:
        """
        Get the chemical formula for a specific chemical.
        
        Args:
            chemical_id: Identifier for the chemical
            
        Returns:
            Chemical formula or None if not found
        """
        chemical_info = self.get_chemical_safety_info(chemical_id)
        if not chemical_info:
            return None
        return chemical_info.get("chemical_formula")
    
    def get_compatible_chemicals(self, chemical_id: str) -> List[str]:
        """
        Get a list of chemicals that are compatible with the specified chemical.
        
        Args:
            chemical_id: Identifier for the chemical
            
        Returns:
            List of compatible chemical IDs
        """
        chemical_id = chemical_id.lower()
        if chemical_id not in self.compatibility_matrix:
            return []
        
        return [
            chem_id for chem_id, compatible in self.compatibility_matrix[chemical_id].items()
            if compatible == 1
        ]
    
    def get_incompatible_chemicals(self, chemical_id: str) -> List[str]:
        """
        Get a list of chemicals that are incompatible with the specified chemical.
        
        Args:
            chemical_id: Identifier for the chemical
            
        Returns:
            List of incompatible chemical IDs
        """
        chemical_id = chemical_id.lower()
        if chemical_id not in self.compatibility_matrix:
            return []
        
        return [
            chem_id for chem_id, compatible in self.compatibility_matrix[chemical_id].items()
            if compatible == 0
        ]
    
    def delete_chemical(self, chemical_id: str) -> bool:
        """
        Delete a chemical from the safety database.
        
        Args:
            chemical_id: Identifier for the chemical
            
        Returns:
            True if successful, False otherwise
        """
        chemical_id = chemical_id.lower()
        if chemical_id not in self.chemicals_data:
            self.logger.warning(f"Cannot delete chemical {chemical_id}: Not found in database")
            return False
        
        try:
            # Remove from chemicals data
            del self.chemicals_data[chemical_id]
            
            # Remove from compatibility matrix
            if chemical_id in self.compatibility_matrix:
                del self.compatibility_matrix[chemical_id]
            
            # Remove from other chemicals' compatibility entries
            for chem_id in self.compatibility_matrix:
                if chemical_id in self.compatibility_matrix[chem_id]:
                    del self.compatibility_matrix[chem_id][chemical_id]
            
            self._save_data()
            self.logger.info(f"Deleted chemical {chemical_id} from safety database")
            return True
        except Exception as e:
            self.logger.error(f"Error deleting chemical {chemical_id}: {str(e)}")
            return False