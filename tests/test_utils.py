# tests/test_utils.py
import pytest
from utils.calculation_helpers import calculate_langelier_saturation_index
from utils.validators import validate_numeric_input
from exceptions import DataValidationError

class TestCalculationHelpers:
    """Tests for the calculation helper functions."""
    
    def test_calculate_lsi_normal_case(self):
        """Test LSI calculation with normal inputs."""
        lsi = calculate_langelier_saturation_index(
            pH=7.5,
            temperature=78,
            calcium_hardness=300,
            total_alkalinity=100
        )
        # LSI should be within a reasonable range
        assert -1.0 <= lsi <= 1.0
        
    def test_calculate_lsi_edge_cases(self):
        """Test LSI calculation with edge case inputs."""
        # Minimum valid values
        lsi_min = calculate_langelier_saturation_index(
            pH=6.0,
            temperature=32,
            calcium_hardness=10,
            total_alkalinity=10
        )
        assert isinstance(lsi_min, float)
        
        # Maximum valid values
        lsi_max = calculate_langelier_saturation_index(
            pH=9.0,
            temperature=105,
            calcium_hardness=1000,
            total_alkalinity=500,
            total_dissolved_solids=5000
        )
        assert isinstance(lsi_max, float)
        
    def test_calculate_lsi_invalid_inputs(self):
        """Test LSI calculation with invalid inputs."""
        # pH too low
        with pytest.raises(ValueError):
            calculate_langelier_saturation_index(
                pH=5.9,  # Below minimum of 6.0
                temperature=78,
                calcium_hardness=300,
                total_alkalinity=100
            )
            
        # pH too high
        with pytest.raises(ValueError):
            calculate_langelier_saturation_index(
                pH=9.1,  # Above maximum of 9.0
                temperature=78,
                calcium_hardness=300,
                total_alkalinity=100
            )
            
        # Negative calcium hardness
        with pytest.raises(ValueError):
            calculate_langelier_saturation_index(
                pH=7.5,
                temperature=78,
                calcium_hardness=-10,  # Must be positive
                total_alkalinity=100
            )

class TestValidators:
    """Tests for the validator functions."""
    
    def test_validate_numeric_input_normal(self):
        """Test numeric input validation with normal inputs."""
        # Valid integer
        result = validate_numeric_input("100", "Test Field")
        assert result == 100.0
        
        # Valid float
        result = validate_numeric_input("7.5", "Test Field")
        assert result == 7.5
        
    def test_validate_numeric_input_with_range(self):
        """Test numeric input validation with range constraints."""
        # Within range
        result = validate_numeric_input("7.5", "pH", min_value=7.0, max_value=8.0)
        assert result == 7.5
        
        # Below minimum
        with pytest.raises(DataValidationError) as excinfo:
            validate_numeric_input("6.9", "pH", min_value=7.0, max_value=8.0)
        assert "must be at least 7.0" in str(excinfo.value)
        
        # Above maximum
        with pytest.raises(DataValidationError) as excinfo:
            validate_numeric_input("8.1", "pH", min_value=7.0, max_value=8.0)
        assert "must not exceed 8.0" in str(excinfo.value)
        
    def test_validate_numeric_input_invalid(self):
        """Test numeric input validation with invalid inputs."""
        # Empty string
        with pytest.raises(DataValidationError) as excinfo:
            validate_numeric_input("", "Test Field")
        assert "cannot be empty" in str(excinfo.value)
        
        # Non-numeric string
        with pytest.raises(DataValidationError) as excinfo:
            validate_numeric_input("abc", "Test Field")
        assert "must be a numeric value" in str(excinfo.value)
        
        # Mixed content
        with pytest.raises(DataValidationError) as excinfo:
            validate_numeric_input("7.5abc", "Test Field")
        assert "must be a numeric value" in str(excinfo.value)
