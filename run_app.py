#!/usr/bin/env python3
import logging
import sys
import os
import traceback
import argparse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("pool_chemistry.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("RunApp")

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Deep Blue Pool Chemistry Application')
    parser.add_argument('--headless', action='store_true', help='Run in headless mode (for testing)')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    return parser.parse_args()

def setup_environment():
    """Set up the environment for the application"""
    # Add the current directory to the path to ensure imports work
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, current_dir)
    
    # Print the Python path for debugging
    logger.debug(f"Python path: {sys.path}")
    
    # Check for required directories
    for directory in ['app', 'app/models', 'app/controllers', 'app/views']:
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
            logger.info(f"Created directory: {directory}")
    
    # Check for config.json
    if not os.path.exists('config.json'):
        logger.warning("config.json not found, using default configuration")
    
    logger.info("Environment setup complete")

def run_headless_test():
    """Run headless tests"""
    try:
        logger.info("Running headless tests...")
        
        # Import modules
        try:
            # Try absolute import first
            from app.gui_controller import PoolChemistryController
            logger.info("Imported PoolChemistryController using absolute import")
        except ImportError:
            # Fall back to relative import
            logger.info("Absolute import failed, trying relative import")
            sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))
            from gui_controller import PoolChemistryController
            logger.info("Imported PoolChemistryController using relative import")
        
        # Test controller
        controller = PoolChemistryController()
        health = controller.check_database_health()
        logger.info(f"Database health: {health}")
        
        # Test chemical calculations
        pool_data = {
            "pool_type": "Concrete/Gunite",
            "pool_size": "10000",
            "ph": "7.2",
            "chlorine": "1.5",
            "alkalinity": "100",
            "calcium_hardness": "250",
            "temperature": "78"
        }
        
        result = controller.calculate_chemicals(pool_data)
        logger.info(f"Chemical calculation result: {result}")
        
        logger.info("Headless tests completed successfully")
        return True
    except Exception as e:
        logger.error(f"Headless test error: {e}")
        traceback.print_exc()
        return False

def run_gui():
    """Run the GUI application"""
    try:
        logger.info("Starting Pool Chemistry GUI...")
        
        # Import the GUI class
        try:
            # Try absolute import first
            from app.gui_elements import PoolChemistryGUI
            logger.info("Imported PoolChemistryGUI using absolute import")
        except ImportError:
            # Fall back to relative import
            logger.info("Absolute import failed, trying relative import")
            sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))
            from gui_elements import PoolChemistryGUI
            logger.info("Imported PoolChemistryGUI using relative import")
        
        # Create and run application
        app = PoolChemistryGUI()
        app.run()
        
        logger.info("GUI application closed")
        return True
    except Exception as e:
        logger.error(f"Error running GUI: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Parse arguments
    args = parse_arguments()
    
    # Set log level
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Debug logging enabled")
    
    logger.info("Starting Deep Blue Pool Chemistry application")
    
    # Set up the environment
    setup_environment()
    
    # Run in appropriate mode
    if args.headless:
        success = run_headless_test()
    else:
        success = run_gui()
    
    if success:
        logger.info("Application exited successfully")
        sys.exit(0)
    else:
        logger.error("Application exited with errors")
        sys.exit(1)
