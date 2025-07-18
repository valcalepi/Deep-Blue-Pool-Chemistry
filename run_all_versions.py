
#!/usr/bin/env python3
"""
Run script for all versions of the Deep Blue Pool Chemistry application.

This script provides a menu to choose which version of the application to run:
- Standard UI
- Responsive UI
- Enhanced Data Visualization
"""

import os
import sys
import logging
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Any, Optional, List, Callable

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/run_all_versions.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("run_all_versions")

class ApplicationLauncher:
    """
    Application launcher for Deep Blue Pool Chemistry.
    
    This class provides a GUI for launching different versions of the application.
    """
    
    def __init__(self, root: tk.Tk):
        """
        Initialize the application launcher.
        
        Args:
            root: Tkinter root window
        """
        self.root = root
        self.root.title("Deep Blue Pool Chemistry Launcher")
        self.root.geometry("600x400")
        
        # Set icon if available
        icon_path = os.path.join("assests", "chemistry.png")
        if os.path.exists(icon_path):
            try:
                icon = tk.PhotoImage(file=icon_path)
                self.root.iconphoto(True, icon)
            except Exception as e:
                logger.warning(f"Failed to load icon: {e}")
        
        # Create main frame
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Add title
        title = ttk.Label(main_frame, text="Deep Blue Pool Chemistry", font=("Arial", 24))
        title.pack(pady=20)
        
        # Add subtitle
        subtitle = ttk.Label(main_frame, text="Select a version to launch:", font=("Arial", 14))
        subtitle.pack(pady=10)
        
        # Create buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Add buttons
        self.create_launch_button(buttons_frame, "Standard UI", 
                                 "Launch the standard user interface",
                                 self.run_standard_ui)
        
        self.create_launch_button(buttons_frame, "Responsive UI", 
                                 "Launch the responsive user interface (better for mobile devices)",
                                 self.run_responsive_ui)
        
        self.create_launch_button(buttons_frame, "Enhanced Data Visualization", 
                                 "Launch the enhanced data visualization tool",
                                 self.run_enhanced_visualization)
        
        # Add exit button
        exit_button = ttk.Button(main_frame, text="Exit", command=self.root.destroy)
        exit_button.pack(side=tk.RIGHT, pady=10)
        
        logger.info("Application launcher initialized")
    
    def create_launch_button(self, parent: ttk.Frame, text: str, description: str, command: Callable):
        """
        Create a launch button with description.
        
        Args:
            parent: Parent frame
            text: Button text
            description: Button description
            command: Button command
        """
        # Create frame for button and description
        frame = ttk.Frame(parent, padding=10)
        frame.pack(fill=tk.X, pady=5)
        
        # Add button
        button = ttk.Button(frame, text=text, command=command, width=25)
        button.pack(side=tk.LEFT, padx=10)
        
        # Add description
        description_label = ttk.Label(frame, text=description)
        description_label.pack(side=tk.LEFT, padx=10)
    
    def run_standard_ui(self):
        """Run the standard UI."""
        try:
            logger.info("Launching standard UI")
            
            # Run the standard UI
            subprocess.Popen([sys.executable, "run_deep_blue_pool.py"])
            
            # Minimize the launcher window
            self.root.iconify()
        except Exception as e:
            logger.error(f"Error launching standard UI: {e}")
            messagebox.showerror("Launch Error", f"Failed to launch standard UI: {e}")
    
    def run_responsive_ui(self):
        """Run the responsive UI."""
        try:
            logger.info("Launching responsive UI")
            
            # Run the responsive UI
            subprocess.Popen([sys.executable, "run_responsive_ui.py"])
            
            # Minimize the launcher window
            self.root.iconify()
        except Exception as e:
            logger.error(f"Error launching responsive UI: {e}")
            messagebox.showerror("Launch Error", f"Failed to launch responsive UI: {e}")
    
    def run_enhanced_visualization(self):
        """Run the enhanced data visualization."""
        try:
            logger.info("Launching enhanced data visualization")
            
            # Run the enhanced data visualization
            subprocess.Popen([sys.executable, "run_enhanced_visualization.py"])
            
            # Minimize the launcher window
            self.root.iconify()
        except Exception as e:
            logger.error(f"Error launching enhanced data visualization: {e}")
            messagebox.showerror("Launch Error", f"Failed to launch enhanced data visualization: {e}")

def main():
    """Main function."""
    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)
    
    # Create root window
    root = tk.Tk()
    
    # Create application launcher
    launcher = ApplicationLauncher(root)
    
    # Run the application
    root.mainloop()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
