#!/usr/bin/env python3
"""
Main entry point for Deep Blue Pool Chemistry application.
This script starts the application with proper error handling and logging.
"""
import os
import sys
import logging
import traceback
from pathlib import Path

# Configure logging
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / "pool_chemistry.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def setup_environment():
    """Set up the environment for the application."""
    # Add project root to Python path
    project_root = os.path.dirname(os.path.abspath(__file__))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    
    # Set environment variables
    os.environ["POOL_APP_ROOT"] = project_root
    
    # Create necessary directories
    for directory in ["logs", "data", "cache", "config"]:
        os.makedirs(os.path.join(project_root, directory), exist_ok=True)

def check_dependencies():
    """Check if all required dependencies are installed."""
    required_modules = [
        "tkinter",
        "ttkthemes",
        "pillow",
        "matplotlib",
        "numpy"
    ]
    
    missing_modules = []
    
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)
    
    return missing_modules

def main():
    """Main entry point for the application."""
    try:
        logger.info("Starting Deep Blue Pool Chemistry application")
        
        # Set up environment
        setup_environment()
        
        # Check dependencies
        missing_modules = check_dependencies()
        if missing_modules:
            logger.error(f"Missing required dependencies: {', '.join(missing_modules)}")
            print(f"Error: Missing required dependencies: {', '.join(missing_modules)}")
            print("Please install the missing dependencies using pip:")
            print(f"pip install {' '.join(missing_modules)}")
            return 1
        
        # Import the GUI launcher
        try:
            from app.gui_launcher import GUILauncher
            
            # Launch the application
            launcher = GUILauncher()
            launcher.launch()
            
            return 0
            
        except ImportError as e:
            logger.critical(f"Failed to import GUI launcher: {e}")
            print(f"Error: Failed to import GUI launcher: {e}")
            return 1
            
    except Exception as e:
        logger.critical(f"Unhandled exception: {e}", exc_info=True)
        print(f"Error: {e}")
        print("\nTraceback:")
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())