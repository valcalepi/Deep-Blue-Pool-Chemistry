# exceptions.py

from typing import Any

class DataValidationError(ValueError):
    """
    Custom exception raised when data validation fails.
    Inherits from ValueError.
    """
    def __init__(self, message: str, value: Any = None):
        super().__init__(message)
        self.message = message
        self.value = value
        
    def __str__(self):
        if self.value is not None:
            return f"{self.message} (Invalid value: {self.value})"
        return self.message
