
#!/usr/bin/env python3
"""
Run script for the responsive UI version of Deep Blue Pool Chemistry application.

This script provides a way to run the application with the responsive UI,
which adapts to different screen sizes and orientations.
"""

import os
import sys
import logging
import tkinter as tk
import argparse
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/responsive_ui.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("run_responsive_ui")

def run_responsive_ui():
    """Run the application with the responsive UI."""
    try:
        # Add the current directory to the Python path
        sys.path.insert(0, os.getcwd())
        
        # Import the pool app
        from pool_app import PoolChemistryApp
        
        # Create the pool app instance
        app = PoolChemistryApp()
        
        # Create the root window
        root = tk.Tk()
        
        # Import the responsive UI
        from responsive_tab_ui import ResponsiveTabUI
        
        # Initialize the responsive UI
        ui = ResponsiveTabUI(
            root=root,
            db_service=app.db_service,
            chemical_safety_db=app.chemical_safety_db,
            test_strip_analyzer=app.test_strip_analyzer,
            weather_service=app.weather_service,
            controller=app.controller
        )
        
        logger.info("Responsive UI initialized successfully")
        
        # Start the main loop
        root.mainloop()
        
        return True
    except Exception as e:
        logger.error(f"Error running responsive UI: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Run Deep Blue Pool Chemistry application with responsive UI")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    args = parser.parse_args()
    
    # Set log level
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Debug logging enabled")
    
    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)
    
    # Run the responsive UI
    success = run_responsive_ui()
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
