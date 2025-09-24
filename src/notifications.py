# src/notifications.py

import logging
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.utils import formatdate
from typing import List, Dict, Optional, Union, Any
from pathlib import Path
import json
from datetime import datetime
import os
import time
import requests
from cryptography.fernet import Fernet

logger = logging.getLogger(__name__)

class NotificationManager:
    """Manager for sending notifications via email and SMS"""
    
    def __init__(self, config_path: str = "data/settings.json"):
        """
        Initialize notification manager
        
        Args:
            config_path (str): Path to configuration file
        """
        try:
            self.config_path = Path(config_path)
            self.email_config = {}
            self.sms_config = {}
            self.notification_history = []
            self.max_history = 100  # Maximum number of notifications to keep in history
            
            # Load configuration if file exists
            if self.config_path.exists():
                self._load_config()
            else:
                logger.warning(f"Config file not found: {config_path}")
                
            # Initialize encryption
            self.key_file = Path("data/encryption.key")
            if not self.key_file.exists():
                self._generate_encryption_key()
            else:
                self._load_encryption_key()
                
            logger.info("Notification manager initialized")
            
        except Exception as e:
            logger.error(f"Error initializing notification manager: {str(e)}")
            raise
            
    def _load_config(self):
        """Load notification configuration from file"""
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
                
            # Extract email configuration
            if 'email_config' in config:
                encrypted_password = config['email_config'].get('app_password', '')
                if encrypted_password:
                    try:
                        password = self._decrypt_data(encrypted_password)
                        config['email_config']['app_password'] = password
                    except Exception as e:
                        logger.error(f"Error decrypting email password: {str(e)}")
                        config['email_config']['app_password'] = ''
                        
                self.email_config = config['email_config']
                
            # Extract SMS configuration
            if 'sms_config' in config:
                encrypted_token = config['sms_config'].get('auth_token', '')
                if encrypted_token:
                    try:
                        token = self._decrypt_data(encrypted_token)
                        config['sms_config']['auth_token'] = token
                    except Exception as e:
                        logger.error(f"Error decrypting SMS token: {str(e)}")
                        config['sms_config']['auth_token'] = ''
                        
                self.sms_config = config['sms_config']
                
            logger.debug("Notification configuration loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading notification configuration: {str(e)}")
            
    def _generate_encryption_key(self):
        """Generate and save encryption key"""
        try:
            key = Fernet.generate_key()
            self.key_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.key_file, 'wb') as f:
                f.write(key)
            self.cipher = Fernet(key)
            logger.debug("Encryption key generated")
            
        except Exception as e:
            logger.error(f"Error generating encryption key: {str(e)}")
            raise
            
    def _load_encryption_key(self):
        """Load encryption key from file"""
        try:
            with open(self.key_file, 'rb') as f:
                key = f.read()
            self.cipher = Fernet(key)
            logger.debug("Encryption key loaded")
            
        except Exception as e:
            logger.error(f"Error loading encryption key: {str(e)}")
            self._generate_encryption_key()  # Fallback to generating new key
            
    def _encrypt_data(self, data: str) -> str:
        """
        Encrypt sensitive data
        
        Args:
            data (str): Data to encrypt
            
        Returns:
            str: Encrypted data as string
        """
        try:
            return self.cipher.encrypt(data.encode()).decode()
        except Exception as e:
            logger.error(f"Error encrypting data: {str(e)}")
            raise
            
    def _decrypt_data(self, encrypted_data: str) -> str:
        """
        Decrypt sensitive data
        
        Args:
            encrypted_data (str): Encrypted data
            
        Returns:
            str: Decrypted data
        """
        try:
            return self.cipher.decrypt(encrypted_data.encode()).decode()
        except Exception as e:
            logger.error(f"Error decrypting data: {str(e)}")
            raise
            
    def save_email_config(self, email: str, password: str, smtp_server: str, 
                         smtp_port: int, use_ssl: bool = True):
        """
        Save email configuration with encrypted password
        
        Args:
            email (str): Email address
            password (str): App password
            smtp_server (str): SMTP server address
            smtp_port (int): SMTP port
            use_ssl (bool): Whether to use SSL
        """
        try:
            self.email_config = {
                'email': email,
                'app_password': password,  # Store unencrypted in memory
                'smtp_server': smtp_server,
                'smtp_port': smtp_port,
                'use_ssl': use_ssl
            }
            
            # Save to file with encrypted password
            config = self._get_full_config()
            config['email_config'] = self.email_config.copy()
            config['email_config']['app_password'] = self._encrypt_data(password)
            
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=4)
                
            logger.info("Email configuration saved")
            
        except Exception as e:
            logger.error(f"Error saving email configuration: {str(e)}")
            raise
            
    def save_sms_config(self, account_sid: str, auth_token: str, twilio_number: str):
        """
        Save SMS configuration with encrypted token
        
        Args:
            account_sid (str): Twilio account SID
            auth_token (str): Twilio auth token
            twilio_number (str): Twilio phone number
        """
        try:
            self.sms_config = {
                'account_sid': account_sid,
                'auth_token': auth_token,  # Store unencrypted in memory
                'twilio_number': twilio_number
            }
            
            # Save to file with encrypted token
            config = self._get_full_config()
            config['sms_config'] = self.sms_config.copy()
            config['sms_config']['auth_token'] = self._encrypt_data(auth_token)
            
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=4)
                
            logger.info("SMS configuration saved")
            
        except Exception as e:
            logger
