
#!/usr/bin/env python3
"""
Main entry point for Deep Blue Pool Chemistry application.

This script initializes and runs the application in either GUI or CLI mode.
"""

import os
import sys
import logging
import argparse
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

def run_gui_mode():
    """Run the application in GUI mode."""
    logger.info("Starting application in GUI mode")
    try:
        # Import from pool_app.py instead of app.py
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from app.pool_app import PoolChemistryApp
        app = PoolChemistryApp()
        app.run_gui()
        return True
    except Exception as e:
        logger.error(f"Error running GUI mode: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def run_cli_mode():
    """Run the application in CLI mode."""
    logger.info("Starting application in CLI mode")
    try:
        # Import from pool_app.py instead of app.py
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from app.pool_app import PoolChemistryApp
        app = PoolChemistryApp()
        app.run_cli()
        return True
    except Exception as e:
        logger.error(f"Error running CLI mode: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Run Deep Blue Pool Chemistry application")
    parser.add_argument("--cli", action="store_true", help="Run in CLI mode")
    args = parser.parse_args()
    
    if args.cli:
        return 0 if run_cli_mode() else 1
    else:
        return 0 if run_gui_mode() else 1

if __name__ == "__main__":
    sys.exit(main())
