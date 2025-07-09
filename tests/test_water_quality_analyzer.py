# /tests/test_water_quality_analyzer.py
import unittest
from unittest.mock import MagicMock
from services.water_quality_analyzer import WaterQualityAnalyzer

class TestWaterQualityAnalyzer(unittest.TestCase):
    """Tests for the new WaterQualityAnalyzer feature."""
    
    def setUp(self):
        """Set up test environment."""
        self.analyzer = WaterQualityAnalyzer()
    
    def test_analyze_water_quality_good(self):
        """Test water quality analysis with good parameters."""
        # Good water quality parameters
        parameters = {
            'ph': 7.4,
            'chlorine': 3.0,
            'alkalinity': 120
        }
        
        result = self.analyzer.analyze_quality(parameters)
        
        self.assertEqual(result['status'], 'good')
        self.assertGreaterEqual(result['score'], 90)
    
    def test_analyze_water_quality_poor(self):
        """Test water quality analysis with poor parameters."""
        # Poor water quality parameters
        parameters = {
            'ph': 8.5,
            'chlorine': 0.5,
            'alkalinity': 50
        }
        
        result = self.analyzer.analyze_quality(parameters)
        
        self.assertEqual(result['status'], 'poor')
        self.assertLess(result['score'], 60)
    
    def test_get_recommendations(self):
        """Test recommendations for water quality improvement."""
        # Poor water quality parameters
        parameters = {
            'ph': 8.5,
            'chlorine': 0.5,
            'alkalinity': 50
        }
        
        recommendations = self.analyzer.get_recommendations(parameters)
        
        self.assertIsInstance(recommendations, list)
        self.assertGreater(len(recommendations), 0)
        # Check for specific recommendations
        self.assertTrue(any('pH' in r for r in recommendations))
        self.assertTrue(any('chlorine' in r for r in recommendations))
