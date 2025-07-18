
#!/usr/bin/env python3
"""
Responsive Design Utilities for Deep Blue Pool Chemistry application.

This module provides utilities for creating responsive UI elements
that adapt to different screen sizes and orientations.
"""

import tkinter as tk
from tkinter import ttk
import logging
from typing import Dict, Any, List, Tuple, Optional, Callable

# Configure logger
logger = logging.getLogger(__name__)

class ResponsiveDesign:
    """
    Responsive design utilities for Tkinter interfaces.
    
    This class provides methods for creating responsive UI elements
    that adapt to different screen sizes and orientations.
    
    Attributes:
        root: Tkinter root window
        min_width: Minimum window width
        min_height: Minimum window height
        breakpoints: Dictionary of screen size breakpoints
    """
    
    def __init__(self, root: tk.Tk, min_width: int = 800, min_height: int = 600):
        """
        Initialize the responsive design utilities.
        
        Args:
            root: Tkinter root window
            min_width: Minimum window width
            min_height: Minimum window height
        """
        self.root = root
        self.min_width = min_width
        self.min_height = min_height
        
        # Define breakpoints for different screen sizes
        self.breakpoints = {
            "small": 800,    # Mobile phones and small tablets
            "medium": 1200,  # Tablets and small laptops
            "large": 1600    # Large laptops and desktops
        }
        
        # Set minimum window size
        self.root.minsize(min_width, min_height)
        
        # Track window size changes
        self.current_width = self.root.winfo_width()
        self.current_height = self.root.winfo_height()
        
        # Bind resize event
        self.root.bind("<Configure>", self._on_window_resize)
        
        # Store responsive callbacks
        self.responsive_callbacks = []
        
        logger.info("Responsive design utilities initialized")
    
    def _on_window_resize(self, event):
        """
        Handle window resize events.
        
        Args:
            event: Tkinter event object
        """
        # Only handle events from the root window
        if event.widget != self.root:
            return
        
        # Check if size has changed significantly
        if (abs(event.width - self.current_width) > 10 or 
            abs(event.height - self.current_height) > 10):
            
            self.current_width = event.width
            self.current_height = event.height
            
            # Call all registered callbacks
            for callback in self.responsive_callbacks:
                try:
                    callback(event.width, event.height)
                except Exception as e:
                    logger.error(f"Error in responsive callback: {e}")
    
    def register_responsive_callback(self, callback: Callable[[int, int], None]):
        """
        Register a callback function to be called when the window size changes.
        
        Args:
            callback: Function to call with (width, height) parameters
        """
        if callback not in self.responsive_callbacks:
            self.responsive_callbacks.append(callback)
    
    def unregister_responsive_callback(self, callback: Callable[[int, int], None]):
        """
        Unregister a previously registered callback function.
        
        Args:
            callback: Function to remove from callbacks
        """
        if callback in self.responsive_callbacks:
            self.responsive_callbacks.remove(callback)
    
    def get_screen_size_category(self) -> str:
        """
        Get the current screen size category based on breakpoints.
        
        Returns:
            String representing the screen size category: "small", "medium", or "large"
        """
        width = self.root.winfo_width()
        
        if width < self.breakpoints["small"]:
            return "small"
        elif width < self.breakpoints["medium"]:
            return "medium"
        else:
            return "large"
    
    def create_responsive_frame(self, parent: tk.Widget, padding: int = 10) -> ttk.Frame:
        """
        Create a responsive frame that adapts to different screen sizes.
        
        Args:
            parent: Parent widget
            padding: Frame padding
            
        Returns:
            A ttk.Frame configured for responsive layout
        """
        frame = ttk.Frame(parent, padding=padding)
        
        # Make the frame expand to fill available space
        frame.pack(fill=tk.BOTH, expand=True)
        
        return frame
    
    def create_responsive_grid(self, parent: tk.Widget, columns: int = 2, padding: int = 10) -> ttk.Frame:
        """
        Create a responsive grid layout that adapts to different screen sizes.
        
        Args:
            parent: Parent widget
            columns: Number of columns in the grid
            padding: Grid padding
            
        Returns:
            A ttk.Frame configured for responsive grid layout
        """
        frame = ttk.Frame(parent, padding=padding)
        
        # Configure grid columns
        for i in range(columns):
            frame.columnconfigure(i, weight=1)
        
        # Make the frame expand to fill available space
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Store the number of columns for later use
        frame.columns = columns
        
        # Register a callback to adjust the grid layout on resize
        def adjust_grid(width, height):
            # Adjust number of columns based on width
            if width < self.breakpoints["small"]:
                new_columns = 1
            elif width < self.breakpoints["medium"]:
                new_columns = min(2, columns)
            else:
                new_columns = columns
            
            # Only reconfigure if the number of columns has changed
            if new_columns != getattr(frame, 'current_columns', columns):
                frame.current_columns = new_columns
                
                # Reconfigure grid
                for i in range(max(columns, new_columns)):
                    weight = 1 if i < new_columns else 0
                    frame.columnconfigure(i, weight=weight)
                
                # Rearrange children
                for i, child in enumerate(frame.winfo_children()):
                    row = i // new_columns
                    col = i % new_columns
                    child.grid(row=row, column=col, sticky="nsew", padx=5, pady=5)
        
        # Register the callback
        self.register_responsive_callback(adjust_grid)
        
        # Store the callback for later removal
        frame.adjust_grid_callback = adjust_grid
        
        # Call once to initialize
        adjust_grid(self.root.winfo_width(), self.root.winfo_height())
        
        return frame
    
    def create_responsive_notebook(self, parent: tk.Widget) -> ttk.Notebook:
        """
        Create a responsive notebook that adapts to different screen sizes.
        
        Args:
            parent: Parent widget
            
        Returns:
            A ttk.Notebook configured for responsive layout
        """
        notebook = ttk.Notebook(parent)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Register a callback to adjust the notebook on resize
        def adjust_notebook(width, height):
            # Adjust tab appearance based on width
            if width < self.breakpoints["small"]:
                # For small screens, use icons only or shorter text
                for i, tab in enumerate(notebook.tabs()):
                    tab_text = notebook.tab(tab, "text")
                    if tab_text and len(tab_text) > 10:
                        # Store original text if not already stored
                        if not hasattr(notebook, f"original_text_{i}"):
                            setattr(notebook, f"original_text_{i}", tab_text)
                        
                        # Use shorter text
                        notebook.tab(tab, text=tab_text[:7] + "...")
            else:
                # For larger screens, use full text
                for i, tab in enumerate(notebook.tabs()):
                    if hasattr(notebook, f"original_text_{i}"):
                        original_text = getattr(notebook, f"original_text_{i}")
                        notebook.tab(tab, text=original_text)
        
        # Register the callback
        self.register_responsive_callback(adjust_notebook)
        
        # Store the callback for later removal
        notebook.adjust_notebook_callback = adjust_notebook
        
        return notebook
    
    def create_responsive_form(self, parent: tk.Widget, padding: int = 10) -> ttk.Frame:
        """
        Create a responsive form layout that adapts to different screen sizes.
        
        Args:
            parent: Parent widget
            padding: Form padding
            
        Returns:
            A ttk.Frame configured for responsive form layout
        """
        frame = ttk.Frame(parent, padding=padding)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Configure grid
        frame.columnconfigure(0, weight=0)  # Label column
        frame.columnconfigure(1, weight=1)  # Input column
        
        # Register a callback to adjust the form layout on resize
        def adjust_form(width, height):
            # Adjust form layout based on width
            if width < self.breakpoints["small"]:
                # For small screens, stack labels and inputs vertically
                for i, child in enumerate(frame.winfo_children()):
                    grid_info = child.grid_info()
                    if grid_info:
                        row = grid_info.get('row', 0)
                        column = grid_info.get('column', 0)
                        
                        # If this is a label (column 0), adjust its layout
                        if column == 0:
                            child.grid(row=row*2, column=0, sticky="w", padx=5, pady=(5, 0))
                        # If this is an input (column 1), adjust its layout
                        elif column == 1:
                            child.grid(row=row*2+1, column=0, sticky="ew", padx=5, pady=(0, 5))
            else:
                # For larger screens, use side-by-side layout
                label_index = 0
                input_index = 0
                
                for child in frame.winfo_children():
                    grid_info = child.grid_info()
                    if grid_info:
                        row = grid_info.get('row', 0)
                        
                        # If this is a label (even row in stacked layout)
                        if row % 2 == 0:
                            child.grid(row=label_index, column=0, sticky="w", padx=5, pady=5)
                            label_index += 1
                        # If this is an input (odd row in stacked layout)
                        else:
                            child.grid(row=input_index, column=1, sticky="ew", padx=5, pady=5)
                            input_index += 1
        
        # Register the callback
        self.register_responsive_callback(adjust_form)
        
        # Store the callback for later removal
        frame.adjust_form_callback = adjust_form
        
        return frame
    
    def create_responsive_button_group(self, parent: tk.Widget, padding: int = 10) -> ttk.Frame:
        """
        Create a responsive button group that adapts to different screen sizes.
        
        Args:
            parent: Parent widget
            padding: Button group padding
            
        Returns:
            A ttk.Frame configured for responsive button layout
        """
        frame = ttk.Frame(parent, padding=padding)
        frame.pack(fill=tk.X)
        
        # Register a callback to adjust the button layout on resize
        def adjust_buttons(width, height):
            # Adjust button layout based on width
            if width < self.breakpoints["small"]:
                # For small screens, stack buttons vertically
                for child in frame.winfo_children():
                    child.pack(fill=tk.X, padx=5, pady=2)
            else:
                # For larger screens, arrange buttons horizontally
                for child in frame.winfo_children():
                    child.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Register the callback
        self.register_responsive_callback(adjust_buttons)
        
        # Store the callback for later removal
        frame.adjust_buttons_callback = adjust_buttons
        
        return frame
    
    def cleanup(self):
        """
        Clean up resources and event bindings.
        """
        # Unbind resize event
        self.root.unbind("<Configure>")
        
        # Clear callbacks
        self.responsive_callbacks.clear()
        
        logger.info("Responsive design utilities cleaned up")
