
#!/usr/bin/env python3
"""
Customer Management UI for Deep Blue Pool Chemistry application.

This module provides the UI components for the Customer Management System.
"""

import os
import sys
import logging
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from typing import Dict, Any, Optional, List, Callable, Union
import threading
from datetime import datetime

# Import UI components
from components.ui import (
    theme_manager, Button, TextInput, NumericInput, 
    Dropdown, Checkbox, Card, StatusCard, MetricCard
)

# Import customer management models and database
from components.customer_management.models import Customer, Address, Contact, Pool, ServiceRecord
from components.customer_management.database import CustomerDatabase

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/customer_management_ui.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("CustomerManagement.UI")

class CustomerManagementUI:
    """
    Main UI class for the Customer Management System.
    
    This class provides the main UI components for managing customers, including:
    - Customer list view
    - Customer detail view
    - Add/edit forms for customers, addresses, contacts, pools, and service records
    """
    
    def __init__(self, parent):
        """
        Initialize the Customer Management UI.
        
        Args:
            parent: The parent widget
        """
        self.parent = parent
        self.db = CustomerDatabase()
        
        # Create main frame
        self.main_frame = ttk.Frame(parent)
        self.main_frame.pack(fill='both', expand=True)
        
        # Create split view (customer list on left, details on right)
        self.paned_window = ttk.PanedWindow(self.main_frame, orient=tk.HORIZONTAL)
        self.paned_window.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Create customer list frame
        self.list_frame = ttk.Frame(self.paned_window)
        self.paned_window.add(self.list_frame, weight=1)
        
        # Create customer details frame
        self.details_frame = ttk.Frame(self.paned_window)
        self.paned_window.add(self.details_frame, weight=2)
        
        # Initialize UI components
        self._init_customer_list()
        self._init_customer_details()
        
        # Load customers
        self._load_customers()
    
    def _init_customer_list(self):
        """Initialize the customer list view."""
        # Create header with title and add button
        header_frame = ttk.Frame(self.list_frame)
        header_frame.pack(fill='x', pady=(0, 10))
        
        title_label = ttk.Label(
            header_frame, 
            text="Customers", 
            font=("TkDefaultFont", 16, "bold")
        )
        title_label.pack(side='left')
        
        add_button = Button(
            header_frame,
            text="Add Customer",
            icon="plus",
            command=self._show_add_customer_dialog
        )
        add_button.pack(side='right')
        
        # Create search frame
        search_frame = ttk.Frame(self.list_frame)
        search_frame.pack(fill='x', pady=(0, 10))
        
        self.search_input = TextInput(
            search_frame,
            placeholder="Search customers...",
            on_change=self._filter_customers
        )
        self.search_input.pack(fill='x')
        
        # Create filter frame
        filter_frame = ttk.Frame(self.list_frame)
        filter_frame.pack(fill='x', pady=(0, 10))
        
        # Status filter
        status_label = ttk.Label(filter_frame, text="Status:")
        status_label.pack(side='left', padx=(0, 5))
        
        self.status_filter = Dropdown(
            filter_frame,
            options=["All", "Active", "Inactive", "Prospect"],
            default="All",
            on_change=self._filter_customers
        )
        self.status_filter.pack(side='left', padx=(0, 10))
        
        # Type filter
        type_label = ttk.Label(filter_frame, text="Type:")
        type_label.pack(side='left', padx=(0, 5))
        
        self.type_filter = Dropdown(
            filter_frame,
            options=["All", "Residential", "Commercial"],
            default="All",
            on_change=self._filter_customers
        )
        self.type_filter.pack(side='left')
        
        # Create customers list frame with scrollbar
        list_container = ttk.Frame(self.list_frame)
        list_container.pack(fill='both', expand=True)
        
        self.customers_canvas = tk.Canvas(list_container)
        scrollbar = ttk.Scrollbar(
            list_container, 
            orient="vertical", 
            command=self.customers_canvas.yview
        )
        self.scrollable_frame = ttk.Frame(self.customers_canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.customers_canvas.configure(
                scrollregion=self.customers_canvas.bbox("all")
            )
        )
        
        self.customers_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.customers_canvas.configure(yscrollcommand=scrollbar.set)
        
        self.customers_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def _init_customer_details(self):
        """Initialize the customer details view."""
        # Create header with title
        header_frame = ttk.Frame(self.details_frame)
        header_frame.pack(fill='x', pady=(0, 10))
        
        self.detail_title_label = ttk.Label(
            header_frame, 
            text="Customer Details", 
            font=("TkDefaultFont", 16, "bold")
        )
        self.detail_title_label.pack(side='left')
        
        # Create action buttons
        self.edit_button = Button(
            header_frame,
            text="Edit",
            icon="edit",
            command=self._show_edit_customer_dialog
        )
        self.edit_button.pack(side='right', padx=(0, 5))
        
        self.delete_button = Button(
            header_frame,
            text="Delete",
            icon="trash",
            style="danger",
            command=self._delete_customer
        )
        self.delete_button.pack(side='right', padx=(0, 5))
        
        # Create notebook for tabbed interface
        self.notebook = ttk.Notebook(self.details_frame)
        self.notebook.pack(fill='both', expand=True)
        
        # Create tabs
        self.info_tab = ttk.Frame(self.notebook)
        self.addresses_tab = ttk.Frame(self.notebook)
        self.contacts_tab = ttk.Frame(self.notebook)
        self.pools_tab = ttk.Frame(self.notebook)
        self.service_history_tab = ttk.Frame(self.notebook)
        
        self.notebook.add(self.info_tab, text="Information")
        self.notebook.add(self.addresses_tab, text="Addresses")
        self.notebook.add(self.contacts_tab, text="Contacts")
        self.notebook.add(self.pools_tab, text="Pools")
        self.notebook.add(self.service_history_tab, text="Service History")
        
        # Initialize tab contents
        self._init_info_tab()
        self._init_addresses_tab()
        self._init_contacts_tab()
        self._init_pools_tab()
        self._init_service_history_tab()
        
        # Hide details initially
        self._hide_customer_details()
    
    def _init_info_tab(self):
        """Initialize the information tab."""
        # Create content frame with padding
        content_frame = ttk.Frame(self.info_tab, padding=10)
        content_frame.pack(fill='both', expand=True)
        
        # Customer information
        info_frame = ttk.Frame(content_frame)
        info_frame.pack(fill='x', pady=(0, 10))
        
        # Customer name
        name_frame = ttk.Frame(info_frame)
        name_frame.pack(fill='x', pady=(0, 10))
        
        name_label = ttk.Label(
            name_frame, 
            text="Name:", 
            width=15, 
            anchor='w'
        )
        name_label.pack(side='left')
        
        self.customer_name_label = ttk.Label(name_frame, text="")
        self.customer_name_label.pack(side='left', fill='x', expand=True)
        
        # Customer type
        type_frame = ttk.Frame(info_frame)
        type_frame.pack(fill='x', pady=(0, 10))
        
        type_label = ttk.Label(
            type_frame, 
            text="Type:", 
            width=15, 
            anchor='w'
        )
        type_label.pack(side='left')
        
        self.customer_type_label = ttk.Label(type_frame, text="")
        self.customer_type_label.pack(side='left', fill='x', expand=True)
        
        # Company name (for commercial customers)
        company_frame = ttk.Frame(info_frame)
        company_frame.pack(fill='x', pady=(0, 10))
        
        company_label = ttk.Label(
            company_frame, 
            text="Company:", 
            width=15, 
            anchor='w'
        )
        company_label.pack(side='left')
        
        self.company_name_label = ttk.Label(company_frame, text="")
        self.company_name_label.pack(side='left', fill='x', expand=True)
        
        # Status
        status_frame = ttk.Frame(info_frame)
        status_frame.pack(fill='x', pady=(0, 10))
        
        status_label = ttk.Label(
            status_frame, 
            text="Status:", 
            width=15, 
            anchor='w'
        )
        status_label.pack(side='left')
        
        self.status_label = ttk.Label(status_frame, text="")
        self.status_label.pack(side='left', fill='x', expand=True)
        
        # Created date
        created_frame = ttk.Frame(info_frame)
        created_frame.pack(fill='x', pady=(0, 10))
        
        created_label = ttk.Label(
            created_frame, 
            text="Created:", 
            width=15, 
            anchor='w'
        )
        created_label.pack(side='left')
        
        self.created_label = ttk.Label(created_frame, text="")
        self.created_label.pack(side='left', fill='x', expand=True)
        
        # Updated date
        updated_frame = ttk.Frame(info_frame)
        updated_frame.pack(fill='x', pady=(0, 10))
        
        updated_label = ttk.Label(
            updated_frame, 
            text="Updated:", 
            width=15, 
            anchor='w'
        )
        updated_label.pack(side='left')
        
        self.updated_label = ttk.Label(updated_frame, text="")
        self.updated_label.pack(side='left', fill='x', expand=True)
        
        # Notes
        notes_frame = ttk.Frame(info_frame)
        notes_frame.pack(fill='x', pady=(0, 10))
        
        notes_label = ttk.Label(
            notes_frame, 
            text="Notes:", 
            width=15, 
            anchor='nw'
        )
        notes_label.pack(side='left', anchor='n')
        
        notes_container = ttk.Frame(notes_frame)
        notes_container.pack(side='left', fill='both', expand=True)
        
        self.notes_text = tk.Text(
            notes_container, 
            wrap='word', 
            height=5, 
            width=40
        )
        self.notes_text.pack(fill='both', expand=True)
        self.notes_text.config(state='disabled')
        
        # Tags
        tags_frame = ttk.Frame(info_frame)
        tags_frame.pack(fill='x', pady=(0, 10))
        
        tags_label = ttk.Label(
            tags_frame, 
            text="Tags:", 
            width=15, 
            anchor='w'
        )
        tags_label.pack(side='left')
        
        self.tags_label = ttk.Label(tags_frame, text="")
        self.tags_label.pack(side='left', fill='x', expand=True)
    
    def _init_addresses_tab(self):
        """Initialize the addresses tab."""
        # Create content frame with padding
        content_frame = ttk.Frame(self.addresses_tab, padding=10)
        content_frame.pack(fill='both', expand=True)
        
        # Create header with title and add button
        header_frame = ttk.Frame(content_frame)
        header_frame.pack(fill='x', pady=(0, 10))
        
        title_label = ttk.Label(
            header_frame, 
            text="Customer Addresses", 
            font=("TkDefaultFont", 12, "bold")
        )
        title_label.pack(side='left')
        
        self.add_address_button = Button(
            header_frame,
            text="Add Address",
            icon="plus",
            command=self._show_add_address_dialog
        )
        self.add_address_button.pack(side='right')
        
        # Create addresses list frame with scrollbar
        list_container = ttk.Frame(content_frame)
        list_container.pack(fill='both', expand=True)
        
        self.addresses_canvas = tk.Canvas(list_container)
        scrollbar = ttk.Scrollbar(
            list_container, 
            orient="vertical", 
            command=self.addresses_canvas.yview
        )
        self.addresses_scrollable_frame = ttk.Frame(self.addresses_canvas)
        
        self.addresses_scrollable_frame.bind(
            "<Configure>",
            lambda e: self.addresses_canvas.configure(
                scrollregion=self.addresses_canvas.bbox("all")
            )
        )
        
        self.addresses_canvas.create_window((0, 0), window=self.addresses_scrollable_frame, anchor="nw")
        self.addresses_canvas.configure(yscrollcommand=scrollbar.set)
        
        self.addresses_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def _init_contacts_tab(self):
        """Initialize the contacts tab."""
        # Create content frame with padding
        content_frame = ttk.Frame(self.contacts_tab, padding=10)
        content_frame.pack(fill='both', expand=True)
        
        # Create header with title and add button
        header_frame = ttk.Frame(content_frame)
        header_frame.pack(fill='x', pady=(0, 10))
        
        title_label = ttk.Label(
            header_frame, 
            text="Customer Contacts", 
            font=("TkDefaultFont", 12, "bold")
        )
        title_label.pack(side='left')
        
        self.add_contact_button = Button(
            header_frame,
            text="Add Contact",
            icon="plus",
            command=self._show_add_contact_dialog
        )
        self.add_contact_button.pack(side='right')
        
        # Create contacts list frame with scrollbar
        list_container = ttk.Frame(content_frame)
        list_container.pack(fill='both', expand=True)
        
        self.contacts_canvas = tk.Canvas(list_container)
        scrollbar = ttk.Scrollbar(
            list_container, 
            orient="vertical", 
            command=self.contacts_canvas.yview
        )
        self.contacts_scrollable_frame = ttk.Frame(self.contacts_canvas)
        
        self.contacts_scrollable_frame.bind(
            "<Configure>",
            lambda e: self.contacts_canvas.configure(
                scrollregion=self.contacts_canvas.bbox("all")
            )
        )
        
        self.contacts_canvas.create_window((0, 0), window=self.contacts_scrollable_frame, anchor="nw")
        self.contacts_canvas.configure(yscrollcommand=scrollbar.set)
        
        self.contacts_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def _init_pools_tab(self):
        """Initialize the pools tab."""
        # Create content frame with padding
        content_frame = ttk.Frame(self.pools_tab, padding=10)
        content_frame.pack(fill='both', expand=True)
        
        # Create header with title and add button
        header_frame = ttk.Frame(content_frame)
        header_frame.pack(fill='x', pady=(0, 10))
        
        title_label = ttk.Label(
            header_frame, 
            text="Customer Pools", 
            font=("TkDefaultFont", 12, "bold")
        )
        title_label.pack(side='left')
        
        self.add_pool_button = Button(
            header_frame,
            text="Add Pool",
            icon="plus",
            command=self._show_add_pool_dialog
        )
        self.add_pool_button.pack(side='right')
        
        # Create pools list frame with scrollbar
        list_container = ttk.Frame(content_frame)
        list_container.pack(fill='both', expand=True)
        
        self.pools_canvas = tk.Canvas(list_container)
        scrollbar = ttk.Scrollbar(
            list_container, 
            orient="vertical", 
            command=self.pools_canvas.yview
        )
        self.pools_scrollable_frame = ttk.Frame(self.pools_canvas)
        
        self.pools_scrollable_frame.bind(
            "<Configure>",
            lambda e: self.pools_canvas.configure(
                scrollregion=self.pools_canvas.bbox("all")
            )
        )
        
        self.pools_canvas.create_window((0, 0), window=self.pools_scrollable_frame, anchor="nw")
        self.pools_canvas.configure(yscrollcommand=scrollbar.set)
        
        self.pools_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def _init_service_history_tab(self):
        """Initialize the service history tab."""
        # Create content frame with padding
        content_frame = ttk.Frame(self.service_history_tab, padding=10)
        content_frame.pack(fill='both', expand=True)
        
        # Create header with title and add button
        header_frame = ttk.Frame(content_frame)
        header_frame.pack(fill='x', pady=(0, 10))
        
        title_label = ttk.Label(
            header_frame, 
            text="Service History", 
            font=("TkDefaultFont", 12, "bold")
        )
        title_label.pack(side='left')
        
        self.add_service_button = Button(
            header_frame,
            text="Add Service Record",
            icon="plus",
            command=self._show_add_service_record_dialog
        )
        self.add_service_button.pack(side='right')
        
        # Create filter frame
        filter_frame = ttk.Frame(content_frame)
        filter_frame.pack(fill='x', pady=(0, 10))
        
        # Date range filter
        from_label = ttk.Label(filter_frame, text="From:")
        from_label.pack(side='left', padx=(0, 5))
        
        self.from_date_input = TextInput(
            filter_frame,
            placeholder="YYYY-MM-DD",
            width=12
        )
        self.from_date_input.pack(side='left', padx=(0, 10))
        
        to_label = ttk.Label(filter_frame, text="To:")
        to_label.pack(side='left', padx=(0, 5))
        
        self.to_date_input = TextInput(
            filter_frame,
            placeholder="YYYY-MM-DD",
            width=12
        )
        self.to_date_input.pack(side='left', padx=(0, 10))
        
        filter_button = Button(
            filter_frame,
            text="Filter",
            command=self._filter_service_records
        )
        filter_button.pack(side='left')
        
        # Create service records list frame with scrollbar
        list_container = ttk.Frame(content_frame)
        list_container.pack(fill='both', expand=True)
        
        self.service_records_canvas = tk.Canvas(list_container)
        scrollbar = ttk.Scrollbar(
            list_container, 
            orient="vertical", 
            command=self.service_records_canvas.yview
        )
        self.service_records_scrollable_frame = ttk.Frame(self.service_records_canvas)
        
        self.service_records_scrollable_frame.bind(
            "<Configure>",
            lambda e: self.service_records_canvas.configure(
                scrollregion=self.service_records_canvas.bbox("all")
            )
        )
        
        self.service_records_canvas.create_window((0, 0), window=self.service_records_scrollable_frame, anchor="nw")
        self.service_records_canvas.configure(yscrollcommand=scrollbar.set)
        
        self.service_records_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def _load_customers(self):
        """Load customers from the database."""
        # Clear existing customer cards
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        # Get customers from database
        customers = list(self.db.customers.values())
        
        if not customers:
            # Show empty state
            empty_label = ttk.Label(
                self.scrollable_frame,
                text="No customers found. Click 'Add Customer' to create one.",
                font=("TkDefaultFont", 10),
                foreground=theme_manager.get_color("text_secondary")
            )
            empty_label.pack(pady=20)
            return
        
        # Sort customers by name
        customers.sort(key=lambda c: c.last_name.lower())
        
        # Create customer cards
        for customer in customers:
            self._create_customer_card(customer)
    
    def _create_customer_card(self, customer):
        """
        Create a card for a customer in the list view.
        
        Args:
            customer: The customer to create a card for
        """
        # Create a frame for the customer card
        card_frame = ttk.Frame(self.scrollable_frame)
        card_frame.pack(fill='x', pady=5)
        
        # Create a card with customer information
        card = Card(card_frame)
        card.pack(fill='x')
        
        # Add customer information to the card
        content_frame = ttk.Frame(card.content_frame)
        content_frame.pack(fill='x')
        
        # Customer name
        name_label = ttk.Label(
            content_frame,
            text=customer.full_name,
            font=("TkDefaultFont", 12, "bold")
        )
        name_label.pack(anchor='w')
        
        # Customer type and company name (if applicable)
        type_text = customer.customer_type.capitalize()
        if customer.company_name:
            type_text += f" - {customer.company_name}"
        
        type_label = ttk.Label(
            content_frame,
            text=type_text,
            foreground=theme_manager.get_color("text_secondary")
        )
        type_label.pack(anchor='w')
        
        # Customer contact information
        primary_contact = customer.get_primary_contact()
        if primary_contact:
            contact_label = ttk.Label(
                content_frame,
                text=f"{primary_contact.contact_type.capitalize()}: {primary_contact.value}"
            )
            contact_label.pack(anchor='w')
        
        # Customer status
        status_frame = ttk.Frame(content_frame)
        status_frame.pack(anchor='w', pady=(5, 0))
        
        status_color = {
            "active": theme_manager.get_color("success"),
            "inactive": theme_manager.get_color("danger"),
            "prospect": theme_manager.get_color("warning")
        }.get(customer.status.lower(), theme_manager.get_color("text_secondary"))
        
        status_indicator = ttk.Label(
            status_frame,
            text="\u25cf",
            foreground=status_color
        )
        status_indicator.pack(side='left')
        
        status_label = ttk.Label(
            status_frame,
            text=customer.status.capitalize(),
            foreground=theme_manager.get_color("text_secondary")
        )
        status_label.pack(side='left', padx=(5, 0))
        
        # Add click event to the card
        for widget in [card.widget, name_label, type_label, status_frame]:
            widget.bind("<Button-1>", lambda e, c=customer: self._show_customer_details(c))
    
    def _show_customer_details(self, customer):
        """
        Show customer details in the details view.
        
        Args:
            customer: The customer to show details for
        """
        self.current_customer = customer
        
        # Update title
        self.detail_title_label.config(text=customer.full_name)
        
        # Update information tab
        self.customer_name_label.config(text=customer.full_name)
        self.customer_type_label.config(text=customer.customer_type.capitalize())
        self.company_name_label.config(text=customer.company_name or "N/A")
        self.status_label.config(text=customer.status.capitalize())
        
        # Format dates
        created_date = datetime.fromisoformat(customer.created_at).strftime("%Y-%m-%d %H:%M")
        updated_date = datetime.fromisoformat(customer.updated_at).strftime("%Y-%m-%d %H:%M")
        
        self.created_label.config(text=created_date)
        self.updated_label.config(text=updated_date)
        
        # Update notes
        self.notes_text.config(state='normal')
        self.notes_text.delete(1.0, tk.END)
        if customer.notes:
            self.notes_text.insert(tk.END, customer.notes)
        self.notes_text.config(state='disabled')
        
        # Update tags
        self.tags_label.config(text=", ".join(customer.tags) if customer.tags else "None")
        
        # Update addresses tab
        self._load_addresses()
        
        # Update contacts tab
        self._load_contacts()
        
        # Update pools tab
        self._load_pools()
        
        # Update service history tab
        self._load_service_records()
        
        # Show details
        self._show_customer_details_ui()
    
    def _hide_customer_details(self):
        """Hide the customer details view."""
        # Hide action buttons
        self.edit_button.pack_forget()
        self.delete_button.pack_forget()
        
        # Show placeholder
        for widget in self.info_tab.winfo_children():
            widget.destroy()
        
        placeholder_label = ttk.Label(
            self.info_tab,
            text="Select a customer to view details",
            font=("TkDefaultFont", 12)
        )
        placeholder_label.pack(expand=True, pady=50)
    
    def _show_customer_details_ui(self):
        """Show the customer details UI."""
        # Show action buttons
        self.edit_button.pack(side='right', padx=(0, 5))
        self.delete_button.pack(side='right', padx=(0, 5))
    
    def _load_addresses(self):
        """Load customer addresses into the addresses tab."""
        # Clear existing address cards
        for widget in self.addresses_scrollable_frame.winfo_children():
            widget.destroy()
        
        if not self.current_customer.addresses:
            # Show empty state
            empty_label = ttk.Label(
                self.addresses_scrollable_frame,
                text="No addresses found. Click 'Add Address' to create one.",
                font=("TkDefaultFont", 10),
                foreground=theme_manager.get_color("text_secondary")
            )
            empty_label.pack(pady=20)
            return
        
        # Create address cards
        for address in self.current_customer.addresses:
            self._create_address_card(address)
    
    def _create_address_card(self, address):
        """
        Create a card for an address in the addresses tab.
        
        Args:
            address: The address to create a card for
        """
        # Create a frame for the address card
        card_frame = ttk.Frame(self.addresses_scrollable_frame)
        card_frame.pack(fill='x', pady=5)
        
        # Create a card with address information
        card = Card(card_frame)
        card.pack(fill='x')
        
        # Add address information to the card
        content_frame = ttk.Frame(card.content_frame)
        content_frame.pack(fill='x')
        
        # Address type
        type_label = ttk.Label(
            content_frame,
            text=address.address_type.capitalize(),
            font=("TkDefaultFont", 10, "bold"),
            foreground=theme_manager.get_color("primary")
        )
        type_label.pack(anchor='w')
        
        # Street address
        street_label = ttk.Label(
            content_frame,
            text=address.street
        )
        street_label.pack(anchor='w')
        
        # City, state, zip
        location_label = ttk.Label(
            content_frame,
            text=f"{address.city}, {address.state} {address.zip_code}"
        )
        location_label.pack(anchor='w')
        
        # Country (if not USA)
        if address.country.upper() != "USA":
            country_label = ttk.Label(
                content_frame,
                text=address.country
            )
            country_label.pack(anchor='w')
        
        # Action buttons
        button_frame = ttk.Frame(content_frame)
        button_frame.pack(anchor='e', pady=(5, 0))
        
        edit_button = Button(
            button_frame,
            text="Edit",
            size="small",
            command=lambda: self._show_edit_address_dialog(address)
        )
        edit_button.pack(side='left', padx=(0, 5))
        
        delete_button = Button(
            button_frame,
            text="Delete",
            size="small",
            style="danger",
            command=lambda: self._delete_address(address)
        )
        delete_button.pack(side='left')
    
    def _load_contacts(self):
        """Load customer contacts into the contacts tab."""
        # Clear existing contact cards
        for widget in self.contacts_scrollable_frame.winfo_children():
            widget.destroy()
        
        if not self.current_customer.contacts:
            # Show empty state
            empty_label = ttk.Label(
                self.contacts_scrollable_frame,
                text="No contacts found. Click 'Add Contact' to create one.",
                font=("TkDefaultFont", 10),
                foreground=theme_manager.get_color("text_secondary")
            )
            empty_label.pack(pady=20)
            return
        
        # Create contact cards
        for contact in self.current_customer.contacts:
            self._create_contact_card(contact)
    
    def _create_contact_card(self, contact):
        """
        Create a card for a contact in the contacts tab.
        
        Args:
            contact: The contact to create a card for
        """
        # Create a frame for the contact card
        card_frame = ttk.Frame(self.contacts_scrollable_frame)
        card_frame.pack(fill='x', pady=5)
        
        # Create a card with contact information
        card = Card(card_frame)
        card.pack(fill='x')
        
        # Add contact information to the card
        content_frame = ttk.Frame(card.content_frame)
        content_frame.pack(fill='x')
        
        # Contact type and primary indicator
        header_frame = ttk.Frame(content_frame)
        header_frame.pack(fill='x')
        
        type_label = ttk.Label(
            header_frame,
            text=contact.contact_type.capitalize(),
            font=("TkDefaultFont", 10, "bold"),
            foreground=theme_manager.get_color("primary")
        )
        type_label.pack(side='left')
        
        if contact.is_primary:
            primary_label = ttk.Label(
                header_frame,
                text="Primary",
                font=("TkDefaultFont", 8),
                foreground=theme_manager.get_color("success")
            )
            primary_label.pack(side='left', padx=(5, 0))
        
        # Contact value
        value_label = ttk.Label(
            content_frame,
            text=contact.value
        )
        value_label.pack(anchor='w')
        
        # Action buttons
        button_frame = ttk.Frame(content_frame)
        button_frame.pack(anchor='e', pady=(5, 0))
        
        edit_button = Button(
            button_frame,
            text="Edit",
            size="small",
            command=lambda: self._show_edit_contact_dialog(contact)
        )
        edit_button.pack(side='left', padx=(0, 5))
        
        delete_button = Button(
            button_frame,
            text="Delete",
            size="small",
            style="danger",
            command=lambda: self._delete_contact(contact)
        )
        delete_button.pack(side='left')
    
    def _load_pools(self):
        """Load customer pools into the pools tab."""
        # Clear existing pool cards
        for widget in self.pools_scrollable_frame.winfo_children():
            widget.destroy()
        
        if not self.current_customer.pools:
            # Show empty state
            empty_label = ttk.Label(
                self.pools_scrollable_frame,
                text="No pools found. Click 'Add Pool' to create one.",
                font=("TkDefaultFont", 10),
                foreground=theme_manager.get_color("text_secondary")
            )
            empty_label.pack(pady=20)
            return
        
        # Create pool cards
        for pool in self.current_customer.pools:
            self._create_pool_card(pool)
    
    def _create_pool_card(self, pool):
        """
        Create a card for a pool in the pools tab.
        
        Args:
            pool: The pool to create a card for
        """
        # Create a frame for the pool card
        card_frame = ttk.Frame(self.pools_scrollable_frame)
        card_frame.pack(fill='x', pady=5)
        
        # Create a card with pool information
        card = Card(card_frame)
        card.pack(fill='x')
        
        # Add pool information to the card
        content_frame = ttk.Frame(card.content_frame)
        content_frame.pack(fill='x')
        
        # Pool type
        type_label = ttk.Label(
            content_frame,
            text=pool.pool_type.capitalize(),
            font=("TkDefaultFont", 12, "bold")
        )
        type_label.pack(anchor='w')
        
        # Pool details
        details_frame = ttk.Frame(content_frame)
        details_frame.pack(fill='x', pady=(5, 0))
        
        # Size and volume
        size_label = ttk.Label(
            details_frame,
            text=f"Size: {pool.size} sq ft"
        )
        size_label.grid(row=0, column=0, sticky='w', padx=(0, 10))
        
        volume_label = ttk.Label(
            details_frame,
            text=f"Volume: {pool.volume} gallons"
        )
        volume_label.grid(row=0, column=1, sticky='w')
        
        # Sanitizer and surface type
        sanitizer_label = ttk.Label(
            details_frame,
            text=f"Sanitizer: {pool.sanitizer_type}"
        )
        sanitizer_label.grid(row=1, column=0, sticky='w', padx=(0, 10))
        
        if pool.surface_type:
            surface_label = ttk.Label(
                details_frame,
                text=f"Surface: {pool.surface_type}"
            )
            surface_label.grid(row=1, column=1, sticky='w')
        
        # Features
        if pool.features:
            features_label = ttk.Label(
                content_frame,
                text=f"Features: {', '.join(pool.features)}"
            )
            features_label.pack(anchor='w', pady=(5, 0))
        
        # Equipment
        if pool.equipment:
            equipment_text = "Equipment: "
            equipment_items = []
            for item in pool.equipment:
                if isinstance(item, dict) and "name" in item:
                    equipment_items.append(item["name"])
                elif isinstance(item, str):
                    equipment_items.append(item)
            
            if equipment_items:
                equipment_label = ttk.Label(
                    content_frame,
                    text=f"Equipment: {', '.join(equipment_items)}"
                )
                equipment_label.pack(anchor='w', pady=(5, 0))
        
        # Notes
        if pool.notes:
            notes_label = ttk.Label(
                content_frame,
                text=f"Notes: {pool.notes}"
            )
            notes_label.pack(anchor='w', pady=(5, 0))
        
        # Action buttons
        button_frame = ttk.Frame(content_frame)
        button_frame.pack(anchor='e', pady=(5, 0))
        
        edit_button = Button(
            button_frame,
            text="Edit",
            size="small",
            command=lambda: self._show_edit_pool_dialog(pool)
        )
        edit_button.pack(side='left', padx=(0, 5))
        
        delete_button = Button(
            button_frame,
            text="Delete",
            size="small",
            style="danger",
            command=lambda: self._delete_pool(pool)
        )
        delete_button.pack(side='left')
    
    def _load_service_records(self):
        """Load customer service records into the service history tab."""
        # Clear existing service record cards
        for widget in self.service_records_scrollable_frame.winfo_children():
            widget.destroy()
        
        if not self.current_customer.service_records:
            # Show empty state
            empty_label = ttk.Label(
                self.service_records_scrollable_frame,
                text="No service records found. Click 'Add Service Record' to create one.",
                font=("TkDefaultFont", 10),
                foreground=theme_manager.get_color("text_secondary")
            )
            empty_label.pack(pady=20)
            return
        
        # Sort service records by date (newest first)
        service_records = sorted(
            self.current_customer.service_records,
            key=lambda r: r.service_date,
            reverse=True
        )
        
        # Create service record cards
        for record in service_records:
            self._create_service_record_card(record)
    
    def _create_service_record_card(self, record):
        """
        Create a card for a service record in the service history tab.
        
        Args:
            record: The service record to create a card for
        """
        # Create a frame for the service record card
        card_frame = ttk.Frame(self.service_records_scrollable_frame)
        card_frame.pack(fill='x', pady=5)
        
        # Create a card with service record information
        card = Card(card_frame)
        card.pack(fill='x')
        
        # Add service record information to the card
        content_frame = ttk.Frame(card.content_frame)
        content_frame.pack(fill='x')
        
        # Header with date and type
        header_frame = ttk.Frame(content_frame)
        header_frame.pack(fill='x')
        
        # Format date
        try:
            date_obj = datetime.fromisoformat(record.service_date)
            formatted_date = date_obj.strftime("%Y-%m-%d")
        except:
            formatted_date = record.service_date
        
        date_label = ttk.Label(
            header_frame,
            text=formatted_date,
            font=("TkDefaultFont", 10, "bold")
        )
        date_label.pack(side='left')
        
        type_label = ttk.Label(
            header_frame,
            text=record.service_type,
            foreground=theme_manager.get_color("primary")
        )
        type_label.pack(side='left', padx=(10, 0))
        
        # Technician
        tech_label = ttk.Label(
            content_frame,
            text=f"Technician: {record.technician}"
        )
        tech_label.pack(anchor='w')
        
        # Description
        desc_label = ttk.Label(
            content_frame,
            text=record.description,
            wraplength=400
        )
        desc_label.pack(anchor='w', pady=(5, 0))
        
        # Chemical readings
        if record.chemical_readings:
            readings_frame = ttk.LabelFrame(content_frame, text="Chemical Readings")
            readings_frame.pack(fill='x', pady=(5, 0))
            
            row = 0
            col = 0
            for name, value in record.chemical_readings.items():
                reading_label = ttk.Label(
                    readings_frame,
                    text=f"{name}: {value}"
                )
                reading_label.grid(row=row, column=col, sticky='w', padx=5, pady=2)
                
                col += 1
                if col > 1:
                    col = 0
                    row += 1
        
        # Chemicals added
        if record.chemicals_added:
            chemicals_text = "Chemicals Added: "
            chemical_items = []
            for item in record.chemicals_added:
                if isinstance(item, dict) and "name" in item and "amount" in item:
                    chemical_items.append(f"{item['name']} ({item['amount']})")
                elif isinstance(item, str):
                    chemical_items.append(item)
            
            if chemical_items:
                chemicals_label = ttk.Label(
                    content_frame,
                    text=chemicals_text + ", ".join(chemical_items),
                    wraplength=400
                )
                chemicals_label.pack(anchor='w', pady=(5, 0))
        
        # Issues and recommendations
        if record.issues:
            issues_label = ttk.Label(
                content_frame,
                text=f"Issues: {', '.join(record.issues)}",
                wraplength=400
            )
            issues_label.pack(anchor='w', pady=(5, 0))
        
        if record.recommendations:
            recommendations_label = ttk.Label(
                content_frame,
                text=f"Recommendations: {', '.join(record.recommendations)}",
                wraplength=400
            )
            recommendations_label.pack(anchor='w', pady=(5, 0))
        
        # Cost and duration
        details_frame = ttk.Frame(content_frame)
        details_frame.pack(fill='x', pady=(5, 0))
        
        if record.cost > 0:
            cost_label = ttk.Label(
                details_frame,
                text=f"Cost: ${record.cost:.2f}"
            )
            cost_label.pack(side='left', padx=(0, 10))
        
        if record.duration_minutes > 0:
            duration_label = ttk.Label(
                details_frame,
                text=f"Duration: {record.duration_minutes} minutes"
            )
            duration_label.pack(side='left')
        
        # Action buttons
        button_frame = ttk.Frame(content_frame)
        button_frame.pack(anchor='e', pady=(5, 0))
        
        edit_button = Button(
            button_frame,
            text="Edit",
            size="small",
            command=lambda: self._show_edit_service_record_dialog(record)
        )
        edit_button.pack(side='left', padx=(0, 5))
        
        delete_button = Button(
            button_frame,
            text="Delete",
            size="small",
            style="danger",
            command=lambda: self._delete_service_record(record)
        )
        delete_button.pack(side='left')
    
    def _filter_customers(self, *args):
        """Filter customers based on search input and filters."""
        search_text = self.search_input.get_value().lower()
        status_filter = self.status_filter.get_value()
        type_filter = self.type_filter.get_value()
        
        # Clear existing customer cards
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        # Get customers from database
        customers = list(self.db.customers.values())
        
        # Apply filters
        filtered_customers = []
        for customer in customers:
            # Apply search filter
            if search_text:
                name_match = search_text in customer.full_name.lower()
                company_match = customer.company_name and search_text in customer.company_name.lower()
                
                # Check contacts
                contact_match = False
                for contact in customer.contacts:
                    if search_text in contact.value.lower():
                        contact_match = True
                        break
                
                if not (name_match or company_match or contact_match):
                    continue
            
            # Apply status filter
            if status_filter != "All" and customer.status.lower() != status_filter.lower():
                continue
            
            # Apply type filter
            if type_filter != "All" and customer.customer_type.lower() != type_filter.lower():
                continue
            
            filtered_customers.append(customer)
        
        if not filtered_customers:
            # Show empty state
            empty_label = ttk.Label(
                self.scrollable_frame,
                text="No customers match your filters.",
                font=("TkDefaultFont", 10),
                foreground=theme_manager.get_color("text_secondary")
            )
            empty_label.pack(pady=20)
            return
        
        # Sort customers by name
        filtered_customers.sort(key=lambda c: c.last_name.lower())
        
        # Create customer cards
        for customer in filtered_customers:
            self._create_customer_card(customer)
    
    def _filter_service_records(self):
        """Filter service records based on date range."""
        from_date = self.from_date_input.get_value()
        to_date = self.to_date_input.get_value()
        
        # Validate dates
        if from_date and not self._is_valid_date(from_date):
            messagebox.showerror("Invalid Date", "From date must be in YYYY-MM-DD format.")
            return
        
        if to_date and not self._is_valid_date(to_date):
            messagebox.showerror("Invalid Date", "To date must be in YYYY-MM-DD format.")
            return
        
        # If dates are empty, show all records
        if not from_date and not to_date:
            self._load_service_records()
            return
        
        # Set default dates if needed
        if not from_date:
            from_date = "0000-00-00"
        
        if not to_date:
            to_date = "9999-12-31"
        
        # Get filtered records
        filtered_records = self.current_customer.get_service_records_by_date_range(from_date, to_date)
        
        # Clear existing service record cards
        for widget in self.service_records_scrollable_frame.winfo_children():
            widget.destroy()
        
        if not filtered_records:
            # Show empty state
            empty_label = ttk.Label(
                self.service_records_scrollable_frame,
                text="No service records found in the selected date range.",
                font=("TkDefaultFont", 10),
                foreground=theme_manager.get_color("text_secondary")
            )
            empty_label.pack(pady=20)
            return
        
        # Sort service records by date (newest first)
        filtered_records.sort(key=lambda r: r.service_date, reverse=True)
        
        # Create service record cards
        for record in filtered_records:
            self._create_service_record_card(record)
    
    def _is_valid_date(self, date_str):
        """
        Check if a string is a valid date in YYYY-MM-DD format.
        
        Args:
            date_str: The date string to check
            
        Returns:
            True if the date is valid, False otherwise
        """
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except ValueError:
            return False
    
    def _show_add_customer_dialog(self):
        """Show dialog to add a new customer."""
        # Create dialog window
        dialog = tk.Toplevel(self.parent)
        dialog.title("Add Customer")
        dialog.geometry("500x600")
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # Create form
        form_frame = ttk.Frame(dialog, padding=20)
        form_frame.pack(fill='both', expand=True)
        
        # First name
        first_name_label = ttk.Label(form_frame, text="First Name:")
        first_name_label.grid(row=0, column=0, sticky='w', pady=(0, 10))
        
        first_name_input = TextInput(form_frame)
        first_name_input.grid(row=0, column=1, sticky='ew', pady=(0, 10))
        
        # Last name
        last_name_label = ttk.Label(form_frame, text="Last Name:")
        last_name_label.grid(row=1, column=0, sticky='w', pady=(0, 10))
        
        last_name_input = TextInput(form_frame)
        last_name_input.grid(row=1, column=1, sticky='ew', pady=(0, 10))
        
        # Customer type
        type_label = ttk.Label(form_frame, text="Customer Type:")
        type_label.grid(row=2, column=0, sticky='w', pady=(0, 10))
        
        type_input = Dropdown(
            form_frame,
            options=["Residential", "Commercial"],
            default="Residential"
        )
        type_input.grid(row=2, column=1, sticky='ew', pady=(0, 10))
        
        # Company name
        company_label = ttk.Label(form_frame, text="Company Name:")
        company_label.grid(row=3, column=0, sticky='w', pady=(0, 10))
        
        company_input = TextInput(form_frame)
        company_input.grid(row=3, column=1, sticky='ew', pady=(0, 10))
        
        # Status
        status_label = ttk.Label(form_frame, text="Status:")
        status_label.grid(row=4, column=0, sticky='w', pady=(0, 10))
        
        status_input = Dropdown(
            form_frame,
            options=["Active", "Inactive", "Prospect"],
            default="Active"
        )
        status_input.grid(row=4, column=1, sticky='ew', pady=(0, 10))
        
        # Notes
        notes_label = ttk.Label(form_frame, text="Notes:")
        notes_label.grid(row=5, column=0, sticky='nw', pady=(0, 10))
        
        notes_frame = ttk.Frame(form_frame)
        notes_frame.grid(row=5, column=1, sticky='ew', pady=(0, 10))
        
        notes_input = tk.Text(notes_frame, height=5, width=30)
        notes_input.pack(fill='both', expand=True)
        
        # Tags
        tags_label = ttk.Label(form_frame, text="Tags:")
        tags_label.grid(row=6, column=0, sticky='w', pady=(0, 10))
        
        tags_input = TextInput(
            form_frame,
            placeholder="Comma-separated tags"
        )
        tags_input.grid(row=6, column=1, sticky='ew', pady=(0, 10))
        
        # Configure grid
        form_frame.columnconfigure(1, weight=1)
        
        # Create buttons
        button_frame = ttk.Frame(dialog, padding=20)
        button_frame.pack(fill='x')
        
        cancel_button = Button(
            button_frame,
            text="Cancel",
            command=dialog.destroy
        )
        cancel_button.pack(side='right', padx=(5, 0))
        
        save_button = Button(
            button_frame,
            text="Save",
            style="primary",
            command=lambda: self._save_new_customer(
                first_name_input.get_value(),
                last_name_input.get_value(),
                type_input.get_value().lower(),
                company_input.get_value(),
                status_input.get_value().lower(),
                notes_input.get("1.0", tk.END).strip(),
                tags_input.get_value(),
                dialog
            )
        )
        save_button.pack(side='right')
    
    def _save_new_customer(self, first_name, last_name, customer_type, 
                          company_name, status, notes, tags_str, dialog):
        """
        Save a new customer to the database.
        
        Args:
            first_name: Customer's first name
            last_name: Customer's last name
            customer_type: Type of customer (residential, commercial)
            company_name: Company name (for commercial customers)
            status: Customer status (active, inactive, prospect)
            notes: Additional notes about the customer
            tags_str: Comma-separated list of tags
            dialog: The dialog window to close after saving
        """
        # Validate required fields
        if not first_name or not last_name:
            messagebox.showerror("Validation Error", "First name and last name are required.")
            return
        
        # Parse tags
        tags = [tag.strip() for tag in tags_str.split(",") if tag.strip()]
        
        # Create customer
        customer = Customer(
            first_name=first_name,
            last_name=last_name,
            customer_type=customer_type,
            company_name=company_name if company_name else None,
            notes=notes if notes else None,
            tags=tags,
            status=status
        )
        
        # Add to database
        self.db.add_customer(customer)
        
        # Close dialog
        dialog.destroy()
        
        # Reload customers
        self._load_customers()
        
        # Show success message
        messagebox.showinfo("Success", f"Customer {customer.full_name} added successfully.")
    
    def _show_edit_customer_dialog(self):
        """Show dialog to edit the current customer."""
        customer = self.current_customer
        
        # Create dialog window
        dialog = tk.Toplevel(self.parent)
        dialog.title(f"Edit Customer: {customer.full_name}")
        dialog.geometry("500x600")
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # Create form
        form_frame = ttk.Frame(dialog, padding=20)
        form_frame.pack(fill='both', expand=True)
        
        # First name
        first_name_label = ttk.Label(form_frame, text="First Name:")
        first_name_label.grid(row=0, column=0, sticky='w', pady=(0, 10))
        
        first_name_input = TextInput(form_frame, default=customer.first_name)
        first_name_input.grid(row=0, column=1, sticky='ew', pady=(0, 10))
        
        # Last name
        last_name_label = ttk.Label(form_frame, text="Last Name:")
        last_name_label.grid(row=1, column=0, sticky='w', pady=(0, 10))
        
        last_name_input = TextInput(form_frame, default=customer.last_name)
        last_name_input.grid(row=1, column=1, sticky='ew', pady=(0, 10))
        
        # Customer type
        type_label = ttk.Label(form_frame, text="Customer Type:")
        type_label.grid(row=2, column=0, sticky='w', pady=(0, 10))
        
        type_input = Dropdown(
            form_frame,
            options=["Residential", "Commercial"],
            default=customer.customer_type.capitalize()
        )
        type_input.grid(row=2, column=1, sticky='ew', pady=(0, 10))
        
        # Company name
        company_label = ttk.Label(form_frame, text="Company Name:")
        company_label.grid(row=3, column=0, sticky='w', pady=(0, 10))
        
        company_input = TextInput(form_frame, default=customer.company_name or "")
        company_input.grid(row=3, column=1, sticky='ew', pady=(0, 10))
        
        # Status
        status_label = ttk.Label(form_frame, text="Status:")
        status_label.grid(row=4, column=0, sticky='w', pady=(0, 10))
        
        status_input = Dropdown(
            form_frame,
            options=["Active", "Inactive", "Prospect"],
            default=customer.status.capitalize()
        )
        status_input.grid(row=4, column=1, sticky='ew', pady=(0, 10))
        
        # Notes
        notes_label = ttk.Label(form_frame, text="Notes:")
        notes_label.grid(row=5, column=0, sticky='nw', pady=(0, 10))
        
        notes_frame = ttk.Frame(form_frame)
        notes_frame.grid(row=5, column=1, sticky='ew', pady=(0, 10))
        
        notes_input = tk.Text(notes_frame, height=5, width=30)
        if customer.notes:
            notes_input.insert(tk.END, customer.notes)
        notes_input.pack(fill='both', expand=True)
        
        # Tags
        tags_label = ttk.Label(form_frame, text="Tags:")
        tags_label.grid(row=6, column=0, sticky='w', pady=(0, 10))
        
        tags_input = TextInput(
            form_frame,
            default=", ".join(customer.tags) if customer.tags else ""
        )
        tags_input.grid(row=6, column=1, sticky='ew', pady=(0, 10))
        
        # Configure grid
        form_frame.columnconfigure(1, weight=1)
        
        # Create buttons
        button_frame = ttk.Frame(dialog, padding=20)
        button_frame.pack(fill='x')
        
        cancel_button = Button(
            button_frame,
            text="Cancel",
            command=dialog.destroy
        )
        cancel_button.pack(side='right', padx=(5, 0))
        
        save_button = Button(
            button_frame,
            text="Save",
            style="primary",
            command=lambda: self._save_customer_edits(
                first_name_input.get_value(),
                last_name_input.get_value(),
                type_input.get_value().lower(),
                company_input.get_value(),
                status_input.get_value().lower(),
                notes_input.get("1.0", tk.END).strip(),
                tags_input.get_value(),
                dialog
            )
        )
        save_button.pack(side='right')
    
    def _save_customer_edits(self, first_name, last_name, customer_type, 
                            company_name, status, notes, tags_str, dialog):
        """
        Save edits to the current customer.
        
        Args:
            first_name: Customer's first name
            last_name: Customer's last name
            customer_type: Type of customer (residential, commercial)
            company_name: Company name (for commercial customers)
            status: Customer status (active, inactive, prospect)
            notes: Additional notes about the customer
            tags_str: Comma-separated list of tags
            dialog: The dialog window to close after saving
        """
        # Validate required fields
        if not first_name or not last_name:
            messagebox.showerror("Validation Error", "First name and last name are required.")
            return
        
        # Parse tags
        tags = [tag.strip() for tag in tags_str.split(",") if tag.strip()]
        
        # Update customer
        customer = self.current_customer
        
        customer.first_name = first_name
        customer.last_name = last_name
        customer.customer_type = customer_type
        customer.company_name = company_name if company_name else None
        customer.status = status
        customer.notes = notes if notes else None
        customer.tags = tags
        customer.updated_at = datetime.now().isoformat()
        
        # Update database
        self.db.update_customer(customer)
        
        # Close dialog
        dialog.destroy()
        
        # Reload customers
        self._load_customers()
        
        # Update details view
        self._show_customer_details(customer)
        
        # Show success message
        messagebox.showinfo("Success", f"Customer {customer.full_name} updated successfully.")
    
    def _delete_customer(self):
        """Delete the current customer."""
        customer = self.current_customer
        
        # Confirm deletion
        if not messagebox.askyesno(
            "Confirm Deletion",
            f"Are you sure you want to delete {customer.full_name}? This action cannot be undone."
        ):
            return
        
        # Delete customer
        self.db.delete_customer(customer.customer_id)
        
        # Hide details
        self._hide_customer_details()
        
        # Reload customers
        self._load_customers()
        
        # Show success message
        messagebox.showinfo("Success", f"Customer {customer.full_name} deleted successfully.")
    
    def _show_add_address_dialog(self):
        """Show dialog to add a new address to the current customer."""
        # Create dialog window
        dialog = tk.Toplevel(self.parent)
        dialog.title("Add Address")
        dialog.geometry("500x400")
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # Create form
        form_frame = ttk.Frame(dialog, padding=20)
        form_frame.pack(fill='both', expand=True)
        
        # Address type
        type_label = ttk.Label(form_frame, text="Address Type:")
        type_label.grid(row=0, column=0, sticky='w', pady=(0, 10))
        
        type_input = Dropdown(
            form_frame,
            options=["Primary", "Billing", "Service", "Other"],
            default="Primary"
        )
        type_input.grid(row=0, column=1, sticky='ew', pady=(0, 10))
        
        # Street
        street_label = ttk.Label(form_frame, text="Street:")
        street_label.grid(row=1, column=0, sticky='w', pady=(0, 10))
        
        street_input = TextInput(form_frame)
        street_input.grid(row=1, column=1, sticky='ew', pady=(0, 10))
        
        # City
        city_label = ttk.Label(form_frame, text="City:")
        city_label.grid(row=2, column=0, sticky='w', pady=(0, 10))
        
        city_input = TextInput(form_frame)
        city_input.grid(row=2, column=1, sticky='ew', pady=(0, 10))
        
        # State
        state_label = ttk.Label(form_frame, text="State:")
        state_label.grid(row=3, column=0, sticky='w', pady=(0, 10))
        
        state_input = TextInput(form_frame)
        state_input.grid(row=3, column=1, sticky='ew', pady=(0, 10))
        
        # ZIP code
        zip_label = ttk.Label(form_frame, text="ZIP Code:")
        zip_label.grid(row=4, column=0, sticky='w', pady=(0, 10))
        
        zip_input = TextInput(form_frame)
        zip_input.grid(row=4, column=1, sticky='ew', pady=(0, 10))
        
        # Country
        country_label = ttk.Label(form_frame, text="Country:")
        country_label.grid(row=5, column=0, sticky='w', pady=(0, 10))
        
        country_input = TextInput(form_frame, default="USA")
        country_input.grid(row=5, column=1, sticky='ew', pady=(0, 10))
        
        # Configure grid
        form_frame.columnconfigure(1, weight=1)
        
        # Create buttons
        button_frame = ttk.Frame(dialog, padding=20)
        button_frame.pack(fill='x')
        
        cancel_button = Button(
            button_frame,
            text="Cancel",
            command=dialog.destroy
        )
        cancel_button.pack(side='right', padx=(5, 0))
        
        save_button = Button(
            button_frame,
            text="Save",
            style="primary",
            command=lambda: self._save_new_address(
                type_input.get_value().lower(),
                street_input.get_value(),
                city_input.get_value(),
                state_input.get_value(),
                zip_input.get_value(),
                country_input.get_value(),
                dialog
            )
        )
        save_button.pack(side='right')
    
    def _save_new_address(self, address_type, street, city, state, zip_code, country, dialog):
        """
        Save a new address to the current customer.
        
        Args:
            address_type: Type of address (primary, billing, service, other)
            street: Street address
            city: City
            state: State/province
            zip_code: ZIP/postal code
            country: Country
            dialog: The dialog window to close after saving
        """
        # Validate required fields
        if not street or not city or not state or not zip_code:
            messagebox.showerror("Validation Error", "Street, city, state, and ZIP code are required.")
            return
        
        # Create address
        address = Address(
            street=street,
            city=city,
            state=state,
            zip_code=zip_code,
            country=country,
            address_type=address_type
        )
        
        # Add to customer
        self.current_customer.add_address(address)
        
        # Update database
        self.db.update_customer(self.current_customer)
        
        # Close dialog
        dialog.destroy()
        
        # Reload addresses
        self._load_addresses()
        
        # Show success message
        messagebox.showinfo("Success", "Address added successfully.")
    
    def _show_edit_address_dialog(self, address):
        """
        Show dialog to edit an address.
        
        Args:
            address: The address to edit
        """
        # Create dialog window
        dialog = tk.Toplevel(self.parent)
        dialog.title("Edit Address")
        dialog.geometry("500x400")
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # Create form
        form_frame = ttk.Frame(dialog, padding=20)
        form_frame.pack(fill='both', expand=True)
        
        # Address type
        type_label = ttk.Label(form_frame, text="Address Type:")
        type_label.grid(row=0, column=0, sticky='w', pady=(0, 10))
        
        type_input = Dropdown(
            form_frame,
            options=["Primary", "Billing", "Service", "Other"],
            default=address.address_type.capitalize()
        )
        type_input.grid(row=0, column=1, sticky='ew', pady=(0, 10))
        
        # Street
        street_label = ttk.Label(form_frame, text="Street:")
        street_label.grid(row=1, column=0, sticky='w', pady=(0, 10))
        
        street_input = TextInput(form_frame, default=address.street)
        street_input.grid(row=1, column=1, sticky='ew', pady=(0, 10))
        
        # City
        city_label = ttk.Label(form_frame, text="City:")
        city_label.grid(row=2, column=0, sticky='w', pady=(0, 10))
        
        city_input = TextInput(form_frame, default=address.city)
        city_input.grid(row=2, column=1, sticky='ew', pady=(0, 10))
        
        # State
        state_label = ttk.Label(form_frame, text="State:")
        state_label.grid(row=3, column=0, sticky='w', pady=(0, 10))
        
        state_input = TextInput(form_frame, default=address.state)
        state_input.grid(row=3, column=1, sticky='ew', pady=(0, 10))
        
        # ZIP code
        zip_label = ttk.Label(form_frame, text="ZIP Code:")
        zip_label.grid(row=4, column=0, sticky='w', pady=(0, 10))
        
        zip_input = TextInput(form_frame, default=address.zip_code)
        zip_input.grid(row=4, column=1, sticky='ew', pady=(0, 10))
        
        # Country
        country_label = ttk.Label(form_frame, text="Country:")
        country_label.grid(row=5, column=0, sticky='w', pady=(0, 10))
        
        country_input = TextInput(form_frame, default=address.country)
        country_input.grid(row=5, column=1, sticky='ew', pady=(0, 10))
        
        # Configure grid
        form_frame.columnconfigure(1, weight=1)
        
        # Create buttons
        button_frame = ttk.Frame(dialog, padding=20)
        button_frame.pack(fill='x')
        
        cancel_button = Button(
            button_frame,
            text="Cancel",
            command=dialog.destroy
        )
        cancel_button.pack(side='right', padx=(5, 0))
        
        save_button = Button(
            button_frame,
            text="Save",
            style="primary",
            command=lambda: self._save_address_edits(
                address,
                type_input.get_value().lower(),
                street_input.get_value(),
                city_input.get_value(),
                state_input.get_value(),
                zip_input.get_value(),
                country_input.get_value(),
                dialog
            )
        )
        save_button.pack(side='right')
    
    def _save_address_edits(self, address, address_type, street, city, state, zip_code, country, dialog):
        """
        Save edits to an address.
        
        Args:
            address: The address to edit
            address_type: Type of address (primary, billing, service, other)
            street: Street address
            city: City
            state: State/province
            zip_code: ZIP/postal code
            country: Country
            dialog: The dialog window to close after saving
        """
        # Validate required fields
        if not street or not city or not state or not zip_code:
            messagebox.showerror("Validation Error", "Street, city, state, and ZIP code are required.")
            return
        
        # Update address
        self.current_customer.update_address(
            address.address_id,
            {
                "address_type": address_type,
                "street": street,
                "city": city,
                "state": state,
                "zip_code": zip_code,
                "country": country
            }
        )
        
        # Update database
        self.db.update_customer(self.current_customer)
        
        # Close dialog
        dialog.destroy()
        
        # Reload addresses
        self._load_addresses()
        
        # Show success message
        messagebox.showinfo("Success", "Address updated successfully.")
    
    def _delete_address(self, address):
        """
        Delete an address from the current customer.
        
        Args:
            address: The address to delete
        """
        # Confirm deletion
        if not messagebox.askyesno(
            "Confirm Deletion",
            "Are you sure you want to delete this address? This action cannot be undone."
        ):
            return
        
        # Delete address
        self.current_customer.remove_address(address.address_id)
        
        # Update database
        self.db.update_customer(self.current_customer)
        
        # Reload addresses
        self._load_addresses()
        
        # Show success message
        messagebox.showinfo("Success", "Address deleted successfully.")
    
    def _show_add_contact_dialog(self):
        """Show dialog to add a new contact to the current customer."""
        # Create dialog window
        dialog = tk.Toplevel(self.parent)
        dialog.title("Add Contact")
        dialog.geometry("500x300")
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # Create form
        form_frame = ttk.Frame(dialog, padding=20)
        form_frame.pack(fill='both', expand=True)
        
        # Contact type
        type_label = ttk.Label(form_frame, text="Contact Type:")
        type_label.grid(row=0, column=0, sticky='w', pady=(0, 10))
        
        type_input = Dropdown(
            form_frame,
            options=["Email", "Phone", "Mobile", "Fax", "Other"],
            default="Email"
        )
        type_input.grid(row=0, column=1, sticky='ew', pady=(0, 10))
        
        # Contact value
        value_label = ttk.Label(form_frame, text="Value:")
        value_label.grid(row=1, column=0, sticky='w', pady=(0, 10))
        
        value_input = TextInput(form_frame)
        value_input.grid(row=1, column=1, sticky='ew', pady=(0, 10))
        
        # Is primary
        is_primary_var = tk.BooleanVar()
        is_primary_check = Checkbox(
            form_frame,
            text="Primary Contact",
            variable=is_primary_var
        )
        is_primary_check.grid(row=2, column=1, sticky='w', pady=(0, 10))
        
        # Configure grid
        form_frame.columnconfigure(1, weight=1)
        
        # Create buttons
        button_frame = ttk.Frame(dialog, padding=20)
        button_frame.pack(fill='x')
        
        cancel_button = Button(
            button_frame,
            text="Cancel",
            command=dialog.destroy
        )
        cancel_button.pack(side='right', padx=(5, 0))
        
        save_button = Button(
            button_frame,
            text="Save",
            style="primary",
            command=lambda: self._save_new_contact(
                type_input.get_value().lower(),
                value_input.get_value(),
                is_primary_var.get(),
                dialog
            )
        )
        save_button.pack(side='right')
    
    def _save_new_contact(self, contact_type, value, is_primary, dialog):
        """
        Save a new contact to the current customer.
        
        Args:
            contact_type: Type of contact (email, phone, mobile, etc.)
            value: Contact value (email address, phone number, etc.)
            is_primary: Whether this is the primary contact of its type
            dialog: The dialog window to close after saving
        """
        # Validate required fields
        if not value:
            messagebox.showerror("Validation Error", "Contact value is required.")
            return
        
        # Create contact
        contact = Contact(
            contact_type=contact_type,
            value=value,
            is_primary=is_primary
        )
        
        # Add to customer
        self.current_customer.add_contact(contact)
        
        # Update database
        self.db.update_customer(self.current_customer)
        
        # Close dialog
        dialog.destroy()
        
        # Reload contacts
        self._load_contacts()
        
        # Show success message
        messagebox.showinfo("Success", "Contact added successfully.")
    
    def _show_edit_contact_dialog(self, contact):
        """
        Show dialog to edit a contact.
        
        Args:
            contact: The contact to edit
        """
        # Create dialog window
        dialog = tk.Toplevel(self.parent)
        dialog.title("Edit Contact")
        dialog.geometry("500x300")
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # Create form
        form_frame = ttk.Frame(dialog, padding=20)
        form_frame.pack(fill='both', expand=True)
        
        # Contact type
        type_label = ttk.Label(form_frame, text="Contact Type:")
        type_label.grid(row=0, column=0, sticky='w', pady=(0, 10))
        
        type_input = Dropdown(
            form_frame,
            options=["Email", "Phone", "Mobile", "Fax", "Other"],
            default=contact.contact_type.capitalize()
        )
        type_input.grid(row=0, column=1, sticky='ew', pady=(0, 10))
        
        # Contact value
        value_label = ttk.Label(form_frame, text="Value:")
        value_label.grid(row=1, column=0, sticky='w', pady=(0, 10))
        
        value_input = TextInput(form_frame, default=contact.value)
        value_input.grid(row=1, column=1, sticky='ew', pady=(0, 10))
        
        # Is primary
        is_primary_var = tk.BooleanVar(value=contact.is_primary)
        is_primary_check = Checkbox(
            form_frame,
            text="Primary Contact",
            variable=is_primary_var
        )
        is_primary_check.grid(row=2, column=1, sticky='w', pady=(0, 10))
        
        # Configure grid
        form_frame.columnconfigure(1, weight=1)
        
        # Create buttons
        button_frame = ttk.Frame(dialog, padding=20)
        button_frame.pack(fill='x')
        
        cancel_button = Button(
            button_frame,
            text="Cancel",
            command=dialog.destroy
        )
        cancel_button.pack(side='right', padx=(5, 0))
        
        save_button = Button(
            button_frame,
            text="Save",
            style="primary",
            command=lambda: self._save_contact_edits(
                contact,
                type_input.get_value().lower(),
                value_input.get_value(),
                is_primary_var.get(),
                dialog
            )
        )
        save_button.pack(side='right')
    
    def _save_contact_edits(self, contact, contact_type, value, is_primary, dialog):
        """
        Save edits to a contact.
        
        Args:
            contact: The contact to edit
            contact_type: Type of contact (email, phone, mobile, etc.)
            value: Contact value (email address, phone number, etc.)
            is_primary: Whether this is the primary contact of its type
            dialog: The dialog window to close after saving
        """
        # Validate required fields
        if not value:
            messagebox.showerror("Validation Error", "Contact value is required.")
            return
        
        # Update contact
        self.current_customer.update_contact(
            contact.contact_id,
            {
                "contact_type": contact_type,
                "value": value,
                "is_primary": is_primary
            }
        )
        
        # Update database
        self.db.update_customer(self.current_customer)
        
        # Close dialog
        dialog.destroy()
        
        # Reload contacts
        self._load_contacts()
        
        # Show success message
        messagebox.showinfo("Success", "Contact updated successfully.")
    
    def _delete_contact(self, contact):
        """
        Delete a contact from the current customer.
        
        Args:
            contact: The contact to delete
        """
        # Confirm deletion
        if not messagebox.askyesno(
            "Confirm Deletion",
            "Are you sure you want to delete this contact? This action cannot be undone."
        ):
            return
        
        # Delete contact
        self.current_customer.remove_contact(contact.contact_id)
        
        # Update database
        self.db.update_customer(self.current_customer)
        
        # Reload contacts
        self._load_contacts()
        
        # Show success message
        messagebox.showinfo("Success", "Contact deleted successfully.")
    
    def _show_add_pool_dialog(self):
        """Show dialog to add a new pool to the current customer."""
        # Create dialog window
        dialog = tk.Toplevel(self.parent)
        dialog.title("Add Pool")
        dialog.geometry("500x600")
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # Create form with scrollbar
        canvas = tk.Canvas(dialog)
        scrollbar = ttk.Scrollbar(dialog, orient="vertical", command=canvas.yview)
        form_frame = ttk.Frame(canvas, padding=20)
        
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        canvas.create_window((0, 0), window=form_frame, anchor="nw")
        form_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        # Pool type
        type_label = ttk.Label(form_frame, text="Pool Type:")
        type_label.grid(row=0, column=0, sticky='w', pady=(0, 10))
        
        type_input = Dropdown(
            form_frame,
            options=["In-ground", "Above-ground", "Spa", "Hot tub", "Other"],
            default="In-ground"
        )
        type_input.grid(row=0, column=1, sticky='ew', pady=(0, 10))
        
        # Size
        size_label = ttk.Label(form_frame, text="Size (sq ft):")
        size_label.grid(row=1, column=0, sticky='w', pady=(0, 10))
        
        size_input = NumericInput(form_frame, default=0)
        size_input.grid(row=1, column=1, sticky='ew', pady=(0, 10))
        
        # Volume
        volume_label = ttk.Label(form_frame, text="Volume (gallons):")
        volume_label.grid(row=2, column=0, sticky='w', pady=(0, 10))
        
        volume_input = NumericInput(form_frame, default=0)
        volume_input.grid(row=2, column=1, sticky='ew', pady=(0, 10))
        
        # Sanitizer type
        sanitizer_label = ttk.Label(form_frame, text="Sanitizer Type:")
        sanitizer_label.grid(row=3, column=0, sticky='w', pady=(0, 10))
        
        sanitizer_input = Dropdown(
            form_frame,
            options=["Chlorine", "Bromine", "Salt", "Mineral", "Other"],
            default="Chlorine"
        )
        sanitizer_input.grid(row=3, column=1, sticky='ew', pady=(0, 10))
        
        # Surface type
        surface_label = ttk.Label(form_frame, text="Surface Type:")
        surface_label.grid(row=4, column=0, sticky='w', pady=(0, 10))
        
        surface_input = Dropdown(
            form_frame,
            options=["Plaster", "Vinyl", "Fiberglass", "Tile", "Pebble", "Other"],
            default="Plaster"
        )
        surface_input.grid(row=4, column=1, sticky='ew', pady=(0, 10))
        
        # Features
        features_label = ttk.Label(form_frame, text="Features:")
        features_label.grid(row=5, column=0, sticky='w', pady=(0, 10))
        
        features_input = TextInput(
            form_frame,
            placeholder="Comma-separated features"
        )
        features_input.grid(row=5, column=1, sticky='ew', pady=(0, 10))
        
        # Equipment
        equipment_label = ttk.Label(form_frame, text="Equipment:")
        equipment_label.grid(row=6, column=0, sticky='w', pady=(0, 10))
        
        equipment_input = TextInput(
            form_frame,
            placeholder="Comma-separated equipment"
        )
        equipment_input.grid(row=6, column=1, sticky='ew', pady=(0, 10))
        
        # Notes
        notes_label = ttk.Label(form_frame, text="Notes:")
        notes_label.grid(row=7, column=0, sticky='nw', pady=(0, 10))
        
        notes_frame = ttk.Frame(form_frame)
        notes_frame.grid(row=7, column=1, sticky='ew', pady=(0, 10))
        
        notes_input = tk.Text(notes_frame, height=5, width=30)
        notes_input.pack(fill='both', expand=True)
        
        # Configure grid
        form_frame.columnconfigure(1, weight=1)
        
        # Create buttons
        button_frame = ttk.Frame(dialog, padding=20)
        button_frame.pack(side='bottom', fill='x')
        
        cancel_button = Button(
            button_frame,
            text="Cancel",
            command=dialog.destroy
        )
        cancel_button.pack(side='right', padx=(5, 0))
        
        save_button = Button(
            button_frame,
            text="Save",
            style="primary",
            command=lambda: self._save_new_pool(
                type_input.get_value(),
                float(size_input.get_value()),
                float(volume_input.get_value()),
                sanitizer_input.get_value(),
                surface_input.get_value(),
                features_input.get_value(),
                equipment_input.get_value(),
                notes_input.get("1.0", tk.END).strip(),
                dialog
            )
        )
        save_button.pack(side='right')
    
    def _save_new_pool(self, pool_type, size, volume, sanitizer_type, 
                      surface_type, features_str, equipment_str, notes, dialog):
        """
        Save a new pool to the current customer.
        
        Args:
            pool_type: Type of pool (in-ground, above-ground, spa, etc.)
            size: Size of the pool in square feet
            volume: Volume of the pool in gallons
            sanitizer_type: Type of sanitizer (chlorine, bromine, salt, etc.)
            surface_type: Type of pool surface (plaster, vinyl, fiberglass, etc.)
            features_str: Comma-separated list of pool features
            equipment_str: Comma-separated list of pool equipment
            notes: Additional notes about the pool
            dialog: The dialog window to close after saving
        """
        # Validate required fields
        if not pool_type or size <= 0 or volume <= 0 or not sanitizer_type:
            messagebox.showerror(
                "Validation Error", 
                "Pool type, size, volume, and sanitizer type are required. Size and volume must be greater than zero."
            )
            return
        
        # Parse features and equipment
        features = [f.strip() for f in features_str.split(",") if f.strip()]
        equipment = [{"name": e.strip()} for e in equipment_str.split(",") if e.strip()]
        
        # Create pool
        pool = Pool(
            pool_type=pool_type,
            size=size,
            volume=volume,
            sanitizer_type=sanitizer_type,
            surface_type=surface_type,
            features=features,
            equipment=equipment,
            notes=notes if notes else None
        )
        
        # Add to customer
        self.current_customer.add_pool(pool)
        
        # Update database
        self.db.update_customer(self.current_customer)
        
        # Close dialog
        dialog.destroy()
        
        # Reload pools
        self._load_pools()
        
        # Show success message
        messagebox.showinfo("Success", "Pool added successfully.")
    
    def _show_edit_pool_dialog(self, pool):
        """
        Show dialog to edit a pool.
        
        Args:
            pool: The pool to edit
        """
        # Create dialog window
        dialog = tk.Toplevel(self.parent)
        dialog.title("Edit Pool")
        dialog.geometry("500x600")
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # Create form with scrollbar
        canvas = tk.Canvas(dialog)
        scrollbar = ttk.Scrollbar(dialog, orient="vertical", command=canvas.yview)
        form_frame = ttk.Frame(canvas, padding=20)
        
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        canvas.create_window((0, 0), window=form_frame, anchor="nw")
        form_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        # Pool type
        type_label = ttk.Label(form_frame, text="Pool Type:")
        type_label.grid(row=0, column=0, sticky='w', pady=(0, 10))
        
        type_input = Dropdown(
            form_frame,
            options=["In-ground", "Above-ground", "Spa", "Hot tub", "Other"],
            default=pool.pool_type.capitalize()
        )
        type_input.grid(row=0, column=1, sticky='ew', pady=(0, 10))
        
        # Size
        size_label = ttk.Label(form_frame, text="Size (sq ft):")
        size_label.grid(row=1, column=0, sticky='w', pady=(0, 10))
        
        size_input = NumericInput(form_frame, default=pool.size)
        size_input.grid(row=1, column=1, sticky='ew', pady=(0, 10))
        
        # Volume
        volume_label = ttk.Label(form_frame, text="Volume (gallons):")
        volume_label.grid(row=2, column=0, sticky='w', pady=(0, 10))
        
        volume_input = NumericInput(form_frame, default=pool.volume)
        volume_input.grid(row=2, column=1, sticky='ew', pady=(0, 10))
        
        # Sanitizer type
        sanitizer_label = ttk.Label(form_frame, text="Sanitizer Type:")
        sanitizer_label.grid(row=3, column=0, sticky='w', pady=(0, 10))
        
        sanitizer_input = Dropdown(
            form_frame,
            options=["Chlorine", "Bromine", "Salt", "Mineral", "Other"],
            default=pool.sanitizer_type.capitalize()
        )
        sanitizer_input.grid(row=3, column=1, sticky='ew', pady=(0, 10))
        
        # Surface type
        surface_label = ttk.Label(form_frame, text="Surface Type:")
        surface_label.grid(row=4, column=0, sticky='w', pady=(0, 10))
        
        surface_options = ["Plaster", "Vinyl", "Fiberglass", "Tile", "Pebble", "Other"]
        surface_default = pool.surface_type.capitalize() if pool.surface_type else surface_options[0]
        
        surface_input = Dropdown(
            form_frame,
            options=surface_options,
            default=surface_default
        )
        surface_input.grid(row=4, column=1, sticky='ew', pady=(0, 10))
        
        # Features
        features_label = ttk.Label(form_frame, text="Features:")
        features_label.grid(row=5, column=0, sticky='w', pady=(0, 10))
        
        features_input = TextInput(
            form_frame,
            default=", ".join(pool.features) if pool.features else ""
        )
        features_input.grid(row=5, column=1, sticky='ew', pady=(0, 10))
        
        # Equipment
        equipment_label = ttk.Label(form_frame, text="Equipment:")
        equipment_label.grid(row=6, column=0, sticky='w', pady=(0, 10))
        
        equipment_items = []
        for item in pool.equipment:
            if isinstance(item, dict) and "name" in item:
                equipment_items.append(item["name"])
            elif isinstance(item, str):
                equipment_items.append(item)
        
        equipment_input = TextInput(
            form_frame,
            default=", ".join(equipment_items) if equipment_items else ""
        )
        equipment_input.grid(row=6, column=1, sticky='ew', pady=(0, 10))
        
        # Notes
        notes_label = ttk.Label(form_frame, text="Notes:")
        notes_label.grid(row=7, column=0, sticky='nw', pady=(0, 10))
        
        notes_frame = ttk.Frame(form_frame)
        notes_frame.grid(row=7, column=1, sticky='ew', pady=(0, 10))
        
        notes_input = tk.Text(notes_frame, height=5, width=30)
        if pool.notes:
            notes_input.insert(tk.END, pool.notes)
        notes_input.pack(fill='both', expand=True)
        
        # Configure grid
        form_frame.columnconfigure(1, weight=1)
        
        # Create buttons
        button_frame = ttk.Frame(dialog, padding=20)
        button_frame.pack(side='bottom', fill='x')
        
        cancel_button = Button(
            button_frame,
            text="Cancel",
            command=dialog.destroy
        )
        cancel_button.pack(side='right', padx=(5, 0))
        
        save_button = Button(
            button_frame,
            text="Save",
            style="primary",
            command=lambda: self._save_pool_edits(
                pool,
                type_input.get_value(),
                float(size_input.get_value()),
                float(volume_input.get_value()),
                sanitizer_input.get_value(),
                surface_input.get_value(),
                features_input.get_value(),
                equipment_input.get_value(),
                notes_input.get("1.0", tk.END).strip(),
                dialog
            )
        )
        save_button.pack(side='right')
    
    def _save_pool_edits(self, pool, pool_type, size, volume, sanitizer_type, 
                        surface_type, features_str, equipment_str, notes, dialog):
        """
        Save edits to a pool.
        
        Args:
            pool: The pool to edit
            pool_type: Type of pool (in-ground, above-ground, spa, etc.)
            size: Size of the pool in square feet
            volume: Volume of the pool in gallons
            sanitizer_type: Type of sanitizer (chlorine, bromine, salt, etc.)
            surface_type: Type of pool surface (plaster, vinyl, fiberglass, etc.)
            features_str: Comma-separated list of pool features
            equipment_str: Comma-separated list of pool equipment
            notes: Additional notes about the pool
            dialog: The dialog window to close after saving
        """
        # Validate required fields
        if not pool_type or size <= 0 or volume <= 0 or not sanitizer_type:
            messagebox.showerror(
                "Validation Error", 
                "Pool type, size, volume, and sanitizer type are required. Size and volume must be greater than zero."
            )
            return
        
        # Parse features and equipment
        features = [f.strip() for f in features_str.split(",") if f.strip()]
        equipment = [{"name": e.strip()} for e in equipment_str.split(",") if e.strip()]
        
        # Update pool
        self.current_customer.update_pool(
            pool.pool_id,
            {
                "pool_type": pool_type,
                "size": size,
                "volume": volume,
                "sanitizer_type": sanitizer_type,
                "surface_type": surface_type,
                "features": features,
                "equipment": equipment,
                "notes": notes if notes else None
            }
        )
        
        # Update database
        self.db.update_customer(self.current_customer)
        
        # Close dialog
        dialog.destroy()
        
        # Reload pools
        self._load_pools()
        
        # Show success message
        messagebox.showinfo("Success", "Pool updated successfully.")
    
    def _delete_pool(self, pool):
        """
        Delete a pool from the current customer.
        
        Args:
            pool: The pool to delete
        """
        # Confirm deletion
        if not messagebox.askyesno(
            "Confirm Deletion",
            "Are you sure you want to delete this pool? This action cannot be undone."
        ):
            return
        
        # Delete pool
        self.current_customer.remove_pool(pool.pool_id)
        
        # Update database
        self.db.update_customer(self.current_customer)
        
        # Reload pools
        self._load_pools()
        
        # Show success message
        messagebox.showinfo("Success", "Pool deleted successfully.")
    
    def _show_add_service_record_dialog(self):
        """Show dialog to add a new service record to the current customer."""
        # Create dialog window
        dialog = tk.Toplevel(self.parent)
        dialog.title("Add Service Record")
        dialog.geometry("600x700")
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # Create form with scrollbar
        canvas = tk.Canvas(dialog)
        scrollbar = ttk.Scrollbar(dialog, orient="vertical", command=canvas.yview)
        form_frame = ttk.Frame(canvas, padding=20)
        
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        canvas.create_window((0, 0), window=form_frame, anchor="nw")
        form_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        # Service date
        date_label = ttk.Label(form_frame, text="Service Date:")
        date_label.grid(row=0, column=0, sticky='w', pady=(0, 10))
        
        today = datetime.now().strftime("%Y-%m-%d")
        date_input = TextInput(form_frame, default=today)
        date_input.grid(row=0, column=1, sticky='ew', pady=(0, 10))
        
        # Service type
        type_label = ttk.Label(form_frame, text="Service Type:")
        type_label.grid(row=1, column=0, sticky='w', pady=(0, 10))
        
        type_input = Dropdown(
            form_frame,
            options=["Regular Maintenance", "Repair", "Installation", "Inspection", "Other"],
            default="Regular Maintenance"
        )
        type_input.grid(row=1, column=1, sticky='ew', pady=(0, 10))
        
        # Technician
        tech_label = ttk.Label(form_frame, text="Technician:")
        tech_label.grid(row=2, column=0, sticky='w', pady=(0, 10))
        
        tech_input = TextInput(form_frame)
        tech_input.grid(row=2, column=1, sticky='ew', pady=(0, 10))
        
        # Description
        desc_label = ttk.Label(form_frame, text="Description:")
        desc_label.grid(row=3, column=0, sticky='nw', pady=(0, 10))
        
        desc_frame = ttk.Frame(form_frame)
        desc_frame.grid(row=3, column=1, sticky='ew', pady=(0, 10))
        
        desc_input = tk.Text(desc_frame, height=3, width=30)
        desc_input.pack(fill='both', expand=True)
        
        # Chemical readings
        readings_label = ttk.Label(form_frame, text="Chemical Readings:")
        readings_label.grid(row=4, column=0, sticky='nw', pady=(0, 10))
        
        readings_frame = ttk.Frame(form_frame)
        readings_frame.grid(row=4, column=1, sticky='ew', pady=(0, 10))
        
        # Add common chemical readings
        readings = {
            "pH": "",
            "Chlorine": "",
            "Alkalinity": "",
            "Calcium": "",
            "Cyanuric Acid": ""
        }
        
        readings_entries = {}
        row = 0
        col = 0
        for name, value in readings.items():
            label = ttk.Label(readings_frame, text=f"{name}:")
            label.grid(row=row, column=col*2, sticky='w', padx=(5 if col else 0, 5), pady=2)
            
            entry = TextInput(readings_frame, default=value, width=10)
            entry.grid(row=row, column=col*2+1, sticky='w', padx=(0, 10), pady=2)
            
            readings_entries[name] = entry
            
            col += 1
            if col > 1:
                col = 0
                row += 1
        
        # Chemicals added
        chemicals_label = ttk.Label(form_frame, text="Chemicals Added:")
        chemicals_label.grid(row=5, column=0, sticky='w', pady=(0, 10))
        
        chemicals_input = TextInput(
            form_frame,
            placeholder="Name: amount, Name: amount, ..."
        )
        chemicals_input.grid(row=5, column=1, sticky='ew', pady=(0, 10))
        
        # Issues
        issues_label = ttk.Label(form_frame, text="Issues:")
        issues_label.grid(row=6, column=0, sticky='w', pady=(0, 10))
        
        issues_input = TextInput(
            form_frame,
            placeholder="Comma-separated issues"
        )
        issues_input.grid(row=6, column=1, sticky='ew', pady=(0, 10))
        
        # Recommendations
        recommendations_label = ttk.Label(form_frame, text="Recommendations:")
        recommendations_label.grid(row=7, column=0, sticky='w', pady=(0, 10))
        
        recommendations_input = TextInput(
            form_frame,
            placeholder="Comma-separated recommendations"
        )
        recommendations_input.grid(row=7, column=1, sticky='ew', pady=(0, 10))
        
        # Cost
        cost_label = ttk.Label(form_frame, text="Cost ($):")
        cost_label.grid(row=8, column=0, sticky='w', pady=(0, 10))
        
        cost_input = NumericInput(form_frame, default=0)
        cost_input.grid(row=8, column=1, sticky='ew', pady=(0, 10))
        
        # Duration
        duration_label = ttk.Label(form_frame, text="Duration (minutes):")
        duration_label.grid(row=9, column=0, sticky='w', pady=(0, 10))
        
        duration_input = NumericInput(form_frame, default=0)
        duration_input.grid(row=9, column=1, sticky='ew', pady=(0, 10))
        
        # Notes
        notes_label = ttk.Label(form_frame, text="Notes:")
        notes_label.grid(row=10, column=0, sticky='nw', pady=(0, 10))
        
        notes_frame = ttk.Frame(form_frame)
        notes_frame.grid(row=10, column=1, sticky='ew', pady=(0, 10))
        
        notes_input = tk.Text(notes_frame, height=3, width=30)
        notes_input.pack(fill='both', expand=True)
        
        # Configure grid
        form_frame.columnconfigure(1, weight=1)
        
        # Create buttons
        button_frame = ttk.Frame(dialog, padding=20)
        button_frame.pack(side='bottom', fill='x')
        
        cancel_button = Button(
            button_frame,
            text="Cancel",
            command=dialog.destroy
        )
        cancel_button.pack(side='right', padx=(5, 0))
        
        save_button = Button(
            button_frame,
            text="Save",
            style="primary",
            command=lambda: self._save_new_service_record(
                date_input.get_value(),
                type_input.get_value(),
                tech_input.get_value(),
                desc_input.get("1.0", tk.END).strip(),
                {name: entry.get_value() for name, entry in readings_entries.items() if entry.get_value()},
                chemicals_input.get_value(),
                issues_input.get_value(),
                recommendations_input.get_value(),
                float(cost_input.get_value()),
                int(duration_input.get_value()),
                notes_input.get("1.0", tk.END).strip(),
                dialog
            )
        )
        save_button.pack(side='right')
    
    def _save_new_service_record(self, service_date, service_type, technician, 
                                description, chemical_readings, chemicals_added_str, 
                                issues_str, recommendations_str, cost, duration, 
                                notes, dialog):
        """
        Save a new service record to the current customer.
        
        Args:
            service_date: Date of service (ISO format)
            service_type: Type of service (regular maintenance, repair, etc.)
            technician: Name of the technician who performed the service
            description: Description of the service performed
            chemical_readings: Dictionary of chemical readings (pH, chlorine, etc.)
            chemicals_added_str: String of chemicals added (name: amount, ...)
            issues_str: Comma-separated list of issues found during the service
            recommendations_str: Comma-separated list of recommendations for future service
            cost: Cost of the service
            duration: Duration of the service in minutes
            notes: Additional notes about the service
            dialog: The dialog window to close after saving
        """
        # Validate required fields
        if not service_date or not service_type or not technician or not description:
            messagebox.showerror(
                "Validation Error", 
                "Service date, type, technician, and description are required."
            )
            return
        
        # Validate date format
        if not self._is_valid_date(service_date):
            messagebox.showerror("Validation Error", "Service date must be in YYYY-MM-DD format.")
            return
        
        # Parse chemicals added
        chemicals_added = []
        if chemicals_added_str:
            for item in chemicals_added_str.split(","):
                item = item.strip()
                if ":" in item:
                    name, amount = item.split(":", 1)
                    chemicals_added.append({
                        "name": name.strip(),
                        "amount": amount.strip()
                    })
                else:
                    chemicals_added.append({"name": item, "amount": ""})
        
        # Parse issues and recommendations
        issues = [i.strip() for i in issues_str.split(",") if i.strip()]
        recommendations = [r.strip() for r in recommendations_str.split(",") if r.strip()]
        
        # Create service record
        service_record = ServiceRecord(
            service_date=service_date,
            service_type=service_type,
            technician=technician,
            description=description,
            chemical_readings=chemical_readings,
            chemicals_added=chemicals_added,
            issues=issues,
            recommendations=recommendations,
            cost=cost,
            duration_minutes=duration,
            notes=notes if notes else None
        )
        
        # Add to customer
        self.current_customer.add_service_record(service_record)
        
        # Update database
        self.db.update_customer(self.current_customer)
        
        # Close dialog
        dialog.destroy()
        
        # Reload service records
        self._load_service_records()
        
        # Show success message
        messagebox.showinfo("Success", "Service record added successfully.")
    
    def _show_edit_service_record_dialog(self, record):
        """
        Show dialog to edit a service record.
        
        Args:
            record: The service record to edit
        """
        # Create dialog window
        dialog = tk.Toplevel(self.parent)
        dialog.title("Edit Service Record")
        dialog.geometry("600x700")
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # Create form with scrollbar
        canvas = tk.Canvas(dialog)
        scrollbar = ttk.Scrollbar(dialog, orient="vertical", command=canvas.yview)
        form_frame = ttk.Frame(canvas, padding=20)
        
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        canvas.create_window((0, 0), window=form_frame, anchor="nw")
        form_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        # Service date
        date_label = ttk.Label(form_frame, text="Service Date:")
        date_label.grid(row=0, column=0, sticky='w', pady=(0, 10))
        
        date_input = TextInput(form_frame, default=record.service_date)
        date_input.grid(row=0, column=1, sticky='ew', pady=(0, 10))
        
        # Service type
        type_label = ttk.Label(form_frame, text="Service Type:")
        type_label.grid(row=1, column=0, sticky='w', pady=(0, 10))
        
        type_options = ["Regular Maintenance", "Repair", "Installation", "Inspection", "Other"]
        type_default = record.service_type if record.service_type in type_options else type_options[0]
        
        type_input = Dropdown(
            form_frame,
            options=type_options,
            default=type_default
        )
        type_input.grid(row=1, column=1, sticky='ew', pady=(0, 10))
        
        # Technician
        tech_label = ttk.Label(form_frame, text="Technician:")
        tech_label.grid(row=2, column=0, sticky='w', pady=(0, 10))
        
        tech_input = TextInput(form_frame, default=record.technician)
        tech_input.grid(row=2, column=1, sticky='ew', pady=(0, 10))
        
        # Description
        desc_label = ttk.Label(form_frame, text="Description:")
        desc_label.grid(row=3, column=0, sticky='nw', pady=(0, 10))
        
        desc_frame = ttk.Frame(form_frame)
        desc_frame.grid(row=3, column=1, sticky='ew', pady=(0, 10))
        
        desc_input = tk.Text(desc_frame, height=3, width=30)
        desc_input.insert(tk.END, record.description)
        desc_input.pack(fill='both', expand=True)
        
        # Chemical readings
        readings_label = ttk.Label(form_frame, text="Chemical Readings:")
        readings_label.grid(row=4, column=0, sticky='nw', pady=(0, 10))
        
        readings_frame = ttk.Frame(form_frame)
        readings_frame.grid(row=4, column=1, sticky='ew', pady=(0, 10))
        
        # Add common chemical readings
        common_readings = ["pH", "Chlorine", "Alkalinity", "Calcium", "Cyanuric Acid"]
        readings = {}
        
        # Add existing readings
        for name, value in record.chemical_readings.items():
            readings[name] = value
        
        # Add missing common readings
        for name in common_readings:
            if name not in readings:
                readings[name] = ""
        
        readings_entries = {}
        row = 0
        col = 0
        for name, value in readings.items():
            label = ttk.Label(readings_frame, text=f"{name}:")
            label.grid(row=row, column=col*2, sticky='w', padx=(5 if col else 0, 5), pady=2)
            
            entry = TextInput(readings_frame, default=str(value), width=10)
            entry.grid(row=row, column=col*2+1, sticky='w', padx=(0, 10), pady=2)
            
            readings_entries[name] = entry
            
            col += 1
            if col > 1:
                col = 0
                row += 1
        
        # Chemicals added
        chemicals_label = ttk.Label(form_frame, text="Chemicals Added:")
        chemicals_label.grid(row=5, column=0, sticky='w', pady=(0, 10))
        
        chemicals_items = []
        for item in record.chemicals_added:
            if isinstance(item, dict) and "name" in item and "amount" in item:
                chemicals_items.append(f"{item['name']}: {item['amount']}")
            elif isinstance(item, dict) and "name" in item:
                chemicals_items.append(item["name"])
            elif isinstance(item, str):
                chemicals_items.append(item)
        
        chemicals_input = TextInput(
            form_frame,
            default=", ".join(chemicals_items) if chemicals_items else ""
        )
        chemicals_input.grid(row=5, column=1, sticky='ew', pady=(0, 10))
        
        # Issues
        issues_label = ttk.Label(form_frame, text="Issues:")
        issues_label.grid(row=6, column=0, sticky='w', pady=(0, 10))
        
        issues_input = TextInput(
            form_frame,
            default=", ".join(record.issues) if record.issues else ""
        )
        issues_input.grid(row=6, column=1, sticky='ew', pady=(0, 10))
        
        # Recommendations
        recommendations_label = ttk.Label(form_frame, text="Recommendations:")
        recommendations_label.grid(row=7, column=0, sticky='w', pady=(0, 10))
        
        recommendations_input = TextInput(
            form_frame,
            default=", ".join(record.recommendations) if record.recommendations else ""
        )
        recommendations_input.grid(row=7, column=1, sticky='ew', pady=(0, 10))
        
        # Cost
        cost_label = ttk.Label(form_frame, text="Cost ($):")
        cost_label.grid(row=8, column=0, sticky='w', pady=(0, 10))
        
        cost_input = NumericInput(form_frame, default=record.cost)
        cost_input.grid(row=8, column=1, sticky='ew', pady=(0, 10))
        
        # Duration
        duration_label = ttk.Label(form_frame, text="Duration (minutes):")
        duration_label.grid(row=9, column=0, sticky='w', pady=(0, 10))
        
        duration_input = NumericInput(form_frame, default=record.duration_minutes)
        duration_input.grid(row=9, column=1, sticky='ew', pady=(0, 10))
        
        # Notes
        notes_label = ttk.Label(form_frame, text="Notes:")
        notes_label.grid(row=10, column=0, sticky='nw', pady=(0, 10))
        
        notes_frame = ttk.Frame(form_frame)
        notes_frame.grid(row=10, column=1, sticky='ew', pady=(0, 10))
        
        notes_input = tk.Text(notes_frame, height=3, width=30)
        if record.notes:
            notes_input.insert(tk.END, record.notes)
        notes_input.pack(fill='both', expand=True)
        
        # Configure grid
        form_frame.columnconfigure(1, weight=1)
        
        # Create buttons
        button_frame = ttk.Frame(dialog, padding=20)
        button_frame.pack(side='bottom', fill='x')
        
        cancel_button = Button(
            button_frame,
            text="Cancel",
            command=dialog.destroy
        )
        cancel_button.pack(side='right', padx=(5, 0))
        
        save_button = Button(
            button_frame,
            text="Save",
            style="primary",
            command=lambda: self._save_service_record_edits(
                record,
                date_input.get_value(),
                type_input.get_value(),
                tech_input.get_value(),
                desc_input.get("1.0", tk.END).strip(),
                {name: entry.get_value() for name, entry in readings_entries.items() if entry.get_value()},
                chemicals_input.get_value(),
                issues_input.get_value(),
                recommendations_input.get_value(),
                float(cost_input.get_value()),
                int(duration_input.get_value()),
                notes_input.get("1.0", tk.END).strip(),
                dialog
            )
        )
        save_button.pack(side='right')
    
    def _save_service_record_edits(self, record, service_date, service_type, technician, 
                                  description, chemical_readings, chemicals_added_str, 
                                  issues_str, recommendations_str, cost, duration, 
                                  notes, dialog):
        """
        Save edits to a service record.
        
        Args:
            record: The service record to edit
            service_date: Date of service (ISO format)
            service_type: Type of service (regular maintenance, repair, etc.)
            technician: Name of the technician who performed the service
            description: Description of the service performed
            chemical_readings: Dictionary of chemical readings (pH, chlorine, etc.)
            chemicals_added_str: String of chemicals added (name: amount, ...)
            issues_str: Comma-separated list of issues found during the service
            recommendations_str: Comma-separated list of recommendations for future service
            cost: Cost of the service
            duration: Duration of the service in minutes
            notes: Additional notes about the service
            dialog: The dialog window to close after saving
        """
        # Validate required fields
        if not service_date or not service_type or not technician or not description:
            messagebox.showerror(
                "Validation Error", 
                "Service date, type, technician, and description are required."
            )
            return
        
        # Validate date format
        if not self._is_valid_date(service_date):
            messagebox.showerror("Validation Error", "Service date must be in YYYY-MM-DD format.")
            return
        
        # Parse chemicals added
        chemicals_added = []
        if chemicals_added_str:
            for item in chemicals_added_str.split(","):
                item = item.strip()
                if ":" in item:
                    name, amount = item.split(":", 1)
                    chemicals_added.append({
                        "name": name.strip(),
                        "amount": amount.strip()
                    })
                else:
                    chemicals_added.append({"name": item, "amount": ""})
        
        # Parse issues and recommendations
        issues = [i.strip() for i in issues_str.split(",") if i.strip()]
        recommendations = [r.strip() for r in recommendations_str.split(",") if r.strip()]
        
        # Update service record
        self.current_customer.update_service_record(
            record.service_id,
            {
                "service_date": service_date,
                "service_type": service_type,
                "technician": technician,
                "description": description,
                "chemical_readings": chemical_readings,
                "chemicals_added": chemicals_added,
                "issues": issues,
                "recommendations": recommendations,
                "cost": cost,
                "duration_minutes": duration,
                "notes": notes if notes else None
            }
        )
        
        # Update database
        self.db.update_customer(self.current_customer)
        
        # Close dialog
        dialog.destroy()
        
        # Reload service records
        self._load_service_records()
        
        # Show success message
        messagebox.showinfo("Success", "Service record updated successfully.")
    
    def _delete_service_record(self, record):
        """
        Delete a service record from the current customer.
        
        Args:
            record: The service record to delete
        """
        # Confirm deletion
        if not messagebox.askyesno(
            "Confirm Deletion",
            "Are you sure you want to delete this service record? This action cannot be undone."
        ):
            return
        
        # Delete service record
        self.current_customer.remove_service_record(record.service_id)
        
        # Update database
        self.db.update_customer(self.current_customer)
        
        # Reload service records
        self._load_service_records()
        
        # Show success message
        messagebox.showinfo("Success", "Service record deleted successfully.")


def create_customer_management_ui(root):
    """
    Create the customer management UI.
    
    Args:
        root: The root Tkinter window
    
    Returns:
        The CustomerManagementUI instance
    """
    return CustomerManagementUI(root)


if __name__ == "__main__":
    # Create a test window
    root = tk.Tk()
    root.title("Customer Management")
    root.geometry("1200x800")
    
    # Create the customer management UI
    ui = create_customer_management_ui(root)
    
    # Run the application
    root.mainloop()
