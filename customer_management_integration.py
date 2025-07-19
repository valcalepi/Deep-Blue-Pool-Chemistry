
#!/usr/bin/env python3
"""
Integration example for the Customer Management UI.

This module demonstrates how to integrate the Customer Management UI
into the main Deep Blue Pool Chemistry application.
"""

import tkinter as tk
from tkinter import ttk

# Import the Customer Management UI
from components.customer_management.ui import create_customer_management_ui

def integrate_customer_management(main_app):
    """
    Integrate the Customer Management UI into the main application.
    
    Args:
        main_app: The main application instance
    """
    # Add a menu item to open the Customer Management UI
    if hasattr(main_app, 'menu_bar'):
        # If the main app has a menu bar, add a menu item
        customer_menu = tk.Menu(main_app.menu_bar, tearoff=0)
        main_app.menu_bar.add_cascade(label="Customers", menu=customer_menu)
        customer_menu.add_command(label="Customer Management", command=lambda: open_customer_management(main_app))
    
    # Add a button to the main toolbar if it exists
    if hasattr(main_app, 'toolbar'):
        customer_button = ttk.Button(
            main_app.toolbar,
            text="Customers",
            command=lambda: open_customer_management(main_app)
        )
        customer_button.pack(side='left', padx=2)

def open_customer_management(main_app):
    """
    Open the Customer Management UI in a new window.
    
    Args:
        main_app: The main application instance
    """
    # Create a new top-level window
    customer_window = tk.Toplevel(main_app.root)
    customer_window.title("Customer Management")
    customer_window.geometry("1200x800")
    
    # Make it modal (blocks interaction with the main window)
    customer_window.transient(main_app.root)
    customer_window.grab_set()
    
    # Create the Customer Management UI
    customer_ui = create_customer_management_ui(customer_window)
    
    # Wait for the window to be closed
    main_app.root.wait_window(customer_window)

# Example of how to use this in your main application
if __name__ == "__main__":
    # This is just for demonstration purposes
    # In your actual code, you would import this module and call integrate_customer_management
    
    class MainApp:
        def __init__(self):
            self.root = tk.Tk()
            self.root.title("Deep Blue Pool Chemistry")
            self.root.geometry("1000x700")
            
            # Create menu bar
            self.menu_bar = tk.Menu(self.root)
            self.root.config(menu=self.menu_bar)
            
            # Create file menu
            file_menu = tk.Menu(self.menu_bar, tearoff=0)
            self.menu_bar.add_cascade(label="File", menu=file_menu)
            file_menu.add_command(label="Exit", command=self.root.quit)
            
            # Create toolbar
            self.toolbar = ttk.Frame(self.root)
            self.toolbar.pack(side='top', fill='x')
            
            # Add some dummy content
            content = ttk.Frame(self.root)
            content.pack(fill='both', expand=True)
            
            label = ttk.Label(content, text="Main Application Content")
            label.pack(expand=True)
            
            # Integrate customer management
            integrate_customer_management(self)
            
            self.root.mainloop()
    
    # Create and run the main application
    app = MainApp()
