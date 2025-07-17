
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
from typing import Dict, List, Optional, Any, Tuple
from PIL import Image

# Configure logger
logger = logging.getLogger(__name__)


class ColorCalibrator:
    """
    Color calibrator for mapping RGB values to chemical readings.
    
    This class handles the calibration data for mapping RGB colors to chemical values.
    
    Attributes:
        calibration_data: Dictionary of calibration data for each chemical
    """
    
    def __init__(self, calibration_file: str = "services/image_processing/calibration.json"):
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
            with open(path, "r") as f:
                self.calibration_data = json.load(f)
            logger.info(f"Loaded calibration data from {path}")
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"Failed to load calibration data: {e}")
            self.calibration_data = {}

    def _distance(self, rgb1: List[int], rgb2: List[int]) -> float:
        """
        Calculate the Euclidean distance between two RGB colors.
        
        Args:
            rgb1: First RGB color as a list [R, G, B]
            rgb2: Second RGB color as a list [R, G, B]
            
        Returns:
            Euclidean distance between the colors
        """
        return np.sqrt(sum((a - b) ** 2 for a, b in zip(rgb1, rgb2)))

    def map_rgb_to_value(self, chemical: str, rgb_sample: List[int]) -> Tuple[Optional[float], float]:
        """
        Map an RGB color to a chemical value using calibration data.
        
        Uses weighted interpolation of the closest calibration samples.
        
        Args:
            chemical: Name of the chemical
            rgb_sample: RGB color as a list [R, G, B]
            
        Returns:
            Tuple of (interpolated value, confidence percentage)
        """
        samples = self.calibration_data.get(chemical, [])
        if not samples:
            return None, 0.0

        # Calculate distances to all calibration samples
        distances = [(self._distance(rgb_sample, s["rgb"]), s["value"]) for s in samples]
        distances.sort(key=lambda x: x[0])
        
        # Use the top 3 closest samples for interpolation
        top = distances[:3]

        # Calculate weighted average based on inverse distance
        weights = [1 / (d + 1e-6) for d, _ in top]
        total_weight = sum(weights)
        interpolated = sum(v * w for (_, v), w in zip(top, weights)) / total_weight
        
        # Calculate confidence based on distance to closest sample
        # 0 distance = 100% confidence, max possible distance = 0% confidence
        max_possible_distance = np.sqrt(3 * 255 ** 2)  # Maximum RGB distance
        confidence = max(0.0, 100 - top[0][0] / max_possible_distance * 100)

        return round(interpolated, 2), round(confidence, 1)

    def rgb_confidence(self, sample: List[int], reference: List[int]) -> float:
        """
        Calculate confidence score for how closely a sample matches a reference color.
        
        Args:
            sample: Sample RGB color as a list [R, G, B]
            reference: Reference RGB color as a list [R, G, B]
            
        Returns:
            Confidence score (0-100)
        """
        dist = self._distance(sample, reference)
        max_dist = np.sqrt(3 * 255 ** 2)
        score = max(0, 100 - (dist / max_dist) * 100)
        return round(score, 1)


class TestStripAnalyzer:
    """
    Analyzer for pool test strips using computer vision.
    
    This class provides functionality for capturing, analyzing, and interpreting
    pool test strips to determine water chemistry parameters.
    
    Attributes:
        latest_image_path: Path to the most recently captured or loaded image
        brand: Brand of test strips being used
        calibrator: Color calibrator for mapping RGB values to chemical readings
        pad_zones: Dictionary of test strip pad zones for each chemical
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the test strip analyzer.
        
        Args:
            config: Configuration dictionary with optional settings
        """
        self.latest_image_path = None
        self.brand = (config or {}).get("strip_brand", "default")
        calib_file = (config or {}).get("calibration_file", "services/image_processing/calibration.json")
        self.calibrator = ColorCalibrator(calib_file)
        self.pad_zones = self._load_pad_zones()
        self.image_cache = {}  # Cache for processed images
        logger.info(f"TestStripAnalyzer initialized with brand: {self.brand}")

    def _load_pad_zones(self) -> Dict[str, List[int]]:
        """
        Load test strip pad zones from configuration file.
        
        Returns:
            Dictionary of pad zones for each chemical
            
        Raises:
            FileNotFoundError: If the pad zones file doesn't exist
            json.JSONDecodeError: If the pad zones file contains invalid JSON
        """
        try:
            with open("services/image_processing/pad_zones.json", "r") as f:
                brands = json.load(f)
                zones = brands.get(self.brand)
                if not zones:
                    logger.warning(f"No pad zones found for brand '{self.brand}', using default layout")
                return zones or {}
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"Failed to load pad zones: {e}")
            return {}

    def capture_image(self) -> Optional[str]:
        """
        Capture or load a test strip image.
        
        In a real implementation, this would capture from a camera.
        This implementation loads a test image from a file.
        
        Returns:
            Path to the captured image or None if failed
            
        Raises:
            FileNotFoundError: If the test image doesn't exist
        """
        test_image_path = "assets/images/test_strip.jpg"
        if not os.path.exists(test_image_path):
            logger.error(f"Test strip image not found: {test_image_path}")
            self.latest_image_path = None
            return None

        self.latest_image_path = test_image_path
        # Clear the image cache when a new image is captured
        self.image_cache = {}
        logger.info(f"Captured image: {self.latest_image_path}")
        return self.latest_image_path

    def load_image(self, image_path: str) -> Optional[str]:
        """
        Load a test strip image from a file.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Path to the loaded image or None if failed
            
        Raises:
            FileNotFoundError: If the image doesn't exist
        """
        if not os.path.exists(image_path):
            logger.error(f"Image not found: {image_path}")
            return None

        self.latest_image_path = image_path
        # Clear the image cache when a new image is loaded
        self.image_cache = {}
        logger.info(f"Loaded image: {self.latest_image_path}")
        return self.latest_image_path

    def get_image_preview(self, with_annotations: bool = True) -> Optional[Image.Image]:
        """
        Get a preview of the test strip image with optional annotations.
        
        Args:
            with_annotations: Whether to include pad zone annotations
            
        Returns:
            PIL Image object or None if no image is available
            
        Raises:
            cv2.error: If there's an error processing the image
        """
        if not self.latest_image_path:
            logger.warning("No image available for preview")
            return None
            
        # Check if we have this preview in the cache
        cache_key = f"preview_{with_annotations}"
        if cache_key in self.image_cache:
            return self.image_cache[cache_key]
            
        try:
            image = cv2.imread(self.latest_image_path)
            if image is None:
                logger.error(f"Failed to load image: {self.latest_image_path}")
                return None
                
            # Create a copy for annotations
            if with_annotations:
                for chem, (x, y, w, h) in self.pad_zones.items():
                    cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    cv2.putText(image, chem, (x, y - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
                    
            # Convert to PIL Image and resize
            preview = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            preview = preview.resize((300, 200))
            
            # Cache the preview
            self.image_cache[cache_key] = preview
            return preview
        except cv2.error as e:
            logger.error(f"Failed to generate image preview: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error generating preview: {e}")
            return None

    def analyze(self) -> Dict[str, Dict[str, Any]]:
        """
        Analyze the test strip image to determine chemical readings.
        
        Returns:
            Dictionary of chemical readings with values, confidence, and RGB colors
            
        Raises:
            cv2.error: If there's an error processing the image
        """
        if not self.latest_image_path:
            logger.error("No image captured for analysis")
            return {}
            
        # Check if we have the analysis in the cache
        if "analysis" in self.image_cache:
            return self.image_cache["analysis"]

        try:
            image = cv2.imread(self.latest_image_path)
            if image is None:
                logger.error(f"Failed to load image for analysis: {self.latest_image_path}")
                return {}

            # Apply image preprocessing for better color detection
            # Convert to LAB color space for better color differentiation
            lab_image = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
            
            # Apply slight Gaussian blur to reduce noise
            lab_image = cv2.GaussianBlur(lab_image, (3, 3), 0)
            
            results = {}
            for chem, (x, y, w, h) in self.pad_zones.items():
                # Extract region of interest (ROI)
                roi = image[y:y + h, x:x + w]
                
                # Calculate average color in the ROI
                avg_color = cv2.mean(roi)[:3]  # BGR
                
                # Convert to RGB for the calibrator
                rgb = [int(avg_color[2]), int(avg_color[1]), int(avg_color[0])]
                
                # Map RGB to chemical value
                value, confidence = self.calibrator.map_rgb_to_value(chem, rgb)
                
                results[chem] = {
                    "value": value,
                    "confidence": confidence,
                    "rgb": rgb
                }
                logger.debug(f"{chem}: RGB={rgb}, Value={value}, Confidence={confidence}%")

            # Cache the analysis results
            self.image_cache["analysis"] = results
            logger.info("Test strip analysis completed")
            return results
        except cv2.error as e:
            logger.error(f"OpenCV error during analysis: {e}")
            return {}
        except Exception as e:
            logger.error(f"Unexpected error during analysis: {e}")
            return {}

    def get_recommendations(self, analysis_results: Dict[str, Dict[str, Any]]) -> Dict[str, str]:
        """
        Generate recommendations based on analysis results.
        
        Args:
            analysis_results: Dictionary of chemical readings from analyze()
            
        Returns:
            Dictionary of recommendations for each chemical
        """
        recommendations = {}
        
        # Define ideal ranges for each chemical
        ideal_ranges = {
            "pH": (7.2, 7.8),
            "free_chlorine": (1.0, 3.0),
            "total_chlorine": (1.0, 3.0),
            "alkalinity": (80, 120),
            "calcium": (200, 400),
            "cyanuric_acid": (30, 50),
            "bromine": (3.0, 5.0),
            "salt": (2700, 3400)
        }
        
        for chem, result in analysis_results.items():
            value = result.get("value")
            if value is None:
                continue
                
            ideal_range = ideal_ranges.get(chem)
            if not ideal_range:
                continue
                
            low, high = ideal_range
            
            if value < low:
                recommendations[chem] = f"Increase {chem} from {value} to {low}-{high}"
            elif value > high:
                recommendations[chem] = f"Decrease {chem} from {value} to {low}-{high}"
            else:
                recommendations[chem] = f"{chem} level is good at {value} (ideal: {low}-{high})"
                
        return recommendations

    def save_analysis_results(self, results: Dict[str, Dict[str, Any]], filename: str) -> bool:
        """
        Save analysis results to a JSON file.
        
        Args:
            results: Dictionary of chemical readings from analyze()
            filename: Path to save the results
            
        Returns:
            True if successful, False otherwise
            
        Raises:
            IOError: If there's an error writing to the file
        """
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            
            # Add timestamp and image path to results
            from datetime import datetime
            output = {
                "timestamp": datetime.now().isoformat(),
                "image_path": self.latest_image_path,
                "results": results
            }
            
            with open(filename, "w") as f:
                json.dump(output, f, indent=4)
                
            logger.info(f"Analysis results saved to {filename}")
            return True
        except (IOError, OSError) as e:
            logger.error(f"Failed to save analysis results: {e}")
            return False

    def clear_cache(self) -> None:
        """
        Clear the image cache to free memory.
        """
        self.image_cache = {}
        logger.debug("Image cache cleared")
