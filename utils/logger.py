"""
Logging configuration for Deep Blue Pool Chemistry Management System.

This module sets up the logging system for the application, configuring
log levels, formats, and output destinations.
"""

import os
import sys
import logging
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from pathlib import Path
from typing import Optional, Dict, Any, Union


# Default logging configuration
DEFAULT_CONFIG = {
    "level": logging.INFO,
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "date_format": "%Y-%m-%d %H:%M:%S",
    "file": {
        "enabled": True,
        "path": "logs/pool_chemistry.log",
        "max_bytes": 10 * 1024 * 1024,  # 10 MB
        "backup_count": 5,
    },
    "console": {
        "enabled": True,
        "level": logging.INFO,
    },
    "timed": {
        "enabled": False,
        "path": "logs/daily/pool_chemistry_{date}.log",
        "when": "midnight",
        "interval": 1,
        "backup_count": 30,
    }
}


def setup_logger(config: Optional[Dict[str, Any]] = None) -> logging.Logger:
    """
    Set up and configure the application logger.
    
    Args:
        config: Optional custom logging configuration
        
    Returns:
        Configured root logger instance
    """
    # Merge provided config with defaults
    cfg = DEFAULT_CONFIG.copy()
    if config:
        # Update nested dictionaries
        for key, value in config.items():
            if isinstance(value, dict) and key in cfg and isinstance(cfg[key], dict):
                cfg[key].update(value)
            else:
                cfg[key] = value
    
