# tests/test_water_tester.py
import unittest
from models.water_tester import WaterTester  # Try this import path
# If the above doesn't work, try these alternatives:
# from pool_controller.models.water_tester import WaterTester
# import sys; sys.path.append('..'); from pool_controller.models.water_tester import WaterTester

class TestWaterTester(unittest.TestCase):
    """Tests for the WaterTester class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.tester = WaterTester()
        self.tester.set_pool_volume(10000)
    
    def test_calculate_ph_dosage(self):
        """Test pH dosage calculation."""
        # Test normal case
        result = self.tester._calculate_ph_dosage(0.5)
        self.assertIn("2.50 lbs", result)
        
        # Test small dosage (under 1 lb)
        result = self.tester._calculate_ph_dosage(0.1)
        self.assertIn("oz", result)
        
        # Test zero dosage
        result = self.tester._calculate_ph_dosage(0)
        self.assertIn("No adjustment needed", result)
        
        # Test negative value (should be handled gracefully)
        result = self.tester._calculate_ph_dosage(-0.1)
        self.assertIn("No adjustment needed", result)

if __name__ == "__main__":
    unittest.main()

