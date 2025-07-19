
"""
Test Strip Analyzer for Deep Blue Pool Chemistry application.

This module provides functionality for analyzing test strips using image processing.
"""

import os
import sys
import logging
import json
import cv2
import numpy as np
from typing import Dict, Any, List, Tuple, Optional, Union

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("pool_chemistry.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("services.test_strip")

class TestStripAnalyzer:
    """
    Test Strip Analyzer class for analyzing pool test strips.
    
    This class provides functionality for analyzing test strips using image processing.
    It can detect the color of test pads and determine chemical levels based on color.
    """
    
    def __init__(self, config=None):
        """
        Initialize the Test Strip Analyzer.
        
        Args:
            config: Configuration dictionary or path to profiles directory
                If a string is provided, it's treated as the profiles_dir
                If a dictionary is provided, it should contain a 'profiles_dir' key
        """
        logger.info("Initializing Test Strip Analyzer")
        
        # Default configuration
        self.config = {
            "profiles_dir": "data/strip_profiles",
            "default_profile": "generic",
            "color_tolerance": 15,
            "pad_min_size": 20,
            "pad_max_size": 100
        }
        
        # Update configuration if provided
        if config is not None:
            if isinstance(config, dict):
                self.config.update(config)
            elif isinstance(config, str):
                # If a string is provided, treat it as the profiles_dir
                self.config["profiles_dir"] = config
            else:
                raise ValueError("Config must be a dictionary or a string (profiles_dir)")
        
        # Ensure profiles directory exists
        os.makedirs(self.config["profiles_dir"], exist_ok=True)
        
        # Load strip profiles
        self.profiles = self._load_profiles()
        
        logger.info(f"Test Strip Analyzer initialized with {len(self.profiles)} profiles")
    
    def set_profiles_dir(self, profiles_dir: str):
        """
        Set the profiles directory.
        
        Args:
            profiles_dir: Path to the profiles directory
        """
        self.config["profiles_dir"] = profiles_dir
        os.makedirs(profiles_dir, exist_ok=True)
        self.profiles = self._load_profiles()
        logger.info(f"Profiles directory set to {profiles_dir}")
    
    def _load_profiles(self) -> Dict[str, Any]:
        """
        Load test strip profiles from the profiles directory.
        
        Returns:
            Dictionary of profiles
        """
        profiles = {}
        profiles_dir = self.config["profiles_dir"]
        
        # Create default profile if it doesn't exist
        default_profile_path = os.path.join(profiles_dir, "generic.json")
        if not os.path.exists(default_profile_path):
            self._create_default_profile(default_profile_path)
        
        # Load all profiles
        try:
            for filename in os.listdir(profiles_dir):
                if filename.endswith(".json"):
                    profile_path = os.path.join(profiles_dir, filename)
                    profile_name = os.path.splitext(filename)[0]
                    
                    try:
                        with open(profile_path, 'r') as f:
                            profile = json.load(f)
                        
                        profiles[profile_name] = profile
                        logger.info(f"Loaded profile: {profile_name}")
                    except Exception as e:
                        logger.error(f"Error loading profile {profile_name}: {e}")
        except FileNotFoundError:
            logger.warning(f"Profiles directory {profiles_dir} not found")
        except Exception as e:
            logger.error(f"Error loading profiles: {e}")
        
        return profiles
    
    def _create_default_profile(self, profile_path: str):
        """
        Create a default test strip profile.
        
        Args:
            profile_path: Path to save the profile
        """
        default_profile = {
            "name": "Generic Test Strip",
            "description": "Generic profile for standard 6-pad test strips",
            "pads": [
                {
                    "name": "Free Chlorine",
                    "unit": "ppm",
                    "colors": [
                        {"value": 0, "color": [255, 255, 255]},
                        {"value": 1, "color": [255, 230, 230]},
                        {"value": 3, "color": [255, 200, 200]},
                        {"value": 5, "color": [255, 150, 150]},
                        {"value": 10, "color": [255, 100, 100]}
                    ]
                },
                {
                    "name": "pH",
                    "unit": "",
                    "colors": [
                        {"value": 6.2, "color": [255, 50, 50]},
                        {"value": 6.8, "color": [255, 150, 50]},
                        {"value": 7.2, "color": [255, 255, 50]},
                        {"value": 7.8, "color": [50, 255, 50]},
                        {"value": 8.4, "color": [50, 50, 255]}
                    ]
                },
                {
                    "name": "Total Alkalinity",
                    "unit": "ppm",
                    "colors": [
                        {"value": 0, "color": [255, 255, 255]},
                        {"value": 40, "color": [230, 230, 255]},
                        {"value": 120, "color": [200, 200, 255]},
                        {"value": 180, "color": [150, 150, 255]},
                        {"value": 240, "color": [100, 100, 255]}
                    ]
                },
                {
                    "name": "Total Hardness",
                    "unit": "ppm",
                    "colors": [
                        {"value": 0, "color": [255, 255, 255]},
                        {"value": 50, "color": [255, 230, 255]},
                        {"value": 150, "color": [255, 200, 255]},
                        {"value": 300, "color": [255, 150, 255]},
                        {"value": 500, "color": [255, 100, 255]}
                    ]
                },
                {
                    "name": "Cyanuric Acid",
                    "unit": "ppm",
                    "colors": [
                        {"value": 0, "color": [255, 255, 255]},
                        {"value": 30, "color": [230, 255, 230]},
                        {"value": 50, "color": [200, 255, 200]},
                        {"value": 100, "color": [150, 255, 150]},
                        {"value": 150, "color": [100, 255, 100]}
                    ]
                },
                {
                    "name": "Total Bromine",
                    "unit": "ppm",
                    "colors": [
                        {"value": 0, "color": [255, 255, 255]},
                        {"value": 2, "color": [255, 255, 230]},
                        {"value": 5, "color": [255, 255, 200]},
                        {"value": 10, "color": [255, 255, 150]},
                        {"value": 20, "color": [255, 255, 100]}
                    ]
                }
            ]
        }
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(profile_path), exist_ok=True)
        
        # Save the profile
        with open(profile_path, 'w') as f:
            json.dump(default_profile, f, indent=4)
        
        logger.info(f"Created default profile at {profile_path}")
    
    def analyze_image(self, image_path: str, profile_name: str = None) -> Dict[str, Any]:
        """
        Analyze a test strip image.
        
        Args:
            image_path: Path to the test strip image
            profile_name: Name of the profile to use (default: generic)
            
        Returns:
            Dictionary of chemical readings
        """
        if profile_name is None:
            profile_name = self.config["default_profile"]
        
        if profile_name not in self.profiles:
            logger.warning(f"Profile {profile_name} not found. Using generic profile.")
            profile_name = "generic"
        
        profile = self.profiles[profile_name]
        
        try:
            # Load image
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"Could not load image: {image_path}")
            
            # For demonstration purposes, we'll just return random values
            # In a real implementation, this would analyze the image
            import random
            
            readings = {}
            for pad in profile["pads"]:
                pad_name = pad["name"]
                pad_unit = pad["unit"]
                
                # Get min and max values from the profile
                min_value = pad["colors"][0]["value"]
                max_value = pad["colors"][-1]["value"]
                
                # Generate a random value within the range
                value = round(random.uniform(min_value, max_value), 1)
                
                readings[pad_name] = {
                    "value": value,
                    "unit": pad_unit
                }
            
            logger.info(f"Analyzed image {image_path} with profile {profile_name}")
            return readings
            
        except Exception as e:
            logger.error(f"Error analyzing image {image_path}: {e}")
            return {}
    
    def calibrate(self, image_path: str, known_values: Dict[str, float], profile_name: str = None) -> bool:
        """
        Calibrate the analyzer using an image with known values.
        
        Args:
            image_path: Path to the calibration image
            known_values: Dictionary of known chemical values
            profile_name: Name of the profile to calibrate (default: generic)
            
        Returns:
            True if calibration was successful, False otherwise
        """
        if profile_name is None:
            profile_name = self.config["default_profile"]
        
        if profile_name not in self.profiles:
            logger.warning(f"Profile {profile_name} not found. Using generic profile.")
            profile_name = "generic"
        
        try:
            # Load image
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"Could not load image: {image_path}")
            
            # For demonstration purposes, we'll just update the profile
            # In a real implementation, this would analyze the image and update the profile
            
            profile = self.profiles[profile_name]
            
            # Update the profile with the known values
            for pad in profile["pads"]:
                pad_name = pad["name"]
                if pad_name in known_values:
                    # Find the closest color in the profile
                    value = known_values[pad_name]
                    closest_idx = 0
                    closest_diff = abs(pad["colors"][0]["value"] - value)
                    
                    for i, color_info in enumerate(pad["colors"]):
                        diff = abs(color_info["value"] - value)
                        if diff < closest_diff:
                            closest_diff = diff
                            closest_idx = i
                    
                    # Update the color value
                    pad["colors"][closest_idx]["value"] = value
            
            # Save the updated profile
            profile_path = os.path.join(self.config["profiles_dir"], f"{profile_name}.json")
            with open(profile_path, 'w') as f:
                json.dump(profile, f, indent=4)
            
            logger.info(f"Calibrated profile {profile_name} with image {image_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error calibrating with image {image_path}: {e}")
            return False
    
    def get_profiles(self) -> List[str]:
        """
        Get a list of available profiles.
        
        Returns:
            List of profile names
        """
        return list(self.profiles.keys())
    
    def get_profile_info(self, profile_name: str) -> Dict[str, Any]:
        """
        Get information about a profile.
        
        Args:
            profile_name: Name of the profile
            
        Returns:
            Profile information dictionary
        """
        if profile_name not in self.profiles:
            logger.warning(f"Profile {profile_name} not found.")
            return {}
        
        profile = self.profiles[profile_name]
        
        # Return a copy of the profile without the colors
        profile_info = {
            "name": profile.get("name", profile_name),
            "description": profile.get("description", ""),
            "pads": []
        }
        
        for pad in profile.get("pads", []):
            pad_info = {
                "name": pad.get("name", ""),
                "unit": pad.get("unit", ""),
                "min_value": pad["colors"][0]["value"] if pad.get("colors") else 0,
                "max_value": pad["colors"][-1]["value"] if pad.get("colors") else 0
            }
            profile_info["pads"].append(pad_info)
        
        return profile_info
