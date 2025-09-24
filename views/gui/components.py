import tkinter as tk
from tkinter import ttk, filedialog
import logging
from exceptions import DataValidationError
import re

logger = logging.getLogger(__name__)

class ValidatedEntry(tk.Frame):
    """Entry field with built-in validation."""
    
    def __init__(self, parent, label_text, validator=None, default_value="", width=10, **kwargs):
        super().__init__(parent, **kwargs)
        self.label = tk.Label(self, text=label_text)
        self.entry = tk.Entry(self, width=width)
        self.validator = validator
        self.error_label = tk.Label(self, text="", fg="red", font=("Arial", 8))
        
        if default_value:
            self.entry.insert(0, default_value)
        
        self.label.pack(side=tk.LEFT)
        self.entry.pack(side=tk.LEFT)
        self.error_label.pack(side=tk.LEFT, padx=(5, 0))
        
    def get(self):
        """Get the entry value, validating if a validator is provided."""
        value = self.entry.get()
        if self.validator:
            try:
                return self.validator(value)
            except DataValidationError as e:
                self.show_error(str(e))
                return None
        return value
    
    def set(self, value):
        """Set the entry value."""
        self.entry.delete(0, tk.END)
        self.entry.insert(0, str(value))
        self.clear_error()
    
    def show_error(self, message):
        """Show an error message."""
        self.error_label.config(text=message)
        
    def clear_error(self):
        """Clear the error message."""
        self.error_label.config(text="")

class NumericEntry(ValidatedEntry):
    """Entry field that only accepts numeric input."""
    
    def __init__(self, parent, label_text, min_value=None, max_value=None, **kwargs):
        def validate_numeric(value):
            try:
                if not value.strip():
                    raise DataValidationError("Required field")
                
                numeric_value = float(value)
                
                if min_value is not None and numeric_value < min_value:
                    raise DataValidationError(f"Min: {min_value}")
                    
                if max_value is not None and numeric_value > max_value:
                    raise DataValidationError(f"Max: {max_value}")
                    
                return numeric_value
            except ValueError:
                raise DataValidationError("Must be numeric")
        
        super().__init__(parent, label_text, validator=validate_numeric, **kwargs)

class LabeledEntry(tk.Frame):
    """Simple labeled entry field without validation."""
    
    def __init__(self, parent, label_text, default_value="", width=10):
        super().__init__(parent)
        self.label = tk.Label(self, text=label_text)
        self.entry = tk.Entry(self, width=width)
        
        if default_value:
            self.entry.insert(0, default_value)
        
        self.label.pack(side=tk.LEFT)
        self.entry.pack(side=tk.LEFT)
        
    def get(self):
        return self.entry.get()
    
    def set(self, value):
        self.entry.delete(0, tk.END)
        self.entry.insert(0, str(value))

class ChemicalDisplay(tk.Frame):
    """Display chemical readings with color coding for ranges."""
    
    def __init__(self, parent, chemical_name, unit="ppm", ideal_range=None):
        super().__init__(parent)
        
        self.name_label = tk.Label(self, text=f"{chemical_name}:")
        self.value_label = tk.Label(self, text="--", width=5)
        self.unit_label = tk.Label(self, text=unit)
        self.ideal_range = ideal_range
        
        self.name_label.grid(row=0, column=0)
        self.value_label.grid(row=0, column=1)
        self.unit_label.grid(row=0, column=2)
        
        if ideal_range:
            self.range_label = tk.Label(self, text=f"Ideal: {ideal_range[0]}-{ideal_range[1]}")
            self.range_label.grid(row=1, column=0, columnspan=3)
    
    def set_value(self, value):
        """Set the value and update display with color coding."""
        if value is None:
            self.value_label.config(text="--")
            return
            
        self.value_label.config(text=str(value))
        
        if self.ideal_range:
            if value < self.ideal_range[0]:
                self.value_label.config(fg="blue")  # Too low
            elif value > self.ideal_range[1]:
                self.value_label.config(fg="red")  # Too high
            else:
                self.value_label.config(fg="green")  # Ideal range
                
    def get_value(self):
        """Get the current value."""
        text = self.value_label.cget("text")
        if text == "--":
            return None
        try:
            return float(text)
        except ValueError:
            return None

class WeatherDisplay(tk.Frame):
    """Display weather data relevant to pool maintenance."""
    
    def __init__(self, parent):
        super().__init__(parent)
        
        # Weather data fields
        self.location_label = tk.Label(self, text="Location: --")
        self.temperature_label = tk.Label(self, text="Temperature: --")
        self.humidity_label = tk.Label(self, text="Humidity: --")
        self.condition_label = tk.Label(self, text="Condition: --")
        self.forecast_label = tk.Label(self, text="Forecast: --")
        
        self.impact_label = tk.Label(self, text="Impact on Pool: --")
        
        # Layout
        self.location_label.pack(anchor="w")
        self.temperature_label.pack(anchor="w")
        self.humidity_label.pack(anchor="w")
        self.condition_label.pack(anchor="w")
        self.forecast_label.pack(anchor="w")
        tk.Label(self, text="").pack()  # Spacer
        self.impact_label.pack(anchor="w")
    
    def update_weather(self, weather_data):
        """Update the display with weather data."""
        self.location_label.config(text=f"Location: {weather_data.get('location', '--')}")
        self.temperature_label.config(text=f"Temperature: {weather_data.get('temperature', '--')}°F")
        self.humidity_label.config(text=f"Humidity: {weather_data.get('humidity', '--')}%")
        self.condition_label.config(text=f"Condition: {weather_data.get('condition', '--')}")
        self.forecast_label.config(text=f"Forecast: {weather_data.get('forecast', '--')}")
        
        # Set impact information
        impact = weather_data.get('pool_impact', '--')
        self.impact_label.config(text=f"Impact on Pool: {impact}")
        
        # Color code based on impact severity
        if "high chlorine depletion" in impact.lower():
            self.impact_label.config(fg="red")
        elif "moderate" in impact.lower():
            self.impact_label.config(fg="orange")
        else:
            self.impact_label.config(fg="black")

class TestStripImageViewer(tk.Frame):
    """Component for uploading and analyzing test strip images."""
    
    def __init__(self, parent, processor=None):
        super().__init__(parent)
        self.processor = processor
        self.image_path = None
        
        # UI Elements
        self.upload_button = tk.Button(self, text="Upload Test Strip Image", command=self.upload_image)
        self.analyze_button = tk.Button(self, text="Analyze Image", command=self.analyze_image, state=tk.DISABLED)
        
        self.image_label = tk.Label(self, text="No image selected")
        self.results_frame = tk.Frame(self)
        
        # Layout
        self.upload_button.pack(pady=(10, 5))
        self.analyze_button.pack(pady=(0, 10))
        self.image_label.pack(pady=10)
        self.results_frame.pack(fill=tk.BOTH, expand=True)
        
        # Results widgets (will be populated after analysis)
        self.result_labels = {}
    
    def upload_image(self):
        """Handle image upload."""
        file_path = filedialog.askopenfilename(
            title="Select Test Strip Image",
            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")]
        )
        
        if file_path:
            self.image_path = file_path
            self.image_label.config(text=f"Selected: {file_path.split('/')[-1]}")
            self.analyze_button.config(state=tk.NORMAL)
            logger.info(f"Test strip image selected: {file_path}")
    
    def analyze_image(self):
        """Analyze the uploaded image."""
        if not self.processor or not self.image_path:
            return
            
        try:
            # Process the image
            results = self.processor.process_image(self.image_path)
            logger.info(f"Test strip analysis results: {results}")
            
            # Clear previous results
            for widget in self.results_frame.winfo_children():
                widget.destroy()
            
            # Display results
            row = 0
            for param, value in results.items():
                label = tk.Label(self.results_frame, text=f"{param}: {value}")
                label.grid(row=row, column=0, sticky="w", pady=2)
                self.result_labels[param] = label
                row += 1
                
        except Exception as e:
            logger.error(f"Error analyzing test strip: {e}", exc_info=True)
            tk.messagebox.showerror("Analysis Error", f"Could not analyze image: {str(e)}")
