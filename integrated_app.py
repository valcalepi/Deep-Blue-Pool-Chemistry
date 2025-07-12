
#!/usr/bin/env python3
"""
Integrated application for Deep Blue Pool Chemistry
This script combines the pool controller backend with the GUI frontend.
"""
import os
import sys
import logging
import threading
import time
from pathlib import Path
import tkinter as tk
from tkinter import messagebox

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

class IntegratedPoolApp:
    """Integrated application combining backend and frontend."""
    
    def __init__(self):
        """Initialize the integrated application."""
        self.controller = None
        self.gui = None
        self.root = None
        self.splash = None
    
    def start(self):
        """Start the integrated application."""
        try:
            # Set up environment
            setup_environment()
            
            # Create hidden root window for splash screen
            self.root = tk.Tk()
            self.root.withdraw()
            
            # Show splash screen
            self.splash = self._create_splash_screen()
            
            # Start initialization in a separate thread
            threading.Thread(target=self._initialize_app, daemon=True).start()
            
            # Start main loop
            self.root.mainloop()
            
        except Exception as e:
            logger.critical(f"Failed to start application: {e}", exc_info=True)
            messagebox.showerror("Startup Error", f"Failed to start application: {e}")
            sys.exit(1)
    
    def _create_splash_screen(self):
        """Create a splash screen."""
        splash_root = tk.Toplevel(self.root)
        splash_root.title("Starting Deep Blue Pool Chemistry")
        
        # Remove window decorations
        splash_root.overrideredirect(True)
        
        # Set size and position
        width, height = 400, 300
        screen_width = splash_root.winfo_screenwidth()
        screen_height = splash_root.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        splash_root.geometry(f"{width}x{height}+{x}+{y}")
        
        # Create content
        frame = tk.Frame(splash_root, bg="#f0f0f0")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = tk.Label(
            frame, 
            text="Deep Blue Pool Chemistry",
            font=("Helvetica", 16, "bold"),
            bg="#f0f0f0"
        )
        title_label.pack(pady=(40, 10))
        
        # Logo or image (placeholder)
        canvas = tk.Canvas(frame, width=100, height=100, bg="#f0f0f0", highlightthickness=0)
        canvas.pack(pady=10)
        canvas.create_oval(10, 10, 90, 90, fill="#2196F3", outline="#1565C0", width=2)
        canvas.create_text(50, 50, text="DB", fill="white", font=("Helvetica", 24, "bold"))
        
        # Status message
        status_var = tk.StringVar(value="Initializing...")
        status_label = tk.Label(frame, textvariable=status_var, bg="#f0f0f0")
        status_label.pack(pady=10)
        
        # Version
        version_label = tk.Label(
            frame,
            text="Version 1.0.0",
            font=("Helvetica", 8),
            bg="#f0f0f0"
        )
        version_label.pack(side=tk.BOTTOM, pady=10)
        
        # Make sure splash screen appears on top
        splash_root.attributes("-topmost", True)
        splash_root.update()
        
        return {
            "root": splash_root,
            "status_var": status_var,
            "update": lambda msg: status_var.set(msg)
        }
    
    def _initialize_app(self):
        """Initialize the application components."""
        try:
            # Initialize backend controller
            self.splash["update"]("Initializing pool controller...")
            
            # Import the pool controller
            from main_app import PoolController
            
            # Create controller instance
            self.controller = PoolController(config_path="config.json")
            self.splash["update"]("Pool controller initialized")
            
            # Initialize GUI
            self.splash["update"]("Initializing GUI...")
            
            # Import GUI elements
            try:
                from app.gui_elements import PoolChemistryGUI
                self.gui = PoolChemistryGUI()
                
                # Connect GUI to controller
                self._connect_gui_to_controller()
                
                self.splash["update"]("GUI initialized")
            except ImportError as e:
                logger.error(f"Failed to import GUI modules: {e}")
                self.splash["update"]("Error loading GUI modules")
                self._show_error(f"Failed to import GUI modules: {e}")
                return
            
            # Close splash screen and show main window
            time.sleep(1)  # Show splash for at least 1 second
            self.root.after(0, self._show_main_window)
            
        except Exception as e:
            logger.critical(f"Initialization error: {e}", exc_info=True)
            self.splash["update"](f"Error: {str(e)}")
            self._show_error(f"Initialization error: {e}")
    
    def _connect_gui_to_controller(self):
        """Connect the GUI to the controller."""
        # This method would connect GUI events to controller methods
        # For example, when a button is clicked in the GUI, it would call a controller method
        pass
    
    def _show_main_window(self):
        """Close splash screen and show main application window."""
        try:
            # Destroy splash screen
            if self.splash:
                self.splash["root"].destroy()
            
            # Run the GUI
            if self.gui:
                self.gui.run()
                
            # Hide the root window (it's just a container)
            self.root.withdraw()
            
        except Exception as e:
            logger.critical(f"Error showing main window: {e}", exc_info=True)
            self._show_error(f"Error showing main window: {e}")
    
    def _show_error(self, message):
        """Show error message and exit application."""
        def _show():
            messagebox.showerror("Application Error", message)
            if self.splash and hasattr(self.splash, "root"):
                self.splash["root"].destroy()
            self.root.destroy()
        
        self.root.after(0, _show)

def main():
    """Main entry point."""
    app = IntegratedPoolApp()
    app.start()

if __name__ == "__main__":
    main()
