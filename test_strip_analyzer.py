# test_strip_analyzer.py
"""
Module for analyzing pool test strips from images.
"""
import cv2
import numpy as np
from PIL import Image
import logging
from typing import Dict, Optional, Tuple
from models.water_tester import WaterTester

class TestStripAnalyzer:
    """
    Analyzes images of pool test strips to extract chemical readings.
    """
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.reference_colors = {
            'ph': {
                6.8: (230, 190, 120),  # RGB values for pH 6.8
                7.2: (180, 180, 90),   # RGB values for pH 7.2
                7.6: (150, 170, 70),   # RGB values for pH 7.6
                8.0: (120, 160, 50),   # RGB values for pH 8.0
                8.4: (90, 150, 30)     # RGB values for pH 8.4
            },
            'chlorine': {
                0: (255, 255, 255),    # RGB values for 0 ppm
                1: (220, 230, 180),    # RGB values for 1 ppm
                3: (170, 210, 120),    # RGB values for 3 ppm
                5: (120, 190, 80),     # RGB values for 5 ppm
                10: (70, 170, 40)      # RGB values for 10 ppm
            },
            'alkalinity': {
                0: (255, 255, 255),     # RGB values for 0 ppm
                40: (230, 190, 180),    # RGB values for 40 ppm
                120: (200, 140, 140),   # RGB values for 120 ppm
                180: (170, 100, 100),   # RGB values for 180 ppm
                240: (140, 60, 60)      # RGB values for 240 ppm
            }
        }

    def analyze_image(self, image_path: str) -> Dict[str, float]:
        """
        Analyze test strip image and return chemical readings.
        
        Args:
            image_path: Path to the test strip image
            
        Returns:
            Dictionary containing chemical readings (pH, chlorine, alkalinity)
        """
        try:
            # Open and preprocess the image
            image = cv2.imread(image_path)
            if image is None:
                self.logger.error(f"Failed to load image from {image_path}")
                return {}
                
            # Convert to RGB (OpenCV loads as BGR)
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Define regions of interest for each chemical
            # These would need to be calibrated for specific test strip brands
            ph_roi = self._extract_roi(image_rgb, 'ph')
            chlorine_roi = self._extract_roi(image_rgb, 'chlorine')
            alkalinity_roi = self._extract_roi(image_rgb, 'alkalinity')
            
            # Analyze colors and determine chemical levels
            ph_level = self._analyze_color(ph_roi, 'ph')
            chlorine_level = self._analyze_color(chlorine_roi, 'chlorine')
            alkalinity_level = self._analyze_color(alkalinity_roi, 'alkalinity')
            
            return {
                'ph': ph_level,
                'chlorine': chlorine_level,
                'alkalinity': alkalinity_level
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing test strip image: {str(e)}")
            return {}
            
    def _extract_roi(self, image: np.ndarray, chemical: str) -> np.ndarray:
        """
        Extract region of interest for a specific chemical from the image.
        This is a placeholder implementation and would need to be customized
        based on the specific test strip layout.
        
        Args:
            image: The input image
            chemical: The chemical to extract ROI for
            
        Returns:
            Region of interest for the specified chemical
        """
        height, width, _ = image.shape
        
        # Placeholder ROI definitions - would need to be calibrated
        roi_mappings = {
            'ph': (0, int(width/3), int(height*0.4), int(height*0.6)),
            'chlorine': (int(width/3), int(2*width/3), int(height*0.4), int(height*0.6)),
            'alkalinity': (int(2*width/3), width, int(height*0.4), int(height*0.6))
        }
        
        x1, x2, y1, y2 = roi_mappings.get(chemical, (0, width, 0, height))
        return image[y1:y2, x1:x2]
        
    def _analyze_color(self, roi: np.ndarray, chemical: str) -> float:
        """
        Analyze the color of a region of interest to determine chemical level.
        
        Args:
            roi: Region of interest
            chemical: Chemical type
            
        Returns:
            Estimated chemical level
        """
        # Calculate average color in ROI
        avg_color = np.mean(roi, axis=(0, 1))
        
        # Find closest match in reference colors
        closest_level = None
        min_distance = float('inf')
        
        for level, color in self.reference_colors.get(chemical, {}).items():
            distance = np.linalg.norm(np.array(color) - avg_color)
            if distance < min_distance:
                min_distance = distance
                closest_level = level
                
        return closest_level if closest_level is not None else 0.0

    def calibrate(self, calibration_images: Dict[str, Dict[float, str]]) -> bool:
        """
        Calibrate the analyzer using known reference images.
        
        Args:
            calibration_images: Dictionary mapping chemical to level and image path
            Example: {'ph': {7.2: 'path/to/ph7.2.jpg', 7.6: 'path/to/ph7.6.jpg'}}
            
        Returns:
            True if calibration was successful, False otherwise
        """
        try:
            for chemical, level_images in calibration_images.items():
                if chemical not in self.reference_colors:
                    self.reference_colors[chemical] = {}
                    
                for level, image_path in level_images.items():
                    image = cv2.imread(image_path)
                    if image is None:
                        self.logger.error(f"Failed to load calibration image {image_path}")
                        continue
                        
                    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                    roi = self._extract_roi(image_rgb, chemical)
                    avg_color = np.mean(roi, axis=(0, 1))
                    
                    self.reference_colors[chemical][level] = tuple(avg_color)
                    
            return True
            
        except Exception as e:
            self.logger.error(f"Error during calibration: {str(e)}")
            return False
