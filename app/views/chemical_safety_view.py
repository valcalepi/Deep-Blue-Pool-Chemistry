#!/usr/bin/env python3
"""
Chemical Safety View for Deep Blue Pool Chemistry

This module provides the UI components for displaying chemical safety information.
"""

import logging
import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)

class ChemicalSafetyView:
    """
    View for displaying chemical safety information.
    """
    
    def __init__(self, parent, chemical_safety_db=None, compatibility_matrix=None):
        """
        Initialize the chemical safety view.
        
        Args:
            parent: Parent tkinter container
            chemical_safety_db: ChemicalSafetyDatabase instance
            compatibility_matrix: ChemicalCompatibilityMatrix instance
        """
        self.parent = parent
        self.chemical_safety_db = chemical_safety_db
        self.compatibility_matrix = compatibility_matrix
        
        self.frame = ttk.Frame(parent)
        self._create_widgets()
        logger.info("Chemical Safety View initialized")
        
    def _create_widgets(self):
        """Create the UI widgets."""
        # Main layout - notebook with tabs
        self.notebook = ttk.Notebook(self.frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create tabs
        self.info_tab = ttk.Frame(self.notebook)
        self.compatibility_tab = ttk.Frame(self.notebook)
        self.procedures_tab = ttk.Frame(self.notebook)
        self.emergency_tab = ttk.Frame(self.notebook)
        
        self.notebook.add(self.info_tab, text="Chemical Information")
        self.notebook.add(self.compatibility_tab, text="Compatibility")
        self.notebook.add(self.procedures_tab, text="Procedures")
        self.notebook.add(self.emergency_tab, text="Emergency")
        
        # Create tab content
        self._create_info_tab()
        self._create_compatibility_tab()
        self._create_procedures_tab()
        self._create_emergency_tab()
        
    def _create_info_tab(self):
        """Create the chemical information tab content."""
        # Top frame for chemical selection
        selection_frame = ttk.Frame(self.info_tab)
        selection_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(selection_frame, text="Chemical:").pack(side=tk.LEFT, padx=(0, 5))
        
        # Get list of chemicals from database
        chemicals = ["chlorine", "bromine", "ph_increaser", "ph_decreaser", 
                    "alkalinity_increaser", "calcium_hardness_increaser", 
                    "cyanuric_acid", "algaecide"]
                    
        if self.chemical_safety_db:
            chemicals = list(self.chemical_safety_db.safety_data.keys())
            
        self.chemical_combo = ttk.Combobox(selection_frame, values=chemicals)
        self.chemical_combo.pack(side=tk.LEFT, padx=5)
        if chemicals:
            self.chemical_combo.current(0)
            
        self.chemical_combo.bind("<<ComboboxSelected>>", self._update_chemical_info)
        
        ttk.Label(selection_frame, text="Type:").pack(side=tk.LEFT, padx=(20, 5))
        self.type_combo = ttk.Combobox(selection_frame)
        self.type_combo.pack(side=tk.LEFT, padx=5)
        self.type_combo.bind("<<ComboboxSelected>>", self._update_chemical_info)
        
        ttk.Button(selection_frame, text="Show Information", command=self._update_chemical_info).pack(side=tk.LEFT, padx=20)
        
        # Main content area - split into sections
        content_frame = ttk.Frame(self.info_tab)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left column
        left_frame = ttk.Frame(content_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Description section
        self.description_frame = ttk.LabelFrame(left_frame, text="Description")
        self.description_frame.pack(fill=tk.BOTH, expand=True, padx=0, pady=(0, 5))
        
        self.description_text = tk.Text(self.description_frame, wrap=tk.WORD, height=4)
        self.description_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Hazards section
        self.hazards_frame = ttk.LabelFrame(left_frame, text="Hazards")
        self.hazards_frame.pack(fill=tk.BOTH, expand=True, padx=0, pady=(5, 0))
        
        self.hazards_text = tk.Text(self.hazards_frame, wrap=tk.WORD)
        self.hazards_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Right column
        right_frame = ttk.Frame(content_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # PPE section
        self.ppe_frame = ttk.LabelFrame(right_frame, text="Personal Protective Equipment")
        self.ppe_frame.pack(fill=tk.BOTH, expand=True, padx=0, pady=(0, 5))
        
        self.ppe_text = tk.Text(self.ppe_frame, wrap=tk.WORD, height=4)
        self.ppe_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Storage section
        self.storage_frame = ttk.LabelFrame(right_frame, text="Storage")
        self.storage_frame.pack(fill=tk.BOTH, expand=True, padx=0, pady=(5, 0))
        
        self.storage_text = tk.Text(self.storage_frame, wrap=tk.WORD)
        self.storage_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Initial update
        self._update_chemical_types()
        self._update_chemical_info()
        
    def _create_compatibility_tab(self):
        """Create the chemical compatibility tab content."""
        # Top frame for chemical selection
        selection_frame = ttk.Frame(self.compatibility_tab)
        selection_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(selection_frame, text="First Chemical:").pack(side=tk.LEFT, padx=(0, 5))
        
        # Get list of chemicals from compatibility matrix
        chemicals = ["chlorine_liquid", "chlorine_tablets", "bromine_tablets", "ph_increaser", "ph_decreaser"]
        chemical_names = {}
        
        if self.compatibility_matrix:
            chemicals = []
            for chem in self.compatibility_matrix.get_all_chemicals():
                chemicals.append(chem["id"])
                chemical_names[chem["id"]] = chem["name"]
                
        self.chem1_combo = ttk.Combobox(selection_frame, values=chemicals)
        self.chem1_combo.pack(side=tk.LEFT, padx=5)
        if chemicals:
            self.chem1_combo.current(0)
            
        ttk.Label(selection_frame, text="Second Chemical:").pack(side=tk.LEFT, padx=(20, 5))
        self.chem2_combo = ttk.Combobox(selection_frame, values=chemicals)
        self.chem2_combo.pack(side=tk.LEFT, padx=5)
        if len(chemicals) > 1:
            self.chem2_combo.current(1)
            
        ttk.Button(selection_frame, text="Check Compatibility", command=self._check_compatibility).pack(side=tk.LEFT, padx=20)
        
        # Results frame
        self.compat_results_frame = ttk.LabelFrame(self.compatibility_tab, text="Compatibility Results")
        self.compat_results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Status frame
        status_frame = ttk.Frame(self.compat_results_frame)
        status_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.compat_status_label = ttk.Label(status_frame, text="", font=("Arial", 12, "bold"))
        self.compat_status_label.pack(side=tk.LEFT)
        
        self.compat_wait_label = ttk.Label(status_frame, text="")
        self.compat_wait_label.pack(side=tk.RIGHT)
        
        # Warnings and precautions
        warnings_frame = ttk.LabelFrame(self.compat_results_frame, text="Warnings")
        warnings_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 5))
        
        self.compat_warnings_text = tk.Text(warnings_frame, wrap=tk.WORD, height=5)
        self.compat_warnings_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        precautions_frame = ttk.LabelFrame(self.compat_results_frame, text="Precautions")
        precautions_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(5, 10))
        
        self.compat_precautions_text = tk.Text(precautions_frame, wrap=tk.WORD, height=5)
        self.compat_precautions_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Full matrix button
        ttk.Button(self.compatibility_tab, text="View Full Compatibility Matrix", 
                  command=self._show_compatibility_matrix).pack(pady=10)
        
    def _create_procedures_tab(self):
        """Create the procedures tab content."""
        # Top frame for chemical selection
        selection_frame = ttk.Frame(self.procedures_tab)
        selection_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(selection_frame, text="Chemical:").pack(side=tk.LEFT, padx=(0, 5))
        
        # Get list of chemicals from database
        chemicals = ["chlorine", "bromine", "ph_increaser", "ph_decreaser", 
                    "alkalinity_increaser", "calcium_hardness_increaser", 
                    "cyanuric_acid", "algaecide"]
                    
        if self.chemical_safety_db:
            chemicals = list(self.chemical_safety_db.safety_data.keys())
            
        self.proc_chemical_combo = ttk.Combobox(selection_frame, values=chemicals)
        self.proc_chemical_combo.pack(side=tk.LEFT, padx=5)
        if chemicals:
            self.proc_chemical_combo.current(0)
            
        self.proc_chemical_combo.bind("<<ComboboxSelected>>", self._update_procedure_types)
        
        ttk.Label(selection_frame, text="Type:").pack(side=tk.LEFT, padx=(20, 5))
        self.proc_type_combo = ttk.Combobox(selection_frame)
        self.proc_type_combo.pack(side=tk.LEFT, padx=5)
        self.proc_type_combo.bind("<<ComboboxSelected>>", self._update_procedures)
        
        ttk.Button(selection_frame, text="Show Procedures", command=self._update_procedures).pack(side=tk.LEFT, padx=20)
        
        # Procedures content
        self.procedures_content = ttk.Frame(self.procedures_tab)
        self.procedures_content.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Handling procedures
        self.handling_frame = ttk.LabelFrame(self.procedures_content, text="Handling Procedures")
        self.handling_frame.pack(fill=tk.BOTH, expand=True, padx=0, pady=(0, 5))
        
        self.handling_text = tk.Text(self.handling_frame, wrap=tk.WORD)
        self.handling_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Application procedures
        self.application_frame = ttk.LabelFrame(self.procedures_content, text="Application Procedures")
        self.application_frame.pack(fill=tk.BOTH, expand=True, padx=0, pady=(5, 0))
        
        self.application_text = tk.Text(self.application_frame, wrap=tk.WORD)
        self.application_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Initial update
        self._update_procedure_types()
        self._update_procedures()
        
    def _create_emergency_tab(self):
        """Create the emergency tab content."""
        # Emergency information
        emergency_frame = ttk.Frame(self.emergency_tab)
        emergency_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Emergency contacts
        contacts_frame = ttk.LabelFrame(emergency_frame, text="Emergency Contacts")
        contacts_frame.pack(fill=tk.X, padx=0, pady=(0, 10))
        
        contacts = [
            ("Poison Control Center", "1-800-222-1222"),
            ("Emergency Services", "911"),
            ("Chemical Safety Hotline", "1-800-424-9300 (CHEMTREC)")
        ]
        
        for i, (name, number) in enumerate(contacts):
            ttk.Label(contacts_frame, text=name, font=("Arial", 10, "bold")).grid(row=i, column=0, sticky=tk.W, padx=10, pady=5)
            ttk.Label(contacts_frame, text=number).grid(row=i, column=1, sticky=tk.W, padx=10, pady=5)
        
        # Emergency procedures
        procedures_frame = ttk.LabelFrame(emergency_frame, text="General Emergency Procedures")
        procedures_frame.pack(fill=tk.BOTH, expand=True, padx=0, pady=10)
        
        procedures_text = tk.Text(procedures_frame, wrap=tk.WORD)
        procedures_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        emergency_procedures = """
CHEMICAL EXPOSURE EMERGENCY PROCEDURES

1. SKIN CONTACT
\u2022 Remove contaminated clothing immediately
\u2022 Rinse affected area with plenty of water for at least 15 minutes
\u2022 For serious chemical burns, cover with clean, dry bandage and seek medical attention immediately

2. EYE CONTACT
\u2022 Flush eyes with water for at least 15 minutes, holding eyelids open
\u2022 Remove contact lenses if present and easy to do
\u2022 Seek medical attention immediately

3. INHALATION
\u2022 Move to fresh air immediately
\u2022 If breathing is difficult, administer oxygen if available
\u2022 If not breathing, provide artificial respiration
\u2022 Seek medical attention immediately

4. INGESTION
\u2022 Do NOT induce vomiting unless directed by poison control or a medical professional
\u2022 Rinse mouth with water
\u2022 If conscious, drink 1-2 glasses of water to dilute
\u2022 Seek medical attention immediately

5. CHEMICAL SPILL
\u2022 Evacuate the area if spill is large or involves highly toxic chemicals
\u2022 Ensure adequate ventilation
\u2022 Wear appropriate protective equipment
\u2022 Contain the spill with absorbent material (sand, cat litter, commercial spill kit)
\u2022 Dispose of waste according to local regulations
\u2022 For large spills, call emergency services

ALWAYS HAVE SAFETY DATA SHEETS (SDS) AVAILABLE FOR ALL POOL CHEMICALS
"""
        procedures_text.insert(tk.END, emergency_procedures)
        procedures_text.config(state=tk.DISABLED)
        
        # Resources
        resources_frame = ttk.LabelFrame(emergency_frame, text="Additional Resources")
        resources_frame.pack(fill=tk.X, padx=0, pady=(10, 0))
        
        resources = [
            ("CDC - Chemical Safety", "https://www.cdc.gov/niosh/topics/chemical-safety/"),
            ("EPA - Pool Chemical Safety", "https://www.epa.gov/swimming-pools"),
            ("APSP - Pool Chemical Safety", "https://www.phta.org/safety/")
        ]
        
        for i, (name, url) in enumerate(resources):
            ttk.Label(resources_frame, text=name, font=("Arial", 10, "bold")).grid(row=i, column=0, sticky=tk.W, padx=10, pady=5)
            link = ttk.Label(resources_frame, text=url, foreground="blue", cursor="hand2")
            link.grid(row=i, column=1, sticky=tk.W, padx=10, pady=5)
            link.bind("<Button-1>", lambda e, url=url: webbrowser.open_new(url))
        
    def _update_chemical_types(self, event=None):
        """Update the chemical types dropdown based on selected chemical."""
        chemical = self.chemical_combo.get()
        
        if not self.chemical_safety_db or not chemical:
            self.type_combo.config(values=[])
            return
            
        # Get types for the selected chemical
        types = self.chemical_safety_db.get_chemical_types(chemical)
        
        if types:
            type_names = [t["name"] for t in types]
            self.type_combo.config(values=type_names)
            self.type_combo.current(0)
        else:
            self.type_combo.config(values=[])
            
    def _update_chemical_info(self, event=None):
        """Update the chemical information display."""
        chemical = self.chemical_combo.get()
        chemical_type = self.type_combo.get()
        
        if not self.chemical_safety_db or not chemical:
            for text_widget in [self.description_text, self.hazards_text, self.ppe_text, self.storage_text]:
                text_widget.delete(1.0, tk.END)
                text_widget.insert(tk.END, "No chemical safety information available")
            return
            
        # Get chemical information
        chemical_info = self.chemical_safety_db.get_chemical_info(chemical)
        
        # Clear text widgets
        for text_widget in [self.description_text, self.hazards_text, self.ppe_text, self.storage_text]:
            text_widget.delete(1.0, tk.END)
            
        # If no specific type or no types available
        if not chemical_type or not self.chemical_safety_db.get_chemical_types(chemical):
            # Display general information
            if "description" in chemical_info:
                self.description_text.insert(tk.END, chemical_info["description"])
                
            # No hazards, PPE, or storage in general info
            self.hazards_text.insert(tk.END, "Select a specific chemical type to view hazards")
            self.ppe_text.insert(tk.END, "Select a specific chemical type to view PPE requirements")
            self.storage_text.insert(tk.END, "Select a specific chemical type to view storage information")
            return
            
        # Find the specific type information
        type_info = None
        for t in self.chemical_safety_db.get_chemical_types(chemical):
            if t["name"] == chemical_type:
                type_info = t
                break
                
        if not type_info:
            for text_widget in [self.description_text, self.hazards_text, self.ppe_text, self.storage_text]:
                text_widget.delete(1.0, tk.END)
                text_widget.insert(tk.END, f"No information found for {chemical_type}")
            return
            
        # Display type-specific information
        self.description_text.insert(tk.END, type_info.get("description", "No description available"))
        
        # Display hazards
        for hazard in type_info.get("hazards", []):
            self.hazards_text.insert(tk.END, f"\u2022 {hazard}\
")
            
        # Display PPE
        for ppe in type_info.get("ppe", []):
            self.ppe_text.insert(tk.END, f"\u2022 {ppe}\
")
            
        # Display storage
        for storage in type_info.get("storage", []):
            self.storage_text.insert(tk.END, f"\u2022 {storage}\
")
            
    def _check_compatibility(self):
        """Check compatibility between two selected chemicals."""
        chem1 = self.chem1_combo.get()
        chem2 = self.chem2_combo.get()
        
        if not self.compatibility_matrix or not chem1 or not chem2:
            for widget in [self.compat_warnings_text, self.compat_precautions_text]:
                widget.delete(1.0, tk.END)
                widget.insert(tk.END, "Chemical compatibility information not available")
            return
            
        # Get compatibility information
        compat_info = self.compatibility_matrix.check_compatibility(chem1, chem2)
        
        # Update status
        if compat_info["compatible"]:
            self.compat_status_label.config(text="\u2713 COMPATIBLE", foreground="green")
        else:
            self.compat_status_label.config(text="\u2717 INCOMPATIBLE", foreground="red")
            
        # Update wait time
        if compat_info["wait_time"] > 0:
            self.compat_wait_label.config(text=f"Wait Time: {compat_info['wait_time']} hours")
        else:
            self.compat_wait_label.config(text="")
            
        # Update warnings
        self.compat_warnings_text.delete(1.0, tk.END)
        for warning in compat_info.get("warnings", []):
            self.compat_warnings_text.insert(tk.END, f"\u2022 {warning}\
")
            
        # Update precautions
        self.compat_precautions_text.delete(1.0, tk.END)
        for precaution in compat_info.get("precautions", []):
            self.compat_precautions_text.insert(tk.END, f"\u2022 {precaution}\
")
            
    def _show_compatibility_matrix(self):
        """Show the full compatibility matrix."""
        if not self.compatibility_matrix:
            messagebox.showerror("Error", "Chemical compatibility matrix not available")
            return
            
        # Create a new window for the matrix
        matrix_window = tk.Toplevel(self.parent)
        matrix_window.title("Chemical Compatibility Matrix")
        matrix_window.geometry("800x600")
        
        # Add a scrollable frame
        main_frame = ttk.Frame(matrix_window)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Add canvas with scrollbars
        canvas = tk.Canvas(main_frame)
        scrollbar_y = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=canvas.yview)
        scrollbar_x = ttk.Scrollbar(main_frame, orient=tk.HORIZONTAL, command=canvas.xview)
        
        canvas.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Create a frame inside the canvas
        matrix_frame = ttk.Frame(canvas)
        canvas.create_window((0, 0), window=matrix_frame, anchor=tk.NW)
        
        # Get HTML matrix
        html_matrix = self.compatibility_matrix.get_compatibility_html()
        
        # Create a label with the HTML content
        from tkinter import font
        
        label = ttk.Label(matrix_frame, text="Loading compatibility matrix...")
        label.pack(padx=10, pady=10)
        
        # Try to use tkhtmlview if available
        try:
            from tkhtmlview import HTMLLabel
            html_label = HTMLLabel(matrix_frame, html=html_matrix)
            html_label.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            label.destroy()  # Remove the loading label
        except ImportError:
            label.config(text="HTML view not available. Please export the matrix to view it.")
            
            # Add export buttons
            export_frame = ttk.Frame(matrix_frame)
            export_frame.pack(pady=10)
            
            ttk.Button(export_frame, text="Export to HTML", 
                      command=lambda: self._export_matrix_html()).pack(side=tk.LEFT, padx=5)
                      
            ttk.Button(export_frame, text="Export to CSV", 
                      command=lambda: self._export_matrix_csv()).pack(side=tk.LEFT, padx=5)
        
        # Update scroll region
        matrix_frame.update_idletasks()
        canvas.config(scrollregion=canvas.bbox(tk.ALL))
        
    def _export_matrix_html(self):
        """Export the compatibility matrix to an HTML file."""
        if not self.compatibility_matrix:
            messagebox.showerror("Error", "Chemical compatibility matrix not available")
            return
            
        from tkinter import filedialog
        import os
        
        file_path = filedialog.asksaveasfilename(
            title="Save Compatibility Matrix HTML",
            defaultextension=".html",
            filetypes=[("HTML files", "*.html")]
        )
        
        if file_path:
            try:
                html_content = """
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Chemical Compatibility Matrix</title>
                    <meta charset="UTF-8">
                </head>
                <body>
                    <h1>Chemical Compatibility Matrix</h1>
                """
                
                html_content += self.compatibility_matrix.get_compatibility_html()
                
                html_content += """
                </body>
                </html>
                """
                
                os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
                with open(file_path, 'w') as f:
                    f.write(html_content)
                    
                messagebox.showinfo("Success", f"Compatibility matrix exported to {file_path}")
                
                # Try to open the file in the default browser
                import webbrowser
                webbrowser.open(file_path)
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export matrix: {str(e)}")
                
    def _export_matrix_csv(self):
        """Export the compatibility matrix to a CSV file."""
        if not self.compatibility_matrix:
            messagebox.showerror("Error", "Chemical compatibility matrix not available")
            return
            
        from tkinter import filedialog
        
        file_path = filedialog.asksaveasfilename(
            title="Save Compatibility Matrix CSV",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")]
        )
        
        if file_path:
            success = self.compatibility_matrix.export_to_csv(file_path)
            
            if success:
                messagebox.showinfo("Success", f"Compatibility matrix exported to {file_path}")
            else:
                messagebox.showerror("Error", "Failed to export matrix")
                
    def _update_procedure_types(self, event=None):
        """Update the procedure types dropdown based on selected chemical."""
        chemical = self.proc_chemical_combo.get()
        
        if not self.chemical_safety_db or not chemical:
            self.proc_type_combo.config(values=[])
            return
            
        # Get types for the selected chemical
        types = self.chemical_safety_db.get_chemical_types(chemical)
        
        if types:
            type_names = [t["name"] for t in types]
            self.proc_type_combo.config(values=type_names)
            self.proc_type_combo.current(0)
        else:
            self.proc_type_combo.config(values=[])
            
        self._update_procedures()
            
    def _update_procedures(self, event=None):
        """Update the procedures display."""
        chemical = self.proc_chemical_combo.get()
        chemical_type = self.proc_type_combo.get()
        
        if not self.chemical_safety_db or not chemical:
            for text_widget in [self.handling_text, self.application_text]:
                text_widget.delete(1.0, tk.END)
                text_widget.insert(tk.END, "No procedure information available")
            return
            
        # Clear text widgets
        for text_widget in [self.handling_text, self.application_text]:
            text_widget.delete(1.0, tk.END)
            
        # Find the specific type information
        type_info = None
        for t in self.chemical_safety_db.get_chemical_types(chemical):
            if t["name"] == chemical_type:
                type_info = t
                break
                
        if not type_info:
            for text_widget in [self.handling_text, self.application_text]:
                text_widget.delete(1.0, tk.END)
                text_widget.insert(tk.END, f"No procedure information found for {chemical_type}")
            return
            
        # Display handling procedures
        for procedure in type_info.get("handling", []):
            self.handling_text.insert(tk.END, f"\u2022 {procedure}\
")
            
        # Display application procedures
        for procedure in type_info.get("application", []):
            self.application_text.insert(tk.END, f"\u2022 {procedure}\
")
            
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
def test_chemical_safety_view():
    """Test the chemical safety view."""
    import sys
    
    # Create a mock chemical safety database
    class MockChemicalSafetyDB:
        def __init__(self):
            self.safety_data = {
                "chlorine": {
                    "name": "Chlorine",
                    "types": [
                        {
                            "name": "Liquid Chlorine",
                            "description": "A liquid form of chlorine, typically 10-12% concentration",
                            "hazards": [
                                "Corrosive to skin and eyes",
                                "Toxic if ingested",
                                "Can release chlorine gas when mixed with acids"
                            ],
                            "ppe": [
                                "Chemical-resistant gloves",
                                "Safety goggles",
                                "Long-sleeved shirt"
                            ],
                            "storage": [
                                "Store in original container",
                                "Keep away from direct sunlight",
                                "Keep away from acids"
                            ],
                            "handling": [
                                "Use plastic measuring cup",
                                "Avoid splashing",
                                "Wash hands after handling"
                            ],
                            "application": [
                                "Add directly to pool water",
                                "Pour slowly around perimeter",
                                "Run pump for at least 1 hour after adding"
                            ]
                        },
                        {
                            "name": "Chlorine Tablets",
                            "description": "Slow-dissolving tablets containing trichloroisocyanuric acid",
                            "hazards": [
                                "Corrosive to skin and eyes",
                                "Toxic if ingested",
                                "Oxidizer - can intensify fire"
                            ],
                            "ppe": [
                                "Chemical-resistant gloves",
                                "Safety goggles",
                                "Dust mask"
                            ],
                            "storage": [
                                "Store in original container",
                                "Keep in cool, dry place",
                                "Keep away from flammable materials"
                            ],
                            "handling": [
                                "Use plastic tongs",
                                "Never touch with bare hands",
                                "Keep tablets dry until use"
                            ],
                            "application": [
                                "Place in skimmer basket or floater",
                                "Never throw directly into pool",
                                "Use 1 tablet per 10,000 gallons"
                            ]
                        }
                    ]
                },
                "ph_increaser": {
                    "name": "pH Increaser",
                    "description": "Raises pH and slightly increases alkalinity",
                    "types": []
                }
            }
            
        def get_chemical_info(self, chemical):
            return self.safety_data.get(chemical, {})
            
        def get_chemical_types(self, chemical):
            return self.safety_data.get(chemical, {}).get("types", [])
    
    # Create a mock compatibility matrix
    class MockCompatibilityMatrix:
        def check_compatibility(self, chem1, chem2):
            if chem1 == "chlorine_liquid" and chem2 == "ph_decreaser":
                return {
                    "compatible": False,
                    "warnings": ["Mixing chlorine and acid releases toxic chlorine gas"],
                    "precautions": ["Never mix these chemicals", "Wait 24 hours between adding"],
                    "wait_time": 24
                }
            else:
                return {
                    "compatible": True,
                    "warnings": [],
                    "precautions": ["Add chemicals one at a time", "Wait at least 1 hour between adding"],
                    "wait_time": 1
                }
                
        def get_all_chemicals(self):
            return [
                {"id": "chlorine_liquid", "name": "Liquid Chlorine"},
                {"id": "chlorine_tablets", "name": "Chlorine Tablets"},
                {"id": "ph_increaser", "name": "pH Increaser"},
                {"id": "ph_decreaser", "name": "pH Decreaser"}
            ]
            
        def get_compatibility_html(self):
            return """
            <table border="1">
                <tr>
                    <th></th>
                    <th>Liquid Chlorine</th>
                    <th>pH Decreaser</th>
                </tr>
                <tr>
                    <th>Liquid Chlorine</th>
                    <td style="background-color: green;">Compatible</td>
                    <td style="background-color: red;">Incompatible</td>
                </tr>
                <tr>
                    <th>pH Decreaser</th>
                    <td style="background-color: red;">Incompatible</td>
                    <td style="background-color: green;">Compatible</td>
                </tr>
            </table>
            """
            
        def export_to_csv(self, file_path):
            try:
                with open(file_path, 'w') as f:
                    f.write("Chemical,Liquid Chlorine,pH Decreaser\
")
                    f.write("Liquid Chlorine,Compatible,Incompatible\
")
                    f.write("pH Decreaser,Incompatible,Compatible\
")
                return True
            except:
                return False
    
    # Create the root window
    root = tk.Tk()
    root.title("Chemical Safety View Test")
    root.geometry("800x600")
    
    # Create the view
    view = ChemicalSafetyView(
        root,
        chemical_safety_db=MockChemicalSafetyDB(),
        compatibility_matrix=MockCompatibilityMatrix()
    )
    view.pack(fill=tk.BOTH, expand=True)
    
    # Run the application
    root.mainloop()

if __name__ == "__main__":
    test_chemical_safety_view()
