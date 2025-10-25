# src/gui_elements.py

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import logging
from typing import Dict, Any, Optional, Callable
import os
from datetime import datetime
import functools

from app.gui_controller import PoolChemistryController
from constants import MIN_WINDOW_SIZE  # Import from constants instead of redefining

logger = logging.getLogger(__name__)

class PoolChemistryGUI:
    """
    Main GUI class for the Pool Chemistry Calculator application.
    
    This class handles the creation and arrangement of all GUI elements,
    connects to the controller for business logic, and manages user interactions.
    """
    
    def __init__(self):
        """Initialize the GUI with all necessary components and connections."""
        self.window = tk.Tk()
        self.window.title("Pool Chemistry Calculator")
        self.window.geometry(f"{MIN_WINDOW_SIZE[0]}x{MIN_WINDOW_SIZE[1]}")
        self.window.minsize(MIN_WINDOW_SIZE[0], MIN_WINDOW_SIZE[1])
        
        self._set_icon()
        self._connect_to_controller()
        self._initialize_gui_components()
        logger.info("GUI initialized successfully")
    
    def _set_icon(self):
        """Set the application icon with proper error handling."""
        try:
            icon_path = os.path.join(os.path.dirname(__file__), "../assets/icon.ico")
            if os.path.exists(icon_path):
                self.window.iconbitmap(icon_path)
            else:
                logger.warning(f"Icon file not found: {icon_path}")
        except Exception as e:
            logger.warning(f"Could not set application icon: {e}")

    def _connect_to_controller(self):
        """
        Initialize connection to the controller and database.
        
        Handles database health checks and migrations with proper error handling.
        """
        try:
            self.controller = PoolChemistryController()
            
            if not self.controller.check_database_health():
                messagebox.showwarning(
                    "Database Warning",
                    "Database connection issue. Some features might not work."
                )
            
            self.controller.run_database_migrations()
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            messagebox.showerror("Error", "Failed to connect to the database.")
            # Don't quit here; allow user to work with limited functionality
    
    def _initialize_gui_components(self):
        """Initialize all GUI components in the correct order."""
        self._create_frames()
        self._create_customer_widgets()
        self._create_pool_widgets()
        self._create_chemical_widgets()
        self._create_result_widgets()
        self._create_action_buttons()
        self._create_menu()
        self._create_status_bar()
        self._set_status("Ready")
    
    def _create_frames(self):
        """
        Create the main frames for the GUI.
        
        Organizes the application into logical sections for different types of data.
        """
        self.main_frame = ttk.Frame(self.window, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Create frames with descriptive names
        frames = {
            'customer_frame': "Customer Information",
            'pool_frame': "Pool Information",
            'chemical_frame': "Chemical Readings",
            'result_frame': "Results",
            'button_frame': None  # No label for button frame
        }

        for frame_attr, frame_text in frames.items():
            if frame_text:
                frame = ttk.LabelFrame(self.main_frame, text=frame_text)
                frame.pack(fill="x", pady=5)
            else:
                frame = ttk.Frame(self.main_frame)
                frame.pack(fill="x", pady=10)
            setattr(self, frame_attr, frame)
            
    def _create_customer_widgets(self):
        """
        Create widgets for customer information input.
        
        Includes fields for name, contact info, and customer ID.
        """
        # Implementation of customer widgets
        customer_fields = [
            ("Name", "name"),
            ("Phone", "phone"),
            ("Email", "email"),
            ("Customer ID", "id")
        ]
        
        self.customer_entries = {}
        
        for row, (label_text, field_name) in enumerate(customer_fields):
            label = ttk.Label(self.customer_frame, text=f"{label_text}:")
            label.grid(row=row, column=0, sticky="e", padx=5, pady=2)
            
            entry = ttk.Entry(self.customer_frame)
            entry.grid(row=row, column=1, sticky="ew", padx=5, pady=2)
            
            self.customer_entries[field_name] = entry
        
        # Make columns expandable
        self.customer_frame.columnconfigure(1, weight=1)

    def _create_pool_widgets(self):
        """
        Create widgets for pool information input.
        
        Includes fields for pool size, type, and treatment history.
        """
        # Implementation of pool widgets
        pool_fields = [
            ("Length (ft)", "length"),
            ("Width (ft)", "width"),
            ("Depth (ft)", "depth"),
            ("Type", "type"),
            ("Last Treatment", "last_treatment")
        ]
        
        self.pool_entries = {}
        
        for row, (label_text, field_name) in enumerate(pool_fields):
            label = ttk.Label(self.pool_frame, text=f"{label_text}:")
            label.grid(row=row, column=0, sticky="e", padx=5, pady=2)
            
            if field_name == "type":
                entry = ttk.Combobox(self.pool_frame, values=["Vinyl", "Concrete", "Fiberglass"])
                entry.current(0)
            elif field_name == "last_treatment":
                entry = ttk.Entry(self.pool_frame)
                entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
            else:
                entry = ttk.Entry(self.pool_frame)
            
            entry.grid(row=row, column=1, sticky="ew", padx=5, pady=2)
            self.pool_entries[field_name] = entry
        
        # Calculate volume button
        volume_button = ttk.Button(
            self.pool_frame,
            text="Calculate Volume",
            command=self._calculate_pool_volume
        )
        volume_button.grid(row=len(pool_fields), column=0, columnspan=2, pady=5)
        
        # Volume result label
        self.volume_label = ttk.Label(self.pool_frame, text="Volume: N/A")
        self.volume_label.grid(row=len(pool_fields)+1, column=0, columnspan=2, pady=5)
        
        # Make columns expandable
        self.pool_frame.columnconfigure(1, weight=1)
        
    def _calculate_pool_volume(self):
        """Calculate and display the pool volume based on dimensions."""
        try:
            length = float(self.pool_entries["length"].get())
            width = float(self.pool_entries["width"].get())
            depth = float(self.pool_entries["depth"].get())
            
            # Basic validation
            if length <= 0 or width <= 0 or depth <= 0:
                raise ValueError("Dimensions must be positive numbers")
                
            # Calculate volume in gallons (length × width × depth × 7.5)
            volume = length * width * depth * 7.5
            self.volume_label.config(text=f"Volume: {volume:.2f} gallons")
            
            # Update controller with volume for calculations
            if hasattr(self.controller, 'set_pool_volume'):
                self.controller.set_pool_volume(volume)
                
        except ValueError as e:
            messagebox.showerror("Input Error", f"Invalid dimensions: {str(e)}")
        except Exception as e:
            logger.error(f"Error calculating volume: {e}")
            messagebox.showerror("Error", f"Failed to calculate volume: {str(e)}")

    def _create_chemical_widgets(self):
        """
        Create widgets for chemical readings input.
        
        Includes fields for pH, chlorine, alkalinity, etc. with validation.
        """
        # Implementation of chemical widgets
        chemical_fields = [
            ("pH", "ph", 0.0, 14.0),
            ("Free Chlorine (ppm)", "free_chlorine", 0.0, 10.0),
            ("Total Chlorine (ppm)", "total_chlorine", 0.0, 10.0),
            ("Alkalinity (ppm)", "alkalinity", 0.0, 300.0),
            ("Hardness (ppm)", "hardness", 0.0, 1000.0),
            ("Cyanuric Acid (ppm)", "cyanuric_acid", 0.0, 100.0)
        ]
        
        self.chemical_entries = {}
        self.chemical_validators = {}
        
        for row, (label_text, field_name, min_val, max_val) in enumerate(chemical_fields):
            label = ttk.Label(self.chemical_frame, text=f"{label_text}:")
            label.grid(row=row, column=0, sticky="e", padx=5, pady=2)
            
            # Create validation function for this field
            validate_cmd = (self.window.register(
                lambda value, min_v=min_val, max_v=max_val: self._validate_chemical_input(value, min_v, max_v)), 
                '%P'
            )
            
            entry = ttk.Entry(self.chemical_frame, validate="key", validatecommand=validate_cmd)
            entry.grid(row=row, column=1, sticky="ew", padx=5, pady=2)
            
            self.chemical_entries[field_name] = entry
        
        # Make columns expandable
        self.chemical_frame.columnconfigure(1, weight=1)
    
    def _validate_chemical_input(self, value, min_val, max_val):
        """Validate that chemical inputs are within appropriate ranges."""
        # Allow empty string for clearing the field
        if value == "":
            return True
        
        try:
            float_value = float(value)
            # Allow partial input (e.g., starting to type "7." for pH)
            if value.endswith('.'):
                return True
            return min_val <= float_value <= max_val
        except ValueError:
            return False

    def _create_result_widgets(self):
        """
        Create widgets for displaying calculation results.
        
        Includes a text area for recommendations and adjustment details.
        """
        # Create a frame for the results with scrollbars
        result_container = ttk.Frame(self.result_frame)
        result_container.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Add scrollbars
        scrollbar_y = ttk.Scrollbar(result_container, orient="vertical")
        scrollbar_y.pack(side="right", fill="y")
        
        scrollbar_x = ttk.Scrollbar(result_container, orient="horizontal")
        scrollbar_x.pack(side="bottom", fill="x")
        
        # Create the text widget
        self.result_text = tk.Text(
            result_container,
            wrap="word",
            height=10,
            width=50,
            yscrollcommand=scrollbar_y.set,
            xscrollcommand=scrollbar_x.set
        )
        self.result_text.pack(fill="both", expand=True)
        
        # Configure scrollbars
        scrollbar_y.config(command=self.result_text.yview)
        scrollbar_x.config(command=self.result_text.xview)
        
        # Configure tags for colored text
        self.result_text.tag_configure("normal", foreground="black")
        self.result_text.tag_configure("good", foreground="green")
        self.result_text.tag_configure("warning", foreground="orange")
        self.result_text.tag_configure("error", foreground="red")
        self.result_text.tag_configure("header", font=("Arial", 12, "bold"))
        
        # Default text
        self.clear_results()

    def clear_results(self):
        """Clear the results display area."""
        self.result_text.config(state="normal")
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, "Enter readings and click 'Calculate' to see recommendations.", "normal")
        self.result_text.config(state="disabled")

    def _create_action_buttons(self):
        """Create the action buttons for the application."""
        # Button definitions with commands
        buttons = [
            ("Calculate", self._on_calculate, True),  # Primary button
            ("Clear", self._on_clear, False),
            ("Save", self._on_save, False),
            ("Load", self._on_load, False),
            ("Exit", self._on_exit, False)
        ]
        
        # Create buttons with appropriate styling
        for col, (text, command, is_primary) in enumerate(buttons):
            if is_primary:
                button = ttk.Button(
                    self.button_frame,
                    text=text,
                    command=command,
                    style="Primary.TButton"  # Assuming a primary style is defined
                )
            else:
                button = ttk.Button(self.button_frame, text=text, command=command)
            
            button.grid(row=0, column=col, padx=5, pady=5)
    
    def _create_menu(self):
        """Create the application menu bar."""
        menu_bar = tk.Menu(self.window)
        self.window.config(menu=menu_bar)
        
        # File menu
        file_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New", command=self._on_new)
        file_menu.add_command(label="Open", command=self._on_load)
        file_menu.add_command(label="Save", command=self._on_save)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self._on_exit)
        
        # Edit menu
        edit_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Clear All", command=self._on_clear)
        
        # Tools menu
        tools_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Calculate", command=self._on_calculate)
        tools_menu.add_command(label="Export Report", command=self._on_export_report)
        
        # Help menu
        help_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Documentation", command=self._show_documentation)
        help_menu.add_command(label="About", command=self._show_about)
    
    def _create_status_bar(self):
        """Create the status bar at the bottom of the window."""
        self.status_var = tk.StringVar()
        self.status_bar = ttk.Label(
            self.window, 
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor="w",
            padding=(5, 2)
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def _set_status(self, message):
        """Set the status bar message with timestamp."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.status_var.set(f"{timestamp} | {message}")
    
    # Button command handlers
    
    def _on_calculate(self):
        """Handle calculate button action with proper validation and error handling."""
        self._set_status("Calculating recommendations...")
        
        try:
            # Gather and validate chemical readings
            readings = {}
            for field_name, entry in self.chemical_entries.items():
                value = entry.get().strip()
                if not value:
                    messagebox.showwarning(
                        "Missing Data", 
                        f"Please enter a value for {field_name}."
                    )
                    self._set_status("Calculation canceled - missing data.")
                    return
                
                try:
                    readings[field_name] = float(value)
                except ValueError:
                    messagebox.showwarning(
                        "Invalid Data",
                        f"The value for {field_name} must be a number."
                    )
                    self._set_status("Calculation canceled - invalid data.")
                    return
            
            # Get pool volume
            try:
                volume_text = self.volume_label.cget("text")
                volume = float(volume_text.split(":")[1].strip().split(" ")[0])
            except (IndexError, ValueError):
                messagebox.showwarning(
                    "Missing Data",
                    "Please calculate the pool volume first."
                )
                self._set_status("Calculation canceled - missing volume.")
                return
            
            # Get recommendations from controller
            results = self.controller.calculate_recommendations(readings, volume)
            
            # Display results
            self._display_results(results)
            self._set_status("Calculation completed successfully.")
            
        except Exception as e:
            logger.error(f"Error during calculation: {e}", exc_info=True)
            messagebox.showerror(
                "Calculation Error",
                f"An error occurred during calculation: {str(e)}"
            )
            self._set_status("Calculation error.")
    
    def _display_results(self, results):
        """Display formatted calculation results in the result area."""
        if not results:
            messagebox.showinfo("No Results", "No recommendations are available.")
            return
        
        self.result_text.config(state="normal")
        self.result_text.delete(1.0, tk.END)
        
        # Add header
        self.result_text.insert(tk.END, "Pool Chemistry Recommendations\n\n", "header")
        
        # Add each chemical result
        for chemical, info in results.items():
            status = info.get("status", "normal")
            current = info.get("current", "N/A")
            ideal_range = info.get("ideal_range", ("N/A", "N/A"))
            recommendation = info.get("recommendation", "No action needed")
            dosage = info.get("dosage", "N/A")
            
            # Format the chemical section
            self.result_text.insert(tk.END, f"{chemical}:\n", "header")
            self.result_text.insert(tk.END, f"  Current level: {current}\n", status)
            self.result_text.insert(tk.END, f"  Ideal range: {ideal_range[0]} - {ideal_range[1]}\n", "normal")
            self.result_text.insert(tk.END, f"  Recommendation: {recommendation}\n", status)
            
            if dosage != "N/A":
                self.result_text.insert(tk.END, f"  Dosage: {dosage}\n", "normal")
            
            self.result_text.insert(tk.END, "\n", "normal")
        
        # Add footer with date/time
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.result_text.insert(tk.END, f"\nGenerated on: {timestamp}", "normal")
        
        self.result_text.config(state="disabled")
    
    def _on_clear(self):
        """Clear all input fields and results."""
        # Clear customer entries
        for entry in self.customer_entries.values():
            entry.delete(0, tk.END)
        
        # Clear pool entries
        for field, entry in self.pool_entries.items():
            if field != "type":  # Skip combo box
                entry.delete(0, tk.END)
        
        # Clear chemical entries
        for entry in self.chemical_entries.values():
            entry.delete(0, tk.END)
        
        # Clear volume and results
        self.volume_label.config(text="Volume: N/A")
        self.clear_results()
        
        self._set_status("All fields cleared.")
    
    def _on_save(self):
        """Save the current pool data to a file."""
        try:
            # Collect data
            data = {
                "customer": {field: entry.get() for field, entry in self.customer_entries.items()},
                "pool": {field: entry.get() for field, entry in self.pool_entries.items()},
                "chemicals": {field: entry.get() for field, entry in self.chemical_entries.items()},
                "volume": self.volume_label.cget("text"),
                "timestamp": datetime.now().isoformat()
            }
            
            # Ask for file location
            file_path = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")],
                title="Save Pool Data"
            )
            
            if not file_path:  # User canceled
                return
            
            # Save to file
            with open(file_path, 'w') as f:
                import json
                json.dump(data, f, indent=4)
            
            self._set_status(f"Data saved to {file_path}")
            
        except Exception as e:
            logger.error(f"Error saving data: {e}", exc_info=True)
            messagebox.showerror(
                "Save Error",
                f"Could not save the data: {str(e)}"
            )
    
    def _on_load(self):
        """Load pool data from a file."""
        try:
            # Ask for file location
            file_path = filedialog.askopenfilename(
                defaultextension=".json",
                filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")],
                title="Load Pool Data"
            )
            
            if not file_path:  # User canceled
                return
            
            # Load from file
            with open(file_path, 'r') as f:
                import json
                data = json.load(f)
            
            # Fill customer entries
            for field, value in data.get("customer", {}).items():
                if field in self.customer_entries:
                    self.customer_entries[field].delete(0, tk.END)
                    self.customer_entries[field].insert(0, value)
            
            # Fill pool entries
            for field, value in data.get("pool", {}).items():
                if field in self.pool_entries:
                    self.pool_entries[field].delete(0, tk.END)
                    self.pool_entries[field].insert(0, value)
            
            # Fill chemical entries
            for field, value in data.get("chemicals", {}).items():
                if field in self.chemical_entries:
                    self.chemical_entries[field].delete(0, tk.END)
                    self.chemical_entries[field].insert(0, value)
            
            # Set volume label
            if "volume" in data:
                self.volume_label.config(text=data["volume"])
            
            self._set_status(f"Data loaded from {file_path}")
            
        except Exception as e:
            logger.error(f"Error loading data: {e}", exc_info=True)
            messagebox.showerror(
                "Load Error",
                f"Could not load the data: {str(e)}"
            )
    
    def _on_new(self):
        """Start a new pool chemistry calculation."""
        if messagebox.askyesno(
            "Confirm",
            "Are you sure you want to start a new calculation? Any unsaved data will be lost."
        ):
            self._on_clear()
    
    def _on_exit(self):
        """Exit the application with confirmation."""
        if messagebox.askyesno(
            "Confirm Exit",
            "Are you sure you want to exit the application? Any unsaved data will be lost."
        ):
            self.window.destroy()
    
    def _on_export_report(self):
        """Export the current results as a formatted report."""
        # Implementation would go here
        messagebox.showinfo(
            "Export Report",
            "Report export functionality is not yet implemented."
        )
    
    def _show_documentation(self):
        """Show application documentation."""
        messagebox.showinfo(
            "Documentation",
            "Please refer to the user manual for detailed instructions."
        )
    
    def _show_about(self):
        """Show information about the application."""
        messagebox.showinfo(
            "About Pool Chemistry Calculator",
            "Pool Chemistry Calculator\nVersion 2.0.0\n©2025 Virtual Control LLC"
        )
    
    def run(self):
        """Start the main event loop."""
        self.window.mainloop()


# If this module is run directly, create and run the GUI
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    app = PoolChemistryGUI()
    app.run()
