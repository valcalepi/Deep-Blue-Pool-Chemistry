
import logging
import sys
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

# Add the current directory to the path so we can import our module
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the ChemicalSafetyDatabase class
from services.chemical_safety.chemical_safety_database import ChemicalSafetyDatabase

def test_chemical_safety_database():
    """Test the ChemicalSafetyDatabase functionality."""
    logger = logging.getLogger("test_chemical_safety")
    logger.info("Testing ChemicalSafetyDatabase...")
    
    # Initialize the database
    db = ChemicalSafetyDatabase()
    
    # Test getting all chemicals
    chemicals = db.get_all_chemicals()
    logger.info(f"Found {len(chemicals)} chemicals in the database")
    
    # Test getting specific chemical info
    chlorine_info = db.get_chemical_safety_info("chlorine")
    if chlorine_info:
        logger.info(f"Chlorine information retrieved: {chlorine_info['name']}")
    else:
        logger.error("Failed to retrieve chlorine information")
    
    # Test compatibility check
    compatible = db.check_compatibility("chlorine", "sodium_bicarbonate")
    logger.info(f"Chlorine and Sodium Bicarbonate compatible: {compatible}")
    
    incompatible = db.check_compatibility("chlorine", "muriatic_acid")
    logger.info(f"Chlorine and Muriatic Acid compatible: {incompatible}")
    
    # Test safety guidelines
    guidelines = db.get_safety_guidelines("calcium_hypochlorite")
    logger.info(f"Safety guidelines for Calcium Hypochlorite: {guidelines}")
    
    logger.info("ChemicalSafetyDatabase tests completed")

if __name__ == "__main__":
    test_chemical_safety_database()
