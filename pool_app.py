import tkinter as tk
from tkinter import ttk, messagebox
import logging
from controllers.pool_controller import PoolController
from exceptions import DataValidationError

class PoolApp:
    """Main application class for the pool chemistry calculator."""

    def __init__(self):
        """Initialize the application."""
        self.controller = PoolController()
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

    def calculate_chemicals(self):
        """Validate inputs and calculate chemical recommendations."""
        try:
            # Get and validate inputs
            customer_name = self.customer_name_entry.get()
            pool_type = self.pool_type_entry.get()

            # Validate numeric inputs
            try:
                pool_size = float(self.pool_size_entry.get())
                pH = float(self.pH_entry.get())
                chlorine = float(self.chlorine_entry.get())
                bromine = float(self.bromine_entry.get())
                alkalinity = float(self.alkalinity_entry.get())
                cyanuric_acid = float(self.cyanuric_acid_entry.get())
                calcium_hardness = float(self.calcium_hardness_entry.get())
                stabilizer = float(self.stabilizer_entry.get())
                salt = float(self.salt_entry.get())
            except ValueError:
                self.show_error_message("All chemical readings must be numeric values")
                return

            # Calculate chemical metrics
            chemical_metrics = self.controller.calculate_chemical_metrics(
                pool_type, pool_size, pH, chlorine, bromine, alkalinity,
                cyanuric_acid, calcium_hardness, stabilizer, salt
            )

            # Display results
            self.display_results(chemical_metrics)

        except DataValidationError as e:
            self.show_error_message(str(e))
        except Exception as e:
            logging.error(f"Error in chemical calculation: {e}", exc_info=True)
            self.show_error_message(f"An unexpected error occurred: {e}")

    def show_error_message(self, message: str):
        """Display an error message to the user."""
        messagebox.showerror("Error", message)

    def display_results(self, metrics: dict):
        """Display the chemical metrics and recommendations."""
        self.result_text.delete(1.0, tk.END)  # Clear previous text
        self.result_text.insert(tk.END, "Chemical Metrics and Recommendations: \n\n")
        
        # Insert each metric and recommendation into the text area
        for key, value in metrics['metrics'].items():
            self.result_text.insert(tk.END, f"{key.capitalize()}: {value}\n")
        
        self.result_text.insert(tk.END, "\nRecommendations: \n")
        
        for key, recommendation in metrics['recommendations'].items():
            self.result_text.insert(tk.END, f"{key.capitalize()}: {recommendation}\n")

    def run(self):
        """Run the application loop."""
        self.window.mainloop()

# Entrypoint to run the application
if __name__ == "__main__":
    app = PoolApp()
    app.run()

print("Completed pool_app.py:")
print(pool_app.py)
