import logging
import sys
import os
import traceback

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("RunGUI")

try:
    # Add the current directory to the path to ensure imports work
    sys.path.insert(0, os.path.abspath('.'))
    
    logger.info("Importing gui_elements...")
    from app.gui_elements import PoolChemistryGUI
    
    logger.info("Creating GUI instance...")
    app = PoolChemistryGUI()
    
    logger.info("Running GUI...")
    app.run()
    
except ImportError as e:
    logger.error(f"Import error: {e}")
    traceback.print_exc()
    
    # Try to diagnose the import error
    logger.info("Checking for app directory...")
    if os.path.exists('app'):
        logger.info("app directory exists")
        logger.info(f"Contents of app directory: {os.listdir('app')}")
        
        if os.path.exists('app/gui_elements.py'):
            logger.info("gui_elements.py exists")
            
            # Check for circular imports
            logger.info("Checking for circular imports...")
            try:
                import app
                logger.info("app module imported successfully")
            except ImportError as app_error:
                logger.error(f"Error importing app module: {app_error}")
    else:
        logger.error("app directory does not exist")
    
except Exception as e:
    logger.error(f"Error: {e}")
    traceback.print_exc()
