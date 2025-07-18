#!/usr/bin/env python3
"""
Main entry point for Deep Blue Pool Chemistry application.

This script initializes and runs the application using the unified launcher.
"""

import os
import sys
import logging
from datetime import datetime

# Configure logging with timestamp in filename
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
log_file = f"logs/pool_app_{timestamp}.log"
os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("PoolApp")

def main():
    """Main function."""
    # Add the current directory to the Python path
    sys.path.insert(0, os.getcwd())
    
    # Import the unified launcher
    try:
        from unified_launcher import main as run_launcher
        return run_launcher()
    except Exception as e:
        logger.error(f"Error running unified launcher: {e}")
        import traceback
        logger.error(traceback.format_exc())
        
        # Fall back to original main function if unified launcher fails
        try:
            from pool_app import PoolChemistryApp
            app = PoolChemistryApp()
            app.run_gui()
            return 0
        except Exception as e2:
            logger.error(f"Error running fallback: {e2}")
            logger.error(traceback.format_exc())
            return 1

if __name__ == "__main__":
    sys.exit(main())
