# test_strip_image_processor.py - Last updated: June 25, 2025
import cv2
import numpy as np
from datetime import datetime
import os

class TestStripImageProcessor:
    def __init__(self, reference_colors):
        """
        Initialize the test strip image processor with reference colors.
        
        Args:
            reference_colors: Dictionary mapping parameter values to RGB colors
        """
        self.reference_colors = reference_colors
        self.last_processed_image = None
        self.last_processed_date = None

    def process_image(self, image_path):
        """
        Process a test strip image to extract chemical readings.
        
        Args:
            image_path: Path to the image file
        
        Returns:
            Dictionary of parameter readings
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")
            
        # Record processing time
        self.last_processed_date = datetime.now()
        
        # Load image
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError("Failed to load image")
            
        self.last_processed_image = image.copy()
        
        # Process image to identify test strip
        strip_regions = self.detect_strip_regions(image)
        
        readings = {}
        for param, region in strip_regions.items():
            # Extract color from region
            color = self.extract_average_color(region)
            
            # Compare with reference colors to determine value
            value = self.match_color_to_value(param, color)
            readings[param] = value
        
        return readings

    def detect_strip_regions(self, image):
        """
        Detect regions of interest for each parameter on the test strip.
        
        Args:
            image: OpenCV image object
            
        Returns:
            Dictionary mapping parameters to image regions
        """
        # This is a simplified implementation
        # In a real application, this would use computer vision techniques
        # such as edge detection, color segmentation, or template matching
        
        height, width = image.shape[:2]
        
        # Divide the image into equal sections for each parameter
        num_params = 6  # Assuming 6 parameters on the test strip
        section_width = width // num_params
        
        regions = {}
        parameters = ["chlorine", "pH", "alkalinity", "hardness", "cyanuric_acid", "bromine"]
        
        for i, param in enumerate(parameters):
            x_start = i * section_width
            x_end = (i + 1) * section_width
            y_start = height // 3  # Skip the top third of the image
            y_end = 2 * height // 3  # Skip the bottom third of the image
            
            region = image[y_start:y_end, x_start:x_end]
            regions[param] = region
        
        return regions

    def extract_average_color(self, region):
        """
        Calculate average color in the region.
        
        Args:
            region: Image region (numpy array)
            
        Returns:
            Average RGB color as a tuple
        """
        # Convert from BGR to RGB
        rgb_region = cv2.cvtColor(region, cv2.COLOR_BGR2RGB)
        
        # Calculate average color
        avg_color_per_row = np.average(rgb_region, axis=0)
        avg_color = np.average(avg_color_per_row, axis=0)
        
        # Return as integer tuple (R, G, B)
        return tuple(map(int, avg_color))

    def match_color_to_value(self, param, color):
        """
        Compare with reference colors to estimate parameter value.
        
        Args:
            param: Parameter name
            color: RGB color tuple
            
        Returns:
            Estimated parameter value
        """
        # Get reference colors for this parameter
        if param not in self.reference_colors:
            return 0  # Default value if parameter not found
            
        param_refs = self.reference_colors[param]
        
        # Find closest color match
        min_distance = float('inf')
        best_match = None
        
        for value, ref_color in param_refs.items():
            # Calculate color distance (Euclidean)
            distance = np.sqrt(sum((c1 - c2) ** 2 for c1, c2 in zip(color, ref_color)))
            
            if distance < min_distance:
                min_distance = distance
                best_match = value
        
        return best_match
    
    def get_last_processed_info(self):
        """Get information about the last processed image."""
        if self.last_processed_date is None:
            return "No image has been processed"
        
        return {
            "date": self.last_processed_date.isoformat(),
            "image_shape": self.last_processed_image.shape if self.last_processed_image is not None else None
        }
