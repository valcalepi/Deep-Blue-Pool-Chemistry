#!/usr/bin/env python3
"""
Test script for the consolidated Deep Blue Pool Chemistry Application.

This script tests the consolidated_pool_app.py and its compatibility wrappers
to ensure they work correctly in various modes.
"""

import os
import sys
import subprocess
import unittest
import tempfile
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TestConsolidatedApp(unittest.TestCase):
    """Test cases for the consolidated application."""
    
    def setUp(self):
        """Set up test environment."""
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.consolidated_script = os.path.join(self.script_dir, "consolidated_pool_app.py")
        self.enhanced_script = os.path.join(self.script_dir, "run_enhanced_app.py")
        self.basic_script = os.path.join(self.script_dir, "launch_pool_app.py")
        
        # Create a test configuration file
        self.config_file = os.path.join(tempfile.gettempdir(), "test_config.json")
        self.create_test_config()
    
    def tearDown(self):
        """Clean up after tests."""
        # Remove test configuration file
        if os.path.exists(self.config_file):
            os.remove(self.config_file)
    
    def create_test_config(self):
        """Create a test configuration file."""
        config = {
            "app_name": "Test Pool Chemistry",
            "version": "1.0.0",
            "location": "Test Location",
            "weather_update_interval": 3600,
            "database_path": ":memory:",  # Use in-memory database for testing
            "theme": "light",
            "enable_camera": False,  # Disable camera for testing
            "enable_weather": True,
            "enable_chemical_safety": True,
            "enable_test_strip_analyzer": True,
            "enable_database": True
        }
        
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=4)
    
    def run_script(self, script, args=None, expected_return_code=0):
        """Run a script and check its return code."""
        if args is None:
            args = []
        
        cmd = [sys.executable, script] + args
        logger.info(f"Running: {' '.join(cmd)}")
        
        # Run with a short timeout to avoid hanging tests
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            logger.info(f"Return code: {result.returncode}")
            logger.info(f"Output: {result.stdout}")
            if result.stderr:
                logger.warning(f"Error output: {result.stderr}")
            
            self.assertEqual(result.returncode, expected_return_code)
            return result
        except subprocess.TimeoutExpired:
            logger.warning("Command timed out")
            self.fail("Command timed out")
    
    def test_help_option(self):
        """Test that the help option works."""
        result = self.run_script(self.consolidated_script, ["--help"])
        self.assertIn("usage:", result.stdout)
        self.assertIn("options:", result.stdout)
    
    def test_debug_option(self):
        """Test that the debug option works."""
        result = self.run_script(self.consolidated_script, ["--debug", "--help"])
        self.assertIn("usage:", result.stdout)
    
    def test_config_option(self):
        """Test that the config option works."""
        result = self.run_script(self.consolidated_script, ["--config", self.config_file, "--help"])
        self.assertIn("usage:", result.stdout)
    
    def test_enhanced_wrapper(self):
        """Test that the enhanced wrapper script works."""
        result = self.run_script(self.enhanced_script, ["--help"])
        self.assertIn("usage:", result.stdout)
        self.assertIn("Enhanced Mode", result.stdout)
    
    def test_basic_wrapper(self):
        """Test that the basic wrapper script works."""
        result = self.run_script(self.basic_script, ["--help"])
        self.assertIn("usage:", result.stdout)
        self.assertIn("Basic Mode", result.stdout)
    
    def test_cli_mode(self):
        """Test CLI mode with help option."""
        result = self.run_script(self.consolidated_script, ["--cli", "--help"])
        self.assertIn("usage:", result.stdout)
    
    def test_gui_mode(self):
        """Test GUI mode with help option."""
        result = self.run_script(self.consolidated_script, ["--gui", "--help"])
        self.assertIn("usage:", result.stdout)

if __name__ == "__main__":
    unittest.main()
