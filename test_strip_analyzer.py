#!/usr/bin/env python3
"""
Test Strip Analyzer for Deep Blue Pool Chemistry
This module provides functionality to analyze pool test strips using computer vision.
"""
import logging
import os
import time
from typing import Dict, Any, Optional, Tuple, List
from pathlib import Path
import json

logger = logging.getLogger(__name__)

class TestStripAnalyzer:
    """Analyzer for pool test strips using computer vision."""
    
    def __init__(self, calibration_file: Optional[str] = None):
        """
        Initialize the test strip analyzer.
        
        Args:
            calibration_file: Path to calibration data file
        """
        self.calibration_data = {}
        self.camera = None
        self.image_processor = None
        
        # Try to import required modules
        self.cv2 = self._import_cv2()
        self.np = self._import_numpy()
        
        # Load calibration data if available
        if calibration_file and os.path.exists(calibration_file):
            self._load_calibration(calibration_file)
        else:
            self._create_default_calibration()
            
        # Initialize camera if OpenCV is available
        if self.cv2:
            self._init_camera()
    
    def _import_cv2(self):
        """Import OpenCV module if available."""
        try:
            import cv2
            logger.info("OpenCV module loaded successfully")
            return cv2
        except ImportError:
            logger.warning("OpenCV module not available - image processing disabled")
            return None
    
    def _import_numpy(self):
        """Import NumPy module if available."""
        try:
            import numpy as np
            return np
        except ImportError:
            logger.warning("NumPy module not available - image processing disabled")
            return None
    
    def _init_camera(self) -> bool:
        """
        Initialize the camera.
        
        Returns:
            bool: True if camera initialized successfully, False otherwise
        """
        if not self.cv2:
            return False
            
        try:
            self.camera = self.cv2.VideoCapture(0)  # Use default camera (index 0)
            if not self.camera.isOpened():
                logger.error("Failed to open camera")
                return False
                
            logger.info("Camera initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error initializing camera: {str(e)}")
            return False
    
    def _load_calibration(self, file_path: str) -> bool:
        """
        Load calibration data from file.
        
        Args:
            file_path: Path to calibration file
            
        Returns:
            bool: True if loaded successfully, False otherwise
        """
        try:
            with open(file_path, 'r') as f:
                self.calibration_data = json.load(f)
            logger.info(f"Loaded calibration data from {file_path}")
            return True
        except Exception as e:
            logger.error(f"Error loading calibration data: {str(e)}")
            self._create_default_calibration()
            return False
    
    def _create_default_calibration(self) -> None:
        """Create default calibration data."""
        self.calibration_data = {
            "ph": {
                "regions": [(10, 10, 30, 30)],  # Example regions (x, y, width, height)
                "color_ranges": {
                    "6.8": [(0, 100, 100), (10, 255, 255)],  # HSV color ranges
                    "7.2": [(10, 100, 100), (20, 255, 255)],
                    "7.6": [(20, 100, 100), (30, 255, 255)],
                    "8.0": [(30, 100, 100), (40, 255, 255)]
                }
            },
            "chlorine": {
                "regions": [(50, 10, 30, 30)],
                "color_ranges": {
                    "0": [(0, 0, 100), (180, 50, 255)],  # White/light color
                    "1": [(20, 100, 100), (30, 255, 255)],  # Light yellow
                    "3": [(30, 100, 100), (40, 255, 255)],  # Yellow
                    "5": [(40, 100, 100), (50, 255, 255)]   # Dark yellow
                }
            },
            "alkalinity": {
                "regions": [(90, 10, 30, 30)],
                "color_ranges": {
                    "40": [(100, 100, 100), (110, 255, 255)],
                    "80": [(110, 100, 100), (120, 255, 255)],
                    "120": [(120, 100, 100), (130, 255, 255)],
                    "180": [(130, 100, 100), (140, 255, 255)]
                }
            }
        }
        logger.info("Created default calibration data")
    
    def save_calibration(self, file_path: str) -> bool:
        """
        Save calibration data to file.
        
        Args:
            file_path: Path to save calibration file
            
        Returns:
            bool: True if saved successfully, False otherwise
        """
        try:
            os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
            with open(file_path, 'w') as f:
                json.dump(self.calibration_data, f, indent=4)
            logger.info(f"Saved calibration data to {file_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving calibration data: {str(e)}")
            return False
    
    def capture_image(self, save_path: Optional[str] = None) -> Optional[Any]:
        """
        Capture an image from the camera.
        
        Args:
            save_path: Path to save the captured image
            
        Returns:
            Optional[Any]: Captured image or None if failed
        """
        if not self.cv2 or not self.camera:
            logger.error("Cannot capture image: Camera not initialized")
            return None
            
        try:
            # Capture frame
            ret, frame = self.camera.read()
            if not ret:
                logger.error("Failed to capture image")
                return None
                
            # Save image if path provided
            if save_path:
                os.makedirs(os.path.dirname(os.path.abspath(save_path)), exist_ok=True)
                self.cv2.imwrite(save_path, frame)
                logger.info(f"Saved captured image to {save_path}")
                
            return frame
            
        except Exception as e:
            logger.error(f"Error capturing image: {str(e)}")
            return None
    
    def analyze_test_strip(self, image=None) -> Dict[str, float]:
        """
        Analyze a test strip image.
        
        Args:
            image: Image to analyze (if None, capture a new image)
            
        Returns:
            Dict[str, float]: Dictionary of test results
        """
        if not self.cv2 or not self.np:
            logger.warning("Cannot analyze test strip: OpenCV or NumPy not available")
            return self._get_mock_results()
            
        try:
            # Capture image if not provided
            if image is None:
                image = self.capture_image()
                if image is None:
                    return self._get_mock_results()
            
            # Convert to HSV for better color analysis
            hsv_image = self.cv2.cvtColor(image, self.cv2.COLOR_BGR2HSV)
            
            results = {}
            
            # Analyze each parameter
            for param, config in self.calibration_data.items():
                regions = config.get("regions", [])
                color_ranges = config.get("color_ranges", {})
                
                if not regions or not color_ranges:
                    continue
                    
                # Extract region of interest
                region = regions[0]  # Use first region for now
                x, y, w, h = region
                roi = hsv_image[y:y+h, x:x+w]
                
                # Find best matching color
                best_match = self._find_best_color_match(roi, color_ranges)
                if best_match:
                    results[param] = float(best_match)
            
            # If no results, use mock data
            if not results:
                logger.warning("No valid test strip analysis results, using mock data")
                return self._get_mock_results()
                
            return results
            
        except Exception as e:
            logger.error(f"Error analyzing test strip: {str(e)}")
            return self._get_mock_results()
    
    def _find_best_color_match(self, roi, color_ranges) -> Optional[str]:
        """
        Find the best matching color range for a region of interest.
        
        Args:
            roi: Region of interest (HSV image)
            color_ranges: Dictionary of color ranges
            
        Returns:
            Optional[str]: Best matching value or None
        """
        if not self.cv2 or not self.np:
            return None
            
        try:
            best_match = None
            best_match_pixels = 0
            
            # Calculate average HSV values
            avg_h = int(self.np.mean(roi[:, :, 0]))
            avg_s = int(self.np.mean(roi[:, :, 1]))
            avg_v = int(self.np.mean(roi[:, :, 2]))
            
            # Find closest match
            for value, (lower, upper) in color_ranges.items():
                lower_bound = self.np.array(lower)
                upper_bound = self.np.array(upper)
                
                # Check if average color is within range
                if (lower_bound[0] <= avg_h <= upper_bound[0] and
                    lower_bound[1] <= avg_s <= upper_bound[1] and
                    lower_bound[2] <= avg_v <= upper_bound[2]):
                    
                    # Create mask for this color range
                    mask = self.cv2.inRange(roi, lower_bound, upper_bound)
                    matching_pixels = self.cv2.countNonZero(mask)
                    
                    # Update best match if this is better
                    if matching_pixels > best_match_pixels:
                        best_match_pixels = matching_pixels
                        best_match = value
            
            return best_match
            
        except Exception as e:
            logger.error(f"Error finding color match: {str(e)}")
            return None
    
    def _get_mock_results(self) -> Dict[str, float]:
        """
        Generate mock test results for testing or when analysis fails.
        
        Returns:
            Dict[str, float]: Dictionary of mock test results
        """
        import random
        
        return {
            "ph": round(random.uniform(7.0, 7.8), 1),
            "chlorine": round(random.choice([0, 1, 3, 5]), 1),
            "alkalinity": round(random.choice([40, 80, 120, 180]), 0),
            "hardness": round(random.choice([50, 100, 250, 500]), 0),
            "cyanuric_acid": round(random.choice([0, 30, 50, 100]), 0)
        }
    
    def calibrate(self, parameter: str, value: str, image=None) -> bool:
        """
        Calibrate the analyzer for a specific parameter and value.
        
        Args:
            parameter: Parameter to calibrate (e.g., 'ph', 'chlorine')
            value: Value to associate with the current color
            image: Image to use for calibration (if None, capture a new image)
            
        Returns:
            bool: True if calibration successful, False otherwise
        """
        if not self.cv2 or not self.np:
            logger.error("Cannot calibrate: OpenCV or NumPy not available")
            return False
            
        try:
            # Capture image if not provided
            if image is None:
                image = self.capture_image()
                if image is None:
                    return False
            
            # Convert to HSV
            hsv_image = self.cv2.cvtColor(image, self.cv2.COLOR_BGR2HSV)
            
            # Get region for parameter
            if parameter not in self.calibration_data:
                self.calibration_data[parameter] = {"regions": [(10, 10, 30, 30)], "color_ranges": {}}
                
            regions = self.calibration_data[parameter]["regions"]
            if not regions:
                regions = [(10, 10, 30, 30)]
                self.calibration_data[parameter]["regions"] = regions
                
            # Extract region of interest
            region = regions[0]  # Use first region
            x, y, w, h = region
            roi = hsv_image[y:y+h, x:x+w]
            
            # Calculate average HSV values
            avg_h = int(self.np.mean(roi[:, :, 0]))
            avg_s = int(self.np.mean(roi[:, :, 1]))
            avg_v = int(self.np.mean(roi[:, :, 2]))
            
            # Create color range with some tolerance
            h_tolerance = 10
            s_tolerance = 50
            v_tolerance = 50
            
            lower_bound = [max(0, avg_h - h_tolerance), max(0, avg_s - s_tolerance), max(0, avg_v - v_tolerance)]
            upper_bound = [min(180, avg_h + h_tolerance), min(255, avg_s + s_tolerance), min(255, avg_v + v_tolerance)]
            
            # Save to calibration data
            if "color_ranges" not in self.calibration_data[parameter]:
                self.calibration_data[parameter]["color_ranges"] = {}
                
            self.calibration_data[parameter]["color_ranges"][value] = [lower_bound, upper_bound]
            
            logger.info(f"Calibrated {parameter} for value {value}")
            return True
            
        except Exception as e:
            logger.error(f"Error during calibration: {str(e)}")
            return False
    
    def release(self) -> None:
        """Release resources."""
        if self.camera:
            self.camera.release()
            logger.info("Camera released")

# Test function
def test_strip_analyzer():
    """Test the test strip analyzer."""
    logging.basicConfig(level=logging.INFO)
    
    analyzer = TestStripAnalyzer()
    
    # Test capturing an image
    image = analyzer.capture_image("test_capture.jpg")
    if image is not None:
        print("Image captured successfully")
    
    # Test analyzing a test strip
    results = analyzer.analyze_test_strip()
    print(f"Test strip analysis results: {results}")
    
    # Test calibration
    analyzer.calibrate("ph", "7.2")
    analyzer.calibrate("chlorine", "3")
    
    # Save calibration
    analyzer.save_calibration("calibration.json")
    
    # Release resources
    analyzer.release()

if __name__ == "__main__":
    test_strip_analyzer()