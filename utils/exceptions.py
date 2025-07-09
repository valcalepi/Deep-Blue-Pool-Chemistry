"""
Custom exceptions for Deep Blue Pool Chemistry Management System.

This module defines custom exception classes used throughout the application
to provide clear and specific error handling.
"""

from typing import Optional


class PoolChemistryError(Exception):
    """Base exception class for all Pool Chemistry Management System errors."""
    
    def __init__(self, message: str, code: Optional[int] = None):
        self.message = message
        self.code = code
        super().__init__(self.message)


class ConfigurationError(PoolChemistryError):
    """Exception raised for errors in the configuration."""
    
    def __init__(self, message: str, code: Optional[int] = None):
        super().__init__(f"Configuration Error: {message}", code or 100)


class DatabaseError(PoolChemistryError):
    """Exception raised for errors interacting with the database."""
    
    def __init__(self, message: str, code: Optional[int] = None):
        super().__init__(f"Database Error: {message}", code or 200)


class ServiceError(PoolChemistryError):
    """Exception raised for errors in external services."""
    
    def __init__(self, message: str, code: Optional[int] = None):
        super().__init__(f"Service Error: {message}", code or 300)


class AnalysisError(PoolChemistryError):
    """Exception raised for errors in chemical analysis."""
    
    def __init__(self, message: str, code: Optional[int] = None):
        super().__init__(f"Analysis Error: {message}", code or 400)


class SensorError(PoolChemistryError):
    """Exception raised for errors with hardware sensors."""
    
    def __init__(self, message: str, code: Optional[int] = None):
        super().__init__(f"Sensor Error: {message}", code or 500)


class ArduinoConnectionError(PoolChemistryError):
    """Exception raised for errors connecting to Arduino devices."""
    
    def __init__(self, message: str, code: Optional[int] = None):
        super().__init__(f"Arduino Connection Error: {message}", code or 600)


class ValidationError(PoolChemistryError):
    """Exception raised for validation errors in input data."""
    
    def __init__(self, message: str, code: Optional[int] = None):
        super().__init__(f"Validation Error: {message}", code or 700)


class AuthorizationError(PoolChemistryError):
    """Exception raised for authorization and permission errors."""
    
    def __init__(self, message: str, code: Optional[int] = None):
        super().__init__(f"Authorization Error: {message}", code or 800)


class FileOperationError(PoolChemistryError):
    """Exception raised for errors in file operations."""
    
    def __init__(self, message: str, code: Optional[int] = None):
        super().__init__(f"File Operation Error: {message}", code or 900)
