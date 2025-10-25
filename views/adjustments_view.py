import tkinter as tk
from tkinter import ttk, messagebox
import datetime
import csv
import os

class AdjustmentsView(tk.Frame):
    """
    A class representing the Pool Chemical Adjustments panel in the PoolApp application.
    This class is responsible for handling the UI and interactions related to pool chemical adjustments.
    """
    
    # Define the ideal ranges for pool chemicals
    IDEAL_RANGES = {
        "ph": (7.4, 7.6),
        "alkalinity": (80, 120),  # ppm
        "chlorine": (1.0, 3.0),   # ppm
        "calcium": (200, 400),    # ppm
        "cyanuric_acid": (30, 50) # ppm
    }
    
    def __init__(self, parent, controller, *args, **kwargs):
        """
        Initialize the AdjustmentsView frame.
        
        Args:
            parent: The parent widget
            controller: The controller that manages this view
            *args, **kwargs: Additional arguments to pass to the parent class constructor
        """
        super().__init__(parent, *args, **kwargs)
        self.controller = controller
        
        # Store the current chemical readings
        self.current_readings = {
            "ph": tk.StringVar(),
            "alkalinity": tk.StringVar(),
            "chlorine": tk.StringVar(),
            "calcium": tk.StringVar(),
            "cyanuric_acid": tk.StringVar()
        }
        
        # Store the adjustment values
        self.adjustments = {
            "ph": tk.StringVar(),
            "alkalinity": tk.StringVar(),
            "chlorine": tk.StringVar(),
            "calcium": tk.StringVar(),
            "cyanuric_acid": tk.StringVar()
        }
        
        # Store history data
        self.history_data = []
        
        # Set up the UI
        self.setup_ui()
        
        # Load history data if available
        self.load_history_data()

    def setup_ui(self):
        """Set up the user interface components for the adjustments frame."""
        # Configure the grid layout
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Create a notebook with tabs
        self.notebook = ttk.Notebook(self)
        self.notebook.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        # Create the readings tab
        self.readings_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.readings_frame, text="Current Readings")
        
        # Create the adjustments tab
        self.adjustments_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.adjustments_frame, text="Adjustments")
        
        # Create the history tab
        self.history_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.history_frame, text="History")
        
        # Set up the content for each tab
        self.setup_readings_tab()
        self.setup_adjustments_tab()
        self.setup_history_tab()

    def setup_readings_tab(self):
        """Set up the current readings tab with input fields for chemical levels."""
        # Title label
        title_label = ttk.Label(self.readings_frame, text="Current Chemical Readings", font=("Arial", 14, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(10, 20))
        
        # Create input fields for each chemical parameter
        row = 1
        for idx, (param, (min_val, max_val)) in enumerate(self.IDEAL_RANGES.items()):
            # Create a label with the parameter name
            param_label = ttk.Label(self.readings_frame, text=f"{param.replace('_', ' ').title()}:")
            param_label.grid(row=row, column=0, sticky="w", padx=10, pady=5)
            
            # Create an entry field for the current reading
            entry = ttk.Entry(self.readings_frame, textvariable=self.current_readings[param], width=10)
            entry.grid(row=row, column=1, padx=5, pady=5)
            
            # Create a label showing the ideal range
            range_label = ttk.Label(self.readings_frame, text=f"Ideal Range: {min_val}-{max_val}")
            range_label.grid(row=row, column=2, sticky="w", padx=10, pady=5)
            
            row += 1
        
        # Add a button to save the current readings
        save_button = ttk.Button(self.readings_frame, text="Save Readings", command=self.save_readings)
        save_button.grid(row=row, column=0, columnspan=3, pady=20)

    def setup_adjustments_tab(self):
        """Set up the adjustments tab with input fields for chemical adjustments."""
        # Title label
        title_label = ttk.Label(self.adjustments_frame, text="Chemical Adjustments", font=("Arial", 14, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(10, 20))
        
        # Create input fields for each chemical parameter adjustment
        row = 1
        for idx, param in enumerate(self.IDEAL_RANGES.keys()):
            # Create a label with the parameter name
            param_label = ttk.Label(self.adjustments_frame, text=f"{param.replace('_', ' ').title()} Adjustment:")
            param_label.grid(row=row, column=0, sticky="w", padx=10, pady=5)
            
            # Create an entry field for the adjustment value
            entry = ttk.Entry(self.adjustments_frame, textvariable=self.adjustments[param], width=10)
            entry.grid(row=row, column=1, padx=5, pady=5)
            
            # Add a button to calculate recommended adjustment
            calc_button = ttk.Button(
                self.adjustments_frame, 
                text="Calculate", 
                command=lambda p=param: self.calculate_adjustment(p)
            )
            calc_button.grid(row=row, column=2, padx=10, pady=5)
            
            row += 1
        
        # Add a button to save the adjustments
        save_button = ttk.Button(self.adjustments_frame, text="Save Adjustments", command=self.save_adjustments)
        save_button.grid(row=row, column=0, columnspan=3, pady=20)

    def setup_history_tab(self):
        """Set up the history tab with a table showing previous readings and adjustments."""
        # Title label
        title_label = ttk.Label(self.history_frame, text="History of Readings and Adjustments", font=("Arial", 14, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(10, 20))
        
        # Create a treeview for displaying history data
        columns = ("date", "ph", "alkalinity", "chlorine", "calcium", "cyanuric_acid")
        self.history_tree = ttk.Treeview(self.history_frame, columns=columns, show="headings")
        
        # Define column headings
        self.history_tree.heading("date", text="Date")
        self.history_tree.heading("ph", text="pH")
        self.history_tree.heading("alkalinity", text="Alkalinity")
        self.history_tree.heading("chlorine", text="Chlorine")
        self.history_tree.heading("calcium", text="Calcium")
        self.history_tree.heading("cyanuric_acid", text="Cyanuric Acid")
        
        # Define column widths
        self.history_tree.column("date", width=150)
        self.history_tree.column("ph", width=80)
        self.history_tree.column("alkalinity", width=80)
        self.history_tree.column("chlorine", width=80)
        self.history_tree.column("calcium", width=80)
        self.history_tree.column("cyanuric_acid", width=100)
        
        # Add a scrollbar
        scrollbar = ttk.Scrollbar(self.history_frame, orient="vertical", command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=scrollbar.set)
        
        # Place the treeview and scrollbar in the grid
        self.history_tree.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        scrollbar.grid(row=1, column=1, sticky="ns", pady=5)
        
        # Make the treeview expandable
        self.history_frame.grid_rowconfigure(1, weight=1)
        self.history_frame.grid_columnconfigure(0, weight=1)
        
        # Add export button
        export_button = ttk.Button(self.history_frame, text="Export History", command=self.export_history)
        export_button.grid(row=2, column=0, pady=10)

    def save_readings(self):
        """Save the current chemical readings."""
        # Validate all inputs
        if not self.validate_inputs(self.current_readings):
            return
        
        # Get current date and time
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Create a new entry for history
        new_entry = {
            "date": timestamp,
            "type": "reading"
        }
        
        # Add all the chemical readings
        for param in self.IDEAL_RANGES.keys():
            try:
                new_entry[param] = float(self.current_readings[param].get())
            except ValueError:
                new_entry[param] = 0.0
        
        # Add to history data
        self.history_data.append(new_entry)
        
        # Save to file
        self.save_history_data()
        
        # Update the history view
        self.update_history_view()
        
        # Show confirmation
        messagebox.showinfo("Success", "Chemical readings saved successfully!")

    def save_adjustments(self):
        """Save the chemical adjustments."""
        # Validate all inputs
        if not self.validate_inputs(self.adjustments):
            return
        
        # Get current date and time
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Create a new entry for history
        new_entry = {
            "date": timestamp,
            "type": "adjustment"
        }
        
        # Add all the chemical adjustments
        for param in self.IDEAL_RANGES.keys():
            try:
                new_entry[param] = float(self.adjustments[param].get())
            except ValueError:
                new_entry[param] = 0.0
        
        # Add to history data
        self.history_data.append(new_entry)
        
        # Save to file
        self.save_history_data()
        
        # Update the history view
        self.update_history_view()
        
        # Show confirmation
        messagebox.showinfo("Success", "Chemical adjustments saved successfully!")

    def calculate_adjustment(self, parameter):
        """
        Calculate the recommended adjustment for a specific chemical parameter.
        
        Args:
            parameter (str): The chemical parameter to calculate adjustment for
        """
        try:
            # Get the current reading
            current = float(self.current_readings[parameter].get())
            
            # Get the ideal range
            min_ideal, max_ideal = self.IDEAL_RANGES[parameter]
            
            # Calculate adjustment needed
            if current < min_ideal:
                adjustment = min_ideal - current
            elif current > max_ideal:
                adjustment = max_ideal - current
            else:
                adjustment = 0.0
            
            # Set the adjustment value
            self.adjustments[parameter].set(f"{adjustment:.2f}")
            
        except ValueError:
            messagebox.showerror("Error", f"Please enter a valid number for the current {parameter} reading.")

    def validate_inputs(self, input_vars):
        """
        Validate that all input fields contain valid numerical values.
        
        Args:
            input_vars (Dict[str, tk.StringVar]): Dictionary of input variables to validate
            
        Returns:
            bool: True if all inputs are valid, False otherwise
        """
        for param, var in input_vars.items():
            value = var.get()
            if not value.strip():  # Allow empty fields
                continue
                
            try:
                float_value = float(value)
                
                # Check for negative values
                if float_value < 0:
                    messagebox.showerror("Invalid Input", f"{param.replace('_', ' ').title()} cannot be negative.")
                    return False
                    
            except ValueError:
                messagebox.showerror("Invalid Input", f"{param.replace('_', ' ').title()} must be a number.")
                return False
                
        return True

    def update_history_view(self):
        """Update the history treeview with the current history data."""
        # Clear the treeview
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        
        # Add each history entry to the treeview
        for entry in self.history_data:
            values = [
                entry["date"],
                f"{entry.get('ph', '')}",
                f"{entry.get('alkalinity', '')}",
                f"{entry.get('chlorine', '')}",
                f"{entry.get('calcium', '')}",
                f"{entry.get('cyanuric_acid', '')}"
            ]
            self.history_tree.insert("", "end", values=values)

    def save_history_data(self):
        """Save the history data to a CSV file."""
        try:
            # Create the data directory if it doesn't exist
            os.makedirs("data", exist_ok=True)
            
            # Open the file for writing
            with open("data/chemical_history.csv", "w", newline="") as csvfile:
                # Create a CSV writer
                writer = csv.writer(csvfile)
                
                # Write the header
                writer.writerow(["date", "type", "ph", "alkalinity", "chlorine", "calcium", "cyanuric_acid"])
                
                # Write each entry
                for entry in self.history_data:
                    writer.writerow([
                        entry.get("date", ""),
                        entry.get("type", ""),
                        entry.get("ph", ""),
                        entry.get("alkalinity", ""),
                        entry.get("chlorine", ""),
                        entry.get("calcium", ""),
                        entry.get("cyanuric_acid", "")
                    ])
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save history data: {str(e)}")

    def load_history_data(self):
        """Load the history data from a CSV file."""
        try:
            # Check if the file exists
            if not os.path.exists("data/chemical_history.csv"):
                return
            
            # Open the file for reading
            with open("data/chemical_history.csv", "r", newline="") as csvfile:
                # Create a CSV reader
                reader = csv.reader(csvfile)
                
                # Read the header
                header = next(reader, None)
                if not header:
                    return
                
                # Read each entry
                self.history_data = []
                for row in reader:
                    if len(row) < 7:
                        continue
                    
                    entry = {
                        "date": row[0],
                        "type": row[1]
                    }
                    
                    # Add the chemical values
                    for i, param in enumerate(["ph", "alkalinity", "chlorine", "calcium", "cyanuric_acid"]):
                        try:
                            if row[i+2]:  # Skip empty values
                                entry[param] = float(row[i+2])
                        except (ValueError, IndexError):
                            pass
                    
                    self.history_data.append(entry)
                
                # Update the history view
                self.update_history_view()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load history data: {str(e)}")

    def export_history(self):
        """Export the history data to a CSV file chosen by the user."""
        try:
            from tkinter import filedialog
            
            # Ask the user for a file location
            filepath = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                title="Export History Data"
            )
            
            if not filepath:
                return  # User cancelled
            
            # Open the file for writing
            with open(filepath, "w", newline="") as csvfile:
                # Create a CSV writer
                writer = csv.writer(csvfile)
                
                # Write the header
                writer.writerow(["date", "type", "ph", "alkalinity", "chlorine", "calcium", "cyanuric_acid"])
                
                # Write each entry
                for entry in self.history_data:
                    writer.writerow([
                        entry.get("date", ""),
                        entry.get("type", ""),
                        entry.get("ph", ""),
                        entry.get("alkalinity", ""),
                        entry.get("chlorine", ""),
                        entry.get("calcium", ""),
                        entry.get("cyanuric_acid", "")
                    ])
                
            messagebox.showinfo("Success", f"History data exported successfully to {filepath}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export history data: {str(e)}")
