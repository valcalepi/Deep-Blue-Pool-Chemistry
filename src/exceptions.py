# src/exceptions.py
"""
Custom exceptions for the pool management software.
"""
from typing import Optional # <--- ADD THIS LINE


class DataValidationError(Exception):
    """
    Exception raised for data validation errors.
    
    Attributes:
        message -- explanation of the error
    """
    
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)
        
        
class ConfigurationError(Exception):
    """
    Exception raised for configuration errors.
    
    Attributes:
        message -- explanation of the error
    """
    
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)
        
        
class ChemicalCalculationError(Exception):
    """
    Exception raised for errors in chemical calculations.
    
    Attributes:
        message -- explanation of the error
    """
    
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

class APIError(Exception):
    """
    Exception raised for errors during API calls.
    
    Attributes:
        message -- explanation of the error
        status_code -- HTTP status code (optional)
    """
    def __init__(self, message: str, status_code: Optional[int] = None):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)
