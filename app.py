#!/usr/bin/env python3
"""
Pool Chemistry Manager - Professional Edition
Main application entry point
"""

import os
import sys
import logging
import tkinter as tk
from tkinter import messagebox

# Add the project directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import application modules
from modules.config_manager import ConfigManager
from modules.ui_components import ApplicationUI

def main():
    """Main function to run the application"""
    try:
        # Create necessary directories
        os.makedirs("config", exist_ok=True)
        os.makedirs("data", exist_ok=True)
        os.makedirs("logs", exist_ok=True)
        
        # Initialize configuration
        config_manager = ConfigManager("config/app_config.json")
        
        # Setup logging
        setup_logging(config_manager.get_config())
        
        # Create and run application
        root = tk.Tk()
        app = ApplicationUI(root, config_manager)
        app.run()
        
    except Exception as e:
        print(f"Failed to start application: {e}")
        import traceback
        traceback.print_exc()
        
        # Show error dialog if possible
        try:
            messagebox.showerror("Application Error", f"Failed to start application: {e}")
        except:
            pass

def setup_logging(config):
    """Setup logging configuration"""
    try:
        # Create logs directory if it doesn't exist
        log_dir = os.path.dirname(config["application"]["log_file"])
        os.makedirs(log_dir, exist_ok=True)
        
        # Configure logging
        logging.basicConfig(
            level=getattr(logging, config["application"]["log_level"]),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(config["application"]["log_file"]),
                logging.StreamHandler()
            ]
        )
        
        logger = logging.getLogger(__name__)
        logger.info("Pool Chemistry Manager started")
        
    except Exception as e:
        print(f"Error setting up logging: {e}")
        # Fallback to basic logging
        logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    main()