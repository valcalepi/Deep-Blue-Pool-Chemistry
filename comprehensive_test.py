
#!/usr/bin/env python3
"""
Comprehensive test script for the Deep Blue Pool Chemistry application.

This script tests all major components of the application to ensure they
are working correctly together.
"""

import os
import sys
import logging
import json
import unittest
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("ComprehensiveTest")

class DeepBluePoolChemistryTests(unittest.TestCase):
    """Test suite for Deep Blue Pool Chemistry application."""
    
    def setUp(self):
        """Set up test environment."""
        # Ensure data directory exists
        os.makedirs("data", exist_ok=True)
        
        # Create test configuration
        self.config = {
            "database": {
                "path": "data/test_pool_data.db"
            },
            "chemical_safety": {
                "data_file": "data/test_chemical_safety_data.json"
            },
            "test_strip": {
                "brand": "default",
                "calibration_file": "data/test_calibration.json"
            },
            "weather": {
                "location": "Florida",
                "update_interval": 3600,
                "cache_file": "data/test_weather_cache.json"
            }
        }
        
        # Save test configuration
        with open("test_config.json", "w") as f:
            json.dump(self.config, f, indent=4)
        
        logger.info("Test environment set up")
    
    def tearDown(self):
        """Clean up test environment."""
        # Remove test files
        test_files = [
            "test_config.json",
            "data/test_pool_data.db",
            "data/test_chemical_safety_data.json",
            "data/test_weather_cache.json"
        ]
        
        for file_path in test_files:
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    logger.debug(f"Removed test file: {file_path}")
                except OSError as e:
                    logger.warning(f"Failed to remove test file {file_path}: {e}")
        
        logger.info("Test environment cleaned up")
    
    def test_database_service(self):
        """Test DatabaseService functionality."""
        from database_service import DatabaseService
        
        # Initialize database service
        db_service = DatabaseService(self.config["database"]["path"])
        
        # Test inserting a reading
        test_data = {
            "pH": "7.2",
            "free_chlorine": "1.5",
            "total_chlorine": "2.0",
            "alkalinity": "100",
            "calcium": "250",
            "cyanuric_acid": "40",
            "bromine": "0",
            "salt": "1000",
            "temperature": "78",
            "water_volume": "10000",
            "source": "test"
        }
        
        result = db_service.insert_reading(test_data)
        self.assertTrue(result, "Failed to insert reading")
        
        # Test retrieving readings
        readings = db_service.get_recent_readings(1)
        self.assertEqual(len(readings), 1, "Failed to retrieve reading")
        
        # Test exporting to CSV
        export_result = db_service.export_to_csv("data/test_export.csv")
        self.assertTrue(export_result, "Failed to export to CSV")
        self.assertTrue(os.path.exists("data/test_export.csv"), "Export file not created")
        
        # Clean up
        os.remove("data/test_export.csv")
        db_service.close_all_connections()
        
        logger.info("DatabaseService tests passed")
    
    def test_chemical_safety_database(self):
        """Test ChemicalSafetyDatabase functionality."""
        from chemical_safety_database import ChemicalSafetyDatabase
        
        # Initialize chemical safety database
        csd = ChemicalSafetyDatabase(self.config["chemical_safety"]["data_file"])
        
        # Test getting chemical information
        chemicals = csd.get_all_chemicals()
        self.assertGreater(len(chemicals), 0, "No chemicals found in database")
        
        # Test compatibility check
        compatibility = csd.check_compatibility("chlorine", "sodium_bicarbonate")
        self.assertTrue(compatibility, "Compatibility check failed")
        
        # Test adding a new chemical
        new_chemical = {
            "name": "Test Chemical",
            "chemical_formula": "H2O",
            "hazard_rating": 1,
            "safety_precautions": ["Test precaution"],
            "storage_guidelines": "Test storage guidelines",
            "emergency_procedures": "Test emergency procedures"
        }
        
        result = csd.add_chemical("test_chemical", new_chemical)
        self.assertTrue(result, "Failed to add chemical")
        
        # Test retrieving the new chemical
        test_chemical = csd.get_chemical_safety_info("test_chemical")
        self.assertIsNotNone(test_chemical, "Failed to retrieve added chemical")
        self.assertEqual(test_chemical["name"], "Test Chemical", "Chemical name mismatch")
        
        logger.info("ChemicalSafetyDatabase tests passed")
    
    def test_test_strip_analyzer(self):
        """Test TestStripAnalyzer functionality."""
        from test_strip_analyzer import TestStripAnalyzer
        
        # Initialize test strip analyzer
        tsa = TestStripAnalyzer(self.config["test_strip"])
        
        # Test capturing an image
        image_path = tsa.capture_image()
        self.assertIsNotNone(image_path, "Failed to capture test strip image")
        self.assertTrue(os.path.exists(image_path), "Test strip image not found")
        
        # Test analyzing the image
        results = tsa.analyze()
        self.assertIsInstance(results, dict, "Analysis results should be a dictionary")
        
        # Test getting recommendations
        recommendations = tsa.get_recommendations(results)
        self.assertIsInstance(recommendations, dict, "Recommendations should be a dictionary")
        
        logger.info("TestStripAnalyzer tests passed")
    
    def test_weather_service(self):
        """Test WeatherService functionality."""
        from weather_service import WeatherService
        
        # Initialize weather service
        ws = WeatherService(self.config["weather"])
        
        # Test getting weather data
        weather_data = ws.get_weather()
        self.assertIsInstance(weather_data, dict, "Weather data should be a dictionary")
        self.assertIn("temperature", weather_data, "Weather data missing temperature")
        self.assertIn("humidity", weather_data, "Weather data missing humidity")
        
        # Test getting forecast
        forecast = ws.get_forecast(3)
        self.assertIsInstance(forecast, list, "Forecast should be a list")
        self.assertEqual(len(forecast), 3, "Forecast should have 3 days")
        
        # Test weather impact analysis
        impact = ws.analyze_weather_impact(weather_data)
        self.assertIsInstance(impact, dict, "Impact analysis should be a dictionary")
        self.assertIn("evaporation_rate", impact, "Impact missing evaporation rate")
        self.assertIn("chlorine_loss_rate", impact, "Impact missing chlorine loss rate")
        
        # Test getting weather with impact
        weather_with_impact = ws.get_weather_with_impact()
        self.assertIsInstance(weather_with_impact, dict, "Weather with impact should be a dictionary")
        self.assertIn("weather", weather_with_impact, "Weather with impact missing weather data")
        self.assertIn("impact", weather_with_impact, "Weather with impact missing impact data")
        
        # Clean up
        ws.clear_cache()
        
        logger.info("WeatherService tests passed")
    
    def test_chemical_calculator(self):
        """Test ChemicalCalculator functionality."""
        from gui_controller import ChemicalCalculator
        
        # Initialize chemical calculator
        cc = ChemicalCalculator()
        
        # Test getting ideal range
        ph_range = cc.get_ideal_range("ph")
        self.assertEqual(ph_range, (7.2, 7.8), "pH range incorrect")
        
        # Test calculating adjustments
        adjustments = cc.calculate_adjustments(
            "Concrete/Gunite", 7.0, 0.5, 90, 250, 10000
        )
        self.assertIsInstance(adjustments, dict, "Adjustments should be a dictionary")
        self.assertIn("ph_increaser", adjustments, "Adjustments missing pH increaser")
        self.assertIn("chlorine", adjustments, "Adjustments missing chlorine")
        
        # Test water balance calculation
        balance = cc.evaluate_water_balance(7.2, 100, 250, 78)
        self.assertIsInstance(balance, float, "Water balance should be a float")
        
        logger.info("ChemicalCalculator tests passed")
    
    def test_pool_chemistry_controller(self):
        """Test PoolChemistryController functionality."""
        from gui_controller import PoolChemistryController
        from database_service import DatabaseService
        
        # Initialize database service and controller
        db_service = DatabaseService(self.config["database"]["path"])
        controller = PoolChemistryController(db_service)
        
        # Test validating pool data
        pool_data = {
            "pool_type": "Concrete/Gunite",
            "pool_size": "10000",
            "ph": "7.2",
            "chlorine": "1.5",
            "alkalinity": "100",
            "calcium_hardness": "250",
            "temperature": "78"
        }
        
        errors = controller.validate_pool_data(pool_data)
        self.assertEqual(len(errors), 0, f"Validation errors: {errors}")
        
        # Test calculating chemicals
        result = controller.calculate_chemicals(pool_data)
        self.assertIsInstance(result, dict, "Calculation result should be a dictionary")
        self.assertIn("adjustments", result, "Result missing adjustments")
        self.assertIn("water_balance", result, "Result missing water balance")
        self.assertIn("ideal_ranges", result, "Result missing ideal ranges")
        
        # Test saving test results
        test_id = controller.save_test_results(pool_data)
        self.assertIsNotNone(test_id, "Failed to save test results")
        
        # Clean up
        db_service.close_all_connections()
        
        logger.info("PoolChemistryController tests passed")
    
    def test_pool_chemistry_app(self):
        """Test PoolChemistryApp initialization."""
        from app import PoolChemistryApp
        
        # Initialize application
        app = PoolChemistryApp("test_config.json")
        
        # Check that all components are initialized
        self.assertIsNotNone(app.db_service, "Database service not initialized")
        self.assertIsNotNone(app.chemical_safety_db, "Chemical safety database not initialized")
        self.assertIsNotNone(app.test_strip_analyzer, "Test strip analyzer not initialized")
        self.assertIsNotNone(app.weather_service, "Weather service not initialized")
        self.assertIsNotNone(app.controller, "Controller not initialized")
        
        # Clean up
        app.cleanup()
        
        logger.info("PoolChemistryApp initialization test passed")

def main():
    """Run the test suite."""
    unittest.main()

if __name__ == "__main__":
    main()
