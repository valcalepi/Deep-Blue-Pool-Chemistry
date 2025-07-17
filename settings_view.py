#!/usr/bin/env python3
"""
Settings View for Deep Blue Pool Chemistry

This module provides the UI components for configuring application settings.
"""

import logging
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Any, Optional, Callable

logger = logging.getLogger(__name__)

class SettingsView:
    """
    View for configuring application settings.
    """
    
    def __init__(self, parent, config=None, on_save=None):
        """
        Initialize the settings view.
        
        Args:
            parent: Parent tkinter container
            config: Configuration dictionary
            on_save: Callback function to call when settings are saved
        """
        self.parent = parent
        self.config = config or {}
        self.on_save = on_save
        
        self.frame = ttk.Frame(parent)
        self._create_widgets()
        logger.info("Settings View initialized")
        
    def _create_widgets(self):
        """Create the UI widgets."""
        # Main layout - notebook with tabs
        self.notebook = ttk.Notebook(self.frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create tabs
        self.pool_tab = ttk.Frame(self.notebook)
        self.weather_tab = ttk.Frame(self.notebook)
        self.gui_tab = ttk.Frame(self.notebook)
        
        self.notebook.add(self.pool_tab, text="Pool Settings")
        self.notebook.add(self.weather_tab, text="Weather Settings")
        self.notebook.add(self.gui_tab, text="GUI Settings")
        
        # Create tab content
        self._create_pool_tab()
        self._create_weather_tab()
        self._create_gui_tab()
        
        # Add save button at the bottom
        button_frame = ttk.Frame(self.frame)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(button_frame, text="Save Settings", command=self._save_settings).pack(side=tk.RIGHT)
        ttk.Button(button_frame, text="Reset to Defaults", command=self._reset_defaults).pack(side=tk.RIGHT, padx=10)
        
    def _create_pool_tab(self):
        """Create the pool settings tab content."""
        # Get pool settings from config
        pool_config = self.config.get("pool", {})
        
        # Create form
        form_frame = ttk.Frame(self.pool_tab)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Pool size
        ttk.Label(form_frame, text="Pool Size (gallons):").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.pool_size_var = tk.StringVar(value=str(pool_config.get("size", 15000)))
        ttk.Entry(form_frame, textvariable=self.pool_size_var).grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Pool type
        ttk.Label(form_frame, text="Pool Type:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.pool_type_var = tk.StringVar(value=pool_config.get("type", "chlorine"))
        pool_type_frame = ttk.Frame(form_frame)
        pool_type_frame.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Radiobutton(pool_type_frame, text="Chlorine", variable=self.pool_type_var, value="chlorine").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(pool_type_frame, text="Bromine", variable=self.pool_type_var, value="bromine").pack(side=tk.LEFT, padx=5)
        
        # Pool surface
        ttk.Label(form_frame, text="Pool Surface:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.pool_surface_var = tk.StringVar(value=pool_config.get("surface", "concrete_gunite"))
        surface_combo = ttk.Combobox(form_frame, textvariable=self.pool_surface_var)
        surface_combo.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        surface_combo['values'] = ["concrete_gunite", "vinyl", "fiberglass", "plaster"]
        
        # Indoor/outdoor
        ttk.Label(form_frame, text="Pool Location:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        self.pool_location_var = tk.StringVar(value=pool_config.get("location", "outdoor"))
        location_frame = ttk.Frame(form_frame)
        location_frame.grid(row=3, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Radiobutton(location_frame, text="Outdoor", variable=self.pool_location_var, value="outdoor").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(location_frame, text="Indoor", variable=self.pool_location_var, value="indoor").pack(side=tk.LEFT, padx=5)
        
        # Additional settings
        ttk.Separator(form_frame, orient=tk.HORIZONTAL).grid(row=4, column=0, columnspan=2, sticky=tk.EW, pady=10)
        
        # Use stabilizer
        self.use_stabilizer_var = tk.BooleanVar(value=pool_config.get("use_stabilizer", True))
        ttk.Checkbutton(form_frame, text="Use Cyanuric Acid (Stabilizer)", variable=self.use_stabilizer_var).grid(row=5, column=0, columnspan=2, sticky=tk.W, padx=5, pady=5)
        
        # Salt water pool
        self.salt_water_var = tk.BooleanVar(value=pool_config.get("salt_water", False))
        ttk.Checkbutton(form_frame, text="Salt Water Pool", variable=self.salt_water_var).grid(row=6, column=0, columnspan=2, sticky=tk.W, padx=5, pady=5)
        
    def _create_weather_tab(self):
        """Create the weather settings tab content."""
        # Get weather settings from config
        weather_config = self.config.get("weather", {})
        
        # Create form
        form_frame = ttk.Frame(self.weather_tab)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Location
        ttk.Label(form_frame, text="Location:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.weather_location_var = tk.StringVar(value=weather_config.get("location", "Florida"))
        ttk.Entry(form_frame, textvariable=self.weather_location_var).grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Update interval
        ttk.Label(form_frame, text="Update Interval (seconds):").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.weather_interval_var = tk.StringVar(value=str(weather_config.get("update_interval", 3600)))
        ttk.Entry(form_frame, textvariable=self.weather_interval_var).grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        # API key (if using real API)
        ttk.Label(form_frame, text="Weather API Key (optional):").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.weather_api_key_var = tk.StringVar(value=weather_config.get("api_key", ""))
        ttk.Entry(form_frame, textvariable=self.weather_api_key_var).grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Use real API
        self.use_real_api_var = tk.BooleanVar(value=weather_config.get("use_real_api", False))
        ttk.Checkbutton(form_frame, text="Use Real Weather API", variable=self.use_real_api_var).grid(row=3, column=0, columnspan=2, sticky=tk.W, padx=5, pady=5)
        
        # Weather impact settings
        ttk.Separator(form_frame, orient=tk.HORIZONTAL).grid(row=4, column=0, columnspan=2, sticky=tk.EW, pady=10)
        
        ttk.Label(form_frame, text="Weather Impact Settings", font=("Arial", 10, "bold")).grid(row=5, column=0, columnspan=2, sticky=tk.W, padx=5, pady=5)
        
        # Consider UV impact
        self.consider_uv_var = tk.BooleanVar(value=weather_config.get("consider_uv", True))
        ttk.Checkbutton(form_frame, text="Consider UV Impact on Chemicals", variable=self.consider_uv_var).grid(row=6, column=0, columnspan=2, sticky=tk.W, padx=5, pady=5)
        
        # Consider temperature impact
        self.consider_temp_var = tk.BooleanVar(value=weather_config.get("consider_temperature", True))
        ttk.Checkbutton(form_frame, text="Consider Temperature Impact", variable=self.consider_temp_var).grid(row=7, column=0, columnspan=2, sticky=tk.W, padx=5, pady=5)
        
        # Consider rainfall impact
        self.consider_rain_var = tk.BooleanVar(value=weather_config.get("consider_rainfall", True))
        ttk.Checkbutton(form_frame, text="Consider Rainfall Impact", variable=self.consider_rain_var).grid(row=8, column=0, columnspan=2, sticky=tk.W, padx=5, pady=5)
        
    def _create_gui_tab(self):
        """Create the GUI settings tab content."""
        # Get GUI settings from config
        gui_config = self.config.get("gui", {})
        
        # Create form
        form_frame = ttk.Frame(self.gui_tab)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Theme
        ttk.Label(form_frame, text="Theme:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.gui_theme_var = tk.StringVar(value=gui_config.get("theme", "blue"))
        theme_frame = ttk.Frame(form_frame)
        theme_frame.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Radiobutton(theme_frame, text="Blue", variable=self.gui_theme_var, value="blue").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(theme_frame, text="Light", variable=self.gui_theme_var, value="light").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(theme_frame, text="Dark", variable=self.gui_theme_var, value="dark").pack(side=tk.LEFT, padx=5)
        
        # Refresh rate
        ttk.Label(form_frame, text="Refresh Rate (ms):").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.gui_refresh_var = tk.StringVar(value=str(gui_config.get("refresh_rate", 5000)))
        ttk.Entry(form_frame, textvariable=self.gui_refresh_var).grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Show tooltips
        self.show_tooltips_var = tk.BooleanVar(value=gui_config.get("show_tooltips", True))
        ttk.Checkbutton(form_frame, text="Show Tooltips", variable=self.show_tooltips_var).grid(row=2, column=0, columnspan=2, sticky=tk.W, padx=5, pady=5)
        
        # Show notifications
        self.show_notifications_var = tk.BooleanVar(value=gui_config.get("show_notifications", True))
        ttk.Checkbutton(form_frame, text="Show Notifications", variable=self.show_notifications_var).grid(row=3, column=0, columnspan=2, sticky=tk.W, padx=5, pady=5)
        
        # Advanced settings
        ttk.Separator(form_frame, orient=tk.HORIZONTAL).grid(row=4, column=0, columnspan=2, sticky=tk.EW, pady=10)
        
        ttk.Label(form_frame, text="Advanced Settings", font=("Arial", 10, "bold")).grid(row=5, column=0, columnspan=2, sticky=tk.W, padx=5, pady=5)
        
        # Debug mode
        self.debug_mode_var = tk.BooleanVar(value=gui_config.get("debug_mode", False))
        ttk.Checkbutton(form_frame, text="Debug Mode", variable=self.debug_mode_var).grid(row=6, column=0, columnspan=2, sticky=tk.W, padx=5, pady=5)
        
        # Log level
        ttk.Label(form_frame, text="Log Level:").grid(row=7, column=0, sticky=tk.W, padx=5, pady=5)
        self.log_level_var = tk.StringVar(value=gui_config.get("log_level", "INFO"))
        log_level_combo = ttk.Combobox(form_frame, textvariable=self.log_level_var)
        log_level_combo.grid(row=7, column=1, sticky=tk.W, padx=5, pady=5)
        log_level_combo['values'] = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        
    def _save_settings(self):
        """Save the settings."""
        try:
            # Validate inputs
            try:
                pool_size = int(self.pool_size_var.get())
                if pool_size <= 0:
                    raise ValueError("Pool size must be a positive number")
            except ValueError:
                messagebox.showerror("Error", "Pool size must be a valid number")
                return
                
            try:
                weather_interval = int(self.weather_interval_var.get())
                if weather_interval <= 0:
                    raise ValueError("Weather update interval must be a positive number")
            except ValueError:
                messagebox.showerror("Error", "Weather update interval must be a valid number")
                return
                
            try:
                gui_refresh = int(self.gui_refresh_var.get())
                if gui_refresh <= 0:
                    raise ValueError("GUI refresh rate must be a positive number")
            except ValueError:
                messagebox.showerror("Error", "GUI refresh rate must be a valid number")
                return
                
            # Update config
            new_config = {
                "pool": {
                    "size": int(self.pool_size_var.get()),
                    "type": self.pool_type_var.get(),
                    "surface": self.pool_surface_var.get(),
                    "location": self.pool_location_var.get(),
                    "use_stabilizer": self.use_stabilizer_var.get(),
                    "salt_water": self.salt_water_var.get()
                },
                "weather": {
                    "location": self.weather_location_var.get(),
                    "update_interval": int(self.weather_interval_var.get()),
                    "api_key": self.weather_api_key_var.get(),
                    "use_real_api": self.use_real_api_var.get(),
                    "consider_uv": self.consider_uv_var.get(),
                    "consider_temperature": self.consider_temp_var.get(),
                    "consider_rainfall": self.consider_rain_var.get()
                },
                "gui": {
                    "theme": self.gui_theme_var.get(),
                    "refresh_rate": int(self.gui_refresh_var.get()),
                    "show_tooltips": self.show_tooltips_var.get(),
                    "show_notifications": self.show_notifications_var.get(),
                    "debug_mode": self.debug_mode_var.get(),
                    "log_level": self.log_level_var.get()
                }
            }
            
            # Call on_save callback if provided
            if self.on_save:
                self.on_save(new_config)
                
            messagebox.showinfo("Settings", "Settings saved successfully")
            
        except Exception as e:
            logger.error(f"Error saving settings: {str(e)}")
            messagebox.showerror("Error", f"Failed to save settings: {str(e)}")
            
    def _reset_defaults(self):
        """Reset settings to defaults."""
        if messagebox.askyesno("Reset Settings", "Are you sure you want to reset all settings to defaults?"):
            # Pool settings
            self.pool_size_var.set("15000")
            self.pool_type_var.set("chlorine")
            self.pool_surface_var.set("concrete_gunite")
            self.pool_location_var.set("outdoor")
            self.use_stabilizer_var.set(True)
            self.salt_water_var.set(False)
            
            # Weather settings
            self.weather_location_var.set("Florida")
            self.weather_interval_var.set("3600")
            self.weather_api_key_var.set("")
            self.use_real_api_var.set(False)
            self.consider_uv_var.set(True)
            self.consider_temp_var.set(True)
            self.consider_rain_var.set(True)
            
            # GUI settings
            self.gui_theme_var.set("blue")
            self.gui_refresh_var.set("5000")
            self.show_tooltips_var.set(True)
            self.show_notifications_var.set(True)
            self.debug_mode_var.set(False)
            self.log_level_var.set("INFO")
            
    def pack(self, **kwargs):
        """Pack the frame into its parent."""
        self.frame.pack(**kwargs)
        
    def grid(self, **kwargs):
        """Grid the frame into its parent."""
        self.frame.grid(**kwargs)
        
    def place(self, **kwargs):
        """Place the frame into its parent."""
        self.frame.place(**kwargs)

# Test function
def test_settings_view():
    """Test the settings view."""
    import sys
    
    # Create the root window
    root = tk.Tk()
    root.title("Settings View Test")
    root.geometry("600x500")
    
    # Sample config
    config = {
        "pool": {
            "size": 15000,
            "type": "chlorine",
            "surface": "concrete_gunite",
            "location": "outdoor",
            "use_stabilizer": True,
            "salt_water": False
        },
        "weather": {
            "location": "Florida",
            "update_interval": 3600,
            "api_key": "",
            "use_real_api": False,
            "consider_uv": True,
            "consider_temperature": True,
            "consider_rainfall": True
        },
        "gui": {
            "theme": "blue",
            "refresh_rate": 5000,
            "show_tooltips": True,
            "show_notifications": True,
            "debug_mode": False,
            "log_level": "INFO"
        }
    }
    
    # Create the view
    def on_save(new_config):
        print("Settings saved:")
        print(new_config)
        
    view = SettingsView(root, config=config, on_save=on_save)
    view.pack(fill=tk.BOTH, expand=True)
    
    # Run the application
    root.mainloop()

if __name__ == "__main__":
    test_settings_view()
