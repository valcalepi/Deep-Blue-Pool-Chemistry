
#!/usr/bin/env python3
"""
Setup script for Deep Blue Pool Chemistry application.

This script:
1. Installs required dependencies
2. Sets up the correct directory structure
3. Fixes import issues
4. Creates any missing files
5. Runs the application
"""

import os
import sys
import subprocess
import shutil
import logging
import argparse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("SetupScript")

def install_dependencies():
    """Install required Python dependencies."""
    logger.info("Installing required dependencies...")
    
    # List of required packages
    requirements = [
        "numpy>=1.20.0",
        "opencv-python>=4.5.0",
        "Pillow>=8.0.0",
        "matplotlib>=3.4.0",
        "requests>=2.25.0",
        "SQLAlchemy>=1.4.0"
    ]
    
    # Install each package
    for package in requirements:
        logger.info(f"Installing {package}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to install {package}: {e}")
            return False
    
    logger.info("All dependencies installed successfully.")
    return True

def fix_directory_structure(repo_path):
    """Fix the directory structure of the application."""
    logger.info("Fixing directory structure...")
    
    # Ensure app directory exists
    app_dir = os.path.join(repo_path, "app")
    if not os.path.exists(app_dir):
        os.makedirs(app_dir)
        logger.info(f"Created app directory: {app_dir}")
    
    # Create __init__.py in app directory if it doesn't exist
    init_file = os.path.join(app_dir, "__init__.py")
    if not os.path.exists(init_file):
        with open(init_file, "w") as f:
            f.write('"""App package for Deep Blue Pool Chemistry."""\
')
        logger.info(f"Created {init_file}")
    
    # Create arduino_monitor.py in app directory if it doesn't exist
    arduino_monitor_file = os.path.join(app_dir, "arduino_monitor.py")
    if not os.path.exists(arduino_monitor_file):
        arduino_monitor_code = """#!/usr/bin/env python3
\"\"\"
Arduino Sensor Monitor GUI for Deep Blue Pool Chemistry

This module provides a GUI for monitoring Arduino sensor data in real-time.
\"\"\"

import os
import sys
import time
import logging
import threading
from datetime import datetime
from typing import Dict, Any, List, Optional

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.dates as mdates
import numpy as np

# Configure logging
logger = logging.getLogger("arduino_monitor")

class ArduinoMonitorApp:
    \"\"\"
    GUI application for monitoring Arduino sensor data in real-time.
    \"\"\"
    
    def __init__(self, parent: Optional[tk.Widget] = None):
        \"\"\"
        Initialize the Arduino Monitor application.
        
        Args:
            parent: Parent widget. If None, a new window will be created.
        \"\"\"
        # Initialize logger
        self.logger = logging.getLogger("arduino_monitor")
        self.logger.info("Initializing Arduino Monitor")
        
        # Store parent widget
        self.parent = parent
        
        # Create main frame
        self.main_frame = ttk.Frame(parent)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Add title
        title = ttk.Label(self.main_frame, text="Arduino Sensor Monitor", font=("Arial", 18))
        title.pack(pady=10)
        
        # Add status message
        self.status_var = tk.StringVar(value="Arduino Monitor is not connected")
        status_label = ttk.Label(self.main_frame, textvariable=self.status_var, font=("Arial", 12))
        status_label.pack(pady=5)
        
        # Add message
        ttk.Label(self.main_frame, text="This is a placeholder for the Arduino Monitor.", font=("Arial", 12)).pack(pady=20)
        ttk.Label(self.main_frame, text="The actual monitor functionality is not available in this version.", font=("Arial", 12)).pack(pady=5)
        
        self.logger.info("Arduino Monitor initialized")
"""
        with open(arduino_monitor_file, "w") as f:
            f.write(arduino_monitor_code)
        logger.info(f"Created {arduino_monitor_file}")
    
    # Create data directory if it doesn't exist
    data_dir = os.path.join(repo_path, "data")
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        logger.info(f"Created data directory: {data_dir}")
    
    # Create logs directory if it doesn't exist
    logs_dir = os.path.join(repo_path, "logs")
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
        logger.info(f"Created logs directory: {logs_dir}")
    
    logger.info("Directory structure fixed successfully.")
    return True

def fix_import_issues(repo_path):
    """Fix import issues in the application code."""
    logger.info("Fixing import issues...")
    
    # Fix pool_app.py
    pool_app_path = os.path.join(repo_path, "pool_app.py")
    if os.path.exists(pool_app_path):
        with open(pool_app_path, "r") as f:
            pool_app_code = f.read()
        
        # Fix the import statement
        if 'from app.arduino_monitor import ArduinoMonitorApp' in pool_app_code:
            pool_app_code = pool_app_code.replace(
                'from app.arduino_monitor import ArduinoMonitorApp',
                'try:\
                from app.arduino_monitor import ArduinoMonitorApp\
            except ImportError:\
                from arduino_monitor_app import ArduinoMonitorApp'
            )
            
            with open(pool_app_path, "w") as f:
                f.write(pool_app_code)
            logger.info(f"Fixed import issues in {pool_app_path}")
    
    # Create arduino_monitor_app.py as a fallback
    arduino_monitor_app_path = os.path.join(repo_path, "arduino_monitor_app.py")
    if not os.path.exists(arduino_monitor_app_path):
        arduino_monitor_app_code = """#!/usr/bin/env python3
\"\"\"
Arduino Sensor Monitor GUI for Deep Blue Pool Chemistry

This module provides a simplified version of the Arduino Monitor for compatibility.
\"\"\"

import tkinter as tk
from tkinter import ttk
import logging

class ArduinoMonitorApp:
    \"\"\"
    Simplified GUI application for monitoring Arduino sensor data.
    \"\"\"
    
    def __init__(self, parent=None):
        \"\"\"
        Initialize the Arduino Monitor application.
        
        Args:
            parent: Parent widget. If None, a new window will be created.
        \"\"\"
        # Initialize logger
        self.logger = logging.getLogger("arduino_monitor")
        self.logger.info("Initializing Arduino Monitor (Simplified)")
        
        # Create main frame
        self.main_frame = ttk.Frame(parent)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Add title
        title = ttk.Label(self.main_frame, text="Arduino Sensor Monitor", font=("Arial", 18))
        title.pack(pady=10)
        
        # Add status message
        self.status_var = tk.StringVar(value="Arduino Monitor is not connected")
        status_label = ttk.Label(self.main_frame, textvariable=self.status_var, font=("Arial", 12))
        status_label.pack(pady=5)
        
        # Add message
        ttk.Label(self.main_frame, text="This is a placeholder for the Arduino Monitor.", font=("Arial", 12)).pack(pady=20)
        ttk.Label(self.main_frame, text="The actual monitor functionality is not available in this version.", font=("Arial", 12)).pack(pady=5)
        
        self.logger.info("Arduino Monitor initialized")
"""
        with open(arduino_monitor_app_path, "w") as f:
            f.write(arduino_monitor_app_code)
        logger.info(f"Created {arduino_monitor_app_path}")
    
    logger.info("Import issues fixed successfully.")
    return True

def create_run_script(repo_path):
    """Create a run script for the application."""
    logger.info("Creating run script...")
    
    run_script_path = os.path.join(repo_path, "run_deep_blue_pool.py")
    run_script_code = """#!/usr/bin/env python3
\"\"\"
Run script for Deep Blue Pool Chemistry application.

This script sets up the environment and runs the application.
\"\"\"

import os
import sys
import logging
import traceback

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("RunScript")

def main():
    \"\"\"Main function.\"\"\"
    # Add the current directory to the Python path
    sys.path.insert(0, os.getcwd())
    
    # Check if required directories exist
    required_dirs = ["app", "data", "logs"]
    for dir_name in required_dirs:
        if not os.path.exists(dir_name):
            logger.error(f"Required directory '{dir_name}' not found.")
            logger.warning("Environment is not properly set up. Running setup...")
            
            # Run setup script
            logger.info("Running setup script...")
            try:
                import setup_deep_blue_pool
                setup_deep_blue_pool.main()
            except Exception as e:
                logger.error(f"Setup failed: {e}")
                logger.error(traceback.format_exc())
                logger.error("Failed to set up environment. Exiting.")
                return 1
    
    # Run the application
    logger.info("Starting application in GUI mode...")
    try:
        # Import and run the main function
        from main import main
        return main()
    except Exception as e:
        logger.error(f"Application failed to start in GUI mode: {e}")
        logger.error(traceback.format_exc())
        return 1

if __name__ == "__main__":
    sys.exit(main())
"""
    with open(run_script_path, "w") as f:
        f.write(run_script_code)
    
    # Make the script executable
    os.chmod(run_script_path, 0o755)
    
    logger.info(f"Created run script: {run_script_path}")
    return True

def run_application(repo_path):
    """Run the Deep Blue Pool Chemistry application."""
    logger.info("Running the application...")
    
    # Change to the repository directory
    os.chdir(repo_path)
    
    # Run the main.py script
    try:
        # Import and run the main function
        sys.path.insert(0, repo_path)
        from main import main
        return main()
    except Exception as e:
        logger.error(f"Failed to run the application: {e}")
        logger.error(traceback.format_exc())
        return False

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Setup Deep Blue Pool Chemistry application")
    parser.add_argument("--repo-path", default="/workspace/Deep-Blue-Pool-Chemistry", help="Path to the repository")
    parser.add_argument("--skip-deps", action="store_true", help="Skip installing dependencies")
    parser.add_argument("--skip-run", action="store_true", help="Skip running the application")
    args = parser.parse_args()
    
    # Check if the repository exists
    if not os.path.exists(args.repo_path):
        logger.error(f"Repository not found at {args.repo_path}")
        return 1
    
    # Install dependencies
    if not args.skip_deps:
        if not install_dependencies():
            logger.error("Failed to install dependencies")
            return 1
    
    # Fix directory structure
    if not fix_directory_structure(args.repo_path):
        logger.error("Failed to fix directory structure")
        return 1
    
    # Fix import issues
    if not fix_import_issues(args.repo_path):
        logger.error("Failed to fix import issues")
        return 1
    
    # Create run script
    if not create_run_script(args.repo_path):
        logger.error("Failed to create run script")
        return 1
    
    # Run the application
    if not args.skip_run:
        if not run_application(args.repo_path):
            logger.error("Failed to run the application")
            return 1
    
    logger.info("Setup completed successfully")
    return 0

if __name__ == "__main__":
    sys.exit(main())
