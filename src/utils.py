# C:\Scripts\Deep Blue scripts and files\pool_controller\src\utils.py

import os
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Union
import base64

# Try to import cryptography, but handle the case if it's not installed
try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    CRYPTOGRAPHY_AVAILABLE = True
except ImportError:
    CRYPTOGRAPHY_AVAILABLE = False
    print("Warning: cryptography package not installed. Encryption functions will not work.")

# Configure logging
logger = logging.getLogger(__name__)

def ensure_directory_exists(directory_path):
    """
    Ensure that a directory exists, creating it if necessary.
    
    Args:
        directory_path: Path to the directory
        
    Returns:
        Path object for the directory
    """
    path = Path(directory_path)
    path.mkdir(parents=True, exist_ok=True)
    return path

def generate_key():
    """
    Generate a new encryption key.
    
    Returns:
        bytes: New encryption key
    """
    if not CRYPTOGRAPHY_AVAILABLE:
        logger.error("Cannot generate key: cryptography package not installed")
        return None
        
    try:
        return Fernet.generate_key()
    except Exception as e:
        logger.error(f"Error generating encryption key: {str(e)}")
        return None

def encrypt_data(data, key):
    """
    Encrypt data using the provided key.
    
    Args:
        data: Data to encrypt (string or bytes)
        key: Encryption key (bytes)
        
    Returns:
        bytes: Encrypted data or None if encryption fails
    """
    if not CRYPTOGRAPHY_AVAILABLE:
        logger.error("Cannot encrypt data: cryptography package not installed")
        return None
        
    try:
        if not isinstance(key, bytes):
            logger.error("Encryption key must be bytes")
            return None
            
        f = Fernet(key)
        
        # Convert data to bytes if it's a string
        if isinstance(data, str):
            data = data.encode('utf-8')
            
        return f.encrypt(data)
    except Exception as e:
        logger.error(f"Error encrypting data: {str(e)}")
        return None

def decrypt_data(encrypted_data, key):
    """
    Decrypt encrypted data.
    
    Args:
        encrypted_data: Encrypted data (bytes)
        key: Encryption key (bytes)
        
    Returns:
        bytes or str: Decrypted data or None if decryption fails
    """
    if not CRYPTOGRAPHY_AVAILABLE:
        logger.error("Cannot decrypt data: cryptography package not installed")
        return None
        
    try:
        if not isinstance(key, bytes):
            logger.error("Encryption key must be bytes")
            return None
            
        f = Fernet(key)
        decrypted = f.decrypt(encrypted_data)
        
        # Try to decode as UTF-8, but return bytes if it fails
        try:
            return decrypted.decode('utf-8')
        except UnicodeDecodeError:
            return decrypted
    except Exception as e:
        logger.error(f"Error decrypting data: {str(e)}")
        return None

def save_json(data, file_path):
    """
    Save data to a JSON file.
    
    Args:
        data: Data to save
        file_path: Path to save the file
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Ensure the directory exists
        directory = os.path.dirname(file_path)
        if directory:
            os.makedirs(directory, exist_ok=True)
            
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, default=str)
        logger.debug(f"Data saved to {file_path}")
        return True
    except Exception as e:
        logger.error(f"Error saving JSON file: {str(e)}")
        return False

def load_json(file_path, default=None):
    """
    Load data from a JSON file.
    
    Args:
        file_path: Path to the JSON file
        default: Default value if file not found or invalid
        
    Returns:
        dict: Loaded data or default value
    """
    if default is None:
        default = {}
        
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.warning(f"File not found: {file_path}, using default")
        return default
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON in file: {file_path}")
        return default
    except Exception as e:
        logger.error(f"Error loading JSON file: {str(e)}")
        return default

def create_backup(source_path, backup_dir):
    """
    Create a backup of a file.
    
    Args:
        source_path: Path to the source file
        backup_dir: Directory to store backups
        
    Returns:
        str: Path to the backup file or None if backup failed
    """
    try:
        # Ensure backup directory exists
        os.makedirs(backup_dir, exist_ok=True)
        
        # Generate backup filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        source_filename = os.path.basename(source_path)
        backup_filename = f"{os.path.splitext(source_filename)[0]}_{timestamp}{os.path.splitext(source_filename)[1]}"
        backup_path = os.path.join(backup_dir, backup_filename)
        
        # Copy the file
        import shutil
        shutil.copy2(source_path, backup_path)
        
        logger.info(f"Backup created: {backup_path}")
        return backup_path
    except Exception as e:
        logger.error(f"Error creating backup: {str(e)}")
        return None

def format_timestamp(timestamp=None, format_str="%Y-%m-%d %H:%M:%S"):
    """
    Format a timestamp.
    
    Args:
        timestamp: Timestamp to format (default: current time)
        format_str: Format string
        
    Returns:
        str: Formatted timestamp
    """
    if timestamp is None:
        timestamp = datetime.now()
    elif isinstance(timestamp, (int, float)):
        timestamp = datetime.fromtimestamp(timestamp)
        
    return timestamp.strftime(format_str)

def parse_timestamp(timestamp_str, format_str="%Y-%m-%d %H:%M:%S"):
    """
    Parse a timestamp string.
    
    Args:
        timestamp_str: Timestamp string to parse
        format_str: Format string
        
    Returns:
        datetime: Parsed timestamp or None if parsing fails
    """
    try:
        return datetime.strptime(timestamp_str, format_str)
    except Exception as e:
        logger.error(f"Error parsing timestamp: {str(e)}")
        return None

# Add any other utility functions you need here
