# modules/utils.py
"""
Utilities Module
Contains utility functions for the Pool Chemistry Manager
"""

import logging
import os
import re
from datetime import datetime

def validate_float(value, default=None):
    """
    Validate and convert a string to float
    
    Args:
        value: String value to convert
        default: Default value if conversion fails
        
    Returns:
        Float value or default if conversion fails
    """
    if value is None or value.strip() == "":
        return default
    
    try:
        return float(value)
    except (ValueError, TypeError):
        return default

def validate_int(value, default=None):
    """
    Validate and convert a string to integer
    
    Args:
        value: String value to convert
        default: Default value if conversion fails
        
    Returns:
        Integer value or default if conversion fails
    """
    if value is None or value.strip() == "":
        return default
    
    try:
        return int(float(value))
    except (ValueError, TypeError):
        return default

def format_date(date_str, input_format="%Y-%m-%d", output_format="%m/%d/%Y"):
    """
    Format a date string
    
    Args:
        date_str: Date string to format
        input_format: Input date format
        output_format: Output date format
        
    Returns:
        Formatted date string
    """
    try:
        date_obj = datetime.strptime(date_str, input_format)
        return date_obj.strftime(output_format)
    except (ValueError, TypeError):
        return date_str

def sanitize_filename(filename):
    """
    Sanitize a filename by removing invalid characters
    
    Args:
        filename: Filename to sanitize
        
    Returns:
        Sanitized filename
    """
    # Replace invalid characters with underscore
    return re.sub(r'[\\/*?:"<>|]', "_", filename)

def ensure_dir(directory):
    """
    Ensure a directory exists
    
    Args:
        directory: Directory path
        
    Returns:
        True if directory exists or was created, False otherwise
    """
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
        return True
    except Exception as e:
        logging.error(f"Error creating directory {directory}: {e}")
        return False

def truncate_string(text, max_length=50, suffix="..."):
    """
    Truncate a string to a maximum length
    
    Args:
        text: String to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated
        
    Returns:
        Truncated string
    """
    if len(text) <= max_length:
        return text
    return text[:max_length-len(suffix)] + suffix

def parse_date_range(date_range):
    """
    Parse a date range string into start and end dates
    
    Args:
        date_range: Date range string (e.g., "Last 30 Days")
        
    Returns:
        Tuple of (start_date, end_date) as datetime objects
    """
    now = datetime.now()
    
    if date_range == "Last 7 Days":
        start_date = now - timedelta(days=7)
    elif date_range == "Last 30 Days":
        start_date = now - timedelta(days=30)
    elif date_range == "Last 90 Days":
        start_date = now - timedelta(days=90)
    elif date_range == "This Year":
        start_date = datetime(now.year, 1, 1)
    else:  # All Time or unknown
        start_date = datetime(1900, 1, 1)  # Far in the past
    
    return (start_date, now)