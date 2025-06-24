# tests/test_water_tester.py
import pytest
from models.water_tester import WaterTester

def test_calculate_ph_dosage():
    """Test pH dosage calculation."""
    tester = WaterTester()
    tester.set_pool_volume(10000)
    
    # Test normal case
    result = tester._calculate_ph_dosage(0.5)
    assert "2.50 lbs" in result
    
    # Test small dosage (under 1 lb)
    result = tester._calculate_ph_dosage(0.1)
    assert "oz" in result
    
    # Test zero dosage
    result = tester._calculate_ph_dosage(0)
    assert "No adjustment needed" in result
    
    # Test negative value (should be handled gracefully)
    result = tester._calculate_ph_dosage(-0.1)
    assert "No adjustment needed" in result
