import unittest
from pool_controller import PoolController
from models.chemical_calculator import ChemicalCalculator
from database.database_connection import DatabaseConnection

class TestPoolController(unittest.TestCase):
    def setUp(self):
        self.controller = PoolController()
        self.calculator = ChemicalCalculator()
        self.db = DatabaseConnection()
        
    def test_set_pool_type(self):
        # Test valid pool type
        self.controller.set_pool_type("Concrete")
        self.assertEqual(self.controller.current_pool_type, "Concrete")
        
        # Test invalid pool type
        with self.assertRaises(ValueError):
            self.controller.set_pool_type("Invalid")
    
    def test_get_ideal_range(self):
        # Test pH range
        self.assertEqual(self.calculator.get_ideal_range("ph"), (7.2, 7.8))
        
        # Test calcium hardness range with specified pool type
        self.assertEqual(self.calculator.get_ideal_range("calcium_hardness", "Vinyl"), (175, 225))
        
        # Test calcium hardness range with current pool type
        self.calculator.set_pool_type("Fiberglass")
        self.assertEqual(self.calculator.get_ideal_range("calcium_hardness"), (150, 250))
        
        # Test unknown parameter
        self.assertEqual(self.calculator.get_ideal_range("unknown"), (0, 0))
    
    def test_calculate_adjustments(self):
        # Test adjustments for values below ideal range
        adjustments = self.calculator.calculate_adjustments(
            "Concrete", 7.0, 0.5, 60, 150
        )
        self.assertIn("Increase", adjustments["pH"])
        self.assertIn("Add", adjustments["Chlorine"])
        self.assertIn("Add", adjustments["Alkalinity"])
        self.assertIn("Add", adjustments["Calcium Hardness"])
        
        # Test adjustments for values within ideal range
        adjustments = self.calculator.calculate_adjustments(
            "Concrete", 7.4, 2.0, 100, 300
        )
        self.assertEqual(adjustments["pH"], "No adjustment needed")
        self.assertEqual(adjustments["Chlorine"], "No adjustment needed")
        self.assertEqual(adjustments["Alkalinity"], "No adjustment needed")
        self.assertEqual(adjustments["Calcium Hardness"], "No adjustment needed")
        
        # Test adjustments for values above ideal range
        adjustments = self.calculator.calculate_adjustments(
            "Concrete", 8.0, 4.0, 140, 500
        )
        self.assertIn("Decrease", adjustments["pH"])
        self.assertIn("Allow chlorine levels", adjustments["Chlorine"])
        self.assertIn("Add", adjustments["Alkalinity"])
        self.assertIn("drain and refill", adjustments["Calcium Hardness"])

if __name__ == "__main__":
    unittest.main()
