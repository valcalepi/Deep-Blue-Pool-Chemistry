"""
Deep Blue Pool Chemistry Management System
Copyright (c) 2024 Michael Hayes. All rights reserved.

This software is proprietary and confidential.
Unauthorized copying, distribution, or use is strictly prohibited.

Owner: Michael Hayes
"""

"""
Advanced Test Strip Analyzer - High Precision Color Analysis
Supports both image upload and camera capture
"""

import cv2
import numpy as np
from PIL import Image
import logging
from typing import Dict, Tuple, Optional, List, Any
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class ColorRange:
    """Color range definition for test strip analysis"""
    name: str
    lower_hsv: Tuple[int, int, int]
    upper_hsv: Tuple[int, int, int]
    value: float
    tolerance: float = 0.1


@dataclass
class TestStripMetric:
    """Test strip metric configuration"""
    name: str
    position: int  # Position on strip (0-based)
    color_ranges: List[ColorRange]
    unit: str
    ideal_min: float
    ideal_max: float


class TestStripAnalyzer:
    """
    High-precision test strip analyzer using advanced computer vision
    """
    
    def __init__(self):
        """Initialize the analyzer with calibrated color ranges"""
        self.metrics = self._initialize_metrics()
        self.calibration_card = None
        self.last_analysis = None
        
    def _initialize_metrics(self) -> Dict[str, TestStripMetric]:
        """
        Initialize test strip metrics with precise color ranges
        Based on standard pool test strip color charts
        """
        
        # pH Color Ranges (Yellow to Red/Purple)
        ph_ranges = [
            ColorRange("pH 6.2", (15, 100, 100), (25, 255, 255), 6.2),
            ColorRange("pH 6.8", (20, 80, 120), (30, 200, 255), 6.8),
            ColorRange("pH 7.2", (25, 60, 140), (35, 180, 255), 7.2),
            ColorRange("pH 7.6", (30, 50, 150), (40, 160, 255), 7.6),
            ColorRange("pH 8.0", (35, 40, 160), (45, 140, 255), 8.0),
            ColorRange("pH 8.4", (140, 40, 160), (160, 140, 255), 8.4),
        ]
        
        # Free Chlorine Ranges (White to Pink/Red)
        free_chlorine_ranges = [
            ColorRange("0 ppm", (0, 0, 200), (180, 30, 255), 0.0),
            ColorRange("0.5 ppm", (160, 30, 180), (180, 80, 255), 0.5),
            ColorRange("1.0 ppm", (150, 50, 160), (170, 120, 255), 1.0),
            ColorRange("2.0 ppm", (140, 80, 140), (160, 160, 255), 2.0),
            ColorRange("3.0 ppm", (130, 100, 120), (150, 200, 255), 3.0),
            ColorRange("5.0 ppm", (120, 120, 100), (140, 240, 255), 5.0),
        ]
        
        # Total Chlorine Ranges (White to Dark Pink)
        total_chlorine_ranges = [
            ColorRange("0 ppm", (0, 0, 200), (180, 30, 255), 0.0),
            ColorRange("0.5 ppm", (160, 30, 180), (180, 80, 255), 0.5),
            ColorRange("1.0 ppm", (150, 50, 160), (170, 120, 255), 1.0),
            ColorRange("2.0 ppm", (140, 80, 140), (160, 160, 255), 2.0),
            ColorRange("3.0 ppm", (130, 100, 120), (150, 200, 255), 3.0),
            ColorRange("5.0 ppm", (120, 120, 100), (140, 240, 255), 5.0),
        ]
        
        # Alkalinity Ranges (Yellow to Green)
        alkalinity_ranges = [
            ColorRange("0 ppm", (20, 100, 100), (30, 255, 255), 0),
            ColorRange("40 ppm", (25, 80, 120), (35, 200, 255), 40),
            ColorRange("80 ppm", (30, 60, 140), (45, 180, 255), 80),
            ColorRange("120 ppm", (40, 50, 150), (60, 160, 255), 120),
            ColorRange("180 ppm", (50, 40, 160), (80, 140, 255), 180),
            ColorRange("240 ppm", (60, 30, 170), (100, 120, 255), 240),
        ]
        
        # Calcium Hardness Ranges (Pink to Purple)
        calcium_ranges = [
            ColorRange("0 ppm", (160, 30, 180), (180, 80, 255), 0),
            ColorRange("100 ppm", (150, 50, 160), (170, 120, 255), 100),
            ColorRange("250 ppm", (140, 80, 140), (160, 160, 255), 250),
            ColorRange("400 ppm", (130, 100, 120), (150, 200, 255), 400),
            ColorRange("800 ppm", (120, 120, 100), (140, 240, 255), 800),
        ]
        
        # Cyanuric Acid Ranges (White to Blue)
        cya_ranges = [
            ColorRange("0 ppm", (0, 0, 200), (180, 30, 255), 0),
            ColorRange("30 ppm", (90, 30, 180), (110, 80, 255), 30),
            ColorRange("50 ppm", (85, 50, 160), (105, 120, 255), 50),
            ColorRange("100 ppm", (80, 80, 140), (100, 160, 255), 100),
            ColorRange("150 ppm", (75, 100, 120), (95, 200, 255), 150),
        ]
        
        # Bromine Ranges (Yellow to Brown)
        bromine_ranges = [
            ColorRange("0 ppm", (20, 100, 100), (30, 255, 255), 0.0),
            ColorRange("2.0 ppm", (15, 80, 120), (25, 200, 255), 2.0),
            ColorRange("4.0 ppm", (10, 60, 140), (20, 180, 255), 4.0),
            ColorRange("6.0 ppm", (5, 50, 150), (15, 160, 255), 6.0),
            ColorRange("8.0 ppm", (0, 40, 160), (10, 140, 255), 8.0),
        ]
        
        # Salt/TDS Ranges (White to Yellow)
        salt_ranges = [
            ColorRange("0 ppm", (0, 0, 200), (180, 30, 255), 0),
            ColorRange("1500 ppm", (25, 20, 180), (35, 60, 255), 1500),
            ColorRange("2700 ppm", (20, 40, 160), (30, 100, 255), 2700),
            ColorRange("3400 ppm", (15, 60, 140), (25, 140, 255), 3400),
            ColorRange("5000 ppm", (10, 80, 120), (20, 180, 255), 5000),
        ]
        
        return {
            'ph': TestStripMetric('pH', 0, ph_ranges, '', 7.2, 7.6),
            'free_chlorine': TestStripMetric('Free Chlorine', 1, free_chlorine_ranges, 'ppm', 1.0, 3.0),
            'total_chlorine': TestStripMetric('Total Chlorine', 2, total_chlorine_ranges, 'ppm', 1.0, 3.0),
            'alkalinity': TestStripMetric('Alkalinity', 3, alkalinity_ranges, 'ppm', 80, 120),
            'calcium_hardness': TestStripMetric('Calcium Hardness', 4, calcium_ranges, 'ppm', 200, 400),
            'cyanuric_acid': TestStripMetric('Cyanuric Acid', 5, cya_ranges, 'ppm', 30, 50),
            'bromine': TestStripMetric('Bromine', 6, bromine_ranges, 'ppm', 2.0, 4.0),
            'salt': TestStripMetric('Salt/TDS', 7, salt_ranges, 'ppm', 2700, 3400),
        }
    
    def analyze_image(self, image_path: str) -> Dict[str, any]:
        """
        Analyze test strip from image file
        
        Args:
            image_path: Path to test strip image
            
        Returns:
            Dictionary with analysis results
        """
        try:
            # Load image
            img = cv2.imread(image_path)
            if img is None:
                raise ValueError(f"Could not load image: {image_path}")
            
            return self._analyze_strip(img)
            
        except Exception as e:
            logger.error(f"Error analyzing image: {e}")
            return {'error': str(e)}
    
    def analyze_camera(self, camera_index: int = 0) -> Dict[str, Any]:
        """
        Capture and analyze test strip from camera
        
        Returns:
            Dictionary with analysis results
        """
        cap = None
        try:
            # Open camera
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                return {
                    'error': 'Could not open camera. Please check:\n'
                             '- Camera is connected\n'
                             '- Camera permissions are granted\n'
                             '- No other app is using the camera'
                }
            
            # Capture frame
            ret, frame = cap.read()
            
            if not ret:
                return {'error': 'Could not capture frame from camera'}
            
            return self._analyze_strip(frame)
            
        except Exception as e:
            logger.error(f"Error analyzing camera: {e}")
            return {'error': str(e)}
        finally:
            if cap is not None:
                cap.release()
    
    def _analyze_strip(self, img: np.ndarray) -> Dict[str, any]:
        """
        Core analysis function for test strip
        
        Args:
            img: OpenCV image (BGR format)
            
        Returns:
            Dictionary with analysis results
        """
        try:
            # Preprocess image
            processed = self._preprocess_image(img)
            
            # Detect test strip
            strip_region = self._detect_strip(processed)
            if strip_region is None:
                return {'error': 'Could not detect test strip in image'}
            
            # Extract color pads
            pads = self._extract_color_pads(strip_region)
            
            # Analyze each pad
            results = {}
            confidence_scores = {}
            
            for metric_name, metric in self.metrics.items():
                if metric.position < len(pads):
                    pad = pads[metric.position]
                    value, confidence = self._analyze_pad(pad, metric)
                    results[metric_name] = value
                    confidence_scores[metric_name] = confidence
                else:
                    results[metric_name] = None
                    confidence_scores[metric_name] = 0.0
            
            # Calculate overall confidence
            overall_confidence = np.mean(list(confidence_scores.values()))
            
            self.last_analysis = {
                'results': results,
                'confidence_scores': confidence_scores,
                'overall_confidence': overall_confidence,
                'timestamp': self._get_timestamp()
            }
            
            return self.last_analysis
            
        except Exception as e:
            logger.error(f"Error in strip analysis: {e}")
            return {'error': str(e)}
    
    def _preprocess_image(self, img: np.ndarray) -> np.ndarray:
        """
        Preprocess image for better analysis
        
        Args:
            img: Input image
            
        Returns:
            Preprocessed image
        """
        # Convert to RGB
        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # Apply white balance
        balanced = self._white_balance(rgb)
        
        # Enhance contrast
        lab = cv2.cvtColor(balanced, cv2.COLOR_RGB2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        l = clahe.apply(l)
        enhanced = cv2.merge([l, a, b])
        enhanced = cv2.cvtColor(enhanced, cv2.COLOR_LAB2RGB)
        
        # Reduce noise
        denoised = cv2.fastNlMeansDenoisingColored(enhanced, None, 10, 10, 7, 21)
        
        return denoised
    
    def _white_balance(self, img: np.ndarray) -> np.ndarray:
        """
        Apply white balance to image
        
        Args:
            img: Input image
            
        Returns:
            White-balanced image
        """
        result = cv2.cvtColor(img, cv2.COLOR_RGB2LAB)
        avg_a = np.average(result[:, :, 1])
        avg_b = np.average(result[:, :, 2])
        result[:, :, 1] = result[:, :, 1] - ((avg_a - 128) * (result[:, :, 0] / 255.0) * 1.1)
        result[:, :, 2] = result[:, :, 2] - ((avg_b - 128) * (result[:, :, 0] / 255.0) * 1.1)
        result = cv2.cvtColor(result, cv2.COLOR_LAB2RGB)
        return result
    
    def _detect_strip(self, img: np.ndarray) -> Optional[np.ndarray]:
        """
        Detect test strip in image
        
        Args:
            img: Preprocessed image
            
        Returns:
            Cropped strip region or None
        """
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        
        # Apply edge detection
        edges = cv2.Canny(gray, 50, 150)
        
        # Find contours
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if not contours:
            return img  # Return full image if no contours found
        
        # Find largest rectangular contour
        largest_contour = max(contours, key=cv2.contourArea)
        
        # Get bounding rectangle
        x, y, w, h = cv2.boundingRect(largest_contour)
        
        # Crop to strip region with margin
        margin = 10
        x = max(0, x - margin)
        y = max(0, y - margin)
        w = min(img.shape[1] - x, w + 2 * margin)
        h = min(img.shape[0] - y, h + 2 * margin)
        
        return img[y:y+h, x:x+w]
    
    def _extract_color_pads(self, strip: np.ndarray) -> List[np.ndarray]:
        """
        Extract individual color pads from strip
        
        Args:
            strip: Strip region image
            
        Returns:
            List of color pad images
        """
        height, width = strip.shape[:2]
        
        # Assume pads are arranged horizontally
        num_pads = 8
        pad_width = width // num_pads
        
        pads = []
        for i in range(num_pads):
            x_start = i * pad_width
            x_end = (i + 1) * pad_width
            
            # Extract center region of pad (avoid edges)
            margin_x = pad_width // 4
            margin_y = height // 4
            
            pad = strip[margin_y:height-margin_y, x_start+margin_x:x_end-margin_x]
            pads.append(pad)
        
        return pads
    
    def _analyze_pad(self, pad: np.ndarray, metric: TestStripMetric) -> Tuple[float, float]:
        """
        Analyze a single color pad
        
        Args:
            pad: Color pad image
            metric: Metric configuration
            
        Returns:
            Tuple of (value, confidence)
        """
        # Convert to HSV
        hsv = cv2.cvtColor(pad, cv2.COLOR_RGB2HSV)
        
        # Get average color
        avg_color = np.mean(hsv, axis=(0, 1))
        
        # Find best matching color range
        best_match = None
        best_distance = float('inf')
        
        for color_range in metric.color_ranges:
            # Calculate color distance
            lower = np.array(color_range.lower_hsv)
            upper = np.array(color_range.upper_hsv)
            center = (lower + upper) / 2
            
            distance = np.linalg.norm(avg_color - center)
            
            if distance < best_distance:
                best_distance = distance
                best_match = color_range
        
        if best_match is None:
            return None, 0.0
        
        # Calculate confidence (inverse of distance, normalized)
        max_distance = 200  # Maximum expected distance
        confidence = max(0.0, 1.0 - (best_distance / max_distance))
        
        return best_match.value, confidence
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    def get_last_analysis(self) -> Optional[Dict]:
        """Get last analysis results"""
        return self.last_analysis
    
    def save_analysis(self, filepath: str):
        """Save last analysis to file"""
        if self.last_analysis is None:
            raise ValueError("No analysis to save")
        
        import json
        with open(filepath, 'w') as f:
            json.dump(self.last_analysis, f, indent=2)
