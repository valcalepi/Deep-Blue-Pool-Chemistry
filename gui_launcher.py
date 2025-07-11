#!/usr/bin/env python3
"""
GUI Launcher for Deep Blue Pool Chemistry
This module initializes and launches the GUI application.
"""
import os
import sys
import logging
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
import threading
import time

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

class SplashScreen:
    """Splash screen shown during application startup."""
    
    def __init__(self, parent):
        self.parent = parent
        self.splash_root = tk.Toplevel(parent)
        self.splash_root.title("Starting Deep Blue Pool Chemistry")
        
        # Remove window decorations
        self.splash_root.overrideredirect(True)
        
        # Set size and position
        width, height = 400, 300
        screen_width = self.splash_root.winfo_screenwidth()
        screen_height = self.splash_root.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.splash_root.geometry(f"{width}x{height}+{x}+{y}")
        
        # Create content
        self.frame = ttk.Frame(self.splash_root)
        self.frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        ttk.Label(
            self.frame, 
            text="Deep Blue Pool Chemistry",
            font=("Helvetica", 16, "bold")
        ).pack(pady=(40, 10))
        
        # Logo or image (placeholder)
        self.canvas = tk.Canvas(self.frame, width=100, height=100, highlightthickness=0)
        self.canvas.pack(pady=10)
        self.canvas.create_oval(10, 10, 90, 90, fill="#2196F3", outline="#1565C0", width=2)
        self.canvas.create_text(50, 50, text="DB", fill="white", font=("Helvetica", 24, "bold"))
        
        # Progress bar
        self.progress = ttk.Progressbar(self.frame, mode="indeterminate", length=300)
        self.progress.pack(pady=20)
        self.progress.start()
        
        # Status message
        self.status_var = tk.StringVar(value="Initializing...")
        self.status_label = ttk.Label(self.frame, textvariable=self.status_var)
        self.status_label.pack(pady=10)
        
        # Version
        ttk.Label(
            self.frame,
            text="Version 1.0.0",
            font=("Helvetica", 8)
        ).pack(side=tk.BOTTOM, pady=10)
        
        # Make sure splash screen appears on top
        self.splash_root.attributes("-topmost", True)
        self.splash_root.update()
    
    def update_status(self, message):
        """Update the status message."""
        self.status_var.set(message)
        self.splash_root.update()
    
    def destroy(self):
        """Close the splash screen."""
        self.splash_root.destroy()

class GUILauncher:
    """Launcher for the Pool Chemistry GUI application."""
    
    def __init__(self):
        """Initialize the launcher."""
        self.root = None
        self.splash = None
        self.app = None
    
    def launch(self):
        """Launch the GUI application."""
        try:
            # Create hidden root window
            self.root = tk.Tk()
            self.root.withdraw()
            
            # Show splash screen
            self.splash = SplashScreen(self.root)
            
            # Start initialization in a separate thread
            threading.Thread(target=self._initialize_app, daemon=True).start()
            
            # Start main loop
            self.root.mainloop()
            
        except Exception as e:
            logger.critical(f"Failed to launch application: {e}", exc_info=True)
            messagebox.showerror("Launch Error", f"Failed to launch application: {e}")
            sys.exit(1)
    
    def _initialize_app(self):
        """Initialize the application components."""
        try:
            # Update import paths
            self._update_import_paths()
            
            # Import required modules
            self.splash.update_status("Loading modules...")
            time.sleep(0.5)  # Simulate loading time
            
            # Import GUI elements
            try:
                from app.gui_elements import PoolChemistryGUI
                self.splash.update_status("GUI modules loaded")
            except ImportError as e:
                logger.error(f"Failed to import GUI modules: {e}")
                self.splash.update_status("Error loading GUI modules")
                self._show_error(f"Failed to import GUI modules: {e}")
                return
            
            # Initialize Arduino interface
            self.splash.update_status("Initializing hardware interfaces...")
            time.sleep(0.5)  # Simulate loading time
            
            # Initialize database
            self.splash.update_status("Connecting to database...")
            time.sleep(0.5)  # Simulate loading time
            
            # Create main application
            self.splash.update_status("Creating application...")
            try:
                self.app = PoolChemistryGUI()
                self.splash.update_status("Application created")
            except Exception as e:
                logger.error(f"Failed to create application: {e}", exc_info=True)
                self.splash.update_status("Error creating application")
                self._show_error(f"Failed to create application: {e}")
                return
            
            # Final setup
            self.splash.update_status("Finalizing setup...")
            time.sleep(0.5)  # Simulate loading time
            
            # Close splash screen and show main window
            self.root.after(0, self._show_main_window)
            
        except Exception as e:
            logger.critical(f"Initialization error: {e}", exc_info=True)
            self.splash.update_status(f"Error: {str(e)}")
            self._show_error(f"Initialization error: {e}")
    
    def _update_import_paths(self):
        """Update Python import paths."""
        # Add project root to path
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if project_root not in sys.path:
            sys.path.insert(0, project_root)
        
        # Add app directory to path
        app_dir = os.path.dirname(os.path.abspath(__file__))
        if app_dir not in sys.path:
            sys.path.insert(0, app_dir)
    
    def _show_main_window(self):
        """Close splash screen and show main application window."""
        try:
            # Destroy splash screen
            if self.splash:
                self.splash.destroy()
            
            # Run the application
            if self.app:
                self.app.run()
                
            # Hide the root window (it's just a container)
            self.root.withdraw()
            
        except Exception as e:
            logger.critical(f"Error showing main window: {e}", exc_info=True)
            self._show_error(f"Error showing main window: {e}")
    
    def _show_error(self, message):
        """Show error message and exit application."""
        def _show():
            messagebox.showerror("Application Error", message)
            self.root.destroy()
        
        self.root.after(0, _show)

def main():
    """Main entry point."""
    launcher = GUILauncher()
    launcher.launch()

if __name__ == "__main__":
    main()