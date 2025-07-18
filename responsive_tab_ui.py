
#!/usr/bin/env python3
"""
Responsive Tab-based UI for Deep Blue Pool Chemistry application.

This module provides a responsive tab-based user interface for the Deep Blue Pool Chemistry application,
adapting to different screen sizes and orientations.
"""

import os
import sys
import logging
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime
from typing import Dict, Any, Optional, List, Callable

# Import responsive design utilities
from utils.responsive_design import ResponsiveDesign

# Configure logger
logger = logging.getLogger("responsive_tab_ui")

class ResponsiveTabUI:
    """
    Responsive tab-based user interface for the Deep Blue Pool Chemistry application.
    
    This class provides a tab-based interface that adapts to different screen sizes with the following tabs:
    - Dashboard: Overview of pool status and recent readings
    - Customer Management: Add, edit, and delete customers
    - Test Strip Analysis: Analyze test strips
    - Chemical Calculator: Calculate chemical adjustments
    - Arduino Sensors: Monitor Arduino sensors
    - Weather Impact: Check weather impact on pool chemistry
    
    Attributes:
        root: Tkinter root window
        notebook: Tkinter notebook for tabs
        db_service: Database service instance
        chemical_safety_db: Chemical safety database instance
        test_strip_analyzer: Test strip analyzer instance
        weather_service: Weather service instance
        controller: Pool chemistry controller instance
        responsive: ResponsiveDesign instance for responsive UI
    """
    
    def __init__(self, root: tk.Tk, db_service, chemical_safety_db, test_strip_analyzer, 
                weather_service, controller):
        """
        Initialize the responsive tab-based UI.
        
        Args:
            root: Tkinter root window
            db_service: Database service instance
            chemical_safety_db: Chemical safety database instance
            test_strip_analyzer: Test strip analyzer instance
            weather_service: Weather service instance
            controller: Pool chemistry controller instance
        """
        self.root = root
        self.db_service = db_service
        self.chemical_safety_db = chemical_safety_db
        self.test_strip_analyzer = test_strip_analyzer
        self.weather_service = weather_service
        self.controller = controller
        
        # Set window properties
        self.root.title("Deep Blue Pool Chemistry")
        self.root.geometry("1000x700")
        
        # Set icon if available
        icon_path = os.path.join("assests", "chemistry.png")
        if os.path.exists(icon_path):
            try:
                icon = tk.PhotoImage(file=icon_path)
                self.root.iconphoto(True, icon)
            except Exception as e:
                logger.warning(f"Failed to load icon: {e}")
        
        # Initialize responsive design utilities
        self.responsive = ResponsiveDesign(self.root, min_width=600, min_height=500)
        
        # Create notebook for tabs
        self.notebook = self.responsive.create_responsive_notebook(self.root)
        
        # Create tabs
        self.create_dashboard_tab()
        self.create_customer_management_tab()
        self.create_test_strip_tab()
        self.create_chemical_calculator_tab()
        self.create_arduino_sensors_tab()
        self.create_weather_tab()
        
        # Create exit button at the bottom
        exit_frame = ttk.Frame(self.root)
        exit_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=10, pady=10)
        ttk.Button(exit_frame, text="Exit", command=self.root.destroy).pack(side=tk.RIGHT)
        
        # Register window resize callback
        self.responsive.register_responsive_callback(self.on_window_resize)
        
        logger.info("Responsive tab-based UI initialized")
    
    def on_window_resize(self, width: int, height: int):
        """
        Handle window resize events.
        
        Args:
            width: New window width
            height: New window height
        """
        # Get screen size category
        size_category = self.responsive.get_screen_size_category()
        
        # Adjust UI based on screen size
        if size_category == "small":
            # For small screens (mobile)
            self.adjust_for_small_screen()
        elif size_category == "medium":
            # For medium screens (tablet)
            self.adjust_for_medium_screen()
        else:
            # For large screens (desktop)
            self.adjust_for_large_screen()
    
    def adjust_for_small_screen(self):
        """Adjust UI for small screens (mobile)."""
        # Implement specific adjustments for small screens
        pass
    
    def adjust_for_medium_screen(self):
        """Adjust UI for medium screens (tablet)."""
        # Implement specific adjustments for medium screens
        pass
    
    def adjust_for_large_screen(self):
        """Adjust UI for large screens (desktop)."""
        # Implement specific adjustments for large screens
        pass
    
    def create_dashboard_tab(self):
        """Create the responsive dashboard tab."""
        dashboard_frame = self.responsive.create_responsive_frame(self.notebook)
        self.notebook.add(dashboard_frame, text="Dashboard")
        
        # Add title
        title = ttk.Label(dashboard_frame, text="Deep Blue Pool Chemistry", font=("Arial", 24))
        title.pack(pady=20)
        
        # Add subtitle
        subtitle = ttk.Label(dashboard_frame, text="Pool Chemistry Management System", font=("Arial", 14))
        subtitle.pack(pady=10)
        
        # Create responsive grid for dashboard sections
        dashboard_grid = self.responsive.create_responsive_grid(dashboard_frame, columns=2)
        
        # Create readings frame
        readings_frame = ttk.LabelFrame(dashboard_grid, text="Recent Readings")
        readings_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        # Add recent readings to readings frame
        self.readings_tree = ttk.Treeview(readings_frame, columns=("Date", "pH", "Chlorine", "Alkalinity"), show="headings")
        self.readings_tree.heading("Date", text="Date")
        self.readings_tree.heading("pH", text="pH")
        self.readings_tree.heading("Chlorine", text="Chlorine")
        self.readings_tree.heading("Alkalinity", text="Alkalinity")
        self.readings_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Add scrollbar to treeview
        scrollbar = ttk.Scrollbar(readings_frame, orient="vertical", command=self.readings_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.readings_tree.configure(yscrollcommand=scrollbar.set)
        
        # Create status frame
        status_frame = ttk.LabelFrame(dashboard_grid, text="Pool Status")
        status_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        
        # Add status indicators
        self.ph_status = self.create_status_indicator(status_frame, "pH Level", 0)
        self.chlorine_status = self.create_status_indicator(status_frame, "Chlorine Level", 1)
        self.alkalinity_status = self.create_status_indicator(status_frame, "Alkalinity", 2)
        self.calcium_status = self.create_status_indicator(status_frame, "Calcium Hardness", 3)
        
        # Create quick actions frame
        actions_frame = ttk.LabelFrame(dashboard_frame, text="Quick Actions")
        actions_frame.pack(fill=tk.X, pady=10, padx=10)
        
        # Create responsive button group for quick actions
        action_buttons = self.responsive.create_responsive_button_group(actions_frame)
        
        # Add quick action buttons
        ttk.Button(action_buttons, text="New Test Reading", 
                  command=lambda: self.notebook.select(2)).pack(side=tk.LEFT, padx=5, pady=5)
        
        ttk.Button(action_buttons, text="Calculate Chemicals", 
                  command=lambda: self.notebook.select(3)).pack(side=tk.LEFT, padx=5, pady=5)
        
        ttk.Button(action_buttons, text="Check Weather Impact", 
                  command=lambda: self.notebook.select(5)).pack(side=tk.LEFT, padx=5, pady=5)
        
        ttk.Button(action_buttons, text="Refresh Dashboard", 
                  command=self.refresh_dashboard).pack(side=tk.LEFT, padx=5, pady=5)
        
        # Populate data
        self.update_recent_readings()
        self.update_pool_status()
    
    def create_status_indicator(self, parent, label_text, row):
        """Create a status indicator with label and colored indicator."""
        frame = ttk.Frame(parent)
        frame.grid(row=row, column=0, sticky="w", pady=5)
        
        ttk.Label(frame, text=f"{label_text}:", width=15).pack(side=tk.LEFT)
        
        value_var = tk.StringVar(value="N/A")
        value_label = ttk.Label(frame, textvariable=value_var, width=10)
        value_label.pack(side=tk.LEFT)
        
        status_canvas = tk.Canvas(frame, width=20, height=20)
        status_canvas.pack(side=tk.LEFT, padx=5)
        
        # Draw indicator circle
        indicator = status_canvas.create_oval(2, 2, 18, 18, fill="gray")
        
        return {"label": value_var, "canvas": status_canvas, "indicator": indicator}
    
    def update_status_indicator(self, indicator, value, optimal_range):
        """Update a status indicator based on the value and optimal range."""
        min_val, max_val = optimal_range
        
        if value is None:
            indicator["label"].set("N/A")
            indicator["canvas"].itemconfig(indicator["indicator"], fill="gray")
        else:
            indicator["label"].set(str(value))
            
            if min_val <= value <= max_val:
                # Good - green
                indicator["canvas"].itemconfig(indicator["indicator"], fill="green")
            elif (value < min_val and value >= min_val * 0.8) or (value > max_val and value <= max_val * 1.2):
                # Warning - yellow
                indicator["canvas"].itemconfig(indicator["indicator"], fill="yellow")
            else:
                # Bad - red
                indicator["canvas"].itemconfig(indicator["indicator"], fill="red")
    
    def update_recent_readings(self):
        """Update the recent readings treeview."""
        # Clear existing items
        for item in self.readings_tree.get_children():
            self.readings_tree.delete(item)
        
        # Get recent readings
        readings = self.db_service.get_recent_readings(10)
        
        # Add readings to treeview
        for reading in readings:
            date = datetime.fromisoformat(reading.get("timestamp", "")).strftime("%Y-%m-%d %H:%M")
            ph = reading.get("pH", "N/A")
            chlorine = reading.get("free_chlorine", "N/A")
            alkalinity = reading.get("alkalinity", "N/A")
            
            self.readings_tree.insert("", "end", values=(date, ph, chlorine, alkalinity))
    
    def update_pool_status(self):
        """Update the pool status indicators."""
        # Get the most recent reading
        readings = self.db_service.get_recent_readings(1)
        
        if readings:
            reading = readings[0]
            
            # Update status indicators
            try:
                ph = float(reading.get("pH", "0"))
                self.update_status_indicator(self.ph_status, ph, (7.2, 7.8))
            except (ValueError, TypeError):
                self.update_status_indicator(self.ph_status, None, (0, 0))
            
            try:
                chlorine = float(reading.get("free_chlorine", "0"))
                self.update_status_indicator(self.chlorine_status, chlorine, (1.0, 3.0))
            except (ValueError, TypeError):
                self.update_status_indicator(self.chlorine_status, None, (0, 0))
            
            try:
                alkalinity = float(reading.get("alkalinity", "0"))
                self.update_status_indicator(self.alkalinity_status, alkalinity, (80, 120))
            except (ValueError, TypeError):
                self.update_status_indicator(self.alkalinity_status, None, (0, 0))
            
            try:
                calcium = float(reading.get("calcium", "0"))
                self.update_status_indicator(self.calcium_status, calcium, (200, 400))
            except (ValueError, TypeError):
                self.update_status_indicator(self.calcium_status, None, (0, 0))
        else:
            # No readings available
            self.update_status_indicator(self.ph_status, None, (0, 0))
            self.update_status_indicator(self.chlorine_status, None, (0, 0))
            self.update_status_indicator(self.alkalinity_status, None, (0, 0))
            self.update_status_indicator(self.calcium_status, None, (0, 0))
    
    def refresh_dashboard(self):
        """Refresh the dashboard data."""
        self.update_recent_readings()
        self.update_pool_status()
    
    def create_customer_management_tab(self):
        """Create the responsive customer management tab."""
        customer_frame = self.responsive.create_responsive_frame(self.notebook)
        self.notebook.add(customer_frame, text="Customers")
        
        # Add title
        title = ttk.Label(customer_frame, text="Customer Management", font=("Arial", 18))
        title.pack(pady=10)
        
        # Create search frame
        search_frame = ttk.Frame(customer_frame)
        search_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        ttk.Button(search_frame, text="Search", 
                  command=self.search_customers).pack(side=tk.LEFT)
        
        # Create responsive grid for customer management
        customer_grid = self.responsive.create_responsive_grid(customer_frame, columns=2)
        
        # Create customer list frame (left side)
        list_frame = ttk.LabelFrame(customer_grid, text="Customers")
        list_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        # Customer treeview
        self.customer_tree = ttk.Treeview(list_frame, columns=("ID", "Name", "Phone"), show="headings")
        self.customer_tree.heading("ID", text="ID")
        self.customer_tree.heading("Name", text="Name")
        self.customer_tree.heading("Phone", text="Phone")
        
        self.customer_tree.column("ID", width=50)
        self.customer_tree.column("Name", width=150)
        self.customer_tree.column("Phone", width=100)
        
        self.customer_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Add scrollbar to treeview
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.customer_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.customer_tree.configure(yscrollcommand=scrollbar.set)
        
        # Bind selection event
        self.customer_tree.bind("<<TreeviewSelect>>", self.on_customer_select)
        
        # Customer buttons
        button_frame = self.responsive.create_responsive_button_group(list_frame)
        
        ttk.Button(button_frame, text="Add Customer", 
                  command=self.show_add_customer_form).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="Edit Customer", 
                  command=self.show_edit_customer_form).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="Delete Customer", 
                  command=self.delete_customer).pack(side=tk.LEFT, padx=5)
        
        # Customer details frame (right side)
        self.details_frame = ttk.LabelFrame(customer_grid, text="Customer Details")
        self.details_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        
        # Placeholder for customer details
        self.details_placeholder = ttk.Label(self.details_frame, text="Select a customer to view details")
        self.details_placeholder.pack(pady=20)
        
        # Load customers
        self.load_customers()
    
    def load_customers(self):
        """Load customers into the treeview."""
        # Clear existing items
        for item in self.customer_tree.get_children():
            self.customer_tree.delete(item)
        
        # Get all customers
        customers = self.db_service.get_all_customers()
        
        # Add customers to treeview
        for customer in customers:
            self.customer_tree.insert("", "end", values=(
                customer["id"], 
                customer["name"], 
                customer["phone"]
            ))
    
    def search_customers(self):
        """Search customers based on search term."""
        search_term = self.search_var.get()
        
        if not search_term:
            self.load_customers()
            return
        
        # Clear existing items
        for item in self.customer_tree.get_children():
            self.customer_tree.delete(item)
        
        # Search customers
        customers = self.db_service.search_customers(search_term)
        
        # Add customers to treeview
        for customer in customers:
            self.customer_tree.insert("", "end", values=(
                customer["id"], 
                customer["name"], 
                customer["phone"]
            ))
    
    def on_customer_select(self, event):
        """Handle customer selection event."""
        selection = self.customer_tree.selection()
        if not selection:
            return
        
        # Get selected customer ID
        item = self.customer_tree.item(selection[0])
        customer_id = item["values"][0]
        
        # Get customer details
        customer = self.db_service.get_customer(customer_id)
        if not customer:
            return
        
        # Clear details frame
        for widget in self.details_frame.winfo_children():
            widget.destroy()
        
        # Create responsive frame for details content
        details_content = self.responsive.create_responsive_frame(self.details_frame)
        
        # Customer info section
        info_frame = ttk.LabelFrame(details_content, text="Customer Information")
        info_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(info_frame, text=f"Name: {customer['name']}").pack(anchor=tk.W, padx=5, pady=2)
        ttk.Label(info_frame, text=f"Email: {customer['email']}").pack(anchor=tk.W, padx=5, pady=2)
        ttk.Label(info_frame, text=f"Phone: {customer['phone']}").pack(anchor=tk.W, padx=5, pady=2)
        ttk.Label(info_frame, text=f"Address: {customer['address']}").pack(anchor=tk.W, padx=5, pady=2)
        
        # Pool info section
        pool_info = self.db_service.get_customer_pool_info(customer_id)
        
        pool_frame = ttk.LabelFrame(details_content, text="Pool Information")
        pool_frame.pack(fill=tk.X, pady=5)
        
        if pool_info:
            ttk.Label(pool_frame, text=f"Pool Type: {pool_info['pool_type']}").pack(anchor=tk.W, padx=5, pady=2)
            ttk.Label(pool_frame, text=f"Pool Size: {pool_info['pool_size']} gallons").pack(anchor=tk.W, padx=5, pady=2)
            ttk.Label(pool_frame, text=f"Pool Shape: {pool_info['pool_shape']}").pack(anchor=tk.W, padx=5, pady=2)
            ttk.Label(pool_frame, text=f"Pool Material: {pool_info['pool_material']}").pack(anchor=tk.W, padx=5, pady=2)
        else:
            ttk.Label(pool_frame, text="No pool information available").pack(anchor=tk.W, padx=5, pady=2)
            ttk.Button(pool_frame, text="Add Pool Information", 
                      command=lambda: self.show_add_pool_info_form(customer_id)).pack(anchor=tk.W, padx=5, pady=5)
        
        # Recent readings section
        readings_frame = ttk.LabelFrame(details_content, text="Recent Readings")
        readings_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        readings = self.db_service.get_customer_readings(customer_id, 5)
        
        if readings:
            # Create treeview for readings
            readings_tree = ttk.Treeview(readings_frame, columns=("Date", "pH", "Chlorine", "Alkalinity"), show="headings")
            readings_tree.heading("Date", text="Date")
            readings_tree.heading("pH", text="pH")
            readings_tree.heading("Chlorine", text="Chlorine")
            readings_tree.heading("Alkalinity", text="Alkalinity")
            readings_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            
            # Add scrollbar to treeview
            scrollbar = ttk.Scrollbar(readings_frame, orient="vertical", command=readings_tree.yview)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            readings_tree.configure(yscrollcommand=scrollbar.set)
            
            # Add readings to treeview
            for reading in readings:
                date = datetime.fromisoformat(reading.get("timestamp", "")).strftime("%Y-%m-%d %H:%M")
                ph = reading.get("pH", "N/A")
                chlorine = reading.get("free_chlorine", "N/A")
                alkalinity = reading.get("alkalinity", "N/A")
                
                readings_tree.insert("", "end", values=(date, ph, chlorine, alkalinity))
        else:
            ttk.Label(readings_frame, text="No readings available for this customer").pack(anchor=tk.W, padx=5, pady=2)
        
        # Actions section
        actions_frame = self.responsive.create_responsive_button_group(details_content)
        
        ttk.Button(actions_frame, text="New Reading", 
                  command=lambda: self.show_add_reading_form(customer_id)).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(actions_frame, text="Calculate Chemicals", 
                  command=lambda: self.show_chemical_calculator_for_customer(customer_id)).pack(side=tk.LEFT, padx=5)
    
    def show_add_customer_form(self):
        """Show form to add a new customer."""
        # Create dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Customer")
        dialog.geometry("400x300")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Create responsive form
        form_frame = self.responsive.create_responsive_form(dialog)
        
        # Add title
        title = ttk.Label(form_frame, text="Add New Customer", font=("Arial", 16))
        title.grid(row=0, column=0, columnspan=2, pady=10)
        
        # Add form fields
        ttk.Label(form_frame, text="Name:").grid(row=1, column=0, sticky="w", pady=(10, 0))
        name_var = tk.StringVar()
        name_entry = ttk.Entry(form_frame, textvariable=name_var, width=40)
        name_entry.grid(row=1, column=1, sticky="ew", pady=(10, 0))
        
        ttk.Label(form_frame, text="Email:").grid(row=2, column=0, sticky="w", pady=(5, 0))
        email_var = tk.StringVar()
        email_entry = ttk.Entry(form_frame, textvariable=email_var, width=40)
        email_entry.grid(row=2, column=1, sticky="ew", pady=(5, 0))
        
        ttk.Label(form_frame, text="Phone:").grid(row=3, column=0, sticky="w", pady=(5, 0))
        phone_var = tk.StringVar()
        phone_entry = ttk.Entry(form_frame, textvariable=phone_var, width=40)
        phone_entry.grid(row=3, column=1, sticky="ew", pady=(5, 0))
        
        ttk.Label(form_frame, text="Address:").grid(row=4, column=0, sticky="w", pady=(5, 0))
        address_var = tk.StringVar()
        address_entry = ttk.Entry(form_frame, textvariable=address_var, width=40)
        address_entry.grid(row=4, column=1, sticky="ew", pady=(5, 0))
        
        # Add buttons
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=5, column=0, columnspan=2, sticky="ew", pady=10)
        
        def save_customer():
            name = name_var.get()
            email = email_var.get()
            phone = phone_var.get()
            address = address_var.get()
            
            if not name:
                messagebox.showerror("Error", "Name is required")
                return
            
            try:
                customer_id = self.db_service.add_customer(name, email, phone, address)
                messagebox.showinfo("Success", f"Customer {name} added successfully")
                dialog.destroy()
                self.load_customers()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add customer: {e}")
        
        ttk.Button(button_frame, text="Save", command=save_customer).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.RIGHT, padx=5)
        
        # Set focus to name entry
        name_entry.focus_set()
    
    def show_edit_customer_form(self):
        """Show form to edit a customer."""
        selection = self.customer_tree.selection()
        if not selection:
            messagebox.showinfo("Info", "Please select a customer to edit")
            return
        
        # Get selected customer ID
        item = self.customer_tree.item(selection[0])
        customer_id = item["values"][0]
        
        # Get customer details
        customer = self.db_service.get_customer(customer_id)
        if not customer:
            messagebox.showerror("Error", "Failed to get customer details")
            return
        
        # Create dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Edit Customer")
        dialog.geometry("400x300")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Create responsive form
        form_frame = self.responsive.create_responsive_form(dialog)
        
        # Add title
        title = ttk.Label(form_frame, text="Edit Customer", font=("Arial", 16))
        title.grid(row=0, column=0, columnspan=2, pady=10)
        
        # Add form fields
        ttk.Label(form_frame, text="Name:").grid(row=1, column=0, sticky="w", pady=(10, 0))
        name_var = tk.StringVar(value=customer["name"])
        name_entry = ttk.Entry(form_frame, textvariable=name_var, width=40)
        name_entry.grid(row=1, column=1, sticky="ew", pady=(10, 0))
        
        ttk.Label(form_frame, text="Email:").grid(row=2, column=0, sticky="w", pady=(5, 0))
        email_var = tk.StringVar(value=customer["email"])
        email_entry = ttk.Entry(form_frame, textvariable=email_var, width=40)
        email_entry.grid(row=2, column=1, sticky="ew", pady=(5, 0))
        
        ttk.Label(form_frame, text="Phone:").grid(row=3, column=0, sticky="w", pady=(5, 0))
        phone_var = tk.StringVar(value=customer["phone"])
        phone_entry = ttk.Entry(form_frame, textvariable=phone_var, width=40)
        phone_entry.grid(row=3, column=1, sticky="ew", pady=(5, 0))
        
        ttk.Label(form_frame, text="Address:").grid(row=4, column=0, sticky="w", pady=(5, 0))
        address_var = tk.StringVar(value=customer["address"])
        address_entry = ttk.Entry(form_frame, textvariable=address_var, width=40)
        address_entry.grid(row=4, column=1, sticky="ew", pady=(5, 0))
        
        # Add buttons
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=5, column=0, columnspan=2, sticky="ew", pady=10)
        
        def save_customer():
            name = name_var.get()
            email = email_var.get()
            phone = phone_var.get()
            address = address_var.get()
            
            if not name:
                messagebox.showerror("Error", "Name is required")
                return
            
            try:
                success = self.db_service.update_customer(customer_id, name, email, phone, address)
                if success:
                    messagebox.showinfo("Success", f"Customer {name} updated successfully")
                    dialog.destroy()
                    self.load_customers()
                else:
                    messagebox.showerror("Error", "Failed to update customer")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update customer: {e}")
        
        ttk.Button(button_frame, text="Save", command=save_customer).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.RIGHT, padx=5)
        
        # Set focus to name entry
        name_entry.focus_set()
    
    def delete_customer(self):
        """Delete the selected customer."""
        selection = self.customer_tree.selection()
        if not selection:
            messagebox.showinfo("Info", "Please select a customer to delete")
            return
        
        # Get selected customer ID
        item = self.customer_tree.item(selection[0])
        customer_id = item["values"][0]
        customer_name = item["values"][1]
        
        # Confirm deletion
        if not messagebox.askyesno("Confirm", f"Are you sure you want to delete customer {customer_name}?"):
            return
        
        try:
            success = self.db_service.delete_customer(customer_id)
            if success:
                messagebox.showinfo("Success", f"Customer {customer_name} deleted successfully")
                self.load_customers()
                
                # Clear details frame
                for widget in self.details_frame.winfo_children():
                    widget.destroy()
                
                self.details_placeholder = ttk.Label(self.details_frame, text="Select a customer to view details")
                self.details_placeholder.pack(pady=20)
            else:
                messagebox.showerror("Error", "Failed to delete customer")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete customer: {e}")
    
    def show_add_pool_info_form(self, customer_id):
        """Show form to add pool information for a customer."""
        # Get customer details
        customer = self.db_service.get_customer(customer_id)
        if not customer:
            messagebox.showerror("Error", "Failed to get customer details")
            return
        
        # Create dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Pool Information")
        dialog.geometry("400x350")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Create responsive form
        form_frame = self.responsive.create_responsive_form(dialog)
        
        # Add title
        title = ttk.Label(form_frame, text=f"Add Pool Information for {customer['name']}", font=("Arial", 16))
        title.grid(row=0, column=0, columnspan=2, pady=10)
        
        # Add form fields
        ttk.Label(form_frame, text="Pool Type:").grid(row=1, column=0, sticky="w", pady=(10, 0))
        pool_type_var = tk.StringVar()
        pool_type_combo = ttk.Combobox(form_frame, textvariable=pool_type_var, 
                                      values=["Inground", "Above Ground", "Spa"])
        pool_type_combo.grid(row=1, column=1, sticky="ew", pady=(10, 0))
        
        ttk.Label(form_frame, text="Pool Size (gallons):").grid(row=2, column=0, sticky="w", pady=(5, 0))
        pool_size_var = tk.StringVar()
        pool_size_entry = ttk.Entry(form_frame, textvariable=pool_size_var, width=40)
        pool_size_entry.grid(row=2, column=1, sticky="ew", pady=(5, 0))
        
        ttk.Label(form_frame, text="Pool Shape:").grid(row=3, column=0, sticky="w", pady=(5, 0))
        pool_shape_var = tk.StringVar()
        pool_shape_combo = ttk.Combobox(form_frame, textvariable=pool_shape_var, 
                                       values=["Rectangle", "Oval", "Kidney", "Custom"])
        pool_shape_combo.grid(row=3, column=1, sticky="ew", pady=(5, 0))
        
        ttk.Label(form_frame, text="Pool Material:").grid(row=4, column=0, sticky="w", pady=(5, 0))
        pool_material_var = tk.StringVar()
        pool_material_combo = ttk.Combobox(form_frame, textvariable=pool_material_var, 
                                         values=["Concrete/Gunite", "Vinyl", "Fiberglass"])
        pool_material_combo.grid(row=4, column=1, sticky="ew", pady=(5, 0))
        
        # Add buttons
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=5, column=0, columnspan=2, sticky="ew", pady=10)
        
        def save_pool_info():
            pool_type = pool_type_var.get()
            pool_size = pool_size_var.get()
            pool_shape = pool_shape_var.get()
            pool_material = pool_material_var.get()
            
            if not pool_type or not pool_size:
                messagebox.showerror("Error", "Pool type and size are required")
                return
            
            try:
                pool_info_id = self.db_service.add_pool_info(
                    customer_id, pool_type, pool_size, pool_shape, pool_material
                )
                messagebox.showinfo("Success", "Pool information added successfully")
                dialog.destroy()
                
                # Refresh customer details
                self.on_customer_select(None)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add pool information: {e}")
        
        ttk.Button(button_frame, text="Save", command=save_pool_info).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.RIGHT, padx=5)
        
        # Set focus to pool type combo
        pool_type_combo.focus_set()
    
    def show_add_reading_form(self, customer_id):
        """Show form to add a new reading for a customer."""
        # Get customer details
        customer = self.db_service.get_customer(customer_id)
        if not customer:
            messagebox.showerror("Error", "Failed to get customer details")
            return
        
        # Create dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Reading")
        dialog.geometry("500x600")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Create scrollable canvas for the form
        canvas = tk.Canvas(dialog)
        scrollbar = ttk.Scrollbar(dialog, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Create responsive form
        form_frame = self.responsive.create_responsive_form(scrollable_frame)
        
        # Add title
        title = ttk.Label(form_frame, text=f"New Reading for {customer['name']}", font=("Arial", 16))
        title.grid(row=0, column=0, columnspan=2, pady=10)
        
        # Create a dictionary to store variables
        reading_vars = {}
        
        # Helper function to add a field
        row = 1
        
        def add_field(name, label, default=""):
            nonlocal row
            ttk.Label(form_frame, text=f"{label}:").grid(row=row, column=0, sticky="w", pady=5)
            var = tk.StringVar(value=default)
            reading_vars[name] = var
            ttk.Entry(form_frame, textvariable=var, width=20).grid(row=row, column=1, sticky="ew", pady=5)
            row += 1
        
        # Add fields
        add_field("pH", "pH", "7.2")
        add_field("free_chlorine", "Free Chlorine (ppm)", "1.5")
        add_field("total_chlorine", "Total Chlorine (ppm)", "2.0")
        add_field("alkalinity", "Alkalinity (ppm)", "100")
        add_field("calcium", "Calcium Hardness (ppm)", "250")
        add_field("cyanuric_acid", "Cyanuric Acid (ppm)", "30")
        add_field("bromine", "Bromine (ppm)", "0")
        add_field("salt", "Salt (ppm)", "0")
        add_field("temperature", "Temperature (\u00b0F)", "78")
        
        # Get pool info for water volume
        pool_info = self.db_service.get_customer_pool_info(customer_id)
        default_volume = pool_info["pool_size"] if pool_info else ""
        add_field("water_volume", "Water Volume (gallons)", default_volume)
        
        # Source field
        ttk.Label(form_frame, text="Source:").grid(row=row, column=0, sticky="w", pady=5)
        source_var = tk.StringVar(value="manual")
        source_combo = ttk.Combobox(form_frame, textvariable=source_var, 
                                   values=["manual", "test_strip", "digital_tester"])
        source_combo.grid(row=row, column=1, sticky="ew", pady=5)
        reading_vars["source"] = source_var
        row += 1
        
        # Add buttons
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=row, column=0, columnspan=2, sticky="ew", pady=10)
        
        def save_reading():
            # Create reading data dictionary
            reading_data = {name: var.get() for name, var in reading_vars.items()}
            
            try:
                success = self.db_service.insert_reading(reading_data, customer_id)
                if success:
                    messagebox.showinfo("Success", "Reading added successfully")
                    dialog.destroy()
                    
                    # Refresh customer details
                    self.on_customer_select(None)
                    
                    # Refresh dashboard
                    self.refresh_dashboard()
                else:
                    messagebox.showerror("Error", "Failed to add reading")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add reading: {e}")
        
        ttk.Button(button_frame, text="Save", command=save_reading).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.RIGHT, padx=5)
    
    def show_chemical_calculator_for_customer(self, customer_id):
        """Show chemical calculator for a specific customer."""
        # Get customer details
        customer = self.db_service.get_customer(customer_id)
        if not customer:
            messagebox.showerror("Error", "Failed to get customer details")
            return
        
        # Get pool info
        pool_info = self.db_service.get_customer_pool_info(customer_id)
        if not pool_info:
            messagebox.showinfo("Info", "No pool information available for this customer")
            return
        
        # Get latest reading
        readings = self.db_service.get_customer_readings(customer_id, 1)
        if not readings:
            messagebox.showinfo("Info", "No readings available for this customer")
            return
        
        # Switch to chemical calculator tab
        self.notebook.select(3)
        
        # Pre-fill chemical calculator form with customer data
        if hasattr(self, 'calc_customer_var'):
            self.calc_customer_var.set(f"{customer_id}: {customer['name']}")
            self.on_calc_customer_select(None)
    
    def create_test_strip_tab(self):
        """Create the responsive test strip analysis tab."""
        test_strip_frame = self.responsive.create_responsive_frame(self.notebook)
        self.notebook.add(test_strip_frame, text="Test Strips")
        
        # Add title
        title = ttk.Label(test_strip_frame, text="Test Strip Analysis", font=("Arial", 18))
        title.pack(pady=10)
        
        # Add instructions
        instructions = ttk.Label(test_strip_frame, text="Capture or load an image of your test strip to analyze it.")
        instructions.pack(pady=5)
        
        # Add customer selection
        customer_frame = ttk.Frame(test_strip_frame)
        customer_frame.pack(fill=tk.X, pady=5, padx=10)
        
        ttk.Label(customer_frame, text="Customer:").pack(side=tk.LEFT, padx=5)
        
        self.customer_var = tk.StringVar()
        self.customer_combo = ttk.Combobox(customer_frame, textvariable=self.customer_var, width=30)
        self.customer_combo.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Populate customer combo
        self.populate_customer_combo()
        
        # Add image frame
        image_frame = ttk.LabelFrame(test_strip_frame, text="Test Strip Image")
        image_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Add image label
        self.image_label = ttk.Label(image_frame, text="No image loaded")
        self.image_label.pack(fill=tk.BOTH, expand=True, padx=50, pady=50)
        
        # Image path variable
        self.image_path_var = tk.StringVar()
        
        # Add buttons frame
        buttons_frame = self.responsive.create_responsive_button_group(test_strip_frame)
        
        # Function to load image
        def load_image():
            file_path = filedialog.askopenfilename(
                title="Select Test Strip Image",
                filetypes=[("Image files", "*.jpg *.jpeg *.png")]
            )
            if file_path:
                self.image_path_var.set(file_path)
                self.image_label.config(text=f"Image loaded: {os.path.basename(file_path)}")
                messagebox.showinfo("Image Loaded", f"Image loaded successfully: {os.path.basename(file_path)}")
        
        # Function to capture image
        def capture_image():
            try:
                image_path = self.test_strip_analyzer.capture_image()
                if image_path:
                    self.image_path_var.set(image_path)
                    self.image_label.config(text=f"Image captured: {os.path.basename(image_path)}")
                    messagebox.showinfo("Image Captured", f"Image captured successfully: {os.path.basename(image_path)}")
                else:
                    messagebox.showerror("Error", "Failed to capture image")
            except Exception as e:
                logger.error(f"Error capturing image: {e}")
                messagebox.showerror("Error", f"Failed to capture image: {e}")
        
        # Function to analyze image
        def analyze_image():
            if not self.image_path_var.get():
                messagebox.showerror("Error", "No image loaded or captured")
                return
            
            try:
                # Set the image path for the analyzer
                self.test_strip_analyzer.image_path = self.image_path_var.get()
                
                # Analyze the image
                results = self.test_strip_analyzer.analyze()
                
                if results:
                    # Get selected customer ID
                    customer_id = None
                    if self.customer_var.get():
                        customer_id = int(self.customer_var.get().split(":")[0])
                    
                    # Save results to database
                    if customer_id:
                        self.db_service.insert_reading(results, customer_id)
                    
                    # Create results dialog
                    results_dialog = tk.Toplevel(self.root)
                    results_dialog.title("Analysis Results")
                    results_dialog.geometry("400x400")
                    results_dialog.transient(self.root)
                    results_dialog.grab_set()
                    
                    # Create responsive frame
                    results_frame = self.responsive.create_responsive_frame(results_dialog)
                    
                    # Add title
                    results_title = ttk.Label(results_frame, text="Analysis Results", font=("Arial", 16))
                    results_title.pack(pady=10)
                    
                    # Add results
                    for param, value in results.items():
                        param_name = param.replace("_", " ").title()
                        ttk.Label(results_frame, text=f"{param_name}: {value}").pack(anchor=tk.W, pady=2)
                    
                    # Add recommendations
                    recommendations = self.test_strip_analyzer.get_recommendations(results)
                    
                    if recommendations:
                        ttk.Label(results_frame, text="\
Recommendations:", font=("Arial", 12, "bold")).pack(anchor=tk.W, pady=5)
                        
                        for param, recommendation in recommendations.items():
                            param_name = param.replace("_", " ").title()
                            ttk.Label(results_frame, text=f"{param_name}: {recommendation}").pack(anchor=tk.W, pady=2)
                    
                    # Add close button
                    ttk.Button(results_frame, text="Close", command=results_dialog.destroy).pack(pady=10)
                    
                    # Refresh dashboard
                    self.refresh_dashboard()
                else:
                    messagebox.showerror("Error", "Analysis failed")
            except Exception as e:
                logger.error(f"Error analyzing image: {e}")
                messagebox.showerror("Error", f"Analysis failed: {e}")
        
        # Add buttons
        ttk.Button(buttons_frame, text="Capture Image", command=capture_image).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Load Image", command=load_image).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Analyze", command=analyze_image).pack(side=tk.LEFT, padx=5)
    
    def populate_customer_combo(self):
        """Populate the customer combo box."""
        customers = self.db_service.get_all_customers()
        
        customer_options = [""]  # Empty option for no customer
        for customer in customers:
            customer_options.append(f"{customer['id']}: {customer['name']}")
        
        self.customer_combo["values"] = customer_options
    
    def create_chemical_calculator_tab(self):
        """Create the responsive chemical calculator tab."""
        calculator_frame = self.responsive.create_responsive_frame(self.notebook)
        self.notebook.add(calculator_frame, text="Calculator")
        
        # Add title
        title = ttk.Label(calculator_frame, text="Chemical Calculator", font=("Arial", 18))
        title.pack(pady=10)
        
        # Add instructions
        instructions = ttk.Label(calculator_frame, text="Enter your pool information and test results to calculate chemical adjustments.")
        instructions.pack(pady=5)
        
        # Create main content frame with scrollbar
        content_canvas = tk.Canvas(calculator_frame)
        scrollbar = ttk.Scrollbar(calculator_frame, orient="vertical", command=content_canvas.yview)
        scrollable_frame = ttk.Frame(content_canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: content_canvas.configure(
                scrollregion=content_canvas.bbox("all")
            )
        )
        
        content_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        content_canvas.configure(yscrollcommand=scrollbar.set)
        
        content_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Add customer selection
        customer_frame = ttk.Frame(scrollable_frame)
        customer_frame.pack(fill=tk.X, pady=5, padx=10)
        
        ttk.Label(customer_frame, text="Customer:").pack(side=tk.LEFT, padx=5)
        
        self.calc_customer_var = tk.StringVar()
        self.calc_customer_combo = ttk.Combobox(customer_frame, textvariable=self.calc_customer_var, width=30)
        self.calc_customer_combo.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Populate customer combo
        self.populate_calc_customer_combo()
        
        # Bind customer selection event
        self.calc_customer_combo.bind("<<ComboboxSelected>>", self.on_calc_customer_select)
        
        # Create responsive form for pool info
        pool_frame = ttk.LabelFrame(scrollable_frame, text="Pool Information")
        pool_frame.pack(fill=tk.X, padx=10, pady=5)
        
        pool_form = self.responsive.create_responsive_form(pool_frame)
        
        # Add pool info fields
        ttk.Label(pool_form, text="Pool Type:").grid(row=0, column=0, sticky="w", pady=2)
        self.pool_type_var = tk.StringVar(value="Concrete/Gunite")
        pool_type_combo = ttk.Combobox(pool_form, textvariable=self.pool_type_var, 
                                      values=["Concrete/Gunite", "Vinyl", "Fiberglass"])
        pool_type_combo.grid(row=0, column=1, sticky="ew", pady=2)
        
        ttk.Label(pool_form, text="Pool Size (gallons):").grid(row=1, column=0, sticky="w", pady=2)
        self.pool_size_var = tk.StringVar(value="10000")
        pool_size_entry = ttk.Entry(pool_form, textvariable=self.pool_size_var)
        pool_size_entry.grid(row=1, column=1, sticky="ew", pady=2)
        
        # Create responsive form for test results
        test_frame = ttk.LabelFrame(scrollable_frame, text="Test Results")
        test_frame.pack(fill=tk.X, padx=10, pady=5)
        
        test_form = self.responsive.create_responsive_grid(test_frame, columns=2)
        
        # Add test result fields
        ttk.Label(test_form, text="pH:").grid(row=0, column=0, sticky="w", pady=2)
        self.ph_var = tk.StringVar(value="7.2")
        ph_entry = ttk.Entry(test_form, textvariable=self.ph_var)
        ph_entry.grid(row=0, column=1, sticky="ew", pady=2)
        
        ttk.Label(test_form, text="Free Chlorine (ppm):").grid(row=1, column=0, sticky="w", pady=2)
        self.chlorine_var = tk.StringVar(value="1.5")
        chlorine_entry = ttk.Entry(test_form, textvariable=self.chlorine_var)
        chlorine_entry.grid(row=1, column=1, sticky="ew", pady=2)
        
        ttk.Label(test_form, text="Alkalinity (ppm):").grid(row=2, column=0, sticky="w", pady=2)
        self.alkalinity_var = tk.StringVar(value="100")
        alkalinity_entry = ttk.Entry(test_form, textvariable=self.alkalinity_var)
        alkalinity_entry.grid(row=2, column=1, sticky="ew", pady=2)
        
        ttk.Label(test_form, text="Calcium Hardness (ppm):").grid(row=3, column=0, sticky="w", pady=2)
        self.calcium_var = tk.StringVar(value="250")
        calcium_entry = ttk.Entry(test_form, textvariable=self.calcium_var)
        calcium_entry.grid(row=3, column=1, sticky="ew", pady=2)
        
        ttk.Label(test_form, text="Temperature (\u00b0F):").grid(row=4, column=0, sticky="w", pady=2)
        self.temp_var = tk.StringVar(value="78")
        temp_entry = ttk.Entry(test_form, textvariable=self.temp_var)
        temp_entry.grid(row=4, column=1, sticky="ew", pady=2)
        
        # Add calculate button
        ttk.Button(scrollable_frame, text="Calculate", 
                  command=self.calculate_chemicals).pack(pady=10)
        
        # Add results frame
        self.results_frame = ttk.LabelFrame(scrollable_frame, text="Recommended Adjustments")
        self.results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Add result labels
        self.results_label = ttk.Label(self.results_frame, text="No calculations performed yet.")
        self.results_label.pack(anchor=tk.W, padx=5, pady=2)
    
    def populate_calc_customer_combo(self):
        """Populate the customer combo box in the calculator tab."""
        customers = self.db_service.get_all_customers()
        
        customer_options = [""]  # Empty option for no customer
        for customer in customers:
            customer_options.append(f"{customer['id']}: {customer['name']}")
        
        self.calc_customer_combo["values"] = customer_options
    
    def on_calc_customer_select(self, event):
        """Handle customer selection in calculator tab."""
        if not self.calc_customer_var.get():
            return
        
        try:
            # Get selected customer ID
            customer_id = int(self.calc_customer_var.get().split(":")[0])
            
            # Get pool info
            pool_info = self.db_service.get_customer_pool_info(customer_id)
            if pool_info:
                self.pool_type_var.set(pool_info["pool_type"])
                self.pool_size_var.set(pool_info["pool_size"])
            
            # Get latest reading
            readings = self.db_service.get_customer_readings(customer_id, 1)
            if readings and readings[0]:
                reading = readings[0]
                
                if reading.get("pH"):
                    self.ph_var.set(reading["pH"])
                
                if reading.get("free_chlorine"):
                    self.chlorine_var.set(reading["free_chlorine"])
                
                if reading.get("alkalinity"):
                    self.alkalinity_var.set(reading["alkalinity"])
                
                if reading.get("calcium"):
                    self.calcium_var.set(reading["calcium"])
                
                if reading.get("temperature"):
                    self.temp_var.set(reading["temperature"])
        except Exception as e:
            logger.error(f"Error loading customer data: {e}")
    
    def calculate_chemicals(self):
        """Calculate chemical adjustments."""
        try:
            # Get values from fields
            pool_data = {
                "pool_type": self.pool_type_var.get(),
                "pool_size": self.pool_size_var.get(),
                "ph": self.ph_var.get(),
                "chlorine": self.chlorine_var.get(),
                "alkalinity": self.alkalinity_var.get(),
                "calcium_hardness": self.calcium_var.get(),
                "temperature": self.temp_var.get()
            }
            
            # Validate data
            errors = self.controller.validate_pool_data(pool_data)
            if errors:
                error_message = "\
".join(errors)
                messagebox.showerror("Validation Error", f"Please correct the following errors:\
\
{error_message}")
                return
            
            # Calculate chemicals
            result = self.controller.calculate_chemicals(pool_data)
            
            # Clear results frame
            for widget in self.results_frame.winfo_children():
                widget.destroy()
            
            # Create scrollable frame for results
            results_canvas = tk.Canvas(self.results_frame)
            results_scrollbar = ttk.Scrollbar(self.results_frame, orient="vertical", command=results_canvas.yview)
            results_scrollable_frame = ttk.Frame(results_canvas)
            
            results_scrollable_frame.bind(
                "<Configure>",
                lambda e: results_canvas.configure(
                    scrollregion=results_canvas.bbox("all")
                )
            )
            
            results_canvas.create_window((0, 0), window=results_scrollable_frame, anchor="nw")
            results_canvas.configure(yscrollcommand=results_scrollbar.set)
            
            results_canvas.pack(side="left", fill="both", expand=True)
            results_scrollbar.pack(side="right", fill="y")
            
            # Add results
            if "adjustments" in result:
                adjustments = result["adjustments"]
                
                # Create adjustments frame
                adjustments_frame = ttk.Frame(results_scrollable_frame)
                adjustments_frame.pack(fill=tk.X, pady=5)
                
                # Add adjustments
                ttk.Label(adjustments_frame, text="Chemical Adjustments:", font=("Arial", 12, "bold")).pack(anchor=tk.W, pady=5)
                
                for chemical, amount in adjustments.items():
                    chemical_name = chemical.replace("_", " ").title()
                    ttk.Label(adjustments_frame, text=f"{chemical_name}: {amount} oz").pack(anchor=tk.W, padx=5, pady=2)
            
            if "water_balance" in result:
                balance = result["water_balance"]
                
                # Create balance frame
                balance_frame = ttk.Frame(results_scrollable_frame)
                balance_frame.pack(fill=tk.X, pady=5)
                
                # Add balance info
                ttk.Label(balance_frame, text=f"\
Water Balance Index: {balance:.2f}", font=("Arial", 12, "bold")).pack(anchor=tk.W, pady=5)
                
                if balance < -0.5:
                    ttk.Label(balance_frame, text="Water is corrosive.").pack(anchor=tk.W, padx=5, pady=2)
                elif balance > 0.5:
                    ttk.Label(balance_frame, text="Water is scale-forming.").pack(anchor=tk.W, padx=5, pady=2)
                else:
                    ttk.Label(balance_frame, text="Water is balanced.").pack(anchor=tk.W, padx=5, pady=2)
            
            # Add safety information
            safety_frame = ttk.LabelFrame(results_scrollable_frame, text="Chemical Safety Information")
            safety_frame.pack(fill=tk.X, pady=10)
            
            # Get safety info for each chemical
            if "adjustments" in result:
                for chemical, amount in adjustments.items():
                    if amount > 0:
                        chemical_id = self.get_chemical_id_from_name(chemical)
                        if chemical_id:
                            safety_info = self.chemical_safety_db.get_chemical_safety_info(chemical_id)
                            if safety_info:
                                # Add chemical name
                                ttk.Label(safety_frame, text=f"{safety_info['name']}:", font=("Arial", 10, "bold")).pack(anchor=tk.W, padx=5, pady=2)
                                
                                # Add safety precautions
                                for precaution in safety_info['safety_precautions'][:2]:  # Show only first 2 precautions
                                    ttk.Label(safety_frame, text=f"\u2022 {precaution}").pack(anchor=tk.W, padx=15, pady=1)
            
            # Add treatment steps
            steps_frame = ttk.LabelFrame(results_scrollable_frame, text="Treatment Steps")
            steps_frame.pack(fill=tk.X, pady=10)
            
            if "adjustments" in result:
                adjustments = result["adjustments"]
                
                # Create ordered list of steps
                steps = []
                
                # Step 1: Always adjust alkalinity first
                if "alkalinity_increaser" in adjustments and adjustments["alkalinity_increaser"] > 0:
                    steps.append("Add alkalinity increaser to raise total alkalinity.")
                
                # Step 2: Adjust pH
                if "ph_increaser" in adjustments and adjustments["ph_increaser"] > 0:
                    steps.append("Add pH increaser to raise pH level.")
                elif "ph_decreaser" in adjustments and adjustments["ph_decreaser"] > 0:
                    steps.append("Add pH decreaser to lower pH level.")
                
                # Step 3: Add calcium if needed
                if "calcium_increaser" in adjustments and adjustments["calcium_increaser"] > 0:
                    steps.append("Add calcium increaser to raise calcium hardness.")
                
                # Step 4: Add chlorine last
                if "chlorine" in adjustments and adjustments["chlorine"] > 0:
                    steps.append("Add chlorine to raise chlorine level.")
                
                # Add steps to frame
                for i, step in enumerate(steps):
                    ttk.Label(steps_frame, text=f"{i+1}. {step}").pack(anchor=tk.W, padx=5, pady=2)
                
                # Add general instructions
                ttk.Label(steps_frame, text="\
General Instructions:", font=("Arial", 10, "bold")).pack(anchor=tk.W, padx=5, pady=2)
                ttk.Label(steps_frame, text="\u2022 Wait at least 6 hours between chemical additions").pack(anchor=tk.W, padx=5, pady=1)
                ttk.Label(steps_frame, text="\u2022 Run pump during and after adding chemicals").pack(anchor=tk.W, padx=5, pady=1)
                ttk.Label(steps_frame, text="\u2022 Retest water after 24 hours").pack(anchor=tk.W, padx=5, pady=1)
            
            # Get selected customer ID
            customer_id = None
            if self.calc_customer_var.get():
                try:
                    customer_id = int(self.calc_customer_var.get().split(":")[0])
                except:
                    pass
            
            # Save test results if customer is selected
            if customer_id:
                test_data = {
                    "pH": self.ph_var.get(),
                    "free_chlorine": self.chlorine_var.get(),
                    "alkalinity": self.alkalinity_var.get(),
                    "calcium": self.calcium_var.get(),
                    "temperature": self.temp_var.get(),
                    "source": "manual"
                }
                
                self.db_service.insert_reading(test_data, customer_id)
                
                ttk.Label(results_scrollable_frame, text=f"\
Test results saved for customer.", font=("Arial", 10, "italic")).pack(anchor=tk.W, pady=5)
            
        except Exception as e:
            logger.error(f"Error calculating chemicals: {e}")
            messagebox.showerror("Error", f"Calculation failed: {e}")
    
    def get_chemical_id_from_name(self, chemical_name):
        """Get chemical ID from name."""
        # Map calculator chemical names to safety database IDs
        chemical_map = {
            "ph_increaser": "sodium_bicarbonate",
            "ph_decreaser": "muriatic_acid",
            "alkalinity_increaser": "sodium_bicarbonate",
            "calcium_increaser": "calcium_chloride",
            "chlorine": "chlorine",
            "cyanuric_acid": "cyanuric_acid"
        }
        
        return chemical_map.get(chemical_name)
    
    def create_arduino_sensors_tab(self):
        """Create the responsive Arduino sensors tab."""
        arduino_frame = self.responsive.create_responsive_frame(self.notebook)
        self.notebook.add(arduino_frame, text="Sensors")
        
        # Add title
        title = ttk.Label(arduino_frame, text="Arduino Sensor Monitor", font=("Arial", 18))
        title.pack(pady=10)
        
        # Add status message
        self.arduino_status_var = tk.StringVar(value="Arduino Monitor is not connected")
        status_label = ttk.Label(arduino_frame, textvariable=self.arduino_status_var, font=("Arial", 12))
        status_label.pack(pady=5)
        
        # Create connection frame
        connection_frame = ttk.Frame(arduino_frame)
        connection_frame.pack(fill=tk.X, pady=10, padx=10)
        
        # Add port selection
        ttk.Label(connection_frame, text="Port:").pack(side=tk.LEFT, padx=5)
        
        self.port_var = tk.StringVar()
        self.port_combo = ttk.Combobox(connection_frame, textvariable=self.port_var, width=20)
        self.port_combo.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Create button group for connection controls
        connection_buttons = self.responsive.create_responsive_button_group(connection_frame)
        
        # Add refresh ports button
        ttk.Button(connection_buttons, text="Refresh Ports", 
                  command=self.refresh_ports).pack(side=tk.LEFT, padx=5)
        
        # Add connect button
        self.connect_button = ttk.Button(connection_buttons, text="Connect", 
                                       command=self.connect_arduino)
        self.connect_button.pack(side=tk.LEFT, padx=5)
        
        # Create responsive grid for sensor data
        sensor_grid = self.responsive.create_responsive_grid(arduino_frame, columns=2)
        
        # Create chart frame
        chart_frame = ttk.LabelFrame(sensor_grid, text="Sensor Data Chart")
        chart_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        # Create figure for chart
        self.fig = plt.Figure(figsize=(5, 4), dpi=100)
        self.ax = self.fig.add_subplot(111)
        
        # Create canvas for chart
        self.canvas = FigureCanvasTkAgg(self.fig, master=chart_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Initialize chart
        self.initialize_chart()
        
        # Create data frame
        data_frame = ttk.LabelFrame(sensor_grid, text="Current Readings")
        data_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        
        # Create sensor value labels
        self.ph_value = self.create_sensor_value_label(data_frame, "pH", 0)
        self.temp_value = self.create_sensor_value_label(data_frame, "Temperature", 1)
        self.orp_value = self.create_sensor_value_label(data_frame, "ORP", 2)
        self.tds_value = self.create_sensor_value_label(data_frame, "TDS", 3)
        
        # Refresh ports
        self.refresh_ports()
        
        # Try to import ArduinoSensorManager
        try:
            from arduino_sensor_manager import ArduinoSensorManager
            self.arduino_manager = ArduinoSensorManager()
            
            # Register callbacks
            self.arduino_manager.register_data_callback(self.on_arduino_data)
            self.arduino_manager.register_connection_callback(self.on_arduino_connection)
            
            logger.info("Arduino Sensor Manager initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing Arduino Sensor Manager: {e}")
            self.arduino_status_var.set(f"Error: {str(e)}")
            self.arduino_manager = None
    
    def create_sensor_value_label(self, parent, name, row):
        """Create a sensor value label."""
        frame = ttk.Frame(parent)
        frame.grid(row=row, column=0, sticky="w", pady=5)
        
        ttk.Label(frame, text=f"{name}:").pack(anchor=tk.W)
        
        value_var = tk.StringVar(value="N/A")
        value_label = ttk.Label(frame, textvariable=value_var, font=("Arial", 14, "bold"))
        value_label.pack(anchor=tk.W)
        
        return value_var
    
    def initialize_chart(self):
        """Initialize the chart."""
        self.ax.clear()
        self.ax.set_title("Sensor Data")
        self.ax.set_xlabel("Time")
        self.ax.set_ylabel("Value")
        self.ax.grid(True)
        
        # Create empty data
        self.times = []
        self.ph_data = []
        self.temp_data = []
        
        # Create lines
        self.ph_line, = self.ax.plot(self.times, self.ph_data, 'b-', label='pH')
        self.temp_line, = self.ax.plot(self.times, self.temp_data, 'r-', label='Temp (\u00b0F)')
        
        self.ax.legend()
        self.fig.tight_layout()
        self.canvas.draw()
    
    def refresh_ports(self):
        """Refresh the list of available ports."""
        if hasattr(self, 'arduino_manager') and self.arduino_manager:
            ports = self.arduino_manager.list_available_ports()
            
            port_options = []
            for port, desc in ports:
                port_options.append(f"{port}: {desc}")
            
            self.port_combo["values"] = port_options
            
            if port_options:
                self.port_combo.current(0)
    
    def connect_arduino(self):
        """Connect to the Arduino."""
        if not hasattr(self, 'arduino_manager') or not self.arduino_manager:
            messagebox.showerror("Error", "Arduino Sensor Manager not initialized")
            return
        
        if self.arduino_manager.connected:
            # Disconnect
            self.arduino_manager.disconnect()
            self.connect_button.config(text="Connect")
        else:
            # Connect
            port = self.port_var.get().split(":")[0] if self.port_var.get() else None
            
            if port:
                self.arduino_manager.port = port
                
                if self.arduino_manager.connect():
                    self.arduino_manager.start()
                    self.connect_button.config(text="Disconnect")
                else:
                    messagebox.showerror("Error", "Failed to connect to Arduino")
            else:
                messagebox.showerror("Error", "No port selected")
    
    def on_arduino_connection(self, connected):
        """Handle Arduino connection status change."""
        if connected:
            self.arduino_status_var.set("Arduino Monitor is connected")
            self.connect_button.config(text="Disconnect")
        else:
            self.arduino_status_var.set("Arduino Monitor is not connected")
            self.connect_button.config(text="Connect")
    
    def on_arduino_data(self, data):
        """Handle Arduino data."""
        # Update sensor value labels
        if "pH" in data:
            self.ph_value.set(f"{data['pH']}")
        
        if "temp" in data:
            self.temp_value.set(f"{data['temp']}\u00b0F")
        
        if "orp" in data:
            self.orp_value.set(f"{data['orp']} mV")
        
        if "tds" in data:
            self.tds_value.set(f"{data['tds']} ppm")
        
        # Update chart
        if "pH" in data and "temp" in data:
            # Add current time
            from datetime import datetime
            current_time = datetime.now().strftime("%H:%M:%S")
            
            # Add data to lists
            self.times.append(current_time)
            self.ph_data.append(float(data["pH"]))
            self.temp_data.append(float(data["temp"]))
            
            # Keep only last 20 points
            if len(self.times) > 20:
                self.times = self.times[-20:]
                self.ph_data = self.ph_data[-20:]
                self.temp_data = self.temp_data[-20:]
            
            # Update lines
            self.ph_line.set_data(range(len(self.times)), self.ph_data)
            self.temp_line.set_data(range(len(self.times)), self.temp_data)
            
            # Update axes
            self.ax.set_xlim(0, len(self.times) - 1)
            self.ax.set_xticks(range(len(self.times)))
            self.ax.set_xticklabels(self.times, rotation=45)
            
            # Update y limits
            ph_min = min(self.ph_data) - 0.5 if self.ph_data else 6.5
            ph_max = max(self.ph_data) + 0.5 if self.ph_data else 8.5
            temp_min = min(self.temp_data) - 5 if self.temp_data else 70
            temp_max = max(self.temp_data) + 5 if self.temp_data else 90
            
            self.ax.set_ylim(min(ph_min, temp_min/10), max(ph_max, temp_max/10))
            
            # Draw
            self.fig.tight_layout()
            self.canvas.draw()
    
    def create_weather_tab(self):
        """Create the responsive weather impact tab."""
        weather_frame = self.responsive.create_responsive_frame(self.notebook)
        self.notebook.add(weather_frame, text="Weather")
        
        # Add title
        title = ttk.Label(weather_frame, text="Weather Impact", font=("Arial", 18))
        title.pack(pady=10)
        
        try:
            # Get weather data
            weather_data = self.weather_service.get_weather()
            
            # Create responsive grid for weather information
            weather_grid = self.responsive.create_responsive_grid(weather_frame, columns=2)
            
            # Add current weather frame
            current_frame = ttk.LabelFrame(weather_grid, text="Current Weather")
            current_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
            
            # Add current weather info
            ttk.Label(current_frame, text=f"Location: {self.weather_service.location}").pack(anchor=tk.W, padx=5, pady=2)
            ttk.Label(current_frame, text=f"Temperature: {weather_data.get('temperature', 'Unknown')}\u00b0F").pack(anchor=tk.W, padx=5, pady=2)
            ttk.Label(current_frame, text=f"Humidity: {weather_data.get('humidity', 'Unknown')}%").pack(anchor=tk.W, padx=5, pady=2)
            ttk.Label(current_frame, text=f"Conditions: {weather_data.get('conditions', 'Unknown')}").pack(anchor=tk.W, padx=5, pady=2)
            
            # Get forecast
            forecast = self.weather_service.get_forecast(3)
            
            # Add forecast frame
            forecast_frame = ttk.LabelFrame(weather_grid, text="3-Day Forecast")
            forecast_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
            
            # Add forecast info
            for i, day in enumerate(forecast):
                ttk.Label(forecast_frame, text=f"Day {i+1}: {day.get('temperature', 'Unknown')}\u00b0F, {day.get('conditions', 'Unknown')}").pack(anchor=tk.W, padx=5, pady=2)
            
            # Get weather impact
            impact = self.weather_service.analyze_weather_impact(weather_data)
            
            # Add impact frame
            impact_frame = ttk.LabelFrame(weather_frame, text="Impact on Pool Chemistry")
            impact_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
            
            # Add impact info
            ttk.Label(impact_frame, text=f"\u2022 Evaporation Rate: {impact.get('evaporation_rate', 'Unknown')} inches per day").pack(anchor=tk.W, padx=5, pady=2)
            ttk.Label(impact_frame, text=f"\u2022 Chlorine Loss Rate: {impact.get('chlorine_loss_rate', 'Unknown')}% per day").pack(anchor=tk.W, padx=5, pady=2)
            
            if weather_data.get('temperature', 0) > 85:
                ttk.Label(impact_frame, text="\u2022 Higher temperatures may increase chlorine consumption").pack(anchor=tk.W, padx=5, pady=2)
            
            if weather_data.get('conditions', '').lower() in ['sunny', 'clear']:
                ttk.Label(impact_frame, text="\u2022 UV exposure will degrade chlorine faster").pack(anchor=tk.W, padx=5, pady=2)
            
            if weather_data.get('conditions', '').lower() in ['rain', 'showers', 'thunderstorm']:
                ttk.Label(impact_frame, text="\u2022 Rain may dilute chemicals and affect water balance").pack(anchor=tk.W, padx=5, pady=2)
            else:
                ttk.Label(impact_frame, text="\u2022 No rain expected, so no dilution of chemicals").pack(anchor=tk.W, padx=5, pady=2)
            
            # Add recommendations frame
            recommendations_frame = ttk.LabelFrame(weather_frame, text="Recommendations")
            recommendations_frame.pack(fill=tk.X, padx=10, pady=5)
            
            # Add recommendations based on weather
            if weather_data.get('temperature', 0) > 85:
                ttk.Label(recommendations_frame, text="\u2022 Check chlorine levels more frequently").pack(anchor=tk.W, padx=5, pady=2)
                ttk.Label(recommendations_frame, text="\u2022 Consider using chlorine stabilizer (cyanuric acid)").pack(anchor=tk.W, padx=5, pady=2)
            
            if weather_data.get('conditions', '').lower() in ['sunny', 'clear']:
                ttk.Label(recommendations_frame, text="\u2022 Use pool cover when not in use to reduce UV exposure").pack(anchor=tk.W, padx=5, pady=2)
            
            if weather_data.get('conditions', '').lower() in ['rain', 'showers', 'thunderstorm']:
                ttk.Label(recommendations_frame, text="\u2022 Test water after rain to check for dilution").pack(anchor=tk.W, padx=5, pady=2)
                ttk.Label(recommendations_frame, text="\u2022 Check pH and alkalinity as rain can be acidic").pack(anchor=tk.W, padx=5, pady=2)
            
            # Add refresh button
            ttk.Button(weather_frame, text="Refresh Weather Data", 
                      command=self.refresh_weather_data).pack(pady=10)
            
        except Exception as e:
            logger.error(f"Error getting weather data: {e}")
            ttk.Label(weather_frame, text=f"Error getting weather data: {e}").pack(pady=10)
    
    def refresh_weather_data(self):
        """Refresh weather data and update the tab."""
        # Clear weather cache
        self.weather_service.clear_cache()
        
        # Remove the current weather tab
        self.notebook.forget(5)
        
        # Create a new weather tab
        self.create_weather_tab()
