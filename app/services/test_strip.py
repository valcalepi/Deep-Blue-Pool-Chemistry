
"""
Test strip analyzer module for the Deep Blue Pool Chemistry application.

This module provides functionality for analyzing pool test strips using computer vision
to determine water chemistry parameters and provide recommendations.
"""

import os
import cv2
import json
import logging
import numpy as np
import time
from typing import Dict, List, Optional, Any, Tuple
from PIL import Image
from datetime import datetime

# Configure logger
logger = logging.getLogger(__name__)


class ColorCalibrator:
    """
    Color calibrator for mapping RGB values to chemical readings.
    
    This class handles the calibration data for mapping RGB colors to chemical values.
    
    Attributes:
        calibration_data: Dictionary of calibration data for each chemical
    """
    
    def __init__(self, calibration_file: str = "../data/calibration.json"):
        """
        Initialize the color calibrator.
        
        Args:
            calibration_file: Path to the calibration data JSON file
        """
        self.calibration_data = {}
        self._load_calibration(calibration_file)

    def _load_calibration(self, path: str) -> None:
        """
        Load calibration data from a JSON file.
        
        Args:
            path: Path to the calibration data JSON file
            
        Raises:
            FileNotFoundError: If the calibration file doesn't exist
            json.JSONDecodeError: If the calibration file contains invalid JSON
        """
        try:
            # Try the specified path
            if os.path.exists(path):
                with open(path, 'r') as f:
                    self.calibration_data = json.load(f)
                return
            
            # Try alternative paths
            alt_paths = [
                "data/calibration.json",
                "data/test_strip_calibration.json",
                "data/strip_calibration.json",
                "test_calibration.json"
            ]
            
            for alt_path in alt_paths:
                if os.path.exists(alt_path):
                    with open(alt_path, 'r') as f:
                        self.calibration_data = json.load(f)
                    return
            
            # If no file found, use default calibration data
            self.calibration_data = {
                "pH": [
                    {"color": [255, 0, 0], "value": 6.2},
                    {"color": [255, 127, 0], "value": 6.8},
                    {"color": [255, 255, 0], "value": 7.2},
                    {"color": [0, 255, 0], "value": 7.8},
                    {"color": [0, 0, 255], "value": 8.4}
                ],
                "chlorine": [
                    {"color": [255, 255, 255], "value": 0.0},
                    {"color": [255, 255, 200], "value": 1.0},
                    {"color": [255, 255, 150], "value": 3.0},
                    {"color": [255, 255, 100], "value": 5.0},
                    {"color": [255, 255, 50], "value": 10.0}
                ],
                "alkalinity": [
                    {"color": [200, 200, 255], "value": 0},
                    {"color": [150, 150, 255], "value": 40},
                    {"color": [100, 100, 255], "value": 80},
                    {"color": [50, 50, 255], "value": 120},
                    {"color": [0, 0, 255], "value": 180},
                    {"color": [0, 0, 200], "value": 240}
                ]
            }
            
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"Error loading calibration data: {e}")
            # Use default calibration data
            self.calibration_data = {
                "pH": [
                    {"color": [255, 0, 0], "value": 6.2},
                    {"color": [255, 127, 0], "value": 6.8},
                    {"color": [255, 255, 0], "value": 7.2},
                    {"color": [0, 255, 0], "value": 7.8},
                    {"color": [0, 0, 255], "value": 8.4}
                ],
                "chlorine": [
                    {"color": [255, 255, 255], "value": 0.0},
                    {"color": [255, 255, 200], "value": 1.0},
                    {"color": [255, 255, 150], "value": 3.0},
                    {"color": [255, 255, 100], "value": 5.0},
                    {"color": [255, 255, 50], "value": 10.0}
                ],
                "alkalinity": [
                    {"color": [200, 200, 255], "value": 0},
                    {"color": [150, 150, 255], "value": 40},
                    {"color": [100, 100, 255], "value": 80},
                    {"color": [50, 50, 255], "value": 120},
                    {"color": [0, 0, 255], "value": 180},
                    {"color": [0, 0, 200], "value": 240}
                ]
            }

    def get_value_from_color(self, chemical: str, color: List[int]) -> float:
        """
        Get the chemical value from a color.
        
        Args:
            chemical: Name of the chemical
            color: RGB color value
            
        Returns:
            The chemical value corresponding to the color
        """
        if chemical not in self.calibration_data:
            logger.warning(f"No calibration data for chemical: {chemical}")
            return 0.0
        
        # Find the closest color in the calibration data
        min_distance = float('inf')
        closest_value = 0.0
        
        for entry in self.calibration_data[chemical]:
            cal_color = entry["color"]
            distance = sum((c1 - c2) ** 2 for c1, c2 in zip(color, cal_color))
            
            if distance < min_distance:
                min_distance = distance
                closest_value = entry["value"]
        
        return closest_value


class TestStripAnalyzer:
    """
    Test strip analyzer for pool water chemistry.
    
    This class provides functionality for analyzing pool test strips using computer vision
    to determine water chemistry parameters and provide recommendations.
    
    Attributes:
        image_path: Path to the test strip image
        calibrator: Color calibrator for mapping RGB values to chemical readings
        config: Configuration dictionary
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the test strip analyzer.
        
        Args:
            config: Configuration dictionary
        """
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initializing Test Strip Analyzer")
        
        self.image_path = None
        self.latest_image_path = None
        self.image_cache = {}
        
        # Default configuration
        self.config = {
            "brand": "default",
            "calibration_file": "data/calibration.json",
            "pad_zones_file": "data/pad_zones.json",
            "cache_dir": "data/cache"
        }
        
        # Update with provided configuration
        if config:
            self.config.update(config)
        
        # Initialize color calibrator
        self.calibrator = ColorCalibrator(self.config["calibration_file"])
        
        # Load pad zones
        self.pad_zones = self._load_pad_zones()
        
        # Ensure cache directory exists
        os.makedirs(self.config["cache_dir"], exist_ok=True)
        
        self.logger.info("Test Strip Analyzer initialized")
    
    def _load_pad_zones(self) -> Dict[str, Dict[str, int]]:
        """
        Load pad zones from a JSON file.
        
        Returns:
            Dictionary of pad zones for each chemical
        """
        try:
            # Try the specified path
            if os.path.exists(self.config["pad_zones_file"]):
                with open(self.config["pad_zones_file"], 'r') as f:
                    return json.load(f)
            
            # Try alternative paths
            alt_paths = [
                "data/pad_zones.json",
                "services/image_processing/pad_zones.json"
            ]
            
            for path in alt_paths:
                if os.path.exists(path):
                    with open(path, 'r') as f:
                        return json.load(f)
            
            # If no file found, use default pad zones
            return {
                "pH": {"x": 50, "y": 100, "width": 50, "height": 50},
                "chlorine": {"x": 150, "y": 100, "width": 50, "height": 50},
                "alkalinity": {"x": 250, "y": 100, "width": 50, "height": 50},
                "calcium": {"x": 350, "y": 100, "width": 50, "height": 50},
                "cyanuric_acid": {"x": 450, "y": 100, "width": 50, "height": 50}
            }
        except (FileNotFoundError, json.JSONDecodeError) as e:
            self.logger.error(f"Error loading pad zones: {e}")
            # Use default pad zones
            return {
                "pH": {"x": 50, "y": 100, "width": 50, "height": 50},
                "chlorine": {"x": 150, "y": 100, "width": 50, "height": 50},
                "alkalinity": {"x": 250, "y": 100, "width": 50, "height": 50},
                "calcium": {"x": 350, "y": 100, "width": 50, "height": 50},
                "cyanuric_acid": {"x": 450, "y": 100, "width": 50, "height": 50}
            }
    
    def capture_image(self) -> Optional[str]:
        """
        Capture an image from the camera.
        
        Returns:
            Path to the captured image, or None if capture failed
        """
        try:
            import cv2
            
            # Initialize camera
            cap = cv2.VideoCapture(0)
            
            if not cap.isOpened():
                self.logger.error("Failed to open camera")
                # Try alternative camera index
                cap = cv2.VideoCapture(1)
                if not cap.isOpened():
                    self.logger.error("Failed to open alternative camera")
                    # Fall back to test image
                    return self._use_test_image()
            
            # Wait for camera to initialize
            time.sleep(1)
            
            # Set camera properties for better image quality
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
            cap.set(cv2.CAP_PROP_BRIGHTNESS, 150)
            cap.set(cv2.CAP_PROP_CONTRAST, 150)
            
            # Capture multiple frames to allow camera to adjust
            for i in range(5):
                ret, frame = cap.read()
                time.sleep(0.1)
            
            # Capture final frame
            ret, frame = cap.read()
            
            if not ret or frame is None:
                self.logger.error("Failed to capture frame")
                cap.release()
                # Fall back to test image
                return self._use_test_image()
            
            # Save frame to file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            image_path = f"data/captured_strip_{timestamp}.jpg"
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(image_path), exist_ok=True)
            
            # Apply image enhancement
            # Convert to HSV for better color analysis
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            
            # Apply slight Gaussian blur to reduce noise
            blurred = cv2.GaussianBlur(hsv, (5, 5), 0)
            
            # Convert back to BGR for saving
            enhanced = cv2.cvtColor(blurred, cv2.COLOR_HSV2BGR)
            
            # Save both original and enhanced images
            cv2.imwrite(image_path, frame)
            
            enhanced_path = f"data/enhanced_strip_{timestamp}.jpg"
            cv2.imwrite(enhanced_path, enhanced)
            
            # Release camera
            cap.release()
            
            self.logger.info(f"Image captured and saved to {image_path}")
            self.logger.info(f"Enhanced image saved to {enhanced_path}")
            
            # Set the image path and clear the cache
            self.image_path = enhanced_path
            self.latest_image_path = enhanced_path
            self.image_cache = {}
            
            # Return the enhanced image path
            return enhanced_path
        except Exception as e:
            self.logger.error(f"Error capturing image: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            # Fall back to test image
            return self._use_test_image()
    
    def _use_test_image(self) -> Optional[str]:
        """
        Use a test image as a fallback.
        
        Returns:
            Path to the test image or None if not found
        """
        test_image_paths = [
            "assets/images/test_strip.jpg",
            "data/test_strip.jpg",
            "services/image_processing/test_strip.jpg"
        ]
        
        for path in test_image_paths:
            if os.path.exists(path):
                self.image_path = path
                self.latest_image_path = path
                self.image_cache = {}
                self.logger.info(f"Using test image: {path}")
                return path
        
        self.logger.error("No test image found")
        return None

    def load_image(self, image_path: str) -> Optional[str]:
        """
        Load a test strip image from a file.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Path to the loaded image or None if failed
            
        Raises:
            FileNotFoundError: If the image file doesn't exist
        """
        if not os.path.exists(image_path):
            self.logger.error(f"Image file not found: {image_path}")
            return None
        
        self.image_path = image_path
        self.latest_image_path = image_path
        # Clear the image cache when a new image is loaded
        self.image_cache = {}
        self.logger.info(f"Loaded image: {self.image_path}")
        return self.image_path
    
    def analyze(self) -> Dict[str, Any]:
        """
        Analyze the test strip image.
        
        Returns:
            Dictionary of chemical readings
            
        Raises:
            ValueError: If no image is loaded
            FileNotFoundError: If the image file doesn't exist
        """
        if not self.image_path:
            if self.latest_image_path:
                self.image_path = self.latest_image_path
            else:
                self.logger.error("No image loaded")
                return {}
        
        if not os.path.exists(self.image_path):
            self.logger.error(f"Image file not found: {self.image_path}")
            return {}
        
        try:
            # Load the image
            image = cv2.imread(self.image_path)
            
            if image is None:
                self.logger.error(f"Failed to load image: {self.image_path}")
                return {}
            
            # Analyze each chemical pad
            results = {}
            
            for chemical, zone in self.pad_zones.items():
                # Extract the pad region
                x, y, width, height = zone["x"], zone["y"], zone["width"], zone["height"]
                
                # Ensure coordinates are within image bounds
                img_height, img_width = image.shape[:2]
                x = min(max(0, x), img_width - 1)
                y = min(max(0, y), img_height - 1)
                width = min(width, img_width - x)
                height = min(height, img_height - y)
                
                # Extract the pad region
                pad = image[y:y+height, x:x+width]
                
                if pad.size == 0:
                    self.logger.warning(f"Empty pad region for {chemical}")
                    continue
                
                # Calculate the average color
                avg_color = np.mean(pad, axis=(0, 1)).astype(int)
                
                # Convert BGR to RGB
                avg_color = avg_color[::-1]
                
                # Get the chemical value from the color
                value = self.calibrator.get_value_from_color(chemical, avg_color.tolist())
                
                # Add to results
                results[chemical] = value
            
            # Add additional information
            results["timestamp"] = datetime.now().isoformat()
            results["source"] = "test_strip"
            
            self.logger.info(f"Analysis results: {results}")
            return results
        except Exception as e:
            self.logger.error(f"Error analyzing image: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            return {}
    
    def get_recommendations(self, results: Dict[str, Any]) -> Dict[str, str]:
        """
        Get recommendations based on the analysis results.
        
        Args:
            results: Dictionary of chemical readings
            
        Returns:
            Dictionary of recommendations for each chemical
        """
        recommendations = {}
        
        # pH recommendations
        if "pH" in results:
            ph = float(results["pH"])
            if ph < 7.2:
                recommendations["pH"] = "pH is too low. Add pH increaser."
            elif ph > 7.8:
                recommendations["pH"] = "pH is too high. Add pH decreaser."
            else:
                recommendations["pH"] = "pH is in the ideal range."
        
        # Chlorine recommendations
        if "chlorine" in results:
            chlorine = float(results["chlorine"])
            if chlorine < 1.0:
                recommendations["chlorine"] = "Chlorine is too low. Add chlorine."
            elif chlorine > 3.0:
                recommendations["chlorine"] = "Chlorine is too high. Stop adding chlorine and wait for levels to decrease."
            else:
                recommendations["chlorine"] = "Chlorine is in the ideal range."
        
        # Alkalinity recommendations
        if "alkalinity" in results:
            alkalinity = float(results["alkalinity"])
            if alkalinity < 80:
                recommendations["alkalinity"] = "Alkalinity is too low. Add alkalinity increaser."
            elif alkalinity > 120:
                recommendations["alkalinity"] = "Alkalinity is too high. Add pH decreaser to lower alkalinity."
            else:
                recommendations["alkalinity"] = "Alkalinity is in the ideal range."
        
        # Calcium recommendations
        if "calcium" in results:
            calcium = float(results["calcium"])
            if calcium < 200:
                recommendations["calcium"] = "Calcium hardness is too low. Add calcium hardness increaser."
            elif calcium > 400:
                recommendations["calcium"] = "Calcium hardness is too high. Dilute with fresh water."
            else:
                recommendations["calcium"] = "Calcium hardness is in the ideal range."
        
        # Cyanuric acid recommendations
        if "cyanuric_acid" in results:
            cyanuric_acid = float(results["cyanuric_acid"])
            if cyanuric_acid < 30:
                recommendations["cyanuric_acid"] = "Cyanuric acid is too low. Add cyanuric acid."
            elif cyanuric_acid > 50:
                recommendations["cyanuric_acid"] = "Cyanuric acid is too high. Dilute with fresh water."
            else:
                recommendations["cyanuric_acid"] = "Cyanuric acid is in the ideal range."
        
        return recommendations
    
    def clear_cache(self) -> None:
        """Clear the image cache."""
        self.image_cache = {}
        self.logger.info("Image cache cleared")
