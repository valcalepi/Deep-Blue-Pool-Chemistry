#!/usr/bin/env python3
"""
Run script for Deep Blue Pool Chemistry application.

This script provides a simple way to run the application in different modes.
"""

import os
import sys
import argparse
import logging
import subprocess

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("pool_chemistry.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("RunScript")

def check_environment():
    """Check if the environment is properly set up."""
    # Check if Python version is compatible
    if sys.version_info < (3, 8):
        logger.error("Python 3.8 or higher is required.")
        return False
    
    # Check if required directories exist
    required_dirs = ["data", "services/image_processing"]
    for directory in required_dirs:
        if not os.path.exists(directory):
            logger.error(f"Required directory '{directory}' not found.")
            return False
    
    # Check if required files exist
    required_files = [
        "config.json",
        "data/calibration.json",
        "data/pad_zones.json"
    ]
    for file_path in required_files:
        if not os.path.exists(file_path):
            logger.error(f"Required file '{file_path}' not found.")
            return False
    
    return True

def run_setup():
    """Run the setup script to initialize the environment."""
    logger.info("Running setup script...")
    try:
        subprocess.check_call([sys.executable, "setup.py"])
        logger.info("Setup completed successfully.")
        return True
    except subprocess.CalledProcessError:
        logger.error("Setup failed. Please check the output above for details.")
        return False

def run_gui():
    """Run the application in GUI mode."""
    logger.info("Starting application in GUI mode...")
    try:
        subprocess.check_call([sys.executable, "main.py"])
        return True
    except subprocess.CalledProcessError:
        logger.error("Application failed to start in GUI mode.")
        return False

def run_cli():
    """Run the application in CLI mode."""
    logger.info("Starting application in CLI mode...")
    try:
        subprocess.check_call([sys.executable, "main.py", "--cli"])
        return True
    except subprocess.CalledProcessError:
        logger.error("Application failed to start in CLI mode.")
        return False

def run_minimal_cli():
    """Run the application in minimal CLI mode."""
    logger.info("Starting application in minimal CLI mode...")
    try:
        subprocess.check_call([sys.executable, "minimal_cli.py"])
        return True
    except subprocess.CalledProcessError:
        logger.error("Application failed to start in minimal CLI mode.")
        return False

def run_tests():
    """Run the test suite."""
    logger.info("Running tests...")
    try:
        subprocess.check_call([sys.executable, "comprehensive_test.py"])
        return True
    except subprocess.CalledProcessError:
        logger.error("Tests failed. Please check the output above for details.")
        return False

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Run Deep Blue Pool Chemistry application")
    parser.add_argument("--gui", action="store_true", help="Run in GUI mode (default)")
    parser.add_argument("--cli", action="store_true", help="Run in CLI mode")
    parser.add_argument("--minimal", action="store_true", help="Run in minimal CLI mode")
    parser.add_argument("--test", action="store_true", help="Run tests")
    parser.add_argument("--setup", action="store_true", help="Run setup")
    args = parser.parse_args()
    
    # Check if environment is properly set up
    if not check_environment():
        logger.warning("Environment is not properly set up. Running setup...")
        if not run_setup():
            logger.error("Failed to set up environment. Exiting.")
            return 1
    
    # Run the application in the specified mode
    if args.setup:
        return 0 if run_setup() else 1
    elif args.test:
        return 0 if run_tests() else 1
    elif args.cli:
        return 0 if run_cli() else 1
    elif args.minimal:
        return 0 if run_minimal_cli() else 1
    else:
        # Default to GUI mode
        return 0 if run_gui() else 1

if __name__ == "__main__":
    sys.exit(main())
