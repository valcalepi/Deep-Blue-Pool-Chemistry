# modules/ui_components.py
"""
UI Components Module
Contains UI components for the Pool Chemistry Manager
"""

import os
import logging
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
from datetime import datetime

from modules.database_manager import DatabaseManager
from modules.business_logic import ChemicalCalculator, TestStripAnalyzer
from modules.reporting import ReportGenerator
from modules.utils import validate_float, validate_int

class ApplicationUI:
    """Main application UI for the Pool Chemistry Manager"""
    
    def __init__(self, root, config_manager):
        """Initialize the application UI"""
        self.logger = logging.getLogger(__name__)
        self.root = root
        self.config_manager = config_manager
        self.config = config_manager.get_config()
        
        # Initialize database manager
        self.db_manager = DatabaseManager(self.config)
        self.db_manager.connect()
        self.db_manager.initialize_database()
        
        # Initialize business logic components
        self.chemical_calculator = ChemicalCalculator(self.config)
        self.test_strip_analyzer = TestStripAnalyzer()
        
        # Initialize report generator
        self.report_generator = ReportGenerator(self.db_manager)
        
        # Initialize variables
        self._init_variables()
        
        # Set up the UI
        self._setup_ui()
        
        # Setup window close handler
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        
        self.logger.info("Application UI initialized")
    
    def _init_variables(self):
        """Initialize all tkinter variables"""
        # Water testing variables
        self.test_vars = {
            "ph": tk.StringVar(),
            "chlorine": tk.StringVar(),
            "alkalinity": tk.StringVar(),
            "hardness": tk.StringVar(),
            "cyanuric_acid": tk.StringVar()
        }
        
        # Chemical calculator variables
        self.pool_size_var = tk.StringVar(value=str(self.config["pool_defaults"]["size"]))
        
        self.current_vars = {
            "ph": tk.StringVar(),
            "chlorine": tk.StringVar(),
            "alkalinity": tk.StringVar(),
            "hardness": tk.StringVar(),
            "cyanuric_acid": tk.StringVar()
        }
        
        self.target_vars = {
            "ph": tk.StringVar(value=str(self.config["pool_defaults"]["target_ph"])),
            "chlorine": tk.StringVar(value=str(self.config["pool_defaults"]["target_chlorine"])),
            "alkalinity": tk.StringVar(value=str(self.config["pool_defaults"]["target_alkalinity"])),
            "hardness": tk.StringVar(value=str(self.config["pool_defaults"]["target_hardness"])),
            "cyanuric_acid": tk.StringVar(value=str(self.config["pool_defaults"]["target_cyanuric"]))
        }
        
        # Customer management variables
        self.customer_vars = {
            "name": tk.StringVar(),
            "phone": tk.StringVar(),
            "email": tk.StringVar(),
            "address": tk.StringVar(),
            "pool_size": tk.StringVar(),
            "pool_type": tk.StringVar(),
            "notes": None  # Will be Text widget
        }
        
        # Report variables
        self.report_type_var = tk.StringVar(value="Customer Summary")
        self.date_range_var = tk.StringVar(value="Last 30 Days")
        
        # Settings variables
        self._init_settings_variables()
        
        # Status bar variables
        self.status_text = tk.StringVar(value="Ready")
        self.time_text = tk.StringVar()
    
    def _init_settings_variables(self):
        """Initialize settings variables"""
        # Database settings
        self.db_type_var = tk.StringVar(value=self.config["database"]["type"])
        self.db_path_var = tk.StringVar(value=self.config["database"]["path"])
        
        # Pool defaults
        self.default_pool_size_var = tk.StringVar(value=str(self.config["pool_defaults"]["size"]))
        self.default_pool_type_var = tk.StringVar(value=self.config["pool_defaults"]["type"])
        self.default_ph_var = tk.StringVar(value=str(self.config["pool_defaults"]["target_ph"]))
        self.default_chlorine_var = tk.StringVar(value=str(self.config["pool_defaults"]["target_chlorine"]))
        self.default_alkalinity_var = tk.StringVar(value=str(self.config["pool_defaults"]["target_alkalinity"]))
        self.default_hardness_var = tk.StringVar(value=str(self.config["pool_defaults"]["target_hardness"]))
        self.default_cyanuric_var = tk.StringVar(value=str(self.config["pool_defaults"]["target_cyanuric"]))
        
        # Chemical preferences
        self.ph_increaser_var = tk.StringVar(value=self.config["chemicals"]["ph_increaser"])
        self.ph_decreaser_var = tk.StringVar(value=self.config["chemicals"]["ph_decreaser"])
        self.chlorine_type_var = tk.StringVar(value=self.config["chemicals"]["chlorine_type"])
        self.alk_increaser_var = tk.StringVar(value=self.config["chemicals"]["alkalinity_increaser"])
        
        # Safety settings
        self.max_adjustments_var = tk.StringVar(value=str(self.config["safety"]["max_adjustments"]))
        self.min_time_var = tk.StringVar(value=str(self.config["safety"]["min_time_hours"]))
        self.safety_warnings_var = tk.BooleanVar(value=self.config["safety"]["safety_warnings"])
        self.dosage_limits_var = tk.BooleanVar(value=self.config["safety"]["dosage_limits"])
        
        # Application settings
        self.theme_var = tk.StringVar(value=self.config["application"]["theme"])
        self.window_size_var = tk.StringVar(value=self.config["application"]["window_size"])
        self.autosave_var = tk.StringVar(value=str(self.config["application"]["autosave_minutes"]))
        self.startup_check_var = tk.BooleanVar(value=self.config["application"]["startup_check"])
        self.confirm_exit_var = tk.BooleanVar(value=self.config["application"]["confirm_exit"])
        self.log_level_var = tk.StringVar(value=self.config["application"]["log_level"])
        self.log_file_var = tk.StringVar(value=self.config["application"]["log_file"])
        self.log_size_var = tk.StringVar(value=str(self.config["application"]["log_size_mb"]))
    
    def _setup_ui(self):
        """Set up the user interface"""
        self.root.title("Pool Chemistry Manager - Professional Edition")
        self.root.geometry(self.config["application"]["window_size"])
        
        # Apply theme if available
        style = ttk.Style()
        try:
            style.theme_use(self.config["application"]["theme"])
        except:
            self.logger.warning(f"Theme {self.config['application']['theme']} not available")
        
        # Create menu
        self._create_menu()
        
        # Create main notebook
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create tabs
        self._create_water_testing_tab()
        self._create_chemical_calculator_tab()
        self._create_customer_management_tab()
        self._create_reports_tab()
        self._create_settings_tab()
        
        # Create status bar
        self._create_status_bar()
        
        # Load initial data
        self._load_customers()
        self._load_test_results()
        
        self.logger.info("UI setup complete")
    
    def _create_menu(self):
        """Create application menu"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Customer", command=self._new_customer)
        file_menu.add_separator()
        file_menu.add_command(label="Open Database", command=self._open_database)
        file_menu.add_separator()
        file_menu.add_command(label="Export Data", command=self._export_data)
        file_menu.add_command(label="Import Data", command=self._import_data)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self._on_closing)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Chemical Calculator", command=lambda: self.notebook.select(1))
        tools_menu.add_command(label="Generate Report", command=lambda: self.notebook.select(3))
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="User Guide", command=self._show_help)
        help_menu.add_command(label="Chemical Safety", command=self._show_safety_info)
        help_menu.add_separator()
        help_menu.add_command(label="About", command=self._show_about)
    
    def _create_water_testing_tab(self):
        """Create water testing tab"""
        test_frame = ttk.Frame(self.notebook)
        self.notebook.add(test_frame, text="Water Testing")
        
        # Input section
        input_frame = ttk.LabelFrame(test_frame, text="Test Results Input", padding="10")
        input_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # pH
        ttk.Label(input_frame, text="pH:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(input_frame, textvariable=self.test_vars["ph"], width=10).grid(row=0, column=1, padx=5, pady=5)
        ttk.Label(input_frame, text="(6.8 - 7.6)").grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        
        # Free Chlorine
        ttk.Label(input_frame, text="Free Chlorine (ppm):").grid(row=0, column=3, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(input_frame, textvariable=self.test_vars["chlorine"], width=10).grid(row=0, column=4, padx=5, pady=5)
        ttk.Label(input_frame, text="(1.0 - 3.0)").grid(row=0, column=5, sticky=tk.W, padx=5, pady=5)
        
        # Total Alkalinity
        ttk.Label(input_frame, text="Total Alkalinity (ppm):").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(input_frame, textvariable=self.test_vars["alkalinity"], width=10).grid(row=1, column=1, padx=5, pady=5)
        ttk.Label(input_frame, text="(80 - 120)").grid(row=1, column=2, sticky=tk.W, padx=5, pady=5)
        
        # Calcium Hardness
        ttk.Label(input_frame, text="Calcium Hardness (ppm):").grid(row=1, column=3, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(input_frame, textvariable=self.test_vars["hardness"], width=10).grid(row=1, column=4, padx=5, pady=5)
        ttk.Label(input_frame, text="(150 - 300)").grid(row=1, column=5, sticky=tk.W, padx=5, pady=5)
        
        # Cyanuric Acid
        ttk.Label(input_frame, text="Cyanuric Acid (ppm):").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(input_frame, textvariable=self.test_vars["cyanuric_acid"], width=10).grid(row=2, column=1, padx=5, pady=5)
        ttk.Label(input_frame, text="(30 - 50)").grid(row=2, column=2, sticky=tk.W, padx=5, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(input_frame)
        button_frame.grid(row=3, column=0, columnspan=6, pady=10)
        
        ttk.Button(button_frame, text="Save Results", command=self._save_test_results).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Clear", command=self._clear_test_inputs).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Analyze Test Strip", command=self._analyze_test_strip).pack(side=tk.LEFT, padx=5)
        
        # Results section
        results_frame = ttk.LabelFrame(test_frame, text="Test History", padding="10")
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Treeview for results
        columns = ("Date/Time", "pH", "Free Cl", "Total Alk", "Ca Hard", "Cyanuric")
        self.results_tree = ttk.Treeview(results_frame, columns=columns, show="headings", height=10)
        
        for col in columns:
            self.results_tree.heading(col, text=col)
            self.results_tree.column(col, width=100)
        
        # Scrollbar for results
        results_scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.results_tree.yview)
        self.results_tree.configure(yscrollcommand=results_scrollbar.set)
        
        self.results_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        results_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def _create_chemical_calculator_tab(self):
        """Create chemical calculator tab"""
        calc_frame = ttk.Frame(self.notebook)
        self.notebook.add(calc_frame, text="Chemical Calculator")
        
        # Pool info section
        pool_frame = ttk.LabelFrame(calc_frame, text="Pool Information", padding="10")
        pool_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(pool_frame, text="Pool Size (gallons):").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(pool_frame, textvariable=self.pool_size_var, width=15).grid(row=0, column=1, padx=5, pady=5)
        
        # Current values section
        current_frame = ttk.LabelFrame(calc_frame, text="Current Water Chemistry", padding="10")
        current_frame.pack(fill=tk.X, padx=10, pady=5)
        
        row = 0
        for param, var in self.current_vars.items():
            label_text = param.replace("_", " ").title()
            if param == "cyanuric_acid":
                label_text = "Cyanuric Acid"
            ttk.Label(current_frame, text=f"{label_text}:").grid(row=row//3, column=(row%3)*2, sticky=tk.W, padx=5, pady=5)
            ttk.Entry(current_frame, textvariable=var, width=10).grid(row=row//3, column=(row%3)*2+1, padx=5, pady=5)
            row += 1
        
        # Target values section
        target_frame = ttk.LabelFrame(calc_frame, text="Target Water Chemistry", padding="10")
        target_frame.pack(fill=tk.X, padx=10, pady=5)
        
        row = 0
        for param, var in self.target_vars.items():
            label_text = param.replace("_", " ").title()
            if param == "cyanuric_acid":
                label_text = "Cyanuric Acid"
            ttk.Label(target_frame, text=f"{label_text}:").grid(row=row//3, column=(row%3)*2, sticky=tk.W, padx=5, pady=5)
            ttk.Entry(target_frame, textvariable=var, width=10).grid(row=row//3, column=(row%3)*2+1, padx=5, pady=5)
            row += 1
        
        # Calculate button
        ttk.Button(calc_frame, text="Calculate Chemical Additions", 
                  command=self._calculate_chemicals).pack(pady=10)
        
        # Results section
        results_frame = ttk.LabelFrame(calc_frame, text="Chemical Addition Recommendations", padding="10")
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.calc_results_text = tk.Text(results_frame, wrap=tk.WORD, height=15)
        calc_scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.calc_results_text.yview)
        self.calc_results_text.configure(yscrollcommand=calc_scrollbar.set)
        
        self.calc_results_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        calc_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def _create_customer_management_tab(self):
        """Create customer management tab"""
        customer_frame = ttk.Frame(self.notebook)
        self.notebook.add(customer_frame, text="Customer Management")
        
        # Customer form section
        form_frame = ttk.LabelFrame(customer_frame, text="Customer Information", padding="10")
        form_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Name and Phone
        ttk.Label(form_frame, text="Name:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(form_frame, textvariable=self.customer_vars["name"], width=25).grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Phone:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(form_frame, textvariable=self.customer_vars["phone"], width=20).grid(row=0, column=3, padx=5, pady=5)
        
        # Email and Address
        ttk.Label(form_frame, text="Email:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(form_frame, textvariable=self.customer_vars["email"], width=25).grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Address:").grid(row=1, column=2, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(form_frame, textvariable=self.customer_vars["address"], width=30).grid(row=1, column=3, padx=5, pady=5)
        
        # Pool info
        ttk.Label(form_frame, text="Pool Size:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(form_frame, textvariable=self.customer_vars["pool_size"], width=15).grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Pool Type:").grid(row=2, column=2, sticky=tk.W, padx=5, pady=5)
        pool_type_combo = ttk.Combobox(form_frame, textvariable=self.customer_vars["pool_type"], width=15)
        pool_type_combo['values'] = ("Chlorine", "Salt Water", "Bromine", "UV/Ozone", "Natural")
        pool_type_combo.grid(row=2, column=3, padx=5, pady=5)
        
        # Notes
        ttk.Label(form_frame, text="Notes:").grid(row=3, column=0, sticky=tk.NW, padx=5, pady=5)
        self.customer_vars["notes"] = tk.Text(form_frame, width=60, height=4)
        self.customer_vars["notes"].grid(row=3, column=1, columnspan=3, padx=5, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=4, column=0, columnspan=4, pady=10)
        
        ttk.Button(button_frame, text="Add Customer", command=self._add_customer).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Update Customer", command=self._update_customer).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Delete Customer", command=self._delete_customer).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Clear Form", command=self._clear_customer_form).pack(side=tk.LEFT, padx=5)
        
        # Customer list section
        list_frame = ttk.LabelFrame(customer_frame, text="Customer List", padding="10")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Treeview for customers
        customer_columns = ("ID", "Name", "Phone", "Email", "Address", "Pool Size", "Pool Type")
        self.customer_tree = ttk.Treeview(list_frame, columns=customer_columns, show="headings", height=12)
        
        for col in customer_columns:
            self.customer_tree.heading(col, text=col)
            if col == "ID":
                self.customer_tree.column(col, width=50)
            elif col in ["Phone", "Pool Size", "Pool Type"]:
                self.customer_tree.column(col, width=100)
            else:
                self.customer_tree.column(col, width=150)
        
        # Bind selection event
        self.customer_tree.bind("<<TreeviewSelect>>", self._on_customer_select)
        
        # Scrollbar for customer list
        customer_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.customer_tree.yview)
        self.customer_tree.configure(yscrollcommand=customer_scrollbar.set)
        
        self.customer_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        customer_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def _create_reports_tab(self):
        """Create reports tab"""
        reports_frame = ttk.Frame(self.notebook)
        self.notebook.add(reports_frame, text="Reports")
        
        # Report options section
        options_frame = ttk.LabelFrame(reports_frame, text="Report Options", padding="10")
        options_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(options_frame, text="Report Type:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        report_combo = ttk.Combobox(options_frame, textvariable=self.report_type_var, width=20)
        report_combo['values'] = ("Customer Summary", "Test History", "Chemical Usage", 
                                 "Monthly Report", "Service Schedule", "Water Quality Trends")
        report_combo.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(options_frame, text="Date Range:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        date_combo = ttk.Combobox(options_frame, textvariable=self.date_range_var, width=15)
        date_combo['values'] = ("Last 7 Days", "Last 30 Days", "Last 90 Days", "This Year", "All Time")
        date_combo.grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Button(options_frame, text="Generate Report", command=self._generate_report).grid(row=0, column=4, padx=10, pady=5)
        
        # Report display section
        display_frame = ttk.LabelFrame(reports_frame, text="Report Output", padding="10")
        display_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.report_text = tk.Text(display_frame, wrap=tk.WORD, font=("Courier", 10))
        report_scrollbar = ttk.Scrollbar(display_frame, orient=tk.VERTICAL, command=self.report_text.yview)
        self.report_text.configure(yscrollcommand=report_scrollbar.set)
        
        self.report_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        report_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def _create_settings_tab(self):
        """Create settings tab"""
        settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(settings_frame, text="Settings")
        
        # Settings notebook
        settings_notebook = ttk.Notebook(settings_frame)
        settings_notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create settings sub-tabs
        self._create_database_settings(settings_notebook)
        self._create_pool_settings(settings_notebook)
        self._create_chemical_settings(settings_notebook)
        self._create_safety_settings(settings_notebook)
        self._create_app_settings(settings_notebook)
        
        # Settings buttons
        button_frame = ttk.Frame(settings_frame)
        button_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(button_frame, text="Save Settings", command=self._save_settings).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Load Settings", command=self._load_settings).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Reset to Defaults", command=self._reset_settings).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Export Settings", command=self._export_settings).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Import Settings", command=self._import_settings).pack(side=tk.LEFT, padx=5)
    
    def _create_database_settings(self, parent):
        """Create database settings tab"""
        db_frame = ttk.Frame(parent)
        parent.add(db_frame, text="Database")
        
        ttk.Label(db_frame, text="Database Type:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        db_type_combo = ttk.Combobox(db_frame, textvariable=self.db_type_var, width=15)
        db_type_combo['values'] = ("sqlite", "mysql", "postgresql")
        db_type_combo.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(db_frame, text="Database Path:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(db_frame, textvariable=self.db_path_var, width=40).grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(db_frame, text="Browse", command=self._browse_database).grid(row=1, column=2, padx=5, pady=5)
        
        # Database buttons
        db_buttons = ttk.Frame(db_frame)
        db_buttons.grid(row=2, column=0, columnspan=3, pady=10)
        
        ttk.Button(db_buttons, text="Test Connection", command=self._test_database_connection).pack(side=tk.LEFT, padx=5)
        ttk.Button(db_buttons, text="Initialize Database", command=self._initialize_database).pack(side=tk.LEFT, padx=5)
        ttk.Button(db_buttons, text="Backup Database", command=self._backup_database).pack(side=tk.LEFT, padx=5)
        ttk.Button(db_buttons, text="Restore Database", command=self._restore_database).pack(side=tk.LEFT, padx=5)
    
    def _create_pool_settings(self, parent):
        """Create pool default settings tab"""
        pool_frame = ttk.Frame(parent)
        parent.add(pool_frame, text="Pool Defaults")
        
        ttk.Label(pool_frame, text="Default Pool Size (gallons):").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(pool_frame, textvariable=self.default_pool_size_var, width=15).grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(pool_frame, text="Default Pool Type:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        pool_type_combo = ttk.Combobox(pool_frame, textvariable=self.default_pool_type_var, width=15)
        pool_type_combo['values'] = ("Chlorine", "Salt Water", "Bromine", "UV/Ozone", "Natural")
        pool_type_combo.grid(row=1, column=1, padx=5, pady=5)
        
        # Target chemistry values
        ttk.Label(pool_frame, text="Target Chemistry Values:", font=("Arial", 10, "bold")).grid(row=2, column=0, columnspan=2, sticky=tk.W, padx=5, pady=(15, 5))
        
        ttk.Label(pool_frame, text="Target pH:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(pool_frame, textvariable=self.default_ph_var, width=15).grid(row=3, column=1, padx=5, pady=5)
        
        ttk.Label(pool_frame, text="Target Free Chlorine (ppm):").grid(row=4, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(pool_frame, textvariable=self.default_chlorine_var, width=15).grid(row=4, column=1, padx=5, pady=5)
        
        ttk.Label(pool_frame, text="Target Total Alkalinity (ppm):").grid(row=5, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(pool_frame, textvariable=self.default_alkalinity_var, width=15).grid(row=5, column=1, padx=5, pady=5)
        
        ttk.Label(pool_frame, text="Target Calcium Hardness (ppm):").grid(row=6, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(pool_frame, textvariable=self.default_hardness_var, width=15).grid(row=6, column=1, padx=5, pady=5)
        
        ttk.Label(pool_frame, text="Target Cyanuric Acid (ppm):").grid(row=7, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(pool_frame, textvariable=self.default_cyanuric_var, width=15).grid(row=7, column=1, padx=5, pady=5)
    
    def _create_chemical_settings(self, parent):
        """Create chemical preferences settings tab"""
        chem_frame = ttk.Frame(parent)
        parent.add(chem_frame, text="Chemical Preferences")
        
        ttk.Label(chem_frame, text="pH Increaser:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        ph_inc_combo = ttk.Combobox(chem_frame, textvariable=self.ph_increaser_var, width=20)
        ph_inc_combo['values'] = ("Sodium Carbonate", "Sodium Bicarbonate", "Potassium Carbonate")
        ph_inc_combo.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(chem_frame, text="pH Decreaser:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        ph_dec_combo = ttk.Combobox(chem_frame, textvariable=self.ph_decreaser_var, width=20)
        ph_dec_combo['values'] = ("Muriatic Acid", "Sodium Bisulfate", "Sulfuric Acid")
        ph_dec_combo.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(chem_frame, text="Chlorine Type:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        chlorine_combo = ttk.Combobox(chem_frame, textvariable=self.chlorine_type_var, width=20)
        chlorine_combo['values'] = ("Liquid Chlorine", "Calcium Hypochlorite", "Sodium Hypochlorite", "Trichlor", "Dichlor")
        chlorine_combo.grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Label(chem_frame, text="Alkalinity Increaser:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        alk_combo = ttk.Combobox(chem_frame, textvariable=self.alk_increaser_var, width=20)
        alk_combo['values'] = ("Sodium Bicarbonate", "Sodium Carbonate")
        alk_combo.grid(row=3, column=1, padx=5, pady=5)
    
    def _create_safety_settings(self, parent):
        """Create safety settings tab"""
        safety_frame = ttk.Frame(parent)
        parent.add(safety_frame, text="Safety Settings")
        
        ttk.Label(safety_frame, text="Max Chemical Adjustments per Day:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(safety_frame, textvariable=self.max_adjustments_var, width=10).grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(safety_frame, text="Minimum Time Between Adjustments (hours):").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(safety_frame, textvariable=self.min_time_var, width=10).grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Checkbutton(safety_frame, text="Show Safety Warnings", variable=self.safety_warnings_var).grid(row=2, column=0, columnspan=2, sticky=tk.W, padx=5, pady=5)
        
        ttk.Checkbutton(safety_frame, text="Enable Dosage Limits", variable=self.dosage_limits_var).grid(row=3, column=0, columnspan=2, sticky=tk.W, padx=5, pady=5)
    
    def _create_app_settings(self, parent):
        """Create application settings tab"""
        app_frame = ttk.Frame(parent)
        parent.add(app_frame, text="Application")
        
        ttk.Label(app_frame, text="Theme:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        theme_combo = ttk.Combobox(app_frame, textvariable=self.theme_var, width=15)
        theme_combo['values'] = ("default", "clam", "alt", "classic")
        theme_combo.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(app_frame, text="Window Size:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        size_combo = ttk.Combobox(app_frame, textvariable=self.window_size_var, width=15)
        size_combo['values'] = ("1200x800", "1400x900", "1600x1000", "maximized")
        size_combo.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(app_frame, text="Autosave Interval (minutes):").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(app_frame, textvariable=self.autosave_var, width=10).grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Checkbutton(app_frame, text="Startup System Check", variable=self.startup_check_var).grid(row=3, column=0, columnspan=2, sticky=tk.W, padx=5, pady=5)
        
        ttk.Checkbutton(app_frame, text="Confirm Exit", variable=self.confirm_exit_var).grid(row=4, column=0, columnspan=2, sticky=tk.W, padx=5, pady=5)
        
        # Logging settings
        ttk.Label(app_frame, text="Log Level:").grid(row=5, column=0, sticky=tk.W, padx=5, pady=5)
        log_combo = ttk.Combobox(app_frame, textvariable=self.log_level_var, width=15)
        log_combo['values'] = ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")
        log_combo.grid(row=5, column=1, padx=5, pady=5)
        
        ttk.Label(app_frame, text="Log File:").grid(row=6, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(app_frame, textvariable=self.log_file_var, width=30).grid(row=6, column=1, padx=5, pady=5)
        
        ttk.Label(app_frame, text="Max Log Size (MB):").grid(row=7, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(app_frame, textvariable=self.log_size_var, width=10).grid(row=7, column=1, padx=5, pady=5)
    
    def _create_status_bar(self):
        """Create status bar"""
        self.status_bar = ttk.Frame(self.root)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        ttk.Label(self.status_bar, textvariable=self.status_text).pack(side=tk.LEFT, padx=5)
        
        # Add current time
        ttk.Label(self.status_bar, textvariable=self.time_text).pack(side=tk.RIGHT, padx=5)
        self._update_time()
    
    def _update_time(self):
        """Update time display"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.time_text.set(current_time)
        self.root.after(1000, self._update_time)
    
    # Event handlers and business logic methods
    def _save_test_results(self):
        """Save water test results"""
        try:
            # Get values from form
            test_data = {
                'ph': validate_float(self.test_vars["ph"].get()),
                'chlorine': validate_float(self.test_vars["chlorine"].get()),
                'alkalinity': validate_int(self.test_vars["alkalinity"].get()),
                'hardness': validate_int(self.test_vars["hardness"].get()),
                'cyanuric_acid': validate_int(self.test_vars["cyanuric_acid"].get()),
                'notes': ""
            }
            
            # Validate required fields
            if test_data['ph'] is None or test_data['chlorine'] is None:
                messagebox.showerror("Error", "pH and Free Chlorine are required fields")
                return
            
            # Save to database
            test_id = self.db_manager.add_water_test(test_data)
            
            if test_id:
                # Add to treeview
                self.results_tree.insert("", 0, values=(
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    test_data['ph'],
                    test_data['chlorine'],
                    test_data['alkalinity'],
                    test_data['hardness'],
                    test_data['cyanuric_acid']
                ))
                
                self.status_text.set("Test results saved successfully")
                self.logger.info(f"Test results saved: {test_data}")
            else:
                messagebox.showerror("Error", "Failed to save test results")
            
        except Exception as e:
            self.logger.error(f"Error saving test results: {e}")
            messagebox.showerror("Error", f"Failed to save test results: {e}")
    
    def _clear_test_inputs(self):
        """Clear test input fields"""
        for var in self.test_vars.values():
            var.set("")
        self.status_text.set("Test inputs cleared")
    
    def _analyze_test_strip(self):
        """Placeholder for test strip analysis"""
        messagebox.showinfo("Test Strip Analysis", "Test strip analysis feature coming soon!")
    
    def _calculate_chemicals(self):
        """Calculate chemical additions needed"""
        try:
            # Get pool size
            pool_size = validate_float(self.pool_size_var.get())
            if pool_size is None or pool_size <= 0:
                messagebox.showerror("Error", "Please enter a valid pool size")
                return
            
            # Get current and target values
            current = {}
            target = {}
            
            for param in self.current_vars:
                current[param] = validate_float(self.current_vars[param].get())
                target[param] = validate_float(self.target_vars[param].get())
            
            # Calculate recommendations
            recommendations = self.chemical_calculator.calculate_chemical_recommendations(pool_size, current, target)
            
            # Display results
            self.calc_results_text.delete(1.0, tk.END)
            self.calc_results_text.insert(tk.END, recommendations)
            
            self.status_text.set("Chemical calculations completed")
            
        except Exception as e:
            self.logger.error(f"Error calculating chemicals: {e}")
            messagebox.showerror("Error", f"Failed to calculate chemicals: {e}")
    
    def _add_customer(self):
        """Add new customer"""
        try:
            # Get customer data
            customer_data = {
                'name': self.customer_vars["name"].get(),
                'phone': self.customer_vars["phone"].get(),
                'email': self.customer_vars["email"].get(),
                'address': self.customer_vars["address"].get(),
                'pool_size': validate_int(self.customer_vars["pool_size"].get()),
                'pool_type': self.customer_vars["pool_type"].get(),
                'notes': self.customer_vars["notes"].get(1.0, tk.END).strip()
            }
            
            # Validate required fields
            if not customer_data['name']:
                messagebox.showerror("Error", "Customer name is required")
                return
            
            # Add to database
            customer_id = self.db_manager.add_customer(customer_data)
            
            if customer_id:
                # Add to treeview
                self.customer_tree.insert("", tk.END, values=(
                    customer_id,
                    customer_data['name'],
                    customer_data['phone'],
                    customer_data['email'],
                    customer_data['address'],
                    customer_data['pool_size'],
                    customer_data['pool_type']
                ))
                
                self._clear_customer_form()
                self.status_text.set("Customer added successfully")
                self.logger.info(f"Customer added: {customer_data['name']}")
            else:
                messagebox.showerror("Error", "Failed to add customer")
            
        except Exception as e:
            self.logger.error(f"Error adding customer: {e}")
            messagebox.showerror("Error", f"Failed to add customer: {e}")
    
    def _update_customer(self):
        """Update selected customer"""
        selected = self.customer_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a customer to update")
            return
        
        try:
            # Get updated data
            customer_data = {
                'name': self.customer_vars["name"].get(),
                'phone': self.customer_vars["phone"].get(),
                'email': self.customer_vars["email"].get(),
                'address': self.customer_vars["address"].get(),
                'pool_size': validate_int(self.customer_vars["pool_size"].get()),
                'pool_type': self.customer_vars["pool_type"].get(),
                'notes': self.customer_vars["notes"].get(1.0, tk.END).strip()
            }
            
            # Validate required fields
            if not customer_data['name']:
                messagebox.showerror("Error", "Customer name is required")
                return
            
            # Get customer ID from treeview
            item = selected[0]
            customer_id = int(self.customer_tree.item(item, 'values')[0])
            
            # Update in database
            success = self.db_manager.update_customer(customer_id, customer_data)
            
            if success:
                # Update treeview
                self.customer_tree.item(item, values=(
                    customer_id,
                    customer_data['name'],
                    customer_data['phone'],
                    customer_data['email'],
                    customer_data['address'],
                    customer_data['pool_size'],
                    customer_data['pool_type']
                ))
                
                self.status_text.set("Customer updated successfully")
                self.logger.info(f"Customer updated: {customer_data['name']}")
            else:
                messagebox.showerror("Error", "Failed to update customer")
            
        except Exception as e:
            self.logger.error(f"Error updating customer: {e}")
            messagebox.showerror("Error", f"Failed to update customer: {e}")
    
    def _delete_customer(self):
        """Delete selected customer"""
        selected = self.customer_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a customer to delete")
            return
        
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this customer?"):
            try:
                # Get customer ID from treeview
                item = selected[0]
                customer_id = int(self.customer_tree.item(item, 'values')[0])
                
                # Delete from database
                success = self.db_manager.delete_customer(customer_id)
                
                if success:
                    # Remove from treeview
                    self.customer_tree.delete(item)
                    self._clear_customer_form()
                    self.status_text.set("Customer deleted successfully")
                    self.logger.info("Customer deleted")
                else:
                    messagebox.showerror("Error", "Failed to delete customer")
                
            except Exception as e:
                self.logger.error(f"Error deleting customer: {e}")
                messagebox.showerror("Error", f"Failed to delete customer: {e}")
    
    def _clear_customer_form(self):
        """Clear customer form"""
        for key, var in self.customer_vars.items():
            if key == "notes":
                var.delete(1.0, tk.END)
            else:
                var.set("")
    
    def _on_customer_select(self, event):
        """Handle customer selection"""
        selected = self.customer_tree.selection()
        if selected:
            item = selected[0]
            values = self.customer_tree.item(item, 'values')
            
            # Populate form with selected customer data
            self.customer_vars["name"].set(values[1])
            self.customer_vars["phone"].set(values[2])
            self.customer_vars["email"].set(values[3])
            self.customer_vars["address"].set(values[4])
            self.customer_vars["pool_size"].set(values[5])
            self.customer_vars["pool_type"].set(values[6])
            
            # Get customer ID from treeview
            customer_id = int(values[0])
            
            # Get customer from database to get notes
            customer = self.db_manager.get_customer(customer_id)
            if customer and customer.get('notes'):
                self.customer_vars["notes"].delete(1.0, tk.END)
                self.customer_vars["notes"].insert(tk.END, customer['notes'])
    
    def _generate_report(self):
        """Generate selected report"""
        try:
            report_type = self.report_type_var.get()
            date_range = self.date_range_var.get()
            
            # Generate report based on type
            if report_type == "Customer Summary":
                report = self.report_generator.generate_customer_summary_report()
            elif report_type == "Test History":
                report = self.report_generator.generate_test_history_report()
            elif report_type == "Chemical Usage":
                report = self.report_generator.generate_chemical_usage_report()
            elif report_type == "Monthly Report":
                report = self.report_generator.generate_monthly_report()
            elif report_type == "Service Schedule":
                report = self.report_generator.generate_service_schedule_report()
            elif report_type == "Water Quality Trends":
                report = self.report_generator.generate_water_quality_trends_report()
            else:
                report = "Report type not implemented yet."
            
            # Display report
            self.report_text.delete(1.0, tk.END)
            self.report_text.insert(tk.END, report)
            
            self.status_text.set(f"{report_type} report generated")
            
        except Exception as e:
            self.logger.error(f"Error generating report: {e}")
            messagebox.showerror("Error", f"Failed to generate report: {e}")
    
    # Settings methods
    def _save_settings(self):
        """Save current settings"""
        try:
            self._update_config_from_gui()
            if self.config_manager.save_config():
                self.status_text.set("Settings saved successfully")
                messagebox.showinfo("Success", "Settings saved successfully")
            else:
                messagebox.showerror("Error", "Failed to save settings")
            
        except Exception as e:
            self.logger.error(f"Error saving settings: {e}")
            messagebox.showerror("Error", f"Failed to save settings: {e}")
    
    def _load_settings(self):
        """Load settings from file"""
        try:
            self.config_manager._load_config()
            self.config = self.config_manager.get_config()
            self._update_gui_from_config()
            self.status_text.set("Settings loaded successfully")
            messagebox.showinfo("Success", "Settings loaded successfully")
            
        except Exception as e:
            self.logger.error(f"Error loading settings: {e}")
            messagebox.showerror("Error", f"Failed to load settings: {e}")
    
    def _reset_settings(self):
        """Reset settings to defaults"""
        if messagebox.askyesno("Confirm Reset", "Are you sure you want to reset all settings to defaults?"):
            try:
                if self.config_manager.reset_to_defaults():
                    self.config = self.config_manager.get_config()
                    self._update_gui_from_config()
                    self.status_text.set("Settings reset to defaults")
                    messagebox.showinfo("Success", "Settings reset to defaults")
                else:
                    messagebox.showerror("Error", "Failed to reset settings")
                
            except Exception as e:
                self.logger.error(f"Error resetting settings: {e}")
                messagebox.showerror("Error", f"Failed to reset settings: {e}")
    
    def _export_settings(self):
        """Export settings to file"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            if filename:
                self._update_config_from_gui()
                if self.config_manager.export_config(filename):
                    self.status_text.set("Settings exported successfully")
                    messagebox.showinfo("Success", f"Settings exported to {filename}")
                else:
                    messagebox.showerror("Error", "Failed to export settings")
                
        except Exception as e:
            self.logger.error(f"Error exporting settings: {e}")
            messagebox.showerror("Error", f"Failed to export settings: {e}")
    
    def _import_settings(self):
        """Import settings from file"""
        try:
            filename = filedialog.askopenfilename(
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            if filename:
                if self.config_manager.import_config(filename):
                    self.config = self.config_manager.get_config()
                    self._update_gui_from_config()
                    self.status_text.set("Settings imported successfully")
                    messagebox.showinfo("Success", f"Settings imported from {filename}")
                else:
                    messagebox.showerror("Error", "Failed to import settings")
                
        except Exception as e:
            self.logger.error(f"Error importing settings: {e}")
            messagebox.showerror("Error", f"Failed to import settings: {e}")
    
    def _update_config_from_gui(self):
        """Update configuration from GUI values"""
        try:
            # Database settings
            self.config["database"]["type"] = self.db_type_var.get()
            self.config["database"]["path"] = self.db_path_var.get()
            
            # Pool defaults
            self.config["pool_defaults"]["size"] = validate_int(self.default_pool_size_var.get(), 20000)
            self.config["pool_defaults"]["type"] = self.default_pool_type_var.get()
            self.config["pool_defaults"]["target_ph"] = validate_float(self.default_ph_var.get(), 7.2)
            self.config["pool_defaults"]["target_chlorine"] = validate_float(self.default_chlorine_var.get(), 2.0)
            self.config["pool_defaults"]["target_alkalinity"] = validate_int(self.default_alkalinity_var.get(), 100)
            self.config["pool_defaults"]["target_hardness"] = validate_int(self.default_hardness_var.get(), 200)
            self.config["pool_defaults"]["target_cyanuric"] = validate_int(self.default_cyanuric_var.get(), 40)
            
            # Chemical preferences
            self.config["chemicals"]["ph_increaser"] = self.ph_increaser_var.get()
            self.config["chemicals"]["ph_decreaser"] = self.ph_decreaser_var.get()
            self.config["chemicals"]["chlorine_type"] = self.chlorine_type_var.get()
            self.config["chemicals"]["alkalinity_increaser"] = self.alk_increaser_var.get()
            
            # Safety settings
            self.config["safety"]["max_adjustments"] = validate_int(self.max_adjustments_var.get(), 3)
            self.config["safety"]["min_time_hours"] = validate_int(self.min_time_var.get(), 4)
            self.config["safety"]["safety_warnings"] = self.safety_warnings_var.get()
            self.config["safety"]["dosage_limits"] = self.dosage_limits_var.get()
            
            # Application settings
            self.config["application"]["theme"] = self.theme_var.get()
            self.config["application"]["window_size"] = self.window_size_var.get()
            self.config["application"]["autosave_minutes"] = validate_int(self.autosave_var.get(), 5)
            self.config["application"]["startup_check"] = self.startup_check_var.get()
            self.config["application"]["confirm_exit"] = self.confirm_exit_var.get()
            self.config["application"]["log_level"] = self.log_level_var.get()
            self.config["application"]["log_file"] = self.log_file_var.get()
            self.config["application"]["log_size_mb"] = validate_int(self.log_size_var.get(), 10)
            
            return True
        except Exception as e:
            self.logger.error(f"Error updating config from GUI: {e}")
            return False
    
    def _update_gui_from_config(self):
        """Update GUI from configuration"""
        try:
            # Database settings
            self.db_type_var.set(self.config["database"]["type"])
            self.db_path_var.set(self.config["database"]["path"])
            
            # Pool defaults
            self.default_pool_size_var.set(str(self.config["pool_defaults"]["size"]))
            self.default_pool_type_var.set(self.config["pool_defaults"]["type"])
            self.default_ph_var.set(str(self.config["pool_defaults"]["target_ph"]))
            self.default_chlorine_var.set(str(self.config["pool_defaults"]["target_chlorine"]))
            self.default_alkalinity_var.set(str(self.config["pool_defaults"]["target_alkalinity"]))
            self.default_hardness_var.set(str(self.config["pool_defaults"]["target_hardness"]))
            self.default_cyanuric_var.set(str(self.config["pool_defaults"]["target_cyanuric"]))
            
            # Update target values in calculator
            self.target_vars["ph"].set(str(self.config["pool_defaults"]["target_ph"]))
            self.target_vars["chlorine"].set(str(self.config["pool_defaults"]["target_chlorine"]))
            self.target_vars["alkalinity"].set(str(self.config["pool_defaults"]["target_alkalinity"]))
            self.target_vars["hardness"].set(str(self.config["pool_defaults"]["target_hardness"]))
            self.target_vars["cyanuric_acid"].set(str(self.config["pool_defaults"]["target_cyanuric"]))
            
            # Chemical preferences
            self.ph_increaser_var.set(self.config["chemicals"]["ph_increaser"])
            self.ph_decreaser_var.set(self.config["chemicals"]["ph_decreaser"])
            self.chlorine_type_var.set(self.config["chemicals"]["chlorine_type"])
            self.alk_increaser_var.set(self.config["chemicals"]["alkalinity_increaser"])
            
            # Safety settings
            self.max_adjustments_var.set(str(self.config["safety"]["max_adjustments"]))
            self.min_time_var.set(str(self.config["safety"]["min_time_hours"]))
            self.safety_warnings_var.set(self.config["safety"]["safety_warnings"])
            self.dosage_limits_var.set(self.config["safety"]["dosage_limits"])
            
            # Application settings
            self.theme_var.set(self.config["application"]["theme"])
            self.window_size_var.set(self.config["application"]["window_size"])
            self.autosave_var.set(str(self.config["application"]["autosave_minutes"]))
            self.startup_check_var.set(self.config["application"]["startup_check"])
            self.confirm_exit_var.set(self.config["application"]["confirm_exit"])
            self.log_level_var.set(self.config["application"]["log_level"])
            self.log_file_var.set(self.config["application"]["log_file"])
            self.log_size_var.set(str(self.config["application"]["log_size_mb"]))
            
        except Exception as e:
            self.logger.error(f"Error updating GUI from config: {e}")
    
    # Database methods
    def _browse_database(self):
        """Browse for database file"""
        filename = filedialog.askopenfilename(
            filetypes=[("SQLite files", "*.db"), ("All files", "*.*")]
        )
        if filename:
            self.db_path_var.set(filename)
    
    def _test_database_connection(self):
        """Test database connection"""
        try:
            # Update database settings
            self.config["database"]["type"] = self.db_type_var.get()
            self.config["database"]["path"] = self.db_path_var.get()
            
            # Test connection
            db_manager = DatabaseManager(self.config)
            if db_manager.connect():
                messagebox.showinfo("Database Test", "Connection successful!")
                db_manager.disconnect()
            else:
                messagebox.showerror("Database Test", "Connection failed!")
        except Exception as e:
            self.logger.error(f"Error testing database connection: {e}")
            messagebox.showerror("Database Test", f"Connection failed: {e}")
    
    def _initialize_database(self):
        """Initialize database"""
        try:
            if messagebox.askyesno("Initialize Database", "This will create or reset the database schema. Continue?"):
                # Update database settings
                self.config["database"]["type"] = self.db_type_var.get()
                self.config["database"]["path"] = self.db_path_var.get()
                
                # Initialize database
                db_manager = DatabaseManager(self.config)
                if db_manager.connect() and db_manager.initialize_database():
                    messagebox.showinfo("Database", "Database initialized successfully!")
                    
                    # Update current database manager
                    self.db_manager.disconnect()
                    self.db_manager = db_manager
                    
                    # Reload data
                    self._load_customers()
                    self._load_test_results()
                else:
                    messagebox.showerror("Database", "Failed to initialize database!")
        except Exception as e:
            self.logger.error(f"Error initializing database: {e}")
            messagebox.showerror("Database", f"Failed to initialize database: {e}")
    
    def _backup_database(self):
        """Backup database"""
        try:
            # Get backup file path
            backup_path = filedialog.asksaveasfilename(
                defaultextension=".db",
                filetypes=[("SQLite files", "*.db"), ("All files", "*.*")],
                initialfile=f"pool_chemistry_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
            )
            
            if backup_path:
                if self.db_manager.backup_database(backup_path):
                    messagebox.showinfo("Database Backup", f"Database backed up to {backup_path}")
                else:
                    messagebox.showerror("Database Backup", "Failed to backup database")
        except Exception as e:
            self.logger.error(f"Error backing up database: {e}")
            messagebox.showerror("Database Backup", f"Failed to backup database: {e}")
    
    def _restore_database(self):
        """Restore database"""
        try:
            # Get backup file path
            backup_path = filedialog.askopenfilename(
                filetypes=[("SQLite files", "*.db"), ("All files", "*.*")]
            )
            
            if backup_path:
                if messagebox.askyesno("Restore Database", "This will overwrite the current database. Continue?"):
                    if self.db_manager.restore_database(backup_path):
                        messagebox.showinfo("Database Restore", "Database restored successfully")
                        
                        # Reload data
                        self._load_customers()
                        self._load_test_results()
                    else:
                        messagebox.showerror("Database Restore", "Failed to restore database")
        except Exception as e:
            self.logger.error(f"Error restoring database: {e}")
            messagebox.showerror("Database Restore", f"Failed to restore database: {e}")
    
    # Data loading methods
    def _load_customers(self):
        """Load customers from database"""
        try:
            # Clear treeview
            for item in self.customer_tree.get_children():
                self.customer_tree.delete(item)
            
            # Get customers from database
            customers = self.db_manager.get_all_customers()
            
            # Add to treeview
            for customer in customers:
                self.customer_tree.insert("", tk.END, values=(
                    customer['id'],
                    customer['name'],
                    customer['phone'],
                    customer['email'],
                    customer['address'],
                    customer['pool_size'],
                    customer['pool_type']
                ))
            
            self.logger.info(f"Loaded {len(customers)} customers")
        except Exception as e:
            self.logger.error(f"Error loading customers: {e}")
    
    def _load_test_results(self):
        """Load test results from database"""
        try:
            # Clear treeview
            for item in self.results_tree.get_children():
                self.results_tree.delete(item)
            
            # Get test results from database
            tests = self.db_manager.get_water_tests()
            
            # Add to treeview
            for test in tests:
                self.results_tree.insert("", tk.END, values=(
                    test['date_time'],
                    test['ph'],
                    test['chlorine'],
                    test['alkalinity'],
                    test['hardness'],
                    test['cyanuric_acid']
                ))
            
            self.logger.info(f"Loaded {len(tests)} test results")
        except Exception as e:
            self.logger.error(f"Error loading test results: {e}")
    
    # Menu methods
    def _new_customer(self):
        """Create new customer"""
        self.notebook.select(2)  # Switch to customer management tab
        self._clear_customer_form()
    
    def _open_database(self):
        """Open database file"""
        filename = filedialog.askopenfilename(
            filetypes=[("SQLite files", "*.db"), ("All files", "*.*")]
        )
        if filename:
            try:
                # Update database path
                self.config["database"]["path"] = filename
                
                # Reconnect to database
                self.db_manager.disconnect()
                self.db_manager = DatabaseManager(self.config)
                if self.db_manager.connect():
                    # Reload data
                    self._load_customers()
                    self._load_test_results()
                    
                    self.status_text.set(f"Database opened: {filename}")
                else:
                    messagebox.showerror("Database", "Failed to open database")
            except Exception as e:
                self.logger.error(f"Error opening database: {e}")
                messagebox.showerror("Database", f"Failed to open database: {e}")
    
    def _export_data(self):
        """Export data"""
        messagebox.showinfo("Export Data", "Data export feature coming soon!")
    
    def _import_data(self):
        """Import data"""
        messagebox.showinfo("Import Data", "Data import feature coming soon!")
    
    def _show_help(self):
        """Show help dialog"""
        help_text = """
Pool Chemistry Manager - User Guide

WATER TESTING:
- Enter test results in the Water Testing tab
- Values are automatically validated against normal ranges
- Test history is saved and displayed

CHEMICAL CALCULATOR:
- Enter pool size and current chemistry values
- Set target values for optimal water balance
- Get specific chemical addition recommendations

CUSTOMER MANAGEMENT:
- Add, edit, and delete customer information
- Track pool specifications and service notes
- Maintain complete customer database

REPORTS:
- Generate various reports for analysis
- Export reports for record keeping
- Track trends and service history

SETTINGS:
- Customize default values and preferences
- Configure chemical types and safety limits
- Set application preferences

For more help, contact support.
        """
        
        help_window = tk.Toplevel(self.root)
        help_window.title("User Guide")
        help_window.geometry("600x500")
        
        text_widget = tk.Text(help_window, wrap=tk.WORD, padx=10, pady=10)
        text_widget.pack(fill=tk.BOTH, expand=True)
        text_widget.insert(tk.END, help_text)
        text_widget.config(state=tk.DISABLED)
    
    def _show_safety_info(self):
        """Show chemical safety information"""
        safety_text = """
CHEMICAL SAFETY INFORMATION

GENERAL SAFETY RULES:
• Always wear protective equipment (gloves, goggles)
• Never mix chemicals directly
• Add chemicals to water, never water to chemicals
• Store chemicals in original containers
• Keep chemicals away from children and pets
• Ensure adequate ventilation when handling chemicals

SPECIFIC CHEMICAL HAZARDS:

MURIATIC ACID (pH Decreaser):
• Highly corrosive - can cause severe burns
• Use in well-ventilated area
• Never mix with chlorine products
• Add slowly to deep end of pool

CHLORINE PRODUCTS:
• Can cause respiratory irritation
• Never mix with acids or other chemicals
• Store in cool, dry place away from heat
• Use proper measuring equipment

SODIUM CARBONATE (pH Increaser):
• Can cause eye and skin irritation
• Avoid inhaling dust
• Dissolve completely before adding to pool

EMERGENCY PROCEDURES:
• Skin contact: Flush with water for 15 minutes
• Eye contact: Flush with water for 15 minutes, seek medical attention
• Inhalation: Move to fresh air, seek medical attention if needed
• Ingestion: Do not induce vomiting, seek immediate medical attention

FIRST AID:
• Keep emergency numbers readily available
• Have eyewash station or clean water source nearby
• Know location of nearest hospital

For emergencies, call 911 immediately.
        """
        
        safety_window = tk.Toplevel(self.root)
        safety_window.title("Chemical Safety Information")
        safety_window.geometry("700x600")
        
        text_widget = tk.Text(safety_window, wrap=tk.WORD, padx=10, pady=10)
        text_widget.pack(fill=tk.BOTH, expand=True)
        text_widget.insert(tk.END, safety_text)
        text_widget.config(state=tk.DISABLED)
    
    def _show_about(self):
        """Show about dialog"""
        about_text = """
Deep Blue Pool Chemistry Manager Professional Edition – Version 3.0.0 Build Date: July 22, 2025

Your all-in-one solution for pool service professionals and dedicated pool owners. Meticulously engineered to streamline water quality control, client servicing, and daily operations.

💡 Key Features
Intelligent water testing & real-time analysis

Precision chemical dosage recommendations

Robust customer database with profile tracking

Smart scheduling for service appointments

In-depth reporting and history logs

Built-in safety guidance for responsible handling

🛠 Developed by: Deep Blue Pool Chemistry Center📞 Support: SavageBiz.com 🌐 Visit us: www.savagebiz.com

© 2025 SavageBiz. All rights reserved.
        """
        
        messagebox.showinfo("About Pool Chemistry Manager", about_text)
    
    def _on_closing(self):
        """Handle application closing"""
        try:
            if self.config["application"]["confirm_exit"]:
                if not messagebox.askyesno("Exit", "Are you sure you want to exit?"):
                    return
            
            # Save configuration
            self._update_config_from_gui()
            self.config_manager.save_config()
            
            # Disconnect from database
            self.db_manager.disconnect()
            
            self.logger.info("Pool Chemistry Manager closing")
            self.root.destroy()
            
        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")
            self.root.destroy()
    
    def run(self):
        """Run the application"""
        try:
            self.logger.info("Starting Pool Chemistry Manager GUI")
            self.root.mainloop()
        except Exception as e:
            self.logger.error(f"Error running application: {e}")
            messagebox.showerror("Application Error", f"An error occurred: {e}")
