
#!/usr/bin/env python3
"""
Run script for the Enhanced Data Visualization tool.

This script provides a way to run the Enhanced Data Visualization tool
as a standalone application.
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
        logging.FileHandler("logs/enhanced_visualization.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("run_enhanced_visualization")

def run_enhanced_visualization():
    """Run the Enhanced Data Visualization tool."""
    try:
        # Add the current directory to the Python path
        sys.path.insert(0, os.getcwd())
        
        # Import the database service
        from database_service import DatabaseService
        
        # Create the database service
        db_service = DatabaseService("data/pool_data.db")
        
        # Create the root window
        root = tk.Tk()
        root.title("Deep Blue Pool Chemistry - Enhanced Data Visualization")
        root.geometry("1200x800")
        
        # Set icon if available
        icon_path = os.path.join("assests", "chemistry.png")
        if os.path.exists(icon_path):
            try:
                icon = tk.PhotoImage(file=icon_path)
                root.iconphoto(True, icon)
            except Exception as e:
                logger.warning(f"Failed to load icon: {e}")
        
        # Import the enhanced data visualization
        from enhanced_data_visualization import EnhancedDataVisualization
        
        # Initialize the enhanced data visualization
        visualizer = EnhancedDataVisualization(db_service, root)
        
        logger.info("Enhanced Data Visualization initialized successfully")
        
        # Start the main loop
        root.mainloop()
        
        return True
    except Exception as e:
        logger.error(f"Error running Enhanced Data Visualization: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Run Deep Blue Pool Chemistry Enhanced Data Visualization")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    args = parser.parse_args()
    
    # Set log level
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Debug logging enabled")
    
    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)
    
    # Run the enhanced data visualization
    success = run_enhanced_visualization()
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
