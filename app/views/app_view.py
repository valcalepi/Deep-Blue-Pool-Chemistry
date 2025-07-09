# /views/app_view.py
import logging
import tkinter as tk
from tkinter import ttk
from utils.error_handler import handle_error
from views.pool_view import PoolView
from views.weather_view import WeatherView

class AppView:
    """Main application view using Tkinter."""
    
    def __init__(self, pool_controller, weather_controller):
        self.logger = logging.getLogger(__name__)
        self.pool_controller = pool_controller
        self.weather_controller = weather_controller
        
        # Initialize Tkinter
        self.root = tk.Tk()
        self.root.title("Deep Blue Pool Chemistry")
        self.root.geometry("1024x768")
        
        # Set theme
        self.style = ttk.Style()
        self.style.theme_use('clam')  # Use a modern theme
        
        # Configure styles
        self.configure_styles()
        
        # Initialize views
        self.initialize_views()
    
    @handle_error
    def configure_styles(self):
        """Configure custom styles for the application."""
        self.logger.debug("Configuring UI styles")
        
        # Configure ttk styles for a more modern look
        self.style.configure('TLabel', font=('Helvetica', 12))
        self.style.configure('TButton', font=('Helvetica', 12), padding=5)
        # More style configurations...
    
    @handle_error
    def initialize_views(self):
        """Initialize all views."""
        self.logger.debug("Initializing views")
        
        # Create notebook for tabbed interface
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Add pool view
        self.pool_frame = ttk.Frame(self.notebook)
        self.pool_view = PoolView(self.pool_frame)
        self.notebook.add(self.pool_frame, text='Pool Chemistry')
        
        # Add weather view
        self.weather_frame = ttk.Frame(self.notebook)
        self.weather_view = WeatherView(self.weather_frame)
        self.notebook.add(self.weather_frame, text='Weather Forecast')
        
        # More views...
    
    @handle_error
    def run(self):
        """Run the application."""
        self.logger.info("Starting UI main loop")
        self.root.mainloop()
