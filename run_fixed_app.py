
#!/usr/bin/env python3
"""
Run script for the fixed Deep Blue Pool Chemistry application.

This script runs the fixed version of the application that addresses the import
and initialization issues.
"""

import os
import sys
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("run_fixed_app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("RunFixedApp")

def setup_environment():
    """
    Set up the environment for running the application.
    
    This function ensures that all necessary directories exist and that
    the Python path is set up correctly.
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
    
    # Add the current directory to the Python path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
    
    # Create services directory if it doesn't exist
    services_dir = os.path.join(current_dir, "services")
    if not os.path.exists(services_dir):
        os.makedirs(services_dir, exist_ok=True)
        logger.info(f"Created services directory: {services_dir}")
    
    # Create test_strip directory if it doesn't exist
    test_strip_dir = os.path.join(services_dir, "test_strip")
    if not os.path.exists(test_strip_dir):
        os.makedirs(test_strip_dir, exist_ok=True)
        logger.info(f"Created test_strip directory: {test_strip_dir}")
    
    # Copy the fixed test_strip_analyzer.py to the services/test_strip directory
    if os.path.exists("test_strip_analyzer_fixed.py"):
        test_strip_analyzer_path = os.path.join(test_strip_dir, "test_strip_analyzer.py")
        with open("test_strip_analyzer_fixed.py", "r") as src_file:
            content = src_file.read()
            with open(test_strip_analyzer_path, "w") as dst_file:
                dst_file.write(content)
        logger.info(f"Copied fixed test_strip_analyzer.py to {test_strip_analyzer_path}")
    
    # Create __init__.py files
    init_files = [
        os.path.join(services_dir, "__init__.py"),
        os.path.join(test_strip_dir, "__init__.py")
    ]
    
    for init_file in init_files:
        if not os.path.exists(init_file):
            with open(init_file, "w") as f:
                f.write('"""\
Service module for Deep Blue Pool Chemistry application.\
"""\
')
            logger.info(f"Created __init__.py file: {init_file}")

def run_application():
    """
    Run the fixed application.
    """
    logger.info("Running fixed application")
    
    try:
        # Import and run the fixed application
        from pool_app_working_fix import main
        main()
    except Exception as e:
        logger.error(f"Error running application: {e}")
        import traceback
        logger.error(traceback.format_exc())
        print(f"Error running application: {e}")
        print("Check the run_fixed_app.log file for details.")

if __name__ == "__main__":
    try:
        setup_environment()
        run_application()
    except Exception as e:
        logger.error(f"Error in run_fixed_app.py: {e}")
        import traceback
        logger.error(traceback.format_exc())
        print(f"Error: {e}")
        print("Check the run_fixed_app.log file for details.")
