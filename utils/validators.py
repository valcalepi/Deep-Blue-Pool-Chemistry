# utils/validators.py
import re
from exceptions import DataValidationError

def validate_numeric_input(value, field_name, min_value=None, max_value=None):
    """
    Validate that a string input can be converted to a numeric value.
    
    Args:
        value (str): The input string to validate
        field_name (str): Name of the field for error reporting
        min_value (float, optional): Minimum allowed value
        max_value (float, optional): Maximum allowed value
        
    Returns:
        float: Converted numeric value
        
    Raises:
        DataValidationError: If validation fails
    """
    if not value.strip():
        raise DataValidationError(f"{field_name} cannot be empty")
    
    try:
        numeric_value = float(value)
    except ValueError:
        raise DataValidationError(f"{field_name} must be a numeric value", value)
        
    if min_value is not None and numeric_value < min_value:
        raise DataValidationError(
            f"{field_name} must be at least {min_value}", numeric_value
        )
        
    if max_value is not None and numeric_value > max_value:
        raise DataValidationError(
            f"{field_name} must not exceed {max_value}", numeric_value
        )
        
    return numeric_value

def validate_string_input(value, field_name, min_length=None, max_length=None):
    """
    Validate that a string input meets length requirements.
    
    Args:
        value (str): The input string to validate
        field_name (str): Name of the field for error reporting
        min_length (int, optional): Minimum allowed length
        max_length (int, optional): Maximum allowed length
        
    Returns:
        str: The validated string
        
    Raises:
        DataValidationError: If validation fails
    """
    if not isinstance(value, str):
        raise DataValidationError(f"{field_name} must be a string", value)
    
    if min_length is not None and len(value) < min_length:
        raise DataValidationError(
            f"{field_name} must be at least {min_length} characters long", value
        )
    
    if max_length is not None and len(value) > max_length:
        raise DataValidationError(
            f"{field_name} must not exceed {max_length} characters", value
        )
    
    return value

def validate_email_input(value, field_name):
    """
    Validate that a string input is a valid email address.
    
    Args:
        value (str): The email string to validate
        field_name (str): Name of the field for error reporting
        
    Returns:
        str: The validated email string
        
    Raises:
        DataValidationError: If validation fails
    """
    if not value.strip():
        raise DataValidationError(f"{field_name} cannot be empty")
    
    # Simple email pattern validation
    email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    if not re.match(email_pattern, value):
        raise DataValidationError(f"{field_name} must be a valid email address", value)
    
    return value

def validate_phone_input(value, field_name):
    """
    Validate that a string input is a valid phone number.
    
    Args:
        value (str): The phone number string to validate
        field_name (str): Name of the field for error reporting
        
    Returns:
        str: The validated phone number string
        
    Raises:
        DataValidationError: If validation fails
    """
    if not value.strip():
        raise DataValidationError(f"{field_name} cannot be empty")
    
    # Strip any non-digit characters for validation
    digits_only = ''.join(char for char in value if char.isdigit())
    
    # Check if we have a valid number of digits (typically 10 for US numbers)
    if len(digits_only) < 10:
        raise DataValidationError(
            f"{field_name} must contain at least 10 digits", value
        )
    
    # Return the original format the user entered
    return value
