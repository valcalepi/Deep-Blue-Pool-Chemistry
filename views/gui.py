# views/gui.py
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, Dict, Any
import logging

class GUI:
    """Main GUI class for the application."""
    
    def __init__(self, controller):
        """
        Initialize the GUI.
        
        Args:
            controller: The controller instance
        """
        self.controller = controller
        self.window = tk.Tk()
        self.window.title("Pool Chemistry Calculator")
        
        # Create input fields and widgets
        self._create_input_fields()
        self._create_calculation_button()
        self._create_result_area()
        
    def _create_input_fields(self):
        """Create input fields for user data entry."""
        # Customer info section
        self._create_section("Customer Information")
        self.customer_name_entry = self._create_field("Customer Name:")
        
        # Pool info section
        self._create_section("Pool Information")
        self.pool_type_entry = self._create_field("Pool Type:")
        self.pool_size_entry = self._create_field("Pool Size (gallons):")
        
        # Chemical readings section
        self._create_section("Chemical Readings")
        self.pH_entry = self._create_field("pH Level:")
        self.chlorine_entry = self._create_field("Chlorine Level:")
        self.bromine_entry = self._create_field("Bromine Level:")
        self.alkalinity_entry = self._create_field("Alkalinity Level:")
        self.cyanuric_acid_entry = self._create_field("Cyanuric Acid Level:")
        self.calcium_hardness_entry = self._create_field("Calcium Hardness Level:")
        self.stabilizer_entry = self._create_field("Stabilizer Level:")
        self.salt_entry = self._create_field("Salt Level:")
        
    def _create_section(self, title: str):
        """Create a labeled section in the GUI."""
        section_frame = ttk.LabelFrame(self.window, text=title)
        section_frame.pack(fill="x", padx=10, pady=5)
        return section_frame
        
    def _create_field(self, label_text: str) -> ttk.Entry:
        """Create a labeled input field."""
        frame = ttk.Frame(self.window)
        frame.pack(fill="x", padx=10, pady=2)
        
        label = ttk.Label(frame, text=label_text, width=20)
        label.pack(side="left")
        
        entry = ttk.Entry(frame)
        entry.pack(side="left", fill="x", expand=True)
        
        return entry
        
    def _create_calculation_button(self):
        """Create the calculate button."""
        self.calculate_button = ttk.Button(
            self.window, 
            text="Calculate", 
            command=self.calculate_chemicals
        )
        self.calculate_button.pack(pady=10)
        
    def _create_result_area(self):
        """Create the result display area."""
        result_frame = ttk.LabelFrame(self.window, text="Results")
        result_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.result_text = tk.Text(result_frame, height=15)
        self.result_text.pack(fill="both", expand=True, padx=5, pady=5)
        
    def show_error_message(self, message: str):
        """Display an error message to the user."""
        messagebox.showerror("Error", message)
        
    def display_results(self, results: Dict[str, Any]):
        """Display calculation results in the result area."""
        self.result_text.delete(1.0, tk.END)
        
        # Format and display the results
        formatted_results = self._format_results(results)
        self.result_text.insert(tk.END, formatted_results)
        
    def _format_results(self, results: Dict[str, Any]) -> str:
        """Format the results dictionary into a readable string."""
        # Implementation...
        
    def run(self):
        """Start the main GUI event loop."""
        self.window.mainloop()

