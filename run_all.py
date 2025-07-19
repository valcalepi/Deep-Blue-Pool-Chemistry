#!/usr/bin/env python3
"""
Run script for Deep Blue Pool Chemistry application.

This script runs the unified launcher, which provides access to all versions
of the application.
"""

import os
import sys
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/run_all.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("RunAll")

def main():
    """Main function."""
    # Add the current directory to the Python path
    sys.path.insert(0, os.getcwd())
    
    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)
    
    # Import and run the unified launcher
    try:
        from unified_launcher import main as run_launcher
        return run_launcher()
    except Exception as e:
        logger.error(f"Error running unified launcher: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return 1

if __name__ == "__main__":
    sys.exit(main())
