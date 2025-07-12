# app/gui_elements.py
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import logging
from typing import Dict, Any, Optional, Callable
import os
from datetime import datetime

from app.gui_controller import PoolChemistryController

# Configure logging
logger = logging.getLogger(__name__)

class PoolChemistryGUI:
    """
    GUI for the Pool Chemistry Calculator application.
    """
    
    def __init__(self):
        """Initialize the GUI with all components."""
        try:
            # Initialize the main window
            self.window = tk.Tk()
            self.window.title("Pool Chemistry Calculator")
            self.window.geometry("800x600")
            
            # Set application icon if available
            try:
                icon_path = os.path.join(os.path.dirname(__file__), "../assets/icon.ico")
                if os.path.exists(icon_path):
                    self.window.iconbitmap(icon_path)
            except Exception as e:
                logger.warning(f"Could not set application icon: {str(e)}")
            
            # Initialize the controller
            self.controller = PoolChemistryController()
            
            # Check database health
            if not self.controller.check_database_health():
                messagebox.showwarning(
                    "Database Warning",
                    "Database connection is not healthy. Some features may not work properly."
                )
            
            # Run database migrations
            self.controller.run_database_migrations()
            
            # Create the main frames
            self._create_frames()
            
            # Create the form widgets
            self._create_customer_widgets()
            self._create_pool_widgets()
            self._create_chemical_widgets()
            self._create_result_widgets()
            
            # Create the action buttons
            self._create_action_buttons()
            
            # Set up the menu
            self._create_menu()
            
            # Initialize status bar
            self._create_status_bar()
            
            # Set the default status
            self._set_status("Ready")
            
            logger.info("GUI initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing GUI: {str(e)}")
            messagebox.showerror(
                "Initialization Error",
                f"Failed to initialize application: {str(e)}"
            )
            raise
    
    def _create_frames(self):
        """Create the main frames for the GUI."""
        # Main frame with padding
        self.main_frame = ttk.Frame(self.window, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Customer information frame
        self.customer_frame = ttk.LabelFrame(self.main_frame, text="Customer Information")
        self.customer_frame.pack(fill="x", pady=5)
        
        # Pool information frame
        self.pool_frame = ttk.LabelFrame(self.main_frame, text="Pool Information")
        self.pool_frame.pack(fill="x", pady=5)
        
        # Chemical readings frame
        self.chemical_frame = ttk.LabelFrame(self.main_frame, text="Chemical Readings")
        self.chemical_frame.pack(fill="x", pady=5)
        
        # Results frame
        self.result_frame = ttk.LabelFrame(self.main_frame, text="Results")
        self.result_frame.pack(fill="both", expand=True, pady=5)
        
        # Button frame
        self.button_frame = ttk.Frame(self.main_frame)
        self.button_frame.pack(fill="x", pady=10)
    
    def _create_customer_widgets(self):
        """Create widgets for customer information."""
        # Create a grid layout for customer information
        for i in range(3):
            self.customer_frame.columnconfigure(i * 2 + 1, weight=1)
        
        # Customer name
        ttk.Label(self.customer_frame, text="Customer Name:").grid(
            row=0, column=0, sticky="w", padx=5, pady=2
        )
        self.customer_name_entry = ttk.Entry(self.customer_frame)
        self.customer_name_entry.grid(
            row=0, column=1, sticky="ew", padx=5, pady=2
        )
        
        # Location name
        ttk.Label(self.customer_frame, text="Location:").grid(
            row=0, column=2, sticky="w", padx=5, pady=2
        )
        self.location_entry = ttk.Entry(self.customer_frame)
        self.location_entry.grid(
            row=0, column=3, sticky="ew", padx=5, pady=2
        )
        
        # Date
        ttk.Label(self.customer_frame, text="Date:").grid(
            row=0, column=4, sticky="w", padx=5, pady=2
        )
        self.date_label = ttk.Label(
            self.customer_frame, 
            text=datetime.now().strftime("%Y-%m-%d")
        )
        self.date_label.grid(
            row=0, column=5, sticky="w", padx=5, pady=2
        )
    
    def _create_pool_widgets(self):
        """Create widgets for pool information."""
        # Create a grid layout for pool information
        for i in range(3):
            self.pool_frame.columnconfigure(i * 2 + 1, weight=1)
        
        # Pool type
        ttk.Label(self.pool_frame, text="Pool Type:").grid(
            row=0, column=0, sticky="w", padx=5, pady=2
        )
        self.pool_type_var = tk.StringVar()
        self.pool_type_combo = ttk.Combobox(
            self.pool_frame, 
            textvariable=self.pool_type_var,
            values=["Concrete", "Vinyl", "Fiberglass"]
        )
        self.pool_type_combo.grid(
            row=0, column=1, sticky="ew", padx=5, pady=2
        )
        
        # Pool size
        ttk.Label(self.pool_frame, text="Pool Size (gallons):").grid(
            row=0, column=2, sticky="w", padx=5, pady=2
        )
        self.pool_size_entry = ttk.Entry(self.pool_frame)
        self.pool_size_entry.grid(
            row=0, column=3, sticky="ew", padx=5, pady=2
        )
        
        # Temperature
        ttk.Label(self.pool_frame, text="Temperature (°F):").grid(
            row=0, column=4, sticky="w", padx=5, pady=2
        )
        self.temperature_entry = ttk.Entry(self.pool_frame)
        self.temperature_entry.insert(0, "78")
        self.temperature_entry.grid(
            row=0, column=5, sticky="ew", padx=5, pady=2
        )
    
    def _create_chemical_widgets(self):
        """Create widgets for chemical readings."""
        # Create a grid layout for chemical readings
        for i in range(4):
            self.chemical_frame.columnconfigure(i * 2 + 1, weight=1)
        
        # Define chemical parameters
        chemicals = [
            ("pH:", "ph"),
            ("Chlorine (ppm):", "chlorine"),
            ("Alkalinity (ppm):", "alkalinity"),
            ("Calcium Hardness (ppm):", "calcium_hardness"),
            ("Cyanuric Acid (ppm):", "cyanuric_acid"),
            ("Salt (ppm):", "salt"),
            ("Bromine (ppm):", "bromine"),
            ("Stabilizer (ppm):", "stabilizer")
        ]
        
        # Create entry fields for each chemical
        self.chemical_entries = {}
        
        for i, (label_text, field_name) in enumerate(chemicals):
            row = i // 4
            col = (i % 4) * 2
            
            ttk.Label(self.chemical_frame, text=label_text).grid(
                row=row, column=col, sticky="w", padx=5, pady=2
            )
            
            entry = ttk.Entry(self.chemical_frame, width=10)
            entry.grid(
                row=row, column=col + 1, sticky="ew", padx=5, pady=2
            )
            
            self.chemical_entries[field_name] = entry
    
    def _create_result_widgets(self):
        """Create widgets for displaying results."""
        # Create a text widget with scrollbar
        self.result_text = tk.Text(
            self.result_frame, 
            height=10, 
            wrap=tk.WORD,
            font=("Consolas", 10)
        )
        
        scrollbar = ttk.Scrollbar(
            self.result_frame, 
            orient="vertical", 
            command=self.result_text.yview
        )
        
        self.result_text.configure(yscrollcommand=scrollbar.set)
        
        # Pack the widgets
        self.result_text.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Make the text widget read-only
        self.result_text.config(state="disabled")
    
    def _create_action_buttons(self):
        """Create action buttons."""
        # Calculate button
        self.calculate_button = ttk.Button(
            self.button_frame, 
            text="Calculate",
            command=self.calculate_chemicals
        )
        self.calculate_button.pack(side="left", padx=5)
        
        # Save button
        self.save_button = ttk.Button(
            self.button_frame, 
            text="Save Results",
            command=self.save_results
        )
        self.save_button.pack(side="left", padx=5)
        
        # Export button
        self.export_button = ttk.Button(
            self.button_frame, 
            text="Export Report",
            command=self.export_report
        )
        self.export_button.pack(side="left", padx=5)
        
        # Clear button
        self.clear_button = ttk.Button(
            self.button_frame, 
            text="Clear Form",
            command=self.clear_form
        )
        self.clear_button.pack(side="left", padx=5)
        
        # Exit button
        self.exit_button = ttk.Button(
            self.button_frame, 
            text="Exit",
            command=self.window.destroy
        )
        self.exit_button.pack(side="right", padx=5)
    
    def _create_menu(self):
        """Create the application menu."""
        menubar = tk.Menu(self.window)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="New", command=self.clear_form)
        file_menu.add_command(label="Save Results", command=self.save_results)
        file_menu.add_command(label="Export Report", command=self.export_report)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.window.destroy)
        menubar.add_cascade(label="File", menu=file_menu)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        tools_menu.add_command(label="Calculate", command=self.calculate_chemicals)
        tools_menu.add_command(label="Database Health Check", command=self.check_database_health)
        tools_menu.add_command(label="Run Migrations", command=self.run_migrations)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about)
        menubar.add_cascade(label="Help", menu=help_menu)
        
        # Set the menu
        self.window.config(menu=menubar)
    
    def _create_status_bar(self):
        """Create the status bar."""
        self.status_bar = ttk.Label(
            self.window, 
            text="Ready", 
            relief=tk.SUNKEN, 
            anchor=tk.W
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def _set_status(self, message: str):
        """
        Set the status bar message.
        
        Args:
            message: Status message to display
        """
        self.status_bar.config(text=message)
        self.window.update_idletasks()
    
    def _get_form_data(self) -> Dict[str, Any]:
        """
        Get data from the form.
        
        Returns:
            Dictionary of form data
        """
        data = {
            "customer_name": self.customer_name_entry.get(),
            "location_name": self.location_entry.get(),
            "pool_type": self.pool_type_var.get(),
            "pool_size": self.pool_size_entry.get(),
            "temperature": self.temperature_entry.get()
        }
        
        # Add chemical readings
        for field_name, entry in self.chemical_entries.items():
            value = entry.get().strip()
            if value:
                data[field_name] = value
        
        return data
    
    def calculate_chemicals(self):
        """Calculate chemical adjustments based on form inputs."""
        try:
            self._set_status("Calculating...")
            
            # Get form data
            pool_data = self._get_form_data()
            
            # Calculate chemicals
            result = self.controller.calculate_chemicals(pool_data)
            
            # Display results
            self.display_results(result)
            
            self._set_status("Calculation completed")
            logger.info("Chemical calculation completed")
            
        except ValueError as e:
            self._set_status("Calculation failed")
            messagebox.showerror("Validation Error", str(e))
            logger.warning(f"Validation error: {str(e)}")
            
        except Exception as e:
            self._set_status("Calculation failed")
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            logger.error(f"Error calculating chemicals: {str(e)}")
    
    def display_results(self, result: Dict[str, Any]):
        """
        Display calculation results in the result text widget.
        
        Args:
            result: Dictionary of calculation results
        """
        # Enable text widget for editing
        self.result_text.config(state="normal")
        
        # Clear previous results
        self.result_text.delete(1.0, tk.END)
        
        # Display adjustments
        self.result_text.insert(tk.END, "CHEMICAL ADJUSTMENTS\n")
        self.result_text.insert(tk.END, "===================\n\n")
        
        for param, adjustment in result["adjustments"].items():
            self.result_text.insert(tk.END, f"{param}: {adjustment}\n")
        
        # Display water balance if available
        if result.get("water_balance"):
            wb = result["water_balance"]
            
            self.result_text.insert(tk.END, "\nWATER BALANCE\n")
            self.result_text.insert(tk.END, "============\n\n")
            self.result_text.insert(tk.END, f"LSI: {wb['lsi']}\n")
            self.result_text.insert(tk.END, f"Status: {wb['status']}\n")
            self.result_text.insert(tk.END, f"Recommendation: {wb['recommendation']}\n")
        
        # Display ideal ranges
        self.result_text.insert(tk.END, "\nIDEAL RANGES\n")
        self.result_text.insert(tk.END, "============\n\n")
        
        for param, (min_val, max_val) in result["ideal_ranges"].items():
            self.result_text.insert(tk.END, f"{param.capitalize()}: {min_val} - {max_val}\n")
        
        # Make text widget read-only again
        self.result_text.config(state="disabled")
    
    def save_results(self):
        """Save test results to the database."""
        try:
            self._set_status("Saving results...")
            
            # Get form data
            pool_data = self._get_form_data()
            
            # Save results
            test_id = self.controller.save_test_results(pool_data)
            
            if test_id:
                self._set_status(f"Results saved (Test ID: {test_id})")
                messagebox.showinfo(
                    "Success", 
                    f"Test results saved successfully (Test ID: {test_id})"
                )
                logger.info(f"Test results saved with ID {test_id}")
            else:
                self._set_status("Failed to save results")
                messagebox.showerror(
                    "Error", 
                    "Failed to save test results"
                )
                logger.error("Failed to save test results")
                
        except Exception as e:
            self._set_status("Failed to save results")
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            logger.error(f"Error saving results: {str(e)}")
    
    def export_report(self):
        """Export results to a file."""
        try:
            # Ask for file location
            file_path = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[
                    ("Text files", "*.txt"),
                    ("CSV files", "*.csv"),
                    ("All files", "*.*")
                ],
                title="Export Report"
            )
            
            if not file_path:
                return
            
            self._set_status("Exporting report...")
            
            # Get text content
            content = self.result_text.get(1.0, tk.END)
            
            # Write to file
            with open(file_path, "w") as f:
                f.write(content)
            
            self._set_status(f"Report exported to {file_path}")
            messagebox.showinfo(
                "Success", 
                f"Report exported to {file_path}"
            )
            logger.info(f"Report exported to {file_path}")
            
        except Exception as e:
            self._set_status("Failed to export report")
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            logger.error(f"Error exporting report: {str(e)}")
    
    def clear_form(self):
        """Clear all form inputs."""
        # Clear customer information
        self.customer_name_entry.delete(0, tk.END)
        self.location_entry.delete(0, tk.END)
        
        # Clear pool information
        self.pool_type_var.set("")
        self.pool_size_entry.delete(0, tk.END)
        self.temperature_entry.delete(0, tk.END)
        self.temperature_entry.insert(0, "78")
        
        # Clear chemical readings
        for entry in self.chemical_entries.values():
            entry.delete(0, tk.END)
        
        # Clear results
        self.result_text.config(state="normal")
        self.result_text.delete(1.0, tk.END)
        self.result_text.config(state="disabled")
        
        self._set_status("Form cleared")
        logger.info("Form cleared")
    
    def check_database_health(self):
        """Check database health and show result."""
        try:
            self._set_status("Checking database health...")
            
            if self.controller.check_database_health():
                self._set_status("Database connection is healthy")
                messagebox.showinfo(
                    "Database Health", 
                    "Database connection is healthy"
                )
                logger.info("Database health check passed")
            else:
                self._set_status("Database connection is not healthy")
                messagebox.showwarning(
                    "Database Health", 
                    "Database connection is not healthy"
                )
                logger.warning("Database health check failed")
                
        except Exception as e:
            self._set_status("Database health check failed")
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            logger.error(f"Error checking database health: {str(e)}")
    
    def run_migrations(self):
        """Run database migrations and show result."""
        try:
            self._set_status("Running database migrations...")
            
            if self.controller.run_database_migrations():
                self._set_status("Database migrations completed")
                messagebox.showinfo(
                    "Migrations", 
                    "Database migrations completed successfully"
                )
                logger.info("Database migrations completed")
            else:
                self._set_status("Database migrations failed")
                messagebox.showwarning(
                    "Migrations", 
                    "Database migrations failed"
                )
                logger.warning("Database migrations failed")
                
        except Exception as e:
            self._set_status("Database migrations failed")
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            logger.error(f"Error running database migrations: {str(e)}")
    
        def show_about(self):
        """Show about dialog."""
        messagebox.showinfo(
            "About Pool Chemistry Calculator",
            "Pool Chemistry Calculator

"
            "Version 1.0.0

"
            "A tool for calculating pool chemical adjustments
"
            "and maintaining proper water balance.

"
            "© 2025 Pool Chemistry Solutions"
        )
    
    def run(self):
        """Run the application main loop."""
        self.window.mainloop()


# Entry point
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("pool_chemistry.log"),
            logging.StreamHandler()
        ]
    )
    
    # Create and run the application
    app = PoolChemistryGUI()
    app.run()

