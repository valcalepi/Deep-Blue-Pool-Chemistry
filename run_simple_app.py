
#!/usr/bin/env python3
"""
Run script for the simplified Deep Blue Pool Chemistry application.

This script runs the simplified version of the application that doesn't rely on
external imports or complex directory structures.
"""

import os
import sys
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("run_simple_app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("RunSimpleApp")

def setup_environment():
    """
    Set up the environment for running the application.
    
    This function ensures that all necessary directories exist.
    """
    logger.info("Setting up environment")
    
    # Create necessary directories
    directories = [
        "data",
        "data/strip_profiles",
        "logs"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        logger.info(f"Created directory: {directory}")

def run_application():
    """
    Run the simplified application.
    """
    logger.info("Running simplified application")
    
    try:
        # Import and run the simplified application
        from simple_pool_app import main
        main()
    except Exception as e:
        logger.error(f"Error running application: {e}")
        import traceback
        logger.error(traceback.format_exc())
        print(f"Error running application: {e}")
        print("Check the run_simple_app.log file for details.")

if __name__ == "__main__":
    try:
        setup_environment()
        run_application()
    except Exception as e:
        logger.error(f"Error in run_simple_app.py: {e}")
        import traceback
        logger.error(traceback.format_exc())
        print(f"Error: {e}")
        print("Check the run_simple_app.log file for details.")
