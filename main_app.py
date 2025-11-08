"""
Deep Blue Pool Chemistry Management System v3.8.2
Copyright (c) 2024 Michael Hayes. All rights reserved.

This software is proprietary and confidential.
Unauthorized copying, distribution, or use is strictly prohibited.

Owner: Michael Hayes

Version 3.8.2 - Critical Health Score &amp; ORP Fixes
- Fixed health score calculation to match safety alerts
- Added ORP monitoring to safety system
- Enhanced bromine support
- Ensured consistency between alerts and health scores
"""

# main_app.py

import os
import sys
import json
import time
import logging
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import urllib3
import requests
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image, ImageTk
import csv
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.utils import formatdate
import openpyxl
from reportlab.lib.pagesizes import letter, inch
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

# Check if matplotlib is available
try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.dates import DateFormatter
    import matplotlib.dates as mdates
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("[WARNING] Matplotlib not available - charts will not be generated")

# Check if ReportLab is available
try:
    from reportlab.platypus import SimpleDocTemplate
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    print("[WARNING] ReportLab not available - PDF generation will not work")


# ReportLab availability flag
REPORTLAB_AVAILABLE = True
import zipfile
import uuid

# --- START: Environment Variable Loading ---
from dotenv import load_dotenv
import io
from tkinter import colorchooser

dotenv_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=dotenv_path)
# --- END: Environment Variable Loading ---

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Constants (with fallbacks)

# Chemical Safety Information
CHEMICAL_SAFETY = {
    "ph": {
        "increase": {
            "chemical": "Soda Ash (Sodium Carbonate)",
            "warnings": [
                "CAUTION: Wear protective gloves and safety goggles",
                "Avoid breathing dust - use in well-ventilated area",
                "Do not mix with acids - can cause violent reaction",
                "Add chemical to water, NEVER water to chemical"
            ],
            "precautions": [
                "Store in cool, dry place away from acids",
                "Keep container tightly closed when not in use",
                "Wash hands thoroughly after handling",
                "In case of skin contact, rinse immediately with water"
            ]
        },
        "decrease": {
            "chemical": "Muriatic Acid (Hydrochloric Acid)",
            "warnings": [
                "DANGER: Highly corrosive - wear protective equipment",
                "NEVER mix with chlorine products - creates toxic gas",
                "Add acid to water slowly, NEVER water to acid",
                "Use in well-ventilated area - avoid breathing fumes"
            ],
            "precautions": [
                "Store away from chlorine and other pool chemicals",
                "Keep out of reach of children and pets",
                "Have baking soda nearby to neutralize spills",
                "If splashed in eyes, flush with water for 15 minutes and seek medical attention"
            ]
        }
    },
    "chlorine": {
        "increase": {
            "chemical": "Liquid Chlorine or Chlorine Tablets",
            "warnings": [
                "CAUTION: Strong oxidizer - keep away from flammable materials",
                "NEVER mix with acids - creates toxic chlorine gas",
                "Wear gloves and avoid skin contact",
                "Do not swim for at least 30 minutes after adding"
            ],
            "precautions": [
                "Store in cool, dry, well-ventilated area",
                "Keep away from direct sunlight",
                "Never mix different types of chlorine",
                "Test water before swimming to ensure safe levels"
            ]
        },
        "decrease": {
            "chemical": "Sodium Thiosulfate (Chlorine Neutralizer)",
            "warnings": [
                "Use sparingly - can lower chlorine too much",
                "Test water frequently when reducing chlorine",
                "Alternative: Allow natural dissipation with sunlight"
            ],
            "precautions": [
                "Add small amounts and retest",
                "Wait 4 hours before retesting chlorine levels",
                "Ensure proper circulation while treating"
            ]
        }
    },
    "alkalinity": {
        "increase": {
            "chemical": "Sodium Bicarbonate (Baking Soda)",
            "warnings": [
                "CAUTION: Wear dust mask when handling powder",
                "Add slowly to avoid clouding water",
                "Can raise pH slightly - monitor both levels"
            ],
            "precautions": [
                "Dissolve in bucket of water before adding to pool",
                "Distribute evenly around pool perimeter",
                "Wait 6 hours before retesting"
            ]
        },
        "decrease": {
            "chemical": "Muriatic Acid",
            "warnings": [
                "DANGER: See pH decrease warnings above",
                "Lowers both alkalinity and pH",
                "Add in small increments"
            ],
            "precautions": [
                "See pH decrease precautions",
                "Monitor both alkalinity and pH levels",
                "Allow 24 hours between treatments"
            ]
        }
    },
    "calcium_hardness": {
        "increase": {
            "chemical": "Calcium Chloride",
            "warnings": [
                "CAUTION: Generates heat when dissolved",
                "Add slowly to avoid hot spots",
                "Wear protective gloves"
            ],
            "precautions": [
                "Pre-dissolve in bucket of water",
                "Pour slowly around pool perimeter",
                "Run pump for 24 hours after adding",
                "Wait 4 hours before retesting"
            ]
        },
        "decrease": {
            "chemical": "Partial Water Drain and Refill",
            "warnings": [
                "Drain no more than 1/3 of pool water at a time",
                "Never drain pool completely (can damage structure)",
                "Check local regulations for water disposal"
            ],
            "precautions": [
                "Test new water before adding to pool",
                "Rebalance all chemicals after refilling",
                "Allow water to circulate for 24 hours"
            ]
        }
    },
    "cyanuric_acid": {
        "increase": {
            "chemical": "Cyanuric Acid (Stabilizer)",
            "warnings": [
                "CAUTION: Dissolves slowly - be patient",
                "Too much can reduce chlorine effectiveness",
                "Cannot be reduced except by dilution"
            ],
            "precautions": [
                "Add to skimmer basket with pump running",
                "Or pre-dissolve in bucket of warm water",
                "Wait 7 days before retesting",
                "Never exceed 100 ppm"
            ]
        }
    }
}

# Threshold definitions for test strips
CHEMICAL_THRESHOLDS = {
    "ph": {
        "min": 7.2,
        "max": 7.8,
        "ideal": 7.4,
        "unit": "",
        "name": "pH"
    },
    "free_chlorine": {
        "min": 1.0,
        "max": 3.0,
        "ideal": 2.0,
        "unit": "ppm",
        "name": "Free Chlorine"
    },
    "total_chlorine": {
        "min": 1.0,
        "max": 3.0,
        "ideal": 2.0,
        "unit": "ppm",
        "name": "Total Chlorine"
    },
    "alkalinity": {
        "min": 80,
        "max": 120,
        "ideal": 100,
        "unit": "ppm",
        "name": "Total Alkalinity"
    },
    "calcium_hardness": {
        "min": 200,
        "max": 400,
        "ideal": 300,
        "unit": "ppm",
        "name": "Calcium Hardness"
    },
    "cyanuric_acid": {
        "min": 30,
        "max": 50,
        "ideal": 40,
        "unit": "ppm",
        "name": "Cyanuric Acid"
    },
    "salt": {
        "min": 2700,
        "max": 3400,
        "ideal": 3000,
        "unit": "ppm",
        "name": "Salt"
    },
    "bromine": {
        "min": 3.0,
        "max": 5.0,
        "ideal": 4.0,
        "unit": "ppm",
        "name": "Bromine"
    }
}

DEFAULT_WINDOW_SIZE = (1400, 1000)
MIN_WINDOW_SIZE = (800, 600)
WEATHER_API_KEY_NAME = os.environ.get("WEATHER_API_KEY")
COLOR_SCHEME = {
    'primary': "#2196F3",
    'secondary': "#BBDEFB",
    'success': "#4CAF50",
    'warning': "#FFC107",
    'danger': "#F44336",
    'info': "#03A9F4",
    'background': "#F5F5F5"
}

# Utility Functions (with fallbacks)
def generate_key():
    """Fallback key generation function"""
    import os
    return os.urandom(32)

def encrypt_data(data, key):
    """SECURE encryption function - CRITICAL FIX"""
    try:
        from cryptography.fernet import Fernet
        import base64
        import os
        
        # Use proper Fernet key format
        if isinstance(key, str):
            # If it's a string, convert to proper Fernet key
            key = key.encode('utf-8')
            if len(key) != 44:
                key = Fernet.generate_key()  # Generate proper key
        elif isinstance(key, bytes):
            if len(key) != 44:
                key = Fernet.generate_key()  # Generate proper key
        
        cipher = Fernet(key)
        
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        encrypted = cipher.encrypt(data)
        return base64.urlsafe_b64encode(encrypted).decode('utf-8')
        
    except ImportError:
        # XOR encryption fallback if cryptography not available
        logger.warning("Using XOR encryption fallback (better than no encryption)")
        if isinstance(data, str):
            data = data.encode('utf-8')
        xor_key = b'SecurePoolChemistry2024'
        result = bytearray()
        for i, byte in enumerate(data):
            result.append(byte ^ xor_key[i % len(xor_key)])
        return base64.b64encode(result).decode('utf-8')
    except Exception as e:
        logger.error(f"Encryption failed: {e}")
        return data  # Ultimate fallback

def decrypt_data(data, key):
    """SECURE decryption function - CRITICAL FIX"""
    try:
        from cryptography.fernet import Fernet
        import base64
        
        # Use proper Fernet key format
        if isinstance(key, str):
            key = key.encode('utf-8')
            if len(key) != 44:
                # For testing, we'll need to handle this case
                return "DECRYPTION_ERROR: Invalid key format"
        elif isinstance(key, bytes):
            if len(key) != 44:
                return "DECRYPTION_ERROR: Invalid key format"
        
        cipher = Fernet(key)
        
        if isinstance(data, str):
            data = base64.urlsafe_b64decode(data.encode('utf-8'))
        
        decrypted = cipher.decrypt(data)
        return decrypted.decode('utf-8')
        
    except ImportError:
        # XOR decryption fallback if cryptography not available
        logger.warning("Using XOR decryption fallback (better than no decryption)")
        try:
            if isinstance(data, str):
                data = base64.b64decode(data.encode('utf-8'))
            xor_key = b'SecurePoolChemistry2024'
            result = bytearray()
            for i, byte in enumerate(data):
                result.append(byte ^ xor_key[i % len(xor_key)])
            return result.decode('utf-8')
        except:
            return str(data)  # Ultimate fallback
    except Exception as e:
        logger.error(f"Decryption failed: {e}")
        return data  # Ultimate fallback

def save_json(data, file_path):
    """Fallback JSON save function"""
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=4)
        return True
    except Exception as e:
        logger.error(f"Error saving JSON: {e}")
        return False

def load_json(file_path, default=None):
    """Fallback JSON load function"""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError, PermissionError, IOError):
        return default or {}

def create_backup(source_path, backup_dir):
    """Fallback backup function"""
    try:
        import shutil
        os.makedirs(backup_dir, exist_ok=True)
        backup_file = os.path.join(backup_dir, os.path.basename(source_path))
        shutil.copy2(source_path, backup_file)
        return backup_file
    except Exception as e:
        logger.error(f"Error creating backup: {e}")
        return None

# Import other modules (with fallbacks)

# ==================== ML LIBRARY IMPORTS ====================
# Try to import ML libraries with fallback
ML_AVAILABLE = False
try:
    from sklearn.preprocessing import StandardScaler
    from sklearn.ensemble import IsolationForest
    from sklearn.linear_model import LinearRegression
    from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
    from statsmodels.tsa.arima.model import ARIMA
    import joblib
    ML_AVAILABLE = True
    print("ML libraries loaded successfully")
except ImportError as e:
    print(f"ML libraries not available: {e}")
    print("ML Analytics will use fallback mode")
    # Define dummy classes for fallback
    class StandardScaler:
        def fit_transform(self, X): return X
        def transform(self, X): return X
    class IsolationForest:
        def __init__(self, **kwargs): pass
        def fit(self, X): pass
        def predict(self, X): return [1] * len(X)
    class LinearRegression:
        def __init__(self): pass
        def fit(self, X, y): pass
        def predict(self, X): return [0] * len(X)
    class ARIMA:
        def __init__(self, *args, **kwargs): pass
        def fit(self): return self
        def forecast(self, steps): return [0] * steps
    def mean_squared_error(y_true, y_pred): return 0.0
    def mean_absolute_error(y_true, y_pred): return 0.0
    def r2_score(y_true, y_pred): return 0.0
    class joblib:
        @staticmethod
        def dump(*args, **kwargs): pass
        @staticmethod
        def load(*args, **kwargs): return None



# ==================== ML ANALYTICS ENGINE V2 ====================
# Integrated from ml_analytics_engine_v2.py
# Copyright © 2024 Michael Hayes. All Rights Reserved.

class PoolAnalyticsEngineV2:
    """
    Advanced Machine Learning Analytics Engine for Pool Chemistry
    
    This engine provides true ML capabilities including:
    - ARIMA time series forecasting
    - Isolation Forest anomaly detection
    - Polynomial trend analysis
    - Model persistence and evaluation
    - Comprehensive data validation
    """
    
    def __init__(self, models_dir: str = "models"):
        """
        Initialize the ML Analytics Engine
        
        Args:
            models_dir: Directory to save/load trained models
        """
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(exist_ok=True)
        
        # ML models and scalers
        self.arima_models = {}
        self.anomaly_detector = None
        self.scaler = StandardScaler() if ML_AVAILABLE else None
        
        # Configuration
        self.parameters = [
            'ph', 'free_chlorine', 'total_chlorine', 
            'alkalinity', 'calcium_hardness', 'cyanuric_acid',
            'temperature', 'bromine', 'salt'
        ]
        
        # Ideal ranges for each parameter
        self.ideal_ranges = {
            'ph': (7.2, 7.6),
            'free_chlorine': (1.0, 3.0),
            'total_chlorine': (1.0, 3.0),
            'alkalinity': (80, 120),
            'calcium_hardness': (200, 400),
            'cyanuric_acid': (30, 50),
            'temperature': (78, 82),
            'bromine': (2.0, 4.0),
            'salt': (2700, 3400)
        }
        
        # Chemical costs (per pound/gallon) - user configurable
        self.chemical_costs = {
            'soda_ash': 8.00,
            'muriatic_acid': 10.00,
            'chlorine': 4.00,
            'baking_soda': 6.00,
            'calcium_chloride': 12.00,
            'stabilizer': 15.00,
            'bromine': 18.00,
            'salt': 0.50
        }
        
        # Performance tracking
        self.prediction_accuracy = {}
        self.model_performance = {}
        
        # Load existing models if available
        self.load_models()
        
        logger.info("ML Analytics Engine V2 initialized")
    
    # ==================== DATA VALIDATION ====================
    
    def validate_reading(self, reading: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate a single reading for data quality
        
        Args:
            reading: Dictionary containing pool chemistry readings
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        if not isinstance(reading, dict):
            return False, ["Reading must be a dictionary"]
        
        # Check for required fields
        required_fields = ['ph', 'free_chlorine', 'total_chlorine']
        for field in required_fields:
            if field not in reading:
                errors.append(f"Missing required field: {field}")
        
        # Validate numeric values
        for param in self.parameters:
            if param in reading:
                value = reading[param]
                
                # Check type
                if not isinstance(value, (int, float)):
                    try:
                        value = float(value)
                    except (ValueError, TypeError):
                        errors.append(f"{param}: Invalid type (must be numeric)")
                        continue
                
                # Check range
                if value < 0:
                    errors.append(f"{param}: Negative value not allowed")
                elif value > 10000:
                    errors.append(f"{param}: Value too large (max 10000)")
                
                # Check specific parameter ranges
                if param == 'ph' and (value < 0 or value > 14):
                    errors.append(f"pH must be between 0 and 14")
                elif param == 'temperature' and (value < 32 or value > 120):
                    errors.append(f"Temperature must be between 32°FF and 120°FF")
        
        # Validate date if present
        if 'date' in reading:
            try:
                if isinstance(reading['date'], str):
                    datetime.strptime(reading['date'], '%Y-%m-%d')
            except ValueError:
                errors.append("Invalid date format (use YYYY-MM-DD)")
        
        is_valid = len(errors) == 0
        return is_valid, errors
    
    def clean_and_validate_data(self, readings: List[Dict]) -> Tuple[List[Dict], List[str]]:
        """
        Clean and validate a list of readings
        
        Args:
            readings: List of reading dictionaries
            
        Returns:
            Tuple of (cleaned_readings, validation_errors)
        """
        if not readings:
            return [], ["No readings provided"]
        
        if not isinstance(readings, list):
            return [], ["Readings must be a list"]
        
        cleaned = []
        all_errors = []
        
        for i, reading in enumerate(readings):
            is_valid, errors = self.validate_reading(reading)
            
            if is_valid:
                cleaned.append(reading)
            else:
                all_errors.append(f"Reading {i+1}: {', '.join(errors)}")
        
        logger.info(f"Validated {len(readings)} readings: {len(cleaned)} valid, {len(all_errors)} errors")
        
        return cleaned, all_errors
    
    def sanitize_value(self, value: Any, param: str) -> Optional[float]:
        """
        Sanitize and convert a value to float
        
        Args:
            value: Value to sanitize
            param: Parameter name for context
            
        Returns:
            Sanitized float value or None if invalid
        """
        try:
            if value is None:
                return None
            
            # Convert to float
            float_val = float(value)
            
            # Check for NaN or infinity
            if np.isnan(float_val) or np.isinf(float_val):
                logger.warning(f"Invalid value for {param}: {value}")
                return None
            
            # Apply reasonable bounds
            if float_val < 0 or float_val > 10000:
                logger.warning(f"Out of range value for {param}: {float_val}")
                return None
            
            return float_val
            
        except (ValueError, TypeError) as e:
            logger.warning(f"Could not convert {param} value '{value}': {e}")
            return None
    
    # ==================== PREDICTIONS (ARIMA) ====================
    
    def predict_next_readings(self, historical_data: List[Dict]) -> Dict[str, Any]:
        """
        Predict next readings using ARIMA time series forecasting
        
        Args:
            historical_data: List of historical readings
            
        Returns:
            Dictionary with predictions and confidence intervals
        """
        if not ML_AVAILABLE:
            logger.warning("ML libraries not available - using fallback method")
            return self._predict_fallback(historical_data)
        
        # Validate and clean data
        cleaned_data, errors = self.clean_and_validate_data(historical_data)
        
        if len(cleaned_data) < 20:
            logger.warning(f"Insufficient data for ARIMA: {len(cleaned_data)} readings (need 20+)")
            return self._predict_fallback(cleaned_data)
        
        predictions = {}
        
        for param in self.parameters:
            try:
                # Extract time series
                values = []
                for reading in cleaned_data:
                    val = self.sanitize_value(reading.get(param), param)
                    if val is not None:
                        values.append(val)
                
                if len(values) < 20:
                    logger.debug(f"Skipping {param}: insufficient data ({len(values)} values)")
                    continue
                
                # Fit ARIMA model (1,1,1) - can be tuned
                model = ARIMA(values, order=(1, 1, 1))
                fitted = model.fit()
                
                # Forecast next value with 95% confidence interval
                forecast = fitted.forecast(steps=1)
                forecast_obj = fitted.get_forecast(steps=1)
                conf_int = forecast_obj.conf_int()
                
                # Handle both DataFrame and array returns
                if hasattr(conf_int, 'iloc'):
                    lower = float(conf_int.iloc[0, 0])
                    upper = float(conf_int.iloc[0, 1])
                else:
                    lower = float(conf_int[0][0])
                    upper = float(conf_int[0][1])
                
                predictions[param] = {
                    'value': float(forecast[0]),
                    'lower_bound': lower,
                    'upper_bound': upper,
                    'confidence': 0.95,
                    'method': 'ARIMA(1,1,1)',
                    'data_points': len(values)
                }
                
                # Store model for later use
                self.arima_models[param] = fitted
                
                logger.debug(f"ARIMA prediction for {param}: {forecast[0]:.2f}")
                
            except Exception as e:
                logger.error(f"ARIMA failed for {param}: {e}")
                # Fallback to simple method for this parameter
                fallback = self._predict_single_param_fallback(cleaned_data, param)
                if fallback:
                    predictions[param] = fallback
        
        if predictions:
            logger.info(f"Generated ARIMA predictions for {len(predictions)} parameters")
        else:
            logger.warning("No ARIMA predictions generated - using fallback")
            return self._predict_fallback(cleaned_data)
        
        return predictions
    
    def _predict_fallback(self, historical_data: List[Dict]) -> Dict[str, Any]:
        """
        Fallback prediction method using exponential moving average
        
        Args:
            historical_data: List of historical readings
            
        Returns:
            Dictionary with predictions
        """
        if not historical_data or len(historical_data) < 3:
            return {}
        
        predictions = {}
        
        for param in self.parameters:
            fallback = self._predict_single_param_fallback(historical_data, param)
            if fallback:
                predictions[param] = fallback
        
        return predictions
    
    def _predict_single_param_fallback(self, historical_data: List[Dict], param: str) -> Optional[Dict]:
        """
        Predict single parameter using exponential moving average
        
        Args:
            historical_data: List of historical readings
            param: Parameter to predict
            
        Returns:
            Prediction dictionary or None
        """
        try:
            # Extract values
            values = []
            recent_data = historical_data[-10:] if len(historical_data) >= 10 else historical_data
            
            for reading in recent_data:
                val = self.sanitize_value(reading.get(param), param)
                if val is not None:
                    values.append(val)
            
            if len(values) < 3:
                return None
            
            # Exponential moving average (more weight to recent values)
            weights = np.exp(np.linspace(-1, 0, len(values)))
            weights /= weights.sum()
            
            prediction = np.average(values, weights=weights)
            std_dev = np.std(values)
            
            return {
                'value': float(prediction),
                'lower_bound': float(prediction - 1.96 * std_dev),
                'upper_bound': float(prediction + 1.96 * std_dev),
                'confidence': 0.95,
                'method': 'Exponential Moving Average',
                'data_points': len(values)
            }
            
        except Exception as e:
            logger.error(f"Fallback prediction failed for {param}: {e}")
            return None
    
    # ==================== ANOMALY DETECTION ====================
    
    def detect_anomalies(self, readings: Dict[str, Any], historical_data: List[Dict]) -> List[Dict]:
        """
        Detect anomalies using Isolation Forest ML algorithm
        
        Args:
            readings: Current readings to check
            historical_data: Historical data for training
            
        Returns:
            List of detected anomalies with details
        """
        if not ML_AVAILABLE:
            logger.warning("ML libraries not available - using fallback method")
            return self._detect_anomalies_fallback(readings, historical_data)
        
        # Validate data
        cleaned_data, _ = self.clean_and_validate_data(historical_data)
        
        if len(cleaned_data) < 30:
            logger.warning(f"Insufficient data for Isolation Forest: {len(cleaned_data)} readings (need 30+)")
            return self._detect_anomalies_fallback(readings, cleaned_data)
        
        try:
            # Prepare feature matrix
            X = []
            for reading in cleaned_data:
                row = []
                for param in self.parameters:
                    val = self.sanitize_value(reading.get(param), param)
                    row.append(val if val is not None else 0.0)
                X.append(row)
            
            X = np.array(X)
            
            # Train Isolation Forest
            clf = IsolationForest(
                contamination=0.1,  # Expect 10% anomalies
                random_state=42,
                n_estimators=100
            )
            clf.fit(X)
            
            # Store model
            self.anomaly_detector = clf
            
            # Check current reading
            current_row = []
            for param in self.parameters:
                val = self.sanitize_value(readings.get(param), param)
                current_row.append(val if val is not None else 0.0)
            
            current_row = np.array(current_row).reshape(1, -1)
            
            # Predict (-1 = anomaly, 1 = normal)
            prediction = clf.predict(current_row)
            anomaly_score = clf.score_samples(current_row)[0]
            
            anomalies = []
            
            if prediction[0] == -1:  # Anomaly detected
                logger.warning(f"Anomaly detected! Score: {anomaly_score:.3f}")
                
                # Identify which parameters are anomalous
                for i, param in enumerate(self.parameters):
                    current_val = current_row[0][i]
                    
                    if current_val == 0.0:
                        continue
                    
                    # Calculate z-score for this parameter
                    param_values = X[:, i]
                    mean = np.mean(param_values)
                    std = np.std(param_values)
                    
                    if std > 0:
                        z_score = abs(current_val - mean) / std
                        
                        if z_score > 3:  # 3 sigma threshold
                            severity = 'critical'
                        elif z_score > 2.5:
                            severity = 'high'
                        elif z_score > 2:
                            severity = 'medium'
                        else:
                            severity = 'low'
                        
                        if z_score > 2:  # Only report significant anomalies
                            anomalies.append({
                                'parameter': param,
                                'current': float(current_val),
                                'expected': float(mean),
                                'deviation': float(abs(current_val - mean)),
                                'z_score': float(z_score),
                                'severity': severity,
                                'anomaly_score': float(anomaly_score),
                                'method': 'Isolation Forest'
                            })
            
            logger.info(f"Anomaly detection complete: {len(anomalies)} anomalies found")
            return anomalies
            
        except Exception as e:
            logger.error(f"Isolation Forest failed: {e}")
            return self._detect_anomalies_fallback(readings, cleaned_data)
    
    def _detect_anomalies_fallback(self, readings: Dict[str, Any], historical_data: List[Dict]) -> List[Dict]:
        """
        Fallback anomaly detection using z-scores
        
        Args:
            readings: Current readings
            historical_data: Historical data
            
        Returns:
            List of anomalies
        """
        if not historical_data or len(historical_data) < 5:
            return []
        
        anomalies = []
        
        try:
            for param in self.parameters:
                current = self.sanitize_value(readings.get(param), param)
                
                if current is None:
                    continue
                
                # Get historical values
                historical_values = []
                for reading in historical_data[-30:]:  # Last 30 readings
                    val = self.sanitize_value(reading.get(param), param)
                    if val is not None:
                        historical_values.append(val)
                
                if len(historical_values) < 5:
                    continue
                
                mean = np.mean(historical_values)
                std = np.std(historical_values)
                
                if std == 0:
                    continue
                
                z_score = abs(current - mean) / std
                
                # Use 3 sigma threshold (less sensitive than before)
                if z_score > 3:
                    severity = 'critical'
                elif z_score > 2.5:
                    severity = 'high'
                elif z_score > 2:
                    severity = 'medium'
                else:
                    continue
                
                anomalies.append({
                    'parameter': param,
                    'current': float(current),
                    'expected': float(mean),
                    'deviation': float(abs(current - mean)),
                    'z_score': float(z_score),
                    'severity': severity,
                    'method': 'Z-Score (3sigma)'
                })
            
            logger.info(f"Fallback anomaly detection: {len(anomalies)} anomalies found")
            
        except Exception as e:
            logger.error(f"Fallback anomaly detection failed: {e}")
        
        return anomalies
    
    # ==================== TREND ANALYSIS ====================
    
    def analyze_trends(self, historical_data: List[Dict]) -> Dict[str, Dict]:
        """
        Analyze trends using polynomial regression
        
        Args:
            historical_data: Historical readings
            
        Returns:
            Dictionary of trend analysis for each parameter
        """
        # Validate data
        cleaned_data, _ = self.clean_and_validate_data(historical_data)
        
        if len(cleaned_data) < 7:
            logger.warning(f"Insufficient data for trend analysis: {len(cleaned_data)} readings (need 7+)")
            return {}
        
        trends = {}
        
        for param in self.parameters:
            try:
                # Extract time series
                values = []
                for reading in cleaned_data:
                    val = self.sanitize_value(reading.get(param), param)
                    if val is not None:
                        values.append(val)
                
                if len(values) < 7:
                    continue
                
                # Prepare data for regression
                X = np.arange(len(values)).reshape(-1, 1)
                y = np.array(values)
                
                # Fit linear regression
                model = LinearRegression()
                model.fit(X, y)
                
                # Calculate predictions and R²
                y_pred = model.predict(X)
                r_squared = r2_score(y, y_pred)
                slope = model.coef_[0]
                
                # Determine direction and strength
                # Use more sensitive threshold for trend detection
                if abs(slope) < 0.005:
                    direction = 'stable'
                    strength = 'weak'
                elif slope > 0:
                    direction = 'increasing'
                    strength = 'strong' if abs(slope) > 0.05 else 'moderate'
                else:
                    direction = 'decreasing'
                    strength = 'strong' if abs(slope) > 0.05 else 'moderate'
                
                # Forecast next 7 days
                future_X = np.arange(len(values), len(values) + 7).reshape(-1, 1)
                forecast = model.predict(future_X)
                
                trends[param] = {
                    'direction': direction,
                    'rate': float(slope),
                    'confidence': float(max(0, min(1, r_squared))),
                    'strength': strength,
                    'forecast_7d': [float(v) for v in forecast],
                    'current_value': float(values[-1]),
                    'data_points': len(values)
                }
                
                logger.debug(f"Trend analysis for {param}: {direction} ({strength})")
                
            except Exception as e:
                logger.error(f"Trend analysis failed for {param}: {e}")
                continue
        
        logger.info(f"Trend analysis complete for {len(trends)} parameters")
        return trends
    
    # ==================== INSIGHTS GENERATION ====================
    
    def get_insights(self, readings: Dict[str, Any], historical_data: List[Dict]) -> List[Dict]:
        """
        Generate AI-powered insights from data
        
        Args:
            readings: Current readings
            historical_data: Historical data
            
        Returns:
            List of insights with priorities and actions
        """
        insights = []
        
        try:
            # Get trends and anomalies
            trends = self.analyze_trends(historical_data)
            anomalies = self.detect_anomalies(readings, historical_data)
            
            # Add anomaly insights (highest priority)
            for anomaly in anomalies:
                param = anomaly['parameter']
                param_name = param.replace('_', ' ').title()
                
                insights.append({
                    'priority': 'high' if anomaly['severity'] in ['critical', 'high'] else 'medium',
                    'type': 'anomaly',
                    'parameter': param,
                    'message': f"{param_name} is {anomaly['deviation']:.2f} units away from normal ({anomaly['severity']} severity)",
                    'action': f"Verify {param_name} reading and check sensor calibration. Expected: {anomaly['expected']:.2f}, Current: {anomaly['current']:.2f}",
                    'severity': anomaly['severity'],
                    'z_score': anomaly.get('z_score', 0)
                })
            
            # Add trend insights
            for param, trend in trends.items():
                param_name = param.replace('_', ' ').title()
                
                if trend['direction'] == 'increasing' and trend['strength'] in ['moderate', 'strong']:
                    # Check if trending out of ideal range
                    ideal_min, ideal_max = self.ideal_ranges.get(param, (0, 1000))
                    current = trend['current_value']
                    forecast_7d = trend['forecast_7d'][-1]  # 7 days ahead
                    
                    if forecast_7d > ideal_max:
                        insights.append({
                            'priority': 'medium',
                            'type': 'trend',
                            'parameter': param,
                            'message': f"{param_name} is trending upward and may exceed ideal range in 7 days",
                            'action': f"Monitor {param_name} closely. Current: {current:.2f}, Forecast: {forecast_7d:.2f}, Ideal max: {ideal_max}",
                            'trend_direction': 'increasing',
                            'forecast': forecast_7d
                        })
                    else:
                        insights.append({
                            'priority': 'low',
                            'type': 'trend',
                            'parameter': param,
                            'message': f"{param_name} is trending upward ({trend['strength']} trend)",
                            'action': f"Monitor {param_name} and prepare to adjust if needed",
                            'trend_direction': 'increasing'
                        })
                
                elif trend['direction'] == 'decreasing' and trend['strength'] in ['moderate', 'strong']:
                    ideal_min, ideal_max = self.ideal_ranges.get(param, (0, 1000))
                    current = trend['current_value']
                    forecast_7d = trend['forecast_7d'][-1]
                    
                    if forecast_7d < ideal_min:
                        insights.append({
                            'priority': 'medium',
                            'type': 'trend',
                            'parameter': param,
                            'message': f"{param_name} is trending downward and may fall below ideal range in 7 days",
                            'action': f"Consider adding {param_name}. Current: {current:.2f}, Forecast: {forecast_7d:.2f}, Ideal min: {ideal_min}",
                            'trend_direction': 'decreasing',
                            'forecast': forecast_7d
                        })
                    else:
                        insights.append({
                            'priority': 'low',
                            'type': 'trend',
                            'parameter': param,
                            'message': f"{param_name} is trending downward ({trend['strength']} trend)",
                            'action': f"Monitor {param_name} and consider adding if it continues to drop",
                            'trend_direction': 'decreasing'
                        })
            
            # Check if all parameters are in ideal range
            all_good = True
            for param in self.parameters:
                val = self.sanitize_value(readings.get(param), param)
                if val is not None:
                    ideal_min, ideal_max = self.ideal_ranges.get(param, (0, 1000))
                    if val < ideal_min or val > ideal_max:
                        all_good = False
                        break
            
            # Add general health insight if no issues
            if not insights and all_good:
                insights.append({
                    'priority': 'low',
                    'type': 'status',
                    'message': 'Pool chemistry is stable and within ideal ranges',
                    'action': 'Continue regular monitoring and maintenance schedule',
                    'status': 'excellent'
                })
            
            # Sort by priority
            priority_order = {'high': 0, 'medium': 1, 'low': 2}
            insights.sort(key=lambda x: priority_order.get(x['priority'], 3))
            
            logger.info(f"Generated {len(insights)} insights")
            
        except Exception as e:
            logger.error(f"Error generating insights: {e}")
            import traceback
            traceback.print_exc()
        
        return insights
    
    # ==================== COST OPTIMIZATION ====================
    
    def optimize_chemical_usage(self, current_readings: Dict, adjustments: List[Dict]) -> Dict[str, Any]:
        """
        Analyze chemical usage and provide cost optimization recommendations
        
        Args:
            current_readings: Current pool readings
            adjustments: Calculated chemical adjustments
            
        Returns:
            Dictionary with cost analysis and optimization recommendations
        """
        if not adjustments:
            return {
                'total_cost': 0.0,
                'savings_potential': 0.0,
                'monthly_estimate': 0.0,
                'recommendations': ['No adjustments needed - pool chemistry is balanced!'],
                'breakdown': []
            }
        
        try:
            total_cost = 0.0
            breakdown = []
            
            # Calculate costs for each adjustment
            for adjustment in adjustments:
                chemical = adjustment.get('chemical', '').lower()
                amount = adjustment.get('amount', 0)
                
                if amount <= 0:
                    continue
                
                # Map chemical names to cost keys
                cost = 0.0
                chemical_key = None
                
                if 'soda ash' in chemical or 'ph up' in chemical:
                    cost = (amount / 16) * self.chemical_costs['soda_ash']
                    chemical_key = 'soda_ash'
                elif 'muriatic acid' in chemical or 'ph down' in chemical:
                    cost = (amount / 128) * self.chemical_costs['muriatic_acid']
                    chemical_key = 'muriatic_acid'
                elif 'chlorine' in chemical:
                    cost = (amount / 16) * self.chemical_costs['chlorine']
                    chemical_key = 'chlorine'
                elif 'baking soda' in chemical or 'alkalinity' in chemical:
                    cost = (amount / 16) * self.chemical_costs['baking_soda']
                    chemical_key = 'baking_soda'
                elif 'calcium' in chemical:
                    cost = (amount / 16) * self.chemical_costs['calcium_chloride']
                    chemical_key = 'calcium_chloride'
                elif 'stabilizer' in chemical or 'cyanuric' in chemical:
                    cost = (amount / 16) * self.chemical_costs['stabilizer']
                    chemical_key = 'stabilizer'
                elif 'bromine' in chemical:
                    cost = (amount / 16) * self.chemical_costs['bromine']
                    chemical_key = 'bromine'
                elif 'salt' in chemical:
                    cost = (amount / 16) * self.chemical_costs['salt']
                    chemical_key = 'salt'
                
                if cost > 0:
                    total_cost += cost
                    breakdown.append({
                        'chemical': chemical,
                        'amount': amount,
                        'cost': round(cost, 2),
                        'unit_price': self.chemical_costs.get(chemical_key, 0)
                    })
            
            # Estimate monthly cost (assuming adjustments every 3 days)
            monthly_estimate = total_cost * 10  # ~10 adjustments per month
            
            # Calculate savings potential
            savings_potential = 0.0
            recommendations = []
            
            # Bulk purchase savings (15-20% for orders over $50)
            if total_cost > 50:
                bulk_savings = total_cost * 0.175
                savings_potential += bulk_savings
                recommendations.append({
                    'category': 'Bulk Purchase',
                    'suggestion': 'Buy chemicals in bulk to save 15-20%',
                    'potential_savings': round(bulk_savings, 2)
                })
            
            # Stabilizer optimization
            chlorine_cost = sum(b['cost'] for b in breakdown if 'chlorine' in b['chemical'].lower())
            if chlorine_cost > 10:
                stabilizer_savings = chlorine_cost * 0.30
                savings_potential += stabilizer_savings
                recommendations.append({
                    'category': 'Chlorine Optimization',
                    'suggestion': 'Use stabilizer (CYA) to reduce chlorine consumption by up to 30%',
                    'potential_savings': round(stabilizer_savings, 2)
                })
            
            # pH adjustment optimization
            ph_cost = sum(b['cost'] for b in breakdown if 'ph' in b['chemical'].lower() or 'acid' in b['chemical'].lower())
            if ph_cost > 5:
                ph_savings = ph_cost * 0.25
                savings_potential += ph_savings
                recommendations.append({
                    'category': 'pH Management',
                    'suggestion': 'Test pH more frequently to catch imbalances early and reduce chemical usage',
                    'potential_savings': round(ph_savings, 2)
                })
            
            # General recommendations
            recommendations.append({
                'category': 'Maintenance',
                'suggestion': 'Regular maintenance reduces overall chemical costs by 20-30%',
                'potential_savings': round(monthly_estimate * 0.25, 2)
            })
            
            recommendations.append({
                'category': 'Evaporation',
                'suggestion': 'Keep pool covered when not in use to reduce water and chemical loss',
                'potential_savings': round(monthly_estimate * 0.15, 2)
            })
            
            return {
                'total_cost': round(total_cost, 2),
                'monthly_estimate': round(monthly_estimate, 2),
                'savings_potential': round(savings_potential, 2),
                'annual_savings': round(savings_potential * 12, 2),
                'breakdown': breakdown,
                'recommendations': recommendations,
                'cost_per_adjustment': round(total_cost, 2)
            }
            
        except Exception as e:
            logger.error(f"Error optimizing chemical usage: {e}")
            import traceback
            traceback.print_exc()
            return {
                'total_cost': 0.0,
                'savings_potential': 0.0,
                'monthly_estimate': 0.0,
                'recommendations': ['Error calculating optimization'],
                'breakdown': [],
                'error': str(e)
            }
    
    # ==================== MODEL PERSISTENCE ====================
    
    def save_models(self):
        """Save trained models to disk"""
        try:
            # Save ARIMA models
            for param, model in self.arima_models.items():
                model_path = self.models_dir / f"{param}_arima.pkl"
                joblib.dump(model, model_path)
            
            # Save anomaly detector
            if self.anomaly_detector:
                detector_path = self.models_dir / "anomaly_detector.pkl"
                joblib.dump(self.anomaly_detector, detector_path)
            
            # Save scaler
            if self.scaler:
                scaler_path = self.models_dir / "scaler.pkl"
                joblib.dump(self.scaler, scaler_path)
            
            # Save metadata
            metadata = {
                'saved_at': datetime.now().isoformat(),
                'models': list(self.arima_models.keys()),
                'has_anomaly_detector': self.anomaly_detector is not None,
                'parameters': self.parameters
            }
            
            metadata_path = self.models_dir / "metadata.json"
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            logger.info(f"Models saved to {self.models_dir}")
            
        except Exception as e:
            logger.error(f"Error saving models: {e}")
    
    def load_models(self):
        """Load trained models from disk"""
        try:
            # Check if models directory exists
            if not self.models_dir.exists():
                logger.info("No saved models found")
                return
            
            # Load metadata
            metadata_path = self.models_dir / "metadata.json"
            if metadata_path.exists():
                with open(metadata_path, 'r') as f:
                    metadata = json.load(f)
                logger.info(f"Found models saved at {metadata.get('saved_at')}")
            
            # Load ARIMA models
            for model_file in self.models_dir.glob("*_arima.pkl"):
                param = model_file.stem.replace("_arima", "")
                self.arima_models[param] = joblib.load(model_file)
                logger.debug(f"Loaded ARIMA model for {param}")
            
            # Load anomaly detector
            detector_path = self.models_dir / "anomaly_detector.pkl"
            if detector_path.exists():
                self.anomaly_detector = joblib.load(detector_path)
                logger.debug("Loaded anomaly detector")
            
            # Load scaler
            scaler_path = self.models_dir / "scaler.pkl"
            if scaler_path.exists():
                self.scaler = joblib.load(scaler_path)
                logger.debug("Loaded scaler")
            
            if self.arima_models:
                logger.info(f"Loaded {len(self.arima_models)} models from disk")
            
        except Exception as e:
            logger.error(f"Error loading models: {e}")
    
    # ==================== MODEL EVALUATION ====================
    
    def evaluate_prediction_accuracy(self, historical_data: List[Dict]) -> Dict[str, float]:
        """
        Evaluate prediction accuracy using train/test split
        
        Args:
            historical_data: Historical readings
            
        Returns:
            Dictionary of accuracy metrics per parameter
        """
        if len(historical_data) < 30:
            logger.warning("Insufficient data for evaluation")
            return {}
        
        accuracy = {}
        
        try:
            # Use 80/20 train/test split
            split_idx = int(len(historical_data) * 0.8)
            train_data = historical_data[:split_idx]
            test_data = historical_data[split_idx:]
            
            for param in self.parameters:
                # Extract values
                train_values = [self.sanitize_value(r.get(param), param) for r in train_data]
                test_values = [self.sanitize_value(r.get(param), param) for r in test_data]
                
                train_values = [v for v in train_values if v is not None]
                test_values = [v for v in test_values if v is not None]
                
                if len(train_values) < 20 or len(test_values) < 5:
                    continue
                
                # Make predictions for test set
                predictions = []
                for i in range(len(test_values)):
                    # Use data up to this point
                    data_subset = train_data + test_data[:i]
                    pred = self.predict_next_readings(data_subset)
                    
                    if param in pred:
                        predictions.append(pred[param]['value'])
                    else:
                        predictions.append(train_values[-1])  # Fallback
                
                # Calculate metrics
                if len(predictions) == len(test_values):
                    mse = mean_squared_error(test_values, predictions)
                    rmse = np.sqrt(mse)
                    
                    # Calculate percentage error
                    mean_val = np.mean(test_values)
                    percentage_error = (rmse / mean_val) * 100 if mean_val > 0 else 100
                    
                    accuracy[param] = {
                        'rmse': float(rmse),
                        'percentage_error': float(percentage_error),
                        'accuracy': float(max(0, 100 - percentage_error))
                    }
            
            logger.info(f"Evaluated accuracy for {len(accuracy)} parameters")
            
        except Exception as e:
            logger.error(f"Error evaluating accuracy: {e}")
        
        return accuracy


# ==================== UTILITY FUNCTIONS ====================

def format_prediction_display(predictions: Dict[str, Any]) -> str:
    """Format predictions for display"""
    if not predictions:
        return "No predictions available"
    
    output = []
    output.append("PREDICTED NEXT READINGS")
    output.append("=" * 60)
    output.append("")
    
    for param, pred in predictions.items():
        param_name = param.replace('_', ' ').title()
        
        if isinstance(pred, dict):
            value = pred.get('value', 0)
            lower = pred.get('lower_bound', value)
            upper = pred.get('upper_bound', value)
            confidence = pred.get('confidence', 0) * 100
            method = pred.get('method', 'Unknown')
            
            output.append(f"{param_name}:")
            output.append(f"   Predicted: {value:.2f}")
            output.append(f"   Range: {lower:.2f} - {upper:.2f} ({confidence:.0f}% confidence)")
            output.append(f"   Method: {method}")
            output.append("")
        else:
            output.append(f"{param_name}: {pred:.2f}")
            output.append("")
    
    return "\n".join(output)


def format_anomalies_display(anomalies: List[Dict]) -> str:
    """Format anomalies for display"""
    if not anomalies:
        return "No anomalies detected - all readings are normal"
    
    output = []
    output.append("ANOMALIES DETECTED")
    output.append("=" * 60)
    output.append("")
    
    for anomaly in anomalies:
        param = anomaly['parameter'].replace('_', ' ').title()
        severity = anomaly['severity'].upper()
        current = anomaly['current']
        expected = anomaly['expected']
        deviation = anomaly['deviation']
        
        # Severity emoji
        if severity == 'CRITICAL':
            emoji = "[RED]"
        elif severity == 'HIGH':
            emoji = "[ORANGE]"
        elif severity == 'MEDIUM':
            emoji = "[YELLOW]"
        else:
            emoji = "[GREEN]"
        
        output.append(f"{emoji} [{severity}] {param}")
        output.append(f"   Current: {current:.2f}")
        output.append(f"   Expected: {expected:.2f}")
        output.append(f"   Deviation: {deviation:.2f}")
        output.append(f"   Z-Score: {anomaly.get('z_score', 0):.2f}")
        output.append("")
    
    return "\n".join(output)


def format_trends_display(trends: Dict[str, Dict]) -> str:
    """Format trends for display"""
    if not trends:
        return "No trend data available"
    
    output = []
    output.append("[UP] TREND ANALYSIS")
    output.append("=" * 60)
    output.append("")
    
    for param, trend in trends.items():
        param_name = param.replace('_', ' ').title()
        direction = trend['direction']
        strength = trend.get('strength', 'unknown')
        confidence = trend['confidence'] * 100
        
        # Direction emoji
        if direction == 'increasing':
            emoji = "[UP]"
        elif direction == 'decreasing':
            emoji = "[DOWN]"
        else:
            emoji = "?"
        
        output.append(f"{emoji} {param_name}")
        output.append(f"   Direction: {direction.upper()} ({strength})")
        output.append(f"   Confidence: {confidence:.1f}%")
        output.append(f"   Current: {trend['current_value']:.2f}")
        
        if 'forecast_7d' in trend:
            forecast = trend['forecast_7d'][-1]
            output.append(f"   7-Day Forecast: {forecast:.2f}")
        
        output.append("")
    
    return "\n".join(output)


def format_insights_display(insights: List[Dict]) -> str:
    """Format insights for display"""
    if not insights:
        return "No insights available"
    
    output = []
    output.append("AI-POWERED INSIGHTS")
    output.append("=" * 60)
    output.append("")
    
    for i, insight in enumerate(insights, 1):
        priority = insight['priority'].upper()
        insight_type = insight['type'].upper()
        message = insight['message']
        action = insight['action']
        
        # Priority emoji
        if priority == 'HIGH':
            emoji = "[RED]"
        elif priority == 'MEDIUM':
            emoji = "[YELLOW]"
        else:
            emoji = "[GREEN]"
        
        output.append(f"{i}. {emoji} [{priority}] {insight_type}")
        output.append(f"   {message}")
        output.append(f"   Action: {action}")
        output.append("")
    
    return "\n".join(output)


def format_optimization_display(optimization: Dict[str, Any]) -> str:
    """Format cost optimization for display"""
    if not optimization or 'error' in optimization:
        return "Cost optimization not available"
    
    output = []
    output.append("[MONEY] COST OPTIMIZATION ANALYSIS")
    output.append("=" * 60)
    output.append("")
    
    output.append(f"Current Adjustment Cost: ${optimization['total_cost']:.2f}")
    output.append(f"Estimated Monthly Cost: ${optimization['monthly_estimate']:.2f}")
    output.append(f"Potential Monthly Savings: ${optimization['savings_potential']:.2f}")
    output.append(f"Potential Annual Savings: ${optimization.get('annual_savings', 0):.2f}")
    output.append("")
    
    if 'breakdown' in optimization and optimization['breakdown']:
        output.append("Cost Breakdown:")
        output.append("-" * 60)
        for item in optimization['breakdown']:
            output.append(f"  * {item['chemical']}: {item['amount']:.1f} oz = ${item['cost']:.2f}")
        output.append("")
    
    if 'recommendations' in optimization:
        output.append("Optimization Recommendations:")
        output.append("-" * 60)
        for rec in optimization['recommendations']:
            if isinstance(rec, dict):
                output.append(f"  {rec['category']}")
                output.append(f"     {rec['suggestion']}")
                output.append(f"     Potential Savings: ${rec['potential_savings']:.2f}")
                output.append("")
            else:
                output.append(f"  * {rec}")
        output.append("")
    
    return "\n".join(output)

# ==================== END ML ANALYTICS ENGINE V2 ====================


class WaterTester:  # Fallback WaterTester
    def __init__(self):
        self.pool_volume = 10000

    def set_pool_volume(self, volume):
        self.pool_volume = volume

    def analyze_ph(self, ph):
        if ph < 7.2:
            return {
                "current": ph,
                "ideal_range": (7.2, 7.8),
                "direction": "low",
                "adjustment": "increase",
                "chemical": "Soda Ash",
                "dosage": f"{(7.2 - ph) * 20:.1f} oz"
            }
        elif ph > 7.8:
            return {
                "current": ph,
                "ideal_range": (7.2, 7.8),
                "direction": "high",
                "adjustment": "decrease",
                "chemical": "Muriatic Acid",
                "dosage": f"{(ph - 7.8) * 20:.1f} oz"
            }
        else:
            return {
                "current": ph,
                "ideal_range": (7.2, 7.8),
                "direction": "normal",
                "adjustment": "none",
                "chemical": None,
                "dosage": "No adjustment needed"
            }

    def analyze_chlorine(self, chlorine):
        if chlorine < 1.0:
            return {
                "current": chlorine,
                "ideal_range": (1.0, 3.0),
                "direction": "low",
                "adjustment": "increase",
                "chemical": "Liquid Chlorine",
                "dosage": f"{(1.0 - chlorine) * 30:.1f} oz"
            }
        elif chlorine > 3.0:
            return {
                "current": chlorine,
                "ideal_range": (1.0, 3.0),
                "direction": "high",
                "adjustment": "decrease",
                "chemical": None,
                "dosage": "Allow chlorine to dissipate naturally"
            }
        else:
            return {
                "current": chlorine,
                "ideal_range": (1.0, 3.0),
                "direction": "normal",
                "adjustment": "none",
                "chemical": None,
                "dosage": "No adjustment needed"
            }

class DataManager:  # Fallback DataManager
    def __init__(self, database_name):
        self.database_name = database_name

    def insert_reading(self, temperature, potential_hydrogen, chlorine):
        logger.info(f"Inserting reading: temp={temperature}, pH={potential_hydrogen}, chlorine={chlorine}")

    def close_connection(self):
        pass

class WeatherAPI:
    def __init__(self, api_key):
        self.api_key = api_key
        # SECURE: Mask API key properly for security (show minimal characters)
        if len(api_key) >= 4:
            masked_key = api_key[:2] + "*" * (len(api_key) - 4) + api_key[-2:]
        else:
            masked_key = "*" * len(api_key)
        logger.info(f"WeatherAPI initialized with secure masked key")
        
        # Rate limiting attributes
        self.last_request_time = 0
        self.min_request_interval = 60  # Minimum 60 seconds between API requests
        logger.info(f"Rate limiting enabled: {self.min_request_interval}s between requests")
    
    def _cleanup_old_cache(self, cache_dir, max_age_days=7):
        """
        Remove cache files older than max_age_days to prevent disk space accumulation.
        
        Args:
            cache_dir: Path object pointing to cache directory
            max_age_days: Maximum age of cache files in days (default: 7)
        """
        import time
        from pathlib import Path
        
        try:
            cutoff_time = time.time() - (max_age_days * 86400)  # 86400 seconds in a day
            removed_count = 0
            
            # Iterate through all weather cache files
            for cache_file in cache_dir.glob("weather_*.json"):
                try:
                    # Check file age
                    if cache_file.stat().st_mtime < cutoff_time:
                        cache_file.unlink()
                        removed_count += 1
                        logger.debug(f"Removed old cache file: {cache_file.name}")
                except Exception as e:
                    logger.warning(f"Failed to remove cache file {cache_file.name}: {e}")
            
            if removed_count > 0:
                logger.info(f"Cache cleanup: Removed {removed_count} old cache file(s)")
        
        except Exception as e:
            logger.error(f"Error during cache cleanup: {e}")

    def get_weather_data(self, zip_code):
        import requests
        import json
        import os
        import time
        from pathlib import Path
        
        # Create a cache directory if it doesn't exist
        cache_dir = Path("cache")
        cache_dir.mkdir(exist_ok=True)
        
        # Periodic cache cleanup (10% chance on each call to avoid overhead)
        import random
        if random.random() < 0.1:  # 10% probability
            self._cleanup_old_cache(cache_dir, max_age_days=7)
        
        # Create a cache file name based on the zip code
        cache_file = cache_dir / f"weather_{zip_code}.json"
        cache_max_age = 3600  # 1 hour in seconds
        
        # Check if we have a valid cache
        if cache_file.exists():
            file_age = time.time() - cache_file.stat().st_mtime
            if file_age < cache_max_age:
                try:
                    with open(cache_file, 'r') as f:
                        cached_data = json.load(f)
                        logger.info(f"Using cached weather data for {zip_code}")
                        return cached_data
                except Exception as e:
                    logger.warning(f"Failed to load cached weather data: {e}")
        
        # No valid cache, make the API request
        # Rate limiting: Check if enough time has passed since last request
        import time
        time_since_last = time.time() - self.last_request_time
        if time_since_last < self.min_request_interval:
            wait_time = self.min_request_interval - time_since_last
            logger.info(f"Rate limiting: waiting {wait_time:.1f}s before next API request")
            time.sleep(wait_time)
        
        # Update last request time
        self.last_request_time = time.time()
        
        base_url = "https://api.weatherapi.com/v1/forecast.json"
        params = {
            "key": self.api_key,
            "q": zip_code,
            "days": 3,  # Get 3-day forecast
            "aqi": "no"
        }
        
        try:
            response = requests.get(base_url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                # Cache the successful response
                try:
                    with open(cache_file, 'w') as f:
                        json.dump(data, f)
                except Exception as e:
                    logger.warning(f"Failed to cache weather data: {e}")
                return data
            else:
                # If we have an expired cache, better to use it than nothing
                if cache_file.exists():
                    try:
                        with open(cache_file, 'r') as f:
                            cached_data = json.load(f)
                            logger.warning(f"Using expired cached weather data for {zip_code}")
                            cached_data["cached"] = True
                            cached_data["cache_warning"] = "Using outdated weather data"
                            return cached_data
                    except (FileNotFoundError, json.JSONDecodeError, KeyError):
                        pass
                        
                try:
                    error_details = response.json()
                    return {"error": f"API Error: {response.status_code} - {error_details.get('error', {}).get('message', 'Unknown error')}"}
                except json.JSONDecodeError:
                    return {"error": f"Invalid response format. Status code: {response.status_code}"}
                    
        except requests.RequestException as e:
            # Try to use cached data as fallback
            if cache_file.exists():
                try:
                    with open(cache_file, 'r') as f:
                        cached_data = json.load(f)
                        logger.warning(f"Network error, using cached weather data for {zip_code}")
                        cached_data["cached"] = True
                        cached_data["cache_warning"] = "Using cached data due to network error"
                        return cached_data
                except (FileNotFoundError, json.JSONDecodeError, KeyError):
                    pass
                    
            return {"error": f"Network error: {str(e)}"}

# Try to import real Arduino interface
try:
    from arduino_interface import ArduinoInterface
    ARDUINO_AVAILABLE = True
except ImportError as e:
    ARDUINO_AVAILABLE = False
    # Fallback ArduinoInterface
    class ArduinoInterface:
        def __init__(self, port=None):
            self.port = port
            self.is_connected = False
        def connect(self):
            return False
        def read_data(self):
            return None
        def disconnect(self):
            pass

# Try to import test strip analyzer
try:
    from test_strip_analyzer import TestStripAnalyzer
    TEST_STRIP_AVAILABLE = True
except ImportError as e:
    TEST_STRIP_AVAILABLE = False
    class TestStripAnalyzer:
        def __init__(self):
            pass
        def load_image(self, path):
            return None
        def analyze_strip(self, image):
            return {}
class ConfigurationError(Exception): pass
class APIError(Exception): pass


class WeatherImpactAnalyzer:
    """Analyzes weather impact on pool chemistry"""
    
    def __init__(self):
        """Initialize the weather impact analyzer"""
        pass
    
    def analyze_weather_impact(self, weather_data, current_readings=None):
        """Analyze how weather affects pool chemistry"""
        if not weather_data:
            return {}
        
        impacts = {
            'temperature': {},
            'uv_index': {},
            'precipitation': {},
            'wind': {},
            'humidity': {},
            'alerts': []
        }
        
        try:
            current = weather_data.get('current', {})
            
            # Temperature impact
            temp_f = current.get('temp_f', 0)
            if temp_f > 85:
                impacts['temperature'] = {
                    'level': 'high',
                    'effect': 'Increased chlorine consumption (2-3x normal)',
                    'action': 'Monitor chlorine levels more frequently'
                }
                impacts['alerts'].append('[TEMP] High temperature increases chlorine demand')
            elif temp_f < 60:
                impacts['temperature'] = {
                    'level': 'low',
                    'effect': 'Reduced chemical activity',
                    'action': 'May need to adjust chemical dosing'
                }
            
            # UV Index impact
            uv = current.get('uv', 0)
            if uv > 6:
                impacts['uv_index'] = {
                    'level': 'high',
                    'effect': 'Rapid chlorine°Fradation (up to 90% in 2 hours)',
                    'action': 'Increase stabilizer (CYA) levels, add chlorine more frequently'
                }
                impacts['alerts'].append('High UV index rapidly depletes chlorine')
            
            # Precipitation impact
            precip = current.get('precip_in', 0)
            if precip > 0.5:
                impacts['precipitation'] = {
                    'level': 'significant',
                    'effect': 'Dilution of chemicals, pH changes, debris',
                    'action': 'Test all parameters after rain, shock if needed'
                }
                impacts['alerts'].append('[RAIN] Heavy rain dilutes pool chemistry')
            
            # Wind impact
            wind_mph = current.get('wind_mph', 0)
            if wind_mph > 15:
                impacts['wind'] = {
                    'level': 'high',
                    'effect': 'Increased evaporation and debris',
                    'action': 'Check water level, clean filters more often'
                }
            
            # Humidity impact
            humidity = current.get('humidity', 0)
            if humidity < 40:
                impacts['humidity'] = {
                    'level': 'low',
                    'effect': 'Increased water evaporation',
                    'action': 'Monitor water level, may need to add water'
                }
        
        except Exception as e:
            logger.error(f"Error analyzing weather impact: {e}")
        
        return impacts
    
    def get_weather_recommendations(self, impacts):
        """Get actionable recommendations based on weather impacts"""
        recommendations = []
        
        try:
            if impacts.get('alerts'):
                recommendations.extend(impacts['alerts'])
            
            for category, data in impacts.items():
                if category != 'alerts' and isinstance(data, dict):
                    if data.get('action'):
                        recommendations.append(f"* {data['action']}")
        
        except Exception as e:
            logger.error(f"Error generating weather recommendations: {e}")
        
        return recommendations

# Version information
__version__ = "2.0.0"
__author__ = "Virtual Control LLC"
__copyright__ = "Copyright © 2025 Virtual Control LLC"

# Configure logging
def setup_logging():
    """Configure application logging"""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=os.environ.get("APP_LOG_LEVEL", "INFO").upper(),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / 'pool_app.log'),
            logging.StreamHandler()
        ]
    )
    
    if os.environ.get("APP_DEBUG", "false").lower() == "true":
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    return logging.getLogger(__name__)

logger = setup_logging()

# SENSOR VALIDATION CLASS - CRITICAL FIX
class SensorValidator:
    """Validates sensor readings to detect malfunctions"""
    
    @staticmethod
    def validate_reading(reading):
        """Validate a single sensor reading for malfunctions"""
        errors = []
        warnings = []
        
        # pH sensor malfunction detection - CRITICAL FIX
        ph = reading.get('ph')
        if ph is not None:
            if ph <= 0.0 or ph > 14.0:
                errors.append(f"CRITICAL: pH sensor malfunction - reading {ph} is impossible")
            elif ph < 6.0 or ph > 9.0:
                warnings.append(f"WARNING: pH reading {ph} is extremely out of normal range")
        
        # Temperature sensor malfunction detection
        temp = reading.get('temperature')
        if temp is not None:
            if temp <= 32.0 or temp > 120.0:
                errors.append(f"CRITICAL: Temperature sensor malfunction - reading {temp}°F is impossible")
            elif temp < 50.0 or temp > 110.0:
                warnings.append(f"WARNING: Temperature reading {temp}°F is extremely out of normal range")
        
        # Free chlorine sensor malfunction detection
        fc = reading.get('free_chlorine')
        if fc is not None:
            if fc < 0.0 or fc > 20.0:
                errors.append(f"CRITICAL: Chlorine sensor malfunction - reading {fc} ppm is impossible")
            elif fc > 10.0:
                warnings.append(f"WARNING: Chlorine reading {fc} ppm is dangerously high")
        
        # Total chlorine validation
        tc = reading.get('total_chlorine')
        if tc is not None:
            if tc < 0.0 or tc > 20.0:
                errors.append(f"CRITICAL: Total chlorine sensor malfunction - reading {tc} ppm is impossible")
        
        # Alkalinity validation
        alk = reading.get('alkalinity')
        if alk is not None:
            if alk < 0.0 or alk > 1000.0:
                errors.append(f"CRITICAL: Alkalinity sensor malfunction - reading {alk} ppm is impossible")
        
        # Calcium hardness validation
        ch = reading.get('calcium_hardness')
        if ch is not None:
            if ch < 0.0 or ch > 2000.0:
                errors.append(f"CRITICAL: Calcium hardness sensor malfunction - reading {ch} ppm is impossible")
        
        # Cyanuric acid validation
        cya = reading.get('cyanuric_acid')
        if cya is not None:
            if cya < 0.0 or cya > 500.0:
                errors.append(f"CRITICAL: Cyanuric acid sensor malfunction - reading {cya} ppm is impossible")
        
        # Salt validation
        salt = reading.get('salt')
        if salt is not None:
            if salt < 0.0 or salt > 10000.0:
                errors.append(f"CRITICAL: Salt sensor malfunction - reading {salt} ppm is impossible")
        
        # Bromine validation
        bromine = reading.get('bromine')
        if bromine is not None:
            if bromine < 0.0 or bromine > 20.0:
                errors.append(f"CRITICAL: Bromine sensor malfunction - reading {bromine} ppm is impossible")
        
        is_valid = len(errors) == 0
        return is_valid, errors, warnings


class SplashScreen:
    """Cool animated splash screen for application startup"""
    
    def __init__(self, parent):
        self.parent = parent
        self.splash = tk.Toplevel(parent)
        self.splash.withdraw()
        self.splash.overrideredirect(True)
        
        # Set size and center
        width, height = 800, 500
        screen_width = self.splash.winfo_screenwidth()
        screen_height = self.splash.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.splash.geometry(f'{width}x{height}+{x}+{y}')
        
        # Load splash image
        splash_image_path = Path(__file__).parent / "splash_screen_realistic.png"
        if splash_image_path.exists():
            try:
                splash_img = Image.open(splash_image_path)
                splash_photo = ImageTk.PhotoImage(splash_img)
                splash_label = tk.Label(self.splash, image=splash_photo, bd=0)
                splash_label.image = splash_photo
                splash_label.pack()
            except Exception as e:
                self._create_simple_splash()
        else:
            self._create_simple_splash()
        
        # Progress bar
        self.progress_frame = tk.Frame(self.splash, bg='#006994', height=30)
        self.progress_frame.pack(side='bottom', fill='x')
        
        self.progress_bar = ttk.Progressbar(self.progress_frame, mode='indeterminate', length=700)
        self.progress_bar.pack(pady=5)
        
        self.status_label = tk.Label(self.progress_frame, text="Initializing...", 
                                     bg='#006994', fg='white', font=('Arial', 10))
        self.status_label.pack()
    
    def _create_simple_splash(self):
        frame = tk.Frame(self.splash, bg='#006994')
        frame.pack(fill='both', expand=True)
        tk.Label(frame, text="Deep Blue", font=('Arial', 48, 'bold'), 
                bg='#006994', fg='white').pack(pady=(100, 10))
        tk.Label(frame, text="Pool Chemistry Manager", font=('Arial', 24), 
                bg='#006994', fg='white').pack(pady=10)
        tk.Label(frame, text="Version 3.6.0", font=('Arial', 14), 
                bg='#006994', fg='white').pack(pady=(50, 10))
    
    def show(self):
        self.splash.deiconify()
        self.splash.lift()
        self.progress_bar.start(10)
        self.splash.update()
    
    def update_status(self, message):
        self.status_label.config(text=message)
        self.splash.update()
    
    def close(self):
        self.progress_bar.stop()
        self.splash.destroy()


class PoolApp(tk.Tk):
    def __init__(self):
        """Initialize the application"""
        logger.debug("Initializing PoolApp")
        logger.info("Initializing PoolApp")
        try:
            # Initialize Tk
            super().__init__()

            # Show splash screen
            self.splash = SplashScreen(self)
            self.splash.show()
            self.splash.update_status("Loading application...")

            logger.info("Tk initialized")

            # Set window properties
            self.title(f"Deep Blue Chemistry Pool Management System v{__version__}")
            self.withdraw()  # Hide main window during splash
            self.geometry(f"{DEFAULT_WINDOW_SIZE[0]}x{DEFAULT_WINDOW_SIZE[1]}")
            self.minsize(MIN_WINDOW_SIZE[0], MIN_WINDOW_SIZE[1])
            self.center_window()  # Call center_window AFTER super().__init__()
            logger.info("Window size and position set")
            
            try:
                # Auto-create assets folder
                assets_dir = os.path.join(os.path.dirname(__file__), "assets")
                os.makedirs(assets_dir, exist_ok=True)
                
                icon_path = os.path.join(assets_dir, "icon.ico")
                if os.path.exists(icon_path):
                    self.iconbitmap(icon_path)
                    logger.info("Application icon loaded")
                else:
                    logger.debug("Application icon not found (this is OK)")
            except Exception as e:
                logger.warning(f"Error setting application icon: {e}")
                logger.error(f"Error setting application icon: {e}")

            # Initialize core components
            self.water_tester = WaterTester()
            self.data_manager = DataManager("pool_data.db")
            weather_api_key = os.environ.get("WEATHER_API_KEY")
            if weather_api_key:
                self.weather_api = WeatherAPI(weather_api_key)
                logger.info("WeatherAPI initialized with API key.")
            else:
                logger.warning("Weather API key not found. Weather features will be disabled.")
                self.weather_api = None



            self._initialize_variables()
            self._configure_colors()
            self._configure_styles()
            self._create_menu_bar()
            self._create_header()
            self._create_main_content()
            self._create_footer()
            self._load_data()

            self.arduino = None
            self._setup_arduino_communication()
            self._start_periodic_updates()
            self.protocol("WM_DELETE_WINDOW", self._on_close)

            logger.info("PoolApp initialization completed successfully")
            logger.info("PoolApp initialization completed successfully")

        except ConfigurationError as e:
            logger.critical(f"Configuration Error: {str(e)}", exc_info=True)
            messagebox.showerror("Configuration Error", f"Application cannot start due to configuration issue: {str(e)}")
            sys.exit(1)
        except Exception as e:
            logger.critical(f"Error initializing application: {str(e)}", exc_info=True)
            logger.error(f"Error initializing application: {str(e)}")
            messagebox.showerror(
                "Initialization Error",
                f"Failed to initialize application: {str(e)}"
            )
            sys.exit(1)

    def center_window(self):
        """Center the window on the screen."""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

    def _update_status(self, message):
        """Safely update status bar"""
        if hasattr(self, 'status_bar'):
            self.status_bar.config(text=message)
        else:
            logger.info(f"Status: {message}")

    def _initialize_variables(self):
        """Initialize application variables."""
        self.customer_info = {}
        self.chemical_readings = []
        self.entries = {}
        self.labels = {}
        self.buttons = {}
        self.frames = {}
        self.status_var = tk.StringVar(value="Ready")
        self.data_dir = Path("data")
        self.data_dir.mkdir(exist_ok=True)
        
        # Ensure alerts.json exists
        alerts_file = self.data_dir / "alerts.json"
        if not alerts_file.exists():
            with open(alerts_file, 'w') as f:
                json.dump([], f)
            logger.info("Created empty alerts.json file")
        
        # Load alert configuration (Phase 1.2)
        self.alert_config = self._load_alert_config()
        logger.info("Alert configuration loaded")
        
        # Initialize branding configuration

        
        self.branding_config = {

        
            "company_info": {

        
                "name": "Deep Blue Pool Chemistry",

        
                "tagline": "Professional Pool Management",

        
                "address": "",

        
                "phone": "",

        
                "email": "",

        
                "website": ""

        
            },

        
            "colors": {

        
                "primary": "#1e3a8a",

        
                "secondary": "#3b82f6",

        
                "accent": "#60a5fa",

        
                "text": "#000000",

        
                "background": "#ffffff",

        
                "success": "#22c55e",

        
                "warning": "#f59e0b",

        
                "error": "#ef4444"

        
            },

        
            "logos": {

        
                "primary": "",

        
                "secondary": "",

        
                "favicon": "",

        
                "watermark": ""

        
            },

        
            "fonts": {

        
                "heading": "Helvetica",

        
                "body": "Helvetica",

        
                "monospace": "Courier"

        
            },

        
            "report_templates": {

        
                "margins": {"top": 72, "bottom": 72, "left": 72, "right": 72},

        
                "header_height": 60,

        
                "footer_height": 40,

        
                "watermark_opacity": 0.1

        
            },

        
            "email_templates": {

        
                "signature": "Best regards,\nDeep Blue Pool Chemistry Team",

        
                "disclaimer": "This report is generated automatically."

        
            }

        
        }

        
        self.branding_file = "branding_config.json"

        

        
        logger.info("Branding configuration initialized")

        
        

        
        # Check for snoozed alerts to reactivate (Phase 1.2)
        reactivated = self._check_snoozed_alerts()
        if reactivated:
            logger.info(f"Reactivated {len(reactivated)} snoozed alerts")

        # Initialize multi-pool system
        self._initialize_pools()
        self.customer_file = self.data_dir / "customer_info.json"
        self.readings_file = self.data_dir / "readings.json"  # Use JSON file for readings
        self.settings_file = self.data_dir / "settings.json"
        self._stop_threads = threading.Event()
        self.serial_conn = None
        self.arduino_thread = None
        self.weather_data = None
        self.zip_code = tk.StringVar(value="")
        self.weather_update_id = None
        self.datetime_update_id = None
        self.task_check_id = None
        self.alert_check_id = None
        self.backup_id = None
        self.fig = None
        self.ax = None
        self.canvas = None
        self.auto_backup_var = tk.BooleanVar(value=True)
        self.gui_initialized = False  # Flag to track GUI initialization status
        
        # Initialize ML and Weather Impact Analyzers
        self.pool_analytics = PoolAnalyticsEngineV2()
        
        # Initialize test strip analyzer
        try:
            from test_strip_analyzer import TestStripAnalyzer
            self.test_strip_analyzer = TestStripAnalyzer()
            logger.info("Test strip analyzer initialized successfully")
        except Exception as e:
            self.test_strip_analyzer = None
            logger.warning(f"Test strip analyzer not available: {e}")
        self.weather_impact_analyzer = WeatherImpactAnalyzer()




    def _configure_colors(self):
        """Configure color scheme."""
        self.colors = COLOR_SCHEME

    def _configure_styles(self):
        """Configure custom styles for the application"""
        self.style = ttk.Style()
        
        # Set default theme
        try:
            self.style.theme_use('clam')
        except Exception as e:
            self.style.theme_use('clam')
        
        # Configure custom colors
        bg_color = "#F0F4F8"  # Light blue-gray background
        fg_color = "#2C3E50"  # Dark blue-gray text
        accent_color = "#3498DB"  # Bright blue accent
        success_color = "#27AE60"  # Green
        warning_color = "#E67E22"  # Orange
        danger_color = "#E74C3C"  # Red
        
        # Configure TFrame
        self.style.configure('TFrame', background=bg_color)
        
        # Configure TLabel
        self.style.configure('TLabel', 
                           background=bg_color, 
                           foreground=fg_color,
                           font=('Arial', 10))
        
        # Configure TButton
        self.style.configure('TButton',
                           background=accent_color,
                           foreground='white',
                           borderwidth=1,
                           focuscolor='none',
                           font=('Arial', 10, 'bold'))
        
        self.style.map('TButton',
                      background=[('active', '#2980B9'), ('pressed', '#21618C')])
        
        # Configure TEntry
        self.style.configure('TEntry',
                           fieldbackground='white',
                           foreground=fg_color,
                           borderwidth=2)
        
        # Configure TLabelframe
        self.style.configure('TLabelframe',
                           background=bg_color,
                           foreground=fg_color,
                           borderwidth=2,
                           relief='groove')
        
        self.style.configure('TLabelframe.Label',
                           background=bg_color,
                           foreground=accent_color,
                           font=('Arial', 11, 'bold'))
        
        # Configure TNotebook
        self.style.configure('TNotebook',
                           background=bg_color,
                           borderwidth=0)
        
        self.style.configure('TNotebook.Tab',
                           background='#D5DBDB',
                           foreground=fg_color,
                           padding=[20, 10],
                           font=('Arial', 10, 'bold'))
        
        self.style.map('TNotebook.Tab',
                      background=[('selected', accent_color)],
                      foreground=[('selected', 'white')])
        
        # Configure Treeview
        self.style.configure('Treeview',
                           background='white',
                           foreground=fg_color,
                           fieldbackground='white',
                           borderwidth=2)
        
        self.style.configure('Treeview.Heading',
                           background=accent_color,
                           foreground='white',
                           font=('Arial', 10, 'bold'))
        
        self.style.map('Treeview.Heading',
                      background=[('active', '#2980B9')])
        
        # Custom styles for status indicators
        self.style.configure('Success.TLabel',
                           foreground=success_color,
                           font=('Arial', 11, 'bold'))
        
        self.style.configure('Warning.TLabel',
                           foreground=warning_color,
                           font=('Arial', 11, 'bold'))
        
        self.style.configure('Danger.TLabel',
                           foreground=danger_color,
                           font=('Arial', 11, 'bold'))

    def _create_menu_bar(self):
        """Create the application menu bar"""
        menubar = tk.Menu(self)
        self.config(menu=menubar)
        
        # File Menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Exit", command=self._on_close, accelerator="Alt+F4")
        
        # Help Menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="User Guide", command=self._show_user_guide)
        help_menu.add_command(label="Quick Start", command=self._show_quick_start)
        help_menu.add_command(label="Chemical Ranges", command=self._show_chemical_ranges)
        help_menu.add_separator()
        help_menu.add_command(label="About", command=self._show_about)
    
    def _show_user_guide(self):
        """Show comprehensive user guide - Opens PDF file"""
        import subprocess
        import platform
        
        pdf_path = os.path.join(os.path.dirname(__file__), "DEEP_BLUE_COMPREHENSIVE_USER_GUIDE.pdf")
        
        if not os.path.exists(pdf_path):
            messagebox.showwarning(
                "User Guide Not Found",
                f"The comprehensive user guide PDF was not found.\n\n"
                f"Expected location: {pdf_path}\n\n"
                f"Please ensure DEEP_BLUE_COMPREHENSIVE_USER_GUIDE.pdf is in the same folder as this application."
            )
            return
        
        try:
            # Open PDF with default application
            if platform.system() == 'Windows':
                os.startfile(pdf_path)
            elif platform.system() == 'Darwin':  # macOS
                subprocess.run(['open', pdf_path])
            else:  # Linux
                subprocess.run(['xdg-open', pdf_path])
            
            self.logger.info("Opened comprehensive user guide PDF")
        except Exception as e:
            self.logger.error(f"Error opening user guide: {e}")
            messagebox.showerror(
                "Error Opening Guide",
                f"Could not open the user guide PDF.\n\n"
                f"Error: {str(e)}\n\n"
                f"Please open the file manually: {pdf_path}"
            )
    def _show_quick_start(self):
        """Show quick start guide - Opens PDF file"""
        import subprocess
        import platform
        
        pdf_path = os.path.join(os.path.dirname(__file__), "DEEP_BLUE_QUICK_START_GUIDE.pdf")
        
        if not os.path.exists(pdf_path):
            messagebox.showwarning(
                "Quick Start Guide Not Found",
                f"The quick start guide PDF was not found.\n\n"
                f"Expected location: {pdf_path}\n\n"
                f"Please ensure DEEP_BLUE_QUICK_START_GUIDE.pdf is in the same folder as this application."
            )
            return
        
        try:
            # Open PDF with default application
            if platform.system() == 'Windows':
                os.startfile(pdf_path)
            elif platform.system() == 'Darwin':  # macOS
                subprocess.run(['open', pdf_path])
            else:  # Linux
                subprocess.run(['xdg-open', pdf_path])
            
            self.logger.info("Opened quick start guide PDF")
        except Exception as e:
            self.logger.error(f"Error opening quick start guide: {e}")
            messagebox.showerror(
                "Error Opening Guide",
                f"Could not open the quick start guide PDF.\n\n"
                f"Error: {str(e)}\n\n"
                f"Please open the file manually: {pdf_path}"
            )
    def _show_chemical_ranges(self):
        """Show detailed chemical ranges reference"""
        ranges_window = tk.Toplevel(self)
        ranges_window.title("Chemical Ranges Reference")
        ranges_window.geometry("700x600")
        
        # Create main frame with canvas for scrolling
        main_frame = tk.Frame(ranges_window)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        canvas = tk.Canvas(main_frame, bg="white")
        scrollbar = tk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="white")
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Title
        title = tk.Label(scrollable_frame, text="Chemical Ranges Reference", 
                        font=("Arial", 16, "bold"), bg="white", fg="#2c3e50")
        title.pack(pady=10)
        
        # Chemical ranges data
        ranges = [
            {
                "name": "pH",
                "ideal": "7.2 - 7.8",
                "unit": "",
                "low_effects": "Corrosive to equipment, eye/skin irritation, rapid chlorine loss",
                "high_effects": "Cloudy water, scaling, reduced chlorine effectiveness",
                "adjust_up": "Soda Ash (Sodium Carbonate)",
                "adjust_down": "Muriatic Acid or Sodium Bisulfate"
            },
            {
                "name": "Free Chlorine",
                "ideal": "1.0 - 3.0 ppm",
                "unit": "ppm",
                "low_effects": "Bacteria growth, algae formation, unsafe water",
                "high_effects": "Skin/eye irritation, bleached swimwear, strong odor",
                "adjust_up": "Chlorine tablets, liquid chlorine, or shock",
                "adjust_down": "Time (natural dissipation) or sodium thiosulfate"
            },
            {
                "name": "Total Chlorine",
                "ideal": "1.0 - 3.0 ppm",
                "unit": "ppm",
                "low_effects": "Same as Free Chlorine",
                "high_effects": "Indicates chloramines if much higher than Free Chlorine",
                "adjust_up": "Same as Free Chlorine",
                "adjust_down": "Shock treatment to break chloramines"
            },
            {
                "name": "Alkalinity",
                "ideal": "80 - 120 ppm",
                "unit": "ppm",
                "low_effects": "pH instability, corrosion, staining",
                "high_effects": "Cloudy water, scaling, pH difficult to adjust",
                "adjust_up": "Sodium Bicarbonate (Baking Soda)",
                "adjust_down": "Muriatic Acid"
            },
            {
                "name": "Calcium Hardness",
                "ideal": "200 - 400 ppm",
                "unit": "ppm",
                "low_effects": "Corrosive to equipment, etching of plaster",
                "high_effects": "Cloudy water, scaling on surfaces and equipment",
                "adjust_up": "Calcium Chloride",
                "adjust_down": "Partial drain and refill with softer water"
            },
            {
                "name": "Cyanuric Acid",
                "ideal": "30 - 50 ppm",
                "unit": "ppm",
                "low_effects": "Chlorine burns off quickly from UV rays",
                "high_effects": "Reduces chlorine effectiveness, algae growth",
                "adjust_up": "Cyanuric Acid (Stabilizer)",
                "adjust_down": "Partial drain and refill"
            },
            {
                "name": "Temperature",
                "ideal": "76 - 84°FF",
                "unit": "°FF",
                "low_effects": "Uncomfortable swimming, slower chemical reactions",
                "high_effects": "Faster chemical consumption, bacteria growth",
                "adjust_up": "Pool heater",
                "adjust_down": "Shade, cooler weather, or aerator"
            },
            {
                "name": "Bromine",
                "ideal": "2.0 - 4.0 ppm",
                "unit": "ppm",
                "low_effects": "Inadequate sanitization",
                "high_effects": "Skin/eye irritation",
                "adjust_up": "Bromine tablets or granules",
                "adjust_down": "Time (natural dissipation)"
            },
            {
                "name": "Salt",
                "ideal": "2700 - 3400 ppm",
                "unit": "ppm",
                "low_effects": "Salt generator won't produce chlorine",
                "high_effects": "Corrosion, salty taste",
                "adjust_up": "Pool salt",
                "adjust_down": "Partial drain and refill"
            }
        ]
        
        for chemical in ranges:
            # Create frame for each chemical
            chem_frame = tk.LabelFrame(scrollable_frame, text=f"{chemical['name']} ({chemical['unit']})",
                                      font=("Arial", 12, "bold"), bg="white", fg="#2c3e50",
                                      padx=10, pady=10)
            chem_frame.pack(fill="x", padx=10, pady=5)
            
            # Ideal range
            ideal_label = tk.Label(chem_frame, text=f"Ideal Range: {chemical['ideal']}",
                                  font=("Arial", 10, "bold"), bg="white", fg="#27ae60")
            ideal_label.pack(anchor="w")
            
            # Low effects
            low_frame = tk.Frame(chem_frame, bg="white")
            low_frame.pack(fill="x", pady=2)
            tk.Label(low_frame, text="Too Low:", font=("Arial", 9, "bold"), 
                    bg="white", fg="#e74c3c").pack(side="left")
            tk.Label(low_frame, text=chemical['low_effects'], font=("Arial", 9),
                    bg="white", wraplength=500, justify="left").pack(side="left", padx=5)
            
            # High effects
            high_frame = tk.Frame(chem_frame, bg="white")
            high_frame.pack(fill="x", pady=2)
            tk.Label(high_frame, text="Too High:", font=("Arial", 9, "bold"),
                    bg="white", fg="#e74c3c").pack(side="left")
            tk.Label(high_frame, text=chemical['high_effects'], font=("Arial", 9),
                    bg="white", wraplength=500, justify="left").pack(side="left", padx=5)
            
            # Adjustments
            adj_up_frame = tk.Frame(chem_frame, bg="white")
            adj_up_frame.pack(fill="x", pady=2)
            tk.Label(adj_up_frame, text="Increase:", font=("Arial", 9, "bold"),
                    bg="white", fg="#3498db").pack(side="left")
            tk.Label(adj_up_frame, text=chemical['adjust_up'], font=("Arial", 9),
                    bg="white").pack(side="left", padx=5)
            
            adj_down_frame = tk.Frame(chem_frame, bg="white")
            adj_down_frame.pack(fill="x", pady=2)
            tk.Label(adj_down_frame, text="Decrease:", font=("Arial", 9, "bold"),
                    bg="white", fg="#3498db").pack(side="left")
            tk.Label(adj_down_frame, text=chemical['adjust_down'], font=("Arial", 9),
                    bg="white").pack(side="left", padx=5)
        
        # Close button
        close_btn = tk.Button(ranges_window, text="Close", command=ranges_window.destroy,
                             font=("Arial", 10, "bold"), bg="#3498db", fg="white",
                             padx=20, pady=5)
        close_btn.pack(pady=10)
    
    def _show_about(self):
        """Show About dialog with Michael Hayes copyright"""
        about_window = tk.Toplevel(self)
        about_window.title("About Deep Blue")
        about_window.geometry("500x450")
        about_window.resizable(False, False)
        
        # Center the window
        about_window.transient(self)
        about_window.grab_set()
        
        # Main frame
        main_frame = tk.Frame(about_window, bg="white")
        main_frame.pack(fill="both", expand=True)
        
        # Header with color
        header_frame = tk.Frame(main_frame, bg="#1e5a8e", height=100)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        tk.Label(header_frame, text="DEEP BLUE",
                font=("Arial", 24, "bold"), bg="#1e5a8e", fg="white").pack(pady=10)
        
        tk.Label(header_frame, text="Pool Chemistry Management System",
                font=("Arial", 12), bg="#1e5a8e", fg="#b3d9ff").pack()
        
        # Content
        content_frame = tk.Frame(main_frame, bg="white")
        content_frame.pack(fill="both", expand=True, padx=30, pady=20)
        
        # Version
        tk.Label(content_frame, text=f"Version {__version__}",
                font=("Arial", 11), bg="white", fg="#666").pack(pady=10)
        
        # Separator
        separator1 = tk.Frame(content_frame, height=2, bg="#e0e0e0")
        separator1.pack(fill="x", pady=15)
        
        # COPYRIGHT SECTION - PROMINENT
        copyright_frame = tk.Frame(content_frame, bg="white")
        copyright_frame.pack(pady=15)
        
        tk.Label(copyright_frame, text="Copyright © 2024 Michael Hayes",
                font=("Arial", 12, "bold"), bg="white", fg="#000").pack()
        
        tk.Label(copyright_frame, text="All Rights Reserved",
                font=("Arial", 10, "bold"), bg="white", fg="#333").pack(pady=(5, 0))
        
        # Separator
        separator2 = tk.Frame(content_frame, height=2, bg="#e0e0e0")
        separator2.pack(fill="x", pady=15)
        
        # Proprietary notice
        proprietary_text = """This software is proprietary and confidential.
Unauthorized copying, distribution, or use
is strictly prohibited."""
        
        tk.Label(content_frame, text=proprietary_text,
                font=("Arial", 9), bg="white", fg="#666",
                justify="center").pack(pady=10)
        
        # Owner
        tk.Label(content_frame, text="Owner: Michael Hayes",
                font=("Arial", 11, "bold"), bg="white", fg="#1e5a8e").pack(pady=10)
        
        # Close button
        close_btn = tk.Button(content_frame, text="Close", command=about_window.destroy,
                            font=("Arial", 10, "bold"), bg="#1e5a8e", fg="white",
                            padx=40, pady=10, relief="flat", cursor="hand2")
        close_btn.pack(pady=20)
        
        # Center the window on screen
        about_window.update_idletasks()
        x = (about_window.winfo_screenwidth() // 2) - (about_window.winfo_width() // 2)
        y = (about_window.winfo_screenheight() // 2) - (about_window.winfo_height() // 2)
        about_window.geometry(f"+{x}+{y}")

    def _create_header(self):
        """Create the application header."""
        header_frame = ttk.Frame(self)
        header_frame.pack(fill="x", padx=10, pady=5)

        title_label = ttk.Label(
            header_frame,
            text="Deep Blue Chemistry",
            style="Header.TLabel"
        )
        title_label.pack(side="left")

        self.datetime_label = ttk.Label(header_frame, text=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        self.datetime_label.pack(side="right")

    def _create_main_content(self):
        """Create the main content area."""
        main_frame = ttk.Frame(self)
        main_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill="both", expand=True)

        # Add pool selector at top
        self.pool_selector_frame = tk.Frame(self, bg="#2c3e50", height=50)
        self.pool_selector_frame.pack(side=tk.TOP, fill=tk.X, before=self.notebook)
        self._create_pool_selector(self.pool_selector_frame)

        self.dashboard_tab = ttk.Frame(self.notebook)
        self.readings_tab = ttk.Frame(self.notebook)
        self.analytics_tab = ttk.Frame(self.notebook)
        self.weather_impacts_tab = ttk.Frame(self.notebook)
        self.history_tab = ttk.Frame(self.notebook)
        self.cost_tracking_tab = ttk.Frame(self.notebook)
        self.inventory_tab = ttk.Frame(self.notebook)
        self.shopping_list_tab = ttk.Frame(self.notebook)
        self.settings_tab = ttk.Frame(self.notebook)

        self.notebook.add(self.dashboard_tab, text="Dashboard")
        self.notebook.add(self.readings_tab, text="Water Testing")
        self.notebook.add(self.analytics_tab, text="ML Analytics")
        self.notebook.add(self.weather_impacts_tab, text="Weather Impacts")
        
        # Arduino Setup tab
        self.arduino_setup_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.arduino_setup_tab, text="Arduino Setup")
        self.notebook.add(self.history_tab, text="History")
        self.notebook.add(self.cost_tracking_tab, text="💰 Cost Tracking")
        self.notebook.add(self.inventory_tab, text="📦 Inventory")
        self.notebook.add(self.shopping_list_tab, text="🛒 Shopping List")

        # Branding Configuration Tab
        self.branding_frame = tk.Frame(self.notebook)
        self.notebook.add(self.branding_frame, text="🎨 Branding Configuration")
        self._create_branding_tab()


        # Keyboard shortcuts for History tab
        self.bind('<F5>', lambda e: self._refresh_analytics_dashboard())
        self.bind('<Control-e>', lambda e: self._export_analytics_report())
        self.bind('<Control-r>', lambda e: self._refresh_analytics_dashboard())
        # Notifications Tab
        self.notifications_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.notifications_tab, text="Notifications")

        
        # Alert History tab (Phase 1.1 - replaced by Phase 1.2)
        # self._create_alerts_history_tab()  # Replaced by Phase 1.2
        self._create_alert_config_tab()
        self._create_enhanced_alert_history_tab()
        # PDF Reports tab (Phase 2.1)
        self.pdf_reports_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.pdf_reports_tab, text="📄 PDF Reports")
        self._create_pdf_reports_tab()
        self._create_branding_tab()


        
        self.notebook.add(self.settings_tab, text="Settings")

        self._create_dashboard_tab()
        self._create_readings_tab()
        self._create_analytics_tab()
        self._create_weather_impacts_tab()
        self._create_arduino_setup_tab()
        self._create_history_tab()
        self._create_cost_tracking_tab()
        self._create_inventory_tab()
        self._create_shopping_list_tab()
        self._create_settings_tab()
        
        # Initialize messaging service BEFORE creating notifications tab
        try:
            from messaging_service import MessagingService
            self.messaging_service = MessagingService()
            self.messaging_enabled = True
        except Exception as e:
            print(f"Messaging service not available: {e}")
            self.messaging_service = None
            self.messaging_enabled = False
        
        self._create_notifications_tab()

        self.gui_initialized = True  # Mark GUI as initialized

        # Close splash screen
        self.splash.update_status("Ready!")
        self.after(5000, self._close_splash_and_show_main)  # 5 seconds - Change this number to adjust splash duration (in milliseconds)

    def _close_splash_and_show_main(self):
        """Close splash screen and show main window"""
        try:
            self.splash.close()
        except (AttributeError, RuntimeError, tk.TclError):
            pass
        
        self.deiconify()  # Show main window
        self.lift()  # Bring to front
        self.focus_force()  # Give focus

    
    def _create_dashboard_tab(self):
        """Create the dashboard tab content"""
        # Customer info section
        customer_frame = ttk.LabelFrame(self.dashboard_tab, text="Customer Information")
        customer_frame.pack(fill="x", padx=5, pady=5)
        
        # Customer name
        ttk.Label(customer_frame, text="Name:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.customer_name_entry = ttk.Entry(customer_frame, width=30)
        self.customer_name_entry.grid(row=0, column=1, sticky="w", padx=5, pady=2)
        self.entries["customer_name"] = self.customer_name_entry

        # --- START: Address Fields (No Verification) ---
        # These fields are still present in the UI for data entry, but no API verification is performed.
        ttk.Label(customer_frame, text="Address Line 1:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.address1_entry = ttk.Entry(customer_frame, width=30)
        self.address1_entry.grid(row=1, column=1, sticky="w", padx=5, pady=2)

        ttk.Label(customer_frame, text="Address Line 2:").grid(row=2, column=0, sticky="w", padx=5, pady=2)
        self.address2_entry = ttk.Entry(customer_frame, width=30)
        self.address2_entry.grid(row=2, column=1, sticky="w", padx=5, pady=2)

        ttk.Label(customer_frame, text="City:").grid(row=1, column=2, sticky="w", padx=5, pady=2)
        self.city_entry = ttk.Entry(customer_frame, width=20)
        self.city_entry.grid(row=1, column=3, sticky="w", padx=5, pady=2)

        ttk.Label(customer_frame, text="State:").grid(row=2, column=2, sticky="w", padx=5, pady=2)
        self.state_entry = ttk.Entry(customer_frame, width=10)
        self.state_entry.grid(row=2, column=3, sticky="w", padx=5, pady=2)

        ttk.Label(customer_frame, text="Postal Code:").grid(row=1, column=4, sticky="w", padx=5, pady=2)
        self.postal_code_entry = ttk.Entry(customer_frame, width=10)
        self.postal_code_entry.grid(row=1, column=5, sticky="w", padx=5, pady=2)

        ttk.Label(customer_frame, text="Country:").grid(row=2, column=4, sticky="w", padx=5, pady=2)
        self.country_entry = ttk.Entry(customer_frame, width=10)
        self.country_entry.insert(0, "US") # Default to US
        self.country_entry.grid(row=2, column=5, sticky="w", padx=5, pady=2)

        # REMOVED: self.verify_address_button and self.address_verification_status_label
        # --- END: Address Fields (No Verification) ---
        
        # Pool info section
        pool_frame = ttk.LabelFrame(self.dashboard_tab, text="Pool Information")
        pool_frame.pack(fill="x", padx=5, pady=5)
        
        # Pool type
        ttk.Label(pool_frame, text="Pool Type:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.pool_type_var = tk.StringVar()
        self.pool_type_combo = ttk.Combobox(
            pool_frame, 
            textvariable=self.pool_type_var,
            values=["Concrete/Gunite", "Vinyl", "Fiberglass", "Above Ground"]
        )
        self.pool_type_combo.grid(row=0, column=1, sticky="w", padx=5, pady=2)
        
        # Pool size
        ttk.Label(pool_frame, text="Size (gallons):").grid(row=0, column=2, sticky="w", padx=5, pady=2)
        self.pool_size_entry = ttk.Entry(pool_frame, width=10)
        self.pool_size_entry.grid(row=0, column=3, sticky="w", padx=5, pady=2)
        
        # Weather section
        weather_frame = ttk.LabelFrame(self.dashboard_tab, text="Weather Information")
        weather_frame.pack(fill="x", padx=5, pady=5)
        
        # ZIP code entry
        ttk.Label(weather_frame, text="ZIP Code:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.zip_entry = ttk.Entry(weather_frame, width=10, textvariable=self.zip_code)
        self.zip_entry.grid(row=0, column=1, sticky="w", padx=5, pady=2)
        
        # Weather update button
        self.weather_button = ttk.Button(
            weather_frame, 
            text="Update Weather",
            command=lambda: self._update_weather() # FIX: Use lambda to defer method call
        )
        self.weather_button.grid(row=0, column=2, sticky="w", padx=5, pady=2)
        
        # Weather display
        self.weather_display_frame = ttk.Frame(weather_frame)
        self.weather_display_frame.grid(row=1, column=0, columnspan=3, sticky="ew", padx=5, pady=5)
        
        # Configure column to expand
        weather_frame.columnconfigure(0, weight=1)
        
        # Status section
        status_frame = ttk.LabelFrame(self.dashboard_tab, text="System Status")
        status_frame.pack(fill="x", padx=5, pady=5)
        
        # Status label
        self.status_label = ttk.Label(status_frame, textvariable=self.status_var)
        self.status_label.pack(padx=5, pady=5)
    
    # REMOVED: _verify_customer_address method
    
    def _create_readings_tab(self):
        """Create the water testing tab content"""
        # ========== INPUT METHOD SELECTOR ==========
        input_method_frame = tk.LabelFrame(
            self.readings_tab,
            text="Input Method - Choose How to Enter Data",
            font=("Arial", 12, "bold"),
            bg="white",
            padx=15,
            pady=15
        )
        input_method_frame.pack(fill="x", padx=5, pady=5)
        
        self.input_method_var = tk.StringVar(value="manual")
        
        methods_frame = tk.Frame(input_method_frame, bg="white")
        methods_frame.pack(fill="x")
        
        tk.Radiobutton(
            methods_frame,
            text="Manual Entry",
            variable=self.input_method_var,
            value="manual",
            font=("Arial", 10),
            bg="white",
            command=self._on_input_method_change
        ).pack(side="left", padx=10)
        
        tk.Radiobutton(
            methods_frame,
            text="Upload Test Strip",
            variable=self.input_method_var,
            value="upload",
            font=("Arial", 10),
            bg="white",
            command=self._on_input_method_change
        ).pack(side="left", padx=10)
        
        tk.Radiobutton(
            methods_frame,
            text="Camera Capture",
            variable=self.input_method_var,
            value="camera",
            font=("Arial", 10),
            bg="white",
            command=self._on_input_method_change
        ).pack(side="left", padx=10)
        
        tk.Radiobutton(
            methods_frame,
            text="Arduino Sensors",
            variable=self.input_method_var,
            value="arduino",
            font=("Arial", 10),
            bg="white",
            command=self._on_input_method_change
        ).pack(side="left", padx=10)
        
        buttons_frame = tk.Frame(input_method_frame, bg="white")
        buttons_frame.pack(fill="x", pady=10)
        
        self.upload_strip_btn = tk.Button(
            buttons_frame,
            text="Select Image",
            font=("Arial", 10, "bold"),
            bg="#27ae60",
            fg="white",
            padx=15,
            pady=5,
            command=self._upload_strip_for_testing,
            state="disabled"
        )
        self.upload_strip_btn.pack(side="left", padx=5)
        
        self.camera_strip_btn = tk.Button(
            buttons_frame,
            text="Take Picture",
            font=("Arial", 10, "bold"),
            bg="#9b59b6",
            fg="white",
            padx=15,
            pady=5,
            command=self._camera_strip_for_testing,
            state="disabled"
        )
        self.camera_strip_btn.pack(side="left", padx=5)
        
        self.arduino_read_btn = tk.Button(
            buttons_frame,
            text="Read Sensors",
            font=("Arial", 10, "bold"),
            bg="#e67e22",
            fg="white",
            padx=15,
            pady=5,
            command=self._read_arduino_sensors,
            state="disabled"
        )
        self.arduino_read_btn.pack(side="left", padx=5)
        
        self.input_status_label = tk.Label(
            input_method_frame,
            text="Enter values manually below",
            font=("Arial", 9, "italic"),
            bg="white",
            fg="#7f8c8d"
        )
        self.input_status_label.pack(pady=5)
        
        # Chemical readings frame (at top)
        readings_frame = ttk.LabelFrame(self.readings_tab, text="Chemical Readings")
        readings_frame.pack(fill="x", padx=5, pady=5)
        
        # Create a grid of chemical reading inputs
        chemicals = [
            ("pH", "ph", ""),
            ("Free Chlorine", "free_chlorine", "ppm"),
            ("Total Chlorine", "total_chlorine", "ppm"),
            ("Alkalinity", "alkalinity", "ppm"),
            ("Calcium Hardness", "calcium_hardness", "ppm"),
            ("Cyanuric Acid", "cyanuric_acid", "ppm"),
            ("Salt", "salt", "ppm"),
            ("Bromine", "bromine", "ppm"),
            ("Temperature", "temperature", "°FF")
        ]
        
        # Create the entries
        for i, (label_text, field_name, unit) in enumerate(chemicals):
            row = i // 4  # Calculate row for grid layout
            col = (i % 4) * 3  # Calculate column for grid layout
            
            # Label
            ttk.Label(readings_frame, text=label_text).grid(
                row=row, column=col, sticky="w", padx=5, pady=2
            )
            
            # Entry
            entry = ttk.Entry(readings_frame, width=8)
            entry.grid(row=row, column=col+1, sticky="w", padx=5, pady=2)
            self.entries[field_name] = entry
            
            # Unit label
            if unit:
                ttk.Label(readings_frame, text=unit).grid(
                    row=row, column=col+2, sticky="w", padx=0, pady=2
                )
        
        # Buttons frame
        buttons_frame = ttk.Frame(self.readings_tab)
        buttons_frame.pack(fill="x", padx=5, pady=10)
        
        # Calculate button
        self.calculate_button = ttk.Button(
            buttons_frame,
            text="Calculate Adjustments",
            command=self._calculate_adjustments
        )
        self.calculate_button.pack(side="left", padx=5)
        
        # Save button
        self.save_button = ttk.Button(
            buttons_frame,
            text="Save Readings",
            command=self._save_readings
        )
        self.save_button.pack(side="left", padx=5)
        
        # Clear button
        self.clear_button = ttk.Button(
            buttons_frame,
            text="Clear",
            command=self._clear_readings
        )
        self.clear_button.pack(side="left", padx=5)
        


        
        # Results frame - SIDE BY SIDE LAYOUT
        results_frame = ttk.LabelFrame(self.readings_tab, text="Recommendations & Visual Test Strips")
        results_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Create two-column layout using PanedWindow for resizable split
        paned_window = ttk.PanedWindow(results_frame, orient=tk.HORIZONTAL)
        paned_window.pack(fill="both", expand=True, padx=5, pady=5)
        
        # LEFT SIDE: Chemical Adjustments (wider - 75%)
        left_frame = ttk.Frame(paned_window)
        paned_window.add(left_frame, weight=3)
        
        # Header for adjustments
        adjustments_header = tk.Frame(left_frame, bg="#3498db", height=40)
        adjustments_header.pack(fill="x")
        adjustments_header.pack_propagate(False)
        
        tk.Label(
            adjustments_header,
            text="Recommended Chemical Adjustments",
            font=("Arial", 12, "bold"),
            fg="white",
            bg="#3498db"
        ).pack(pady=8)
        
        # Adjustments frame for displaying recommendations
        # Create a container for adjustments with Pool Health Scoreboard
        adjustments_container = ttk.Frame(left_frame)
        adjustments_container.pack(fill="both", expand=True, padx=2, pady=2)
        
        # LEFT: Adjustments list with warnings/precautions (65%)
        self.adjustments_frame = ttk.Frame(adjustments_container)
        self.adjustments_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        # RIGHT: Pool Health Scoreboard (35%)
        self.health_score_frame = ttk.Frame(adjustments_container, relief="solid", borderwidth=2, width=400)
        self.health_score_frame.configure(height=420)  # Ensure enough height
        self.health_score_frame.pack(side="left", fill="y", padx=(5, 0))
        self.health_score_frame.pack_propagate(False)  # Maintain fixed width
        self._create_pool_health_scoreboard()
        
        # RIGHT SIDE: Visual Test Strips (narrower - 25%)
        right_frame = ttk.Frame(paned_window)
        paned_window.add(right_frame, weight=1)
        
        # Header for test strips
        test_strips_header = tk.Frame(right_frame, bg="#764ba2", height=40)
        test_strips_header.pack(fill="x")
        test_strips_header.pack_propagate(False)
        
        tk.Label(
            test_strips_header,
            text="Visual Test Strips",
            font=("Arial", 12, "bold"),
            fg="white",
            bg="#764ba2"
        ).pack(pady=8)
        
        # Test strips container
        self.test_strips_container = ttk.Frame(right_frame)

        # Visual Test Strips - NO SCROLLBAR, fills area, all 9 metrics
        strips_main = tk.Frame(self.test_strips_container, bg='white')
        strips_main.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # Title
        tk.Label(strips_main, text="Visual Test Strips", 
                font=('Arial', 13, 'bold'), bg='white', fg='#764ba2').pack(pady=(8, 5))
        
        # Legend
        legend_frame = tk.Frame(strips_main, bg='white')
        legend_frame.pack(pady=(0, 8))
        
        for text, color in [("Good", "#28a745"), ("Low", "#ffc107"), ("High", "#dc3545")]:
            item_frame = tk.Frame(legend_frame, bg='white')
            item_frame.pack(side=tk.LEFT, padx=8)
            tk.Label(item_frame, text="  ", bg=color, relief=tk.RAISED, bd=1).pack(side=tk.LEFT, padx=(0, 4))
            tk.Label(item_frame, text=text, font=('Arial', 9), bg='white').pack(side=tk.LEFT)
        
        # Strips container - 3 columns, 3 rows for 9 metrics
        strips_frame = tk.Frame(strips_main, bg='white')
        strips_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Configure grid - 3 columns, 3 rows
        for i in range(3):
            strips_frame.columnconfigure(i, weight=1, uniform="col")
            strips_frame.rowconfigure(i, weight=1, uniform="row")
        
        # All 9 metrics in 3x3 grid
        strip_params = [
            ('pH', 'ph', 7.2, 7.8),
            ('Free Chlorine', 'free_chlorine', 1.0, 3.0),
            ('Total Chlorine', 'total_chlorine', 1.0, 3.0),
            ('Total Alkalinity', 'alkalinity', 80, 120),
            ('Calcium Hardness', 'calcium_hardness', 200, 400),
            ('Cyanuric Acid', 'cyanuric_acid', 30, 50),
            ('Temperature', 'temperature', 78, 82),
            ('Bromine', 'bromine', 2.0, 4.0),
            ('Salt', 'salt', 2700, 3400)
        ]
        
        self.strip_widgets = {}
        
        for idx, (label, key, min_val, max_val) in enumerate(strip_params):
            row = idx // 3
            col = idx % 3
            
            # Card frame with border
            card = tk.Frame(strips_frame, bg='white', relief=tk.RIDGE, bd=2)
            card.grid(row=row, column=col, padx=4, pady=4, sticky='nsew')
            
            # Metric name
            tk.Label(card, text=label, font=('Arial', 10, 'bold'),
                    bg='white', fg='#333').pack(pady=(6, 3))
            
            # Value display
            value_label = tk.Label(card, text="NO DATA", font=('Arial', 16, 'bold'),
                                  bg='white', fg='#666')
            value_label.pack(pady=3)
            
            # Unit
            unit_text = "ppm"
            if key == 'ph':
                unit_text = ""
            elif key == 'temperature':
                unit_text = "°FF"
            
            if unit_text:
                tk.Label(card, text=unit_text, font=('Arial', 8), 
                        bg='white', fg='#999').pack(pady=1)
            
            # Status badge
            status_label = tk.Label(card, text="", font=('Arial', 8, 'bold'),
                                   bg='white', fg='white', relief=tk.RAISED, bd=1,
                                   padx=10, pady=3)
            status_label.pack(pady=(3, 6))
            
            # Range label
            if key == 'ph':
                range_text = f"Range: {min_val}-{max_val}"
            elif key == 'temperature':
                range_text = f"Range: {min_val}-{max_val}°FF"
            else:
                range_text = f"Range: {int(min_val)}-{int(max_val)}"
            
            tk.Label(card, text=range_text, font=('Arial', 7), 
                    bg='white', fg='#666').pack(pady=(0, 4))
            
            self.strip_widgets[key] = {
                'value': value_label,
                'status': status_label,
                'min': min_val,
                'max': max_val
            }

        self.test_strips_container.pack(fill="both", expand=True, padx=2, pady=2)
        
        # Create initial empty state


# NEW ANALYTICS DASHBOARD - Complete replacement for History Tab
# This will be integrated into main_app.py

    def _create_history_tab(self):
        """Create comprehensive Analytics Dashboard tab"""
        self.splash.update_status("Creating Analytics Dashboard...")
        logger.info("Creating Analytics Dashboard...")
        
        # Main container with canvas for scrolling
        main_canvas = tk.Canvas(self.history_tab, bg="#f0f4f8")
        main_scrollbar = ttk.Scrollbar(self.history_tab, orient="vertical", command=main_canvas.yview)
        scrollable_frame = ttk.Frame(main_canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        )
        
        main_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        main_canvas.configure(yscrollcommand=main_scrollbar.set)
        
        # Pack canvas and scrollbar
        main_canvas.pack(side="left", fill="both", expand=True)
        main_scrollbar.pack(side="right", fill="y")
        
        # Enable mouse wheel scrolling
        def _on_mousewheel(event):
            main_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        main_canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # ========== HEADER SECTION ==========
        header_frame = tk.Frame(scrollable_frame, bg="#2c3e50", height=80)
        header_frame.pack(fill="x", padx=0, pady=0)
        header_frame.pack_propagate(False)
        
        tk.Label(
            header_frame,
            text="Pool Analytics Dashboard",
            font=("Arial", 24, "bold"),
            fg="white",
            bg="#2c3e50"
        ).pack(side="left", padx=20, pady=20)
        
        # Controls in header
        controls_container = tk.Frame(header_frame, bg="#2c3e50")
        controls_container.pack(side="right", padx=20, pady=20)
        
        # Date range selector
        tk.Label(controls_container, text="Time Period:", fg="white", bg="#2c3e50", font=("Arial", 10)).pack(side="left", padx=5)
        self.analytics_range_var = tk.StringVar(value="Last 30 Days")
        range_combo = ttk.Combobox(
            controls_container,
            textvariable=self.analytics_range_var,
            values=["Today", "Last 7 Days", "Last 30 Days", "Last 90 Days", "All Time", "Custom Range"],
            state="readonly",
            width=15
        )
        range_combo.pack(side="left", padx=5)
        range_combo.bind("<<ComboboxSelected>>", lambda e: self._refresh_analytics_dashboard())
        
        # Refresh button
        refresh_btn = ttk.Button(
            controls_container,
            text="Refresh",
            command=self._refresh_analytics_dashboard
        )
        refresh_btn.pack(side="left", padx=5)
        
        # Export button
        export_btn = ttk.Button(
            controls_container,
            text="Export",
            command=self._export_analytics_report
        )
        export_btn.pack(side="left", padx=5)
        
        # ========== KEY METRICS CARDS SECTION ==========
        metrics_frame = tk.Frame(scrollable_frame, bg="#f0f4f8")
        metrics_frame.pack(fill="x", padx=10, pady=10)
        
        # Create 7 metric cards
        self.metric_cards = {}
        metrics_config = [
            ("pH Level", "ph", "#3498db", "7.2-7.6"),
            ("Free Chlorine", "free_chlorine", "#27ae60", "1-3 ppm"),
            ("Total Chlorine", "total_chlorine", "#16a085", "1-3 ppm"),
            ("Alkalinity", "alkalinity", "#e67e22", "80-120 ppm"),
            ("Ca Hardness", "calcium_hardness", "#9b59b6", "200-400 ppm"),
            ("Cyanuric Acid", "cyanuric_acid", "#e74c3c", "30-50 ppm"),
            ("Temperature", "temperature", "#f39c12", "78-82°FF"),
            ("Bromine", "bromine", "#c0392b", "2-4 ppm"),
            ("Salt/TDS", "salt", "#34495e", "2700-3400 ppm")
        ]
        
        for i, (title, key, color, ideal) in enumerate(metrics_config):
            row = i // 3  # 3 columns layout
            col = i % 3
            
            card = tk.Frame(metrics_frame, bg=color, relief="raised", borderwidth=3)
            card.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")
            metrics_frame.columnconfigure(col, weight=1)
            
            # Title
            tk.Label(
                card,
                text=title,
                font=("Arial", 11, "bold"),
                bg=color,
                fg="white"
            ).pack(pady=(12, 2))
            
            # Current value
            value_label = tk.Label(
                card,
                text="--",
                font=("Arial", 20, "bold"),
                bg=color,
                fg="white"
            )
            value_label.pack(pady=2)
            
            # Trend indicator
            trend_label = tk.Label(
                card,
                text="--",
                font=("Arial", 10),
                bg=color,
                fg="white"
            )
            trend_label.pack(pady=2)
            
            # Ideal range
            tk.Label(
                card,
                text=f"Ideal: {ideal}",
                font=("Arial", 8, "italic"),
                bg=color,
                fg="white"
            ).pack(pady=(2, 12))
            
            self.metric_cards[key] = {
                'value': value_label,
                'trend': trend_label,
                'frame': card
            }
        
        # ========== POOL HEALTH SCORE SECTION ==========
        stats_frame = tk.LabelFrame(scrollable_frame, text="UP] Statistical Summary", font=("Arial", 14, "bold"), bg="white")
        stats_frame.pack(fill="both", padx=10, pady=10, expand=True)
        
        # Create statistics table
        stats_columns = ("Metric", "Current", "Min", "Max", "Average", "Std Dev", "Status")
        self.stats_tree = ttk.Treeview(
            stats_frame,
            columns=stats_columns,
            show="headings",
            height=8
        )
        
        # Define headings
        for col in stats_columns:
            self.stats_tree.heading(col, text=col)
            if col == "Metric":
                self.stats_tree.column(col, width=120, anchor="w")
            else:
                self.stats_tree.column(col, width=90, anchor="center")
        
        # Add scrollbar
        stats_scrollbar = ttk.Scrollbar(stats_frame, orient="vertical", command=self.stats_tree.yview)
        self.stats_tree.configure(yscrollcommand=stats_scrollbar.set)
        
        self.stats_tree.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        stats_scrollbar.pack(side="right", fill="y")
        
        # ========== INTERACTIVE CHARTS SECTION ==========
        charts_frame = tk.LabelFrame(scrollable_frame, text="Interactive Charts", font=("Arial", 14, "bold"), bg="white")
        charts_frame.pack(fill="both", padx=10, pady=10, expand=True)
        
        # Chart controls
        chart_controls = tk.Frame(charts_frame, bg="white")
        chart_controls.pack(fill="x", padx=10, pady=10)
        
        tk.Label(chart_controls, text="Chart Type:", bg="white", font=("Arial", 10, "bold")).pack(side="left", padx=5)
        self.chart_type_var = tk.StringVar(value="Line Chart")
        chart_type_combo = ttk.Combobox(
            chart_controls,
            textvariable=self.chart_type_var,
            values=["Line Chart", "Bar Chart", "Scatter Plot", "Multi-Metric"],
            state="readonly",
            width=15
        )
        chart_type_combo.pack(side="left", padx=5)
        chart_type_combo.bind("<<ComboboxSelected>>", lambda e: self._update_analytics_chart())
        
        tk.Label(chart_controls, text="Metric:", bg="white", font=("Arial", 10, "bold")).pack(side="left", padx=5)
        self.chart_metric_var = tk.StringVar(value="pH")
        chart_metric_combo = ttk.Combobox(
            chart_controls,
            textvariable=self.chart_metric_var,
            values=["pH", "Free Chlorine", "Total Chlorine", "Alkalinity", "Calcium Hardness", "Cyanuric Acid", "Temperature", "Bromine", "Salt/TDS"],
            state="readonly",
            width=18
        )
        chart_metric_combo.pack(side="left", padx=5)
        chart_metric_combo.bind("<<ComboboxSelected>>", lambda e: self._update_analytics_chart())
        
        # Chart canvas placeholder
        self.chart_frame = tk.Frame(charts_frame, bg="white", height=400)
        self.chart_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # ========== ANOMALIES & ALERTS SECTION ==========
        alerts_frame = tk.LabelFrame(scrollable_frame, text="!] Anomalies & Alerts", font=("Arial", 14, "bold"), bg="white")
        alerts_frame.pack(fill="both", padx=10, pady=10, expand=True)
        
        self.alerts_text = tk.Text(alerts_frame, height=8, wrap="word", font=("Arial", 10), bg="#fff3cd")
        self.alerts_text.pack(fill="both", expand=True, padx=5, pady=5)
        
        # ========== RECENT READINGS TABLE ==========
        readings_frame = tk.LabelFrame(scrollable_frame, text="LIST] Recent Readings (Last 50)", font=("Arial", 14, "bold"), bg="white")
        readings_frame.pack(fill="both", padx=10, pady=10, expand=True)
        
        # Create treeview
        readings_columns = ("Date", "Time", "pH", "Free Cl", "Total Cl", "Alk", "Ca Hard", "CYA", "Temp", "Br", "Salt")
        self.readings_tree = ttk.Treeview(
            readings_frame,
            columns=readings_columns,
            show="headings",
            height=15
        )
        
        # Define headings and columns
        for col in readings_columns:
            self.readings_tree.heading(col, text=col)
            if col in ["Date", "Time"]:
                self.readings_tree.column(col, width=100, anchor="center")
            else:
                self.readings_tree.column(col, width=80, anchor="center")
        
        # Add scrollbar
        readings_scrollbar = ttk.Scrollbar(readings_frame, orient="vertical", command=self.readings_tree.yview)
        self.readings_tree.configure(yscrollcommand=readings_scrollbar.set)
        
        self.readings_tree.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        readings_scrollbar.pack(side="right", fill="y")
        
        # Initial data load
        self._refresh_analytics_dashboard()
        
        logger.info("Analytics Dashboard created successfully")


    

    def _create_cost_tracking_tab(self):
        """Create the chemical cost tracking tab"""
        # Main container with scrollbar
        canvas = tk.Canvas(self.cost_tracking_tab, bg="white")
        scrollbar = ttk.Scrollbar(self.cost_tracking_tab, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="white")
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Header
        header_frame = tk.Frame(scrollable_frame, bg="white", pady=10)
        header_frame.pack(fill=tk.X, padx=20)
        
        title_label = tk.Label(
            header_frame,
            text="Chemical Cost Tracking",
            font=("Arial", 18, "bold"),
            bg="white",
            fg="#2c3e50"
        )
        title_label.pack(side=tk.LEFT)
        
        # Add Purchase Button
        add_btn = tk.Button(
            header_frame,
            text="+ Add Purchase",
            command=self._show_add_purchase_dialog,
            bg="#27ae60",
            fg="white",
            font=("Arial", 12, "bold"),
            padx=20,
            pady=8,
            relief=tk.FLAT,
            cursor="hand2"
        )
        add_btn.pack(side=tk.RIGHT, padx=5)
        
        # Cost Summary Cards
        summary_frame = tk.Frame(scrollable_frame, bg="white")
        summary_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Configure grid
        for i in range(4):
            summary_frame.columnconfigure(i, weight=1)
        
        # Summary cards
        self.cost_cards = {}
        cards_info = [
            ("This Month", "this_month", "#3498db"),
            ("This Year", "this_year", "#2ecc71"),
            ("Total Spent", "total", "#e74c3c"),
            ("Avg/Month", "avg_month", "#f39c12")
        ]
        
        for idx, (title, key, color) in enumerate(cards_info):
            card = tk.Frame(summary_frame, bg=color, relief=tk.RAISED, borderwidth=2)
            card.grid(row=0, column=idx, padx=5, pady=5, sticky="nsew")
            
            tk.Label(card, text=title, font=("Arial", 10, "bold"), bg=color, fg="white").pack(pady=5)
            value_label = tk.Label(card, text="$0.00", font=("Arial", 20, "bold"), bg=color, fg="white")
            value_label.pack(pady=5)
            
            self.cost_cards[key] = value_label
        
        # Purchase History Section
        history_frame = tk.LabelFrame(
            scrollable_frame,
            text="Purchase History",
            font=("Arial", 12, "bold"),
            bg="white",
            padx=10,
            pady=10
        )
        history_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Create Treeview for purchases
        columns = ("Date", "Chemical", "Brand", "Quantity", "Unit", "Cost", "Store")
        self.purchases_tree = ttk.Treeview(history_frame, columns=columns, show="headings", height=15)
        
        for col in columns:
            self.purchases_tree.heading(col, text=col)
            width = 100 if col in ["Date", "Cost"] else 120
            self.purchases_tree.column(col, width=width, anchor=tk.CENTER)
        
        # Scrollbars
        y_scrollbar = ttk.Scrollbar(history_frame, orient=tk.VERTICAL, command=self.purchases_tree.yview)
        x_scrollbar = ttk.Scrollbar(history_frame, orient=tk.HORIZONTAL, command=self.purchases_tree.xview)
        self.purchases_tree.configure(yscrollcommand=y_scrollbar.set, xscrollcommand=x_scrollbar.set)
        
        self.purchases_tree.grid(row=0, column=0, sticky="nsew")
        y_scrollbar.grid(row=0, column=1, sticky="ns")
        x_scrollbar.grid(row=1, column=0, sticky="ew")
        
        history_frame.grid_rowconfigure(0, weight=1)
        history_frame.grid_columnconfigure(0, weight=1)
        
        # Delete button
        delete_btn = tk.Button(
            history_frame,
            text="Delete Selected",
            command=self._delete_selected_purchase,
            bg="#e74c3c",
            fg="white",
            font=("Arial", 10),
            padx=15,
            pady=5,
            relief=tk.FLAT,
            cursor="hand2"
        )
        delete_btn.grid(row=2, column=0, pady=10, sticky="w")
        
        # Export button
        export_btn = tk.Button(
            history_frame,
            text="Export to CSV",
            command=self._export_cost_report,
            bg="#3498db",
            fg="white",
            font=("Arial", 10),
            padx=15,
            pady=5,
            relief=tk.FLAT,
            cursor="hand2"
        )
        export_btn.grid(row=2, column=0, pady=10, sticky="e")
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Load existing purchases
        self._load_purchases()
    
    def _show_add_purchase_dialog(self):
        """Show dialog to add new chemical purchase"""
        dialog = tk.Toplevel(self)
        dialog.title("Add Chemical Purchase")
        dialog.geometry("500x450")
        dialog.transient(self)
        dialog.grab_set()
        
        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (500 // 2)
        y = (dialog.winfo_screenheight() // 2) - (450 // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Form frame
        form_frame = tk.Frame(dialog, padx=20, pady=20)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # Date
        tk.Label(form_frame, text="Date:", font=("Arial", 10)).grid(row=0, column=0, sticky=tk.W, pady=5)
        date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        date_entry = ttk.Entry(form_frame, textvariable=date_var, width=30)
        date_entry.grid(row=0, column=1, sticky=tk.W, pady=5, padx=5)
        
        # Chemical Name
        tk.Label(form_frame, text="Chemical Name:", font=("Arial", 10)).grid(row=1, column=0, sticky=tk.W, pady=5)
        chemical_var = tk.StringVar()
        chemical_combo = ttk.Combobox(
            form_frame,
            textvariable=chemical_var,
            values=["Liquid Chlorine", "Chlorine Tablets", "pH Up", "pH Down", "Alkalinity Up", 
                   "Calcium Hardness", "Cyanuric Acid", "Algaecide", "Clarifier", "Shock"],
            width=28
        )
        chemical_combo.grid(row=1, column=1, sticky=tk.W, pady=5, padx=5)
        
        # Brand
        tk.Label(form_frame, text="Brand:", font=("Arial", 10)).grid(row=2, column=0, sticky=tk.W, pady=5)
        brand_var = tk.StringVar()
        brand_entry = ttk.Entry(form_frame, textvariable=brand_var, width=30)
        brand_entry.grid(row=2, column=1, sticky=tk.W, pady=5, padx=5)
        
        # Quantity
        tk.Label(form_frame, text="Quantity:", font=("Arial", 10)).grid(row=3, column=0, sticky=tk.W, pady=5)
        quantity_var = tk.StringVar()
        quantity_entry = ttk.Entry(form_frame, textvariable=quantity_var, width=30)
        quantity_entry.grid(row=3, column=1, sticky=tk.W, pady=5, padx=5)
        
        # Unit
        tk.Label(form_frame, text="Unit:", font=("Arial", 10)).grid(row=4, column=0, sticky=tk.W, pady=5)
        unit_var = tk.StringVar()
        unit_combo = ttk.Combobox(
            form_frame,
            textvariable=unit_var,
            values=["gallons", "lbs", "oz", "tablets", "bottles"],
            width=28
        )
        unit_combo.grid(row=4, column=1, sticky=tk.W, pady=5, padx=5)
        
        # Cost
        tk.Label(form_frame, text="Cost ($):", font=("Arial", 10)).grid(row=5, column=0, sticky=tk.W, pady=5)
        cost_var = tk.StringVar()
        cost_entry = ttk.Entry(form_frame, textvariable=cost_var, width=30)
        cost_entry.grid(row=5, column=1, sticky=tk.W, pady=5, padx=5)
        
        # Store
        tk.Label(form_frame, text="Store:", font=("Arial", 10)).grid(row=6, column=0, sticky=tk.W, pady=5)
        store_var = tk.StringVar()
        store_combo = ttk.Combobox(
            form_frame,
            textvariable=store_var,
            values=["Amazon", "Home Depot", "Lowe's", "Walmart", "Pool Supply Store", "Other"],
            width=28
        )
        store_combo.grid(row=6, column=1, sticky=tk.W, pady=5, padx=5)
        
        # Notes
        tk.Label(form_frame, text="Notes:", font=("Arial", 10)).grid(row=7, column=0, sticky=tk.W, pady=5)
        notes_text = tk.Text(form_frame, width=30, height=4)
        notes_text.grid(row=7, column=1, sticky=tk.W, pady=5, padx=5)
        
        # Buttons
        button_frame = tk.Frame(form_frame)
        button_frame.grid(row=8, column=0, columnspan=2, pady=20)
        
        def save_purchase():
            try:
                # Validate inputs
                if not chemical_var.get():
                    messagebox.showerror("Error", "Please enter chemical name")
                    return
                if not quantity_var.get() or not cost_var.get():
                    messagebox.showerror("Error", "Please enter quantity and cost")
                    return
                
                # Create purchase record
                purchase = {
                    'date': date_var.get(),
                    'time': datetime.now().strftime("%H:%M:%S"),
                    'chemical_name': chemical_var.get(),
                    'brand': brand_var.get(),
                    'quantity': float(quantity_var.get()),
                    'unit': unit_var.get(),
                    'cost': float(cost_var.get()),
                    'store': store_var.get(),
                    'notes': notes_text.get("1.0", tk.END).strip()
                }
                
                # Save purchase
                self._save_purchase(purchase)
                
                # Close dialog
                dialog.destroy()
                
                # Refresh display
                self._load_purchases()
                
                messagebox.showinfo("Success", "Purchase added successfully!")
                
            except ValueError:
                messagebox.showerror("Error", "Please enter valid numbers for quantity and cost")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save purchase: {e}")
        
        save_btn = tk.Button(
            button_frame,
            text="Save",
            command=save_purchase,
            bg="#27ae60",
            fg="white",
            font=("Arial", 11, "bold"),
            padx=30,
            pady=8,
            relief=tk.FLAT,
            cursor="hand2"
        )
        save_btn.pack(side=tk.LEFT, padx=5)
        
        cancel_btn = tk.Button(
            button_frame,
            text="Cancel",
            command=dialog.destroy,
            bg="#95a5a6",
            fg="white",
            font=("Arial", 11),
            padx=30,
            pady=8,
            relief=tk.FLAT,
            cursor="hand2"
        )
        cancel_btn.pack(side=tk.LEFT, padx=5)
    
    def _save_purchase(self, purchase):
        """Save purchase to database"""
        try:
            # Load existing purchases
            purchases_file = self.data_dir / "chemical_purchases.json"
            
            if purchases_file.exists():
                with open(purchases_file, 'r') as f:
                    purchases = json.load(f)
            else:
                purchases = []
            
            # Add new purchase
            purchases.append(purchase)
            
            # Save back to file
            with open(purchases_file, 'w') as f:
                json.dump(purchases, f, indent=4)
            
            logger.info(f"Saved chemical purchase: {purchase['chemical_name']} - ${purchase['cost']}")
            
        except Exception as e:
            logger.error(f"Error saving purchase: {e}")
            raise
    
    def _load_purchases(self):
        """Load and display purchase history"""
        try:
            # Clear existing items
            for item in self.purchases_tree.get_children():
                self.purchases_tree.delete(item)
            
            # Load purchases
            purchases_file = self.data_dir / "chemical_purchases.json"
            
            if not purchases_file.exists():
                self._update_cost_summary([])
                return
            
            with open(purchases_file, 'r') as f:
                purchases = json.load(f)
            
            # Sort by date (newest first)
            purchases.sort(key=lambda x: x.get('date', ''), reverse=True)
            
            # Display purchases
            for purchase in purchases:
                self.purchases_tree.insert('', 'end', values=(
                    purchase.get('date', ''),
                    purchase.get('chemical', purchase.get('chemical_name', '')),
                    purchase.get('brand', ''),
                    f"{purchase.get('quantity', 0):.1f}",
                    purchase.get('unit', ''),
                    f"${purchase.get('cost', 0):.2f}",
                    purchase.get('store', '')
                ))
            
            # Update cost summary
            self._update_cost_summary(purchases)
            
        except Exception as e:
            logger.error(f"Error loading purchases: {e}")
    
    def _update_cost_summary(self, purchases):
        """Update cost summary cards"""
        try:
            from datetime import datetime
            
            now = datetime.now()
            this_month = 0
            this_year = 0
            total = 0
            
            for purchase in purchases:
                cost = purchase.get('cost', 0)
                total += cost
                
                # Parse date
                try:
                    purchase_date = datetime.strptime(purchase.get('date', ''), '%Y-%m-%d')
                    
                    if purchase_date.year == now.year:
                        this_year += cost
                        
                        if purchase_date.month == now.month:
                            this_month += cost
                except:
                    pass
            
            # Calculate average per month
            if purchases:
                # Get date range
                dates = []
                for purchase in purchases:
                    try:
                        dates.append(datetime.strptime(purchase.get('date', ''), '%Y-%m-%d'))
                    except:
                        pass
                
                if dates:
                    dates.sort()
                    months_span = max(1, ((now - dates[0]).days / 30))
                    avg_month = total / months_span
                else:
                    avg_month = 0
            else:
                avg_month = 0
            
            # Update cards
            self.cost_cards['this_month'].config(text=f"${this_month:.2f}")
            self.cost_cards['this_year'].config(text=f"${this_year:.2f}")
            self.cost_cards['total'].config(text=f"${total:.2f}")
            self.cost_cards['avg_month'].config(text=f"${avg_month:.2f}")
            
        except Exception as e:
            logger.error(f"Error updating cost summary: {e}")
    
    def _delete_selected_purchase(self):
        """Delete selected purchase"""
        try:
            selected = self.purchases_tree.selection()
            if not selected:
                messagebox.showwarning("Warning", "Please select a purchase to delete")
                return
            
            if not messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this purchase?"):
                return
            
            # Get selected item data
            item = self.purchases_tree.item(selected[0])
            values = item['values']
            
            # Load purchases
            purchases_file = self.data_dir / "chemical_purchases.json"
            with open(purchases_file, 'r') as f:
                purchases = json.load(f)
            
            # Find and remove purchase
            for i, purchase in enumerate(purchases):
                if (purchase.get('date') == values[0] and 
                    purchase.get('chemical_name') == values[1] and
                    f"${purchase.get('cost', 0):.2f}" == values[5]):
                    purchases.pop(i)
                    break
            
            # Save back
            with open(purchases_file, 'w') as f:
                json.dump(purchases, f, indent=4)
            
            # Refresh display
            self._load_purchases()
            
            messagebox.showinfo("Success", "Purchase deleted successfully!")
            
        except Exception as e:
            logger.error(f"Error deleting purchase: {e}")
            messagebox.showerror("Error", f"Failed to delete purchase: {e}")
    
    def _export_cost_report(self):
        """Export cost report to CSV"""
        try:
            from tkinter import filedialog
            import csv
            
            # Ask for save location
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                initialfile=f"chemical_costs_{datetime.now().strftime('%Y%m%d')}.csv"
            )
            
            if not filename:
                return
            
            # Load purchases
            purchases_file = self.data_dir / "chemical_purchases.json"
            
            if not purchases_file.exists():
                messagebox.showwarning("Warning", "No purchases to export")
                return
            
            with open(purchases_file, 'r') as f:
                purchases = json.load(f)
            
            # Write to CSV
            with open(filename, 'w', newline='') as f:
                fieldnames = ['date', 'time', 'chemical_name', 'brand', 'quantity', 'unit', 'cost', 'store', 'notes']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                
                writer.writeheader()
                for purchase in purchases:
                    writer.writerow(purchase)
            
            messagebox.showinfo("Success", f"Cost report exported to:\n{filename}")
            logger.info(f"Cost report exported to {filename}")
            
        except Exception as e:
            logger.error(f"Error exporting cost report: {e}")
            messagebox.showerror("Error", f"Failed to export report: {e}")

    def _create_inventory_tab(self):
        """Create the chemical inventory management tab"""
        # Main container with scrollbar
        canvas = tk.Canvas(self.inventory_tab, bg="white")
        scrollbar = ttk.Scrollbar(self.inventory_tab, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="white")
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Header
        header_frame = tk.Frame(scrollable_frame, bg="white", pady=10)
        header_frame.pack(fill=tk.X, padx=20)
        
        title_label = tk.Label(
            header_frame,
            text="Chemical Inventory Management",
            font=("Arial", 18, "bold"),
            bg="white",
            fg="#2c3e50"
        )
        title_label.pack(side=tk.LEFT)
        
        # Action Buttons
        btn_frame = tk.Frame(header_frame, bg="white")
        btn_frame.pack(side=tk.RIGHT)
        
        add_btn = tk.Button(
            btn_frame,
            text="+ Add Chemical",
            command=self._show_add_chemical_dialog,
            bg="#27ae60",
            fg="white",
            font=("Arial", 11, "bold"),
            padx=15,
            pady=6,
            relief=tk.FLAT,
            cursor="hand2"
        )
        add_btn.pack(side=tk.LEFT, padx=5)
        
        update_btn = tk.Button(
            btn_frame,
            text="Update Stock",
            command=self._show_update_stock_dialog,
            bg="#3498db",
            fg="white",
            font=("Arial", 11, "bold"),
            padx=15,
            pady=6,
            relief=tk.FLAT,
            cursor="hand2"
        )
        update_btn.pack(side=tk.LEFT, padx=5)
        
        # Summary Cards
        summary_frame = tk.Frame(scrollable_frame, bg="white")
        summary_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Configure grid
        for i in range(4):
            summary_frame.columnconfigure(i, weight=1)
        
        # Summary cards
        self.inventory_cards = {}
        cards_info = [
            ("Total Items", "total_items", "#3498db"),
            ("Low Stock", "low_stock", "#f39c12"),
            ("Out of Stock", "out_of_stock", "#e74c3c"),
            ("Total Value", "total_value", "#2ecc71")
        ]
        
        for idx, (title, key, color) in enumerate(cards_info):
            card = tk.Frame(summary_frame, bg=color, relief=tk.RAISED, borderwidth=2)
            card.grid(row=0, column=idx, padx=5, pady=5, sticky="nsew")
            
            tk.Label(card, text=title, font=("Arial", 10, "bold"), bg=color, fg="white").pack(pady=5)
            value_label = tk.Label(card, text="0", font=("Arial", 20, "bold"), bg=color, fg="white")
            value_label.pack(pady=5)
            
            self.inventory_cards[key] = value_label
        
        # Inventory Table Section
        table_frame = tk.LabelFrame(
            scrollable_frame,
            text="Current Inventory",
            font=("Arial", 12, "bold"),
            bg="white",
            padx=10,
            pady=10
        )
        table_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Create Treeview for inventory
        columns = ("Chemical", "Current", "Min", "Max", "Unit", "Status", "Value", "Last Updated")
        self.inventory_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=12)
        
        # Configure columns
        column_widths = {
            "Chemical": 150,
            "Current": 80,
            "Min": 60,
            "Max": 60,
            "Unit": 80,
            "Status": 100,
            "Value": 80,
            "Last Updated": 100
        }
        
        for col in columns:
            self.inventory_tree.heading(col, text=col)
            self.inventory_tree.column(col, width=column_widths.get(col, 100), anchor=tk.CENTER)
        
        # Configure tags for color coding
        self.inventory_tree.tag_configure('out_of_stock', background='#ffcccc')
        self.inventory_tree.tag_configure('low_stock', background='#fff3cd')
        self.inventory_tree.tag_configure('good_stock', background='#d4edda')
        
        # Scrollbars
        y_scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.inventory_tree.yview)
        x_scrollbar = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=self.inventory_tree.xview)
        self.inventory_tree.configure(yscrollcommand=y_scrollbar.set, xscrollcommand=x_scrollbar.set)
        
        self.inventory_tree.grid(row=0, column=0, sticky="nsew")
        y_scrollbar.grid(row=0, column=1, sticky="ns")
        x_scrollbar.grid(row=1, column=0, sticky="ew")
        
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
        
        # Action buttons below table
        action_frame = tk.Frame(table_frame, bg="white")
        action_frame.grid(row=2, column=0, columnspan=2, pady=10, sticky="ew")
        
        delete_btn = tk.Button(
            action_frame,
            text="Delete Selected",
            command=self._delete_selected_chemical,
            bg="#e74c3c",
            fg="white",
            font=("Arial", 10),
            padx=15,
            pady=5,
            relief=tk.FLAT,
            cursor="hand2"
        )
        delete_btn.pack(side=tk.LEFT, padx=5)
        
        refresh_btn = tk.Button(
            action_frame,
            text="Refresh",
            command=self._load_inventory,
            bg="#95a5a6",
            fg="white",
            font=("Arial", 10),
            padx=15,
            pady=5,
            relief=tk.FLAT,
            cursor="hand2"
        )
        refresh_btn.pack(side=tk.LEFT, padx=5)
        
        export_btn = tk.Button(
            action_frame,
            text="Export to CSV",
            command=self._export_inventory_report,
            bg="#3498db",
            fg="white",
            font=("Arial", 10),
            padx=15,
            pady=5,
            relief=tk.FLAT,
            cursor="hand2"
        )
        export_btn.pack(side=tk.RIGHT, padx=5)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Load existing inventory
        self._load_inventory()

    def _load_inventory(self):
        """Load and display inventory"""
        try:
            # Clear existing items
            for item in self.inventory_tree.get_children():
                self.inventory_tree.delete(item)
            
            # Load inventory
            inventory_file = self.data_dir / "chemical_inventory.json"
            
            if not inventory_file.exists():
                self._update_inventory_summary([])
                return
            
            with open(inventory_file, 'r') as f:
                inventory = json.load(f)
            
            # Sort by chemical name
            inventory.sort(key=lambda x: x.get('chemical', ''))
            
            # Display inventory items
            for item in inventory:
                current = item.get('current_qty', 0)
                min_qty = item.get('min_qty', 0)
                cost_per_unit = item.get('cost_per_unit', 0)
                
                # Determine status and tag
                if current == 0:
                    status = "OUT OF STOCK"
                    tag = 'out_of_stock'
                elif current < min_qty:
                    status = "LOW STOCK"
                    tag = 'low_stock'
                else:
                    status = "GOOD"
                    tag = 'good_stock'
                
                # Calculate value
                value = current * cost_per_unit
                
                self.inventory_tree.insert('', 'end', values=(
                    item.get('chemical', ''),
                    f"{current:.1f}",
                    f"{min_qty:.1f}",
                    f"{item.get('max_qty', 0):.1f}",
                    item.get('unit', ''),
                    status,
                    f"${value:.2f}",
                    item.get('last_updated', '')
                ), tags=(tag,))
            
            # Update summary
            self._update_inventory_summary(inventory)
            
        except Exception as e:
            logger.error(f"Error loading inventory: {e}")

    def _update_inventory_summary(self, inventory):
        """Update inventory summary cards"""
        try:
            total_items = len(inventory)
            out_of_stock = sum(1 for item in inventory if item.get('current_qty', 0) == 0)
            low_stock = sum(1 for item in inventory if 0 < item.get('current_qty', 0) < item.get('min_qty', 0))
            total_value = sum(item.get('current_qty', 0) * item.get('cost_per_unit', 0) for item in inventory)
            
            # Update cards
            self.inventory_cards['total_items'].config(text=str(total_items))
            self.inventory_cards['low_stock'].config(text=str(low_stock))
            self.inventory_cards['out_of_stock'].config(text=str(out_of_stock))
            self.inventory_cards['total_value'].config(text=f"${total_value:.2f}")
            
        except Exception as e:
            logger.error(f"Error updating inventory summary: {e}")

    def _show_add_chemical_dialog(self):
        """Show dialog to add new chemical to inventory"""
        dialog = tk.Toplevel(self)
        dialog.title("Add Chemical to Inventory")
        dialog.geometry("500x500")
        dialog.transient(self)
        dialog.grab_set()
        
        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (250)
        y = (dialog.winfo_screenheight() // 2) - (250)
        dialog.geometry(f"+{x}+{y}")
        
        # Form frame
        form_frame = tk.Frame(dialog, padx=20, pady=20)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # Chemical Name
        tk.Label(form_frame, text="Chemical Name:", font=("Arial", 10)).grid(row=0, column=0, sticky=tk.W, pady=5)
        chemical_var = tk.StringVar()
        chemical_combo = ttk.Combobox(form_frame, textvariable=chemical_var, width=28)
        chemical_combo['values'] = [
            "Liquid Chlorine", "Chlorine Tablets", "Shock Treatment",
            "pH Increaser", "pH Decreaser", "Alkalinity Increaser",
            "Calcium Hardness Increaser", "Cyanuric Acid",
            "Algaecide", "Clarifier", "Test Strips"
        ]
        chemical_combo.grid(row=0, column=1, sticky=tk.W, pady=5, padx=5)
        
        # Current Quantity
        tk.Label(form_frame, text="Current Quantity:", font=("Arial", 10)).grid(row=1, column=0, sticky=tk.W, pady=5)
        current_var = tk.StringVar(value="0")
        current_entry = ttk.Entry(form_frame, textvariable=current_var, width=30)
        current_entry.grid(row=1, column=1, sticky=tk.W, pady=5, padx=5)
        
        # Minimum Quantity
        tk.Label(form_frame, text="Minimum Quantity:", font=("Arial", 10)).grid(row=2, column=0, sticky=tk.W, pady=5)
        min_var = tk.StringVar(value="0")
        min_entry = ttk.Entry(form_frame, textvariable=min_var, width=30)
        min_entry.grid(row=2, column=1, sticky=tk.W, pady=5, padx=5)
        
        # Maximum Quantity
        tk.Label(form_frame, text="Maximum Quantity:", font=("Arial", 10)).grid(row=3, column=0, sticky=tk.W, pady=5)
        max_var = tk.StringVar(value="0")
        max_entry = ttk.Entry(form_frame, textvariable=max_var, width=30)
        max_entry.grid(row=3, column=1, sticky=tk.W, pady=5, padx=5)
        
        # Unit
        tk.Label(form_frame, text="Unit:", font=("Arial", 10)).grid(row=4, column=0, sticky=tk.W, pady=5)
        unit_var = tk.StringVar()
        unit_combo = ttk.Combobox(form_frame, textvariable=unit_var, width=28)
        unit_combo['values'] = ["gallons", "lbs", "quarts", "bottles", "tablets"]
        unit_combo.grid(row=4, column=1, sticky=tk.W, pady=5, padx=5)
        
        # Cost Per Unit
        tk.Label(form_frame, text="Cost Per Unit ($):", font=("Arial", 10)).grid(row=5, column=0, sticky=tk.W, pady=5)
        cost_var = tk.StringVar(value="0.00")
        cost_entry = ttk.Entry(form_frame, textvariable=cost_var, width=30)
        cost_entry.grid(row=5, column=1, sticky=tk.W, pady=5, padx=5)
        
        # Notes
        tk.Label(form_frame, text="Notes:", font=("Arial", 10)).grid(row=6, column=0, sticky=tk.W, pady=5)
        notes_text = tk.Text(form_frame, width=30, height=4)
        notes_text.grid(row=6, column=1, sticky=tk.W, pady=5, padx=5)
        
        # Buttons
        btn_frame = tk.Frame(form_frame)
        btn_frame.grid(row=7, column=0, columnspan=2, pady=20)
        
        def save_chemical():
            try:
                # Validate inputs
                if not chemical_var.get():
                    messagebox.showerror("Error", "Please enter chemical name")
                    return
                
                # Load existing inventory
                inventory_file = self.data_dir / "chemical_inventory.json"
                if inventory_file.exists():
                    with open(inventory_file, 'r') as f:
                        inventory = json.load(f)
                else:
                    inventory = []
                
                # Generate ID
                max_id = 0
                for item in inventory:
                    try:
                        item_num = int(item['id'].replace('INV', ''))
                        max_id = max(max_id, item_num)
                    except:
                        pass
                new_id = f"INV{max_id + 1:03d}"
                
                # Create new item
                new_item = {
                    'id': new_id,
                    'chemical': chemical_var.get(),
                    'current_qty': float(current_var.get() or 0),
                    'min_qty': float(min_var.get() or 0),
                    'max_qty': float(max_var.get() or 0),
                    'unit': unit_var.get(),
                    'cost_per_unit': float(cost_var.get() or 0),
                    'last_updated': datetime.now().strftime('%Y-%m-%d'),
                    'notes': notes_text.get('1.0', tk.END).strip()
                }
                
                # Add to inventory
                inventory.append(new_item)
                
                # Save
                with open(inventory_file, 'w') as f:
                    json.dump(inventory, f, indent=2)
                
                # Reload display
                self._load_inventory()
                
                messagebox.showinfo("Success", f"Added {chemical_var.get()} to inventory")
                dialog.destroy()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add chemical: {str(e)}")
        
        save_btn = tk.Button(
            btn_frame,
            text="Save",
            command=save_chemical,
            bg="#27ae60",
            fg="white",
            font=("Arial", 11, "bold"),
            padx=30,
            pady=8,
            relief=tk.FLAT,
            cursor="hand2"
        )
        save_btn.pack(side=tk.LEFT, padx=10)
        
        cancel_btn = tk.Button(
            btn_frame,
            text="Cancel",
            command=dialog.destroy,
            bg="#95a5a6",
            fg="white",
            font=("Arial", 11, "bold"),
            padx=30,
            pady=8,
            relief=tk.FLAT,
            cursor="hand2"
        )
        cancel_btn.pack(side=tk.LEFT, padx=10)

    def _show_update_stock_dialog(self):
        """Show dialog to update stock levels"""
        # Get selected item
        selection = self.inventory_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a chemical to update")
            return
        
        # Get item values
        item_values = self.inventory_tree.item(selection[0])['values']
        chemical_name = item_values[0]
        current_qty = float(item_values[1])
        
        # Create dialog
        dialog = tk.Toplevel(self)
        dialog.title(f"Update Stock: {chemical_name}")
        dialog.geometry("400x300")
        dialog.transient(self)
        dialog.grab_set()
        
        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (200)
        y = (dialog.winfo_screenheight() // 2) - (150)
        dialog.geometry(f"+{x}+{y}")
        
        # Form frame
        form_frame = tk.Frame(dialog, padx=20, pady=20)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # Current stock display
        tk.Label(form_frame, text=f"Chemical: {chemical_name}", font=("Arial", 12, "bold")).pack(pady=10)
        tk.Label(form_frame, text=f"Current Stock: {current_qty}", font=("Arial", 11)).pack(pady=5)
        
        # Action selection
        tk.Label(form_frame, text="Action:", font=("Arial", 10)).pack(pady=10)
        action_var = tk.StringVar(value="add")
        
        action_frame = tk.Frame(form_frame)
        action_frame.pack(pady=5)
        
        tk.Radiobutton(action_frame, text="Add Stock", variable=action_var, value="add").pack(side=tk.LEFT, padx=10)
        tk.Radiobutton(action_frame, text="Remove Stock", variable=action_var, value="remove").pack(side=tk.LEFT, padx=10)
        tk.Radiobutton(action_frame, text="Set Stock", variable=action_var, value="set").pack(side=tk.LEFT, padx=10)
        
        # Quantity
        tk.Label(form_frame, text="Quantity:", font=("Arial", 10)).pack(pady=10)
        qty_var = tk.StringVar(value="0")
        qty_entry = ttk.Entry(form_frame, textvariable=qty_var, width=20, font=("Arial", 12))
        qty_entry.pack(pady=5)
        
        # Buttons
        btn_frame = tk.Frame(form_frame)
        btn_frame.pack(pady=20)
        
        def update_stock():
            try:
                qty = float(qty_var.get() or 0)
                action = action_var.get()
                
                # Load inventory
                inventory_file = self.data_dir / "chemical_inventory.json"
                with open(inventory_file, 'r') as f:
                    inventory = json.load(f)
                
                # Find and update item
                for item in inventory:
                    if item['chemical'] == chemical_name:
                        if action == "add":
                            item['current_qty'] += qty
                        elif action == "remove":
                            item['current_qty'] = max(0, item['current_qty'] - qty)
                        else:  # set
                            item['current_qty'] = qty
                        
                        item['last_updated'] = datetime.now().strftime('%Y-%m-%d')
                        break
                
                # Save
                with open(inventory_file, 'w') as f:
                    json.dump(inventory, f, indent=2)
                
                # Reload display
                self._load_inventory()
                
                messagebox.showinfo("Success", f"Updated {chemical_name} stock")
                dialog.destroy()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update stock: {str(e)}")
        
        save_btn = tk.Button(
            btn_frame,
            text="Update",
            command=update_stock,
            bg="#3498db",
            fg="white",
            font=("Arial", 11, "bold"),
            padx=30,
            pady=8,
            relief=tk.FLAT,
            cursor="hand2"
        )
        save_btn.pack(side=tk.LEFT, padx=10)
        
        cancel_btn = tk.Button(
            btn_frame,
            text="Cancel",
            command=dialog.destroy,
            bg="#95a5a6",
            fg="white",
            font=("Arial", 11, "bold"),
            padx=30,
            pady=8,
            relief=tk.FLAT,
            cursor="hand2"
        )
        cancel_btn.pack(side=tk.LEFT, padx=10)

    def _delete_selected_chemical(self):
        """Delete selected chemical from inventory"""
        selection = self.inventory_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a chemical to delete")
            return
        
        # Get item values
        item_values = self.inventory_tree.item(selection[0])['values']
        chemical_name = item_values[0]
        
        # Confirm deletion
        if not messagebox.askyesno("Confirm Delete", f"Delete {chemical_name} from inventory?"):
            return
        
        try:
            # Load inventory
            inventory_file = self.data_dir / "chemical_inventory.json"
            with open(inventory_file, 'r') as f:
                inventory = json.load(f)
            
            # Remove item
            inventory = [item for item in inventory if item['chemical'] != chemical_name]
            
            # Save
            with open(inventory_file, 'w') as f:
                json.dump(inventory, f, indent=2)
            
            # Reload display
            self._load_inventory()
            
            messagebox.showinfo("Success", f"Deleted {chemical_name} from inventory")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete chemical: {str(e)}")

    def _export_inventory_report(self):
        """Export inventory to CSV"""
        try:
            from tkinter import filedialog
            
            # Ask for save location
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                initialfile=f"inventory_report_{datetime.now().strftime('%Y%m%d')}.csv"
            )
            
            if not filename:
                return
            
            # Load inventory
            inventory_file = self.data_dir / "chemical_inventory.json"
            with open(inventory_file, 'r') as f:
                inventory = json.load(f)
            
            # Write CSV
            import csv
            with open(filename, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['Chemical', 'Current Qty', 'Min Qty', 'Max Qty', 'Unit', 
                               'Cost Per Unit', 'Total Value', 'Status', 'Last Updated', 'Notes'])
                
                for item in inventory:
                    current = item.get('current_qty', 0)
                    min_qty = item.get('min_qty', 0)
                    cost = item.get('cost_per_unit', 0)
                    value = current * cost
                    
                    if current == 0:
                        status = "OUT OF STOCK"
                    elif current < min_qty:
                        status = "LOW STOCK"
                    else:
                        status = "GOOD"
                    
                    writer.writerow([
                        item.get('chemical', ''),
                        current,
                        min_qty,
                        item.get('max_qty', 0),
                        item.get('unit', ''),
                        cost,
                        value,
                        status,
                        item.get('last_updated', ''),
                        item.get('notes', '')
                    ])
            
            messagebox.showinfo("Success", f"Inventory exported to:\n{filename}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export inventory: {str(e)}")

    def _create_shopping_list_tab(self):
        """Create the shopping list generator tab"""
        # Main container with scrollbar
        canvas = tk.Canvas(self.shopping_list_tab, bg="white")
        scrollbar = ttk.Scrollbar(self.shopping_list_tab, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="white")
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Header
        header_frame = tk.Frame(scrollable_frame, bg="white", pady=10)
        header_frame.pack(fill=tk.X, padx=20)
        
        title_label = tk.Label(
            header_frame,
            text="Shopping List Generator",
            font=("Arial", 18, "bold"),
            bg="white",
            fg="#2c3e50"
        )
        title_label.pack(side=tk.LEFT)
        
        # Action Buttons
        btn_frame = tk.Frame(header_frame, bg="white")
        btn_frame.pack(side=tk.RIGHT)
        
        generate_btn = tk.Button(
            btn_frame,
            text="Generate from Inventory",
            command=self._generate_from_inventory,
            bg="#27ae60",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=12,
            pady=6,
            relief=tk.FLAT,
            cursor="hand2"
        )
        generate_btn.pack(side=tk.LEFT, padx=3)
        
        adjustments_btn = tk.Button(
            btn_frame,
            text="Add from Adjustments",
            command=self._add_from_adjustments,
            bg="#3498db",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=12,
            pady=6,
            relief=tk.FLAT,
            cursor="hand2"
        )
        adjustments_btn.pack(side=tk.LEFT, padx=3)
        
        custom_btn = tk.Button(
            btn_frame,
            text="+ Add Custom",
            command=self._add_custom_shopping_item,
            bg="#9b59b6",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=12,
            pady=6,
            relief=tk.FLAT,
            cursor="hand2"
        )
        custom_btn.pack(side=tk.LEFT, padx=3)
        
        # Summary Cards
        summary_frame = tk.Frame(scrollable_frame, bg="white")
        summary_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Configure grid
        for i in range(4):
            summary_frame.columnconfigure(i, weight=1)
        
        # Summary cards
        self.shopping_cards = {}
        cards_info = [
            ("Total Items", "total_items", "#3498db"),
            ("High Priority", "high_priority", "#e74c3c"),
            ("Total Cost", "total_cost", "#2ecc71"),
            ("Purchased", "purchased", "#95a5a6")
        ]
        
        for idx, (title, key, color) in enumerate(cards_info):
            card = tk.Frame(summary_frame, bg=color, relief=tk.RAISED, borderwidth=2)
            card.grid(row=0, column=idx, padx=5, pady=5, sticky="nsew")
            
            tk.Label(card, text=title, font=("Arial", 10, "bold"), bg=color, fg="white").pack(pady=5)
            value_label = tk.Label(card, text="0", font=("Arial", 20, "bold"), bg=color, fg="white")
            value_label.pack(pady=5)
            
            self.shopping_cards[key] = value_label
        
        # Shopping List Table Section
        table_frame = tk.LabelFrame(
            scrollable_frame,
            text="Current Shopping List",
            font=("Arial", 12, "bold"),
            bg="white",
            padx=10,
            pady=10
        )
        table_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Create Treeview for shopping list
        columns = ("Item", "Qty", "Unit", "Cost", "Priority", "Source", "Reason", "Store")
        self.shopping_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=12)
        
        # Configure columns
        column_widths = {
            "Item": 120,
            "Qty": 60,
            "Unit": 70,
            "Cost": 70,
            "Priority": 80,
            "Source": 90,
            "Reason": 200,
            "Store": 130
        }
        
        for col in columns:
            self.shopping_tree.heading(col, text=col)
            self.shopping_tree.column(col, width=column_widths.get(col, 100), anchor=tk.CENTER if col in ["Qty", "Cost", "Priority"] else tk.W)
        
        # Configure tags for priority color coding
        self.shopping_tree.tag_configure('high_priority', background='#ffcccc')
        self.shopping_tree.tag_configure('medium_priority', background='#fff3cd')
        self.shopping_tree.tag_configure('low_priority', background='#d4edda')
        self.shopping_tree.tag_configure('purchased', background='#e8e8e8', foreground='#999999')
        
        # Scrollbars
        y_scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.shopping_tree.yview)
        x_scrollbar = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=self.shopping_tree.xview)
        self.shopping_tree.configure(yscrollcommand=y_scrollbar.set, xscrollcommand=x_scrollbar.set)
        
        self.shopping_tree.grid(row=0, column=0, sticky="nsew")
        y_scrollbar.grid(row=0, column=1, sticky="ns")
        x_scrollbar.grid(row=1, column=0, sticky="ew")
        
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
        
        # Action buttons below table
        action_frame = tk.Frame(table_frame, bg="white")
        action_frame.grid(row=2, column=0, columnspan=2, pady=10, sticky="ew")
        
        mark_purchased_btn = tk.Button(
            action_frame,
            text="Mark as Purchased",
            command=self._mark_as_purchased,
            bg="#27ae60",
            fg="white",
            font=("Arial", 10),
            padx=15,
            pady=5,
            relief=tk.FLAT,
            cursor="hand2"
        )
        mark_purchased_btn.pack(side=tk.LEFT, padx=5)
        
        delete_btn = tk.Button(
            action_frame,
            text="Delete Selected",
            command=self._delete_shopping_item,
            bg="#e74c3c",
            fg="white",
            font=("Arial", 10),
            padx=15,
            pady=5,
            relief=tk.FLAT,
            cursor="hand2"
        )
        delete_btn.pack(side=tk.LEFT, padx=5)
        
        clear_btn = tk.Button(
            action_frame,
            text="Clear Purchased",
            command=self._clear_purchased_items,
            bg="#95a5a6",
            fg="white",
            font=("Arial", 10),
            padx=15,
            pady=5,
            relief=tk.FLAT,
            cursor="hand2"
        )
        clear_btn.pack(side=tk.LEFT, padx=5)
        
        export_pdf_btn = tk.Button(
            action_frame,
            text="Export to PDF",
            command=self._export_shopping_list_pdf,
            bg="#3498db",
            fg="white",
            font=("Arial", 10),
            padx=15,
            pady=5,
            relief=tk.FLAT,
            cursor="hand2"
        )
        export_pdf_btn.pack(side=tk.RIGHT, padx=5)
        
        email_btn = tk.Button(
            action_frame,
            text="Email List",
            command=self._email_shopping_list,
            bg="#9b59b6",
            fg="white",
            font=("Arial", 10),
            padx=15,
            pady=5,
            relief=tk.FLAT,
            cursor="hand2"
        )
        email_btn.pack(side=tk.RIGHT, padx=5)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Load existing shopping list
        self._load_shopping_list()

    def _load_shopping_list(self):
        """Load and display shopping list"""
        try:
            # Clear existing items
            for item in self.shopping_tree.get_children():
                self.shopping_tree.delete(item)
            
            # Load shopping list
            shopping_file = self.data_dir / "shopping_lists.json"
            
            if not shopping_file.exists():
                self._update_shopping_summary([])
                return
            
            with open(shopping_file, 'r') as f:
                shopping_list = json.load(f)
            
            # Sort by priority (HIGH, MEDIUM, LOW) then by item name
            priority_order = {'HIGH': 0, 'MEDIUM': 1, 'LOW': 2}
            shopping_list.sort(key=lambda x: (priority_order.get(x.get('priority', 'LOW'), 3), x.get('item', '')))
            
            # Display shopping list items
            for item in shopping_list:
                priority = item.get('priority', 'LOW')
                purchased = item.get('purchased', False)
                
                # Determine tag
                if purchased:
                    tag = 'purchased'
                elif priority == 'HIGH':
                    tag = 'high_priority'
                elif priority == 'MEDIUM':
                    tag = 'medium_priority'
                else:
                    tag = 'low_priority'
                
                # Format item name with checkmark if purchased
                item_name = item.get('item', '')
                if purchased:
                    item_name = f"[DONE] {item_name}"
                
                self.shopping_tree.insert('', 'end', values=(
                    item_name,
                    f"{item.get('quantity', 0):.1f}",
                    item.get('unit', ''),
                    f"${item.get('estimated_cost', 0):.2f}",
                    priority,
                    item.get('source', ''),
                    item.get('reason', ''),
                    item.get('store', '')
                ), tags=(tag,))
            
            # Update summary
            self._update_shopping_summary(shopping_list)
            
        except Exception as e:
            logger.error(f"Error loading shopping list: {e}")

    def _update_shopping_summary(self, shopping_list):
        """Update shopping list summary cards"""
        try:
            total_items = len([item for item in shopping_list if not item.get('purchased', False)])
            high_priority = sum(1 for item in shopping_list if item.get('priority') == 'HIGH' and not item.get('purchased', False))
            total_cost = sum(item.get('estimated_cost', 0) for item in shopping_list if not item.get('purchased', False))
            purchased = sum(1 for item in shopping_list if item.get('purchased', False))
            
            # Update cards
            self.shopping_cards['total_items'].config(text=str(total_items))
            self.shopping_cards['high_priority'].config(text=str(high_priority))
            self.shopping_cards['total_cost'].config(text=f"${total_cost:.2f}")
            self.shopping_cards['purchased'].config(text=str(purchased))
            
        except Exception as e:
            logger.error(f"Error updating shopping summary: {e}")

    def _generate_from_inventory(self):
        """Generate shopping list from low inventory items"""
        try:
            # Load inventory
            inventory_file = self.data_dir / "chemical_inventory.json"
            if not inventory_file.exists():
                messagebox.showwarning("No Inventory", "No inventory data found. Please add chemicals to inventory first.")
                return
            
            with open(inventory_file, 'r') as f:
                inventory = json.load(f)
            
            # Load existing shopping list
            shopping_file = self.data_dir / "shopping_lists.json"
            if shopping_file.exists():
                with open(shopping_file, 'r') as f:
                    shopping_list = json.load(f)
            else:
                shopping_list = []
            
            # Find low stock and out of stock items
            added_count = 0
            for inv_item in inventory:
                current = inv_item.get('current_qty', 0)
                min_qty = inv_item.get('min_qty', 0)
                max_qty = inv_item.get('max_qty', 0)
                chemical = inv_item.get('chemical', '')
                
                # Check if already in shopping list
                already_exists = any(item['item'] == chemical and not item.get('purchased', False) for item in shopping_list)
                
                if already_exists:
                    continue
                
                # Determine if needs to be added
                if current == 0:
                    # Out of stock - add max quantity
                    qty_needed = max_qty
                    priority = "HIGH"
                    reason = f"Out of stock - restock to maximum ({max_qty} {inv_item.get('unit', '')})"
                elif current < min_qty:
                    # Low stock - add enough to reach max
                    qty_needed = max_qty - current
                    priority = "HIGH"
                    reason = f"Low stock - below minimum ({current:.1f}/{min_qty:.1f} {inv_item.get('unit', '')})"
                else:
                    continue
                
                # Generate ID
                max_id = 0
                for item in shopping_list:
                    try:
                        item_num = int(item['id'].replace('SHOP', ''))
                        max_id = max(max_id, item_num)
                    except:
                        pass
                new_id = f"SHOP{max_id + 1:03d}"
                
                # Add to shopping list
                new_item = {
                    'id': new_id,
                    'item': chemical,
                    'quantity': qty_needed,
                    'unit': inv_item.get('unit', ''),
                    'estimated_cost': qty_needed * inv_item.get('cost_per_unit', 0),
                    'priority': priority,
                    'source': 'inventory',
                    'reason': reason,
                    'store': '',
                    'purchased': False,
                    'date_added': datetime.now().strftime('%Y-%m-%d')
                }
                
                shopping_list.append(new_item)
                added_count += 1
            
            # Save shopping list
            with open(shopping_file, 'w') as f:
                json.dump(shopping_list, f, indent=2)
            
            # Reload display
            self._load_shopping_list()
            
            if added_count > 0:
                messagebox.showinfo("Success", f"Added {added_count} item(s) to shopping list from inventory")
            else:
                messagebox.showinfo("No Items", "No low stock items found in inventory")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate shopping list: {str(e)}")

    def _add_from_adjustments(self):
        """Add chemicals from water testing adjustments to shopping list"""
        try:
            # Get current adjustments from water testing tab
            if not hasattr(self, 'chemical_readings') or not self.chemical_readings:
                messagebox.showwarning("No Data", "No water test data available. Please save a reading first.")
                return
            
            # Get latest reading
            latest_reading = self.chemical_readings[-1]
            
            # Calculate adjustments
            adjustments = self._calculate_adjustments(latest_reading)
            
            if not adjustments:
                messagebox.showinfo("No Adjustments", "No chemical adjustments needed based on current readings")
                return
            
            # Load existing shopping list
            shopping_file = self.data_dir / "shopping_lists.json"
            if shopping_file.exists():
                with open(shopping_file, 'r') as f:
                    shopping_list = json.load(f)
            else:
                shopping_list = []
            
            added_count = 0
            for adj in adjustments:
                chemical = adj.get('chemical', '')
                amount = adj.get('amount', 0)
                
                if amount <= 0:
                    continue
                
                # Check if already in shopping list
                already_exists = any(item['item'] == chemical and not item.get('purchased', False) for item in shopping_list)
                
                if already_exists:
                    continue
                
                # Generate ID
                max_id = 0
                for item in shopping_list:
                    try:
                        item_num = int(item['id'].replace('SHOP', ''))
                        max_id = max(max_id, item_num)
                    except:
                        pass
                new_id = f"SHOP{max_id + 1:03d}"
                
                # Estimate cost (use inventory cost if available)
                estimated_cost = 0
                unit = adj.get('unit', 'lbs')
                
                # Try to get cost from inventory
                inventory_file = self.data_dir / "chemical_inventory.json"
                if inventory_file.exists():
                    with open(inventory_file, 'r') as f:
                        inventory = json.load(f)
                    for inv_item in inventory:
                        if inv_item.get('chemical', '') == chemical:
                            estimated_cost = amount * inv_item.get('cost_per_unit', 0)
                            break
                
                # Add to shopping list
                new_item = {
                    'id': new_id,
                    'item': chemical,
                    'quantity': amount,
                    'unit': unit,
                    'estimated_cost': estimated_cost,
                    'priority': 'MEDIUM',
                    'source': 'adjustment',
                    'reason': f"Recommended: {adj.get('action', '')}",
                    'store': '',
                    'purchased': False,
                    'date_added': datetime.now().strftime('%Y-%m-%d')
                }
                
                shopping_list.append(new_item)
                added_count += 1
            
            # Save shopping list
            with open(shopping_file, 'w') as f:
                json.dump(shopping_list, f, indent=2)
            
            # Reload display
            self._load_shopping_list()
            
            if added_count > 0:
                messagebox.showinfo("Success", f"Added {added_count} item(s) to shopping list from adjustments")
            else:
                messagebox.showinfo("No Items", "No new items to add from adjustments")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add from adjustments: {str(e)}")

    def _add_custom_shopping_item(self):
        """Show dialog to add custom item to shopping list"""
        dialog = tk.Toplevel(self)
        dialog.title("Add Custom Shopping Item")
        dialog.geometry("500x450")
        dialog.transient(self)
        dialog.grab_set()
        
        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (250)
        y = (dialog.winfo_screenheight() // 2) - (225)
        dialog.geometry(f"+{x}+{y}")
        
        # Form frame
        form_frame = tk.Frame(dialog, padx=20, pady=20)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # Item Name
        tk.Label(form_frame, text="Item Name:", font=("Arial", 10)).grid(row=0, column=0, sticky=tk.W, pady=5)
        item_var = tk.StringVar()
        item_entry = ttk.Entry(form_frame, textvariable=item_var, width=30)
        item_entry.grid(row=0, column=1, sticky=tk.W, pady=5, padx=5)
        
        # Quantity
        tk.Label(form_frame, text="Quantity:", font=("Arial", 10)).grid(row=1, column=0, sticky=tk.W, pady=5)
        qty_var = tk.StringVar(value="1")
        qty_entry = ttk.Entry(form_frame, textvariable=qty_var, width=30)
        qty_entry.grid(row=1, column=1, sticky=tk.W, pady=5, padx=5)
        
        # Unit
        tk.Label(form_frame, text="Unit:", font=("Arial", 10)).grid(row=2, column=0, sticky=tk.W, pady=5)
        unit_var = tk.StringVar()
        unit_combo = ttk.Combobox(form_frame, textvariable=unit_var, width=28)
        unit_combo['values'] = ["gallons", "lbs", "quarts", "bottles", "tablets", "each"]
        unit_combo.grid(row=2, column=1, sticky=tk.W, pady=5, padx=5)
        
        # Estimated Cost
        tk.Label(form_frame, text="Estimated Cost ($):", font=("Arial", 10)).grid(row=3, column=0, sticky=tk.W, pady=5)
        cost_var = tk.StringVar(value="0.00")
        cost_entry = ttk.Entry(form_frame, textvariable=cost_var, width=30)
        cost_entry.grid(row=3, column=1, sticky=tk.W, pady=5, padx=5)
        
        # Priority
        tk.Label(form_frame, text="Priority:", font=("Arial", 10)).grid(row=4, column=0, sticky=tk.W, pady=5)
        priority_var = tk.StringVar(value="MEDIUM")
        priority_frame = tk.Frame(form_frame)
        priority_frame.grid(row=4, column=1, sticky=tk.W, pady=5, padx=5)
        tk.Radiobutton(priority_frame, text="HIGH", variable=priority_var, value="HIGH").pack(side=tk.LEFT, padx=5)
        tk.Radiobutton(priority_frame, text="MEDIUM", variable=priority_var, value="MEDIUM").pack(side=tk.LEFT, padx=5)
        tk.Radiobutton(priority_frame, text="LOW", variable=priority_var, value="LOW").pack(side=tk.LEFT, padx=5)
        
        # Store
        tk.Label(form_frame, text="Store:", font=("Arial", 10)).grid(row=5, column=0, sticky=tk.W, pady=5)
        store_var = tk.StringVar()
        store_combo = ttk.Combobox(form_frame, textvariable=store_var, width=28)
        store_combo['values'] = ["Leslie's Pool Supplies", "Home Depot", "Walmart", "Amazon", "Local Pool Store"]
        store_combo.grid(row=5, column=1, sticky=tk.W, pady=5, padx=5)
        
        # Reason
        tk.Label(form_frame, text="Reason:", font=("Arial", 10)).grid(row=6, column=0, sticky=tk.W, pady=5)
        reason_text = tk.Text(form_frame, width=30, height=3)
        reason_text.grid(row=6, column=1, sticky=tk.W, pady=5, padx=5)
        
        # Buttons
        btn_frame = tk.Frame(form_frame)
        btn_frame.grid(row=7, column=0, columnspan=2, pady=20)
        
        def save_item():
            try:
                if not item_var.get():
                    messagebox.showerror("Error", "Please enter item name")
                    return
                
                # Load existing shopping list
                shopping_file = self.data_dir / "shopping_lists.json"
                if shopping_file.exists():
                    with open(shopping_file, 'r') as f:
                        shopping_list = json.load(f)
                else:
                    shopping_list = []
                
                # Generate ID
                max_id = 0
                for item in shopping_list:
                    try:
                        item_num = int(item['id'].replace('SHOP', ''))
                        max_id = max(max_id, item_num)
                    except:
                        pass
                new_id = f"SHOP{max_id + 1:03d}"
                
                # Create new item
                new_item = {
                    'id': new_id,
                    'item': item_var.get(),
                    'quantity': float(qty_var.get() or 1),
                    'unit': unit_var.get(),
                    'estimated_cost': float(cost_var.get() or 0),
                    'priority': priority_var.get(),
                    'source': 'manual',
                    'reason': reason_text.get('1.0', tk.END).strip(),
                    'store': store_var.get(),
                    'purchased': False,
                    'date_added': datetime.now().strftime('%Y-%m-%d')
                }
                
                # Add to shopping list
                shopping_list.append(new_item)
                
                # Save
                with open(shopping_file, 'w') as f:
                    json.dump(shopping_list, f, indent=2)
                
                # Reload display
                self._load_shopping_list()
                
                messagebox.showinfo("Success", f"Added {item_var.get()} to shopping list")
                dialog.destroy()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add item: {str(e)}")
        
        save_btn = tk.Button(
            btn_frame,
            text="Add to List",
            command=save_item,
            bg="#27ae60",
            fg="white",
            font=("Arial", 11, "bold"),
            padx=30,
            pady=8,
            relief=tk.FLAT,
            cursor="hand2"
        )
        save_btn.pack(side=tk.LEFT, padx=10)
        
        cancel_btn = tk.Button(
            btn_frame,
            text="Cancel",
            command=dialog.destroy,
            bg="#95a5a6",
            fg="white",
            font=("Arial", 11, "bold"),
            padx=30,
            pady=8,
            relief=tk.FLAT,
            cursor="hand2"
        )
        cancel_btn.pack(side=tk.LEFT, padx=10)

    def _mark_as_purchased(self):
        """Mark selected item as purchased"""
        selection = self.shopping_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select an item to mark as purchased")
            return
        
        # Get item values
        item_values = self.shopping_tree.item(selection[0])['values']
        item_name = item_values[0].replace('[DONE] ', '')  # Remove [DONE] prefix if present
        
        try:
            # Load shopping list
            shopping_file = self.data_dir / "shopping_lists.json"
            with open(shopping_file, 'r') as f:
                shopping_list = json.load(f)
            
            # Find and mark item
            for item in shopping_list:
                if item['item'] == item_name:
                    item['purchased'] = True
                    break
            
            # Save
            with open(shopping_file, 'w') as f:
                json.dump(shopping_list, f, indent=2)
            
            # Reload display
            self._load_shopping_list()
            
            messagebox.showinfo("Success", f"Marked {item_name} as purchased")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to mark as purchased: {str(e)}")

    def _delete_shopping_item(self):
        """Delete selected item from shopping list"""
        selection = self.shopping_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select an item to delete")
            return
        
        # Get item values
        item_values = self.shopping_tree.item(selection[0])['values']
        item_name = item_values[0].replace('[DONE] ', '')
        
        # Confirm deletion
        if not messagebox.askyesno("Confirm Delete", f"Delete {item_name} from shopping list?"):
            return
        
        try:
            # Load shopping list
            shopping_file = self.data_dir / "shopping_lists.json"
            with open(shopping_file, 'r') as f:
                shopping_list = json.load(f)
            
            # Remove item
            shopping_list = [item for item in shopping_list if item['item'] != item_name]
            
            # Save
            with open(shopping_file, 'w') as f:
                json.dump(shopping_list, f, indent=2)
            
            # Reload display
            self._load_shopping_list()
            
            messagebox.showinfo("Success", f"Deleted {item_name} from shopping list")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete item: {str(e)}")

    def _clear_purchased_items(self):
        """Clear all purchased items from shopping list"""
        if not messagebox.askyesno("Confirm Clear", "Remove all purchased items from shopping list?"):
            return
        
        try:
            # Load shopping list
            shopping_file = self.data_dir / "shopping_lists.json"
            with open(shopping_file, 'r') as f:
                shopping_list = json.load(f)
            
            # Count purchased items
            purchased_count = sum(1 for item in shopping_list if item.get('purchased', False))
            
            # Remove purchased items
            shopping_list = [item for item in shopping_list if not item.get('purchased', False)]
            
            # Save
            with open(shopping_file, 'w') as f:
                json.dump(shopping_list, f, indent=2)
            
            # Reload display
            self._load_shopping_list()
            
            messagebox.showinfo("Success", f"Cleared {purchased_count} purchased item(s)")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to clear purchased items: {str(e)}")

    def _export_shopping_list_pdf(self):
        """Export shopping list to PDF"""
        try:
            from tkinter import filedialog
            
            # Ask for save location
            filename = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
                initialfile=f"shopping_list_{datetime.now().strftime('%Y%m%d')}.pdf"
            )
            
            if not filename:
                return
            
            # Load shopping list
            shopping_file = self.data_dir / "shopping_lists.json"
            with open(shopping_file, 'r') as f:
                shopping_list = json.load(f)
            
            # Filter out purchased items
            active_items = [item for item in shopping_list if not item.get('purchased', False)]
            
            if not active_items:
                messagebox.showwarning("Empty List", "No active items to export")
                return
            
            # Create simple text file (PDF generation requires additional libraries)
            # For now, create a formatted text file
            txt_filename = filename.replace('.pdf', '.txt')
            
            with open(txt_filename, 'w') as f:
                f.write("=" * 80 + "\n")
                f.write("POOL CHEMICAL SHOPPING LIST\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
                f.write("=" * 80 + "\n\n")
                
                # Summary
                total_cost = sum(item.get('estimated_cost', 0) for item in active_items)
                high_priority = sum(1 for item in active_items if item.get('priority') == 'HIGH')
                
                f.write(f"Total Items: {len(active_items)}\n")
                f.write(f"High Priority: {high_priority}\n")
                f.write(f"Estimated Total Cost: ${total_cost:.2f}\n\n")
                f.write("=" * 80 + "\n\n")
                
                # Group by priority
                for priority in ['HIGH', 'MEDIUM', 'LOW']:
                    priority_items = [item for item in active_items if item.get('priority') == priority]
                    if not priority_items:
                        continue
                    
                    f.write(f"\n{priority} PRIORITY ITEMS:\n")
                    f.write("-" * 80 + "\n")
                    
                    for item in priority_items:
                        f.write(f"\n[ ] {item.get('item', '')}\n")
                        f.write(f"    Quantity: {item.get('quantity', 0):.1f} {item.get('unit', '')}\n")
                        f.write(f"    Estimated Cost: ${item.get('estimated_cost', 0):.2f}\n")
                        f.write(f"    Store: {item.get('store', 'Any')}\n")
                        f.write(f"    Reason: {item.get('reason', '')}\n")
            
            messagebox.showinfo("Success", f"Shopping list exported to:\n{txt_filename}\n\n(Note: PDF export requires additional setup)")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export shopping list: {str(e)}")

    def _email_shopping_list(self):
        """Email shopping list"""
        try:
            # Check if messaging service is available
            if not hasattr(self, 'messaging_service') or not self.messaging_service:
                messagebox.showwarning("Email Not Configured", "Email notifications are not configured. Please set up email in the Notifications tab first.")
                return
            
            # Load shopping list
            shopping_file = self.data_dir / "shopping_lists.json"
            with open(shopping_file, 'r') as f:
                shopping_list = json.load(f)
            
            # Filter out purchased items
            active_items = [item for item in shopping_list if not item.get('purchased', False)]
            
            if not active_items:
                messagebox.showwarning("Empty List", "No active items to email")
                return
            
            # Create email content
            total_cost = sum(item.get('estimated_cost', 0) for item in active_items)
            high_priority = sum(1 for item in active_items if item.get('priority') == 'HIGH')
            
            # Send notification
            self.messaging_service.send_notification(
                notification_type='shopping_list',
                data={
                    'total_items': len(active_items),
                    'high_priority': high_priority,
                    'total_cost': total_cost,
                    'items': active_items
                }
            )
            
            messagebox.showinfo("Success", "Shopping list sent via email")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to email shopping list: {str(e)}")

    # POOL MANAGEMENT METHODS
    # ============================================================================

    def _initialize_pools(self):
        """Initialize pool management system"""
        try:
            # Load pool type specifications
            spec_file = Path("pool_type_specifications.json")
            if spec_file.exists():
                with open(spec_file, 'r') as f:
                    self.pool_type_specs = json.load(f)['pool_types']
            else:
                self.pool_type_specs = {}
            
            # Load pools
            pools_file = self.data_dir / "pools.json"
            if not pools_file.exists():
                # Create default pool from existing data
                default_pool = {
                    'id': 'POOL001',
                    'name': 'Main Pool',
                    'type': 'chlorine',
                    'volume': 20000,
                    'unit': 'gallons',
                    'location': 'Backyard',
                    'created_date': datetime.now().strftime('%Y-%m-%d'),
                    'is_active': True,
                    'notes': 'Default pool'
                }
                with open(pools_file, 'w') as f:
                    json.dump([default_pool], f, indent=2)
            
            with open(pools_file, 'r') as f:
                self.pools = json.load(f)
            
            # Set active pool (first active pool or first pool)
            self.current_pool = None
            for pool in self.pools:
                if pool.get('is_active', False):
                    self.current_pool = pool
                    break
            
            if not self.current_pool and self.pools:
                self.current_pool = self.pools[0]
                self.current_pool['is_active'] = True
                self._save_pools()
            
        except Exception as e:
            logger.error(f"Error initializing pools: {e}")
            # Create default pool
            self.pools = [{
                'id': 'POOL001',
                'name': 'Main Pool',
                'type': 'chlorine',
                'volume': 20000,
                'unit': 'gallons',
                'location': 'Backyard',
                'created_date': datetime.now().strftime('%Y-%m-%d'),
                'is_active': True,
                'notes': 'Default pool'
            }]
            self.current_pool = self.pools[0]
            self._save_pools()

    def _save_pools(self):
        """Save pools to file"""
        try:
            pools_file = self.data_dir / "pools.json"
            with open(pools_file, 'w') as f:
                json.dump(self.pools, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving pools: {e}")
    
    def _get_pool_data(self, pool_id):
        """Get pool data by pool ID"""
        try:
            if not hasattr(self, 'pools') or not self.pools:
                return None
            
            for pool in self.pools:
                if pool.get('id') == pool_id:
                    return pool
            
            return None
        except Exception as e:
            logger.error(f"Error getting pool data: {e}")
            return None

    def _create_pool_selector(self, parent_frame):
        """Create pool selector dropdown in parent frame"""
        selector_frame = tk.Frame(parent_frame, bg="#2c3e50", pady=5)
        selector_frame.pack(fill=tk.X, side=tk.TOP)
        
        # Pool label
        tk.Label(
            selector_frame,
            text="Current Pool:",
            font=("Arial", 10, "bold"),
            bg="#2c3e50",
            fg="white"
        ).pack(side=tk.LEFT, padx=(10, 5))
        
        # Pool dropdown
        self.pool_selector_var = tk.StringVar()
        if self.current_pool:
            self.pool_selector_var.set(f"{self.current_pool['name']} ({self.current_pool['type'].title()})")
        
        pool_names = [f"{p['name']} ({p['type'].title()})" for p in self.pools]
        
        self.pool_selector = ttk.Combobox(
            selector_frame,
            textvariable=self.pool_selector_var,
            values=pool_names,
            state="readonly",
            width=30,
            font=("Arial", 10)
        )
        self.pool_selector.pack(side=tk.LEFT, padx=5)
        self.pool_selector.bind('<<ComboboxSelected>>', self._on_pool_changed)
        
        # Manage Pools button
        manage_btn = tk.Button(
            selector_frame,
            text="Manage Pools",
            command=self._show_manage_pools_dialog,
            bg="#3498db",
            fg="white",
            font=("Arial", 9, "bold"),
            padx=10,
            pady=3,
            relief=tk.FLAT,
            cursor="hand2"
        )
        manage_btn.pack(side=tk.LEFT, padx=5)
        
        # Pool info label
        if self.current_pool:
            info_text = f"{self.current_pool['volume']:,} {self.current_pool['unit']}"
            tk.Label(
                selector_frame,
                text=info_text,
                font=("Arial", 9),
                bg="#2c3e50",
                fg="#ecf0f1"
            ).pack(side=tk.LEFT, padx=10)

    def _on_pool_changed(self, event=None):
        """Handle pool selection change"""
        try:
            selected = self.pool_selector_var.get()
            # Extract pool name from "Name (Type)" format
            pool_name = selected.split(' (')[0]
            
            # Find and switch to selected pool
            for pool in self.pools:
                if pool['name'] == pool_name:
                    self._switch_pool(pool['id'])
                    break
        except Exception as e:
            logger.error(f"Error changing pool: {e}")

    def _switch_pool(self, pool_id):
        """Switch to a different pool"""
        try:
            # Find the pool
            new_pool = None
            for pool in self.pools:
                if pool['id'] == pool_id:
                    new_pool = pool
                    pool['is_active'] = True
                else:
                    pool['is_active'] = False
            
            if not new_pool:
                messagebox.showerror("Error", "Pool not found")
                return
            
            # Update current pool
            self.current_pool = new_pool
            self._save_pools()
            
            # Update title
            self.title(f"Deep Blue Pool Chemistry - {new_pool['name']}")
            
            # Reload all data for new pool
            self._reload_all_data()
            
            messagebox.showinfo("Pool Switched", f"Switched to: {new_pool['name']}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to switch pool: {str(e)}")

    def _reload_all_data(self):
        """Reload all data for current pool"""
        try:
            # Reload readings
            if hasattr(self, '_load_readings'):
                self.chemical_readings = []
                readings_file = self.data_dir / "readings.json"
                if readings_file.exists():
                    with open(readings_file, 'r') as f:
                        all_readings = json.load(f)
                    # Filter by current pool
                    self.chemical_readings = [r for r in all_readings if r.get('pool_id') == self.current_pool['id']]
            
            # Reload inventory
            if hasattr(self, '_load_inventory'):
                self._load_inventory()
            
            # Reload cost tracking
            if hasattr(self, '_load_purchases'):
                self._load_purchases()
            
            # Reload shopping list
            if hasattr(self, '_load_shopping_list'):
                self._load_shopping_list()
            
            # Refresh all tabs
            if hasattr(self, '_refresh_analytics_dashboard'):
                self._refresh_analytics_dashboard()
            
        except Exception as e:
            logger.error(f"Error reloading data: {e}")

    def _show_manage_pools_dialog(self):
        """Show pool management dialog"""
        dialog = tk.Toplevel(self)
        dialog.title("Manage Pools")
        dialog.geometry("800x500")
        dialog.transient(self)
        dialog.grab_set()
        
        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (400)
        y = (dialog.winfo_screenheight() // 2) - (250)
        dialog.geometry(f"+{x}+{y}")
        
        # Header
        header_frame = tk.Frame(dialog, bg="#2c3e50", pady=10)
        header_frame.pack(fill=tk.X)
        
        tk.Label(
            header_frame,
            text="Pool Management",
            font=("Arial", 16, "bold"),
            bg="#2c3e50",
            fg="white"
        ).pack()
        
        # Pools list
        list_frame = tk.Frame(dialog, padx=20, pady=10)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create Treeview
        columns = ("Name", "Type", "Volume", "Location", "Active")
        pools_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=10)
        
        for col in columns:
            pools_tree.heading(col, text=col)
            width = 150 if col == "Name" else 100
            pools_tree.column(col, width=width, anchor=tk.CENTER)
        
        # Populate pools
        for pool in self.pools:
            active = "Yes" if pool.get('is_active', False) else "No"
            pools_tree.insert('', 'end', values=(
                pool['name'],
                pool['type'].title(),
                f"{pool['volume']} {pool['unit']}",
                pool.get('location', ''),
                active
            ), tags=(pool['id'],))
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=pools_tree.yview)
        pools_tree.configure(yscrollcommand=scrollbar.set)
        
        pools_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Buttons
        btn_frame = tk.Frame(dialog, pady=10)
        btn_frame.pack(fill=tk.X)
        
        def add_pool():
            dialog.destroy()
            self._show_add_pool_dialog()
        
        def edit_pool():
            selection = pools_tree.selection()
            if not selection:
                messagebox.showwarning("No Selection", "Please select a pool to edit")
                return
            pool_id = pools_tree.item(selection[0])['tags'][0]
            dialog.destroy()
            self._show_edit_pool_dialog(pool_id)
        
        def delete_pool():
            selection = pools_tree.selection()
            if not selection:
                messagebox.showwarning("No Selection", "Please select a pool to delete")
                return
            
            if len(self.pools) <= 1:
                messagebox.showerror("Error", "Cannot delete the last pool")
                return
            
            pool_id = pools_tree.item(selection[0])['tags'][0]
            pool = next((p for p in self.pools if p['id'] == pool_id), None)
            
            if not messagebox.askyesno("Confirm Delete", f"Delete pool '{pool['name']}'?\n\nThis will delete all associated data!"):
                return
            
            # Remove pool
            self.pools = [p for p in self.pools if p['id'] != pool_id]
            
            # If deleted pool was active, switch to first pool
            if pool.get('is_active', False):
                self.pools[0]['is_active'] = True
                self.current_pool = self.pools[0]
            
            self._save_pools()
            dialog.destroy()
            self._reload_all_data()
            messagebox.showinfo("Success", f"Deleted pool '{pool['name']}'")
        
        def switch_pool():
            selection = pools_tree.selection()
            if not selection:
                messagebox.showwarning("No Selection", "Please select a pool to switch to")
                return
            pool_id = pools_tree.item(selection[0])['tags'][0]
            dialog.destroy()
            self._switch_pool(pool_id)
        
        tk.Button(
            btn_frame,
            text="Add New Pool",
            command=add_pool,
            bg="#27ae60",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=15,
            pady=5,
            relief=tk.FLAT,
            cursor="hand2"
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            btn_frame,
            text="Edit Pool",
            command=edit_pool,
            bg="#3498db",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=15,
            pady=5,
            relief=tk.FLAT,
            cursor="hand2"
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            btn_frame,
            text="Delete Pool",
            command=delete_pool,
            bg="#e74c3c",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=15,
            pady=5,
            relief=tk.FLAT,
            cursor="hand2"
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            btn_frame,
            text="Switch to Pool",
            command=switch_pool,
            bg="#9b59b6",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=15,
            pady=5,
            relief=tk.FLAT,
            cursor="hand2"
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            btn_frame,
            text="Close",
            command=dialog.destroy,
            bg="#95a5a6",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=15,
            pady=5,
            relief=tk.FLAT,
            cursor="hand2"
        ).pack(side=tk.RIGHT, padx=5)

    def _show_add_pool_dialog(self):
        """Show dialog to add new pool"""
        dialog = tk.Toplevel(self)
        dialog.title("Add New Pool")
        dialog.geometry("500x550")
        dialog.transient(self)
        dialog.grab_set()
        
        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (250)
        y = (dialog.winfo_screenheight() // 2) - (275)
        dialog.geometry(f"+{x}+{y}")
        
        # Form frame
        form_frame = tk.Frame(dialog, padx=20, pady=20)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # Pool Name
        tk.Label(form_frame, text="Pool Name:", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky=tk.W, pady=5)
        name_var = tk.StringVar()
        name_entry = ttk.Entry(form_frame, textvariable=name_var, width=30)
        name_entry.grid(row=0, column=1, sticky=tk.W, pady=5, padx=5)
        
        # Pool Type
        tk.Label(form_frame, text="Pool Type:", font=("Arial", 10, "bold")).grid(row=1, column=0, sticky=tk.W, pady=5)
        type_var = tk.StringVar(value="chlorine")
        type_frame = tk.Frame(form_frame)
        type_frame.grid(row=1, column=1, sticky=tk.W, pady=5, padx=5)
        
        tk.Radiobutton(type_frame, text="Chlorine Pool", variable=type_var, value="chlorine").pack(anchor=tk.W)
        tk.Radiobutton(type_frame, text="Salt Water Pool", variable=type_var, value="saltwater").pack(anchor=tk.W)
        tk.Radiobutton(type_frame, text="Hot Tub / Spa", variable=type_var, value="hottub").pack(anchor=tk.W)
        
        # Volume
        tk.Label(form_frame, text="Volume:", font=("Arial", 10, "bold")).grid(row=2, column=0, sticky=tk.W, pady=5)
        volume_var = tk.StringVar(value="20000")
        volume_entry = ttk.Entry(form_frame, textvariable=volume_var, width=30)
        volume_entry.grid(row=2, column=1, sticky=tk.W, pady=5, padx=5)
        
        # Unit
        tk.Label(form_frame, text="Unit:", font=("Arial", 10, "bold")).grid(row=3, column=0, sticky=tk.W, pady=5)
        unit_var = tk.StringVar(value="gallons")
        unit_combo = ttk.Combobox(form_frame, textvariable=unit_var, width=28)
        unit_combo['values'] = ["gallons", "liters"]
        unit_combo.grid(row=3, column=1, sticky=tk.W, pady=5, padx=5)
        
        # Location
        tk.Label(form_frame, text="Location:", font=("Arial", 10, "bold")).grid(row=4, column=0, sticky=tk.W, pady=5)
        location_var = tk.StringVar()
        location_entry = ttk.Entry(form_frame, textvariable=location_var, width=30)
        location_entry.grid(row=4, column=1, sticky=tk.W, pady=5, padx=5)
        
        # Notes
        tk.Label(form_frame, text="Notes:", font=("Arial", 10, "bold")).grid(row=5, column=0, sticky=tk.W, pady=5)
        notes_text = tk.Text(form_frame, width=30, height=4)
        notes_text.grid(row=5, column=1, sticky=tk.W, pady=5, padx=5)
        
        # Buttons
        btn_frame = tk.Frame(form_frame)
        btn_frame.grid(row=6, column=0, columnspan=2, pady=20)
        
        def save_pool():
            try:
                if not name_var.get():
                    messagebox.showerror("Error", "Please enter pool name")
                    return
                
                # Generate ID
                max_id = 0
                for pool in self.pools:
                    try:
                        pool_num = int(pool['id'].replace('POOL', ''))
                        max_id = max(max_id, pool_num)
                    except:
                        pass
                new_id = f"POOL{max_id + 1:03d}"
                
                # Create new pool
                new_pool = {
                    'id': new_id,
                    'name': name_var.get(),
                    'type': type_var.get(),
                    'volume': float(volume_var.get() or 0),
                    'unit': unit_var.get(),
                    'location': location_var.get(),
                    'created_date': datetime.now().strftime('%Y-%m-%d'),
                    'is_active': False,
                    'notes': notes_text.get('1.0', tk.END).strip()
                }
                
                # Add to pools
                self.pools.append(new_pool)
                self._save_pools()
                
                # Update pool selector
                pool_names = [f"{p['name']} ({p['type'].title()})" for p in self.pools]
                self.pool_selector['values'] = pool_names
                
                messagebox.showinfo("Success", f"Added pool '{new_pool['name']}'")
                dialog.destroy()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add pool: {str(e)}")
        
        tk.Button(
            btn_frame,
            text="Save Pool",
            command=save_pool,
            bg="#27ae60",
            fg="white",
            font=("Arial", 11, "bold"),
            padx=30,
            pady=8,
            relief=tk.FLAT,
            cursor="hand2"
        ).pack(side=tk.LEFT, padx=10)
        
        tk.Button(
            btn_frame,
            text="Cancel",
            command=dialog.destroy,
            bg="#95a5a6",
            fg="white",
            font=("Arial", 11, "bold"),
            padx=30,
            pady=8,
            relief=tk.FLAT,
            cursor="hand2"
        ).pack(side=tk.LEFT, padx=10)

    def _show_edit_pool_dialog(self, pool_id):
        """Show dialog to edit existing pool"""
        # Find the pool
        pool = next((p for p in self.pools if p['id'] == pool_id), None)
        if not pool:
            messagebox.showerror("Error", "Pool not found")
            return
        
        dialog = tk.Toplevel(self)
        dialog.title(f"Edit Pool: {pool['name']}")
        dialog.geometry("500x550")
        dialog.transient(self)
        dialog.grab_set()
        
        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (250)
        y = (dialog.winfo_screenheight() // 2) - (275)
        dialog.geometry(f"+{x}+{y}")
        
        # Form frame
        form_frame = tk.Frame(dialog, padx=20, pady=20)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # Pool Name
        tk.Label(form_frame, text="Pool Name:", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky=tk.W, pady=5)
        name_var = tk.StringVar(value=pool['name'])
        name_entry = ttk.Entry(form_frame, textvariable=name_var, width=30)
        name_entry.grid(row=0, column=1, sticky=tk.W, pady=5, padx=5)
        
        # Pool Type
        tk.Label(form_frame, text="Pool Type:", font=("Arial", 10, "bold")).grid(row=1, column=0, sticky=tk.W, pady=5)
        type_var = tk.StringVar(value=pool['type'])
        type_frame = tk.Frame(form_frame)
        type_frame.grid(row=1, column=1, sticky=tk.W, pady=5, padx=5)
        
        tk.Radiobutton(type_frame, text="Chlorine Pool", variable=type_var, value="chlorine").pack(anchor=tk.W)
        tk.Radiobutton(type_frame, text="Salt Water Pool", variable=type_var, value="saltwater").pack(anchor=tk.W)
        tk.Radiobutton(type_frame, text="Hot Tub / Spa", variable=type_var, value="hottub").pack(anchor=tk.W)
        
        # Volume
        tk.Label(form_frame, text="Volume:", font=("Arial", 10, "bold")).grid(row=2, column=0, sticky=tk.W, pady=5)
        volume_var = tk.StringVar(value=str(pool['volume']))
        volume_entry = ttk.Entry(form_frame, textvariable=volume_var, width=30)
        volume_entry.grid(row=2, column=1, sticky=tk.W, pady=5, padx=5)
        
        # Unit
        tk.Label(form_frame, text="Unit:", font=("Arial", 10, "bold")).grid(row=3, column=0, sticky=tk.W, pady=5)
        unit_var = tk.StringVar(value=pool['unit'])
        unit_combo = ttk.Combobox(form_frame, textvariable=unit_var, width=28)
        unit_combo['values'] = ["gallons", "liters"]
        unit_combo.grid(row=3, column=1, sticky=tk.W, pady=5, padx=5)
        
        # Location
        tk.Label(form_frame, text="Location:", font=("Arial", 10, "bold")).grid(row=4, column=0, sticky=tk.W, pady=5)
        location_var = tk.StringVar(value=pool.get('location', ''))
        location_entry = ttk.Entry(form_frame, textvariable=location_var, width=30)
        location_entry.grid(row=4, column=1, sticky=tk.W, pady=5, padx=5)
        
        # Notes
        tk.Label(form_frame, text="Notes:", font=("Arial", 10, "bold")).grid(row=5, column=0, sticky=tk.W, pady=5)
        notes_text = tk.Text(form_frame, width=30, height=4)
        notes_text.insert('1.0', pool.get('notes', ''))
        notes_text.grid(row=5, column=1, sticky=tk.W, pady=5, padx=5)
        
        # Buttons
        btn_frame = tk.Frame(form_frame)
        btn_frame.grid(row=6, column=0, columnspan=2, pady=20)
        
        def save_changes():
            try:
                if not name_var.get():
                    messagebox.showerror("Error", "Please enter pool name")
                    return
                
                # Update pool
                pool['name'] = name_var.get()
                pool['type'] = type_var.get()
                pool['volume'] = float(volume_var.get() or 0)
                pool['unit'] = unit_var.get()
                pool['location'] = location_var.get()
                pool['notes'] = notes_text.get('1.0', tk.END).strip()
                
                self._save_pools()
                
                # Update pool selector if this is current pool
                if pool['id'] == self.current_pool['id']:
                    self.pool_selector_var.set(f"{pool['name']} ({pool['type'].title()})")
                    self.title(f"Deep Blue Pool Chemistry - {pool['name']}")
                
                # Update pool selector values
                pool_names = [f"{p['name']} ({p['type'].title()})" for p in self.pools]
                self.pool_selector['values'] = pool_names
                
                messagebox.showinfo("Success", f"Updated pool '{pool['name']}'")
                dialog.destroy()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update pool: {str(e)}")
        
        tk.Button(
            btn_frame,
            text="Save Changes",
            command=save_changes,
            bg="#27ae60",
            fg="white",
            font=("Arial", 11, "bold"),
            padx=30,
            pady=8,
            relief=tk.FLAT,
            cursor="hand2"
        ).pack(side=tk.LEFT, padx=10)
        
        tk.Button(
            btn_frame,
            text="Cancel",
            command=dialog.destroy,
            bg="#95a5a6",
            fg="white",
            font=("Arial", 11, "bold"),
            padx=30,
            pady=8,
            relief=tk.FLAT,
            cursor="hand2"
        ).pack(side=tk.LEFT, padx=10)

    def _get_chemical_ranges_for_pool(self):
        """Get chemical ranges based on current pool type"""
        if not self.current_pool:
            return {}
        
        pool_type = self.current_pool.get('type', 'chlorine')
        
        if pool_type in self.pool_type_specs:
            return self.pool_type_specs[pool_type]['chemical_ranges']
        
        # Default to chlorine ranges
        return self.pool_type_specs.get('chlorine', {}).get('chemical_ranges', {})

    def _filter_data_by_pool(self, data_list):
        """Filter data list by current pool ID"""
        if not self.current_pool:
            return data_list
        
        pool_id = self.current_pool['id']
        return [item for item in data_list if item.get('pool_id') == pool_id]

    def _add_pool_id_to_data(self, data_dict):
        """Add current pool ID to data dictionary"""
        if self.current_pool:
            data_dict['pool_id'] = self.current_pool['id']
        return data_dict

    def _safe_format(self, value, decimals=2, default='--'):
        """Safely format numeric values"""
        if value is None:
            return default
        try:
            return f"{float(value):.{decimals}f}"
        except (ValueError, TypeError):
            return default
    

    def _show_loading(self, message="Loading..."):
        """Show loading indicator"""
        if hasattr(self, '_loading_label'):
            self._loading_label.destroy()
        
        self._loading_label = tk.Label(
            self.history_tab,
            text=message,
            font=("Arial", 14, "bold"),
            bg="white",
            fg="#3498db"
        )
        self._loading_label.place(relx=0.5, rely=0.5, anchor="center")
        self.update()
    
    def _hide_loading(self):
        """Hide loading indicator"""
        if hasattr(self, '_loading_label'):
            self._loading_label.destroy()
    
    def _refresh_analytics_dashboard(self):
            """Refresh all analytics dashboard data"""
            try:
                self._show_loading("Refreshing Analytics Dashboard...")
                logger.info("Refreshing analytics dashboard...")
            
                # Load readings
                readings = self.chemical_readings if hasattr(self, "chemical_readings") else []
                if not readings:
                    logger.warning("No readings found")
                    return
            
                # Filter by date range
                filtered_readings = self._filter_readings_by_range(readings, self.analytics_range_var.get())
            
                if not filtered_readings:
                    logger.warning("No readings in selected range")
                    return
            
                # Update metric cards
                self._update_metric_cards(filtered_readings)  # DISABLED: Pool Health Score removed from Analytics Dashboard
                # 
            
                # DISABLED: Pool Health Score removed from Analytics Dashboard
                # self._update_health_score(filtered_readings)
            
                # Update statistics table
                self._update_statistics_table(filtered_readings)
            
                # Update chart
                self._update_analytics_chart()
            
                # Update anomalies
                self._update_anomalies_alerts(filtered_readings)
            
                # Update recent readings table
                self._update_recent_readings_table(filtered_readings[:50])  # Last 50 from filtered range
            
                logger.info("Analytics dashboard refreshed successfully")
                self._hide_loading()
            
            except Exception as e:
                logger.error(f"Error refreshing analytics dashboard: {e}")
                self._hide_loading()
                import traceback
                traceback.print_exc()


    def _filter_readings_by_range(self, readings, range_str):
        """Filter readings by date range"""
        from datetime import datetime, timedelta
        
        if range_str == "All Time":
            return readings
        
        # Handle Today
        if range_str == "Today":
            today = datetime.now().date()
            filtered = []
            for reading in readings:
                try:
                    reading_date = datetime.strptime(reading['date'], '%Y-%m-%d').date()
                    if reading_date == today:
                        filtered.append(reading)
                except Exception as e:
                    continue
            return filtered
        
        # Handle Custom Range
        if range_str == "Custom Range" or range_str.startswith("Custom:"):
            return self._show_custom_date_picker(readings)
        
        # Parse days
        days_map = {
            "Last 7 Days": 7,
            "Last 30 Days": 30,
            "Last 90 Days": 90
        }
        
        days = days_map.get(range_str, 30)
        cutoff_date = datetime.now() - timedelta(days=days)
        
        filtered = []
        for reading in readings:
            try:
                reading_date = datetime.strptime(reading['date'], '%Y-%m-%d')
                if reading_date >= cutoff_date:
                    filtered.append(reading)
            except Exception as e:
                continue
        
        return filtered



    def _show_custom_date_picker(self, readings):
        """Show custom date range picker dialog"""
        from datetime import datetime
        import tkinter as tk
        from tkinter import ttk, messagebox
        
        dialog = tk.Toplevel(self)
        dialog.title("Custom Date Range")
        dialog.geometry("400x250")
        dialog.resizable(False, False)
        
        # Center the dialog
        dialog.transient(self)
        dialog.grab_set()
        
        # Main frame
        main_frame = tk.Frame(dialog, bg="white", padx=20, pady=20)
        main_frame.pack(fill="both", expand=True)
        
        # Title
        tk.Label(main_frame, text="Select Date Range", font=("Arial", 14, "bold"),
                bg="white", fg="#2c3e50").pack(pady=(0, 20))
        
        # Start date
        start_frame = tk.Frame(main_frame, bg="white")
        start_frame.pack(fill="x", pady=5)
        tk.Label(start_frame, text="Start Date:", font=("Arial", 10),
                bg="white", width=12, anchor="w").pack(side="left")
        
        start_date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        start_entry = tk.Entry(start_frame, textvariable=start_date_var, font=("Arial", 10), width=15)
        start_entry.pack(side="left", padx=5)
        tk.Label(start_frame, text="(YYYY-MM-DD)", font=("Arial", 8),
                bg="white", fg="#7f8c8d").pack(side="left")
        
        # End date
        end_frame = tk.Frame(main_frame, bg="white")
        end_frame.pack(fill="x", pady=5)
        tk.Label(end_frame, text="End Date:", font=("Arial", 10),
                bg="white", width=12, anchor="w").pack(side="left")
        
        end_date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        end_entry = tk.Entry(end_frame, textvariable=end_date_var, font=("Arial", 10), width=15)
        end_entry.pack(side="left", padx=5)
        tk.Label(end_frame, text="(YYYY-MM-DD)", font=("Arial", 8),
                bg="white", fg="#7f8c8d").pack(side="left")
        
        # Result variable
        result = {"filtered": readings}  # Default to all readings
        
        def apply_filter():
            try:
                start_str = start_date_var.get()
                end_str = end_date_var.get()
                
                start_date = datetime.strptime(start_str, "%Y-%m-%d").date()
                end_date = datetime.strptime(end_str, "%Y-%m-%d").date()
                
                if start_date > end_date:
                    messagebox.showerror("Invalid Range", "Start date must be before end date")
                    return
                
                # Filter readings
                filtered = []
                for reading in readings:
                    try:
                        reading_date = datetime.strptime(reading['date'], '%Y-%m-%d').date()
                        if start_date <= reading_date <= end_date:
                            filtered.append(reading)
                    except Exception as e:
                        continue
                
                result["filtered"] = filtered
                
                # Update the range display
                self.analytics_range_var.set(f"Custom: {start_str} to {end_str}")
                
                dialog.destroy()
                
            except ValueError:
                messagebox.showerror("Invalid Date", "Please enter dates in YYYY-MM-DD format")
        
        def cancel():
            dialog.destroy()
        
        # Buttons
        button_frame = tk.Frame(main_frame, bg="white")
        button_frame.pack(pady=20)
        
        apply_btn = tk.Button(button_frame, text="Apply", command=apply_filter,
                             font=("Arial", 10, "bold"), bg="#3498db", fg="white",
                             padx=20, pady=5, cursor="hand2")
        apply_btn.pack(side="left", padx=5)
        
        cancel_btn = tk.Button(button_frame, text="Cancel", command=cancel,
                              font=("Arial", 10), bg="#95a5a6", fg="white",
                              padx=20, pady=5, cursor="hand2")
        cancel_btn.pack(side="left", padx=5)
        
        # Wait for dialog to close
        dialog.wait_window()
        
        return result["filtered"]

    def _update_metric_cards(self, readings):
        """Update metric cards with current values and trends"""
        import statistics
        
        metrics = ['ph', 'free_chlorine', 'total_chlorine', 'alkalinity', 'calcium_hardness', 'cyanuric_acid', 'temperature', 'bromine', 'salt']
        
        for metric in metrics:
            try:
                # Get values
                values = [r[metric] for r in readings if metric in r and r[metric] is not None]
                
                if not values:
                    continue
                
                # Current value (most recent)
                current = values[0]
                
                # Define units
                units = {
                    'ph': '',
                    'free_chlorine': ' ppm',
                    'total_chlorine': ' ppm',
                    'alkalinity': ' ppm',
                    'calcium_hardness': ' ppm',
                    'cyanuric_acid': ' ppm',
                    'temperature': '°FF',
                    'bromine': ' ppm',
                    'salt': ' ppm'
                }
                unit = units.get(metric, '')
                
                # Calculate trend (compare last 3 vs previous 3)
                if len(values) >= 6:
                    recent_avg = statistics.mean(values[:3])
                    previous_avg = statistics.mean(values[3:6])
                    trend_pct = ((recent_avg - previous_avg) / previous_avg) * 100
                    
                    if abs(trend_pct) < 1:
                        trend_text = "-> Stable"
                        trend_color = "white"
                    elif trend_pct > 0:
                        trend_text = f"^ +{trend_pct:.1f}%"
                        trend_color = "white"
                    else:
                        trend_text = f"v {trend_pct:.1f}%"
                        trend_color = "white"
                else:
                    trend_text = "-- No trend"
                    trend_color = "white"
                
                # Update card with units
                if metric in self.metric_cards:
                    self.metric_cards[metric]['value'].config(text=f"{current:.2f}{unit}")
                    self.metric_cards[metric]['trend'].config(text=trend_text, fg=trend_color)
                    
            except Exception as e:
                logger.error(f"Error updating metric card for {metric}: {e}")


    # DISABLED:     def _update_health_score(self, readings):
    # DISABLED:         """Calculate and display overall pool health score"""
    # DISABLED:         try:
    # DISABLED:             if not readings:
    # DISABLED:                 return
            
    # DISABLED:             latest = readings[0]
            
            # Define ideal ranges and scoring
    # DISABLED:             ranges = {
    # DISABLED:                 'ph': (7.2, 7.6, 7.4),
    # DISABLED:                 'free_chlorine': (1.0, 3.0, 2.0),
    # DISABLED:                 'total_chlorine': (1.0, 3.0, 2.0),
    # DISABLED:                 'alkalinity': (80, 120, 100),
    # DISABLED:                 'calcium_hardness': (200, 400, 300),
    # DISABLED:                 'cyanuric_acid': (30, 50, 40)
    # DISABLED:             }
            
    # DISABLED:             scores = []
    # DISABLED:             for metric, (min_val, max_val, ideal) in ranges.items():
    # DISABLED:                 if metric in latest and latest[metric] is not None:
    # DISABLED:                     value = latest[metric]
                    
                    # Calculate score (0-100)
    # DISABLED:                     if min_val <= value <= max_val:
                        # Within range - score based on distance from ideal
    # DISABLED:                         distance = abs(value - ideal)
    # DISABLED:                         max_distance = max(ideal - min_val, max_val - ideal)
    # DISABLED:                         score = 100 - (distance / max_distance * 20)  # Max 20 points deduction
    # DISABLED:                     else:
                        # Out of range
    # DISABLED:                         if value < min_val:
    # DISABLED:                             distance = min_val - value
    # DISABLED:                             score = max(0, 80 - (distance / min_val * 80))
    # DISABLED:                         else:
    # DISABLED:                             distance = value - max_val
    # DISABLED:                             score = max(0, 80 - (distance / max_val * 80))
                    
    # DISABLED:                     scores.append(score)
            
            # Calculate overall score
    # DISABLED:             if scores:
    # DISABLED:                 overall_score = sum(scores) / len(scores)
    # DISABLED:             else:
    # DISABLED:                 overall_score = 0
            
            # Draw gauge
    # DISABLED:             self._draw_health_gauge(overall_score)
            
            # Update label
    # DISABLED:             if overall_score >= 90:
    # DISABLED:                 status = "Excellent [OK]"
    # DISABLED:                 color = "#27ae60"
    # DISABLED:             elif overall_score >= 75:
    # DISABLED:                 status = "Good"
    # DISABLED:                 color = "#3498db"
    # DISABLED:             elif overall_score >= 60:
    # DISABLED:                 status = "Fair [!]"
    # DISABLED:                 color = "#f39c12"
    # DISABLED:             else:
    # DISABLED:                 status = "Needs Attention [!]"
    # DISABLED:                 color = "#e74c3c"
            
    # DISABLED:             self.health_score_label.config(
    # DISABLED:                 text=f"Score: {overall_score:.0f}/100 - {status}",
    # DISABLED:                 fg=color
    # DISABLED:             )
            
    # DISABLED:         except Exception as e:
    # DISABLED:             logger.error(f"Error updating health score: {e}")


    # DISABLED:     def _draw_health_gauge(self, score):
    # DISABLED:         """Draw circular health gauge"""
    # DISABLED:         try:
    # DISABLED:             canvas = self.analytics_health_canvas
    # DISABLED:             canvas.delete("all")
            
            # Center and radius
    # DISABLED:             cx, cy = 150, 150
    # DISABLED:             radius = 110  # Larger radius for bigger canvas
            
            # Background circle
    # DISABLED:             canvas.create_oval(
    # DISABLED:                 cx - radius, cy - radius,
    # DISABLED:                 cx + radius, cy + radius,
    # DISABLED:                 fill="#ecf0f1", outline="#bdc3c7", width=3
    # DISABLED:             )
            
            # Score arc
    # DISABLED:             if score >= 90:
    # DISABLED:                 color = "#27ae60"
    # DISABLED:             elif score >= 75:
    # DISABLED:                 color = "#3498db"
    # DISABLED:             elif score >= 60:
    # DISABLED:                 color = "#f39c12"
    # DISABLED:             else:
    # DISABLED:                 color = "#e74c3c"
            
            # Calculate arc extent (0-360°Frees)
    # DISABLED:             extent = (score / 100) * 360
            
    # DISABLED:             canvas.create_arc(
    # DISABLED:                 cx - radius, cy - radius,
    # DISABLED:                 cx + radius, cy + radius,
    # DISABLED:                 start=90, extent=-extent,
    # DISABLED:                 fill=color, outline=color, width=3
    # DISABLED:             )
            
            # Inner circle
    # DISABLED:             inner_radius = radius - 20
    # DISABLED:             canvas.create_oval(
    # DISABLED:                 cx - inner_radius, cy - inner_radius,
    # DISABLED:                 cx + inner_radius, cy + inner_radius,
    # DISABLED:                 fill="white", outline="#bdc3c7", width=2
    # DISABLED:             )
            
            # Score text
    # DISABLED:             canvas.create_text(
    # DISABLED:                 cx, cy,
    # DISABLED:                 text=f"{score:.0f}",
    # DISABLED:                 font=("Arial", 48, "bold"),
    # DISABLED:                 fill=color
    # DISABLED:             )
            
    # DISABLED:         except Exception as e:
    # DISABLED:             logger.error(f"Error drawing health gauge: {e}")


    def _update_statistics_table(self, readings):
        """Update statistics summary table"""
        try:
            import statistics
            
            # Clear existing items
            for item in self.stats_tree.get_children():
                self.stats_tree.delete(item)
            
            metrics_config = [
                ('pH', 'ph', 7.2, 7.6),
                ('Free Chlorine', 'free_chlorine', 1.0, 3.0),
                ('Total Chlorine', 'total_chlorine', 1.0, 3.0),
                ('Alkalinity', 'alkalinity', 80, 120),
                ('Ca Hardness', 'calcium_hardness', 200, 400),
                ('Cyanuric Acid', 'cyanuric_acid', 30, 50),
                ('Temperature', 'temperature', 78, 82),
                ('Bromine', 'bromine', 2.0, 4.0),
                ('Salt/TDS', 'salt', 2700, 3400)
            ]
            
            for name, key, min_ideal, max_ideal in metrics_config:
                values = [r[key] for r in readings if key in r and r[key] is not None]
                
                if not values:
                    continue
                
                current = values[0]
                min_val = min(values)
                max_val = max(values)
                avg_val = statistics.mean(values)
                std_val = statistics.stdev(values) if len(values) > 1 else 0
                
                # Determine status
                if min_ideal <= current <= max_ideal:
                    status = "Good"
                    tag = "good"
                elif current < min_ideal:
                    status = "v Low"
                    tag = "low"
                else:
                    status = "^ High"
                    tag = "high"
                
                # Insert row
                self.stats_tree.insert(
                    "",
                    "end",
                    values=(
                        name,
                        f"{current:.2f}",
                        f"{min_val:.2f}",
                        f"{max_val:.2f}",
                        f"{avg_val:.2f}",
                        f"{std_val:.2f}",
                        status
                    ),
                    tags=(tag,)
                )
            
            # Configure tags
            self.stats_tree.tag_configure("good", foreground="#27ae60")
            self.stats_tree.tag_configure("low", foreground="#e67e22")
            self.stats_tree.tag_configure("high", foreground="#e74c3c")
            
        except Exception as e:
            logger.error(f"Error updating statistics table: {e}")


    def _update_analytics_chart(self):
        """Update the analytics chart based on selected type and metric"""
        try:
            from matplotlib.figure import Figure
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
            from datetime import datetime
            
            # Clear existing chart
            for widget in self.chart_frame.winfo_children():
                widget.destroy()
            
            # Load and filter readings
            readings = self.chemical_readings if hasattr(self, "chemical_readings") else []
            filtered_readings = self._filter_readings_by_range(readings, self.analytics_range_var.get())
            
            if not filtered_readings:
                tk.Label(
                    self.chart_frame,
                    text="No data available for selected range",
                    font=("Arial", 12),
                    bg="white"
                ).pack(expand=True)
                return
            
            # Create figure
            fig = Figure(figsize=(10, 4), dpi=100)
            ax = fig.add_subplot(111)
            
            chart_type = self.chart_type_var.get()
            
            if chart_type == "Multi-Metric":
                # Plot multiple metrics
                metrics = ['ph', 'free_chlorine', 'alkalinity']
                colors = ['#3498db', '#27ae60', '#e67e22']
                
                for metric, color in zip(metrics, colors):
                    values = []
                    dates = []
                    for r in filtered_readings:
                        if metric in r and r[metric] is not None:
                            try:
                                date_obj = datetime.strptime(r['date'], '%Y-%m-%d')
                                values.append(r[metric])
                                dates.append(date_obj)
                            except Exception as e:
                                continue
                    
                    if values and dates:
                        # Reverse to show oldest to newest
                        values.reverse()
                        dates.reverse()
                        ax.plot(dates, values, marker='o', label=metric.replace('_', ' ').title(), color=color, linewidth=2)
                
                ax.legend()
                ax.set_title("Multi-Metric Trends", fontsize=14, fontweight='bold')
                
            else:
                # Single metric
                metric_map = {
                    "pH": "ph",
                    "Free Chlorine": "free_chlorine",
                    "Total Chlorine": "total_chlorine",
                    "Alkalinity": "alkalinity",
                    "Calcium Hardness": "calcium_hardness",
                    "Cyanuric Acid": "cyanuric_acid",
                    "Temperature": "temperature",
                    "Bromine": "bromine",
                    "Salt/TDS": "salt"
                }
                
                metric = metric_map.get(self.chart_metric_var.get(), "ph")
                
                # Extract values and dates with error handling
                values = []
                dates = []
                for r in filtered_readings:
                    if metric in r and r[metric] is not None:
                        try:
                            date_obj = datetime.strptime(r['date'], '%Y-%m-%d')
                            values.append(r[metric])
                            dates.append(date_obj)
                        except Exception as e:
                            logger.warning(f"Skipping reading with invalid date: {r.get('date')}")
                            continue
                
                # Reverse to show oldest to newest (left to right)
                values.reverse()
                dates.reverse()
                
                if not values or not dates:
                    tk.Label(
                        self.chart_frame,
                        text=f"No data available for {self.chart_metric_var.get()}",
                        font=("Arial", 12),
                        bg="white"
                    ).pack(expand=True)
                    return
                
                if chart_type == "Line Chart":
                    ax.plot(dates, values, marker='o', color='#3498db', linewidth=2, markersize=6)
                elif chart_type == "Bar Chart":
                    ax.bar(dates, values, color='#3498db', alpha=0.7)
                elif chart_type == "Scatter Plot":
                    ax.scatter(dates, values, color='#3498db', s=100, alpha=0.6)
                
                ax.set_title(f"{self.chart_metric_var.get()} Over Time", fontsize=14, fontweight='bold')
            
            ax.set_xlabel("Date", fontsize=10)
            ax.set_ylabel("Value", fontsize=10)
            ax.grid(True, alpha=0.3)
            
            # Add ideal range lines for single metric charts
            if chart_type != "Multi-Metric":
                ideal_ranges = {
                    'ph': (7.2, 7.6),
                    'free_chlorine': (1.0, 3.0),
                    'total_chlorine': (1.0, 3.0),
                    'alkalinity': (80, 120),
                    'calcium_hardness': (200, 400),
                    'cyanuric_acid': (30, 50),
                    'temperature': (78, 82),
                    'bromine': (2.0, 4.0),
                    'salt': (2700, 3400)
                }
                
                if metric in ideal_ranges:
                    min_ideal, max_ideal = ideal_ranges[metric]
                    ax.axhline(y=min_ideal, color='green', linestyle='--', alpha=0.5, linewidth=1.5, label='Min Ideal')
                    ax.axhline(y=max_ideal, color='green', linestyle='--', alpha=0.5, linewidth=1.5, label='Max Ideal')
                    ax.legend(loc='best', framealpha=0.9)
            
            fig.autofmt_xdate()
            fig.tight_layout()
            
            # Embed in tkinter
            canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)
            
        except Exception as e:
            logger.error(f"Error updating analytics chart: {e}")
            import traceback
            traceback.print_exc()


    def _update_anomalies_alerts(self, readings):
        """Detect and display anomalies"""
        try:
            import statistics
            
            self.alerts_text.delete(1.0, tk.END)
            
            if len(readings) < 10:
                self.alerts_text.insert(tk.END, "Need at least 10 readings to detect anomalies.\n")
                return
            
            anomalies_found = False
            
            metrics = ['ph', 'free_chlorine', 'total_chlorine', 'alkalinity', 'calcium_hardness', 'cyanuric_acid', 'bromine', 'salt']
            
            for metric in metrics:
                values = [r[metric] for r in readings if metric in r and r[metric] is not None]
                
                if len(values) < 10:
                    continue
                
                mean = statistics.mean(values)
                stdev = statistics.stdev(values)
                
                # Check latest reading
                latest = values[0]
                z_score = abs((latest - mean) / stdev) if stdev > 0 else 0
                
                if z_score > 3:  # 3 standard deviations (more conservative)
                    anomalies_found = True
                    self.alerts_text.insert(
                        tk.END,
                        f"ANOMALY DETECTED: {metric.replace('_', ' ').title()}\n"
                    )
                    self.alerts_text.insert(
                        tk.END,
                        f"   Current: {latest:.2f} | Average: {mean:.2f} | Deviation: {z_score:.2f}sigma\n\n"
                    )
            
            if not anomalies_found:
                self.alerts_text.insert(tk.END, "No anomalies detected. All readings within normal range.\n")
            
        except Exception as e:
            logger.error(f"Error updating anomalies: {e}")


    def _update_recent_readings_table(self, readings):
        """Update recent readings table with sorted data and safe formatting"""
        try:
            # Clear existing items
            for item in self.readings_tree.get_children():
                self.readings_tree.delete(item)
            
            # Sort by date and time (newest first)
            sorted_readings = sorted(
                readings,
                key=lambda r: (r.get('date', ''), r.get('time', '')),
                reverse=True
            )
            
            # Insert readings with safe formatting
            for reading in sorted_readings[:50]:  # Last 50
                self.readings_tree.insert(
                    "",
                    "end",
                    values=(
                        reading.get('date', '--'),
                        reading.get('time', '--'),
                        self._safe_format(reading.get('ph'), 2),
                        self._safe_format(reading.get('free_chlorine'), 2),
                        self._safe_format(reading.get('total_chlorine'), 2),
                        self._safe_format(reading.get('alkalinity'), 1),
                        self._safe_format(reading.get('calcium_hardness'), 1),
                        self._safe_format(reading.get('cyanuric_acid'), 1),
                        self._safe_format(reading.get('temperature'), 1),
                        self._safe_format(reading.get('bromine'), 2),
                        self._safe_format(reading.get('salt'), 0)
                    )
                )
            
        except Exception as e:
            logger.error(f"Error updating recent readings table: {e}")


    def _export_analytics_report(self):
        """Export analytics report to CSV"""
        try:
            from tkinter import filedialog
            import csv
            from datetime import datetime
            
            # Ask for save location
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                initialfile=f"pool_analytics_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            )
            
            if not filename:
                return
            
            # Load readings
            readings = self.chemical_readings if hasattr(self, "chemical_readings") else []
            filtered_readings = self._filter_readings_by_range(readings, self.analytics_range_var.get())
            
            if not filtered_readings:
                messagebox.showwarning("No Data", "No readings to export")
                return
            
            # Write to CSV
            with open(filename, 'w', newline='') as f:
                fieldnames = ['date', 'time', 'ph', 'free_chlorine', 'total_chlorine', 
                             'alkalinity', 'calcium_hardness', 'cyanuric_acid', 'temperature', 'bromine', 'salt']
                writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
                
                writer.writeheader()
                for reading in filtered_readings:
                    writer.writerow(reading)
            
            messagebox.showinfo("Export Complete", f"Analytics report exported to:\n{filename}")
            logger.info(f"Analytics report exported to {filename}")
            
        except (IOError, PermissionError, OSError) as e:
            logger.error(f"Error exporting analytics report: {e}")
            messagebox.showerror("Export Error", f"Failed to export report:\n{str(e)}")
    def _create_settings_tab(self):
        """Create the settings tab content"""
        # Settings frame
        self.settings_frame = ttk.Frame(self.settings_tab)
        self.settings_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Theme selection
        # Auto backup toggle
        ttk.Label(self.settings_frame, text="Auto Backup:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.auto_backup_var = tk.BooleanVar(value=True)
        auto_backup_checkbox = ttk.Checkbutton(
            self.settings_frame,
            variable=self.auto_backup_var,
            onvalue=True,
            offvalue=False
        )
        auto_backup_checkbox.grid(row=1, column=1, sticky="w", padx=5, pady=2)

        # Save settings button
        save_settings_button = ttk.Button(
            self.settings_frame,
            text="Save Settings",
            command=self._save_settings
        )
        save_settings_button.grid(row=2, column=0, columnspan=2, sticky="w", padx=5, pady=2)

    
    

    def _create_analytics_tab(self):
        """Create the ML Analytics tab content"""
        # Main container with scrollbar
        main_container = ttk.Frame(self.analytics_tab)
        main_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Title
        title_frame = tk.Frame(main_container, bg="#3498db", height=50)
        title_frame.pack(fill="x", pady=(0, 10))
        title_frame.pack_propagate(False)
        
        tk.Label(
            title_frame,
            text="Machine Learning & Deep Analytics",
            font=("Arial", 16, "bold"),
            fg="white",
            bg="#3498db"
        ).pack(pady=10)
        
        # Create notebook for different analytics sections
        analytics_notebook = ttk.Notebook(main_container)
        analytics_notebook.pack(fill="both", expand=True)
        
        # Predictions Tab
        predictions_frame = ttk.Frame(analytics_notebook)
        analytics_notebook.add(predictions_frame, text="Predictions")
        self._create_predictions_section(predictions_frame)
        
        # Insights Tab
        insights_frame = ttk.Frame(analytics_notebook)
        analytics_notebook.add(insights_frame, text="Insights")
        self._create_insights_section(insights_frame)
        
        # Trends Tab
        trends_frame = ttk.Frame(analytics_notebook)
        analytics_notebook.add(trends_frame, text="Trends")
        self._create_trends_section(trends_frame)
        
        # Optimization Tab
        optimization_frame = ttk.Frame(analytics_notebook)
        analytics_notebook.add(optimization_frame, text="Cost Optimization")
        self._create_optimization_section(optimization_frame)
        
        # Anomalies Tab
        anomalies_frame = ttk.Frame(analytics_notebook)
        analytics_notebook.add(anomalies_frame, text="Anomaly Detection")
        self._create_anomalies_section(anomalies_frame)
        
    def _create_predictions_section(self, parent):
        """Create predictions section"""
        # Header
        header = tk.Frame(parent, bg="#27ae60", height=40)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        tk.Label(
            header,
            text="Predictive Analytics - Next Reading Forecast",
            font=("Arial", 12, "bold"),
            fg="white",
            bg="#27ae60"
        ).pack(pady=8)
        
        # Content
        self.predictions_display = tk.Text(parent, height=20, wrap="word", font=("Arial", 10))
        self.predictions_display.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Refresh button
        ttk.Button(
            parent,
            text="Generate Predictions",
            command=self._update_predictions
        ).pack(pady=10)
        
    def _create_insights_section(self, parent):
        """Create insights section"""
        # Header
        header = tk.Frame(parent, bg="#e67e22", height=40)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        tk.Label(
            header,
            text="AI-Powered Insights & Recommendations",
            font=("Arial", 12, "bold"),
            fg="white",
            bg="#e67e22"
        ).pack(pady=8)
        
        # Content
        self.insights_display = tk.Text(parent, height=20, wrap="word", font=("Arial", 10))
        self.insights_display.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Refresh button
        ttk.Button(
            parent,
            text="Generate Insights",
            command=self._update_insights
        ).pack(pady=10)
        
    def _create_trends_section(self, parent):
        """Create trends section"""
        # Header
        header = tk.Frame(parent, bg="#9b59b6", height=40)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        tk.Label(
            header,
            text="Trend Analysis & Pattern Recognition",
            font=("Arial", 12, "bold"),
            fg="white",
            bg="#9b59b6"
        ).pack(pady=8)
        
        # Content
        self.trends_display = tk.Text(parent, height=20, wrap="word", font=("Arial", 10))
        self.trends_display.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Refresh button
        ttk.Button(
            parent,
            text="Analyze Trends",
            command=self._update_trends
        ).pack(pady=10)
        
    def _create_optimization_section(self, parent):
        """Create optimization section"""
        # Header
        header = tk.Frame(parent, bg="#16a085", height=40)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        tk.Label(
            header,
            text="Cost Optimization & Efficiency Analysis",
            font=("Arial", 12, "bold"),
            fg="white",
            bg="#16a085"
        ).pack(pady=8)
        
        # Content
        self.optimization_display = tk.Text(parent, height=20, wrap="word", font=("Arial", 10))
        self.optimization_display.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Refresh button
        ttk.Button(
            parent,
            text="Optimize Costs",
            command=self._update_optimization
        ).pack(pady=10)
        
    def _create_anomalies_section(self, parent):
        """Create anomalies section"""
        # Header
        header = tk.Frame(parent, bg="#c0392b", height=40)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        tk.Label(
            header,
            text="Anomaly Detection & Alert System",
            font=("Arial", 12, "bold"),
            fg="white",
            bg="#c0392b"
        ).pack(pady=8)
        
        # Content
        self.anomalies_display = tk.Text(parent, height=20, wrap="word", font=("Arial", 10))
        self.anomalies_display.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Refresh button
        ttk.Button(
            parent,
            text="Detect Anomalies",
            command=self._update_anomalies
        ).pack(pady=10)
        
    def _update_predictions(self):
        """Update predictions display"""
        self.predictions_display.delete(1.0, tk.END)
        
        if not self.pool_analytics:
            self.predictions_display.insert(tk.END, "ML Analytics Engine not available.\n")
            self.predictions_display.insert(tk.END, "Install required libraries: pip install numpy scikit-learn pandas scipy")
            return
            
        if len(self.chemical_readings) < 10:
            self.predictions_display.insert(tk.END, "Insufficient Data for Predictions\n\n")
            self.predictions_display.insert(tk.END, f"Current readings: {len(self.chemical_readings)}\n")
            self.predictions_display.insert(tk.END, "Minimum required: 10 readings\n\n")
            self.predictions_display.insert(tk.END, "Keep adding readings to enable predictive analytics!")
            return
            
        try:
            # Use historical data for predictions
            predictions = self.pool_analytics.predict_next_readings(self.chemical_readings)
            
            
            if predictions:
                self.predictions_display.insert(tk.END, "PREDICTED NEXT READINGS\n", "title")
                self.predictions_display.insert(tk.END, "=" * 50 + "\n\n")
                
                for param, pred_data in predictions.items():
                    param_name = param.replace('_', ' ').title()
                    self.predictions_display.insert(tk.END, f"{param_name}\n", "bold")
                    
                    # Handle both dict and float formats
                    if isinstance(pred_data, dict):
                        value = pred_data.get('value', 0)
                        lower = pred_data.get('lower_bound', value)
                        upper = pred_data.get('upper_bound', value)
                        confidence = pred_data.get('confidence', 0) * 100
                        method = pred_data.get('method', 'Statistical')
                        
                        self.predictions_display.insert(tk.END, f"   Predicted: {value:.2f}\n")
                        self.predictions_display.insert(tk.END, f"   Range: {lower:.2f} - {upper:.2f}\n")
                        self.predictions_display.insert(tk.END, f"   Confidence: {confidence:.0f}%\n")
                        self.predictions_display.insert(tk.END, f"   Method: {method}\n\n")
                    else:
                        # Fallback for simple float values
                        self.predictions_display.insert(tk.END, f"   Predicted: {pred_data:.2f}\n\n")
                    
                self.predictions_display.insert(tk.END, "\n" + "=" * 50 + "\n")
                self.predictions_display.insert(tk.END, "\nUse these predictions for proactive pool maintenance!")
            else:
                self.predictions_display.insert(tk.END, "Unable to generate predictions.\n")
                self.predictions_display.insert(tk.END, "More data needed for accurate forecasting.")
                
        except Exception as e:
            self.predictions_display.insert(tk.END, f"Error: {str(e)}")
            
        # Configure tags
        self.predictions_display.tag_config("title", font=("Arial", 12, "bold"), foreground="#27ae60")
        self.predictions_display.tag_config("bold", font=("Arial", 10, "bold"))
        
    def _update_insights(self):
        """Update insights display"""
        self.insights_display.delete(1.0, tk.END)
        
        if not self.pool_analytics:
            self.insights_display.insert(tk.END, "ML Analytics Engine not available.")
            return
            
        try:
            current = self._get_readings_from_form(show_warnings=False)
            if not current:
                self.insights_display.insert(tk.END, "No readings available for analysis.")
                return
                
            # Get historical data for insights
            historical = self.chemical_readings[-10:] if len(self.chemical_readings) >= 10 else self.chemical_readings
            insights = self.pool_analytics.get_insights(current, historical)
            
            if insights:
                self.insights_display.insert(tk.END, "AI-POWERED INSIGHTS\n", "title")
                self.insights_display.insert(tk.END, "=" * 50 + "\n\n")
                
                for i, insight in enumerate(insights, 1):
                    priority = insight.get('priority', 'low').upper()
                    self.insights_display.insert(tk.END, f"\n{i}. ", "bold")
                    self.insights_display.insert(tk.END, f"[{priority}] ", f"priority_{priority.lower()}")
                    self.insights_display.insert(tk.END, f"{insight['type'].upper()}\n", "type")
                    self.insights_display.insert(tk.END, f"   {insight['message']}\n")
                    self.insights_display.insert(tk.END, f"   Action: {insight['action']}\n")
            else:
                self.insights_display.insert(tk.END, "No critical insights at this time.\n")
                self.insights_display.insert(tk.END, "Your pool chemistry looks good!")
                
        except Exception as e:
            self.insights_display.insert(tk.END, f"Error: {str(e)}")
            
        # Configure tags
        self.insights_display.tag_config("title", font=("Arial", 12, "bold"), foreground="#e67e22")
        self.insights_display.tag_config("bold", font=("Arial", 10, "bold"))
        self.insights_display.tag_config("type", foreground="#3498db", font=("Arial", 10, "bold"))
        self.insights_display.tag_config("priority_high", foreground="#e74c3c", font=("Arial", 10, "bold"))
        self.insights_display.tag_config("priority_medium", foreground="#f39c12", font=("Arial", 10, "bold"))
        
    def _update_trends(self):
        """Update trends display"""
        self.trends_display.delete(1.0, tk.END)
        
        if not self.pool_analytics:
            self.trends_display.insert(tk.END, "ML Analytics Engine not available.")
            return
            
        if len(self.chemical_readings) < 7:
            self.trends_display.insert(tk.END, f"Insufficient data: {len(self.chemical_readings)} readings\n")
            self.trends_display.insert(tk.END, "Need at least 7 readings for trend analysis")
            return
            
        try:
            # Get historical data for trends
            historical = self.chemical_readings[-10:] if len(self.chemical_readings) >= 10 else self.chemical_readings
            trends = self.pool_analytics.analyze_trends(historical)
            
            if trends:
                self.trends_display.insert(tk.END, "TREND ANALYSIS\n", "title")
                self.trends_display.insert(tk.END, "=" * 50 + "\n\n")
                
                for param, trend_data in trends.items():
                    direction = trend_data['direction']
                    rate = trend_data['rate']
                    confidence = trend_data['confidence'] * 100
                    
                    arrow = "[UP]" if direction == "increasing" else "[DOWN]"
                    
                    self.trends_display.insert(tk.END, f"{arrow} {param.replace('_', ' ').title()}\n", "bold")
                    self.trends_display.insert(tk.END, f"   Direction: {direction.upper()}\n")
                    self.trends_display.insert(tk.END, f"   Rate: {rate:.4f} per reading\n")
                    self.trends_display.insert(tk.END, f"   Confidence: {confidence:.1f}%\n\n")
            else:
                self.trends_display.insert(tk.END, "No significant trends detected.\n")
                self.trends_display.insert(tk.END, "Pool chemistry is stable.")
                
        except Exception as e:
            self.trends_display.insert(tk.END, f"Error: {str(e)}")
            
        # Configure tags
        self.trends_display.tag_config("title", font=("Arial", 12, "bold"), foreground="#9b59b6")
        self.trends_display.tag_config("bold", font=("Arial", 10, "bold"))
        
    def _update_optimization(self):
        """Update optimization display"""
        self.optimization_display.delete(1.0, tk.END)
        
        if not self.pool_analytics:
            self.optimization_display.insert(tk.END, "ML Analytics Engine not available.")
            return
            
        try:
            current = self._get_readings_from_form(show_warnings=False)
            if not current:
                self.optimization_display.insert(tk.END, "No readings available.")
                return
                
            # Get adjustments first
            adjustments = self._calculate_adjustments()
            
            if adjustments:
                   # Convert adjustments dict to list format
                   adjustments_list = []
                   for param, adj_data in adjustments.items():
                       if isinstance(adj_data, dict):
                           adj_dict = adj_data.copy()
                           adj_dict["parameter"] = param
                           if "chemical" not in adj_dict:
                               adj_dict["chemical"] = param
                           adjustments_list.append(adj_dict)
                   
                   optimization = self.pool_analytics.optimize_chemical_usage(current, adjustments_list)
                
                   if optimization:
                       self.optimization_display.insert(tk.END, "COST OPTIMIZATION ANALYSIS\n", "title")
                       self.optimization_display.insert(tk.END, "=" * 50 + "\n\n")
                    
                       self.optimization_display.insert(tk.END, f"Estimated Cost: ${optimization['total_cost']:.2f}\n", "cost")
                       self.optimization_display.insert(tk.END, f"Savings Potential: ${optimization['savings_potential']:.2f}\n\n", "savings")
                    
                       self.optimization_display.insert(tk.END, "Recommendations:\n", "bold")
                       for rec in optimization['recommendations']:
                           if isinstance(rec, dict):
                               # Format dictionary recommendations professionally
                               category = rec.get('category', 'General')
                               suggestion = rec.get('suggestion', '')
                               savings = rec.get('potential_savings', 0)
                               self.optimization_display.insert(tk.END, f"   • {category}: ", "bold")
                               self.optimization_display.insert(tk.END, f"{suggestion}")
                               if savings > 0:
                                   self.optimization_display.insert(tk.END, f" (Save: ${savings:.2f})", "savings")
                               self.optimization_display.insert(tk.END, "\n")
                           else:
                               # Handle string recommendations
                               self.optimization_display.insert(tk.END, f"   • {rec}\n")
                   else:
                       self.optimization_display.insert(tk.END, "No adjustments needed.\n")
                       self.optimization_display.insert(tk.END, "Pool chemistry is balanced!")
                
        except Exception as e:
            self.optimization_display.insert(tk.END, f"Error: {str(e)}")
            
        # Configure tags
        self.optimization_display.tag_config("title", font=("Arial", 12, "bold"), foreground="#16a085")
        self.optimization_display.tag_config("bold", font=("Arial", 10, "bold"))
        self.optimization_display.tag_config("cost", font=("Arial", 11, "bold"), foreground="#e74c3c")
        self.optimization_display.tag_config("savings", font=("Arial", 11, "bold"), foreground="#27ae60")
        
    def _update_anomalies(self):
        """Update anomalies display"""
        self.anomalies_display.delete(1.0, tk.END)
        
        if not self.pool_analytics:
            self.anomalies_display.insert(tk.END, "ML Analytics Engine not available.")
            return
            
        if len(self.chemical_readings) < 10:
            self.anomalies_display.insert(tk.END, f"Insufficient data: {len(self.chemical_readings)} readings\n")
            self.anomalies_display.insert(tk.END, "Need at least 10 readings for anomaly detection")
            return
            
        try:
            current = self._get_readings_from_form(show_warnings=False)
            if not current:
                self.anomalies_display.insert(tk.END, "No readings available.")
                return
                
            # Get historical data for anomaly detection
            historical = self.chemical_readings[-10:] if len(self.chemical_readings) >= 10 else self.chemical_readings
            anomalies = self.pool_analytics.detect_anomalies(current, historical)
            
            if anomalies:
                self.anomalies_display.insert(tk.END, "ANOMALY DETECTION RESULTS\n", "title")
                self.anomalies_display.insert(tk.END, "=" * 50 + "\n\n")
                
                for anomaly in anomalies:
                    severity = anomaly['severity'].upper()
                    self.anomalies_display.insert(tk.END, f"[{severity}] ", f"severity_{severity.lower()}")
                    self.anomalies_display.insert(tk.END, f"{anomaly['parameter'].replace('_', ' ').title()}\n", "bold")
                    self.anomalies_display.insert(tk.END, f"   Current Value: {anomaly['current']:.2f}\n")
                    self.anomalies_display.insert(tk.END, f"   Expected Value: {anomaly['expected']:.2f}\n")
                    self.anomalies_display.insert(tk.END, f"   Deviation: {anomaly['deviation']:.2f} (Z-score: {anomaly['z_score']:.2f})\n")
                    self.anomalies_display.insert(tk.END, f"   This reading is unusual - verify accuracy\n\n")
            else:
                self.anomalies_display.insert(tk.END, "NO ANOMALIES DETECTED\n", "title")
                self.anomalies_display.insert(tk.END, "\nAll readings are within expected ranges.")
                
        except Exception as e:
            self.anomalies_display.insert(tk.END, f"Error: {str(e)}")
            
        # Configure tags
        self.anomalies_display.tag_config("title", font=("Arial", 12, "bold"), foreground="#c0392b")
        self.anomalies_display.tag_config("bold", font=("Arial", 10, "bold"))
        self.anomalies_display.tag_config("severity_high", foreground="#e74c3c", font=("Arial", 10, "bold"))
        self.anomalies_display.tag_config("severity_medium", foreground="#f39c12", font=("Arial", 10, "bold"))


    def _create_weather_impacts_tab(self):
        """Create the Weather Impacts tab content"""
        # Main container
        main_container = ttk.Frame(self.weather_impacts_tab)
        main_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Title
        title_frame = tk.Frame(main_container, bg="#f39c12", height=50)
        title_frame.pack(fill="x", pady=(0, 10))
        title_frame.pack_propagate(False)
        
        tk.Label(
            title_frame,
            text="Weather Impact Analysis & Notifications",
            font=("Arial", 16, "bold"),
            fg="white",
            bg="#f39c12"
        ).pack(pady=10)
        
        # Info section
        info_frame = tk.Frame(main_container, bg="#e8f5e9", bd=2, relief="solid")
        info_frame.pack(fill="x", pady=(0, 10))
        
        tk.Label(
            info_frame,
            text="Real-time analysis of how weather conditions affect your pool chemistry",
            font=("Arial", 11),
            bg="#e8f5e9",
            fg="#155724"
        ).pack(pady=10)
        
        # Refresh button
        button_frame = ttk.Frame(main_container)
        button_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Button(
            button_frame,
            text="Refresh Weather Impacts",
            command=self._refresh_weather_impacts
        ).pack(side="left", padx=5)
        
        ttk.Button(
            button_frame,
            text="View Detailed Forecast",
            command=lambda: self.notebook.select(0)  # Go to dashboard
        ).pack(side="left", padx=5)
        
        # Impacts display area
        self.weather_impacts_display = tk.Text(
            main_container,
            wrap="word",
            font=("Arial", 10),
            height=25
        )
        self.weather_impacts_display.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(
            main_container,
            orient="vertical",
            command=self.weather_impacts_display.yview
        )
        scrollbar.pack(side="right", fill="y")
        self.weather_impacts_display.config(yscrollcommand=scrollbar.set)
        
        # Configure text tags
        self.weather_impacts_display.tag_config("title", font=("Arial", 14, "bold"), foreground="#2c3e50")
        self.weather_impacts_display.tag_config("high", font=("Arial", 11, "bold"), foreground="#e74c3c")
        self.weather_impacts_display.tag_config("medium", font=("Arial", 11, "bold"), foreground="#f39c12")
        self.weather_impacts_display.tag_config("low", font=("Arial", 11, "bold"), foreground="#27ae60")
        self.weather_impacts_display.tag_config("icon", font=("Arial", 16))
        self.weather_impacts_display.tag_config("section", font=("Arial", 12, "bold"), foreground="#3498db")
        self.weather_impacts_display.tag_config("impact", font=("Arial", 10), foreground="#7f8c8d")
        
        # Initial load
        self._refresh_weather_impacts()
        
    def _refresh_weather_impacts(self):
        """Refresh weather impacts display"""
        self.weather_impacts_display.delete(1.0, tk.END)
        
        if not self.weather_impact_analyzer:
            self.weather_impacts_display.insert(tk.END, "Weather Impact Analyzer not available.\n")
            return
            
        try:
            # Get current readings
            current_readings = self._get_readings_from_form(show_warnings=False)
            
            # Analyze weather impacts
            impacts = self.weather_impact_analyzer.analyze_weather_impact(
                self.weather_data if hasattr(self, 'weather_data') else None,
                current_readings
            )
            
            # Check if there are any actual impacts (not just empty dict)
            has_impacts = False
            if impacts:
                for category, data in impacts.items():
                    if category != "alerts" and isinstance(data, dict) and data:
                        has_impacts = True
                        break
            
            if not has_impacts:
                # No impacts - show simple message
                self.weather_impacts_display.insert(tk.END, "WEATHER CONDITIONS\n\n", "title")
                self.weather_impacts_display.insert(tk.END, "No significant weather impacts detected.\n\n")
                self.weather_impacts_display.insert(tk.END, "Current weather conditions are favorable for pool maintenance.\n")
                self.weather_impacts_display.insert(tk.END, "Continue with normal maintenance schedule.\n\n")
                self.weather_impacts_display.insert(tk.END, "TIP: This tab will show alerts when weather conditions may affect your pool chemistry.")
                return
                
            # Display impacts
            self.weather_impacts_display.insert(tk.END, "WEATHER IMPACT ANALYSIS\n", "title")
            self.weather_impacts_display.insert(tk.END, "=" * 70 + "\n\n")
            
            # Get recommendations
            recommendations = self.weather_impact_analyzer.get_weather_recommendations(impacts)
            
            if recommendations:
                self.weather_impacts_display.insert(tk.END, "? PRIORITY ALERTS\n", "section")
                self.weather_impacts_display.insert(tk.END, "-" * 70 + "\n")
                
                for rec in recommendations:
                    self.weather_impacts_display.insert(tk.END, f"* {rec}\n")

                self.weather_impacts_display.insert(tk.END, "\n" + "=" * 70 + "\n\n")
            
            # Display individual impacts
            self.weather_impacts_display.insert(tk.END, "DETAILED IMPACT ANALYSIS\n", "section")
            self.weather_impacts_display.insert(tk.END, "-" * 70 + "\n\n")
            
            impact_count = 0
            for category, data in impacts.items():
                if category == "alerts" or not isinstance(data, dict):
                    continue
                
                impact_count += 1
                
                # Title
                self.weather_impacts_display.insert(tk.END, f"{category.replace('_', ' ').title()}\n", "section")
                
                # Level
                if "level" in data:
                    level_tag = "high" if data["level"] in ["high", "significant"] else "medium"
                    self.weather_impacts_display.insert(tk.END, f"Level: {data['level'].upper()}\n", level_tag)
                
                # Effect
                if "effect" in data:
                    self.weather_impacts_display.insert(tk.END, f"\nEffect: {data['effect']}\n")
                
                # Action
                if "action" in data:
                    self.weather_impacts_display.insert(tk.END, f"\nAction: {data['action']}\n")
                
                self.weather_impacts_display.insert(tk.END, "\n" + "-" * 70 + "\n\n")
                
            # Footer
            self.weather_impacts_display.insert(tk.END, "\n" + "=" * 70 + "\n")
            self.weather_impacts_display.insert(tk.END, "\nTIP: Check this tab after weather changes for updated recommendations\n")
            
            # Update status
            self.status_var.set(f"Weather impacts analyzed - {impact_count} factors detected")
            
        except Exception as e:
            logger.error(f"Error refreshing weather impacts: {e}")
            self.weather_impacts_display.insert(tk.END, f"Error analyzing weather impacts: {str(e)}")

    def _create_arduino_setup_tab(self):
        """Create the Arduino Setup tab with sensor configuration and diagnostics"""
        # Main container with scrollbar
        main_container = ttk.Frame(self.arduino_setup_tab)
        main_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Canvas for scrolling
        canvas = tk.Canvas(main_container, bg="#f0f4f8")
        scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Title
        title_frame = tk.Frame(scrollable_frame, bg="#2c3e50", height=60)
        title_frame.pack(fill="x", pady=(0, 20))
        title_frame.pack_propagate(False)
        
        tk.Label(
            title_frame,
            text="Arduino Sensor Setup & Configuration",
            font=("Arial", 18, "bold"),
            fg="white",
            bg="#2c3e50"
        ).pack(pady=15)
        
        # Connection Status Section
        self._create_connection_status_section(scrollable_frame)
        
        # Sensor Configuration Section
        self._create_sensor_config_section(scrollable_frame)
        
        # Real-time Readings Section
        self._create_realtime_readings_section(scrollable_frame)
        
        # Wiring Guide Section
        self._create_wiring_guide_section(scrollable_frame)
        
        # Calibration Section
        self._create_calibration_section(scrollable_frame)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Start periodic updates
        self._update_arduino_status()
    
    def _create_connection_status_section(self, parent):
        """Create connection status section"""
        frame = tk.LabelFrame(
            parent,
            text="Connection Status",
            font=("Arial", 12, "bold"),
            bg="white",
            fg="#2c3e50",
            padx=15,
            pady=15
        )
        frame.pack(fill="x", padx=10, pady=10)
        
        # Status display
        status_container = tk.Frame(frame, bg="white")
        status_container.pack(fill="x", pady=10)
        
        tk.Label(
            status_container,
            text="Status:",
            font=("Arial", 11, "bold"),
            bg="white"
        ).pack(side="left", padx=5)
        
        self.arduino_status_label = tk.Label(
            status_container,
            text="Checking...",
            font=("Arial", 11),
            bg="white"
        )
        self.arduino_status_label.pack(side="left", padx=5)
        
        # Port display
        port_container = tk.Frame(frame, bg="white")
        port_container.pack(fill="x", pady=5)
        
        tk.Label(
            port_container,
            text="Port:",
            font=("Arial", 10),
            bg="white"
        ).pack(side="left", padx=5)
        
        self.arduino_port_label = tk.Label(
            port_container,
            text="Not connected",
            font=("Arial", 10),
            bg="white",
            fg="#7f8c8d"
        )
        self.arduino_port_label.pack(side="left", padx=5)
        
        # Statistics
        stats_container = tk.Frame(frame, bg="white")
        stats_container.pack(fill="x", pady=10)
        
        self.arduino_stats_label = tk.Label(
            stats_container,
            text="Total Readings: 0 | Success Rate: 0%",
            font=("Arial", 9),
            bg="white",
            fg="#7f8c8d"
        )
        self.arduino_stats_label.pack()
        
        # Buttons
        button_frame = tk.Frame(frame, bg="white")
        button_frame.pack(fill="x", pady=10)
        
        ttk.Button(
            button_frame,
            text="Reconnect",
            command=self._reconnect_arduino
        ).pack(side="left", padx=5)
        
        ttk.Button(
            button_frame,
            text="Scan Ports",
            command=self._scan_arduino_ports
        ).pack(side="left", padx=5)
        
        ttk.Button(
            button_frame,
            text="View Logs",
            command=self._view_arduino_logs
        ).pack(side="left", padx=5)
    
    def _create_sensor_config_section(self, parent):
        """Create sensor configuration section"""
        frame = tk.LabelFrame(
            parent,
            text="Sensor Configuration",
            font=("Arial", 12, "bold"),
            bg="white",
            fg="#2c3e50",
            padx=15,
            pady=15
        )
        frame.pack(fill="x", padx=10, pady=10)
        
        # Sensor list
        sensors = [
            ("pH Sensor", "Analog A0", "pH probe with BNC connector"),
            ("Free Chlorine", "Analog A1", "ORP sensor or colorimetric"),
            ("Total Chlorine", "Analog A2", "DPD colorimetric sensor"),
            ("Temperature", "Digital Pin 2", "DS18B20 waterproof sensor"),
            ("Alkalinity", "Analog A3", "Titration or colorimetric"),
            ("Calcium Hardness", "Analog A4", "Colorimetric sensor"),
            ("Cyanuric Acid", "Analog A5", "Turbidity sensor"),
               ("Bromine", "Analog A6", "DPD colorimetric sensor"),
               ("Salt/TDS", "Analog A7", "Conductivity/TDS sensor")
        ]
        
        for sensor_name, pin, description in sensors:
            sensor_frame = tk.Frame(frame, bg="white", relief="solid", borderwidth=1)
            sensor_frame.pack(fill="x", pady=5)
            
            # Sensor name
            tk.Label(
                sensor_frame,
                text=f"{sensor_name}",
                font=("Arial", 10, "bold"),
                bg="white",
                anchor="w"
            ).pack(fill="x", padx=10, pady=(5, 0))
            
            # Pin and description
            info_frame = tk.Frame(sensor_frame, bg="white")
            info_frame.pack(fill="x", padx=10, pady=(0, 5))
            
            tk.Label(
                info_frame,
                text=f"Pin: {pin}",
                font=("Arial", 9),
                bg="white",
                fg="#3498db"
            ).pack(side="left", padx=(0, 10))
            
            tk.Label(
                info_frame,
                text=description,
                font=("Arial", 9),
                bg="white",
                fg="#7f8c8d"
            ).pack(side="left")
    
    def _create_realtime_readings_section(self, parent):
        """Create real-time readings section"""
        frame = tk.LabelFrame(
            parent,
            text="Real-Time Sensor Readings",
            font=("Arial", 12, "bold"),
            bg="white",
            fg="#2c3e50",
            padx=15,
            pady=15
        )
        frame.pack(fill="x", padx=10, pady=10)
        
        # Readings display
        self.arduino_readings_text = tk.Text(
            frame,
            height=10,
            font=("Courier", 10),
            bg="#f8f9fa",
            relief="solid",
            borderwidth=1
        )
        self.arduino_readings_text.pack(fill="both", expand=True, pady=5)
        
        # Configure tags
        self.arduino_readings_text.tag_config("header", font=("Courier", 10, "bold"), foreground="#2c3e50")
        self.arduino_readings_text.tag_config("value", font=("Courier", 10), foreground="#27ae60")
        self.arduino_readings_text.tag_config("timestamp", font=("Courier", 9), foreground="#7f8c8d")
        
        # Initial message
        self.arduino_readings_text.insert("1.0", "Waiting for sensor data...\n\n", "header")
        self.arduino_readings_text.insert("end", "Connect Arduino and sensors to see real-time readings.", "timestamp")
        self.arduino_readings_text.config(state="disabled")
        
        # Auto-populate button
        button_frame = tk.Frame(frame, bg="white")
        button_frame.pack(fill="x", pady=10)
        
        ttk.Button(
            button_frame,
            text="Auto-Populate Water Testing Form",
            command=self._auto_populate_from_arduino
        ).pack(side="left", padx=5)
        
        ttk.Button(
            button_frame,
            text="Save Current Readings",
            command=self._save_arduino_readings
        ).pack(side="left", padx=5)
    
    def _create_wiring_guide_section(self, parent):
        """Create wiring guide section"""
        frame = tk.LabelFrame(
            parent,
            text="Wiring Guide",
            font=("Arial", 12, "bold"),
            bg="white",
            fg="#2c3e50",
            padx=15,
            pady=15
        )
        frame.pack(fill="x", padx=10, pady=10)
        
        guide_text = """[PIN] BASIC WIRING SETUP:

1. pH Sensor (Analog A0):
   * Red wire -> 5V
   * Black wire -> GND
   * Blue wire -> A0

2. Temperature Sensor DS18B20 (Digital Pin 2):
   * Red wire -> 5V
   * Black wire -> GND
   * Yellow wire -> Pin 2
   * 4.7k? resistor between 5V and Pin 2

3. ORP/Chlorine Sensor (Analog A1):
   * Red wire -> 5V
   * Black wire -> GND
   * Signal wire -> A1

4. Additional Analog Sensors (A2-A5):
   * Follow same pattern as pH sensor
   * Check sensor datasheet for specific wiring

IMPORTANT SAFETY NOTES:
   * Never connect sensors while Arduino is powered
   * Use waterproof sensors rated for pool use
   * Keep electronics away from water
   * Use proper enclosures for outdoor installation
   * Ground all equipment properly

TIPS:
   * Use shielded cables for analog sensors
   * Keep sensor cables away from power lines
   * Calibrate sensors regularly
   * Test in controlled environment first"""
        
        text_widget = tk.Text(
            frame,
            height=25,
            font=("Courier", 9),
            bg="#f8f9fa",
            relief="solid",
            borderwidth=1,
            wrap="word"
        )
        text_widget.pack(fill="both", expand=True)
        text_widget.insert("1.0", guide_text)
        text_widget.config(state="disabled")
    
    def _create_calibration_section(self, parent):
        """Create calibration section"""
        frame = tk.LabelFrame(
            parent,
            text="Sensor Calibration",
            font=("Arial", 12, "bold"),
            bg="white",
            fg="#2c3e50",
            padx=15,
            pady=15
        )
        frame.pack(fill="x", padx=10, pady=10)
        
        calibration_text = """CALIBRATION PROCEDURE:

1. pH Sensor Calibration:
   * Use pH 4.0, 7.0, and 10.0 buffer solutions
   * Rinse probe between solutions
   * Wait for stable reading (2-3 minutes)
   * Record values and adjust in Arduino code

2. Temperature Sensor:
   * Compare with accurate thermometer
   * Test at multiple temperatures
   * Adjust offset if needed

3. ORP/Chlorine Sensor:
   * Use standard chlorine solution (1.0 ppm)
   * Allow sensor to stabilize
   * Calibrate against test strip or DPD test

4. Other Sensors:
   * Follow manufacturer calibration procedure
   * Use known standard solutions
   * Document calibration dates

? CALIBRATION SCHEDULE:
   * pH Sensor: Weekly
   * Temperature: Monthly
   * Chlorine/ORP: Weekly
   * Other sensors: As per manufacturer specs

Keep calibration log in Arduino comments!"""
        
        text_widget = tk.Text(
            frame,
            height=20,
            font=("Courier", 9),
            bg="#f8f9fa",
            relief="solid",
            borderwidth=1,
            wrap="word"
        )
        text_widget.pack(fill="both", expand=True)
        text_widget.insert("1.0", calibration_text)
        text_widget.config(state="disabled")
        
        # Calibration buttons
        button_frame = tk.Frame(frame, bg="white")
        button_frame.pack(fill="x", pady=10)
        
        ttk.Button(
            button_frame,
            text="Start Calibration Wizard",
            command=self._start_calibration_wizard
        ).pack(side="left", padx=5)
        
        ttk.Button(
            button_frame,
            text="View Calibration Log",
            command=self._view_calibration_log
        ).pack(side="left", padx=5)
    
    def _update_arduino_status(self):
        """Update Arduino status display"""
        try:
            if hasattr(self, 'arduino') and self.arduino:
                if hasattr(self.arduino, 'is_connected') and self.arduino.is_connected:
                    self.arduino_status_label.config(
                        text="Connected",
                        fg="#27ae60"
                    )
                    
                    if hasattr(self.arduino, 'port'):
                        self.arduino_port_label.config(
                            text=self.arduino.port,
                            fg="#2c3e50"
                        )
                    
                    # Update statistics
                    if hasattr(self.arduino, 'get_status'):
                        status = self.arduino.get_status()
                        total = status.get('total_readings', 0)
                        success = status.get('successful_readings', 0)
                        rate = (success / total * 100) if total > 0 else 0
                        
                        self.arduino_stats_label.config(
                            text=f"Total Readings: {total} | Success Rate: {rate:.1f}%"
                        )
                else:
                    self.arduino_status_label.config(
                        text="Disconnected",
                        fg="#e74c3c"
                    )
                    self.arduino_port_label.config(
                        text="Not connected",
                        fg="#7f8c8d"
                    )
            else:
                self.arduino_status_label.config(
                    text="Not initialized",
                    fg="#95a5a6"
                )
        except Exception as e:
            logger.error(f"Error updating Arduino status: {e}")
        
        # Schedule next update
        if hasattr(self, 'arduino_setup_tab'):
            self.after(2000, self._update_arduino_status)
    
    def _reconnect_arduino(self):
        """Reconnect to Arduino"""
        try:
            self._setup_arduino_communication()
            messagebox.showinfo("Arduino", "Reconnection attempted. Check status above.")
        except Exception as e:
            messagebox.showerror("Arduino", f"Reconnection failed: {e}")
    
    def _scan_arduino_ports(self):
        """Scan for available COM ports"""
        try:
            import serial.tools.list_ports
            ports = list(serial.tools.list_ports.comports())
            
            if not ports:
                messagebox.showinfo("Port Scan", "No COM ports found.\n\nMake sure Arduino is connected via USB.")
                return
            
            port_list = "\n".join([f"* {p.device}: {p.description}" for p in ports])
            messagebox.showinfo("Available Ports", f"Found {len(ports)} port(s):\n\n{port_list}")
        except ImportError:
            messagebox.showerror("Error", "pyserial not installed.\n\nInstall with: pip install pyserial")
        except Exception as e:
            messagebox.showerror("Error", f"Port scan failed: {e}")
    
    def _view_arduino_logs(self):
        """View Arduino communication logs"""
        try:
            log_locations = [
                "logs/pool_app.log",
                "pool_app.log",
                "logs/app.log",
                "app.log",
                os.path.join(os.path.dirname(__file__), "logs", "pool_app.log"),
                os.path.join(os.path.dirname(__file__), "logs", "app.log")
            ]
            log_file = next((loc for loc in log_locations if os.path.exists(loc)), None)
            if log_file:
                # Read last 100 lines
                with open(log_file, 'r') as f:
                    lines = f.readlines()
                    arduino_lines = [line for line in lines[-100:] if 'arduino' in line.lower()]
                    
                if arduino_lines:
                    log_text = "".join(arduino_lines[-20:])  # Last 20 Arduino-related lines
                    
                    # Create log window
                    log_window = tk.Toplevel(self)
                    log_window.title("Arduino Logs")
                    log_window.geometry("800x400")
                    
                    text_widget = tk.Text(log_window, wrap="word", font=("Courier", 9))
                    text_widget.pack(fill="both", expand=True, padx=10, pady=10)
                    text_widget.insert("1.0", log_text)
                    text_widget.config(state="disabled")
                    
                    ttk.Button(log_window, text="Close", command=log_window.destroy).pack(pady=10)
                else:
                    messagebox.showinfo("Logs", "No Arduino-related log entries found.")
            else:
                messagebox.showinfo("Logs", "Log file not found.")
        except Exception as e:
            messagebox.showerror("Error", f"Could not read logs: {e}")
    
    def _auto_populate_from_arduino(self):
        """Auto-populate water testing form from Arduino readings"""
        try:
            if not (hasattr(self, 'arduino') and self.arduino and self.arduino.is_connected):
                messagebox.showwarning("Arduino", "Arduino not connected.\n\nConnect Arduino first.")
                return
            
            # Get current readings
            if hasattr(self.arduino, 'last_reading') and self.arduino.last_reading:
                # Parse the data
                readings = {}
                for item in self.arduino.last_reading.split(','):
                    if ':' in item:
                        key, value = item.split(':', 1)
                        try:
                            readings[key.strip().upper()] = float(value.strip())
                        except ValueError:
                            pass
                
                if readings:
                    # Populate form fields
                    if 'PH' in readings and hasattr(self, 'ph_entry'):
                        self.ph_entry.delete(0, tk.END)
                        self.ph_entry.insert(0, str(readings['PH']))
                    
                    if 'CL' in readings and hasattr(self, 'free_chlorine_entry'):
                        self.free_chlorine_entry.delete(0, tk.END)
                        self.free_chlorine_entry.insert(0, str(readings['CL']))
                    
                    if 'TCL' in readings and hasattr(self, 'total_chlorine_entry'):
                        self.total_chlorine_entry.delete(0, tk.END)
                        self.total_chlorine_entry.insert(0, str(readings['TCL']))
                    
                    if 'ALK' in readings and hasattr(self, 'alkalinity_entry'):
                        self.alkalinity_entry.delete(0, tk.END)
                        self.alkalinity_entry.insert(0, str(readings['ALK']))
                    
                    if 'HARD' in readings and hasattr(self, 'calcium_hardness_entry'):
                        self.calcium_hardness_entry.delete(0, tk.END)
                        self.calcium_hardness_entry.insert(0, str(readings['HARD']))
                    
                    if 'CYA' in readings and hasattr(self, 'cyanuric_acid_entry'):
                        self.cyanuric_acid_entry.delete(0, tk.END)
                        self.cyanuric_acid_entry.insert(0, str(readings['CYA']))
                    
                    # Switch to Water Testing tab
                    self.notebook.select(1)
                    
                    messagebox.showinfo("Success", "Arduino readings populated!\n\nReview values in Water Testing tab.")
                else:
                    messagebox.showwarning("No Data", "No valid readings received from Arduino.")
            else:
                messagebox.showwarning("No Data", "No recent readings from Arduino.\n\nWait for data or check connection.")
        except Exception as e:
            logger.error(f"Error auto-populating from Arduino: {e}")
            messagebox.showerror("Error", f"Failed to populate form: {e}")
    
    def _save_arduino_readings(self):
        """Save current Arduino readings to history"""
        try:
            if not (hasattr(self, 'arduino') and self.arduino and self.arduino.is_connected):
                messagebox.showwarning("Arduino", "Arduino not connected.")
                return
            
            # Auto-populate and save
            self._auto_populate_from_arduino()
            self._save_readings()
            
            messagebox.showinfo("Saved", "Arduino readings saved to history!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save readings: {e}")
    
    def _start_calibration_wizard(self):
        """Start sensor calibration wizard"""
        messagebox.showinfo(
            "Calibration Wizard",
            "Calibration wizard coming soon!\n\n" +
            "For now, calibrate sensors manually:\n" +
            "1. Use buffer solutions\n" +
            "2. Adjust values in Arduino code\n" +
            "3. Upload updated code to Arduino"
        )
    
    def _view_calibration_log(self):
        """View calibration log"""
        dialog = tk.Toplevel(self)
        dialog.title("Calibration Log")
        dialog.geometry("400x250")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        main_frame = tk.Frame(dialog, bg="white")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        title_frame = tk.Frame(main_frame, bg="white")
        title_frame.pack(fill="x", pady=(0, 15))
        icon_canvas = tk.Canvas(title_frame, width=50, height=50, bg="white", highlightthickness=0)
        icon_canvas.pack(side="left", padx=(0, 15))
        icon_canvas.create_oval(5, 5, 45, 45, fill="#2196F3", outline="")
        icon_canvas.create_text(25, 25, text="i", font=("Arial", 24, "bold"), fill="white")
        title_label = tk.Label(title_frame, text="Calibration logging coming soon!", font=("Arial", 12, "bold"), bg="white", fg="#333333")
        title_label.pack(side="left", anchor="w")
        message_frame = tk.Frame(main_frame, bg="white")
        message_frame.pack(fill="both", expand=True, pady=10)
        message_text = "For now, keep calibration notes in:\n* Arduino code comments\n* Separate calibration notebook\n* Date and values for each calibration"
        message_label = tk.Label(message_frame, text=message_text, font=("Arial", 10), bg="white", fg="#666666", justify="left", anchor="w")
        message_label.pack(fill="both", expand=True)
        button_frame = tk.Frame(main_frame, bg="white")
        button_frame.pack(fill="x", pady=(15, 0))
        ok_button = tk.Button(button_frame, text="OK", command=dialog.destroy, width=10, bg="#f0f0f0", relief="solid", borderwidth=1, font=("Arial", 10))
        ok_button.pack(side="right")

    def _create_pool_health_scoreboard(self):
        """Create the Pool Health Scoreboard in the middle section"""
        # Clear any existing widgets
        for widget in self.health_score_frame.winfo_children():
            widget.destroy()
        
        # Title
        title_label = tk.Label(
            self.health_score_frame,
            text="Pool Health Status",
            font=("Arial", 14, "bold"),
            bg="white",
            fg="#2c3e50"
        )
        title_label.pack(pady=(10, 5))
        
        # Canvas for circular gauge
        self.health_canvas = tk.Canvas(
            self.health_score_frame,
            width=280,
            height=280,
            bg="white",
            highlightthickness=0
        )
        self.health_canvas.pack(pady=10)
        
        # Status text
        self.health_status_label = tk.Label(
            self.health_score_frame,
            text="Water Quality: Not Tested",
            font=("Arial", 12, "bold"),
            bg="white",
            fg="#95a5a6"
        )
        self.health_status_label.pack(pady=(5, 10))
        
        # Draw initial empty gauge
        self._draw_water_testing_gauge(0, "#95a5a6")
    
    def _calculate_pool_health_score(self, readings):
        """Calculate overall pool health score 0-100 (STRICT - matches safety alerts)"""
        if not readings:
            return 0
        
        scores = []
        
        try:
            # pH score (ideal 7.2-7.6) - STRICT SCORING
            ph = float(readings.get('ph', 0))
            if ph > 0:
                if ph < 6.8 or ph > 8.2:
                    scores.append(0)    # CRITICAL - DO NOT SWIM
                elif 6.8 <= ph < 7.0 or 8.0 < ph <= 8.2:
                    scores.append(30)   # WARNING - needs attention
                elif 7.0 <= ph < 7.2 or 7.6 < ph <= 8.0:
                    scores.append(70)   # ACCEPTABLE
                elif 7.2 <= ph <= 7.6:
                    scores.append(100)  # IDEAL
            
            # Free Chlorine score (ideal 1-3 ppm) - STRICT SCORING
            cl = float(readings.get('free_chlorine', 0))
            if cl > 0:
                if cl < 0.5 or cl > 5.0:
                    scores.append(0)    # CRITICAL - DO NOT SWIM
                elif 0.5 <= cl < 1.0 or 4.0 < cl <= 5.0:
                    scores.append(30)   # WARNING - needs attention
                elif 1.0 <= cl <= 3.0:
                    scores.append(100)  # IDEAL
                elif 3.0 < cl <= 4.0:
                    scores.append(70)   # ACCEPTABLE
            
            # Total Chlorine score (should be close to free chlorine)
            tcl = float(readings.get('total_chlorine', 0))
            if tcl > 0 and cl > 0:
                diff = abs(tcl - cl)
                if diff <= 0.2:
                    scores.append(100)
                elif diff <= 0.5:
                    scores.append(85)
                elif diff <= 1.0:
                    scores.append(70)
                else:
                    scores.append(50)
            
            # Alkalinity score (ideal 80-120 ppm)
            alk = float(readings.get('alkalinity', 0))
            if alk > 0:
                if 80 <= alk <= 120:
                    scores.append(100)
                elif 60 <= alk <= 150:
                    scores.append(85)
                elif 40 <= alk <= 180:
                    scores.append(70)
                else:
                    scores.append(50)
            
            # Calcium Hardness score (ideal 200-400 ppm)
            hard = float(readings.get('calcium_hardness', 0))
            if hard > 0:
                if 200 <= hard <= 400:
                    scores.append(100)
                elif 150 <= hard <= 500:
                    scores.append(85)
                elif 100 <= hard <= 600:
                    scores.append(70)
                else:
                    scores.append(50)
            
            # Cyanuric Acid score (ideal 30-50 ppm) - STRICT SCORING
            cya = float(readings.get('cyanuric_acid', 0))
            if cya > 0:
                if cya > 100:
                    scores.append(0)    # CRITICAL - DO NOT SWIM
                elif 80 < cya <= 100:
                    scores.append(30)   # WARNING
                elif 30 <= cya <= 50:
                    scores.append(100)  # IDEAL
                elif 20 <= cya < 30 or 50 < cya <= 80:
                    scores.append(70)   # ACCEPTABLE
                else:
                    scores.append(50)
            
            # Temperature score (ideal 78-82F) - STRICT SCORING
            temp = float(readings.get('temperature', 0))
            if temp > 0:
                if temp > 104:
                    scores.append(0)    # CRITICAL - DO NOT SWIM
                elif 100 < temp <= 104:
                    scores.append(30)   # WARNING - too hot
                elif 78 <= temp <= 82:
                    scores.append(100)  # IDEAL
                elif 75 <= temp < 78 or 82 < temp <= 90:
                    scores.append(85)   # GOOD
                elif 70 <= temp < 75 or 90 < temp <= 100:
                    scores.append(70)   # ACCEPTABLE
                else:
                    scores.append(50)
            
            # ORP score (ideal 700-750 mV) - NEW ADDITION
            orp = float(readings.get('orp', 0))
            if orp > 0:
                if orp < 650 or orp > 800:
                    scores.append(0)    # CRITICAL - DO NOT SWIM
                elif 650 <= orp < 700 or 750 < orp <= 800:
                    scores.append(70)   # ACCEPTABLE
                elif 700 <= orp <= 750:
                    scores.append(100)  # IDEAL
            
            # Bromine score (ideal 2-4 ppm) if used instead of chlorine
            br = float(readings.get('bromine', 0))
            if br > 0:
                if br < 1.0 or br > 6.0:
                    scores.append(0)    # CRITICAL
                elif 1.0 <= br < 2.0 or 4.0 < br <= 6.0:
                    scores.append(50)   # WARNING
                elif 2.0 <= br <= 4.0:
                    scores.append(100)  # IDEAL
            
            # Calculate average score
            if scores:
                # CRITICAL FIX: If ANY metric is CRITICAL (0 points), force score to 40
                if 0 in scores:
                    # Force score to 40 to trigger "Attention Required" status (< 50)
                    return min(int(sum(scores) / len(scores)), 40)
                return int(sum(scores) / len(scores))
            else:
                return 0
                
        except Exception as e:
            logger.error(f"Error calculating pool health score: {e}")
            return 0
    
    
    def _draw_water_testing_gauge(self, score, color="#95a5a6"):
        """Draw the circular health gauge"""
        self.health_canvas.delete("all")
        
        # Center coordinates
        cx, cy = 140, 140  # Center for 280x280 canvas
        radius = 110  # Larger radius for bigger canvas
        
        # Draw outer circle (background)
        self.health_canvas.create_oval(
            cx - radius, cy - radius,
            cx + radius, cy + radius,
            outline="#ecf0f1",
            width=20,
            fill="white"
        )
        
        # Draw score arc
        if score > 0:
            # Calculate arc extent (0-360°Frees)
            extent = (score / 100) * 360
            
            # Draw colored arc
            self.health_canvas.create_arc(
                cx - radius, cy - radius,
                cx + radius, cy + radius,
                start=90,  # Start at top
                extent=-extent,  # Clockwise
                outline=color,
                width=20,
                style="arc"
            )
        
        # Draw score text in center
        self.health_canvas.create_text(
            cx, cy - 10,
            text=str(score),
            font=("Arial", 48, "bold"),
            fill=color
        )
        
        # Draw "out of 100" text
        self.health_canvas.create_text(
            cx, cy + 30,
            text="out of 100",
            font=("Arial", 12),
            fill="#7f8c8d"
        )
    
    def _update_pool_health_display(self, readings):
        """Update the pool health scoreboard with current readings"""
        if not readings:
            self._draw_water_testing_gauge(0, "#95a5a6")
            self.health_status_label.config(
                text="Water Quality: Not Tested",
                fg="#95a5a6"
            )
            return
        
        # Calculate score
        score = self._calculate_pool_health_score(readings)
        
        # Determine color and status based on score
        if score >= 90:
            color = "#3498db"  # Blue - Excellent
            status = "Water Quality: Safe to Swim [OK]"
            status_color = "#27ae60"
        elif score >= 75:
            color = "#2ecc71"  # Green - Good
            status = "Water Quality: Good"
            status_color = "#27ae60"
        elif score >= 60:
            color = "#f39c12"  # Yellow - Caution
            status = "Water Quality: Caution [!]"
            status_color = "#f39c12"
        else:
            color = "#e74c3c"  # Red - Action Needed
            status = "Water Quality: Attention Required [!]"
            status_color = "#e74c3c"
        
        # Update gauge
        self._draw_water_testing_gauge(score, color)
        
        # Update status label
        self.health_status_label.config(
            text=status,
            fg=status_color
        )

    def _check_safety_alerts(self):
        """Check for unsafe water conditions and alert user with severity classification"""
        try:
            current = self._get_readings_from_form(show_warnings=False)
            if not current:
                return
            
            # Get custom thresholds for this pool
            pool_id = self.active_pool_id if hasattr(self, 'active_pool_id') and self.active_pool_id else 'default'
            thresholds = self._apply_custom_thresholds(pool_id)
            
            alerts = []
            critical_alerts = []
            
            # Check pH
            ph = current.get('ph')
            if ph is not None:
                severity = self._classify_alert_severity('ph', ph, thresholds['ph_min'], thresholds['ph_max'])
                if severity:
                    if severity == 'critical':
                        if ph < 6.8:
                            alert_data = ('pH', ph, 'DANGEROUSLY LOW', 
                                'Acidic water can cause eye/skin irritation', 
                                'Add Soda Ash immediately. Do not swim!', 'critical')
                        else:
                            alert_data = ('pH', ph, 'DANGEROUSLY HIGH',
                                'Alkaline water can cause eye/skin irritation',
                                'Add Muriatic Acid immediately. Do not swim!', 'critical')
                        critical_alerts.append(alert_data)
                        # Save to history BEFORE showing popup
                        self._save_alert_to_history(
                            parameter='pH',
                            value=ph,
                            threshold_min=thresholds['ph_min'],
                            threshold_max=thresholds['ph_max'],
                            message=f"pH {alert_data[2]}: {alert_data[3]}",
                            severity='critical'
                        )
                    elif severity == 'warning':
                        alert_data = ('pH', ph, 'Out of Range',
                            'Can cause irritation and reduce chlorine effectiveness',
                            'Adjust pH to 7.2-7.6 range', 'warning')
                        alerts.append(alert_data)
                        self._save_alert_to_history(
                            parameter='pH',
                            value=ph,
                            threshold_min=thresholds['ph_min'],
                            threshold_max=thresholds['ph_max'],
                            message=f"pH {alert_data[2]}: {alert_data[3]}",
                            severity='warning'
                        )
                    elif severity == 'info':
                        alert_data = ('pH', ph, 'Slightly Out of Range',
                            'Minor deviation from ideal range',
                            'Monitor and adjust if needed', 'info')
                        alerts.append(alert_data)
                        self._save_alert_to_history(
                            parameter='pH',
                            value=ph,
                            threshold_min=thresholds['ph_min'],
                            threshold_max=thresholds['ph_max'],
                            message=f"pH {alert_data[2]}: {alert_data[3]}",
                            severity='info'
                        )
            
            # Check Free Chlorine
            fc = current.get('free_chlorine')
            if fc is not None:
                severity = self._classify_alert_severity('chlorine', fc, thresholds['chlorine_min'], thresholds['chlorine_max'])
                if severity:
                    if severity == 'critical':
                        if fc < 0.5:
                            alert_data = ('Free Chlorine', fc, 'CRITICALLY LOW',
                                'Bacteria and algae can grow. Water unsafe!',
                                'Add chlorine immediately. Do not swim!', 'critical')
                        else:
                            alert_data = ('Free Chlorine', fc, 'DANGEROUSLY HIGH',
                                'Can cause severe eye/skin irritation',
                                'Do not swim! Wait for chlorine to drop below 3.0', 'critical')
                        critical_alerts.append(alert_data)
                        self._save_alert_to_history(
                            parameter='Free Chlorine',
                            value=fc,
                            threshold_min=thresholds['chlorine_min'],
                            threshold_max=thresholds['chlorine_max'],
                            message=f"Chlorine {alert_data[2]}: {alert_data[3]}",
                            severity='critical'
                        )
                    elif severity == 'warning':
                        alert_data = ('Free Chlorine', fc, 'Out of Range',
                            'Insufficient sanitization or too strong',
                            'Adjust chlorine to 1.0-3.0 ppm range', 'warning')
                        alerts.append(alert_data)
                        self._save_alert_to_history(
                            parameter='Free Chlorine',
                            value=fc,
                            threshold_min=thresholds['chlorine_min'],
                            threshold_max=thresholds['chlorine_max'],
                            message=f"Chlorine {alert_data[2]}: {alert_data[3]}",
                            severity='warning'
                        )
                    elif severity == 'info':
                        alert_data = ('Free Chlorine', fc, 'Slightly Out of Range',
                            'Minor deviation from ideal range',
                            'Monitor and adjust if needed', 'info')
                        alerts.append(alert_data)
                        self._save_alert_to_history(
                            parameter='Free Chlorine',
                            value=fc,
                            threshold_min=thresholds['chlorine_min'],
                            threshold_max=thresholds['chlorine_max'],
                            message=f"Chlorine {alert_data[2]}: {alert_data[3]}",
                            severity='info'
                        )
            
            # Check Cyanuric Acid
            cya = current.get('cyanuric_acid')
            if cya is not None:
                severity = self._classify_alert_severity('cya', cya, thresholds['cya_min'], thresholds['cya_max'])
                if severity:
                    if severity == 'critical' or cya > 100:
                        alert_data = ('Cyanuric Acid', cya, 'DANGEROUSLY HIGH',
                            'Chlorine effectiveness severely reduced',
                            'Partially drain and refill pool', 'critical')
                        critical_alerts.append(alert_data)
                        self._save_alert_to_history(
                            parameter='Cyanuric Acid',
                            value=cya,
                            threshold_min=thresholds['cya_min'],
                            threshold_max=thresholds['cya_max'],
                            message=f"CYA {alert_data[2]}: {alert_data[3]}",
                            severity='critical'
                        )
                    elif severity == 'warning':
                        alert_data = ('Cyanuric Acid', cya, 'Out of Range',
                            'May affect chlorine effectiveness',
                            'Adjust CYA levels', 'warning')
                        alerts.append(alert_data)
                        self._save_alert_to_history(
                            parameter='Cyanuric Acid',
                            value=cya,
                            threshold_min=thresholds['cya_min'],
                            threshold_max=thresholds['cya_max'],
                            message=f"CYA {alert_data[2]}: {alert_data[3]}",
                            severity='warning'
                        )
            
            # Check Temperature
            temp = current.get('temperature')
            if temp is not None:
                # Only alert for temperature if it's significantly out of range
                # Temperature is comfort-related, not safety-critical (except extreme heat)
                if temp > 104:
                    # Dangerously hot - health risk
                    alert_data = ('Temperature', temp, 'DANGEROUSLY HIGH',
                        'Risk of heat exhaustion',
                        'Do not swim! Allow water to cool', 'critical')
                    critical_alerts.append(alert_data)
                    self._save_alert_to_history(
                        parameter='Temperature',
                        value=temp,
                        threshold_min=thresholds['temperature_min'],
                        threshold_max=thresholds['temperature_max'],
                        message=f"Temperature {alert_data[2]}: {alert_data[3]}",
                        severity='critical'
                    )
                elif temp > 95:
                    # Very warm but not dangerous
                    alert_data = ('Temperature', temp, 'Very Warm',
                        'Water temperature is quite high',
                        'Monitor temperature, may be uncomfortable', 'warning')
                    alerts.append(alert_data)
                    self._save_alert_to_history(
                        parameter='Temperature',
                        value=temp,
                        threshold_min=thresholds['temperature_min'],
                        threshold_max=thresholds['temperature_max'],
                        message=f"Temperature {alert_data[2]}: {alert_data[3]}",
                        severity='warning'
                    )
                elif temp < 65:
                    # Very cold - most people won't swim
                    alert_data = ('Temperature', temp, 'Very Cold',
                        'Water temperature is quite low',
                        'Water will be very cold for swimming', 'info')
                    alerts.append(alert_data)
                    self._save_alert_to_history(
                        parameter='Temperature',
                        value=temp,
                        threshold_min=thresholds['temperature_min'],
                        threshold_max=thresholds['temperature_max'],
                        message=f"Temperature {alert_data[2]}: {alert_data[3]}",
                        severity='info'
                    )
                # Note: Temperatures between 65-95°F don't trigger alerts
                # This range (including 71°F) is acceptable for swimming
            
            # Check ORP (Oxidation-Reduction Potential)
            orp = current.get('orp')
            if orp is not None:
                if orp < 650:
                    alert_data = ('ORP', orp, 'CRITICALLY LOW',
                        'Insufficient sanitization - bacteria/algae can grow',
                        'Add chlorine immediately. Do not swim!', 'critical')
                    critical_alerts.append(alert_data)
                    self._save_alert_to_history(
                        parameter='ORP',
                        value=orp,
                        threshold_min=650,
                        threshold_max=750,
                        message=f"ORP {alert_data[2]}: {alert_data[3]}",
                        severity='critical'
                    )
                elif orp > 800:
                    alert_data = ('ORP', orp, 'DANGEROUSLY HIGH',
                        'Over-oxidized water can cause eye/skin irritation',
                        'Do not swim! Wait for ORP to drop below 750 mV', 'critical')
                    critical_alerts.append(alert_data)
                    self._save_alert_to_history(
                        parameter='ORP',
                        value=orp,
                        threshold_min=650,
                        threshold_max=750,
                        message=f"ORP {alert_data[2]}: {alert_data[3]}",
                        severity='critical'
                    )
                elif 650 <= orp < 700:
                    alert_data = ('ORP', orp, 'Low',
                        'Sanitization may be insufficient',
                        'Check chlorine levels and adjust', 'warning')
                    alerts.append(alert_data)
                    self._save_alert_to_history(
                        parameter='ORP',
                        value=orp,
                        threshold_min=650,
                        threshold_max=750,
                        message=f"ORP {alert_data[2]}: {alert_data[3]}",
                        severity='warning'
                    )
                elif 750 < orp <= 800:
                    alert_data = ('ORP', orp, 'High',
                        'Water may be over-oxidized',
                        'Reduce chlorine or wait for levels to drop', 'warning')
                    alerts.append(alert_data)
                    self._save_alert_to_history(
                        parameter='ORP',
                        value=orp,
                        threshold_min=650,
                        threshold_max=750,
                        message=f"ORP {alert_data[2]}: {alert_data[3]}",
                        severity='warning'
                    )
            
            # Check Bromine (if used instead of chlorine)
            br = current.get('bromine')
            if br is not None:
                if br < 1.0:
                    alert_data = ('Bromine', br, 'CRITICALLY LOW',
                        'Insufficient sanitization - bacteria can grow',
                        'Add bromine immediately. Do not swim!', 'critical')
                    critical_alerts.append(alert_data)
                    self._save_alert_to_history(
                        parameter='Bromine',
                        value=br,
                        threshold_min=2.0,
                        threshold_max=4.0,
                        message=f"Bromine {alert_data[2]}: {alert_data[3]}",
                        severity='critical'
                    )
                elif br > 6.0:
                    alert_data = ('Bromine', br, 'DANGEROUSLY HIGH',
                        'Can cause severe eye/skin irritation',
                        'Do not swim! Wait for bromine to drop below 4.0', 'critical')
                    critical_alerts.append(alert_data)
                    self._save_alert_to_history(
                        parameter='Bromine',
                        value=br,
                        threshold_min=2.0,
                        threshold_max=4.0,
                        message=f"Bromine {alert_data[2]}: {alert_data[3]}",
                        severity='critical'
                    )
                elif 1.0 <= br < 2.0 or 4.0 < br <= 6.0:
                    alert_data = ('Bromine', br, 'Out of Range',
                        'Sanitization may be insufficient or too strong',
                        'Adjust bromine to 2.0-4.0 ppm range', 'warning')
                    alerts.append(alert_data)
                    self._save_alert_to_history(
                        parameter='Bromine',
                        value=br,
                        threshold_min=2.0,
                        threshold_max=4.0,
                        message=f"Bromine {alert_data[2]}: {alert_data[3]}",
                        severity='warning'
                    )
            
            # Show alerts
            if critical_alerts:
                self._show_critical_alert_popup(critical_alerts)
            elif alerts:
                self._show_warning_alert_popup(alerts)
                
        except Exception as e:
            logger.error(f"Error checking safety: {e}")

    
    def _show_critical_alert_popup(self, alerts):
        """Show critical safety alert"""
        msg = "CRITICAL SAFETY ALERT - DO NOT SWIM!\n\n"
        parameters = {}
        danger_text = ""
        action_text = ""
        
        for param, value, issue, danger, action, severity in alerts:
            msg += f"{param}: {value:.1f} - {issue}\n"
            msg += f"Danger: {danger}\n"
            msg += f"Action: {action}\n\n"
            parameters[param] = f"{value:.1f} - {issue}"
            danger_text += f"{danger} "
            action_text += f"{action} "
        
        messagebox.showerror("CRITICAL SAFETY ALERT", msg)
        
        # Send notification
        self._send_notification('critical_alert', {
            'message': 'CRITICAL SAFETY ALERT - DO NOT SWIM!',
            'danger': danger_text.strip(),
            'action': action_text.strip(),
            'parameters': parameters
        })

    def _show_warning_alert_popup(self, alerts):
        """Show warning alert"""
        msg = "Water chemistry needs attention:\n\n"
        parameters = {}
        caution_text = ""
        action_text = ""
        
        for param, value, issue, danger, action, severity in alerts:
            msg += f"{param}: {value:.1f} - {issue}\n"
            msg += f"{danger}\n"
            msg += f"Action: {action}\n\n"
            parameters[param] = f"{value:.1f} - {issue}"
            caution_text += f"{danger} "
            action_text += f"{action} "
        
        messagebox.showwarning("Safety Alert", msg)
        
        # Send notification
        self._send_notification('warning_alert', {
            'message': 'Water chemistry needs attention',
            'caution': caution_text.strip(),
            'action': action_text.strip(),
            'parameters': parameters
        })


    def _create_empty_test_strips(self):
        """Create empty test strips display"""
        for widget in self.test_strips_container.winfo_children():
            widget.destroy()
        
        # Create styled empty state
        empty_frame = tk.Frame(self.test_strips_container, bg="#f8f9fa", bd=2, relief="solid")
        empty_frame.pack(fill="both", expand=True, padx=10, pady=20)
        
        tk.Label(
            empty_frame,
            text="No test results yet",
            font=("Arial", 14, "bold"),
            fg="#6c757d",
            bg="#f8f9fa"
        ).pack(pady=(30, 10))
        
        tk.Label(
            empty_frame,
            text="Enter water test readings above and click 'Calculate Adjustments'\nto see your visual test strip results here.",
            font=("Arial", 11),
            fg="#6c757d",
            bg="#f8f9fa",
            justify="center"
        ).pack(pady=(0, 30))
    
    def _update_test_strips(self, readings):
        """Update test strips with color-coded results - ALL 9 METRICS - IMPROVED LAYOUT"""
        for widget in self.test_strips_container.winfo_children():
            widget.destroy()
        
        # Main container
        main_frame = tk.Frame(self.test_strips_container, bg="white")
        main_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Legend at top
        legend_frame = tk.Frame(main_frame, bg="white")
        legend_frame.pack(fill="x", pady=(0, 10))
        
        tk.Label(legend_frame, text="Legend:", font=("Arial", 9, "bold"), bg="white").pack(side="left", padx=5)
        
        # Green
        tk.Label(legend_frame, text="*", font=("Arial", 14), fg="#32CD32", bg="white").pack(side="left")
        tk.Label(legend_frame, text="Good", font=("Arial", 8), bg="white").pack(side="left", padx=(0, 10))
        
        # Orange
        tk.Label(legend_frame, text="*", font=("Arial", 14), fg="#FF8C00", bg="white").pack(side="left")
        tk.Label(legend_frame, text="Low", font=("Arial", 8), bg="white").pack(side="left", padx=(0, 10))
        
        # Red
        tk.Label(legend_frame, text="*", font=("Arial", 14), fg="#DC143C", bg="white").pack(side="left")
        tk.Label(legend_frame, text="High", font=("Arial", 8), bg="white").pack(side="left")
        
        # Scrollable container for strips
        canvas = tk.Canvas(main_frame, bg="white", highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="white")
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Define ALL 9 test strip parameters
        strip_params = [
            'ph', 'free_chlorine', 'total_chlorine', 
            'alkalinity', 'calcium_hardness', 'cyanuric_acid',
            'temperature', 'bromine', 'salt'
        ]
        
        # Create grid of test strips (2 columns for better fit)
        row_num = 0
        col_num = 0
        
        for param in strip_params:
            if param not in readings:
                # Show "No Data" for missing parameters
                value = 0
                show_no_data = True
            else:
                value = readings[param]
                show_no_data = False
            
            thresholds = CHEMICAL_THRESHOLDS.get(param, {})
            
            if not thresholds:
                continue
            
            # Determine color based on thresholds
            if show_no_data:
                color = "#CCCCCC"  # Gray for no data
                status = "NO DATA"
                status_color = "#666666"
            else:
                min_val = thresholds.get('min', 0)
                max_val = thresholds.get('max', 100)
                
                if value < min_val:
                    color = "#FF8C00"  # Orange
                    status = "LOW"
                    status_color = "#FF8C00"
                elif value > max_val:
                    color = "#DC143C"  # Red
                    status = "HIGH"
                    status_color = "#DC143C"
                else:
                    color = "#32CD32"  # Green
                    status = "GOOD"
                    status_color = "#32CD32"
            
            # Create strip frame
            strip_frame = tk.Frame(
                scrollable_frame,
                bg=color,
                relief="raised",
                borderwidth=2,
                width=100,
                height=160
            )
            strip_frame.grid(row=row_num, column=col_num, padx=8, pady=8, sticky="nsew")
            strip_frame.grid_propagate(False)
            
            # Parameter name
            param_name = thresholds.get('name', param.replace('_', ' ').title())
            tk.Label(
                strip_frame,
                text=param_name,
                font=("Arial", 9, "bold"),
                bg=color,
                fg="white"
            ).pack(pady=(10, 5))
            
            # Value
            unit = thresholds.get('unit', '')
            if show_no_data:
                value_text = "No Data"
            else:
                value_text = f"{value}"
            
            tk.Label(
                strip_frame,
                text=value_text,
                font=("Arial", 16, "bold"),
                bg=color,
                fg="white"
            ).pack(pady=5)
            
            # Unit
            if not show_no_data:
                tk.Label(
                    strip_frame,
                    text=unit,
                    font=("Arial", 9),
                    bg=color,
                    fg="white"
                ).pack()
            
            # Status
            tk.Label(
                strip_frame,
                text=status,
                font=("Arial", 8, "bold"),
                bg="white",
                fg=status_color,
                relief="solid",
                borderwidth=1,
                padx=5,
                pady=2
            ).pack(pady=(10, 5))
            
            # Range
            if not show_no_data:
                min_val = thresholds.get('min', 0)
                max_val = thresholds.get('max', 100)
                range_text = f"Range: {min_val}-{max_val}"
                tk.Label(
                    strip_frame,
                    text=range_text,
                    font=("Arial", 7),
                    bg=color,
                    fg="white"
                ).pack()
            
            # Update grid position
            col_num += 1
            if col_num >= 4:  # 4 columns
                col_num = 0
                row_num += 1
        
        # Configure grid weights
        for i in range(4):
            scrollable_frame.columnconfigure(i, weight=1)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Enable mouse wheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
    def _create_footer(self):
        """Create the application footer"""
        # Footer frame
        self.footer_frame = ttk.Frame(self)
        self.footer_frame.pack(fill="x", padx=10, pady=5)

        # Status bar
        self.status_bar = ttk.Label(
            self.footer_frame,
            text="Ready",
            relief="sunken",
            anchor="w"
        )
        self.status_bar.pack(fill="x")

    def _load_data(self):
        """Load saved data"""
        # Safety check to ensure GUI is initialized before loading data
        if not getattr(self, 'gui_initialized', False):
            logger.warning("GUI not initialized yet, skipping data load")
            return
            
        try:
            if self.customer_file.exists():
                self.customer_info = load_json(self.customer_file)
                self._populate_customer_info(self.customer_info)

            if self.readings_file.exists():
                readings_data = load_json(self.readings_file)
                if "readings" in readings_data:
                    self.chemical_readings = readings_data["readings"]
                    self._refresh_analytics_dashboard()

            logger.info("Data loaded successfully")
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            messagebox.showwarning("Error", f"Error loading data: {e}")

    def _populate_customer_info(self, customer_info):
        """Populate customer information fields"""
        # Safety check to ensure GUI components exist before accessing them
        if not hasattr(self, 'customer_name_entry') or not self.customer_name_entry:
            logger.warning("GUI components not initialized yet, skipping customer info population")
            return
            
        self.customer_name_entry.delete(0, tk.END)
        self.customer_name_entry.insert(0, customer_info.get("name", ""))
        self.pool_type_var.set(customer_info.get("pool_type", ""))

        pool_size = customer_info.get("pool_size")
        self.pool_size_entry.delete(0, tk.END)
        if pool_size:
            self.pool_size_entry.insert(0, str(pool_size))

        self.address1_entry.delete(0, tk.END)
        self.address1_entry.insert(0, customer_info.get("address_line1", ""))
        self.address2_entry.delete(0, tk.END)
        self.address2_entry.insert(0, customer_info.get("address_line2", ""))
        self.city_entry.delete(0, tk.END)
        self.city_entry.insert(0, customer_info.get("city", ""))
        self.state_entry.delete(0, tk.END)
        self.state_entry.insert(0, customer_info.get("state", ""))
        self.postal_code_entry.delete(0, tk.END)
        self.postal_code_entry.insert(0, customer_info.get("postal_code", ""))
        self.country_entry.delete(0, tk.END)
        self.country_entry.insert(0, customer_info.get("country", "US"))


    def _setup_arduino_communication(self):
        """Set up communication with Arduino if available"""
        try:
            try:
                import serial.tools.list_ports
                ports = list(serial.tools.list_ports.comports())
                
                if not ports:
                    # No COM ports available - Arduino not connected (this is OK)
                    logger.debug("No COM ports found - Arduino not connected")
                    self.arduino = None
                    return
                
                # Try to find Arduino by description first
                arduino_port = None
                for p in ports:
                    desc = p.description.upper()
                    if any(keyword in desc for keyword in ["ARDUINO", "CH340", "USB SERIAL", "USB-SERIAL"]):
                        arduino_port = p.device
                        logger.info(f"Found Arduino-like device: {p.device} - {p.description}")
                        break
                
                if not arduino_port:
                    # No Arduino found - this is OK, just log at debug level
                    logger.debug(f"No Arduino device found in {len(ports)} available ports")
                    logger.debug(f"Available ports: {[f'{p.device}: {p.description}' for p in ports]}")
                    self.arduino = None
                    return
                
                # Try to connect to the Arduino
                self.arduino = ArduinoInterface(port=arduino_port)
                if self.arduino.connect():
                    logger.info(f"Connected to Arduino on {arduino_port}")
                    self.arduino_thread = threading.Thread(target=self._arduino_communication_loop, daemon=True)
                    self.arduino_thread.start()
                else:
                    logger.warning(f"Arduino found on {arduino_port} but connection failed")
                    logger.warning(f"HINT: If you see 'Access is denied', close Arduino IDE Serial Monitor and restart this app")
                    self.arduino = None
                    
            except ImportError:
                logger.debug("pyserial not installed. Arduino communication disabled.")
                self.arduino = None
        except Exception as e:
            logger.debug(f"Arduino setup error (this is OK if no Arduino connected): {e}")
            self.arduino = None

    def _arduino_communication_loop(self):
        """Background thread for Arduino communication"""
        while not self._stop_threads.is_set():
            try:
                data = self.arduino.read_data()
                if data:
                    readings = {}
                    for item in data.split(','):
                        if ':' in item:
                            parts = item.split(':', 1)  # Split only on first colon
                            if len(parts) != 2:
                                continue
                            key, value = parts
                            try:
                                readings[key.strip()] = float(value.strip())
                            except ValueError:
                                pass
                    if readings:
                        self.after(0, lambda: self._update_readings_from_arduino(readings))
            except Exception as e:
                logger.error(f"Arduino communication error: {e}")
            time.sleep(1)

    def _update_readings_from_arduino(self, readings):
        """Update UI with readings from Arduino"""
        try:
            for key, value in readings.items():
                normalized_key = key.lower().replace(" ", "_")
                if normalized_key in self.entries:
                    self.entries[normalized_key].delete(0, tk.END)
                    self.entries[normalized_key].insert(0, str(value))
        except Exception as e:
            logger.error(f"Error updating readings from Arduino: {e}")


    def _start_periodic_updates(self):
        """Start periodic update tasks"""
        self._update_datetime()
        if self.zip_code.get():
            self._update_weather()
        if self.auto_backup_var.get():
            if self.backup_id:
                self.after_cancel(self.backup_id)
            self.backup_id = self.after(3600000, self._backup_data)  # Every hour (3600000 ms)
            logger.info("Next automatic backup scheduled.")

    def _update_datetime(self):
        """Update the date/time display"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.datetime_label.config(text=current_time)
        self.datetime_update_id = self.after(1000, self._update_datetime)

    def _update_weather(self):
        """Update weather information"""
        # Check if weather API is available
        if not self.weather_api:
            self.status_var.set("Weather API not configured. Set WEATHER_API_KEY environment variable.")
            self._update_status("Weather API not configured.")
            return
        
        zip_code = self.zip_code.get()
        if not zip_code:
            self.status_var.set("Enter a ZIP code for weather updates.")
            self._update_status("Enter a ZIP code for weather updates.")
            return

        try:
            self.status_var.set("Updating weather...")
            self._update_status("Updating weather...")
            
            # Add a timeout to prevent the application from hanging
            weather_data = self.weather_api.get_weather_data(zip_code)

            if "error" in weather_data:
                logger.warning(f"Weather API error: {weather_data['error']}")
                self.status_var.set(f"Weather update failed: {weather_data['error']}")
                self._update_status(f"Weather update failed: {weather_data['error']}")
                
                # Use cached weather data if available
                if hasattr(self, 'weather_data') and self.weather_data and "error" not in self.weather_data:
                    logger.info("Using cached weather data")
                    self.status_var.set("Using cached weather data")
                    return
                else:
                    # Show a graceful error message in the UI
                    self._display_weather_error(weather_data['error'])
                    return

            self.weather_data = weather_data
            self.after(0, lambda: self._display_weather(weather_data))
            self.status_var.set("Weather updated successfully")
            self._update_status("Weather updated successfully")
            self.weather_update_id = self.after(1800000, self._update_weather)  # 30 minutes
        except Exception as e:
            logger.error(f"Error updating weather: {str(e)}", exc_info=True)
            self.status_var.set("Weather update failed")
            self._update_status("Weather update failed")
            # Display error in UI
            self._display_weather_error(str(e))

    def _display_weather_error(self, error_message):
        """Display a weather error in the UI"""
        for widget in self.weather_display_frame.winfo_children():
            widget.destroy()
        ttk.Label(
            self.weather_display_frame,
            text=f"Weather update failed: {error_message}",
            foreground="red"
        ).grid(row=0, column=0, sticky="w", padx=5, pady=2)
        ttk.Label(
            self.weather_display_frame,
            text="Using default values for calculations",
            foreground="blue"
        ).grid(row=1, column=0, sticky="w", padx=5, pady=2)


    def _display_weather(self, weather_data):
        """Display weather information in the UI"""
        try:
            for widget in self.weather_display_frame.winfo_children():
                widget.destroy()

            if "error" in weather_data:
                ttk.Label(self.weather_display_frame, text=f"Error: {weather_data['error']}", 
                         foreground="red").grid(row=0, column=0, sticky="w", padx=5, pady=2)
                return

            # Display current weather
            current = weather_data.get("current", {})
            location = weather_data.get("location", {})
            
            # Configure the display frame to expand
            self.weather_display_frame.columnconfigure(0, weight=1)
            
            # Current weather section
            current_frame = ttk.LabelFrame(self.weather_display_frame, text="Current Weather")
            current_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
            
            ttk.Label(current_frame, 
                     text=f"Location: {location.get('name', 'N/A')}, {location.get('region', 'N/A')}").grid(
                     row=0, column=0, sticky="w", padx=5, pady=2)
            
            ttk.Label(current_frame, 
                     text=f"Temperature: {current.get('temp_f', 'N/A')}°FF (Feels like: {current.get('feelslike_f', 'N/A')}°FF)").grid(
                     row=1, column=0, sticky="w", padx=5, pady=2)
            
            ttk.Label(current_frame, 
                     text=f"Humidity: {current.get('humidity', 'N/A')}%").grid(
                     row=2, column=0, sticky="w", padx=5, pady=2)
            
            condition = current.get('condition', {})
            ttk.Label(current_frame, 
                     text=f"Condition: {condition.get('text', 'N/A')}").grid(
                     row=3, column=0, sticky="w", padx=5, pady=2)

            impact = self._calculate_weather_impact(current)
            impact_label = ttk.Label(current_frame, text=f"Pool Impact: {impact}")
            impact_label.grid(row=4, column=0, sticky="w", padx=5, pady=2)
            
            # 5-Day Forecast section
            forecast = weather_data.get("forecast", {}).get("forecastday", [])
            if forecast:
                forecast_frame = ttk.LabelFrame(self.weather_display_frame, text=f"{len(forecast)}-Day Forecast")
                forecast_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
                
                # Configure forecast frame to expand
                forecast_frame.columnconfigure(0, weight=1)
                
                # Display message if less than 5 days
                if len(forecast) < 5:
                    ttk.Label(
                        forecast_frame,
                        text=f"Note: Only {len(forecast)} days available (API may limit free tier to 3 days)",
                        font=("Arial", 8, "italic"),
                        foreground="orange"
                    ).grid(row=0, column=0, sticky="w", padx=5, pady=2)
                    start_row = 1
                else:
                    start_row = 0
                
                for idx, day in enumerate(forecast[:5]):  # Limit to 5 days
                    date = day.get('date', 'N/A')
                    day_data = day.get('day', {})
                    
                    # Create a frame for each day
                    day_frame = ttk.Frame(forecast_frame)
                    day_frame.grid(row=start_row + idx, column=0, sticky="ew", padx=5, pady=2)
                    
                    ttk.Label(day_frame, text=f"{date}:", font=("Arial", 9, "bold")).pack(side="left", padx=5)
                    ttk.Label(day_frame, text=f"High: {day_data.get('maxtemp_f', 'N/A')}°FF").pack(side="left", padx=5)
                    ttk.Label(day_frame, text=f"Low: {day_data.get('mintemp_f', 'N/A')}°FF").pack(side="left", padx=5)
                    ttk.Label(day_frame, text=f"{day_data.get('condition', {}).get('text', 'N/A')}").pack(side="left", padx=5)
            else:
                # No forecast data available
                ttk.Label(
                    self.weather_display_frame,
                    text="No forecast data available. Update weather to fetch forecast.",
                    font=("Arial", 9, "italic"),
                    foreground="gray"
                ).grid(row=1, column=0, sticky="w", padx=5, pady=5)
                    
        except Exception as e:
            logger.error(f"Error displaying weather: {e}")
            ttk.Label(self.weather_display_frame, 
                     text=f"Error displaying weather information: {str(e)}", 
                     foreground="red").grid(row=0, column=0, sticky="w", padx=5, pady=2)

    def _calculate_weather_impact(self, weather_data):
        """Calculate the impact of weather on pool chemistry"""
        try:
            temp = weather_data.get('temp_f', 75)
            humidity = weather_data.get('humidity', 50)
            conditions = weather_data.get('condition', {}).get('text', '').lower()
            
            impact = "Low"
            
            # Higher temperatures increase chlorine demand
            if temp > 85:
                impact = "High"
            elif temp > 75:
                impact = "Medium"
                
            # Rain can affect pH and dilute chemicals
            if any(term in conditions for term in ['rain', 'shower', 'drizzle', 'precipitation']):
                impact = "High"
                
            # High humidity can reduce water evaporation
            if humidity > 80 and impact != "High":
                impact = "Medium"
                
            # Store impact for later calculations
            self.weather_impact = impact
            return impact
        except Exception as e:
            logger.error(f"Error calculating weather impact: {e}")
            return "Unknown"


    def _calculate_adjustments(self):
        """Calculate chemical adjustments based on readings"""
        try:
            readings = self._get_readings_from_form()
            if not readings:
                return None
                
            adjustments = {}
            
            # Calculate chlorine adjustment
            target_chlorine = 3.0  # ppm
            current_chlorine = readings.get('free_chlorine', 0)
            pool_size = float(self.pool_size_entry.get()) if self.pool_size_entry.get() else 10000
            
            if current_chlorine < target_chlorine:
                chlorine_needed = (target_chlorine - current_chlorine) * pool_size / 10000
                adjustments['chlorine'] = {
                    'action': 'add',
                    'amount': round(chlorine_needed, 2),
                    'unit': 'oz'
                }
            elif current_chlorine > target_chlorine + 1:
                adjustments['chlorine'] = {
                    'action': 'reduce',
                    'amount': 0,
                    'unit': '',
                    'message': 'Let chlorine levels naturally reduce or partially drain and refill'
                }
            
            # Calculate pH adjustment
            target_ph_min = 7.2
            target_ph_max = 7.6
            current_ph = readings.get('ph', 7.4)
            
            if current_ph < target_ph_min:
                ph_adjustment = (target_ph_min - current_ph) * pool_size / 10000
                adjustments['ph'] = {
                    'action': 'increase',
                    'amount': round(ph_adjustment * 2, 2),
                    'unit': 'oz',
                    'chemical': 'soda ash'
                }
            elif current_ph > target_ph_max:
                ph_adjustment = (current_ph - target_ph_max) * pool_size / 10000
                adjustments['ph'] = {
                    'action': 'decrease',
                    'amount': round(ph_adjustment * 3, 2),
                    'unit': 'oz',
                    'chemical': 'muriatic acid'
                }
            
            # Calculate alkalinity adjustment
            target_alk_min = 80
            target_alk_max = 120
            current_alk = readings.get('alkalinity', 0)
            
            if current_alk < target_alk_min:
                alk_needed = (target_alk_min - current_alk) * pool_size / 10000
                adjustments['alkalinity'] = {
                    'action': 'increase',
                    'amount': round(alk_needed * 1.5, 2),
                    'unit': 'oz',
                    'chemical': 'sodium bicarbonate'
                }
            elif current_alk > target_alk_max:
                alk_adjustment = (current_alk - target_alk_max) * pool_size / 10000
                adjustments['alkalinity'] = {
                    'action': 'decrease',
                    'amount': round(alk_adjustment * 2, 2),
                    'unit': 'oz',
                    'chemical': 'muriatic acid'
                }
                
            # Weather impact can affect dosage
            if hasattr(self, 'weather_impact'):
                if self.weather_impact == "High":
                    for key in adjustments:
                        if 'amount' in adjustments[key]:
                            adjustments[key]['amount'] *= 1.2
                            adjustments[key]['weather_factor'] = "Increased due to weather conditions"
            
            # Update test strips visualization
            self._update_test_strips(readings)

            # Update pool health scoreboard
            self._update_pool_health_display(readings)


            # Display adjustments with safety warnings
            self._display_adjustments(adjustments)


            return adjustments
        except Exception as e:
            logger.error(f"Error calculating adjustments: {e}")
            messagebox.showerror("Calculation Error", f"An error occurred: {e}")
            return None
    def _get_readings_from_form(self, show_warnings=True):
        """Get chemical readings from form inputs
        
        Args:
            show_warnings: If False, don't show warning popups (for background operations)
        """
        try:
            readings = {}
            
            # Validate and collect readings from entry fields
            # List of fields that should be excluded from chemical readings
            excluded_fields = ['customer_name', 'pool_size']
            
            for param, entry in self.entries.items():
                # Skip non-chemical reading fields
                if param in excluded_fields:
                    continue
                    
                value = entry.get().strip()
                if value:
                    try:
                        readings[param] = float(value)
                    except ValueError:
                        if show_warnings:
                            messagebox.showwarning(
                                "Invalid Input", 
                                f"The value for {param.replace('_', ' ').title()} must be a number."
                            )
                            entry.delete(0, tk.END)
                            entry.focus_set()
                        return None
            
            # Ensure required readings are present (only check if show_warnings is True)
            if show_warnings:
                required_params = ['ph', 'free_chlorine']
                missing = [param.replace('_', ' ').title() for param in required_params if param not in readings]
                
                if missing:
                    messagebox.showwarning(
                        "Missing Readings",
                        f"Please enter values for: {', '.join(missing)}"
                    )
                    return None
                
            # SENSOR VALIDATION - CRITICAL FIX
            # Validate readings for sensor malfunctions before returning
            is_valid, errors, warnings = SensorValidator.validate_reading(readings)
            
            if not is_valid:
                error_msg = "SENSOR MALFUNCTION DETECTED:\n\n" + "\n".join(errors)
                if show_warnings:
                    messagebox.showerror("Sensor Error", error_msg)
                logger.error(f"Sensor validation failed: {'; '.join(errors)}")
                return None
            
            if warnings and show_warnings:
                warning_msg = "SENSOR WARNINGS:\n\n" + "\n".join(warnings)
                messagebox.showwarning("Sensor Warnings", warning_msg)
                logger.warning(f"Sensor warnings: {'; '.join(warnings)}")
            
            return readings
        except Exception as e:
            logger.error(f"Error getting readings from form: {e}")
            if show_warnings:
                messagebox.showerror("Input Error", f"An error occurred: {e}")
            return None

    def _display_adjustments(self, adjustments):
        """Display chemical adjustment recommendations with safety warnings"""
        # Safety check to ensure adjustments_frame exists
        if not hasattr(self, 'adjustments_frame') or not self.adjustments_frame:
            logger.warning("Adjustments frame not initialized yet, skipping display")
            return
            
        try:
            # Clear any previous adjustment displays
            for widget in self.adjustments_frame.winfo_children():
                widget.destroy()
                
            if not adjustments:
                no_adj_frame = tk.Frame(self.adjustments_frame, bg="#d4edda", relief="solid", borderwidth=1)
                no_adj_frame.pack(fill="x", padx=5, pady=5)
                tk.Label(
                    no_adj_frame, 
                    text="No adjustments needed. Your pool chemistry is balanced.",
                    fg="#155724",
                    bg="#d4edda",
                    font=("Arial", 11, "bold"),
                    pady=10
                ).pack()
                return
                
            # Create compact header
            header_frame = tk.Frame(self.adjustments_frame, bg="#2c3e50", height=40)
            header_frame.pack(fill="x", padx=0, pady=0)
            header_frame.pack_propagate(False)
            
            tk.Label(
                header_frame,
                text="Chemical Adjustments Needed",
                font=("Arial", 12, "bold"),
                fg="white",
                bg="#2c3e50"
            ).pack(pady=8)
            
            # Create a scrollable frame for adjustments with minimal padding
            canvas = tk.Canvas(self.adjustments_frame, bg="white", highlightthickness=0)
            scrollbar = ttk.Scrollbar(self.adjustments_frame, orient="vertical", command=canvas.yview)
            scrollable_frame = tk.Frame(canvas, bg="white")
            
            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )
            
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            
            # Create compact frames for each adjustment
            for chemical, data in adjustments.items():
                # Main adjustment frame with colored header
                adj_container = tk.Frame(scrollable_frame, bg="white", relief="solid", borderwidth=1)
                adj_container.pack(fill="x", padx=5, pady=3)
                
                # Header with chemical name
                header = tk.Frame(adj_container, bg="#3498db", height=25)
                header.pack(fill="x")
                header.pack_propagate(False)
                
                tk.Label(
                    header,
                    text=f"{chemical.replace('_', ' ').title()}",
                    font=("Arial", 10, "bold"),
                    fg="white",
                    bg="#3498db"
                ).pack(side="left", padx=10, pady=5)
                
                # Content frame
                content_frame = tk.Frame(adj_container, bg="white")
                content_frame.pack(fill="x", padx=8, pady=5)
                
                # Action and amount in one line
                action_text = f"{data['action'].title()}"
                if 'chemical' in data:
                    action_text += f" using {data['chemical'].title()}"
                if 'amount' in data and data['amount'] > 0:
                    action_text += f": {data['amount']} {data['unit']}"
                    
                tk.Label(
                    content_frame,
                    text=action_text,
                    font=("Arial", 10, "bold"),
                    fg="#2c3e50",
                    bg="white",
                    anchor="w"
                ).pack(fill="x", pady=2)
                
                # Message (if applicable)
                if 'message' in data:
                    tk.Label(
                        content_frame,
                        text=f"{data['message']}",
                        font=("Arial", 9),
                        fg="#7f8c8d",
                        bg="white",
                        wraplength=450,
                        justify="left",
                        anchor="w"
                    ).pack(fill="x", pady=2)
                
                # Weather factor (if applicable)
                if 'weather_factor' in data:
                    tk.Label(
                        content_frame,
                        text=f"{data['weather_factor']}",
                        font=("Arial", 9),
                        fg="#f39c12",
                        bg="white",
                        anchor="w"
                    ).pack(fill="x", pady=2)
                
                # Add compact safety warnings
                safety_key = chemical.lower()
                action_key = data.get('action', '').lower()
                
                if safety_key in CHEMICAL_SAFETY and action_key in CHEMICAL_SAFETY[safety_key]:
                    safety_info = CHEMICAL_SAFETY[safety_key][action_key]
                    
                    # Warnings in compact format
                    if safety_info.get('warnings'):
                        warning_frame = tk.Frame(content_frame, bg="#fff3cd", relief="solid", borderwidth=1)
                        warning_frame.pack(fill="x", pady=3)
                        
                        tk.Label(
                            warning_frame,
                            text="SAFETY WARNINGS",
                            font=("Arial", 9, "bold"),
                            fg="#856404",
                            bg="#fff3cd"
                        ).pack(anchor="w", padx=5, pady=2)
                        
                        for warning in safety_info.get('warnings', [])[:2]:  # Show max 2 warnings
                            tk.Label(
                                warning_frame,
                                text=f"* {warning}",
                                font=("Arial", 8),
                                fg="#856404",
                                bg="#fff3cd",
                                wraplength=430,
                                justify="left",
                                anchor="w"
                            ).pack(anchor="w", padx=15, pady=1)
                    
                    # Precautions in compact format
                    if safety_info.get('precautions'):
                        precaution_frame = tk.Frame(content_frame, bg="#d4edda", relief="solid", borderwidth=1)
                        precaution_frame.pack(fill="x", pady=3)
                        
                        tk.Label(
                            precaution_frame,
                            text="KEY PRECAUTIONS",
                            font=("Arial", 9, "bold"),
                            fg="#155724",
                            bg="#d4edda"
                        ).pack(anchor="w", padx=5, pady=2)
                        
                        for precaution in safety_info.get('precautions', [])[:2]:  # Show max 2 precautions
                            tk.Label(
                                precaution_frame,
                                text=f"* {precaution}",
                                font=("Arial", 8),
                                fg="#155724",
                                bg="#d4edda",
                                wraplength=430,
                                justify="left",
                                anchor="w"
                            ).pack(anchor="w", padx=15, pady=1)
            
            # Pack canvas and scrollbar
            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
            
        except Exception as e:
            logger.error(f"Error displaying adjustments: {e}")
            messagebox.showerror("Display Error", f"An error occurred: {e}")


    
    def _get_chemical_adjustments_for_email(self, readings):
        """Get chemical adjustments formatted for email"""
        adjustments = []
        
        try:
            # Get current values
            ph = float(readings.get('ph', 0))
            fc = float(readings.get('free_chlorine', 0))
            alk = float(readings.get('alkalinity', 0))
            
            # Calculate adjustments
            if ph > 0 and ph < 7.2:
                amount = (7.4 - ph) * 4.5  # Rough calculation
                adjustments.append({
                    'chemical': 'pH Increaser (Soda Ash)',
                    'amount': f'{amount:.1f} oz',
                    'current': f'{ph:.1f}',
                    'target': '7.4',
                    'ideal_range': '7.2-7.6'
                })
            elif ph > 7.6:
                amount = (ph - 7.4) * 3.5
                adjustments.append({
                    'chemical': 'pH Decreaser (Muriatic Acid)',
                    'amount': f'{amount:.1f} oz',
                    'current': f'{ph:.1f}',
                    'target': '7.4',
                    'ideal_range': '7.2-7.6'
                })
            
            if fc > 0 and fc < 1.5:
                amount = (2.5 - fc) * 1.5
                adjustments.append({
                    'chemical': 'Chlorine (Liquid or Granular)',
                    'amount': f'{amount:.2f} oz',
                    'current': f'{fc:.1f} ppm',
                    'target': '2.5 ppm',
                    'ideal_range': '1.0-3.0 ppm'
                })
            
            if alk > 0 and alk < 80:
                amount = (100 - alk) * 0.1
                adjustments.append({
                    'chemical': 'Alkalinity Increaser (Sodium Bicarbonate)',
                    'amount': f'{amount:.1f} oz',
                    'current': f'{alk:.0f} ppm',
                    'target': '100 ppm',
                    'ideal_range': '80-120 ppm'
                })
            
        except Exception as e:
            logger.error(f"Error calculating adjustments for email: {e}")
        
        return adjustments

    def _save_readings(self):
        """Save current readings to history"""
        try:
            readings = self._get_readings_from_form()
            if not readings:
                return

            # Add date and time fields for analytics compatibility
            now = datetime.now()
            readings['date'] = now.strftime('%Y-%m-%d')
            readings['time'] = now.strftime('%H:%M:%S')
            readings['timestamp'] = now.isoformat()

            self.chemical_readings.append(readings)

            save_data = {'timestamp': now.isoformat(), 'readings': self.chemical_readings}

            if save_json(save_data, self.readings_file):
                self.status_var.set("Readings saved successfully")
                self._update_status("Readings saved successfully")
                self._refresh_analytics_dashboard()
                # Update pool health display with saved readings
                self._update_pool_health_display(readings)
                # Check for safety alerts
                self._check_safety_alerts()  # SPEED FIX: No delay, run immediately
                
                # Refresh Alert History tab if it exists
                if hasattr(self, 'alerts_tree'):
                    self.after(100, self._update_alerts_history_table)  # Refresh after 100ms
                self._save_to_database(readings)
                
                # Send notification for readings saved
                health_score = self._calculate_pool_health_score(readings)
                # Get safety alerts and adjustments for email
                alerts = self._get_safety_alerts_for_email(readings)
                adjustments = self._get_chemical_adjustments_for_email(readings)
                
                # Send enhanced notification (Option B)
                self._send_notification('readings_saved', {
                    'readings': readings,
                    'health_score': health_score,
                    'alerts': alerts,
                    'adjustments': adjustments
                })
            else:
                self.status_var.set("Failed to save readings")
                self._update_status("Failed to save readings")

        except Exception as e:
            logger.error(f"Error saving readings: {str(e)}")
            messagebox.showerror("Save Error", f"An error occurred: {str(e)}")
            self.status_var.set("Save failed")
            self._update_status("Save failed")


    def _save_to_database(self, readings):
        """Save readings to database"""
        try:
            temperature = readings.get('temperature', 0)
            ph = readings.get('ph', 0)
            chlorine = readings.get('free_chlorine', 0)  # Or total_chlorine as needed
            self.data_manager.insert_reading(temperature, ph, chlorine)
            logger.info("Readings saved to database")
        except Exception as e:
            logger.error(f"Error saving to database: {str(e)}")
            messagebox.showerror("Database Error", f"An error occurred saving to the database: {str(e)}")


    def _clear_readings(self):
        """Clear all reading inputs"""
        for field, entry in self.entries.items():
            if field not in ['customer_name', 'pool_size']:
                entry.delete(0, "end")
        # Clear adjustments frame
        if hasattr(self, 'adjustments_frame') and self.adjustments_frame:
            for widget in self.adjustments_frame.winfo_children():
                widget.destroy()
        self.status_var.set("Readings cleared")
        self._update_status("Readings cleared")
    
    def _scan_test_strip(self):
        """Scan test strip using camera"""
        if not self.test_strip_analyzer:
            messagebox.showerror("Error", "Test strip analyzer not available")
            return
        
        try:
            self.status_var.set("Opening camera...")
            
            # Capture image from camera
            results = self.test_strip_analyzer.analyze_camera()
            
            if not results or 'error' in results:
                error_msg = results.get('error', 'Unknown error') if results else 'Failed to capture image'
                messagebox.showerror("Camera Error", f"Failed to capture image from camera.\n\nError: {error_msg}\n\nPlease check:\n- Camera is connected\n- Camera permissions are granted\n- No other app is using the camera")
                self.status_var.set("Camera capture failed")
                return
            
            # Populate fields with results
            self._populate_fields_from_results(results)
            self.status_var.set("Camera capture successful")
            
        except Exception as e:
            logger.error(f"Error scanning test strip: {e}")
            messagebox.showerror("Error", f"Failed to scan test strip:\n{str(e)}")
            self.status_var.set("Scan failed")
    
    def _upload_test_strip_image(self):
        """Upload test strip image from file"""
        if not self.test_strip_analyzer:
            messagebox.showerror("Error", "Test strip analyzer not available")
            return
        
        try:
            # Open file dialog
            from tkinter import filedialog
            file_path = filedialog.askopenfilename(
                title="Select Test Strip Image",
                filetypes=[
                    ("Image files", "*.jpg *.jpeg *.png *.bmp"),
                    ("All files", "*.*")
                ]
            )
            
            if not file_path:
                return  # User cancelled
            
            self.status_var.set("Loading image...")
            
            # Load and analyze image
            results = self.test_strip_analyzer.analyze_image(file_path)
            
            if not results or 'error' in results:
                error_msg = results.get('error', 'Unknown error') if results else 'Failed to load image'
                messagebox.showerror("Error", f"Failed to load image:\n{file_path}\n\nError: {error_msg}")
                self.status_var.set("Image load failed")
                return
            
            # Populate fields with results
            self._populate_fields_from_results(results)
            self.status_var.set(f"Image loaded: {os.path.basename(file_path)}")
            
        except Exception as e:
            logger.error(f"Error uploading test strip image: {e}")
            messagebox.showerror("Error", f"Failed to upload image:\n{str(e)}")
            self.status_var.set("Upload failed")
    
    def _process_test_strip_image(self, image, source_name):
        """Process test strip image and extract values"""
        try:
            self.status_var.set("Analyzing test strip...")
            
            # Analyze the strip
            results = self.test_strip_analyzer.analyze_strip(image)
            
            if not results:
                messagebox.showwarning("Analysis Failed", "Could not detect test strip in image.\n\nTips:\n- Ensure good lighting\n- Place strip on contrasting background\n- Keep strip horizontal\n- Avoid shadows")
                self.status_var.set("Analysis failed")
                return
            
            # Show results dialog
            self._show_test_strip_results(results, source_name)
            
        except Exception as e:
            logger.error(f"Error processing test strip image: {e}")
            messagebox.showerror("Error", f"Failed to process image:\n{str(e)}")
            self.status_var.set("Processing failed")
    
    def _show_test_strip_results(self, results, source_name):
        """Show test strip analysis results and allow user to accept/reject"""
        # Create results dialog
        dialog = tk.Toplevel(self)
        dialog.title("Test Strip Analysis Results")
        dialog.geometry("600x500")
        dialog.transient(self)
        dialog.grab_set()
        
        # Title
        title_frame = tk.Frame(dialog, bg="#3498db", height=60)
        title_frame.pack(fill="x")
        title_frame.pack_propagate(False)
        
        tk.Label(
            title_frame,
            text="Test Strip Analysis Results",
            font=("Arial", 14, "bold"),
            fg="white",
            bg="#3498db"
        ).pack(pady=15)
        
        # Source info
        info_frame = tk.Frame(dialog, bg="#e8f5e9")
        info_frame.pack(fill="x", padx=10, pady=5)
        
        tk.Label(
            info_frame,
            text=f"Source: {source_name}",
            font=("Arial", 10),
            bg="#e8f5e9"
        ).pack(pady=5)
        
        # Results table
        results_frame = ttk.Frame(dialog)
        results_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create scrollable frame
        canvas = tk.Canvas(results_frame)
        scrollbar = ttk.Scrollbar(results_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Headers
        headers = ["Parameter", "Value", "Confidence", "Status"]
        for col, header in enumerate(headers):
            tk.Label(
                scrollable_frame,
                text=header,
                font=("Arial", 10, "bold"),
                bg="#ecf0f1",
                relief="solid",
                borderwidth=1,
                width=15
            ).grid(row=0, column=col, sticky="ew", padx=1, pady=1)
        
        # Parameter mapping
        param_names = {
            'ph': 'pH',
            'free_chlorine': 'Free Chlorine',
            'total_chlorine': 'Total Chlorine',
            'alkalinity': 'Alkalinity',
            'calcium_hardness': 'Calcium Hardness',
            'cyanuric_acid': 'Cyanuric Acid'
        }
        
        # Results rows
        row = 1
        for param, data in results.items():
            value = data['value']
            confidence = data['confidence']
            confidence_level = self.test_strip_analyzer.get_confidence_level(confidence)
            
            # Determine status color
            if confidence >= 0.8:
                status_color = "#27ae60"  # Green
                status_text = "Good"
            elif confidence >= 0.6:
                status_color = "#f39c12"  # Orange
                status_text = "Fair"
            else:
                status_color = "#e74c3c"  # Red
                status_text = "Low"
            
            # Parameter name
            tk.Label(
                scrollable_frame,
                text=param_names.get(param, param),
                font=("Arial", 10),
                relief="solid",
                borderwidth=1,
                width=15
            ).grid(row=row, column=0, sticky="ew", padx=1, pady=1)
            
            # Value
            tk.Label(
                scrollable_frame,
                text=f"{value:.2f}",
                font=("Arial", 10, "bold"),
                relief="solid",
                borderwidth=1,
                width=15
            ).grid(row=row, column=1, sticky="ew", padx=1, pady=1)
            
            # Confidence
            tk.Label(
                scrollable_frame,
                text=f"{confidence:.0%} ({confidence_level})",
                font=("Arial", 10),
                relief="solid",
                borderwidth=1,
                width=15
            ).grid(row=row, column=2, sticky="ew", padx=1, pady=1)
            
            # Status
            tk.Label(
                scrollable_frame,
                text=status_text,
                font=("Arial", 10, "bold"),
                fg=status_color,
                relief="solid",
                borderwidth=1,
                width=15
            ).grid(row=row, column=3, sticky="ew", padx=1, pady=1)
            
            row += 1
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Warning message
        warning_frame = tk.Frame(dialog, bg="#fff3cd")
        warning_frame.pack(fill="x", padx=10, pady=5)
        
        tk.Label(
            warning_frame,
            text="Review values carefully. Low confidence readings should be verified manually.",
            font=("Arial", 9),
            bg="#fff3cd",
            fg="#856404",
            wraplength=550
        ).pack(pady=5)
        
        # Buttons
        button_frame = ttk.Frame(dialog)
        button_frame.pack(fill="x", padx=10, pady=10)
        
        def accept_values():
            """Accept and populate form with values"""
            # Populate form fields
            field_mapping = {
                'ph': 'ph',
                'free_chlorine': 'free_chlorine',
                'total_chlorine': 'total_chlorine',
                'alkalinity': 'alkalinity',
                'calcium_hardness': 'calcium_hardness',
                'cyanuric_acid': 'cyanuric_acid'
            }
            
            for param, field_name in field_mapping.items():
                if param in results and field_name in self.entries:
                    value = results[param]['value']
                    self.entries[field_name].delete(0, "end")
                    self.entries[field_name].insert(0, f"{value:.2f}")
            
            self.status_var.set("Test strip values loaded successfully")
            messagebox.showinfo("Success", "Test strip values have been loaded into the form.\n\nYou can now calculate adjustments or modify values as needed.")
            dialog.destroy()
        
        def reject_values():
            """Reject and close dialog"""
            self.status_var.set("Test strip analysis cancelled")
            dialog.destroy()
        
        ttk.Button(
            button_frame,
            text="Accept and Populate Form",
            command=accept_values
        ).pack(side="left", padx=5)
        
        ttk.Button(
            button_frame,
            text="Cancel",
            command=reject_values
        ).pack(side="left", padx=5)
        
        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")


    def _show_test_strip_tips(self):
        """Show tips for scanning test strips"""
        tips_text = """Test Strip Scanning Tips

[PHOTO] Camera Scanning:
* Use good lighting (natural light is best)
* Hold strip steady and flat
* Fill the frame with the test strip
* Avoid shadows and glare
* Wait 15 seconds after dipping strip

[SEND] Image Upload:
* Use clear, well-lit photos
* Ensure strip is in focus
* Avoid blurry or dark images
* JPEG or PNG format works best

Best Results:
* Scan immediately after color develops
* Keep strip horizontal
* Use white background if possible
* Ensure all color pads are visible
* Compare with color chart if uncertain

Important:
* Low confidence readings should be verified manually
* Always double-check critical parameters
* Recalibrate if results seem incorrect"""
        
        messagebox.showinfo("Test Strip Scanning Tips", tips_text)








    def _create_notifications_tab(self):
        """Create the notifications and settings tab."""
        # Create main container with scrollbar
        canvas = tk.Canvas(self.notifications_tab, bg='white')
        scrollbar = ttk.Scrollbar(self.notifications_tab, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Title
        title_frame = ttk.Frame(scrollable_frame)
        title_frame.pack(fill=tk.X, padx=20, pady=20)
        
        title_label = ttk.Label(
            title_frame,
            text="Notifications & Settings",
            font=('Arial', 18, 'bold')
        )
        title_label.pack(side=tk.LEFT)
        
        # Status indicator
        if self.messaging_enabled:
            status_text = "Service Active"
            status_color = "green"
        else:
            status_text = "Service Unavailable"
            status_color = "red"
        
        status_label = ttk.Label(
            title_frame,
            text=status_text,
            foreground=status_color,
            font=('Arial', 10, 'bold')
        )
        status_label.pack(side=tk.RIGHT)
        
        if not self.messaging_enabled:
            # Show error message if service not available
            error_frame = ttk.LabelFrame(scrollable_frame, text="Service Status", padding=15)
            error_frame.pack(fill=tk.X, padx=20, pady=10)
            
            error_label = ttk.Label(
                error_frame,
                text="Messaging service is not available. Please check that messaging_service.py is in the same directory.",
                foreground="red",
                wraplength=700
            )
            error_label.pack()
            return
        
        # Email Configuration Section
        email_frame = ttk.LabelFrame(scrollable_frame, text="Email Configuration", padding=15)
        email_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Email enabled checkbox
        self.email_enabled_var = tk.BooleanVar(value=self.messaging_service.config.get('email', {}).get('enabled', False))
        email_enabled_cb = ttk.Checkbutton(
            email_frame,
            text="Enable Email Notifications",
            variable=self.email_enabled_var
        )
        email_enabled_cb.grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # SMTP Server
        ttk.Label(email_frame, text="SMTP Server:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.smtp_server_var = tk.StringVar(value=self.messaging_service.config.get('email', {}).get('smtp_server', 'smtp.gmail.com'))
        smtp_entry = ttk.Entry(email_frame, textvariable=self.smtp_server_var, width=40)
        smtp_entry.grid(row=1, column=1, sticky=tk.W, pady=5, padx=5)
        
        # SMTP Port
        ttk.Label(email_frame, text="SMTP Port:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.smtp_port_var = tk.StringVar(value=str(self.messaging_service.config.get('email', {}).get('smtp_port', 587)))
        port_entry = ttk.Entry(email_frame, textvariable=self.smtp_port_var, width=40)
        port_entry.grid(row=2, column=1, sticky=tk.W, pady=5, padx=5)
        
        # Username
        ttk.Label(email_frame, text="Username/Email:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.smtp_username_var = tk.StringVar(value=self.messaging_service.config.get('email', {}).get('username', ''))
        username_entry = ttk.Entry(email_frame, textvariable=self.smtp_username_var, width=40)
        username_entry.grid(row=3, column=1, sticky=tk.W, pady=5, padx=5)
        
        # Password
        ttk.Label(email_frame, text="Password:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.smtp_password_var = tk.StringVar(value=self.messaging_service.config.get('email', {}).get('password', ''))
        password_entry = ttk.Entry(email_frame, textvariable=self.smtp_password_var, width=40, show="*")
        password_entry.grid(row=4, column=1, sticky=tk.W, pady=5, padx=5)
        
        # From Email
        ttk.Label(email_frame, text="From Email:").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.from_email_var = tk.StringVar(value=self.messaging_service.config.get('email', {}).get('from_address', ''))
        from_entry = ttk.Entry(email_frame, textvariable=self.from_email_var, width=40)
        from_entry.grid(row=5, column=1, sticky=tk.W, pady=5, padx=5)
        
        # To Emails
        ttk.Label(email_frame, text="To Emails (comma-separated):").grid(row=6, column=0, sticky=tk.W, pady=5)
        to_emails = ', '.join(self.messaging_service.config.get('email', {}).get('recipients', []))
        self.to_emails_var = tk.StringVar(value=to_emails)
        to_entry = ttk.Entry(email_frame, textvariable=self.to_emails_var, width=40)
        to_entry.grid(row=6, column=1, sticky=tk.W, pady=5, padx=5)
        
        # Test Email Button
        test_email_btn = ttk.Button(
            email_frame,
            text="Send Test Email",
            command=self._test_email
        )
        test_email_btn.grid(row=7, column=1, sticky=tk.W, pady=10, padx=5)
        
        # Help text for Gmail
        help_text = ttk.Label(
            email_frame,
            text="For Gmail: Use 'smtp.gmail.com' and port 587. You'll need an App Password (not your regular password).\nGo to Google Account > Security > 2-Step Verification > App Passwords to create one.",
            foreground="gray",
            wraplength=600,
            font=('Arial', 8)
        )
        help_text.grid(row=8, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # SMS Configuration Section
        sms_frame = ttk.LabelFrame(scrollable_frame, text="SMS Configuration (Twilio)", padding=15)
        sms_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # SMS enabled checkbox
        self.sms_enabled_var = tk.BooleanVar(value=self.messaging_service.config.get('sms', {}).get('enabled', False))
        sms_enabled_cb = ttk.Checkbutton(
            sms_frame,
            text="Enable SMS Notifications",
            variable=self.sms_enabled_var
        )
        sms_enabled_cb.grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # Twilio Account SID
        ttk.Label(sms_frame, text="Twilio Account SID:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.twilio_sid_var = tk.StringVar(value=self.messaging_service.config.get('sms', {}).get('account_sid', ''))
        sid_entry = ttk.Entry(sms_frame, textvariable=self.twilio_sid_var, width=40)
        sid_entry.grid(row=1, column=1, sticky=tk.W, pady=5, padx=5)
        
        # Twilio Auth Token
        ttk.Label(sms_frame, text="Twilio Auth Token:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.twilio_token_var = tk.StringVar(value=self.messaging_service.config.get('sms', {}).get('auth_token', ''))
        token_entry = ttk.Entry(sms_frame, textvariable=self.twilio_token_var, width=40, show="*")
        token_entry.grid(row=2, column=1, sticky=tk.W, pady=5, padx=5)
        
        # Twilio Phone Number
        ttk.Label(sms_frame, text="Twilio Phone Number:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.twilio_phone_var = tk.StringVar(value=self.messaging_service.config.get('sms', {}).get('from_number', ''))
        phone_entry = ttk.Entry(sms_frame, textvariable=self.twilio_phone_var, width=40)
        phone_entry.grid(row=3, column=1, sticky=tk.W, pady=5, padx=5)
        
        # To Phone Numbers
        ttk.Label(sms_frame, text="To Phone Numbers (comma-separated):").grid(row=4, column=0, sticky=tk.W, pady=5)
        to_phones = ', '.join(self.messaging_service.config.get('sms', {}).get('recipients', []))
        self.to_phones_var = tk.StringVar(value=to_phones)
        to_phones_entry = ttk.Entry(sms_frame, textvariable=self.to_phones_var, width=40)
        to_phones_entry.grid(row=4, column=1, sticky=tk.W, pady=5, padx=5)
        
        # Test SMS Button
        test_sms_btn = ttk.Button(
            sms_frame,
            text="Send Test SMS",
            command=self._test_sms
        )
        test_sms_btn.grid(row=5, column=1, sticky=tk.W, pady=10, padx=5)
        
        # Help text for Twilio
        twilio_help = ttk.Label(
            sms_frame,
            text="Sign up for Twilio at twilio.com. You'll get a free trial with $15 credit.\nPhone numbers must include country code (e.g., +1234567890).",
            foreground="gray",
            wraplength=600,
            font=('Arial', 8)
        )
        twilio_help.grid(row=6, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # Notification Preferences Section
        prefs_frame = ttk.LabelFrame(scrollable_frame, text="Notification Preferences", padding=15)
        prefs_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.notify_critical_var = tk.BooleanVar(value=self.messaging_service.config.get('notifications', {}).get('critical_alerts', True))
        ttk.Checkbutton(
            prefs_frame,
            text="Critical Alerts (DO NOT SWIM conditions)",
            variable=self.notify_critical_var
        ).grid(row=0, column=0, sticky=tk.W, pady=5)
        
        self.notify_warning_var = tk.BooleanVar(value=self.messaging_service.config.get('notifications', {}).get('warning_alerts', True))
        ttk.Checkbutton(
            prefs_frame,
            text="Warning Alerts (Needs attention)",
            variable=self.notify_warning_var
        ).grid(row=1, column=0, sticky=tk.W, pady=5)
        
        self.notify_readings_var = tk.BooleanVar(value=self.messaging_service.config.get('notify_readings_saved', False))
        ttk.Checkbutton(
            prefs_frame,
            text="Readings Saved (Every time you save a reading)",
            variable=self.notify_readings_var
        ).grid(row=2, column=0, sticky=tk.W, pady=5)
        
        self.notify_adjustments_var = tk.BooleanVar(value=self.messaging_service.config.get('notifications', {}).get('chemical_adjustments', True))
        ttk.Checkbutton(
            prefs_frame,
            text="Chemical Adjustments Recommended",
            variable=self.notify_adjustments_var
        ).grid(row=3, column=0, sticky=tk.W, pady=5)
        
        # Pool Name Section
        pool_frame = ttk.LabelFrame(scrollable_frame, text="Pool Information", padding=15)
        pool_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.include_pool_name_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            pool_frame,
            text="Include pool name in notifications",
            variable=self.include_pool_name_var
        ).grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        ttk.Label(pool_frame, text="Pool Name:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.pool_name_var = tk.StringVar(value=self.messaging_service.config.get('pool_name', 'My Pool'))
        pool_name_entry = ttk.Entry(pool_frame, textvariable=self.pool_name_var, width=40)
        pool_name_entry.grid(row=1, column=1, sticky=tk.W, pady=5, padx=5)
        
        # Save Button
        button_frame = ttk.Frame(scrollable_frame)
        button_frame.pack(fill=tk.X, padx=20, pady=20)
        
        save_btn = ttk.Button(
            button_frame,
            text="Save All Settings",
            command=self._save_notification_settings
        )
        save_btn.pack(side=tk.LEFT, padx=5)
        
        reset_btn = ttk.Button(
            button_frame,
            text="Reset to Defaults",
            command=self._reset_notification_settings
        )
        reset_btn.pack(side=tk.LEFT, padx=5)
    
    def _test_email(self):
        """Send a test email."""
        if not self.messaging_enabled:
            messagebox.showerror("Error", "Messaging service is not available")
            return
        
        # Save current settings first
        self._save_notification_settings()
        
        # Send test email
        success, message = self.messaging_service.test_email()
        
        if success:
            messagebox.showinfo("Success", "Test email sent successfully! Check your inbox.")
        else:
            messagebox.showerror("Error", f"Failed to send test email:\n\n{message}")
    
    def _test_sms(self):
        """Send a test SMS."""
        if not self.messaging_enabled:
            messagebox.showerror("Error", "Messaging service is not available")
            return
        
        # Save current settings first
        self._save_notification_settings()
        
        # Send test SMS
        success, message = self.messaging_service.test_sms()
        
        if success:
            messagebox.showinfo("Success", "Test SMS sent successfully! Check your phone.")
        else:
            messagebox.showerror("Error", f"Failed to send test SMS:\n\n{message}")
    
    def _save_notification_settings(self):
        """Save notification settings to config file."""
        if not self.messaging_enabled:
            return
        
        try:
            # Parse email list
            to_emails = [email.strip() for email in self.to_emails_var.get().split(',') if email.strip()]
            
            # Parse phone list
            to_phones = [phone.strip() for phone in self.to_phones_var.get().split(',') if phone.strip()]
            
            # Create config dictionary in the CORRECT structure for messaging_service
            config = {
                'email': {
                    'enabled': self.email_enabled_var.get(),
                    'smtp_server': self.smtp_server_var.get(),
                    'smtp_port': int(self.smtp_port_var.get()),
                    'username': self.smtp_username_var.get(),
                    'password': self.smtp_password_var.get(),
                    'from_address': self.from_email_var.get(),
                    'recipients': to_emails
                },
                'sms': {
                    'enabled': self.sms_enabled_var.get(),
                    'account_sid': self.twilio_sid_var.get(),
                    'auth_token': self.twilio_token_var.get(),
                    'from_number': self.twilio_phone_var.get(),
                    'recipients': to_phones
                },
                'notifications': {
                    'critical_alerts': self.notify_critical_var.get(),
                    'warning_alerts': self.notify_warning_var.get(),
                    'readings_saved': self.notify_readings_var.get(),
                    'chemical_adjustments': self.notify_adjustments_var.get()
                },
                'pool_name': self.pool_name_var.get()
            }
            
            # Save config
            if self.messaging_service.save_config(config):
                messagebox.showinfo("Success", "Settings saved successfully!")
            else:
                messagebox.showerror("Error", "Failed to save settings")
                
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid port number: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"Error saving settings: {e}")
    
    def _reset_notification_settings(self):
        """Reset notification settings to defaults."""
        if not self.messaging_enabled:
            return
        
        if messagebox.askyesno("Confirm Reset", "Are you sure you want to reset all notification settings to defaults?"):
            # Reset to defaults
            default_config = self.messaging_service._default_config()
            self.messaging_service.save_config(default_config)
            
            # Reload the tab
            for widget in self.notifications_tab.winfo_children():
                widget.destroy()
            self._create_notifications_tab()
            
            messagebox.showinfo("Success", "Settings reset to defaults")
    

    def _get_safety_alerts_for_email(self, reading):
        """Get safety alerts for email notification"""
        alerts = {
            'critical': [],
            'warnings': []
        }
        
        # Check pH
        ph = reading.get('ph')
        if ph is not None:
            if ph < 6.8 or ph > 8.2:
                alerts['critical'].append(f"pH is unsafe ({ph:.1f}) - DO NOT SWIM")
            elif ph < 7.0 or ph > 8.0:
                alerts['warnings'].append(f"pH is outside ideal range ({ph:.1f})")
        
        # Check Free Chlorine
        fc = reading.get('free_chlorine')
        if fc is not None:
            if fc < 0.5 or fc > 5.0:
                alerts['critical'].append(f"Free chlorine is unsafe ({fc:.1f} ppm) - DO NOT SWIM")
            elif fc < 1.0 or fc > 4.0:
                alerts['warnings'].append(f"Free chlorine outside ideal range ({fc:.1f} ppm)")
        
        # Check Cyanuric Acid
        cya = reading.get('cyanuric_acid')
        if cya is not None:
            if cya > 100:
                alerts['critical'].append(f"Cyanuric acid too high ({cya:.0f} ppm) - DO NOT SWIM")
            elif cya > 80:
                alerts['warnings'].append(f"Cyanuric acid elevated ({cya:.0f} ppm)")
        
        # Check Temperature
        temp = reading.get('temperature')
        if temp is not None:
            if temp > 104:
                alerts['critical'].append(f"Water temperature too hot ({temp:.0f}F) - DO NOT SWIM")
            elif temp > 95:
                alerts['warnings'].append(f"Water temperature high ({temp:.0f}F)")
        
        # Check Alkalinity
        alk = reading.get('alkalinity')
        if alk is not None:
            if alk < 60 or alk > 180:
                alerts['warnings'].append(f"Alkalinity outside ideal range ({alk:.0f} ppm)")
        
        # Check ORP
        orp = reading.get('orp')
        if orp is not None:
            if orp < 650 or orp > 800:
                alerts['critical'].append(f"ORP outside safe range ({orp:.0f} mV) - DO NOT SWIM")
        
        return alerts
    
    def _get_chemical_adjustments_for_email(self, reading):
        """Get chemical adjustments for email notification"""
        adjustments = []
        
        # pH adjustments
        ph = reading.get('ph')
        if ph is not None:
            if ph < 7.2:
                amount = (7.4 - ph) * 1.5
                adjustments.append({
                    'chemical': 'pH Increaser (Soda Ash)',
                    'action': 'Add',
                    'amount': f'{amount:.1f} lbs',
                    'reason': f'pH is low ({ph:.1f})',
                    'warnings': [
                        'Do not add more than 2 lbs at once',
                        'Wait 4 hours before retesting'
                    ],
                    'precautions': [
                        'Wear protective gloves',
                        'Keep pool pump running during treatment'
                    ]
                })
            elif ph > 7.6:
                amount = (ph - 7.4) * 1.2
                adjustments.append({
                    'chemical': 'pH Decreaser (Muriatic Acid)',
                    'action': 'Add',
                    'amount': f'{amount:.1f} lbs',
                    'reason': f'pH is high ({ph:.1f})',
                    'warnings': [
                        'Highly corrosive - handle with extreme care',
                        'Never mix with other chemicals'
                    ],
                    'precautions': [
                        'Wear safety goggles and gloves',
                        'Add slowly near return jets'
                    ]
                })
        
        # Chlorine adjustments
        fc = reading.get('free_chlorine')
        if fc is not None and fc < 1.5:
            amount = (2.0 - fc) * 0.3
            adjustments.append({
                'chemical': 'Liquid Chlorine (12.5%)',
                'action': 'Add',
                'amount': f'{amount:.1f} gallons',
                'reason': f'Free chlorine is low ({fc:.1f} ppm)',
                'warnings': [
                    'Do not mix with other chemicals',
                    'Add slowly to avoid splashing'
                ],
                'precautions': [
                    'Add near return jets',
                    'Keep away from children and pets'
                ]
            })
        
        # Alkalinity adjustments
        alk = reading.get('alkalinity')
        if alk is not None:
            if alk < 80:
                amount = (100 - alk) * 0.15
                adjustments.append({
                    'chemical': 'Alkalinity Increaser (Sodium Bicarbonate)',
                    'action': 'Add',
                    'amount': f'{amount:.1f} lbs',
                    'reason': f'Alkalinity is low ({alk:.0f} ppm)',
                    'warnings': [
                        'May temporarily cloud water',
                        'Wait 6 hours before retesting'
                    ],
                    'precautions': [
                        'Dissolve in bucket of water first',
                        'Pour around pool perimeter'
                    ]
                })
            elif alk > 120:
                adjustments.append({
                    'chemical': 'pH Decreaser (Muriatic Acid)',
                    'action': 'Add',
                    'amount': '0.5 lbs',
                    'reason': f'Alkalinity is high ({alk:.0f} ppm)',
                    'warnings': [
                        'Will also lower pH',
                        'Highly corrosive'
                    ],
                    'precautions': [
                        'Wear safety goggles and gloves',
                        'Add slowly near return jets'
                    ]
                })
        
        # Calcium Hardness adjustments
        ch = reading.get('calcium_hardness')
        if ch is not None and ch < 200:
            amount = (250 - ch) * 0.01
            adjustments.append({
                'chemical': 'Calcium Hardness Increaser',
                'action': 'Add',
                'amount': f'{amount:.1f} lbs',
                'reason': f'Calcium hardness is low ({ch:.0f} ppm)',
                'warnings': [
                    'May temporarily cloud water',
                    'Wait 24 hours before retesting'
                ],
                'precautions': [
                    'Dissolve in bucket first',
                    'Add slowly with pump running'
                ]
            })
        
        return adjustments

    def _send_notification(self, notification_type: str, data: dict):
        """Send a notification via configured channels."""
        if not self.messaging_enabled:
            return
        
        try:
            result = self.messaging_service.send_notification(notification_type, data)
            
            # Check if notification was successful
            if result.get('success'):
                print(f"Notification sent successfully")
                
                # Log individual channel results if available
                if 'results' in result:
                    for channel, channel_result in result['results'].items():
                        if channel_result:
                            if channel_result.get('success'):
                                print(f"  {channel}: {channel_result.get('message', 'Success')}")
                            else:
                                print(f"  [FAILED] {channel}: {channel_result.get('message', 'Failed')}")
            else:
                print(f"[INFO] {result.get('message', 'Notification not sent')}")
                    
        except (ConnectionError, TimeoutError, ValueError, KeyError, AttributeError) as e:
            print(f"Error sending notification: {e}")
            import traceback
            traceback.print_exc()


    def _save_settings(self):
        """Save application settings"""
        try:
            settings = {
                'theme': 'clam',
                'auto_backup': self.auto_backup_var.get()
            }
            save_json(settings, self.settings_file)
            self.status_var.set("Settings saved successfully")
            self._update_status("Settings saved successfully")
        except Exception as e:
            logger.error(f"Error saving settings: {str(e)}")
            messagebox.showerror("Save Error", f"An error occurred: {str(e)}")


    def _backup_data(self):
        """Create a backup of all data files"""
        try:
            backup_dir = self.data_dir / "backups"
            backup_dir.mkdir(exist_ok=True)
            backup_file = backup_dir / f"backup_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.zip"
            with zipfile.ZipFile(backup_file, 'w') as zip_file:
                for file in self.data_dir.glob('*'):
                    if file.is_file():
                        zip_file.write(file, arcname=file.name)
            self.status_var.set(f"Backup created at {backup_file}")
            self._update_status(f"Backup created at {backup_file}")
            logger.info(f"Backup created at {backup_file}")
        except Exception as e:
            logger.error(f"Error creating backup: {str(e)}")
            messagebox.showerror("Backup Error", f"An error occurred: {str(e)}")



    def _save_alert_to_history(self, parameter, value, threshold_min, threshold_max, message, severity='warning'):
        """Save alert to history database with Phase 1.2 enhancements"""
        try:
            from datetime import datetime
            import uuid
            
            # Get pool name
            pool_name = "Unknown Pool"
            if hasattr(self, 'active_pool_id') and self.active_pool_id:
                pool_data = self._get_pool_data(self.active_pool_id)
                if pool_data:
                    pool_name = pool_data.get('name', 'Unknown Pool')
            
            # Create alert record with Phase 1.2 fields
            alert = {
                'alert_id': str(uuid.uuid4()),
                'pool_id': self.active_pool_id if hasattr(self, 'active_pool_id') else 'default',
                'pool_name': pool_name,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'parameter': parameter,
                'value': value,
                'threshold_min': threshold_min,
                'threshold_max': threshold_max,
                'message': message,
                'severity': severity,
                'status': 'unacknowledged',
                'acknowledged_at': None,
                'acknowledged_by': None,
                'snoozed_until': None,
                'dismissed': False,
                'dismissed_at': None,
                'notes': ''
            }
            
            # Load existing alerts
            alerts_file = self.data_dir / "alerts.json"
            if alerts_file.exists():
                with open(alerts_file, 'r') as f:
                    alerts = json.load(f)
            else:
                alerts = []
            
            # Add new alert
            alerts.append(alert)
            
            # Keep only last 1000 alerts
            if len(alerts) > 1000:
                alerts = alerts[-1000:]
            
            # Save to file
            with open(alerts_file, 'w') as f:
                json.dump(alerts, f, indent=2)
            
            logger.info(f"Alert saved to history: {alert['alert_id']} - {severity} - {parameter}")
            
        except Exception as e:
            logger.error(f"Error saving alert to history: {e}")


    def _load_alert_history(self, pool_id=None, days=30):
        """Load alert history from database"""
        try:
            from datetime import datetime, timedelta
            
            alerts_file = self.data_dir / "alerts.json"
            if not alerts_file.exists():
                return []
            
            with open(alerts_file, 'r') as f:
                all_alerts = json.load(f)
            
            # Filter by pool
            if pool_id:
                all_alerts = [a for a in all_alerts if a.get('pool_id') == pool_id]
            else:
                # Filter by active pool, but if no active_pool_id, show all
                if hasattr(self, 'active_pool_id') and self.active_pool_id:
                    all_alerts = [a for a in all_alerts if a.get('pool_id') == self.active_pool_id]
                # If no pool filtering possible, show all alerts
                logger.info(f"Filtering alerts by pool: {self.active_pool_id if hasattr(self, 'active_pool_id') else 'ALL'}")
            
            # Filter by date range
            if days:
                cutoff_date = datetime.now() - timedelta(days=days)
                filtered_alerts = []
                for a in all_alerts:
                    try:
                        # Try standard format first
                        timestamp = datetime.strptime(a['timestamp'], '%Y-%m-%d %H:%M:%S')
                    except ValueError:
                        try:
                            # Try ISO format (for old alerts)
                            timestamp = datetime.fromisoformat(a['timestamp'])
                        except ValueError:
                            # Skip alerts with invalid timestamps
                            continue
                    
                    if timestamp >= cutoff_date:
                        filtered_alerts.append(a)
                
                all_alerts = filtered_alerts
            
            # Sort by timestamp (newest first)
            all_alerts.sort(key=lambda x: x['timestamp'], reverse=True)
            
            return all_alerts
            
        except Exception as e:
            logger.error(f"Error loading alert history: {e}")
            return []


    def _create_alerts_history_tab(self):
        """Create the Alert History tab"""
        self.alerts_history_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.alerts_history_tab, text="Alert History")
        
        # Main container
        main_frame = ttk.Frame(self.alerts_history_tab)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Label(
            header_frame,
            text="Alert History & Management",
            font=("Arial", 16, "bold")
        ).pack(side="left")
        
        # Controls
        controls_frame = ttk.Frame(header_frame)
        controls_frame.pack(side="right")
        
        ttk.Button(
            controls_frame,
            text="Refresh",
            command=self._update_alerts_history_table
        ).pack(side="left", padx=2)
        
        ttk.Button(
            controls_frame,
            text="Export Report",
            command=self._export_alerts_report
        ).pack(side="left", padx=2)
        
        # Filter frame
        filter_frame = ttk.LabelFrame(main_frame, text="Filters", padding=10)
        filter_frame.pack(fill="x", pady=(0, 10))
        
        # Date range filter
        ttk.Label(filter_frame, text="Date Range:").grid(row=0, column=0, sticky="w", padx=5)
        self.alert_date_range_var = tk.StringVar(value="30")
        date_options = [
            ("Last 7 Days", "7"),
            ("Last 30 Days", "30"),
            ("Last 90 Days", "90"),
            ("All Time", "0")
        ]
        for i, (text, value) in enumerate(date_options):
            ttk.Radiobutton(
                filter_frame,
                text=text,
                variable=self.alert_date_range_var,
                value=value,
                command=self._update_alerts_history_table
            ).grid(row=0, column=i+1, padx=5)
        
        # Severity filter
        ttk.Label(filter_frame, text="Severity:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.alert_severity_var = tk.StringVar(value="all")
        severity_options = [
            ("All", "all"),
            ("Critical", "critical"),
            ("Warning", "warning")
        ]
        for i, (text, value) in enumerate(severity_options):
            ttk.Radiobutton(
                filter_frame,
                text=text,
                variable=self.alert_severity_var,
                value=value,
                command=self._update_alerts_history_table
            ).grid(row=1, column=i+1, padx=5)
        
        # Status filter
        ttk.Label(filter_frame, text="Status:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.alert_status_var = tk.StringVar(value="all")
        status_options = [
            ("All", "all"),
            ("Active", "active"),
            ("Resolved", "resolved")
        ]
        for i, (text, value) in enumerate(status_options):
            ttk.Radiobutton(
                filter_frame,
                text=text,
                variable=self.alert_status_var,
                value=value,
                command=self._update_alerts_history_table
            ).grid(row=2, column=i+1, padx=5)
        
        # Statistics frame
        stats_frame = ttk.LabelFrame(main_frame, text="Alert Statistics", padding=10)
        stats_frame.pack(fill="x", pady=(0, 10))
        
        self.alert_stats_labels = {}
        stats_items = [
            ("total", "Total Alerts:"),
            ("critical", "Critical:"),
            ("warning", "Warning:"),
            ("active", "Active:"),
            ("resolved", "Resolved:")
        ]
        
        for i, (key, label) in enumerate(stats_items):
            ttk.Label(stats_frame, text=label).grid(row=0, column=i*2, sticky="w", padx=5)
            self.alert_stats_labels[key] = ttk.Label(stats_frame, text="0", font=("Arial", 10, "bold"))
            self.alert_stats_labels[key].grid(row=0, column=i*2+1, sticky="w", padx=5)
        
        # Alerts table
        table_frame = ttk.Frame(main_frame)
        table_frame.pack(fill="both", expand=True)
        
        # Scrollbars
        y_scroll = ttk.Scrollbar(table_frame, orient="vertical")
        y_scroll.pack(side="right", fill="y")
        
        x_scroll = ttk.Scrollbar(table_frame, orient="horizontal")
        x_scroll.pack(side="bottom", fill="x")
        
        # Treeview
        columns = ("timestamp", "severity", "parameter", "value", "message", "status")
        self.alerts_tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            yscrollcommand=y_scroll.set,
            xscrollcommand=x_scroll.set,
            height=15
        )
        
        # Configure scrollbars
        y_scroll.config(command=self.alerts_tree.yview)
        x_scroll.config(command=self.alerts_tree.xview)
        
        # Column headings
        self.alerts_tree.heading("timestamp", text="Date/Time")
        self.alerts_tree.heading("severity", text="Severity")
        self.alerts_tree.heading("parameter", text="Parameter")
        self.alerts_tree.heading("value", text="Value")
        self.alerts_tree.heading("message", text="Message")
        self.alerts_tree.heading("status", text="Status")
        
        # Column widths
        self.alerts_tree.column("timestamp", width=150)
        self.alerts_tree.column("severity", width=80)
        self.alerts_tree.column("parameter", width=120)
        self.alerts_tree.column("value", width=80)
        self.alerts_tree.column("message", width=300)
        self.alerts_tree.column("status", width=80)
        
        self.alerts_tree.pack(fill="both", expand=True)
        
        # Action buttons
        action_frame = ttk.Frame(main_frame)
        action_frame.pack(fill="x", pady=(10, 0))
        
        ttk.Button(
            action_frame,
            text="Mark as Resolved",
            command=self._mark_alert_resolved
        ).pack(side="left", padx=5)
        
        ttk.Button(
            action_frame,
            text="Add Notes",
            command=self._add_alert_notes
        ).pack(side="left", padx=5)
        
        ttk.Button(
            action_frame,
            text="View Details",
            command=self._view_alert_details
        ).pack(side="left", padx=5)
        
        # Load initial data
        self._update_alerts_history_table()


    def _update_alerts_history_table(self):
        """Update the alerts history table"""
        try:
            # Safety check - ensure alerts_tree exists
            if not hasattr(self, 'alerts_tree'):
                logger.warning("alerts_tree not initialized yet")
                return
            
            # Clear existing items
            for item in self.alerts_tree.get_children():
                self.alerts_tree.delete(item)
            
            # Get filters
            days = int(self.alert_date_range_var.get()) if self.alert_date_range_var.get() != "0" else None
            severity_filter = self.alert_severity_var.get()
            status_filter = self.alert_status_var.get()
            
            # Load alerts
            alerts = self._load_alert_history(days=days)
            
            # Apply filters
            if severity_filter != "all":
                alerts = [a for a in alerts if a.get('severity') == severity_filter]
            
            if status_filter == "active":
                alerts = [a for a in alerts if not a.get('resolved', False)]
            elif status_filter == "resolved":
                alerts = [a for a in alerts if a.get('resolved', False)]
            
            # Update statistics
            total = len(alerts)
            critical = len([a for a in alerts if a.get('severity') == 'critical'])
            warning = len([a for a in alerts if a.get('severity') == 'warning'])
            active = len([a for a in alerts if not a.get('resolved', False)])
            resolved = len([a for a in alerts if a.get('resolved', False)])
            
            self.alert_stats_labels['total'].config(text=str(total))
            self.alert_stats_labels['critical'].config(text=str(critical))
            self.alert_stats_labels['warning'].config(text=str(warning))
            self.alert_stats_labels['active'].config(text=str(active))
            self.alert_stats_labels['resolved'].config(text=str(resolved))
            
            # Populate table
            for alert in alerts:
                status = "Resolved" if alert.get('resolved', False) else "Active"
                
                # Color code by severity
                tags = ()
                if alert.get('severity') == 'critical':
                    tags = ('critical',)
                elif alert.get('severity') == 'warning':
                    tags = ('warning',)
                
                self.alerts_tree.insert(
                    "",
                    "end",
                    values=(
                        alert.get('timestamp', ''),
                        alert.get('severity', '').upper(),
                        alert.get('parameter', ''),
                        f"{alert.get('value', 0):.1f}",
                        alert.get('message', ''),
                        status
                    ),
                    tags=tags
                )
            
            # Configure tags for color coding
            self.alerts_tree.tag_configure('critical', background='#ffcccc')
            self.alerts_tree.tag_configure('warning', background='#fff4cc')
            
        except Exception as e:
            logger.error(f"Error updating alerts history table: {e}")
            messagebox.showerror("Error", f"Failed to update alerts: {str(e)}")


    def _mark_alert_resolved(self):
        """Mark selected alert as resolved"""
        try:
            selection = self.alerts_tree.selection()
            if not selection:
                messagebox.showwarning("No Selection", "Please select an alert to mark as resolved")
                return
            
            # Get selected alert timestamp
            item = self.alerts_tree.item(selection[0])
            timestamp = item['values'][0]
            
            # Load alerts
            alerts_file = self.data_dir / "alerts.json"
            with open(alerts_file, 'r') as f:
                alerts = json.load(f)
            
            # Find and update alert
            from datetime import datetime
            for alert in alerts:
                if alert['timestamp'] == timestamp and alert.get('pool_id') == self.active_pool_id:
                    alert['resolved'] = True
                    alert['resolved_timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    break
            
            # Save updated alerts
            with open(alerts_file, 'w') as f:
                json.dump(alerts, f, indent=2)
            
            # Refresh table
            self._update_alerts_history_table()
            
            messagebox.showinfo("Success", "Alert marked as resolved")
            
        except Exception as e:
            logger.error(f"Error marking alert as resolved: {e}")
            messagebox.showerror("Error", f"Failed to mark alert as resolved: {str(e)}")


    def _export_alerts_report(self):
        """Export alerts history to CSV"""
        try:
            from tkinter import filedialog
            from datetime import datetime
            
            # Ask for save location
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                initialfile=f"alerts_report_{datetime.now().strftime('%Y%m%d')}.csv"
            )
            
            if not filename:
                return
            
            # Get current filters
            days = int(self.alert_date_range_var.get()) if self.alert_date_range_var.get() != "0" else None
            severity_filter = self.alert_severity_var.get()
            status_filter = self.alert_status_var.get()
            
            # Load alerts
            alerts = self._load_alert_history(days=days)
            
            # Apply filters
            if severity_filter != "all":
                alerts = [a for a in alerts if a.get('severity') == severity_filter]
            
            if status_filter == "active":
                alerts = [a for a in alerts if not a.get('resolved', False)]
            elif status_filter == "resolved":
                alerts = [a for a in alerts if a.get('resolved', False)]
            
            # Write to CSV
            import csv
            with open(filename, 'w', newline='') as f:
                writer = csv.writer(f)
                
                # Header
                writer.writerow([
                    'Alert ID', 'Pool ID', 'Timestamp', 'Severity', 'Parameter',
                    'Value', 'Threshold', 'Message', 'Action Recommended',
                    'Status', 'Resolved Timestamp', 'Action Taken', 'Notes'
                ])
                
                # Data
                for alert in alerts:
                    status = "Resolved" if alert.get('resolved', False) else "Active"
                    writer.writerow([
                        alert.get('alert_id', ''),
                        alert.get('pool_id', ''),
                        alert.get('timestamp', ''),
                        alert.get('severity', ''),
                        alert.get('parameter', ''),
                        alert.get('value', ''),
                        alert.get('threshold', ''),
                        alert.get('message', ''),
                        alert.get('action_recommended', ''),
                        status,
                        alert.get('resolved_timestamp', ''),
                        alert.get('action_taken', ''),
                        alert.get('notes', '')
                    ])
            
            messagebox.showinfo("Success", f"Alert report exported to:\n{filename}")
            
        except Exception as e:
            logger.error(f"Error exporting alerts report: {e}")
            messagebox.showerror("Error", f"Failed to export report: {str(e)}")


    def _add_alert_notes(self):
        """Add notes to selected alert"""
        try:
            selection = self.alerts_tree.selection()
            if not selection:
                messagebox.showwarning("No Selection", "Please select an alert")
                return
            
            # Get selected alert timestamp
            item = self.alerts_tree.item(selection[0])
            timestamp = item['values'][0]
            
            # Create dialog
            dialog = tk.Toplevel(self)
            dialog.title("Add Notes")
            dialog.geometry("400x200")
            
            ttk.Label(dialog, text="Notes:").pack(pady=5)
            
            notes_text = tk.Text(dialog, height=8, width=45)
            notes_text.pack(padx=10, pady=5)
            
            def save_notes():
                notes = notes_text.get("1.0", "end-1c")
                
                # Load alerts
                alerts_file = self.data_dir / "alerts.json"
                with open(alerts_file, 'r') as f:
                    alerts = json.load(f)
                
                # Find and update alert
                for alert in alerts:
                    if alert['timestamp'] == timestamp and alert.get('pool_id') == self.active_pool_id:
                        alert['notes'] = notes
                        break
                
                # Save
                with open(alerts_file, 'w') as f:
                    json.dump(alerts, f, indent=2)
                
                dialog.destroy()
                messagebox.showinfo("Success", "Notes saved")
            
            ttk.Button(dialog, text="Save", command=save_notes).pack(pady=5)
            
        except Exception as e:
            logger.error(f"Error adding notes: {e}")
            messagebox.showerror("Error", f"Failed to add notes: {str(e)}")


    def _view_alert_details(self):
        """View detailed information about selected alert"""
        try:
            selection = self.alerts_tree.selection()
            if not selection:
                messagebox.showwarning("No Selection", "Please select an alert")
                return
            
            # Get selected alert timestamp
            item = self.alerts_tree.item(selection[0])
            timestamp = item['values'][0]
            
            # Load alerts
            alerts_file = self.data_dir / "alerts.json"
            with open(alerts_file, 'r') as f:
                alerts = json.load(f)
            
            # Find alert
            alert = None
            for a in alerts:
                if a['timestamp'] == timestamp and a.get('pool_id') == self.active_pool_id:
                    alert = a
                    break
            
            if not alert:
                messagebox.showerror("Error", "Alert not found")
                return
            
            # Create dialog
            dialog = tk.Toplevel(self)
            dialog.title("Alert Details")
            dialog.geometry("500x400")
            
            # Details frame
            details_frame = ttk.Frame(dialog, padding=10)
            details_frame.pack(fill="both", expand=True)
            
            # Display details
            details = [
                ("Alert ID:", alert.get('alert_id', '')),
                ("Pool ID:", alert.get('pool_id', '')),
                ("Timestamp:", alert.get('timestamp', '')),
                ("Severity:", alert.get('severity', '').upper()),
                ("Parameter:", alert.get('parameter', '')),
                ("Value:", f"{alert.get('value', 0):.2f}"),
                ("Threshold:", f"{alert.get('threshold', 0):.2f}"),
                ("Message:", alert.get('message', '')),
                ("Action Recommended:", alert.get('action_recommended', '')),
                ("Status:", "Resolved" if alert.get('resolved', False) else "Active"),
                ("Resolved Timestamp:", alert.get('resolved_timestamp', 'N/A')),
                ("Action Taken:", alert.get('action_taken', 'N/A')),
                ("Notes:", alert.get('notes', 'None'))
            ]
            
            for i, (label, value) in enumerate(details):
                ttk.Label(details_frame, text=label, font=("Arial", 9, "bold")).grid(
                    row=i, column=0, sticky="w", padx=5, pady=2
                )
                ttk.Label(details_frame, text=str(value)).grid(
                    row=i, column=1, sticky="w", padx=5, pady=2
                )
            
            ttk.Button(dialog, text="Close", command=dialog.destroy).pack(pady=10)
            
        except Exception as e:
            logger.error(f"Error viewing alert details: {e}")
            messagebox.showerror("Error", f"Failed to view details: {str(e)}")

    def _on_close(self):
        """Handle application close event"""
        try:
            self._stop_threads.set()
            if self.arduino_thread:
                self.arduino_thread.join()
            self._cleanup()
            self.destroy()
        except Exception as e:
            logger.error(f"Error on close: {str(e)}")


    def _cleanup(self):
        """Clean up resources before exit"""
        try:
            if self.data_manager:
                self.data_manager.close_connection()
            if self.arduino:
                self.arduino.disconnect()
        except Exception as e:
            logger.error(f"Error cleaning up: {str(e)}")



    def _on_input_method_change(self):
        """Handle input method change"""
        method = self.input_method_var.get()
        
        if method == "manual":
            self.upload_strip_btn.config(state="disabled")
            self.camera_strip_btn.config(state="disabled")
            self.arduino_read_btn.config(state="disabled")
            self.input_status_label.config(text="Enter values manually below", fg="#7f8c8d")
        elif method == "upload":
            self.upload_strip_btn.config(state="normal")
            self.camera_strip_btn.config(state="disabled")
            self.arduino_read_btn.config(state="disabled")
            self.input_status_label.config(text="Click Select Image to upload test strip", fg="#3498db")
        elif method == "camera":
            self.upload_strip_btn.config(state="disabled")
            self.camera_strip_btn.config(state="normal")
            self.arduino_read_btn.config(state="disabled")
            self.input_status_label.config(text="Click Take Picture to capture test strip", fg="#9b59b6")
        elif method == "arduino":
            self.upload_strip_btn.config(state="disabled")
            self.camera_strip_btn.config(state="disabled")
            self.arduino_read_btn.config(state="normal")
            if self.arduino:
                self.input_status_label.config(text="Arduino connected - Click Read Sensors", fg="#27ae60")
            else:
                self.input_status_label.config(text="Arduino not connected", fg="#e74c3c")
    
    def _upload_strip_for_testing(self):
        """Upload test strip image and populate fields"""
        if not self.test_strip_analyzer:
            messagebox.showerror("Error", "Test strip analyzer not available")
            return
        
        from tkinter import filedialog
        
        filepath = filedialog.askopenfilename(
            title="Select Test Strip Image",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp"), ("All files", "*.*")]
        )
        
        if not filepath:
            return
        
        self.input_status_label.config(text="Analyzing image...", fg="#f39c12")
        self.update()
        
        try:
            results = self.test_strip_analyzer.analyze_image(filepath)
            
            if 'error' in results:
                messagebox.showerror("Analysis Error", results['error'])
                self.input_status_label.config(text="Analysis failed", fg="#e74c3c")
                return
            
            self._populate_fields_from_analysis(results)
            
            confidence = results.get('overall_confidence', 0) * 100
            self.input_status_label.config(text=f"Analysis complete - Confidence: {confidence:.0f}%", fg="#27ae60")
            
        except Exception as e:
            logger.error(f"Error analyzing image: {e}")
            messagebox.showerror("Error", f"Failed to analyze image: {e}")
            self.input_status_label.config(text="Error", fg="#e74c3c")
    
    def _camera_strip_for_testing(self):
        """Capture test strip from camera and populate fields"""
        if not self.test_strip_analyzer:
            messagebox.showerror("Error", "Test strip analyzer not available")
            return
        
        self.input_status_label.config(text="Capturing image...", fg="#f39c12")
        self.update()
        
        try:
            results = self.test_strip_analyzer.analyze_camera()
            
            if 'error' in results:
                messagebox.showerror("Capture Error", results['error'])
                self.input_status_label.config(text="Capture failed", fg="#e74c3c")
                return
            
            self._populate_fields_from_analysis(results)
            
            confidence = results.get('overall_confidence', 0) * 100
            self.input_status_label.config(text=f"Capture complete - Confidence: {confidence:.0f}%", fg="#27ae60")
            messagebox.showinfo("Success", "Image captured and analyzed successfully!")
            
        except Exception as e:
            logger.error(f"Error capturing from camera: {e}")
            messagebox.showerror("Error", f"Failed to capture from camera: {e}")
            self.input_status_label.config(text="Error", fg="#e74c3c")
    
    def _read_arduino_sensors(self):
        """Read values from Arduino sensors and populate fields"""
        if not self.arduino:
            messagebox.showerror("Error", "Arduino not connected")
            return
        
        self.input_status_label.config(text="Reading sensors...", fg="#f39c12")
        self.update()
        
        try:
            sensor_data = self.arduino.read_sensors()
            
            if not sensor_data:
                messagebox.showerror("Error", "No data received from Arduino")
                self.input_status_label.config(text="No data received", fg="#e74c3c")
                return
            
            if 'ph' in sensor_data and sensor_data['ph'] is not None:
                self.entries['ph'].delete(0, tk.END)
                self.entries['ph'].insert(0, f"{sensor_data['ph']:.1f}")
            
            if 'temperature' in sensor_data and sensor_data['temperature'] is not None:
                self.entries['temperature'].delete(0, tk.END)
                self.entries['temperature'].insert(0, f"{sensor_data['temperature']:.1f}")
            
            if 'orp' in sensor_data and sensor_data['orp'] is not None:
                orp = sensor_data['orp']
                chlorine_estimate = 3.0 if orp > 650 else 2.0 if orp > 600 else 1.0 if orp > 550 else 0.5
                self.entries['free_chlorine'].delete(0, tk.END)
                self.entries['free_chlorine'].insert(0, f"{chlorine_estimate:.1f}")
            
            if 'tds' in sensor_data and sensor_data['tds'] is not None:
                self.entries['salt'].delete(0, tk.END)
                self.entries['salt'].insert(0, f"{sensor_data['tds']:.0f}")
            
            self.input_status_label.config(text="Sensor data loaded successfully", fg="#27ae60")
            messagebox.showinfo("Success", "Sensor readings loaded successfully!")
            
        except Exception as e:
            logger.error(f"Error reading sensors: {e}")
            messagebox.showerror("Error", f"Failed to read sensors: {e}")
            self.input_status_label.config(text="Sensor read failed", fg="#e74c3c")
    
    def _populate_fields_from_analysis(self, results):
        """Populate input fields from test strip analysis results"""
        if 'results' not in results:
            return
        
        readings = results['results']
        
        for key in ['ph', 'free_chlorine', 'total_chlorine', 'alkalinity', 
                    'calcium_hardness', 'cyanuric_acid', 'bromine', 'salt']:
            if readings.get(key) is not None and key in self.entries:
                self.entries[key].delete(0, tk.END)
                if key in ['ph', 'free_chlorine', 'total_chlorine', 'bromine']:
                    self.entries[key].insert(0, f"{readings[key]:.1f}")
                else:
                    self.entries[key].insert(0, f"{readings[key]:.0f}")


## Main function to run the application
    # ========================================================================
    # PHASE 1.2: UI COMPONENTS
    # ========================================================================

    def _create_alert_config_tab(self):
            """Create the Alert Configuration tab"""
            # Create main frame
            config_frame = ttk.Frame(self.notebook)
            self.notebook.add(config_frame, text="Alert Configuration")

            # Create scrollable canvas
            canvas = tk.Canvas(config_frame, bg='#F0F4F8')
            scrollbar = ttk.Scrollbar(config_frame, orient="vertical", command=canvas.yview)
            scrollable_frame = ttk.Frame(canvas)

            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )

            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)

            # Pack canvas and scrollbar
            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")

            # Title
            title_label = tk.Label(
                scrollable_frame,
                text="Alert Configuration",
                font=("Arial", 16, "bold"),
                bg='#F0F4F8',
                fg='#2C3E50'
            )
            title_label.pack(pady=10)

            # Pool Selection
            pool_frame = ttk.LabelFrame(scrollable_frame, text="Select Pool", padding=10)
            pool_frame.pack(fill="x", padx=20, pady=10)

            self.config_pool_var = tk.StringVar(value="global_defaults")

            tk.Label(pool_frame, text="Configure alerts for:", bg='#F0F4F8').pack(side="left", padx=5)

            # Get pool list
            pool_options = ["Global Defaults (All Pools)"]
            if hasattr(self, 'pools') and self.pools:
                for pool_data in self.pools:
                    pool_id = pool_data.get('id', 'unknown')
                    pool_name = pool_data.get('name', pool_id)
                    pool_options.append(f"{pool_name} ({pool_id})")

            pool_dropdown = ttk.Combobox(
                pool_frame,
                textvariable=self.config_pool_var,
                values=pool_options,
                state="readonly",
                width=40
            )
            pool_dropdown.pack(side="left", padx=5)
            pool_dropdown.bind("<<ComboboxSelected>>", lambda e: self._load_pool_config())

            # Threshold Configuration Panel
            threshold_frame = ttk.LabelFrame(scrollable_frame, text="Alert Thresholds", padding=10)
            threshold_frame.pack(fill="both", expand=True, padx=20, pady=10)

            # Create grid for thresholds
            # Create a frame to hold the grid
            threshold_grid_frame = ttk.Frame(threshold_frame)
            threshold_grid_frame.pack(fill="both", expand=True, padx=5, pady=5)
            
            parameters = [
                ("pH", "ph", 0.0, 14.0),
                ("Free Chlorine (ppm)", "chlorine", 0.0, 10.0),
                ("Total Alkalinity (ppm)", "alkalinity", 0, 200),
                ("Calcium Hardness (ppm)", "calcium", 0, 1000),
                ("Cyanuric Acid (ppm)", "cya", 0, 150),
                ("Salt (ppm)", "salt", 0, 5000),
                ("Temperature (°F)", "temperature", 32, 120)
            ]

            # Headers
            tk.Label(threshold_grid_frame, text="Parameter", font=("Arial", 10, "bold"), bg='#F0F4F8').grid(row=0, column=0, padx=5, pady=5, sticky="w")
            tk.Label(threshold_grid_frame, text="Minimum", font=("Arial", 10, "bold"), bg='#F0F4F8').grid(row=0, column=1, padx=5, pady=5)
            tk.Label(threshold_grid_frame, text="Maximum", font=("Arial", 10, "bold"), bg='#F0F4F8').grid(row=0, column=2, padx=5, pady=5)
            tk.Label(threshold_grid_frame, text="Actions", font=("Arial", 10, "bold"), bg='#F0F4F8').grid(row=0, column=3, padx=5, pady=5)

            self.threshold_entries = {}

            for idx, (label, param, min_val, max_val) in enumerate(parameters, start=1):
                # Parameter label
                tk.Label(threshold_grid_frame, text=label, bg='#F0F4F8').grid(row=idx, column=0, padx=5, pady=5, sticky="w")

                # Min entry
                min_var = tk.DoubleVar()
                min_entry = ttk.Entry(threshold_grid_frame, textvariable=min_var, width=10)
                min_entry.grid(row=idx, column=1, padx=5, pady=5)

                # Max entry
                max_var = tk.DoubleVar()
                max_entry = ttk.Entry(threshold_grid_frame, textvariable=max_var, width=10)
                max_entry.grid(row=idx, column=2, padx=5, pady=5)

                # Reset button
                reset_btn = ttk.Button(
                    threshold_grid_frame,
                    text="Reset",
                    command=lambda p=param: self._reset_threshold(p)
                )
                reset_btn.grid(row=idx, column=3, padx=5, pady=5)

                self.threshold_entries[param] = {
                    'min_var': min_var,
                    'max_var': max_var,
                    'min_entry': min_entry,
                    'max_entry': max_entry
                }

            # Severity Threshold Panel
            severity_frame = ttk.LabelFrame(scrollable_frame, text="Severity Thresholds (Deviation from Range)", padding=10)
            severity_frame.pack(fill="both", expand=True, padx=20, pady=10)

            severity_info = tk.Label(
                severity_frame,
                text="Configure how far from the ideal range triggers each severity level",
                font=("Arial", 9, "italic"),
                bg='#F0F4F8',
                fg='#666'
            )
            severity_info.pack(pady=5)

            # Severity grid
            # Create a frame to hold the grid
            severity_grid_frame = ttk.Frame(severity_frame)
            severity_grid_frame.pack(fill="both", expand=True, padx=5, pady=5)
            
            severity_params = [
                ("pH", "ph", 0.01, 1.0),
                ("Chlorine (ppm)", "chlorine", 0.1, 5.0),
                ("Alkalinity (ppm)", "alkalinity", 1, 100),
                ("Calcium (ppm)", "calcium", 10, 500),
                ("CYA (ppm)", "cya", 1, 50),
                ("Salt (ppm)", "salt", 50, 1000),
                ("Temperature (°F)", "temperature", 1, 20)
            ]

            # Headers
            tk.Label(severity_grid_frame, text="Parameter", font=("Arial", 10, "bold"), bg='#F0F4F8').grid(row=0, column=0, padx=5, pady=5, sticky="w")
            tk.Label(severity_grid_frame, text="Info", font=("Arial", 10, "bold"), fg='#2196F3', bg='#F0F4F8').grid(row=0, column=1, padx=5, pady=5)
            tk.Label(severity_grid_frame, text="Warning", font=("Arial", 10, "bold"), fg='#FF9800', bg='#F0F4F8').grid(row=0, column=2, padx=5, pady=5)
            tk.Label(severity_grid_frame, text="Critical", font=("Arial", 10, "bold"), fg='#F44336', bg='#F0F4F8').grid(row=0, column=3, padx=5, pady=5)

            self.severity_entries = {}

            for idx, (label, param, min_val, max_val) in enumerate(severity_params, start=1):
                tk.Label(severity_grid_frame, text=label, bg='#F0F4F8').grid(row=idx, column=0, padx=5, pady=5, sticky="w")

                self.severity_entries[param] = {}

                for col, level in enumerate(['info', 'warning', 'critical'], start=1):
                    var = tk.DoubleVar()
                    entry = ttk.Entry(severity_grid_frame, textvariable=var, width=10)
                    entry.grid(row=idx, column=col, padx=5, pady=5)
                    self.severity_entries[param][level] = {'var': var, 'entry': entry}

            # Action Buttons
            button_frame = ttk.Frame(scrollable_frame)
            button_frame.pack(fill="x", padx=20, pady=20)

            save_btn = tk.Button(
                button_frame,
                text="Save Configuration",
                command=self._save_config_from_ui,
                bg='#27AE60',
                fg='white',
                font=("Arial", 12, "bold"),
                padx=20,
                pady=10
            )
            save_btn.pack(side="left", padx=5)

            reset_all_btn = tk.Button(
                button_frame,
                text="Reset All to Defaults",
                command=self._reset_all_config,
                bg='#E67E22',
                fg='white',
                font=("Arial", 12, "bold"),
                padx=20,
                pady=10
            )
            reset_all_btn.pack(side="left", padx=5)

            # Load initial config
            self._load_pool_config()

    def _load_pool_config(self):
            """Load configuration for selected pool"""
            try:
                selected = self.config_pool_var.get()

                if selected == "Global Defaults (All Pools)":
                    pool_id = "global_defaults"
                    config = self.alert_config['global_defaults']
                else:
                    # Extract pool_id from selection
                    pool_id = selected.split('(')[-1].strip(')')
                    if pool_id in self.alert_config['pool_specific']:
                        config = self.alert_config['pool_specific'][pool_id]
                    else:
                        config = self.alert_config['global_defaults']

                # Load thresholds
                for param, entries in self.threshold_entries.items():
                    min_key = f"{param}_min"
                    max_key = f"{param}_max"
                    entries['min_var'].set(config.get(min_key, 0))
                    entries['max_var'].set(config.get(max_key, 0))

                # Load severity thresholds
                severity_config = self.alert_config['severity_thresholds']
                for param, levels in self.severity_entries.items():
                    for level, entry_data in levels.items():
                        key = f"{param}_deviation"
                        value = severity_config[level].get(key, 0)
                        entry_data['var'].set(value)

                print(f"[Config] Loaded configuration for {selected}")

            except Exception as e:
                print(f"[Config] Error loading pool config: {e}")
                messagebox.showerror("Error", f"Failed to load configuration: {e}")

    def _save_config_from_ui(self):
            """Save configuration from UI to file"""
            try:
                selected = self.config_pool_var.get()

                if selected == "Global Defaults (All Pools)":
                    # Update global defaults
                    for param, entries in self.threshold_entries.items():
                        min_key = f"{param}_min"
                        max_key = f"{param}_max"
                        self.alert_config['global_defaults'][min_key] = entries['min_var'].get()
                        self.alert_config['global_defaults'][max_key] = entries['max_var'].get()
                else:
                    # Update pool-specific config
                    pool_id = selected.split('(')[-1].strip(')')

                    if pool_id not in self.alert_config['pool_specific']:
                        self.alert_config['pool_specific'][pool_id] = {}

                    for param, entries in self.threshold_entries.items():
                        min_key = f"{param}_min"
                        max_key = f"{param}_max"
                        self.alert_config['pool_specific'][pool_id][min_key] = entries['min_var'].get()
                        self.alert_config['pool_specific'][pool_id][max_key] = entries['max_var'].get()

                # Update severity thresholds (always global)
                for param, levels in self.severity_entries.items():
                    for level, entry_data in levels.items():
                        key = f"{param}_deviation"
                        self.alert_config['severity_thresholds'][level][key] = entry_data['var'].get()

                # Validate and save
                is_valid, errors = self._validate_alert_config(self.alert_config)
                if not is_valid:
                    messagebox.showerror("Validation Error", "Configuration errors:\n" + "\n".join(errors))
                    return

                if self._save_alert_config(self.alert_config):
                    messagebox.showinfo("Success", "Configuration saved successfully!")
                else:
                    messagebox.showerror("Error", "Failed to save configuration")

            except Exception as e:
                print(f"[Config] Error saving config: {e}")
                messagebox.showerror("Error", f"Failed to save configuration: {e}")

    def _reset_threshold(self, param):
            """Reset a single threshold to default"""
            try:
                defaults = self._get_default_alert_config()['global_defaults']
                min_key = f"{param}_min"
                max_key = f"{param}_max"

                self.threshold_entries[param]['min_var'].set(defaults[min_key])
                self.threshold_entries[param]['max_var'].set(defaults[max_key])

                print(f"[Config] Reset {param} to defaults")
            except Exception as e:
                print(f"[Config] Error resetting threshold: {e}")

    def _reset_all_config(self):
            """Reset all configuration to defaults"""
            try:
                if messagebox.askyesno("Confirm Reset", "Reset all configuration to defaults?"):
                    self.alert_config = self._get_default_alert_config()
                    self._save_alert_config(self.alert_config)
                    self._load_pool_config()
                    messagebox.showinfo("Success", "Configuration reset to defaults!")
            except Exception as e:
                print(f"[Config] Error resetting config: {e}")
                messagebox.showerror("Error", f"Failed to reset configuration: {e}")

        # ============================================================================
        # SECTION 2: ENHANCED ALERT HISTORY TAB
        # ============================================================================

    def _create_enhanced_alert_history_tab(self):
            """Create enhanced Alert History tab with filtering and actions"""
            # Find and remove old alert history tab if it exists
            for i in range(self.notebook.index("end")):
                if self.notebook.tab(i, "text") == "Alert History":
                    self.notebook.forget(i)
                    break

            # Create new enhanced tab
            history_frame = ttk.Frame(self.notebook)
            self.notebook.add(history_frame, text="Alert History")

            # Filter Bar
            filter_frame = ttk.LabelFrame(history_frame, text="Filters", padding=10)
            filter_frame.pack(fill="x", padx=10, pady=10)

            # Row 1: Severity, Pool, Status
            row1 = ttk.Frame(filter_frame)
            row1.pack(fill="x", pady=5)

            tk.Label(row1, text="Severity:", bg='#F0F4F8').pack(side="left", padx=5)
            self.filter_severity_var = tk.StringVar(value="all")
            severity_combo = ttk.Combobox(
                row1,
                textvariable=self.filter_severity_var,
                values=["all", "info", "warning", "critical"],
                state="readonly",
                width=15
            )
            severity_combo.pack(side="left", padx=5)

            tk.Label(row1, text="Pool:", bg='#F0F4F8').pack(side="left", padx=5)
            self.filter_pool_var = tk.StringVar(value="all")
            pool_options = ["all"]
            if hasattr(self, 'pools') and self.pools:
                pool_options.extend([pool_data.get('name', pool_data.get('id', 'unknown')) for pool_data in self.pools])
            pool_combo = ttk.Combobox(
                row1,
                textvariable=self.filter_pool_var,
                values=pool_options,
                state="readonly",
                width=20
            )
            pool_combo.pack(side="left", padx=5)

            tk.Label(row1, text="Status:", bg='#F0F4F8').pack(side="left", padx=5)
            self.filter_status_var = tk.StringVar(value="all")
            status_combo = ttk.Combobox(
                row1,
                textvariable=self.filter_status_var,
                values=["all", "unacknowledged", "acknowledged", "snoozed", "dismissed"],
                state="readonly",
                width=15
            )
            status_combo.pack(side="left", padx=5)

            # Row 2: Search and Apply
            row2 = ttk.Frame(filter_frame)
            row2.pack(fill="x", pady=5)

            tk.Label(row2, text="Search:", bg='#F0F4F8').pack(side="left", padx=5)
            self.filter_search_var = tk.StringVar()
            search_entry = ttk.Entry(row2, textvariable=self.filter_search_var, width=40)
            search_entry.pack(side="left", padx=5)

            apply_btn = tk.Button(
                row2,
                text="Apply Filters",
                command=self._apply_alert_filters,
                bg='#3498DB',
                fg='white',
                font=("Arial", 10, "bold"),
                padx=15,
                pady=5
            )
            apply_btn.pack(side="left", padx=5)

            clear_btn = tk.Button(
                row2,
                text="Clear Filters",
                command=self._clear_alert_filters,
                bg='#95A5A6',
                fg='white',
                font=("Arial", 10, "bold"),
                padx=15,
                pady=5
            )
            clear_btn.pack(side="left", padx=5)

            # Unacknowledged Counter
            counter_frame = ttk.Frame(history_frame)
            counter_frame.pack(fill="x", padx=10, pady=5)

            self.unack_count_label = tk.Label(
                counter_frame,
                text="Unacknowledged Alerts: 0",
                font=("Arial", 12, "bold"),
                bg='#F0F4F8',
                fg='#E74C3C'
            )
            self.unack_count_label.pack(side="left", padx=10)

            refresh_btn = tk.Button(
                counter_frame,
                text="Refresh",
                command=self._refresh_alert_history,
                bg='#27AE60',
                fg='white',
                font=("Arial", 10, "bold"),
                padx=15,
                pady=5
            )
            refresh_btn.pack(side="right", padx=10)

            # Alert List (Scrollable)
            list_frame = ttk.Frame(history_frame)
            list_frame.pack(fill="both", expand=True, padx=10, pady=10)

            # Create canvas for scrolling
            canvas = tk.Canvas(list_frame, bg='#F0F4F8')
            scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=canvas.yview)
            self.alert_list_frame = ttk.Frame(canvas)

            self.alert_list_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )

            canvas.create_window((0, 0), window=self.alert_list_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)

            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")

            # Initial load
            self._refresh_alert_history()

    def _apply_alert_filters(self):
            """Apply filters and refresh alert display"""
            self._refresh_alert_history()

    def _clear_alert_filters(self):
            """Clear all filters"""
            self.filter_severity_var.set("all")
            self.filter_pool_var.set("all")
            self.filter_status_var.set("all")
            self.filter_search_var.set("")
            self._refresh_alert_history()

    def _refresh_alert_history(self):
            """Refresh alert history display with filters"""
            try:
                # Clear existing alerts
                for widget in self.alert_list_frame.winfo_children():
                    widget.destroy()

                # Load all alerts
                all_alerts = self._load_alert_history()

                # Apply filters
                filtered_alerts = self._apply_all_filters(
                    all_alerts,
                    severity=self.filter_severity_var.get(),
                    pool_id=self.filter_pool_var.get(),
                    status=self.filter_status_var.get(),
                    search_term=self.filter_search_var.get()
                )

                # Update unacknowledged count
                unack_count, _ = self._get_unacknowledged_alerts()
                self.unack_count_label.config(text=f"Unacknowledged Alerts: {unack_count}")

                # Display filtered alerts
                if not filtered_alerts:
                    tk.Label(
                        self.alert_list_frame,
                        text="No alerts found",
                        font=("Arial", 12),
                        bg='#F0F4F8',
                        fg='#666'
                    ).pack(pady=20)
                    return

                # Sort by timestamp (newest first)
                filtered_alerts.sort(key=lambda x: x.get('timestamp', ''), reverse=True)

                # Display each alert
                for alert in filtered_alerts:
                    self._create_alert_item(alert)

            except Exception as e:
                print(f"[Alert History] Error refreshing: {e}")
                messagebox.showerror("Error", f"Failed to refresh alert history: {e}")

    def _create_alert_item(self, alert):
            """Create a single alert item widget"""
            # Main frame for alert
            alert_frame = tk.Frame(
                self.alert_list_frame,
                bg='white',
                bd=2,
                relief="solid",
                padx=10,
                pady=10
            )
            alert_frame.pack(fill="x", padx=5, pady=5)

            # Get severity color and icon
            severity = alert.get('severity', 'warning')
            color = self._get_severity_color(severity)
            icon = self._get_severity_icon(severity)

            # Header row
            header_frame = tk.Frame(alert_frame, bg='white')
            header_frame.pack(fill="x")

            # Severity indicator
            severity_label = tk.Label(
                header_frame,
                text=f"{icon} {severity.upper()}",
                font=("Arial", 10, "bold"),
                fg=color,
                bg='white'
            )
            severity_label.pack(side="left", padx=5)

            # Pool name
            pool_label = tk.Label(
                header_frame,
                text=alert.get('pool_name', 'Unknown Pool'),
                font=("Arial", 10, "bold"),
                bg='white'
            )
            pool_label.pack(side="left", padx=10)

            # Timestamp
            timestamp_label = tk.Label(
                header_frame,
                text=alert.get('timestamp', ''),
                font=("Arial", 9),
                fg='#666',
                bg='white'
            )
            timestamp_label.pack(side="right", padx=5)

            # Status indicator
            status = alert.get('status', 'unacknowledged')
            status_colors = {
                'unacknowledged': '#E74C3C',
                'acknowledged': '#27AE60',
                'snoozed': '#F39C12',
                'dismissed': '#95A5A6'
            }
            status_label = tk.Label(
                header_frame,
                text=status.upper(),
                font=("Arial", 9, "bold"),
                fg=status_colors.get(status, '#666'),
                bg='white'
            )
            status_label.pack(side="right", padx=10)

            # Message
            message_label = tk.Label(
                alert_frame,
                text=alert.get('message', ''),
                font=("Arial", 10),
                bg='white',
                wraplength=700,
                justify="left"
            )
            message_label.pack(fill="x", pady=5)

            # Parameter and value
            param_text = f"{alert.get('parameter', 'N/A')}: {alert.get('value', 0):.2f}"
            param_label = tk.Label(
                alert_frame,
                text=param_text,
                font=("Arial", 9, "bold"),
                bg='white'
            )
            param_label.pack(anchor="w", pady=2)

            # Action buttons
            if status != 'dismissed':
                button_frame = tk.Frame(alert_frame, bg='white')
                button_frame.pack(fill="x", pady=5)

                if status == 'unacknowledged':
                    ack_btn = tk.Button(
                        button_frame,
                        text="✓ Acknowledge",
                        command=lambda: self._acknowledge_and_refresh(alert['alert_id']),
                        bg='#27AE60',
                        fg='white',
                        font=("Arial", 9, "bold"),
                        padx=10,
                        pady=3
                    )
                    ack_btn.pack(side="left", padx=5)

                # Snooze button
                snooze_btn = tk.Button(
                    button_frame,
                    text="⏰ Snooze 1h",
                    command=lambda: self._snooze_and_refresh(alert['alert_id'], 1),
                    bg='#F39C12',
                    fg='white',
                    font=("Arial", 9, "bold"),
                    padx=10,
                    pady=3
                )
                snooze_btn.pack(side="left", padx=5)

                snooze_4h_btn = tk.Button(
                    button_frame,
                    text="⏰ Snooze 4h",
                    command=lambda: self._snooze_and_refresh(alert['alert_id'], 4),
                    bg='#F39C12',
                    fg='white',
                    font=("Arial", 9, "bold"),
                    padx=10,
                    pady=3
                )
                snooze_4h_btn.pack(side="left", padx=5)

                snooze_24h_btn = tk.Button(
                    button_frame,
                    text="⏰ Snooze 24h",
                    command=lambda: self._snooze_and_refresh(alert['alert_id'], 24),
                    bg='#F39C12',
                    fg='white',
                    font=("Arial", 9, "bold"),
                    padx=10,
                    pady=3
                )
                snooze_24h_btn.pack(side="left", padx=5)

                # Dismiss button
                dismiss_btn = tk.Button(
                    button_frame,
                    text="✕ Dismiss",
                    command=lambda: self._dismiss_and_refresh(alert['alert_id']),
                    bg='#E74C3C',
                    fg='white',
                    font=("Arial", 9, "bold"),
                    padx=10,
                    pady=3
                )
                dismiss_btn.pack(side="left", padx=5)

    def _acknowledge_and_refresh(self, alert_id):
            """Acknowledge alert and refresh display"""
            if self._acknowledge_alert(alert_id):
                self._refresh_alert_history()

    def _snooze_and_refresh(self, alert_id, hours):
            """Snooze alert and refresh display"""
            if self._snooze_alert(alert_id, hours):
                messagebox.showinfo("Snoozed", f"Alert snoozed for {hours} hour(s)")
                self._refresh_alert_history()

    def _dismiss_and_refresh(self, alert_id):
            """Dismiss alert and refresh display"""
            if messagebox.askyesno("Confirm Dismiss", "Permanently dismiss this alert?"):
                if self._dismiss_alert(alert_id):
                    self._refresh_alert_history()

    # ========================================================================
    # PHASE 1.2: ALERT CONFIGURATION & MANAGEMENT METHODS
    # ========================================================================

    def _get_default_alert_config(self):
            """
            Get default alert configuration structure.
            Returns dictionary with global defaults and severity thresholds.
            """
            return {
                "global_defaults": {
                    "ph_min": 7.2,
                    "ph_max": 7.8,
                    "chlorine_min": 1.0,
                    "chlorine_max": 3.0,
                    "alkalinity_min": 80,
                    "alkalinity_max": 120,
                    "calcium_min": 200,
                    "calcium_max": 400,
                    "cya_min": 30,
                    "cya_max": 50,
                    "salt_min": 2700,
                    "salt_max": 3400,
                    "temperature_min": 78,
                    "temperature_max": 104
                },
                "pool_specific": {},
                "severity_thresholds": {
                    "info": {
                        "ph_deviation": 0.1,
                        "chlorine_deviation": 0.3,
                        "alkalinity_deviation": 10,
                        "calcium_deviation": 25,
                        "cya_deviation": 5,
                        "salt_deviation": 100,
                        "temperature_deviation": 2
                    },
                    "warning": {
                        "ph_deviation": 0.3,
                        "chlorine_deviation": 0.5,
                        "alkalinity_deviation": 20,
                        "calcium_deviation": 50,
                        "cya_deviation": 10,
                        "salt_deviation": 200,
                        "temperature_deviation": 5
                    },
                    "critical": {
                        "ph_deviation": 0.5,
                        "chlorine_deviation": 1.0,
                        "alkalinity_deviation": 40,
                        "calcium_deviation": 100,
                        "cya_deviation": 20,
                        "salt_deviation": 400,
                        "temperature_deviation": 10
                    }
                }
            }

    def _load_alert_config(self):
            """
            Load alert configuration from file or create default.
            Returns configuration dictionary.
            """
            config_file = os.path.join(self.data_dir, "alert_config.json")

            try:
                if os.path.exists(config_file):
                    with open(config_file, 'r') as f:
                        config = json.load(f)
                    print(f"[Alert Config] Loaded configuration from {config_file}")
                    return config
                else:
                    # Create default configuration
                    config = self._get_default_alert_config()
                    self._save_alert_config(config)
                    print(f"[Alert Config] Created default configuration at {config_file}")
                    return config
            except Exception as e:
                print(f"[Alert Config] Error loading configuration: {e}")
                return self._get_default_alert_config()

    def _save_alert_config(self, config):
            """
            Save alert configuration to file.
            Validates configuration before saving.
            """
            config_file = os.path.join(self.data_dir, "alert_config.json")

            try:
                # Validate configuration
                is_valid, errors = self._validate_alert_config(config)
                if not is_valid:
                    print(f"[Alert Config] Validation errors: {errors}")
                    return False

                # Save to file
                with open(config_file, 'w') as f:
                    json.dump(config, f, indent=2)

                print(f"[Alert Config] Configuration saved successfully")
                return True
            except Exception as e:
                print(f"[Alert Config] Error saving configuration: {e}")
                return False

    def _validate_alert_config(self, config):
            """
            Validate alert configuration values.
            Returns (is_valid, error_messages).
            """
            errors = []

            try:
                # Check required sections
                required_sections = ['global_defaults', 'pool_specific', 'severity_thresholds']
                for section in required_sections:
                    if section not in config:
                        errors.append(f"Missing required section: {section}")

                if errors:
                    return False, errors

                # Validate global defaults
                defaults = config['global_defaults']
                parameters = ['ph', 'chlorine', 'alkalinity', 'calcium', 'cya', 'salt', 'temperature']

                for param in parameters:
                    min_key = f"{param}_min"
                    max_key = f"{param}_max"

                    if min_key not in defaults or max_key not in defaults:
                        errors.append(f"Missing threshold for {param}")
                        continue

                    min_val = defaults[min_key]
                    max_val = defaults[max_key]

                    if min_val >= max_val:
                        errors.append(f"{param}: min ({min_val}) must be less than max ({max_val})")

                # Validate severity thresholds
                severity_levels = ['info', 'warning', 'critical']
                for level in severity_levels:
                    if level not in config['severity_thresholds']:
                        errors.append(f"Missing severity threshold: {level}")

                return len(errors) == 0, errors

            except Exception as e:
                return False, [f"Validation error: {str(e)}"]

    def _apply_custom_thresholds(self, pool_id):
            """
            Get effective thresholds for a specific pool.
            Pool-specific settings override global defaults.
            Returns dictionary of thresholds.
            """
            try:
                config = self.alert_config
                thresholds = config['global_defaults'].copy()

                # Apply pool-specific overrides if they exist
                if pool_id in config['pool_specific']:
                    pool_config = config['pool_specific'][pool_id]
                    thresholds.update(pool_config)

                return thresholds
            except Exception as e:
                print(f"[Alert Config] Error applying custom thresholds: {e}")
                return config['global_defaults']

        # ============================================================================
        # SECTION 2: SEVERITY CLASSIFICATION METHODS
        # ============================================================================

    def _classify_alert_severity(self, parameter, value, min_threshold, max_threshold):
            """
            Determine severity level of an alert based on deviation from thresholds.
            Returns 'info', 'warning', 'critical', or None if within range.
            """
            try:
                # Check if value is within range
                if min_threshold <= value <= max_threshold:
                    return None  # No alert needed

                # Calculate deviation
                if value < min_threshold:
                    deviation = min_threshold - value
                else:
                    deviation = value - max_threshold

                # Get severity thresholds for this parameter
                config = self.alert_config
                param_key = f"{parameter.lower()}_deviation"

                info_threshold = config['severity_thresholds']['info'].get(param_key, 0)
                warning_threshold = config['severity_thresholds']['warning'].get(param_key, 0)

                # Classify severity
                if deviation <= info_threshold:
                    return 'info'
                elif deviation <= warning_threshold:
                    return 'warning'
                else:
                    return 'critical'

            except Exception as e:
                print(f"[Severity] Error classifying severity: {e}")
                return 'warning'  # Default to warning on error

    def _get_severity_color(self, severity):
            """
            Get color code for severity level.
            Returns hex color string.
            """
            colors = {
                'info': '#2196F3',      # Blue
                'warning': '#FF9800',   # Orange
                'critical': '#F44336'   # Red
            }
            return colors.get(severity, '#757575')  # Gray for unknown

    def _get_severity_icon(self, severity):
            """
            Get emoji icon for severity level.
            Returns emoji string.
            """
            icons = {
                'info': 'ℹ️',
                'warning': '⚠️',
                'critical': '🚨'
            }
            return icons.get(severity, '•')

        # ============================================================================
        # SECTION 3: ALERT ACKNOWLEDGMENT METHODS
        # ============================================================================

    def _acknowledge_alert(self, alert_id):
            """
            Mark alert as acknowledged.
            Updates status and timestamp in alerts.json.
            """
            try:
                alerts_file = os.path.join(self.data_dir, "alerts.json")

                if not os.path.exists(alerts_file):
                    print(f"[Acknowledge] Alerts file not found")
                    return False

                # Load alerts
                with open(alerts_file, 'r') as f:
                    alerts = json.load(f)

                # Find and update alert
                alert_found = False
                for alert in alerts:
                    if alert.get('alert_id') == alert_id:
                        alert['status'] = 'acknowledged'
                        alert['acknowledged_at'] = datetime.now().isoformat()
                        alert_found = True
                        break

                if not alert_found:
                    print(f"[Acknowledge] Alert {alert_id} not found")
                    return False

                # Save updated alerts
                with open(alerts_file, 'w') as f:
                    json.dump(alerts, f, indent=2)

                print(f"[Acknowledge] Alert {alert_id} acknowledged")
                return True

            except Exception as e:
                print(f"[Acknowledge] Error acknowledging alert: {e}")
                return False

    def _get_unacknowledged_alerts(self):
            """
            Get count and list of unacknowledged alerts.
            Returns (count, alerts_list).
            """
            try:
                alerts = self._load_alert_history()

                unacknowledged = [
                    alert for alert in alerts
                    if alert.get('status') == 'unacknowledged' 
                    and not alert.get('dismissed', False)
                    and not alert.get('snoozed_until')
                ]

                return len(unacknowledged), unacknowledged

            except Exception as e:
                print(f"[Unacknowledged] Error getting unacknowledged alerts: {e}")
                return 0, []

    def _mark_alert_reviewed(self, alert_id, notes=""):
            """
            Mark alert as reviewed and add optional notes.
            """
            try:
                alerts_file = os.path.join(self.data_dir, "alerts.json")

                if not os.path.exists(alerts_file):
                    return False

                with open(alerts_file, 'r') as f:
                    alerts = json.load(f)

                for alert in alerts:
                    if alert.get('alert_id') == alert_id:
                        alert['status'] = 'acknowledged'
                        alert['acknowledged_at'] = datetime.now().isoformat()
                        if notes:
                            alert['notes'] = notes
                        break

                with open(alerts_file, 'w') as f:
                    json.dump(alerts, f, indent=2)

                return True

            except Exception as e:
                print(f"[Review] Error marking alert as reviewed: {e}")
                return False

        # ============================================================================
        # SECTION 4: SNOOZE & DISMISS METHODS
        # ============================================================================

    def _snooze_alert(self, alert_id, hours):
            """
            Temporarily hide alert for specified hours.
            Updates snoozed_until timestamp.
            """
            try:
                alerts_file = os.path.join(self.data_dir, "alerts.json")

                if not os.path.exists(alerts_file):
                    return False

                with open(alerts_file, 'r') as f:
                    alerts = json.load(f)

                # Calculate snooze end time
                snooze_until = (datetime.now() + timedelta(hours=hours)).isoformat()

                # Find and update alert
                for alert in alerts:
                    if alert.get('alert_id') == alert_id:
                        alert['snoozed_until'] = snooze_until
                        alert['status'] = 'snoozed'
                        break

                with open(alerts_file, 'w') as f:
                    json.dump(alerts, f, indent=2)

                print(f"[Snooze] Alert {alert_id} snoozed for {hours} hours")
                return True

            except Exception as e:
                print(f"[Snooze] Error snoozing alert: {e}")
                return False

    def _dismiss_alert(self, alert_id):
            """
            Permanently dismiss alert.
            Updates dismissed flag and timestamp.
            """
            try:
                alerts_file = os.path.join(self.data_dir, "alerts.json")

                if not os.path.exists(alerts_file):
                    return False

                with open(alerts_file, 'r') as f:
                    alerts = json.load(f)

                for alert in alerts:
                    if alert.get('alert_id') == alert_id:
                        alert['dismissed'] = True
                        alert['dismissed_at'] = datetime.now().isoformat()
                        alert['status'] = 'dismissed'
                        break

                with open(alerts_file, 'w') as f:
                    json.dump(alerts, f, indent=2)

                print(f"[Dismiss] Alert {alert_id} dismissed")
                return True

            except Exception as e:
                print(f"[Dismiss] Error dismissing alert: {e}")
                return False

    def _check_snoozed_alerts(self):
            """
            Check if any snoozed alerts should be reactivated.
            Returns list of reactivated alert IDs.
            """
            try:
                alerts_file = os.path.join(self.data_dir, "alerts.json")

                if not os.path.exists(alerts_file):
                    return []

                with open(alerts_file, 'r') as f:
                    alerts = json.load(f)

                current_time = datetime.now()
                reactivated = []

                for alert in alerts:
                    snooze_until = alert.get('snoozed_until')
                    if snooze_until:
                        snooze_time = datetime.fromisoformat(snooze_until)
                        if current_time >= snooze_time:
                            alert['snoozed_until'] = None
                            alert['status'] = 'unacknowledged'
                            reactivated.append(alert['alert_id'])

                if reactivated:
                    with open(alerts_file, 'w') as f:
                        json.dump(alerts, f, indent=2)
                    print(f"[Snooze] Reactivated {len(reactivated)} alerts")

                return reactivated

            except Exception as e:
                print(f"[Snooze] Error checking snoozed alerts: {e}")
                return []

    def _restore_dismissed_alert(self, alert_id):
            """
            Restore a dismissed alert.
            """
            try:
                alerts_file = os.path.join(self.data_dir, "alerts.json")

                if not os.path.exists(alerts_file):
                    return False

                with open(alerts_file, 'r') as f:
                    alerts = json.load(f)

                for alert in alerts:
                    if alert.get('alert_id') == alert_id:
                        alert['dismissed'] = False
                        alert['dismissed_at'] = None
                        alert['status'] = 'unacknowledged'
                        break

                with open(alerts_file, 'w') as f:
                    json.dump(alerts, f, indent=2)

                return True

            except Exception as e:
                print(f"[Restore] Error restoring alert: {e}")
                return False

        # ============================================================================
        # SECTION 5: FILTERING & SEARCH METHODS
        # ============================================================================

    def _filter_alerts_by_severity(self, alerts, severity):
            """
            Filter alerts by severity level.
            severity: 'all', 'info', 'warning', 'critical'
            """
            if severity == 'all':
                return alerts

            return [alert for alert in alerts if alert.get('severity') == severity]

    def _filter_alerts_by_pool(self, alerts, pool_id):
            """
            Filter alerts by pool ID.
            pool_id: 'all' or specific pool ID
            """
            if pool_id == 'all':
                return alerts

            return [alert for alert in alerts if alert.get('pool_id') == pool_id]

    def _filter_alerts_by_date(self, alerts, start_date, end_date):
            """
            Filter alerts by date range.
            Dates should be datetime objects.
            """
            try:
                filtered = []
                for alert in alerts:
                    alert_time = datetime.fromisoformat(alert['timestamp'])
                    if start_date <= alert_time <= end_date:
                        filtered.append(alert)
                return filtered
            except Exception as e:
                print(f"[Filter] Error filtering by date: {e}")
                return alerts

    def _filter_alerts_by_status(self, alerts, status):
            """
            Filter alerts by acknowledgment status.
            status: 'all', 'unacknowledged', 'acknowledged', 'snoozed', 'dismissed'
            """
            if status == 'all':
                return [alert for alert in alerts if not alert.get('dismissed', False)]
            elif status == 'unacknowledged':
                return [
                    alert for alert in alerts 
                    if alert.get('status') == 'unacknowledged' 
                    and not alert.get('dismissed', False)
                    and not alert.get('snoozed_until')
                ]
            elif status == 'acknowledged':
                return [
                    alert for alert in alerts 
                    if alert.get('status') == 'acknowledged'
                    and not alert.get('dismissed', False)
                ]
            elif status == 'snoozed':
                return [
                    alert for alert in alerts 
                    if alert.get('snoozed_until') 
                    and not alert.get('dismissed', False)
                ]
            elif status == 'dismissed':
                return [alert for alert in alerts if alert.get('dismissed', False)]

            return alerts

    def _search_alerts(self, alerts, search_term):
            """
            Search alerts by text in message, parameter, or pool name.
            Case-insensitive search.
            """
            if not search_term:
                return alerts

            search_term = search_term.lower()
            filtered = []

            for alert in alerts:
                searchable_text = " ".join([
                    alert.get('message', ''),
                    alert.get('parameter', ''),
                    alert.get('pool_name', ''),
                    alert.get('notes', '')
                ]).lower()

                if search_term in searchable_text:
                    filtered.append(alert)

            return filtered

    def _apply_all_filters(self, alerts, severity='all', pool_id='all', 
                            status='all', search_term='', start_date=None, end_date=None):
            """
            Apply all filters in sequence.
            Returns filtered alert list.
            """
            filtered = alerts

            # Apply each filter
            filtered = self._filter_alerts_by_severity(filtered, severity)
            filtered = self._filter_alerts_by_pool(filtered, pool_id)
            filtered = self._filter_alerts_by_status(filtered, status)
            filtered = self._search_alerts(filtered, search_term)

            if start_date and end_date:
                filtered = self._filter_alerts_by_date(filtered, start_date, end_date)

            return filtered


    # ============================================================================
    # PHASE 2.1: PDF REPORT FOUNDATION METHODS
    # ============================================================================

    def _aggregate_pool_data(self, pool_ids, start_date, end_date):
        """
        Aggregate data for specified pools over date range.
        Returns dict of aggregated data per pool.
        """
        try:
            aggregated_data = {}

            # Convert dates to datetime if strings
            if isinstance(start_date, str):
                start_date = datetime.strptime(start_date, '%Y-%m-%d')
            if isinstance(end_date, str):
                end_date = datetime.strptime(end_date, '%Y-%m-%d')

            for pool_id in pool_ids:
                # Get pool info
                pool_data = self._get_pool_data(pool_id)
                if not pool_data:
                    continue

                # Load readings for date range
                readings = self._load_readings_for_range(pool_id, start_date, end_date)

                # Load alerts for date range
                alerts = self._load_alerts_for_range(pool_id, start_date, end_date)

                # Calculate statistics
                statistics = self._calculate_all_statistics(readings)

                # Aggregate maintenance data
                maintenance = self._aggregate_maintenance_data(pool_id, start_date, end_date)

                # Calculate costs
                costs = self._calculate_costs(pool_id, start_date, end_date)

                aggregated_data[pool_id] = {
                    'pool_id': pool_id,
                    'pool_name': pool_data.get('name', pool_id),
                    'pool_type': pool_data.get('type', 'unknown'),
                    'date_range': {
                        'start': start_date.strftime('%Y-%m-%d'),
                        'end': end_date.strftime('%Y-%m-%d')
                    },
                    'readings': readings,
                    'statistics': statistics,
                    'alerts': {
                        'total': len(alerts),
                        'critical': len([a for a in alerts if a.get('severity') == 'critical']),
                        'warning': len([a for a in alerts if a.get('severity') == 'warning']),
                        'info': len([a for a in alerts if a.get('severity') == 'info']),
                        'list': alerts
                    },
                    'maintenance': maintenance,
                    'costs': costs
                }

            return aggregated_data

        except Exception as e:
            print(f"[PDF] Error aggregating pool data: {e}")
            return {}


    def _load_readings_for_range(self, pool_id, start_date, end_date):
        """Load readings for a pool within date range"""
        try:
            readings_file = self.data_dir / "readings.json"
            if not readings_file.exists():
                print(f"[PDF] Readings file not found: {readings_file}")
                return []

            with open(readings_file, 'r') as f:
                data = json.load(f)

            # Handle different data structures
            all_readings = []
            
            # Structure 1: Direct array [{"date": "...", ...}, ...]
            if isinstance(data, list):
                all_readings = data
                print(f"[PDF] Data structure: Direct array with {len(data)} items")
            
            # Structure 2: Dictionary with 'readings' key {"readings": [...]}
            elif isinstance(data, dict):
                if 'readings' in data:
                    all_readings = data['readings']
                    print(f"[PDF] Data structure: Dictionary with 'readings' key, {len(all_readings)} items")
                else:
                    # Structure 3: Dictionary where each key is a pool_id
                    if pool_id in data:
                        all_readings = data[pool_id]
                        print(f"[PDF] Data structure: Dictionary with pool_id keys, {len(all_readings)} items for {pool_id}")
                    else:
                        print(f"[PDF] Data structure: Dictionary but no 'readings' key or pool_id key found")
                        print(f"[PDF] Available keys: {list(data.keys())[:10]}")
                        return []
            else:
                print(f"[PDF] Unknown data structure type: {type(data)}")
                return []

            # Filter by pool and date range
            filtered = []
            for reading in all_readings:
                # Handle both dict and string readings
                if isinstance(reading, str):
                    # Skip string entries (like "timestamp", "readings", etc.)
                    continue
                
                if not isinstance(reading, dict):
                    continue
                
                # If reading has pool_id, check it matches
                reading_pool_id = reading.get('pool_id', pool_id)  # Default to requested pool_id if not present
                if reading_pool_id != pool_id:
                    continue

                # Check date range
                try:
                    reading_date = datetime.strptime(reading['date'], '%Y-%m-%d')
                    if start_date <= reading_date <= end_date:
                        # Add pool_id if missing
                        if 'pool_id' not in reading:
                            reading['pool_id'] = pool_id
                        filtered.append(reading)
                except (KeyError, ValueError) as e:
                    continue

            # Sort by date
            filtered.sort(key=lambda x: x.get('date', ''))

            print(f"[PDF] Loaded {len(filtered)} readings for {pool_id} in date range {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
            return filtered

        except Exception as e:
            print(f"[PDF] Error loading readings: {e}")
            import traceback
            traceback.print_exc()
            return []


    def _load_alerts_for_range(self, pool_id, start_date, end_date):
        """Load alerts for a pool within date range"""
        try:
            alerts_file = self.data_dir / "alerts.json"
            if not alerts_file.exists():
                print(f"[PDF] Alerts file not found: {alerts_file}")
                return []

            with open(alerts_file, 'r') as f:
                data = json.load(f)

            # Handle different data structures
            all_alerts = []
            
            # Structure 1: Direct array
            if isinstance(data, list):
                all_alerts = data
                print(f"[PDF] Alerts structure: Direct array with {len(data)} items")
            
            # Structure 2: Dictionary with 'alerts' key
            elif isinstance(data, dict):
                if 'alerts' in data:
                    all_alerts = data['alerts']
                    print(f"[PDF] Alerts structure: Dictionary with 'alerts' key, {len(all_alerts)} items")
                else:
                    # Structure 3: Dictionary where each key is a pool_id
                    if pool_id in data:
                        all_alerts = data[pool_id]
                        print(f"[PDF] Alerts structure: Dictionary with pool_id keys, {len(all_alerts)} items for {pool_id}")
                    else:
                        print(f"[PDF] Alerts structure: Dictionary but no 'alerts' key or pool_id key found")
                        return []
            else:
                print(f"[PDF] Unknown alerts structure type: {type(data)}")
                return []

            # Filter by pool and date range
            filtered = []
            for alert in all_alerts:
                # Handle both dict and string alerts
                if isinstance(alert, str):
                    continue
                
                if not isinstance(alert, dict):
                    continue
                
                # If alert has pool_id, check it matches
                alert_pool_id = alert.get('pool_id', pool_id)  # Default to requested pool_id if not present
                if alert_pool_id != pool_id:
                    continue

                alert_date = datetime.fromisoformat(alert['timestamp'])
                if start_date <= alert_date <= end_date:
                    filtered.append(alert)

            return filtered

        except Exception as e:
            print(f"[PDF] Error loading alerts: {e}")
            return []


    def _calculate_all_statistics(self, readings):
        """Calculate statistics for all parameters"""
        try:
            if not readings:
                return {}

            parameters = ['ph', 'free_chlorine', 'total_chlorine', 'alkalinity', 
                         'calcium_hardness', 'cyanuric_acid', 'salt', 'temperature']

            statistics = {}

            for param in parameters:
                values = [r.get(param) for r in readings if r.get(param) is not None]
                if values:
                    statistics[param] = self._calculate_parameter_statistics(values, param)

            return statistics

        except Exception as e:
            print(f"[PDF] Error calculating statistics: {e}")
            return {}


    def _calculate_parameter_statistics(self, values, parameter):
        """Calculate statistics for a single parameter"""
        try:
            if not values:
                return {}

            # Basic statistics
            avg = sum(values) / len(values)
            sorted_values = sorted(values)
            min_val = sorted_values[0]
            max_val = sorted_values[-1]

            # Median
            n = len(sorted_values)
            if n % 2 == 0:
                median = (sorted_values[n//2 - 1] + sorted_values[n//2]) / 2
            else:
                median = sorted_values[n//2]

            # Standard deviation
            variance = sum((x - avg) ** 2 for x in values) / len(values)
            std_dev = variance ** 0.5

            # In-range percentage (using default ranges)
            ranges = {
                'ph': (7.2, 7.8),
                'free_chlorine': (1.0, 3.0),
                'total_chlorine': (1.0, 3.0),
                'alkalinity': (80, 120),
                'calcium_hardness': (200, 400),
                'cyanuric_acid': (30, 50),
                'salt': (2700, 3400),
                'temperature': (78, 104)
            }

            if parameter in ranges:
                min_range, max_range = ranges[parameter]
                in_range = sum(1 for v in values if min_range <= v <= max_range)
                in_range_percent = (in_range / len(values)) * 100
            else:
                in_range_percent = 0

            return {
                'avg': round(avg, 2),
                'min': round(min_val, 2),
                'max': round(max_val, 2),
                'median': round(median, 2),
                'std_dev': round(std_dev, 2),
                'in_range_percent': round(in_range_percent, 1),
                'count': len(values)
            }

        except Exception as e:
            print(f"[PDF] Error calculating parameter statistics: {e}")
            return {}


    def _aggregate_maintenance_data(self, pool_id, start_date, end_date):
        """Aggregate maintenance data for date range"""
        try:
            # This would load from maintenance log if available
            # For now, return placeholder
            return {
                'tasks_completed': 0,
                'chemicals_added': {},
                'equipment_serviced': []
            }

        except Exception as e:
            print(f"[PDF] Error aggregating maintenance: {e}")
            return {}


    def _calculate_costs(self, pool_id, start_date, end_date):
        """Calculate costs for date range"""
        try:
            # This would calculate from cost tracking if available
            # For now, return placeholder
            return {
                'chemicals': 0.0,
                'maintenance': 0.0,
                'equipment': 0.0,
                'total': 0.0
            }

        except Exception as e:
            print(f"[PDF] Error calculating costs: {e}")
            return {}

    # ============================================================================
    # SECTION 2: CHART GENERATION METHODS
    # ============================================================================


    def _generate_chart(self, chart_type, data, options=None):
        """
        Generate a chart image for inclusion in PDF.
        Returns BytesIO object containing PNG image.
        """
        try:
            if not MATPLOTLIB_AVAILABLE:
                print("[PDF] Matplotlib not available - cannot generate charts")
                return None

            if options is None:
                options = {}

            # Create figure
            fig = Figure(figsize=(8, 4), dpi=100)
            ax = fig.add_subplot(111)

            # Generate chart based on type
            if chart_type == 'line':
                self._generate_line_chart(ax, data, options)
            elif chart_type == 'bar':
                self._generate_bar_chart(ax, data, options)
            elif chart_type == 'pie':
                self._generate_pie_chart(ax, data, options)
            elif chart_type == 'area':
                self._generate_area_chart(ax, data, options)
            else:
                print(f"[PDF] Unknown chart type: {chart_type}")
                return None

            # Save to BytesIO
            img_buffer = io.BytesIO()
            fig.savefig(img_buffer, format='png', bbox_inches='tight', dpi=100)
            img_buffer.seek(0)

            plt.close(fig)

            return img_buffer

        except Exception as e:
            print(f"[PDF] Error generating chart: {e}")
            return None


    def _generate_line_chart(self, ax, data, options):
        """Generate a line chart"""
        try:
            # Extract data
            dates = data.get('dates', [])
            series = data.get('series', {})

            # Convert dates to datetime
            if dates and isinstance(dates[0], str):
                dates = [datetime.strptime(d, '%Y-%m-%d') for d in dates]

            # Plot each series
            for label, values in series.items():
                ax.plot(dates, values, label=label, marker='o', linewidth=2)

            # Formatting
            ax.set_xlabel(options.get('xlabel', 'Date'))
            ax.set_ylabel(options.get('ylabel', 'Value'))
            ax.set_title(options.get('title', 'Chart'), fontsize=14, fontweight='bold')
            ax.legend(loc='best')
            ax.grid(True, alpha=0.3)

            # Format x-axis dates
            if dates:
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
                ax.xaxis.set_major_locator(mdates.AutoDateLocator())
                plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')

            # Add reference range if provided
            if 'range' in options:
                min_val, max_val = options['range']
                ax.axhspan(min_val, max_val, alpha=0.2, color='green', label='Ideal Range')

        except Exception as e:
            print(f"[PDF] Error generating line chart: {e}")


    def _generate_bar_chart(self, ax, data, options):
        """Generate a bar chart"""
        try:
            categories = data.get('categories', [])
            values = data.get('values', [])

            ax.bar(categories, values, color=options.get('color', 'steelblue'))

            ax.set_xlabel(options.get('xlabel', 'Category'))
            ax.set_ylabel(options.get('ylabel', 'Value'))
            ax.set_title(options.get('title', 'Chart'), fontsize=14, fontweight='bold')
            ax.grid(True, alpha=0.3, axis='y')

            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')

        except Exception as e:
            print(f"[PDF] Error generating bar chart: {e}")


    def _generate_pie_chart(self, ax, data, options):
        """Generate a pie chart"""
        try:
            labels = data.get('labels', [])
            values = data.get('values', [])
            colors_list = options.get('colors', None)

            ax.pie(values, labels=labels, autopct='%1.1f%%', colors=colors_list, startangle=90)
            ax.set_title(options.get('title', 'Chart'), fontsize=14, fontweight='bold')

        except Exception as e:
            print(f"[PDF] Error generating pie chart: {e}")


    def _generate_area_chart(self, ax, data, options):
        """Generate an area chart"""
        try:
            dates = data.get('dates', [])
            values = data.get('values', [])

            if dates and isinstance(dates[0], str):
                dates = [datetime.strptime(d, '%Y-%m-%d') for d in dates]

            ax.fill_between(dates, values, alpha=0.3, color=options.get('color', 'steelblue'))
            ax.plot(dates, values, color=options.get('color', 'steelblue'), linewidth=2)

            ax.set_xlabel(options.get('xlabel', 'Date'))
            ax.set_ylabel(options.get('ylabel', 'Value'))
            ax.set_title(options.get('title', 'Chart'), fontsize=14, fontweight='bold')
            ax.grid(True, alpha=0.3)

            if dates:
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
                plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')

        except Exception as e:
            print(f"[PDF] Error generating area chart: {e}")


    def _generate_chemical_trend_chart(self, pool_data):
        """
        Generate chemical trend chart for a pool.
        Returns path to saved chart image.
        """
        try:
            import matplotlib
            matplotlib.use('Agg')  # Use non-interactive backend
            import matplotlib.pyplot as plt
            from matplotlib.dates import DateFormatter
            import matplotlib.dates as mdates
            
            readings = pool_data.get('readings', [])
            if not readings:
                print(f"[PDF] No readings available for chemical trend chart")
                return None
            
            # Create figure
            fig, ax = plt.subplots(figsize=(10, 6))
            
            # Extract dates and chemical values
            dates = []
            ph_values = []
            chlorine_values = []
            alkalinity_values = []
            
            for reading in readings:
                try:
                    date_str = reading.get('date', '')
                    if date_str:
                        dates.append(datetime.strptime(date_str, '%Y-%m-%d'))
                        ph_values.append(reading.get('ph', 0))
                        chlorine_values.append(reading.get('free_chlorine', 0))
                        alkalinity_values.append(reading.get('alkalinity', 0))
                except Exception as e:
                    continue
            
            if not dates:
                print(f"[PDF] No valid dates found for chemical trend chart")
                plt.close(fig)
                return None
            
            # Plot chemical trends
            ax.plot(dates, ph_values, marker='o', label='pH', linewidth=2)
            ax.plot(dates, [c/10 for c in chlorine_values], marker='s', label='Chlorine (÷10)', linewidth=2)
            ax.plot(dates, [a/100 for a in alkalinity_values], marker='^', label='Alkalinity (÷100)', linewidth=2)
            
            # Format chart
            ax.set_xlabel('Date', fontsize=12, fontweight='bold')
            ax.set_ylabel('Values (Scaled)', fontsize=12, fontweight='bold')
            ax.set_title(f"Chemical Trends - {pool_data.get('pool_name', 'Pool')}", 
                        fontsize=14, fontweight='bold', pad=20)
            ax.legend(loc='best', fontsize=10)
            ax.grid(True, alpha=0.3)
            
            # Format x-axis dates
            ax.xaxis.set_major_formatter(DateFormatter('%m/%d'))
            plt.xticks(rotation=45)
            
            # Tight layout
            plt.tight_layout()
            
            # Save chart
            chart_path = self.data_dir / f"chart_chemical_trend_{pool_data.get('pool_id', 'unknown')}.png"
            plt.savefig(chart_path, dpi=150, bbox_inches='tight')
            plt.close(fig)
            
            print(f"[PDF] Chemical trend chart saved: {chart_path}")
            return str(chart_path)
            
        except Exception as e:
            print(f"[PDF] Error generating chemical trend chart: {e}")
            import traceback
            traceback.print_exc()
            return None


    def _generate_alert_frequency_chart(self, pool_data):
        """
        Generate alert frequency chart for a pool.
        Returns path to saved chart image.
        """
        try:
            import matplotlib
            matplotlib.use('Agg')  # Use non-interactive backend
            import matplotlib.pyplot as plt
            
            alerts = pool_data.get('alerts', {})
            if not alerts or alerts.get('total', 0) == 0:
                print(f"[PDF] No alerts available for frequency chart")
                return None
            
            # Create figure
            fig, ax = plt.subplots(figsize=(8, 6))
            
            # Prepare data
            categories = ['Critical', 'Warning', 'Info']
            values = [
                alerts.get('critical', 0),
                alerts.get('warning', 0),
                alerts.get('info', 0)
            ]
            colors = ['#e74c3c', '#f39c12', '#3498db']
            
            # Create bar chart
            bars = ax.bar(categories, values, color=colors, alpha=0.7, edgecolor='black', linewidth=1.5)
            
            # Add value labels on bars
            for bar in bars:
                height = bar.get_height()
                if height > 0:
                    ax.text(bar.get_x() + bar.get_width()/2., height,
                           f'{int(height)}',
                           ha='center', va='bottom', fontsize=12, fontweight='bold')
            
            # Format chart
            ax.set_xlabel('Alert Severity', fontsize=12, fontweight='bold')
            ax.set_ylabel('Number of Alerts', fontsize=12, fontweight='bold')
            ax.set_title(f"Alert Frequency - {pool_data.get('pool_name', 'Pool')}", 
                        fontsize=14, fontweight='bold', pad=20)
            ax.grid(True, alpha=0.3, axis='y')
            
            # Set y-axis to start at 0
            ax.set_ylim(bottom=0)
            
            # Tight layout
            plt.tight_layout()
            
            # Save chart
            chart_path = self.data_dir / f"chart_alert_frequency_{pool_data.get('pool_id', 'unknown')}.png"
            plt.savefig(chart_path, dpi=150, bbox_inches='tight')
            plt.close(fig)
            
            print(f"[PDF] Alert frequency chart saved: {chart_path}")
            return str(chart_path)
            
        except Exception as e:
            print(f"[PDF] Error generating alert frequency chart: {e}")
            import traceback
            traceback.print_exc()
            return None


    def _generate_chemical_trend_chart(self, pool_data):
        """Generate chemical trend chart for a pool"""
        try:
            readings = pool_data.get('readings', [])
            if not readings:
                return None

            # Extract dates and values
            dates = [r['date'] for r in readings]
            ph_values = [r.get('ph') for r in readings if r.get('ph') is not None]
            chlorine_values = [r.get('free_chlorine') for r in readings if r.get('free_chlorine') is not None]
            alkalinity_values = [r.get('alkalinity') for r in readings if r.get('alkalinity') is not None]

            # Prepare data
            data = {
                'dates': dates[:len(ph_values)],  # Match shortest series
                'series': {}
            }

            if ph_values:
                data['series']['pH'] = ph_values
            if chlorine_values:
                data['series']['Chlorine'] = chlorine_values

            options = {
                'title': f"Chemical Trends - {pool_data['pool_name']}",
                'xlabel': 'Date',
                'ylabel': 'Value',
                'range': (7.2, 7.8)  # pH range
            }

            return self._generate_chart('line', data, options)

        except Exception as e:
            print(f"[PDF] Error generating chemical trend chart: {e}")
            return None


    def _generate_pdf_report(self, pool_ids, start_date, end_date, template_name, options=None):
        """
        Main entry point for PDF report generation.
        Returns path to generated PDF file.
        """
        try:
            if not REPORTLAB_AVAILABLE:
                print("[PDF] ReportLab not available - cannot generate PDF")
                return None

            if options is None:
                options = {}

            print(f"[PDF] Generating report for pools: {pool_ids}")
            print(f"[PDF] Date range: {start_date} to {end_date}")
            print(f"[PDF] Template: {template_name}")

            # Step 1: Aggregate data
            print("[PDF] Step 1: Aggregating data...")
            aggregated_data = self._aggregate_pool_data(pool_ids, start_date, end_date)

            if not aggregated_data:
                print("[PDF] No data available for selected pools/dates")
                return None

            # Step 2: Generate charts
            print("[PDF] Step 2: Generating charts...")
            charts = {}
            if options.get('include_charts', True):
                for pool_id, pool_data in aggregated_data.items():
                    charts[pool_id] = {
                        'chemical_trend': self._generate_chemical_trend_chart(pool_data),
                        'alert_frequency': self._generate_alert_frequency_chart(pool_data)
                    }

            # Step 3: Build PDF
            print("[PDF] Step 3: Building PDF document...")
            pdf_path = self._build_pdf_document(template_name, aggregated_data, charts, options)

            if pdf_path:
                print(f"[PDF] Report generated successfully: {pdf_path}")

            return pdf_path

        except Exception as e:
            print(f"[PDF] Error generating PDF report: {e}")
            import traceback
            traceback.print_exc()
            return None


    def _build_pdf_document(self, template_name, aggregated_data, charts, options):
        """
        Build PDF document using template and data.
        Returns path to generated PDF file.
        """
        try:
            # Create reports directory
            reports_dir = self.data_dir / "reports"
            reports_dir.mkdir(exist_ok=True)

            # Create year/month subdirectories
            now = datetime.now()
            year_dir = reports_dir / str(now.year)
            year_dir.mkdir(exist_ok=True)
            month_dir = year_dir / f"{now.month:02d}"
            month_dir.mkdir(exist_ok=True)

            # Generate filename
            timestamp = now.strftime("%Y%m%d_%H%M%S")
            pool_count = len(aggregated_data)
            filename = f"RPT_{timestamp}_{template_name}_{pool_count}pools.pdf"
            pdf_path = month_dir / filename

            # Create PDF document
            doc = SimpleDocTemplate(
                str(pdf_path),
                pagesize=letter,
                rightMargin=0.75*inch,
                leftMargin=0.75*inch,
                topMargin=0.75*inch,
                bottomMargin=0.75*inch
            )

            # Build content based on template
            story = []

            if template_name == 'executive_summary':
                story = self._build_executive_summary(aggregated_data, charts, options)
            elif template_name == 'detailed_technical':
                story = self._build_detailed_technical(aggregated_data, charts, options)
            elif template_name == 'maintenance_schedule':
                story = self._build_maintenance_schedule(aggregated_data, charts, options)
            else:
                # Default template
                story = self._build_executive_summary(aggregated_data, charts, options)

            # Build PDF
            doc.build(story, onFirstPage=self._create_professional_page, onLaterPages=self._create_professional_page)

            return str(pdf_path)

        except Exception as e:
            print(f"[PDF] Error building PDF document: {e}")
            import traceback
            traceback.print_exc()
            return None


    def _add_page_number(self, canvas_obj, doc):
        """Add page number to PDF pages"""
        try:
            page_num = canvas_obj.getPageNumber()
            text = f"Page {page_num}"
            canvas_obj.saveState()
            canvas_obj.setFont('Helvetica', 9)
            canvas_obj.drawRightString(7.5*inch, 0.5*inch, text)
            canvas_obj.restoreState()
        except Exception as e:
            print(f"[PDF] Error adding page number: {e}")

    def _create_professional_page(self, canvas_obj, doc):
        """Create professional page with header and footer."""
        try:
            # Get logo path
            logo_path = self.data_dir / "logo.png"
            logo_path_str = str(logo_path) if logo_path.exists() else None
            
            # Add header
            self._create_professional_header(canvas_obj, doc, logo_path_str)
            
            # Add footer
            self._create_professional_footer(canvas_obj, doc)
            
        except Exception as e:
            print(f"[PDF] Error creating professional page: {e}")

    # ============================================================================
    # SECTION 4: TEMPLATE RENDERING METHODS
    # ============================================================================


    def _build_executive_summary(self, aggregated_data, charts, options):
        """Build Executive Summary template"""
        try:
            story = []
            
            # Add professional cover page
            story.extend(self._create_cover_page(aggregated_data, options))
            styles = getSampleStyleSheet()

            # Custom styles
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#2C3E50'),
                spaceAfter=30,
                alignment=TA_CENTER
            )

            heading_style = ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading2'],
                fontSize=16,
                textColor=colors.HexColor('#34495E'),
                spaceAfter=12,
                spaceBefore=12
            )

            # Cover Page
            story.append(Spacer(1, 2*inch))
            story.append(Paragraph("Pool Chemistry Report", title_style))
            story.append(Paragraph("Executive Summary", styles['Heading2']))
            story.append(Spacer(1, 0.5*inch))

            # Date range
            if aggregated_data:
                first_pool = list(aggregated_data.values())[0]
                date_range = first_pool['date_range']
                story.append(Paragraph(
                    f"Report Period: {date_range['start']} to {date_range['end']}",
                    styles['Normal']
                ))

            story.append(Spacer(1, 0.3*inch))
            story.append(Paragraph(
                f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}",
                styles['Normal']
            ))

            story.append(PageBreak())

            # Executive Summary Section
            story.append(Paragraph("Executive Summary", heading_style))
            story.append(Spacer(1, 0.2*inch))

            # Overall status
            total_pools = len(aggregated_data)
            total_alerts = sum(pool['alerts']['total'] for pool in aggregated_data.values())
            critical_alerts = sum(pool['alerts']['critical'] for pool in aggregated_data.values())

            summary_text = f"""
            This report covers {total_pools} pool(s) for the specified period. 
            A total of {total_alerts} alerts were recorded, including {critical_alerts} critical alerts.
            """
            story.append(Paragraph(summary_text, styles['Normal']))
            story.append(Spacer(1, 0.3*inch))

            # Pool Status Overview
            story.append(Paragraph("Pool Status Overview", heading_style))
            story.append(Spacer(1, 0.2*inch))

            for pool_id, pool_data in aggregated_data.items():
                story.append(Paragraph(f"<b>{pool_data['pool_name']}</b>", styles['Heading3']))

                # Status table
                stats = pool_data['statistics']
                table_data = [
                    ['Parameter', 'Average', 'Min', 'Max', 'In Range %']
                ]

                for param, stat in stats.items():
                    if stat:
                        table_data.append([
                            param.replace('_', ' ').title(),
                            f"{stat.get('avg', 0):.2f}",
                            f"{stat.get('min', 0):.2f}",
                            f"{stat.get('max', 0):.2f}",
                            f"{stat.get('in_range_percent', 0):.1f}%"
                        ])

                if len(table_data) > 1:
                    table = Table(table_data, colWidths=[2*inch, 1*inch, 1*inch, 1*inch, 1*inch])
                    table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498DB')),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, 0), 12),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black)
                    ]))
                    story.append(table)

                story.append(Spacer(1, 0.3*inch))

                # Add charts if available
                if charts.get(pool_id):
                    pool_charts = charts[pool_id]

                    if pool_charts.get('chemical_trend'):
                        story.append(Paragraph("Chemical Trends", styles['Heading4']))
                        img = Image(pool_charts['chemical_trend'], width=6*inch, height=3*inch)
                        story.append(img)
                        story.append(Spacer(1, 0.2*inch))

                    if pool_charts.get('alert_frequency'):
                        story.append(Paragraph("Alert Frequency", styles['Heading4']))
                        img = Image(pool_charts['alert_frequency'], width=6*inch, height=3*inch)
                        story.append(img)
                        story.append(Spacer(1, 0.2*inch))

                story.append(PageBreak())

            # Recommendations Section
            story.append(Paragraph("Recommendations", heading_style))
            story.append(Spacer(1, 0.2*inch))

            recommendations = self._generate_recommendations_list(aggregated_data)
            for rec in recommendations:
                story.append(Paragraph(f"• {rec}", styles['Normal']))
                story.append(Spacer(1, 0.1*inch))

            return story

        except Exception as e:
            print(f"[PDF] Error building executive summary: {e}")
            import traceback
            traceback.print_exc()
            return []


    def _build_detailed_technical(self, aggregated_data, charts, options):
        """Build Detailed Technical template"""
        try:
            # For now, use executive summary as base
            # This would be expanded with more technical details
            story = self._build_executive_summary(aggregated_data, charts, options)

            # Add technical appendices
            styles = getSampleStyleSheet()
            story.append(PageBreak())
            story.append(Paragraph("Technical Appendix", styles['Heading2']))
            story.append(Paragraph("Detailed parameter analysis and raw data tables would appear here.", styles['Normal']))

            return story

        except Exception as e:
            print(f"[PDF] Error building detailed technical: {e}")
            return []


    def _build_maintenance_schedule(self, aggregated_data, charts, options):
        """Build Maintenance Schedule template"""
        try:
            story = []
            styles = getSampleStyleSheet()

            # Title
            story.append(Spacer(1, 1*inch))
            story.append(Paragraph("Maintenance Schedule Report", styles['Title']))
            story.append(Spacer(1, 0.5*inch))

            # Content
            story.append(Paragraph("Scheduled Maintenance Tasks", styles['Heading2']))
            story.append(Paragraph("Maintenance schedule and task tracking would appear here.", styles['Normal']))

            return story

        except Exception as e:
            print(f"[PDF] Error building maintenance schedule: {e}")
            return []



    def _generate_recommendations_list(self, aggregated_data):
        """
        Generate recommendations list for PDF reports.
        Returns list of recommendation strings.
        """
        try:
            recommendations = []
            
            for pool_id, pool_data in aggregated_data.items():
                pool_name = pool_data.get('pool_name', pool_id)
                statistics = pool_data.get('statistics', {})
                
                # Check pH
                ph_avg = statistics.get('ph', {}).get('avg', 0)
                if ph_avg > 0:
                    if ph_avg < 7.2:
                        recommendations.append(f"{pool_name}: pH is low ({ph_avg:.1f}). Add pH increaser.")
                    elif ph_avg > 7.8:
                        recommendations.append(f"{pool_name}: pH is high ({ph_avg:.1f}). Add pH decreaser.")
                    else:
                        recommendations.append(f"{pool_name}: pH is optimal ({ph_avg:.1f}).")
                
                # Check chlorine
                chlorine_avg = statistics.get('free_chlorine', {}).get('avg', 0)
                if chlorine_avg > 0:
                    if chlorine_avg < 1.0:
                        recommendations.append(f"{pool_name}: Chlorine is low ({chlorine_avg:.1f} ppm). Add chlorine.")
                    elif chlorine_avg > 5.0:
                        recommendations.append(f"{pool_name}: Chlorine is high ({chlorine_avg:.1f} ppm). Reduce chlorine.")
                    else:
                        recommendations.append(f"{pool_name}: Chlorine is optimal ({chlorine_avg:.1f} ppm).")
                
                # Check alkalinity
                alkalinity_avg = statistics.get('alkalinity', {}).get('avg', 0)
                if alkalinity_avg > 0:
                    if alkalinity_avg < 80:
                        recommendations.append(f"{pool_name}: Alkalinity is low ({alkalinity_avg:.0f} ppm). Add alkalinity increaser.")
                    elif alkalinity_avg > 120:
                        recommendations.append(f"{pool_name}: Alkalinity is high ({alkalinity_avg:.0f} ppm). Add pH decreaser.")
                    else:
                        recommendations.append(f"{pool_name}: Alkalinity is optimal ({alkalinity_avg:.0f} ppm).")
                
                # Check alerts
                alerts = pool_data.get('alerts', {})
                critical_count = alerts.get('critical', 0)
                if critical_count > 0:
                    recommendations.append(f"{pool_name}: {critical_count} critical alerts require immediate attention.")
            
            if not recommendations:
                recommendations.append("All pools are within optimal ranges. Continue regular maintenance.")
            
            return recommendations
            
        except Exception as e:
            print(f"[PDF] Error generating recommendations: {e}")
            return ["Unable to generate recommendations. Please check pool data."]




    def _create_professional_header(self, canvas_obj, doc, logo_path=None):
        """
        Create professional header with logo for PDF pages.
        """
        try:
            from reportlab.lib.colors import HexColor
        
            # Deep Blue color scheme
            DEEP_BLUE = HexColor('#1e3a8a')
            LIGHT_BLUE = HexColor('#3b82f6')
        
            canvas_obj.saveState()
        
            # Draw header background
            canvas_obj.setFillColor(DEEP_BLUE)
            canvas_obj.rect(0.5*inch, 10.5*inch, 7.5*inch, 0.5*inch, fill=1, stroke=0)
        
            # Add logo if available
            if logo_path and Path(logo_path).exists():
                try:
                    canvas_obj.drawImage(logo_path, 0.75*inch, 10.6*inch, 
                                       width=0.4*inch, height=0.4*inch, 
                                       preserveAspectRatio=True, mask='auto')
                except:
                    pass
        
            # Add company name
            canvas_obj.setFillColor(colors.white)
            canvas_obj.setFont('Helvetica-Bold', 14)
            canvas_obj.drawString(1.25*inch, 10.65*inch, "Deep Blue Pool Chemistry")
        
            # Add page number
            page_num = canvas_obj.getPageNumber()
            canvas_obj.setFont('Helvetica', 10)
            canvas_obj.drawRightString(7.75*inch, 10.65*inch, f"Page {page_num}")
        
            canvas_obj.restoreState()
        
        except Exception as e:
            print(f"[PDF] Error creating header: {e}")


    def _create_professional_footer(self, canvas_obj, doc):
        """
        Create professional footer for PDF pages.
        """
        try:
            from reportlab.lib.colors import HexColor
        
            LIGHT_GRAY = HexColor('#9ca3af')
            DARK_GRAY = HexColor('#374151')
        
            canvas_obj.saveState()
        
            # Draw footer line
            canvas_obj.setStrokeColor(LIGHT_GRAY)
            canvas_obj.setLineWidth(1)
            canvas_obj.line(0.75*inch, 0.75*inch, 7.75*inch, 0.75*inch)
        
            # Add footer text
            canvas_obj.setFillColor(DARK_GRAY)
            canvas_obj.setFont('Helvetica', 8)
        
            # Left side - company info
            canvas_obj.drawString(0.75*inch, 0.5*inch, 
                                "Deep Blue Pool Chemistry Management System")
        
            # Right side - date
            from datetime import datetime
            date_str = datetime.now().strftime("%B %d, %Y")
            canvas_obj.drawRightString(7.75*inch, 0.5*inch, date_str)
        
            canvas_obj.restoreState()
        
        except Exception as e:
            print(f"[PDF] Error creating footer: {e}")


    def _create_cover_page(self, aggregated_data, options):
        """
        Create professional cover page with logo.
        """
        try:
            from reportlab.lib.colors import HexColor
            from reportlab.platypus import Spacer, Paragraph, PageBreak
            from reportlab.lib.styles import ParagraphStyle
            from reportlab.lib.enums import TA_CENTER
        
            story = []
        
            # Deep Blue colors
            DEEP_BLUE = HexColor('#1e3a8a')
            LIGHT_BLUE = HexColor('#3b82f6')
        
            # Add logo if available
            logo_path = self.data_dir / "logo.png"
            if logo_path.exists():
                try:
                    from reportlab.platypus import Image as RLImage
                    logo = RLImage(str(logo_path), width=2*inch, height=2*inch)
                    story.append(logo)
                    story.append(Spacer(1, 0.5*inch))
                except:
                    pass
            else:
                story.append(Spacer(1, 2*inch))
        
            # Title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=getSampleStyleSheet()['Heading1'],
                fontSize=28,
                textColor=DEEP_BLUE,
                spaceAfter=30,
                alignment=TA_CENTER,
                fontName='Helvetica-Bold'
            )
        
            story.append(Paragraph("POOL CHEMISTRY REPORT", title_style))
            story.append(Spacer(1, 0.3*inch))
        
            # Subtitle
            subtitle_style = ParagraphStyle(
                'CustomSubtitle',
                parent=getSampleStyleSheet()['Heading2'],
                fontSize=18,
                textColor=LIGHT_BLUE,
                spaceAfter=20,
                alignment=TA_CENTER,
                fontName='Helvetica'
            )
        
            template_names = {
                'executive_summary': 'Executive Summary',
                'detailed_technical': 'Detailed Technical Report',
                'maintenance_schedule': 'Maintenance Schedule'
            }
            template_name = options.get('template', 'executive_summary')
            story.append(Paragraph(template_names.get(template_name, 'Report'), subtitle_style))
        
            story.append(Spacer(1, 1*inch))
        
            # Report details
            details_style = ParagraphStyle(
                'Details',
                parent=getSampleStyleSheet()['Normal'],
                fontSize=12,
                textColor=colors.black,
                spaceAfter=10,
                alignment=TA_CENTER,
                fontName='Helvetica'
            )
        
            # Date range
            date_range = options.get('date_range', {})
            start_date = date_range.get('start', 'N/A')
            end_date = date_range.get('end', 'N/A')
            story.append(Paragraph(f"<b>Report Period:</b> {start_date} to {end_date}", details_style))
        
            # Pool count
            pool_count = len(aggregated_data)
            pool_names = [data.get('pool_name', 'Unknown') for data in aggregated_data.values()]
            story.append(Paragraph(f"<b>Pools Monitored:</b> {pool_count}", details_style))
            story.append(Paragraph(f"<b>Pool Names:</b> {', '.join(pool_names)}", details_style))
        
            story.append(Spacer(1, 1*inch))
        
            # Generated date
            from datetime import datetime
            gen_date = datetime.now().strftime("%B %d, %Y at %I:%M %p")
            story.append(Paragraph(f"<b>Generated:</b> {gen_date}", details_style))
        
            story.append(Spacer(1, 1*inch))
        
            # Footer text
            footer_style = ParagraphStyle(
                'Footer',
                parent=getSampleStyleSheet()['Normal'],
                fontSize=10,
                textColor=colors.grey,
                alignment=TA_CENTER,
                fontName='Helvetica-Oblique'
            )
        
            story.append(Paragraph("Prepared by Deep Blue Pool Chemistry Management System", footer_style))
            story.append(Paragraph("Professional Pool Monitoring & Analytics", footer_style))
        
            # Page break
            story.append(PageBreak())
        
            return story
        
        except Exception as e:
            print(f"[PDF] Error creating cover page: {e}")
            return []


    def _create_styled_table(self, data, col_widths=None, style_name='default'):
        """
        Create professionally styled table.
        """
        try:
            from reportlab.lib.colors import HexColor
            from reportlab.platypus import Table, TableStyle
        
            # Deep Blue colors
            DEEP_BLUE = HexColor('#1e3a8a')
            LIGHT_BLUE = HexColor('#3b82f6')
            ACCENT_BLUE = HexColor('#60a5fa')
            LIGHT_GRAY = HexColor('#f3f4f6')
        
            # Create table
            table = Table(data, colWidths=col_widths)
        
            # Apply style
            if style_name == 'default':
                style = TableStyle([
                    # Header row
                    ('BACKGROUND', (0, 0), (-1, 0), DEEP_BLUE),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 11),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('TOPPADDING', (0, 0), (-1, 0), 12),
                
                    # Data rows
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 1), (-1, -1), 10),
                    ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
                    ('TOPPADDING', (0, 1), (-1, -1), 8),
                
                    # Alternating row colors
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, LIGHT_GRAY]),
                
                    # Grid
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                    ('BOX', (0, 0), (-1, -1), 1, DEEP_BLUE),
                
                    # Alignment
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ])
        
            table.setStyle(style)
            return table
        
        except Exception as e:
            print(f"[PDF] Error creating styled table: {e}")
            return None


    def _send_report_email(self, pdf_path, recipients, subject=None, body=None):
        """
        Send PDF report via email.
        """
        try:
            import smtplib
            from email.mime.multipart import MIMEMultipart
            from email.mime.text import MIMEText
            from email.mime.application import MIMEApplication
            from pathlib import Path
        
            # Get email configuration
            email_config = self._load_email_config()
            if not email_config:
                print("[EMAIL] Email not configured")
                return False
        
            # Create message
            msg = MIMEMultipart()
            msg['From'] = email_config.get('from_email')
            msg['To'] = ', '.join(recipients) if isinstance(recipients, list) else recipients
            msg['Subject'] = subject or "Pool Chemistry Report"
        
            # Email body
            if not body:
                body = f"""
                <html>
                <body style="font-family: Arial, sans-serif;">
                    <div style="background-color: #1e3a8a; color: white; padding: 20px; text-align: center;">
                        <h1>Deep Blue Pool Chemistry</h1>
                        <p>Professional Pool Monitoring & Analytics</p>
                    </div>
                
                    <div style="padding: 20px;">
                        <h2>Pool Chemistry Report</h2>
                        <p>Please find attached your pool chemistry report.</p>
                    
                        <p>This report includes:</p>
                        <ul>
                            <li>Current water chemistry readings</li>
                            <li>Trend analysis and predictions</li>
                            <li>Professional recommendations</li>
                            <li>Alert summary</li>
                        </ul>
                    
                        <p>If you have any questions, please don't hesitate to contact us.</p>
                    
                        <p>Best regards,<br>
                        Deep Blue Pool Chemistry Team</p>
                    </div>
                
                    <div style="background-color: #f3f4f6; padding: 10px; text-align: center; font-size: 12px; color: #6b7280;">
                        <p>This is an automated message from Deep Blue Pool Chemistry Management System</p>
                    </div>
                </body>
                </html>
                """
        
            msg.attach(MIMEText(body, 'html'))
        
            # Attach PDF
            with open(pdf_path, 'rb') as f:
                pdf_attachment = MIMEApplication(f.read(), _subtype='pdf')
                pdf_filename = Path(pdf_path).name
                pdf_attachment.add_header('Content-Disposition', 'attachment', filename=pdf_filename)
                msg.attach(pdf_attachment)
        
            # Send email
            smtp_server = email_config.get('smtp_server', 'smtp.gmail.com')
            smtp_port = email_config.get('smtp_port', 587)
            username = email_config.get('username')
            password = email_config.get('password')
        
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(username, password)
                server.send_message(msg)
        
            print(f"[EMAIL] Report sent successfully to {recipients}")
            return True
        
        except Exception as e:
            print(f"[EMAIL] Error sending email: {e}")
            import traceback
            traceback.print_exc()
            return False


    def _load_email_config(self):
        """Load email configuration from file."""
        try:
            config_file = self.data_dir / "email_config.json"
            if config_file.exists():
                with open(config_file, 'r') as f:
                    return json.load(f)
            return None
        except Exception as e:
            print(f"[EMAIL] Error loading email config: {e}")
            return None


    def _save_email_config(self, config):
        """Save email configuration to file."""
        try:
            config_file = self.data_dir / "email_config.json"
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
            print("[EMAIL] Email configuration saved")
            return True
        except Exception as e:
            print(f"[EMAIL] Error saving email config: {e}")
            return False


    def _create_email_config_dialog(self):
        """Create dialog for email configuration."""
        try:
            dialog = tk.Toplevel(self.root)
            dialog.title("Email Configuration")
            dialog.geometry("500x400")
            dialog.configure(bg='#2c3e50')
        
            # Load existing config
            config = self._load_email_config() or {}
        
            # Title
            tk.Label(
                dialog,
                text="Email Configuration",
                font=('Helvetica', 16, 'bold'),
                bg='#2c3e50',
                fg='white'
            ).pack(pady=20)
        
            # Form frame
            form_frame = tk.Frame(dialog, bg='#2c3e50')
            form_frame.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)
        
            # SMTP Server
            tk.Label(form_frame, text="SMTP Server:", bg='#2c3e50', fg='white').grid(row=0, column=0, sticky='w', pady=5)
            smtp_server = tk.Entry(form_frame, width=40)
            smtp_server.insert(0, config.get('smtp_server', 'smtp.gmail.com'))
            smtp_server.grid(row=0, column=1, pady=5)
        
            # SMTP Port
            tk.Label(form_frame, text="SMTP Port:", bg='#2c3e50', fg='white').grid(row=1, column=0, sticky='w', pady=5)
            smtp_port = tk.Entry(form_frame, width=40)
            smtp_port.insert(0, config.get('smtp_port', '587'))
            smtp_port.grid(row=1, column=1, pady=5)
        
            # From Email
            tk.Label(form_frame, text="From Email:", bg='#2c3e50', fg='white').grid(row=2, column=0, sticky='w', pady=5)
            from_email = tk.Entry(form_frame, width=40)
            from_email.insert(0, config.get('from_email', ''))
            from_email.grid(row=2, column=1, pady=5)
        
            # Username
            tk.Label(form_frame, text="Username:", bg='#2c3e50', fg='white').grid(row=3, column=0, sticky='w', pady=5)
            username = tk.Entry(form_frame, width=40)
            username.insert(0, config.get('username', ''))
            username.grid(row=3, column=1, pady=5)
        
            # Password
            tk.Label(form_frame, text="Password:", bg='#2c3e50', fg='white').grid(row=4, column=0, sticky='w', pady=5)
            password = tk.Entry(form_frame, width=40, show='*')
            password.insert(0, config.get('password', ''))
            password.grid(row=4, column=1, pady=5)
        
            # Save button
            def save_config():
                new_config = {
                    'smtp_server': smtp_server.get(),
                    'smtp_port': int(smtp_port.get()),
                    'from_email': from_email.get(),
                    'username': username.get(),
                    'password': password.get()
                }
                if self._save_email_config(new_config):
                    messagebox.showinfo("Success", "Email configuration saved successfully!")
                    dialog.destroy()
                else:
                    messagebox.showerror("Error", "Failed to save email configuration")
        
            tk.Button(
                dialog,
                text="Save Configuration",
                command=save_config,
                bg='#3498db',
                fg='white',
                font=('Helvetica', 12, 'bold'),
                padx=20,
                pady=10
            ).pack(pady=20)
        
        except Exception as e:
            print(f"[EMAIL] Error creating email config dialog: {e}")
            messagebox.showerror("Error", f"Failed to create email configuration dialog: {e}")



    def _send_report_email_ui(self):
        """UI for sending report via email."""
        try:
            # Check if there are recent reports
            if not hasattr(self, 'recent_reports_list') or not self.recent_reports_list.get(0, tk.END):
                messagebox.showwarning("No Reports", "Please generate a report first before sending via email.")
                return
            
            # Get selected report
            selection = self.recent_reports_list.curselection()
            if not selection:
                messagebox.showwarning("No Selection", "Please select a report to send.")
                return
            
            report_path = self.recent_reports_list.get(selection[0])
            
            # Create email dialog
            dialog = tk.Toplevel(self.root)
            dialog.title("Send Report via Email")
            dialog.geometry("500x300")
            dialog.configure(bg='#2c3e50')
            
            # Title
            tk.Label(
                dialog,
                text="Send Report via Email",
                font=('Helvetica', 16, 'bold'),
                bg='#2c3e50',
                fg='white'
            ).pack(pady=20)
            
            # Form
            form_frame = tk.Frame(dialog, bg='#2c3e50')
            form_frame.pack(padx=20, pady=10)
            
            # Recipients
            tk.Label(form_frame, text="To (comma-separated):", bg='#2c3e50', fg='white').grid(row=0, column=0, sticky='w', pady=5)
            recipients_entry = tk.Entry(form_frame, width=40)
            recipients_entry.grid(row=0, column=1, pady=5)
            
            # Subject
            tk.Label(form_frame, text="Subject:", bg='#2c3e50', fg='white').grid(row=1, column=0, sticky='w', pady=5)
            subject_entry = tk.Entry(form_frame, width=40)
            subject_entry.insert(0, "Pool Chemistry Report")
            subject_entry.grid(row=1, column=1, pady=5)
            
            # Send button
            def send_email():
                recipients = [r.strip() for r in recipients_entry.get().split(',')]
                subject = subject_entry.get()
                
                if not recipients or not recipients[0]:
                    messagebox.showerror("Error", "Please enter at least one recipient email address.")
                    return
                
                # Send email
                if self._send_report_email(report_path, recipients, subject):
                    messagebox.showinfo("Success", f"Report sent successfully to {', '.join(recipients)}")
                    dialog.destroy()
                else:
                    messagebox.showerror("Error", "Failed to send email. Please check your email configuration.")
            
            tk.Button(
                dialog,
                text="Send Email",
                command=send_email,
                bg='#3498db',
                fg='white',
                font=('Helvetica', 12, 'bold'),
                padx=20,
                pady=10
            ).pack(pady=20)
            
        except Exception as e:
            print(f"[EMAIL] Error in send email UI: {e}")
            messagebox.showerror("Error", f"Failed to open email dialog: {e}")

    def _create_report_schedule(self, schedule_config):
        """
        Create a new report schedule.
        Returns schedule ID.
        """
        try:
            # Validate configuration
            required_fields = ['name', 'frequency', 'pools', 'template']
            for field in required_fields:
                if field not in schedule_config:
                    print(f"[Schedule] Missing required field: {field}")
                    return None

            # Generate schedule ID
            schedule_id = f"SCH_{datetime.now().strftime('%Y%m%d%H%M%S')}"

            # Calculate next run time
            next_run = self._calculate_next_run_time(
                schedule_config['frequency'],
                schedule_config.get('day_of_month', 1),
                schedule_config.get('day_of_week', 1),
                schedule_config.get('time', '08:00')
            )

            # Create schedule entry
            schedule = {
                'schedule_id': schedule_id,
                'name': schedule_config['name'],
                'frequency': schedule_config['frequency'],  # daily, weekly, monthly
                'day_of_month': schedule_config.get('day_of_month', 1),
                'day_of_week': schedule_config.get('day_of_week', 1),  # 1=Monday
                'time': schedule_config.get('time', '08:00'),
                'pools': schedule_config['pools'],
                'template': schedule_config['template'],
                'include_charts': schedule_config.get('include_charts', True),
                'email_to': schedule_config.get('email_to', []),
                'enabled': schedule_config.get('enabled', True),
                'created_at': datetime.now().isoformat(),
                'last_run': None,
                'next_run': next_run.isoformat()
            }

            # Load existing schedules
            schedules_file = self.data_dir / "report_schedules.json"
            if schedules_file.exists():
                with open(schedules_file, 'r') as f:
                    schedules = json.load(f)
            else:
                schedules = []

            # Add new schedule
            schedules.append(schedule)

            # Save schedules
            with open(schedules_file, 'w') as f:
                json.dump(schedules, f, indent=2)

            print(f"[Schedule] Created schedule: {schedule_id} - {schedule['name']}")
            return schedule_id

        except Exception as e:
            print(f"[Schedule] Error creating schedule: {e}")
            return None


    def _calculate_next_run_time(self, frequency, day_of_month, day_of_week, time_str):
        """
        Calculate next run time based on frequency.
        Returns datetime object.
        """
        try:
            now = datetime.now()
            hour, minute = map(int, time_str.split(':'))

            if frequency == 'daily':
                # Next occurrence of specified time
                next_run = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
                if next_run <= now:
                    next_run += timedelta(days=1)

            elif frequency == 'weekly':
                # Next occurrence of specified day and time
                days_ahead = day_of_week - now.isoweekday()
                if days_ahead <= 0:  # Target day already happened this week
                    days_ahead += 7
                next_run = now + timedelta(days=days_ahead)
                next_run = next_run.replace(hour=hour, minute=minute, second=0, microsecond=0)

            elif frequency == 'monthly':
                # Next occurrence of specified day of month
                next_run = now.replace(day=day_of_month, hour=hour, minute=minute, second=0, microsecond=0)
                if next_run <= now:
                    # Move to next month
                    if now.month == 12:
                        next_run = next_run.replace(year=now.year + 1, month=1)
                    else:
                        next_run = next_run.replace(month=now.month + 1)

            else:
                # Default to tomorrow
                next_run = now + timedelta(days=1)
                next_run = next_run.replace(hour=hour, minute=minute, second=0, microsecond=0)

            return next_run

        except Exception as e:
            print(f"[Schedule] Error calculating next run time: {e}")
            return datetime.now() + timedelta(days=1)


    def _check_scheduled_reports(self):
        """
        Check for and run scheduled reports.
        Returns list of generated report paths.
        """
        try:
            schedules_file = self.data_dir / "report_schedules.json"
            if not schedules_file.exists():
                return []

            with open(schedules_file, 'r') as f:
                schedules = json.load(f)

            now = datetime.now()
            generated_reports = []

            for schedule in schedules:
                if not schedule.get('enabled', True):
                    continue

                next_run = datetime.fromisoformat(schedule['next_run'])

                # Check if it's time to run
                if now >= next_run:
                    print(f"[Schedule] Running scheduled report: {schedule['name']}")

                    # Determine date range based on frequency
                    if schedule['frequency'] == 'daily':
                        start_date = (now - timedelta(days=1)).strftime('%Y-%m-%d')
                        end_date = now.strftime('%Y-%m-%d')
                    elif schedule['frequency'] == 'weekly':
                        start_date = (now - timedelta(days=7)).strftime('%Y-%m-%d')
                        end_date = now.strftime('%Y-%m-%d')
                    elif schedule['frequency'] == 'monthly':
                        start_date = (now - timedelta(days=30)).strftime('%Y-%m-%d')
                        end_date = now.strftime('%Y-%m-%d')
                    else:
                        start_date = (now - timedelta(days=7)).strftime('%Y-%m-%d')
                        end_date = now.strftime('%Y-%m-%d')

                    # Get pool IDs
                    pool_ids = schedule['pools']
                    if pool_ids == ['all']:
                        pool_ids = [pool['id'] for pool in self.pools]

                    # Generate report
                    options = {
                        'include_charts': schedule.get('include_charts', True)
                    }

                    report_path = self._generate_pdf_report(
                        pool_ids,
                        start_date,
                        end_date,
                        schedule['template'],
                        options
                    )

                    if report_path:
                        generated_reports.append(report_path)

                        # Send email if configured
                        if schedule.get('email_to'):
                            self._email_report(report_path, schedule['email_to'], schedule['name'])

                        # Update schedule
                        schedule['last_run'] = now.isoformat()
                        schedule['next_run'] = self._calculate_next_run_time(
                            schedule['frequency'],
                            schedule.get('day_of_month', 1),
                            schedule.get('day_of_week', 1),
                            schedule.get('time', '08:00')
                        ).isoformat()

            # Save updated schedules
            with open(schedules_file, 'w') as f:
                json.dump(schedules, f, indent=2)

            return generated_reports

        except Exception as e:
            print(f"[Schedule] Error checking scheduled reports: {e}")
            return []


    def _update_report_schedule(self, schedule_id, updates):
        """
        Update an existing schedule.
        Returns success boolean.
        """
        try:
            schedules_file = self.data_dir / "report_schedules.json"
            if not schedules_file.exists():
                return False

            with open(schedules_file, 'r') as f:
                schedules = json.load(f)

            # Find and update schedule
            schedule_found = False
            for schedule in schedules:
                if schedule['schedule_id'] == schedule_id:
                    schedule.update(updates)

                    # Recalculate next run if frequency changed
                    if 'frequency' in updates or 'time' in updates:
                        schedule['next_run'] = self._calculate_next_run_time(
                            schedule['frequency'],
                            schedule.get('day_of_month', 1),
                            schedule.get('day_of_week', 1),
                            schedule.get('time', '08:00')
                        ).isoformat()

                    schedule_found = True
                    break

            if not schedule_found:
                print(f"[Schedule] Schedule not found: {schedule_id}")
                return False

            # Save updated schedules
            with open(schedules_file, 'w') as f:
                json.dump(schedules, f, indent=2)

            print(f"[Schedule] Updated schedule: {schedule_id}")
            return True

        except Exception as e:
            print(f"[Schedule] Error updating schedule: {e}")
            return False


    def _delete_report_schedule(self, schedule_id):
        """
        Delete a report schedule.
        Returns success boolean.
        """
        try:
            schedules_file = self.data_dir / "report_schedules.json"
            if not schedules_file.exists():
                return False

            with open(schedules_file, 'r') as f:
                schedules = json.load(f)

            # Filter out the schedule to delete
            original_count = len(schedules)
            schedules = [s for s in schedules if s['schedule_id'] != schedule_id]

            if len(schedules) == original_count:
                print(f"[Schedule] Schedule not found: {schedule_id}")
                return False

            # Save updated schedules
            with open(schedules_file, 'w') as f:
                json.dump(schedules, f, indent=2)

            print(f"[Schedule] Deleted schedule: {schedule_id}")
            return True

        except Exception as e:
            print(f"[Schedule] Error deleting schedule: {e}")
            return False


    def _get_all_schedules(self):
        """
        Get all report schedules.
        Returns list of schedules.
        """
        try:
            schedules_file = self.data_dir / "report_schedules.json"
            if not schedules_file.exists():
                return []

            with open(schedules_file, 'r') as f:
                schedules = json.load(f)

            return schedules

        except Exception as e:
            print(f"[Schedule] Error getting schedules: {e}")
            return []


    def _create_pdf_reports_tab(self):
        """Create the PDF Reports tab"""
        try:
            # Use the existing pdf_reports_tab frame created in __init__
            reports_frame = self.pdf_reports_tab

            # Create scrollable canvas
            canvas = tk.Canvas(reports_frame, bg='#F0F4F8')
            scrollbar = ttk.Scrollbar(reports_frame, orient="vertical", command=canvas.yview)
            scrollable_frame = ttk.Frame(canvas)

            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )

            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)

            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")

            # Title
            title_label = tk.Label(
                scrollable_frame,
                text="PDF Reports",
                font=("Arial", 16, "bold"),
                bg='#F0F4F8',
                fg='#2C3E50'
            )
            title_label.pack(pady=10)

            # Report Configuration Section
            config_frame = ttk.LabelFrame(scrollable_frame, text="Report Configuration", padding=15)
            config_frame.pack(fill="x", padx=20, pady=10)

            # Pool Selection
            pool_select_frame = ttk.Frame(config_frame)
            pool_select_frame.pack(fill="x", pady=5)

            tk.Label(pool_select_frame, text="Select Pools:", font=("Arial", 10, "bold"), bg='#F0F4F8').pack(anchor="w")

            # Create checkboxes for each pool
            self.pdf_pool_vars = {}
            pools_checkbox_frame = ttk.Frame(pool_select_frame)
            pools_checkbox_frame.pack(fill="x", pady=5)

            if hasattr(self, 'pools') and self.pools:
                for pool in self.pools:
                    pool_id = pool.get('id')
                    pool_name = pool.get('name', pool_id)
                    var = tk.BooleanVar(value=True)
                    cb = ttk.Checkbutton(
                        pools_checkbox_frame,
                        text=pool_name,
                        variable=var
                    )
                    cb.pack(side="left", padx=10)
                    self.pdf_pool_vars[pool_id] = var

            # Select All / Clear All buttons
            select_buttons_frame = ttk.Frame(pool_select_frame)
            select_buttons_frame.pack(fill="x", pady=5)

            ttk.Button(
                select_buttons_frame,
                text="Select All",
                command=self._select_all_pools_for_report
            ).pack(side="left", padx=5)

            ttk.Button(
                select_buttons_frame,
                text="Clear All",
                command=self._clear_all_pools_for_report
            ).pack(side="left", padx=5)

            # Date Range Selection
            date_frame = ttk.Frame(config_frame)
            date_frame.pack(fill="x", pady=10)

            tk.Label(date_frame, text="Date Range:", font=("Arial", 10, "bold"), bg='#F0F4F8').pack(anchor="w")

            date_inputs_frame = ttk.Frame(date_frame)
            date_inputs_frame.pack(fill="x", pady=5)

            tk.Label(date_inputs_frame, text="From:", bg='#F0F4F8').pack(side="left", padx=5)

            # Start date
            self.pdf_start_date = tk.StringVar(value=(datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
            start_date_entry = ttk.Entry(date_inputs_frame, textvariable=self.pdf_start_date, width=12)
            start_date_entry.pack(side="left", padx=5)

            tk.Label(date_inputs_frame, text="To:", bg='#F0F4F8').pack(side="left", padx=5)

            # End date
            self.pdf_end_date = tk.StringVar(value=datetime.now().strftime('%Y-%m-%d'))
            end_date_entry = ttk.Entry(date_inputs_frame, textvariable=self.pdf_end_date, width=12)
            end_date_entry.pack(side="left", padx=5)

            # Quick date range buttons
            quick_dates_frame = ttk.Frame(date_frame)
            quick_dates_frame.pack(fill="x", pady=5)

            tk.Label(quick_dates_frame, text="Quick Select:", bg='#F0F4F8').pack(side="left", padx=5)

            ttk.Button(
                quick_dates_frame,
                text="Last 7 Days",
                command=lambda: self._set_date_range(7)
            ).pack(side="left", padx=2)

            ttk.Button(
                quick_dates_frame,
                text="Last 30 Days",
                command=lambda: self._set_date_range(30)
            ).pack(side="left", padx=2)

            ttk.Button(
                quick_dates_frame,
                text="Last 90 Days",
                command=lambda: self._set_date_range(90)
            ).pack(side="left", padx=2)

            ttk.Button(
                quick_dates_frame,
                text="Last Year",
                command=lambda: self._set_date_range(365)
            ).pack(side="left", padx=2)

            # Template Selection
            template_frame = ttk.Frame(config_frame)
            template_frame.pack(fill="x", pady=10)

            tk.Label(template_frame, text="Report Template:", font=("Arial", 10, "bold"), bg='#F0F4F8').pack(anchor="w")

            self.pdf_template_var = tk.StringVar(value="executive_summary")

            templates = [
                ("Executive Summary", "executive_summary"),
                ("Detailed Technical", "detailed_technical"),
                ("Maintenance Schedule", "maintenance_schedule")
            ]

            for label, value in templates:
                rb = ttk.Radiobutton(
                    template_frame,
                    text=label,
                    variable=self.pdf_template_var,
                    value=value
                )
                rb.pack(anchor="w", pady=2)

            # Options
            options_frame = ttk.Frame(config_frame)
            options_frame.pack(fill="x", pady=10)

            tk.Label(options_frame, text="Options:", font=("Arial", 10, "bold"), bg='#F0F4F8').pack(anchor="w")

            self.pdf_include_charts = tk.BooleanVar(value=True)
            ttk.Checkbutton(
                options_frame,
                text="Include Charts",
                variable=self.pdf_include_charts
            ).pack(anchor="w", pady=2)

            self.pdf_include_recommendations = tk.BooleanVar(value=True)
            ttk.Checkbutton(
                options_frame,
                text="Include Recommendations",
                variable=self.pdf_include_recommendations
            ).pack(anchor="w", pady=2)

            self.pdf_include_cost_analysis = tk.BooleanVar(value=True)
            ttk.Checkbutton(
                options_frame,
                text="Include Cost Analysis",
                variable=self.pdf_include_cost_analysis
            ).pack(anchor="w", pady=2)

            # Actions Section
            actions_frame = ttk.LabelFrame(scrollable_frame, text="Actions", padding=15)
            actions_frame.pack(fill="x", padx=20, pady=10)

            buttons_frame = ttk.Frame(actions_frame)
            buttons_frame.pack(fill="x")

            tk.Button(
                buttons_frame,
                text="Generate PDF",
                command=self._generate_pdf_report_ui,
                bg='#27AE60',
                fg='white',
                font=("Arial", 11, "bold"),
                padx=20,
                pady=8
            ).pack(side="left", padx=5)

            tk.Button(
                buttons_frame,
                text="Schedule Report",
                command=self._schedule_report_ui,
                bg='#3498DB',
                fg='white',
                font=("Arial", 11, "bold"),
                padx=20,
                pady=8
            ).pack(side="left", padx=5)

            tk.Button(
                buttons_frame,
                text="View Schedules",
                command=self._view_schedules_ui,
                bg='#95A5A6',
                fg='white',
                font=("Arial", 11, "bold"),
                padx=20,
                pady=8
            ).pack(side="left", padx=5)

            # Recent Reports Section
            recent_frame = ttk.LabelFrame(scrollable_frame, text="Recent Reports", padding=15)
            recent_frame.pack(fill="both", expand=True, padx=20, pady=10)

            # Create treeview for recent reports
            columns = ('Date', 'Pools', 'Template', 'Size')
            self.recent_reports_tree = ttk.Treeview(recent_frame, columns=columns, show='headings', height=5)

            for col in columns:
                self.recent_reports_tree.heading(col, text=col)
                self.recent_reports_tree.column(col, width=150)

            self.recent_reports_tree.pack(fill="both", expand=True)

            # Add scrollbar to treeview
            tree_scrollbar = ttk.Scrollbar(recent_frame, orient="vertical", command=self.recent_reports_tree.yview)
            self.recent_reports_tree.configure(yscrollcommand=tree_scrollbar.set)
            tree_scrollbar.pack(side="right", fill="y")

            # Buttons for recent reports
            recent_buttons_frame = ttk.Frame(recent_frame)
            recent_buttons_frame.pack(fill="x", pady=5)

            ttk.Button(
                recent_buttons_frame,
                text="Open Report",
                command=self._open_selected_report
            ).pack(side="left", padx=5)

            ttk.Button(
                recent_buttons_frame,
                text="Refresh List",
                command=self._refresh_recent_reports
            ).pack(side="left", padx=5)

            # Load recent reports
            self._refresh_recent_reports()

            print("[PDF UI] PDF Reports tab created successfully")

        except Exception as e:
            print(f"[PDF UI] Error creating PDF reports tab: {e}")
            import traceback
            traceback.print_exc()


    def _select_all_pools_for_report(self):
        """Select all pools for report generation"""
        for var in self.pdf_pool_vars.values():
            var.set(True)


    def _clear_all_pools_for_report(self):
        """Clear all pool selections"""
        for var in self.pdf_pool_vars.values():
            var.set(False)


    def _set_date_range(self, days):
        """Set date range based on number of days"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        self.pdf_start_date.set(start_date.strftime('%Y-%m-%d'))
        self.pdf_end_date.set(end_date.strftime('%Y-%m-%d'))


    def _generate_pdf_report_ui(self):
        """Generate PDF report from UI"""
        try:
            # Get selected pools
            selected_pools = [pool_id for pool_id, var in self.pdf_pool_vars.items() if var.get()]

            if not selected_pools:
                messagebox.showwarning("No Pools Selected", "Please select at least one pool for the report.")
                return

            # Get date range
            start_date = self.pdf_start_date.get()
            end_date = self.pdf_end_date.get()

            # Get template
            template = self.pdf_template_var.get()

            # Get options
            options = {
                'include_charts': self.pdf_include_charts.get(),
                'include_recommendations': self.pdf_include_recommendations.get(),
                'include_cost_analysis': self.pdf_include_cost_analysis.get()
            }

            # Show progress
            progress_window = tk.Toplevel(self)
            progress_window.title("Generating Report")
            progress_window.geometry("400x150")
            progress_window.transient(self)
            progress_window.grab_set()

            tk.Label(
                progress_window,
                text="Generating PDF Report...",
                font=("Arial", 12, "bold")
            ).pack(pady=20)

            progress_label = tk.Label(progress_window, text="Please wait...")
            progress_label.pack(pady=10)

            progress_window.update()

            # Generate report
            report_path = self._generate_pdf_report(selected_pools, start_date, end_date, template, options)

            progress_window.destroy()

            if report_path:
                result = messagebox.askyesno(
                    "Report Generated",
                    f"Report generated successfully!\n\nPath: {report_path}\n\nWould you like to open it now?"
                )

                if result:
                    import os
                    os.startfile(report_path)  # Windows

                # Refresh recent reports list
                self._refresh_recent_reports()
            else:
                messagebox.showerror("Error", "Failed to generate report. Check console for details.")

        except Exception as e:
            print(f"[PDF UI] Error generating report: {e}")
            messagebox.showerror("Error", f"Failed to generate report: {str(e)}")


    def _schedule_report_ui(self):
        """Open dialog to schedule a report"""
        try:
            # Create schedule dialog
            dialog = tk.Toplevel(self)
            dialog.title("Schedule Report")
            dialog.geometry("500x600")
            dialog.transient(self)
            dialog.grab_set()

            # Title
            tk.Label(
                dialog,
                text="Schedule Automated Report",
                font=("Arial", 14, "bold")
            ).pack(pady=10)

            # Schedule name
            name_frame = ttk.Frame(dialog)
            name_frame.pack(fill="x", padx=20, pady=5)
            tk.Label(name_frame, text="Schedule Name:").pack(side="left")
            schedule_name_var = tk.StringVar()
            ttk.Entry(name_frame, textvariable=schedule_name_var, width=30).pack(side="left", padx=10)

            # Frequency
            freq_frame = ttk.Frame(dialog)
            freq_frame.pack(fill="x", padx=20, pady=5)
            tk.Label(freq_frame, text="Frequency:").pack(side="left")
            frequency_var = tk.StringVar(value="monthly")
            ttk.Combobox(
                freq_frame,
                textvariable=frequency_var,
                values=["daily", "weekly", "monthly"],
                state="readonly",
                width=15
            ).pack(side="left", padx=10)

            # Time
            time_frame = ttk.Frame(dialog)
            time_frame.pack(fill="x", padx=20, pady=5)
            tk.Label(time_frame, text="Time:").pack(side="left")
            time_var = tk.StringVar(value="08:00")
            ttk.Entry(time_frame, textvariable=time_var, width=10).pack(side="left", padx=10)
            tk.Label(time_frame, text="(HH:MM format)").pack(side="left")

            # Template
            template_frame = ttk.Frame(dialog)
            template_frame.pack(fill="x", padx=20, pady=5)
            tk.Label(template_frame, text="Template:").pack(side="left")
            template_var = tk.StringVar(value="executive_summary")
            ttk.Combobox(
                template_frame,
                textvariable=template_var,
                values=["executive_summary", "detailed_technical", "maintenance_schedule"],
                state="readonly",
                width=20
            ).pack(side="left", padx=10)

            # Email recipients
            email_frame = ttk.Frame(dialog)
            email_frame.pack(fill="x", padx=20, pady=5)
            tk.Label(email_frame, text="Email To:").pack(anchor="w")
            email_var = tk.StringVar()
            ttk.Entry(email_frame, textvariable=email_var, width=40).pack(fill="x", pady=5)
            tk.Label(email_frame, text="(Comma-separated email addresses)", font=("Arial", 8)).pack(anchor="w")

            # Buttons
            button_frame = ttk.Frame(dialog)
            button_frame.pack(fill="x", padx=20, pady=20)

            def save_schedule():
                name = schedule_name_var.get()
                if not name:
                    messagebox.showwarning("Missing Name", "Please enter a schedule name.")
                    return

                # Get selected pools
                selected_pools = [pool_id for pool_id, var in self.pdf_pool_vars.items() if var.get()]
                if not selected_pools:
                    selected_pools = ['all']

                # Parse email addresses
                email_to = [e.strip() for e in email_var.get().split(',') if e.strip()]

                schedule_config = {
                    'name': name,
                    'frequency': frequency_var.get(),
                    'time': time_var.get(),
                    'pools': selected_pools,
                    'template': template_var.get(),
                    'email_to': email_to,
                    'include_charts': True
                }

                schedule_id = self._create_report_schedule(schedule_config)

                if schedule_id:
                    messagebox.showinfo("Success", f"Schedule created successfully!\nSchedule ID: {schedule_id}")
                    dialog.destroy()
                else:
                    messagebox.showerror("Error", "Failed to create schedule.")

            ttk.Button(button_frame, text="Save Schedule", command=save_schedule).pack(side="left", padx=5)
            ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side="left", padx=5)

        except Exception as e:
            print(f"[PDF UI] Error in schedule dialog: {e}")
            messagebox.showerror("Error", f"Failed to open schedule dialog: {str(e)}")


    def _view_schedules_ui(self):
        """View and manage scheduled reports"""
        try:
            # Create schedules dialog
            dialog = tk.Toplevel(self)
            dialog.title("Scheduled Reports")
            dialog.geometry("700x400")
            dialog.transient(self)

            # Title
            tk.Label(
                dialog,
                text="Scheduled Reports",
                font=("Arial", 14, "bold")
            ).pack(pady=10)

            # Create treeview
            columns = ('Name', 'Frequency', 'Next Run', 'Status')
            tree = ttk.Treeview(dialog, columns=columns, show='headings', height=10)

            for col in columns:
                tree.heading(col, text=col)
                tree.column(col, width=150)

            tree.pack(fill="both", expand=True, padx=20, pady=10)

            # Load schedules
            schedules = self._get_all_schedules()
            for schedule in schedules:
                tree.insert('', 'end', values=(
                    schedule['name'],
                    schedule['frequency'],
                    schedule['next_run'][:16],  # Trim to date and time
                    'Enabled' if schedule.get('enabled', True) else 'Disabled'
                ), tags=(schedule['schedule_id'],))

            # Buttons
            button_frame = ttk.Frame(dialog)
            button_frame.pack(fill="x", padx=20, pady=10)

            def run_now():
                selection = tree.selection()
                if not selection:
                    messagebox.showwarning("No Selection", "Please select a schedule to run.")
                    return

                schedule_id = tree.item(selection[0])['tags'][0]
                messagebox.showinfo("Running", f"Running schedule: {schedule_id}")
                # Would trigger immediate run

            def delete_schedule():
                selection = tree.selection()
                if not selection:
                    messagebox.showwarning("No Selection", "Please select a schedule to delete.")
                    return

                if messagebox.askyesno("Confirm Delete", "Delete this schedule?"):
                    schedule_id = tree.item(selection[0])['tags'][0]
                    if self._delete_report_schedule(schedule_id):
                        tree.delete(selection[0])
                        messagebox.showinfo("Success", "Schedule deleted.")

            ttk.Button(button_frame, text="Run Now", command=run_now).pack(side="left", padx=5)
            ttk.Button(button_frame, text="Delete", command=delete_schedule).pack(side="left", padx=5)
            ttk.Button(button_frame, text="Close", command=dialog.destroy).pack(side="left", padx=5)

        except Exception as e:
            print(f"[PDF UI] Error viewing schedules: {e}")
            messagebox.showerror("Error", f"Failed to view schedules: {str(e)}")


    def _refresh_recent_reports(self):
        """Refresh the list of recent reports"""
        try:
            # Clear existing items
            for item in self.recent_reports_tree.get_children():
                self.recent_reports_tree.delete(item)

            # Get reports directory
            reports_dir = self.data_dir / "reports"
            if not reports_dir.exists():
                return

            # Find all PDF files
            pdf_files = []
            for year_dir in reports_dir.iterdir():
                if year_dir.is_dir():
                    for month_dir in year_dir.iterdir():
                        if month_dir.is_dir():
                            for pdf_file in month_dir.glob("*.pdf"):
                                pdf_files.append(pdf_file)

            # Sort by modification time (newest first)
            pdf_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)

            # Add to treeview (limit to 20 most recent)
            for pdf_file in pdf_files[:20]:
                # Parse filename to extract info
                filename = pdf_file.stem
                parts = filename.split('_')

                # Get file size
                size_bytes = pdf_file.stat().st_size
                size_mb = size_bytes / (1024 * 1024)

                # Get modification time
                mod_time = datetime.fromtimestamp(pdf_file.stat().st_mtime)

                self.recent_reports_tree.insert('', 'end', values=(
                    mod_time.strftime('%Y-%m-%d %H:%M'),
                    parts[3] if len(parts) > 3 else 'N/A',  # Pool count
                    parts[2] if len(parts) > 2 else 'N/A',  # Template
                    f"{size_mb:.2f} MB"
                ), tags=(str(pdf_file),))

        except Exception as e:
            print(f"[PDF UI] Error refreshing recent reports: {e}")

    def _open_selected_report(self):
        """Open the selected PDF report from the recent reports list"""
        try:
            # Get selected item from treeview
            selection = self.recent_reports_tree.selection()
            if not selection:
                messagebox.showinfo("No Selection", "Please select a report to open.")
                return
            
            # Get the report file path from the treeview
            item = self.recent_reports_tree.item(selection[0])
            tags = item.get('tags', [])
            
            if not tags:
                messagebox.showerror("Error", "Could not locate the selected report file.")
                return
            
            report_path = tags[0]  # First tag contains the file path
            
            # Check if file exists
            if not os.path.exists(report_path):
                messagebox.showerror("File Not Found", 
                    f"The report file could not be found:\n{report_path}\n\n"
                    f"The file may have been moved or deleted.")
                return
            
            # Try to open the PDF file
            import subprocess
            import platform
            
            system = platform.system()
            
            try:
                if system == "Windows":
                    # Use Windows default PDF viewer
                    os.startfile(report_path)
                elif system == "Darwin":  # macOS
                    # Use macOS default PDF viewer
                    subprocess.run(['open', report_path], check=True)
                elif system == "Linux":
                    # Try common Linux PDF viewers
                    viewers = ['xdg-open', 'evince', 'okular', 'acroread']
                    for viewer in viewers:
                        try:
                            subprocess.run([viewer, report_path], check=True)
                            break
                        except (subprocess.CalledProcessError, FileNotFoundError):
                            continue
                    else:
                        # No viewer found, try xdg-open as last resort
                        subprocess.run(['xdg-open', report_path], check=True)
                
                print(f"[PDF UI] Opened report: {report_path}")
                
            except Exception as open_error:
                messagebox.showerror("Open Failed", 
                    f"Could not open the PDF file.\n\n"
                    f"File: {report_path}\n"
                    f"Error: {str(open_error)}\n\n"
                    f"You can try opening the file manually with your PDF viewer.")
                
        except Exception as e:
            messagebox.showerror("Error", 
                f"Failed to open selected report:\n{str(e)}")
            print(f"[PDF UI] Error opening selected report: {e}")








    # ============================================================================
    # PHASE 2.2: ENHANCED PDF FEATURES
    # ============================================================================

    # Custom Branding System
    def _create_branding_tab(self):
        """Create the Custom Branding tab"""
        try:
            # Create branding tab
            branding_frame = ttk.Frame(self.notebook)
            self.notebook.add(branding_frame, text="🎨 Branding")
            
            # Create scrollable canvas
            canvas = tk.Canvas(branding_frame, bg='#F0F4F8')
            scrollbar = ttk.Scrollbar(branding_frame, orient="vertical", command=canvas.yview)
            scrollable_frame = ttk.Frame(canvas)
            
            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )
            
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            
            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
            
            # Title
            title_label = tk.Label(
                scrollable_frame,
                text="Custom Branding",
                font=("Arial", 16, "bold"),
                bg='#F0F4F8',
                fg='#2C3E50'
            )
            title_label.pack(pady=10)
            
            # Logo Section
            logo_frame = ttk.LabelFrame(scrollable_frame, text="Company Logo", padding=15)
            logo_frame.pack(fill="x", padx=20, pady=10)
            
            # Logo preview
            self.logo_preview_label = tk.Label(
                logo_frame,
                text="No logo uploaded",
                bg='white',
                width=40,
                height=10,
                relief='sunken'
            )
            self.logo_preview_label.pack(pady=10)
            
            # Logo buttons
            logo_buttons_frame = ttk.Frame(logo_frame)
            logo_buttons_frame.pack(fill="x", pady=5)
            
            ttk.Button(
                logo_buttons_frame,
                text="Upload Logo",
                command=self._upload_logo
            ).pack(side="left", padx=5)
            
            ttk.Button(
                logo_buttons_frame,
                text="Remove Logo",
                command=self._remove_logo
            ).pack(side="left", padx=5)
            
            # Company Information Section
            company_frame = ttk.LabelFrame(scrollable_frame, text="Company Information", padding=15)
            company_frame.pack(fill="x", padx=20, pady=10)
            
            # Company name
            tk.Label(company_frame, text="Company Name:", font=("Arial", 10, "bold")).pack(anchor="w", pady=5)
            self.company_name_var = tk.StringVar(value="Deep Blue Pool Services")
            ttk.Entry(company_frame, textvariable=self.company_name_var, width=50).pack(fill="x", pady=5)
            
            # Tagline
            tk.Label(company_frame, text="Tagline:", font=("Arial", 10, "bold")).pack(anchor="w", pady=5)
            self.company_tagline_var = tk.StringVar(value="Professional Pool Chemistry Management")
            ttk.Entry(company_frame, textvariable=self.company_tagline_var, width=50).pack(fill="x", pady=5)
            
            # Address
            tk.Label(company_frame, text="Address:", font=("Arial", 10, "bold")).pack(anchor="w", pady=5)
            self.company_address_var = tk.StringVar(value="")
            ttk.Entry(company_frame, textvariable=self.company_address_var, width=50).pack(fill="x", pady=5)
            
            # Phone
            tk.Label(company_frame, text="Phone:", font=("Arial", 10, "bold")).pack(anchor="w", pady=5)
            self.company_phone_var = tk.StringVar(value="")
            ttk.Entry(company_frame, textvariable=self.company_phone_var, width=50).pack(fill="x", pady=5)
            
            # Email
            tk.Label(company_frame, text="Email:", font=("Arial", 10, "bold")).pack(anchor="w", pady=5)
            self.company_email_var = tk.StringVar(value="")
            ttk.Entry(company_frame, textvariable=self.company_email_var, width=50).pack(fill="x", pady=5)
            
            # Website
            tk.Label(company_frame, text="Website:", font=("Arial", 10, "bold")).pack(anchor="w", pady=5)
            self.company_website_var = tk.StringVar(value="")
            ttk.Entry(company_frame, textvariable=self.company_website_var, width=50).pack(fill="x", pady=5)
            
            # Color Scheme Section
            colors_frame = ttk.LabelFrame(scrollable_frame, text="Color Scheme", padding=15)
            colors_frame.pack(fill="x", padx=20, pady=10)
            
            # Primary color
            primary_color_frame = ttk.Frame(colors_frame)
            primary_color_frame.pack(fill="x", pady=5)
            
            tk.Label(primary_color_frame, text="Primary Color:", font=("Arial", 10, "bold")).pack(side="left", padx=5)
            self.primary_color_var = tk.StringVar(value="#1e3a8a")
            self.primary_color_display = tk.Label(
                primary_color_frame,
                bg=self.primary_color_var.get(),
                width=10,
                relief='raised'
            )
            self.primary_color_display.pack(side="left", padx=5)
            
            ttk.Button(
                primary_color_frame,
                text="Choose Color",
                command=lambda: self._choose_color('primary')
            ).pack(side="left", padx=5)
            
            # Secondary color
            secondary_color_frame = ttk.Frame(colors_frame)
            secondary_color_frame.pack(fill="x", pady=5)
            
            tk.Label(secondary_color_frame, text="Secondary Color:", font=("Arial", 10, "bold")).pack(side="left", padx=5)
            self.secondary_color_var = tk.StringVar(value="#3b82f6")
            self.secondary_color_display = tk.Label(
                secondary_color_frame,
                bg=self.secondary_color_var.get(),
                width=10,
                relief='raised'
            )
            self.secondary_color_display.pack(side="left", padx=5)
            
            ttk.Button(
                secondary_color_frame,
                text="Choose Color",
                command=lambda: self._choose_color('secondary')
            ).pack(side="left", padx=5)
            
            # Accent color
            accent_color_frame = ttk.Frame(colors_frame)
            accent_color_frame.pack(fill="x", pady=5)
            
            tk.Label(accent_color_frame, text="Accent Color:", font=("Arial", 10, "bold")).pack(side="left", padx=5)
            self.accent_color_var = tk.StringVar(value="#10b981")
            self.accent_color_display = tk.Label(
                accent_color_frame,
                bg=self.accent_color_var.get(),
                width=10,
                relief='raised'
            )
            self.accent_color_display.pack(side="left", padx=5)
            
            ttk.Button(
                accent_color_frame,
                text="Choose Color",
                command=lambda: self._choose_color('accent')
            ).pack(side="left", padx=5)
            
            # Preset color schemes
            presets_frame = ttk.Frame(colors_frame)
            presets_frame.pack(fill="x", pady=10)
            
            tk.Label(presets_frame, text="Preset Schemes:", font=("Arial", 10, "bold")).pack(anchor="w", pady=5)
            
            presets = [
                ("Deep Blue (Default)", "#1e3a8a", "#3b82f6", "#10b981"),
                ("Ocean Breeze", "#0891b2", "#06b6d4", "#22d3ee"),
                ("Sunset", "#dc2626", "#f97316", "#fbbf24"),
                ("Forest", "#065f46", "#059669", "#10b981"),
                ("Royal Purple", "#6b21a8", "#9333ea", "#c084fc"),
                ("Professional Gray", "#374151", "#6b7280", "#9ca3af")
            ]
            
            for name, primary, secondary, accent in presets:
                btn = ttk.Button(
                    presets_frame,
                    text=name,
                    command=lambda p=primary, s=secondary, a=accent: self._apply_color_preset(p, s, a)
                )
                btn.pack(side="left", padx=2)
            
            # Actions Section
            actions_frame = ttk.LabelFrame(scrollable_frame, text="Actions", padding=15)
            actions_frame.pack(fill="x", padx=20, pady=10)
            
            buttons_frame = ttk.Frame(actions_frame)
            buttons_frame.pack(fill="x")
            
            tk.Button(
                buttons_frame,
                text="Save Branding",
                command=self._save_branding,
                bg='#27AE60',
                fg='white',
                font=("Arial", 11, "bold"),
                padx=20,
                pady=8
            ).pack(side="left", padx=5)
            
            tk.Button(
                buttons_frame,
                text="Load Branding",
                command=self._load_branding,
                bg='#3498DB',
                fg='white',
                font=("Arial", 11, "bold"),
                padx=20,
                pady=8
            ).pack(side="left", padx=5)
            
            tk.Button(
                buttons_frame,
                text="Reset to Default",
                command=self._reset_branding,
                bg='#95A5A6',
                fg='white',
                font=("Arial", 11, "bold"),
                padx=20,
                pady=8
            ).pack(side="left", padx=5)
            
            tk.Button(
                buttons_frame,
                text="Preview Report",
                command=self._preview_branded_report,
                bg='#E67E22',
                fg='white',
                font=("Arial", 11, "bold"),
                padx=20,
                pady=8
            ).pack(side="left", padx=5)
            
            # Load existing branding if available
            self._load_branding(silent=True)
            
            print("[Branding] Custom Branding tab created successfully")
            
        except Exception as e:
            print(f"[Branding] Error creating branding tab: {e}")
            import traceback
            traceback.print_exc()
    
    

    def _upload_logo(self):
        """Upload a custom logo"""
        try:
            from PIL import Image as PILImage
            file_path = filedialog.askopenfilename(
                title="Select Logo Image",
                filetypes=[
                    ("Image files", "*.png *.jpg *.jpeg *.gif *.bmp"),
                    ("All files", "*.*")
                ]
            )
            
            if file_path:
                # Create branding directory if it doesn't exist
                branding_dir = self.data_dir / "branding"
                branding_dir.mkdir(exist_ok=True)
                
                # Copy logo to branding directory
                logo_dest = branding_dir / "logo.png"
                
                # Open and resize image if needed
                img = PILImage.open(file_path)
                
                # Resize to max 400x400 while maintaining aspect ratio
                img.thumbnail((400, 400), PILImage.Resampling.LANCZOS)
                
                # Save as PNG
                img.save(logo_dest, "PNG")
                
                # Update preview
                self._update_logo_preview(logo_dest)
                
                messagebox.showinfo("Success", "Logo uploaded successfully!")
                
        except Exception as e:
            print(f"[Branding] Error uploading logo: {e}")
            messagebox.showerror("Error", f"Failed to upload logo: {str(e)}")
    
    

    def _remove_logo(self):
        """Remove the custom logo"""
        try:
            logo_path = self.data_dir / "branding" / "logo.png"
            if logo_path.exists():
                logo_path.unlink()
            
            # Reset preview
            self.logo_preview_label.config(image='', text="No logo uploaded")
            
            messagebox.showinfo("Success", "Logo removed successfully!")
            
        except Exception as e:
            print(f"[Branding] Error removing logo: {e}")
            messagebox.showerror("Error", f"Failed to remove logo: {str(e)}")
    
    

    def _update_logo_preview(self, logo_path):
        """Update the logo preview"""
        try:
            from PIL import Image as PILImage
            img = PILImage.open(logo_path)
            img.thumbnail((200, 200), PILImage.Resampling.LANCZOS)
            
            photo = ImageTk.PhotoImage(img)
            self.logo_preview_label.config(image=photo, text='')
            self.logo_preview_label.image = photo  # Keep a reference
            
        except Exception as e:
            print(f"[Branding] Error updating logo preview: {e}")
    
    

    def _choose_color(self, color_type):
        """Open color chooser dialog"""
        try:
            if color_type == 'primary':
                current_color = self.primary_color_var.get()
            elif color_type == 'secondary':
                current_color = self.secondary_color_var.get()
            else:  # accent
                current_color = self.accent_color_var.get()
            
            color = colorchooser.askcolor(
                title=f"Choose {color_type.title()} Color",
                initialcolor=current_color
            )
            
            if color[1]:  # color[1] is the hex value
                if color_type == 'primary':
                    self.primary_color_var.set(color[1])
                    self.primary_color_display.config(bg=color[1])
                elif color_type == 'secondary':
                    self.secondary_color_var.set(color[1])
                    self.secondary_color_display.config(bg=color[1])
                else:  # accent
                    self.accent_color_var.set(color[1])
                    self.accent_color_display.config(bg=color[1])
                    
        except Exception as e:
            print(f"[Branding] Error choosing color: {e}")
    
    

    def _apply_color_preset(self, primary, secondary, accent):
        """Apply a preset color scheme"""
        try:
            self.primary_color_var.set(primary)
            self.primary_color_display.config(bg=primary)
            
            self.secondary_color_var.set(secondary)
            self.secondary_color_display.config(bg=secondary)
            
            self.accent_color_var.set(accent)
            self.accent_color_display.config(bg=accent)
            
            messagebox.showinfo("Success", "Color preset applied!")
            
        except Exception as e:
            print(f"[Branding] Error applying preset: {e}")
    
    

    def _save_branding(self):
        """Save branding configuration"""
        try:
            branding_config = {
                'company_name': self.company_name_var.get(),
                'tagline': self.company_tagline_var.get(),
                'address': self.company_address_var.get(),
                'phone': self.company_phone_var.get(),
                'email': self.company_email_var.get(),
                'website': self.company_website_var.get(),
                'primary_color': self.primary_color_var.get(),
                'secondary_color': self.secondary_color_var.get(),
                'accent_color': self.accent_color_var.get()
            }
            
            # Create branding directory
            branding_dir = self.data_dir / "branding"
            branding_dir.mkdir(exist_ok=True)
            
            # Save config
            config_file = branding_dir / "branding_config.json"
            with open(config_file, 'w') as f:
                json.dump(branding_config, f, indent=4)
            
            messagebox.showinfo("Success", "Branding configuration saved successfully!")
            
        except Exception as e:
            print(f"[Branding] Error saving branding: {e}")
            messagebox.showerror("Error", f"Failed to save branding: {str(e)}")
    
    

    def _load_branding(self, silent=False):
        """Load branding configuration"""
        try:
            config_file = self.data_dir / "branding" / "branding_config.json"
            
            if config_file.exists():
                with open(config_file, 'r') as f:
                    branding_config = json.load(f)
                
                # Load values
                self.company_name_var.set(branding_config.get('company_name', ''))
                self.company_tagline_var.set(branding_config.get('tagline', ''))
                self.company_address_var.set(branding_config.get('address', ''))
                self.company_phone_var.set(branding_config.get('phone', ''))
                self.company_email_var.set(branding_config.get('email', ''))
                self.company_website_var.set(branding_config.get('website', ''))
                
                # Load colors
                primary = branding_config.get('primary_color', '#1e3a8a')
                secondary = branding_config.get('secondary_color', '#3b82f6')
                accent = branding_config.get('accent_color', '#10b981')
                
                self.primary_color_var.set(primary)
                self.primary_color_display.config(bg=primary)
                
                self.secondary_color_var.set(secondary)
                self.secondary_color_display.config(bg=secondary)
                
                self.accent_color_var.set(accent)
                self.accent_color_display.config(bg=accent)
                
                # Load logo preview if exists
                logo_path = self.data_dir / "branding" / "logo.png"
                if logo_path.exists():
                    self._update_logo_preview(logo_path)
                
                if not silent:
                    messagebox.showinfo("Success", "Branding configuration loaded successfully!")
            else:
                if not silent:
                    messagebox.showinfo("Info", "No saved branding configuration found.")
                    
        except Exception as e:
            print(f"[Branding] Error loading branding: {e}")
            if not silent:
                messagebox.showerror("Error", f"Failed to load branding: {str(e)}")
    
    

    def _reset_branding(self):
        """Reset branding to default"""
        try:
            result = messagebox.askyesno(
                "Confirm Reset",
                "Are you sure you want to reset branding to default values?"
            )
            
            if result:
                # Reset to defaults
                self.company_name_var.set("Deep Blue Pool Services")
                self.company_tagline_var.set("Professional Pool Chemistry Management")
                self.company_address_var.set("")
                self.company_phone_var.set("")
                self.company_email_var.set("")
                self.company_website_var.set("")
                
                self._apply_color_preset("#1e3a8a", "#3b82f6", "#10b981")
                
                # Remove logo
                self._remove_logo()
                
                messagebox.showinfo("Success", "Branding reset to default!")
                
        except Exception as e:
            print(f"[Branding] Error resetting branding: {e}")
            messagebox.showerror("Error", f"Failed to reset branding: {str(e)}")
    
    

    def _preview_branded_report(self):
        """Preview branding changes by generating a sample PDF report"""
        try:
            # Show confirmation dialog
            response = messagebox.askyesno(
                "Generate Preview",
                "This will generate a sample PDF report with your current branding settings.\n\n"
                "The PDF will include:\n"
                "• Your company logo and information\n"
                "• Your custom color scheme\n"
                "• Sample pool data and charts\n"
                "• All report formatting\n\n"
                "Do you want to continue?",
                icon='question'
            )
            
            if response:
                # Generate and open the preview PDF
                self._generate_preview_pdf()
                
        except Exception as e:
            print(f"[Branding] Error previewing report: {e}")
            messagebox.showerror("Error", f"Failed to preview report: {str(e)}")
    
    def _generate_scatter_chart(self, data, title, xlabel, ylabel, output_path):
        """Generate scatter plot for correlation analysis"""
        try:
            fig, ax = plt.subplots(figsize=(10, 6))
            
            # Extract x and y data
            x_data = data.get('x', [])
            y_data = data.get('y', [])
            colors = data.get('colors', ['#1e3a8a'] * len(x_data))
            sizes = data.get('sizes', [50] * len(x_data))
            
            # Create scatter plot
            scatter = ax.scatter(x_data, y_data, c=colors, s=sizes, alpha=0.6, edgecolors='black')
            
            # Add trend line if requested
            if data.get('show_trend', False) and len(x_data) > 1:
                z = np.polyfit(x_data, y_data, 1)
                p = np.poly1d(z)
                ax.plot(x_data, p(x_data), "r--", alpha=0.8, linewidth=2, label='Trend')
                ax.legend()
            
            ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
            ax.set_xlabel(xlabel, fontsize=12)
            ax.set_ylabel(ylabel, fontsize=12)
            ax.grid(True, alpha=0.3)
            
            plt.tight_layout()
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return output_path
            
        except Exception as e:
            print(f"[Charts] Error generating scatter chart: {e}")
            return None
    
    

    def _generate_heatmap_chart(self, data, title, output_path):
        """Generate heatmap for parameter correlation"""
        try:
            fig, ax = plt.subplots(figsize=(10, 8))
            
            # Get data matrix and labels
            matrix = data.get('matrix', [])
            row_labels = data.get('row_labels', [])
            col_labels = data.get('col_labels', [])
            
            # Create heatmap
            im = ax.imshow(matrix, cmap='RdYlGn', aspect='auto')
            
            # Set ticks and labels
            ax.set_xticks(np.arange(len(col_labels)))
            ax.set_yticks(np.arange(len(row_labels)))
            ax.set_xticklabels(col_labels)
            ax.set_yticklabels(row_labels)
            
            # Rotate x labels
            plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
            
            # Add values to cells
            for i in range(len(row_labels)):
                for j in range(len(col_labels)):
                    text = ax.text(j, i, f"{matrix[i][j]:.2f}",
                                 ha="center", va="center", color="black", fontsize=10)
            
            ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
            
            # Add colorbar
            cbar = plt.colorbar(im, ax=ax)
            cbar.set_label('Correlation', rotation=270, labelpad=20)
            
            plt.tight_layout()
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return output_path
            
        except Exception as e:
            print(f"[Charts] Error generating heatmap: {e}")
            return None
    
    

    def _generate_gauge_chart(self, value, title, min_val, max_val, optimal_range, output_path):
        """Generate gauge chart for single parameter status"""
        try:
            fig, ax = plt.subplots(figsize=(8, 6), subplot_kw={'projection': 'polar'})
            
            # Normalize value to 0-180 degrees
            normalized_value = ((value - min_val) / (max_val - min_val)) * 180
            
            # Define color zones
            theta = np.linspace(0, np.pi, 100)
            
            # Red zone (low)
            red_low = np.linspace(0, np.pi * 0.3, 30)
            ax.fill_between(red_low, 0, 1, color='#ef4444', alpha=0.3)
            
            # Yellow zone (caution)
            yellow_low = np.linspace(np.pi * 0.3, np.pi * 0.4, 10)
            ax.fill_between(yellow_low, 0, 1, color='#fbbf24', alpha=0.3)
            
            # Green zone (optimal)
            green = np.linspace(np.pi * 0.4, np.pi * 0.6, 20)
            ax.fill_between(green, 0, 1, color='#10b981', alpha=0.3)
            
            # Yellow zone (caution)
            yellow_high = np.linspace(np.pi * 0.6, np.pi * 0.7, 10)
            ax.fill_between(yellow_high, 0, 1, color='#fbbf24', alpha=0.3)
            
            # Red zone (high)
            red_high = np.linspace(np.pi * 0.7, np.pi, 30)
            ax.fill_between(red_high, 0, 1, color='#ef4444', alpha=0.3)
            
            # Draw needle
            needle_angle = np.radians(normalized_value)
            ax.plot([needle_angle, needle_angle], [0, 0.9], 'k-', linewidth=3)
            ax.plot(needle_angle, 0.9, 'ko', markersize=10)
            
            # Add value text
            ax.text(np.pi/2, -0.3, f"{value:.2f}", 
                   ha='center', va='center', fontsize=20, fontweight='bold')
            
            # Configure axes
            ax.set_ylim(0, 1)
            ax.set_theta_zero_location('S')
            ax.set_theta_direction(1)
            ax.set_xticks([0, np.pi/4, np.pi/2, 3*np.pi/4, np.pi])
            ax.set_xticklabels([f'{min_val}', '', f'{(min_val+max_val)/2}', '', f'{max_val}'])
            ax.set_yticks([])
            ax.spines['polar'].set_visible(False)
            
            plt.title(title, fontsize=14, fontweight='bold', pad=20)
            
            plt.tight_layout()
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return output_path
            
        except Exception as e:
            print(f"[Charts] Error generating gauge chart: {e}")
            return None
    
    

    def _generate_multi_axis_chart(self, data, title, output_path):
        """Generate chart with multiple y-axes for different parameters"""
        try:
            fig, ax1 = plt.subplots(figsize=(12, 6))
            
            # Get data
            dates = data.get('dates', [])
            datasets = data.get('datasets', [])
            
            if not datasets:
                return None
            
            # First dataset on primary axis
            color1 = '#1e3a8a'
            ax1.set_xlabel('Date', fontsize=12)
            ax1.set_ylabel(datasets[0]['label'], color=color1, fontsize=12)
            ax1.plot(dates, datasets[0]['values'], color=color1, linewidth=2, marker='o', label=datasets[0]['label'])
            ax1.tick_params(axis='y', labelcolor=color1)
            ax1.grid(True, alpha=0.3)
            
            # Additional datasets on secondary axes
            axes = [ax1]
            colors = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444']
            
            for i, dataset in enumerate(datasets[1:], 1):
                ax = ax1.twinx()
                
                # Offset the right spine
                if i > 1:
                    ax.spines['right'].set_position(('outward', 60 * (i - 1)))
                
                color = colors[min(i-1, len(colors)-1)]
                ax.set_ylabel(dataset['label'], color=color, fontsize=12)
                ax.plot(dates, dataset['values'], color=color, linewidth=2, marker='s', label=dataset['label'])
                ax.tick_params(axis='y', labelcolor=color)
                
                axes.append(ax)
            
            # Format x-axis
            ax1.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
            ax1.xaxis.set_major_locator(mdates.DayLocator(interval=max(1, len(dates)//10)))
            plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45, ha='right')
            
            # Title
            ax1.set_title(title, fontsize=14, fontweight='bold', pad=20)
            
            # Legend
            lines = []
            labels = []
            for ax in axes:
                line, label = ax.get_legend_handles_labels()
                lines.extend(line)
                labels.extend(label)
            ax1.legend(lines, labels, loc='upper left', bbox_to_anchor=(0, -0.15), ncol=len(datasets))
            
            plt.tight_layout()
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return output_path
            
        except Exception as e:
            print(f"[Charts] Error generating multi-axis chart: {e}")
            return None
    
    

    def _generate_box_plot(self, data, title, output_path):
        """Generate box plot for parameter distribution"""
        try:
            fig, ax = plt.subplots(figsize=(10, 6))
            
            # Get data
            datasets = data.get('datasets', [])
            labels = data.get('labels', [])
            
            # Create box plot
            bp = ax.boxplot(datasets, labels=labels, patch_artist=True,
                           showmeans=True, meanline=True)
            
            # Customize colors
            colors = ['#1e3a8a', '#3b82f6', '#10b981', '#f59e0b', '#ef4444']
            for patch, color in zip(bp['boxes'], colors * (len(datasets) // len(colors) + 1)):
                patch.set_facecolor(color)
                patch.set_alpha(0.6)
            
            # Customize other elements
            for element in ['whiskers', 'fliers', 'means', 'medians', 'caps']:
                plt.setp(bp[element], color='black', linewidth=1.5)
            
            ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
            ax.set_ylabel('Value', fontsize=12)
            ax.grid(True, alpha=0.3, axis='y')
            
            # Rotate x labels if needed
            if len(labels) > 5:
                plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
            
            plt.tight_layout()
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return output_path
            
        except Exception as e:
            print(f"[Charts] Error generating box plot: {e}")
            return None
    
    

    def _generate_stacked_area_chart(self, data, title, output_path):
        """Generate stacked area chart for composition over time"""
        try:
            fig, ax = plt.subplots(figsize=(12, 6))
            
            # Get data
            dates = data.get('dates', [])
            datasets = data.get('datasets', [])
            labels = data.get('labels', [])
            
            # Prepare data for stacking
            values = [dataset['values'] for dataset in datasets]
            
            # Create stacked area chart
            colors = ['#1e3a8a', '#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6']
            ax.stackplot(dates, *values, labels=labels, colors=colors, alpha=0.7)
            
            # Format x-axis
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
            ax.xaxis.set_major_locator(mdates.DayLocator(interval=max(1, len(dates)//10)))
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
            
            ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
            ax.set_xlabel('Date', fontsize=12)
            ax.set_ylabel('Value', fontsize=12)
            ax.legend(loc='upper left', bbox_to_anchor=(1, 1))
            ax.grid(True, alpha=0.3)
            
            plt.tight_layout()
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return output_path
            
        except Exception as e:
            print(f"[Charts] Error generating stacked area chart: {e}")
            return None
    
    

    def _generate_comparison_chart(self, data, title, output_path):
        """Generate comparison chart for multiple pools"""
        try:
            fig, ax = plt.subplots(figsize=(12, 6))
            
            # Get data
            categories = data.get('categories', [])
            pools = data.get('pools', [])
            
            # Set up bar positions
            x = np.arange(len(categories))
            width = 0.8 / len(pools)
            
            # Create bars for each pool
            colors = ['#1e3a8a', '#3b82f6', '#10b981', '#f59e0b', '#ef4444']
            for i, pool in enumerate(pools):
                offset = (i - len(pools)/2) * width + width/2
                ax.bar(x + offset, pool['values'], width, label=pool['name'],
                      color=colors[i % len(colors)], alpha=0.8)
            
            ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
            ax.set_xlabel('Parameters', fontsize=12)
            ax.set_ylabel('Value', fontsize=12)
            ax.set_xticks(x)
            ax.set_xticklabels(categories, rotation=45, ha='right')
            ax.legend()
            ax.grid(True, alpha=0.3, axis='y')
            
            plt.tight_layout()
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return output_path
            
        except Exception as e:
            print(f"[Charts] Error generating comparison chart: {e}")
            return None
    
    

    def _generate_radar_chart(self, data, title, output_path):
        """Generate radar chart for pool health overview"""
        try:
            fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(projection='polar'))
            
            # Get data
            categories = data.get('categories', [])
            values = data.get('values', [])
            max_value = data.get('max_value', 100)
            
            # Number of variables
            N = len(categories)
            
            # Compute angle for each axis
            angles = [n / float(N) * 2 * np.pi for n in range(N)]
            values = values + [values[0]]  # Complete the circle
            angles += angles[:1]
            
            # Plot
            ax.plot(angles, values, 'o-', linewidth=2, color='#1e3a8a', label='Current')
            ax.fill(angles, values, alpha=0.25, color='#1e3a8a')
            
            # Add optimal range if provided
            if 'optimal_values' in data:
                optimal = data['optimal_values'] + [data['optimal_values'][0]]
                ax.plot(angles, optimal, 'o-', linewidth=2, color='#10b981', label='Optimal', linestyle='--')
                ax.fill(angles, optimal, alpha=0.15, color='#10b981')
            
            # Fix axis to go in the right order
            ax.set_xticks(angles[:-1])
            ax.set_xticklabels(categories)
            ax.set_ylim(0, max_value)
            
            # Add title and legend
            ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
            ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
            ax.grid(True)
            
            plt.tight_layout()
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return output_path
            
        except Exception as e:
            print(f"[Charts] Error generating radar chart: {e}")
            return None

    # Export Options
    def _export_to_excel(self, data, output_path, sheet_name="Data"):
        """Export data to Excel format"""
        try:
            # Create Excel writer
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                # Convert data to DataFrame
                if isinstance(data, dict):
                    # Multiple sheets
                    for name, sheet_data in data.items():
                        df = pd.DataFrame(sheet_data)
                        df.to_excel(writer, sheet_name=name, index=False)
                else:
                    # Single sheet
                    df = pd.DataFrame(data)
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
            
            print(f"[Export] Excel file created: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"[Export] Error exporting to Excel: {e}")
            return None
    
    

    def _export_to_csv(self, data, output_path):
        """Export data to CSV format"""
        try:
            df = pd.DataFrame(data)
            df.to_csv(output_path, index=False)
            
            print(f"[Export] CSV file created: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"[Export] Error exporting to CSV: {e}")
            return None
    
    

    def _export_pool_data_excel(self, pool_ids, start_date, end_date):
        """Export pool data to Excel with multiple sheets"""
        try:
            output_path = self.data_dir / f"pool_data_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            
            data_sheets = {}
            
            for pool_id in pool_ids:
                # Get pool data
                pool = self._get_pool_data(pool_id)
                if not pool:
                    continue
                
                pool_name = pool.get('name', pool_id)
                
                # Load readings
                readings = self._load_readings_for_range(pool_id, start_date, end_date)
                if readings:
                    data_sheets[f"{pool_name}_Readings"] = readings
                
                # Load alerts
                alerts = self._load_alerts_for_range(pool_id, start_date, end_date)
                if alerts:
                    data_sheets[f"{pool_name}_Alerts"] = alerts
                
                # Add pool info sheet
                pool_info = {
                    'Property': ['Pool ID', 'Name', 'Type', 'Volume', 'Surface Area'],
                    'Value': [
                        pool.get('id', ''),
                        pool.get('name', ''),
                        pool.get('type', ''),
                        f"{pool.get('volume', 0)} gallons",
                        f"{pool.get('surface_area', 0)} sq ft"
                    ]
                }
                data_sheets[f"{pool_name}_Info"] = pool_info
            
            # Export to Excel
            return self._export_to_excel(data_sheets, output_path)
            
        except Exception as e:
            print(f"[Export] Error exporting pool data to Excel: {e}")
            return None
    
    

    def _export_readings_csv(self, pool_id, start_date, end_date):
        """Export readings to CSV"""
        try:
            output_path = self.data_dir / f"readings_{pool_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            
            readings = self._load_readings_for_range(pool_id, start_date, end_date)
            
            if readings:
                return self._export_to_csv(readings, output_path)
            else:
                print(f"[Export] No readings found for pool {pool_id}")
                return None
                
        except Exception as e:
            print(f"[Export] Error exporting readings to CSV: {e}")
            return None
    
    

    def _export_alerts_csv(self, pool_id, start_date, end_date):
        """Export alerts to CSV"""
        try:
            output_path = self.data_dir / f"alerts_{pool_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            
            alerts = self._load_alerts_for_range(pool_id, start_date, end_date)
            
            if alerts:
                return self._export_to_csv(alerts, output_path)
            else:
                print(f"[Export] No alerts found for pool {pool_id}")
                return None
                
        except Exception as e:
            print(f"[Export] Error exporting alerts to CSV: {e}")
            return None
    
    

    def _batch_generate_reports(self, pool_ids, start_date, end_date, template, options):
        """Generate reports for multiple pools"""
        try:
            report_paths = []
            
            for pool_id in pool_ids:
                # Generate report for each pool
                report_path = self._generate_pdf_report(
                    [pool_id],
                    start_date,
                    end_date,
                    template,
                    options
                )
                
                if report_path:
                    report_paths.append(report_path)
            
            print(f"[Export] Generated {len(report_paths)} reports")
            return report_paths
            
        except Exception as e:
            print(f"[Export] Error in batch report generation: {e}")
            return []
    
    

    def _create_report_archive(self, report_paths, archive_name=None):
        """Create ZIP archive of multiple reports"""
        try:
            if not archive_name:
                archive_name = f"reports_archive_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
            
            archive_path = self.data_dir / archive_name
            
            with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for report_path in report_paths:
                    if Path(report_path).exists():
                        zipf.write(report_path, Path(report_path).name)
            
            print(f"[Export] Archive created: {archive_path}")
            return archive_path
            
        except Exception as e:
            print(f"[Export] Error creating archive: {e}")
            return None
    
    

    def _export_statistics_excel(self, pool_ids, start_date, end_date):
        """Export statistical analysis to Excel"""
        try:
            output_path = self.data_dir / f"statistics_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            
            data_sheets = {}
            
            for pool_id in pool_ids:
                pool = self._get_pool_data(pool_id)
                if not pool:
                    continue
                
                pool_name = pool.get('name', pool_id)
                
                # Calculate statistics
                stats = self._calculate_all_statistics(pool_id, start_date, end_date)
                
                if stats:
                    # Convert stats to tabular format
                    stats_data = []
                    for param, param_stats in stats.items():
                        if isinstance(param_stats, dict):
                            stats_data.append({
                                'Parameter': param,
                                'Mean': param_stats.get('mean', 0),
                                'Median': param_stats.get('median', 0),
                                'Min': param_stats.get('min', 0),
                                'Max': param_stats.get('max', 0),
                                'Std Dev': param_stats.get('std', 0),
                                'Count': param_stats.get('count', 0)
                            })
                    
                    data_sheets[pool_name] = stats_data
            
            if data_sheets:
                return self._export_to_excel(data_sheets, output_path)
            else:
                print("[Export] No statistics data to export")
                return None
                
        except Exception as e:
            print(f"[Export] Error exporting statistics: {e}")
            return None
    
    

    def _export_maintenance_log_excel(self, pool_ids, start_date, end_date):
        """Export maintenance log to Excel"""
        try:
            output_path = self.data_dir / f"maintenance_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            
            data_sheets = {}
            
            for pool_id in pool_ids:
                pool = self._get_pool_data(pool_id)
                if not pool:
                    continue
                
                pool_name = pool.get('name', pool_id)
                
                # Get maintenance data
                maintenance_data = self._aggregate_maintenance_data(pool_id, start_date, end_date)
                
                if maintenance_data:
                    data_sheets[pool_name] = maintenance_data
            
            if data_sheets:
                return self._export_to_excel(data_sheets, output_path)
            else:
                print("[Export] No maintenance data to export")
                return None
                
        except Exception as e:
            print(f"[Export] Error exporting maintenance log: {e}")
            return None
    
    

    def _export_cost_analysis_excel(self, pool_ids, start_date, end_date):
        """Export cost analysis to Excel"""
        try:
            output_path = self.data_dir / f"cost_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            
            data_sheets = {}
            
            for pool_id in pool_ids:
                pool = self._get_pool_data(pool_id)
                if not pool:
                    continue
                
                pool_name = pool.get('name', pool_id)
                
                # Calculate costs
                costs = self._calculate_costs(pool_id, start_date, end_date)
                
                if costs:
                    # Convert to tabular format
                    cost_data = []
                    for chemical, amount in costs.get('chemicals', {}).items():
                        cost_data.append({
                            'Item': chemical,
                            'Amount': amount,
                            'Cost': costs.get('chemical_costs', {}).get(chemical, 0),
                            'Category': 'Chemical'
                        })
                    
                    # Add total
                    cost_data.append({
                        'Item': 'TOTAL',
                        'Amount': '',
                        'Cost': costs.get('total_cost', 0),
                        'Category': 'Total'
                    })
                    
                    data_sheets[pool_name] = cost_data
            
            if data_sheets:
                return self._export_to_excel(data_sheets, output_path)
            else:
                print("[Export] No cost data to export")
                return None
                
        except Exception as e:
            print(f"[Export] Error exporting cost analysis: {e}")
            return None
    
    

    def _create_export_ui(self):
        """Create export options UI dialog"""
        try:
            import tkinter as tk
            from tkinter import ttk, messagebox
            
            dialog = tk.Toplevel(self)
            dialog.title("Export Options")
            dialog.geometry("600x500")
            dialog.transient(self)
            dialog.grab_set()
            
            # Title
            tk.Label(
                dialog,
                text="Export Data",
                font=("Arial", 14, "bold")
            ).pack(pady=10)
            
            # Export type selection
            type_frame = ttk.LabelFrame(dialog, text="Export Type", padding=15)
            type_frame.pack(fill="x", padx=20, pady=10)
            
            export_type_var = tk.StringVar(value="excel")
            
            ttk.Radiobutton(
                type_frame,
                text="Excel Workbook (.xlsx)",
                variable=export_type_var,
                value="excel"
            ).pack(anchor="w", pady=2)
            
            ttk.Radiobutton(
                type_frame,
                text="CSV Files (.csv)",
                variable=export_type_var,
                value="csv"
            ).pack(anchor="w", pady=2)
            
            ttk.Radiobutton(
                type_frame,
                text="PDF Reports (Batch)",
                variable=export_type_var,
                value="pdf_batch"
            ).pack(anchor="w", pady=2)
            
            ttk.Radiobutton(
                type_frame,
                text="ZIP Archive (All)",
                variable=export_type_var,
                value="zip"
            ).pack(anchor="w", pady=2)
            
            # Data selection
            data_frame = ttk.LabelFrame(dialog, text="Data to Export", padding=15)
            data_frame.pack(fill="x", padx=20, pady=10)
            
            export_readings = tk.BooleanVar(value=True)
            export_alerts = tk.BooleanVar(value=True)
            export_stats = tk.BooleanVar(value=True)
            export_maintenance = tk.BooleanVar(value=False)
            export_costs = tk.BooleanVar(value=False)
            
            ttk.Checkbutton(data_frame, text="Readings", variable=export_readings).pack(anchor="w", pady=2)
            ttk.Checkbutton(data_frame, text="Alerts", variable=export_alerts).pack(anchor="w", pady=2)
            ttk.Checkbutton(data_frame, text="Statistics", variable=export_stats).pack(anchor="w", pady=2)
            ttk.Checkbutton(data_frame, text="Maintenance Log", variable=export_maintenance).pack(anchor="w", pady=2)
            ttk.Checkbutton(data_frame, text="Cost Analysis", variable=export_costs).pack(anchor="w", pady=2)
            
            # Pool selection
            pool_frame = ttk.LabelFrame(dialog, text="Pools", padding=15)
            pool_frame.pack(fill="x", padx=20, pady=10)
            
            tk.Label(pool_frame, text="Select pools to export:").pack(anchor="w", pady=5)
            
            # Use existing pool selection from PDF tab
            selected_pools = []
            if hasattr(self, 'pdf_pool_vars'):
                for pool_id, var in self.pdf_pool_vars.items():
                    if var.get():
                        selected_pools.append(pool_id)
            
            tk.Label(pool_frame, text=f"Selected: {len(selected_pools)} pool(s)").pack(anchor="w", pady=5)
            
            # Buttons
            button_frame = ttk.Frame(dialog)
            button_frame.pack(fill="x", padx=20, pady=20)
            
            def do_export():
                export_type = export_type_var.get()
                
                # Get date range from PDF tab
                start_date = self.pdf_start_date.get() if hasattr(self, 'pdf_start_date') else None
                end_date = self.pdf_end_date.get() if hasattr(self, 'pdf_end_date') else None
                
                if not selected_pools:
                    messagebox.showwarning("No Pools", "Please select at least one pool.")
                    return
                
                try:
                    exported_files = []
                    
                    if export_type == "excel":
                        if export_readings.get():
                            file = self._export_pool_data_excel(selected_pools, start_date, end_date)
                            if file:
                                exported_files.append(file)
                        
                        if export_stats.get():
                            file = self._export_statistics_excel(selected_pools, start_date, end_date)
                            if file:
                                exported_files.append(file)
                        
                        if export_maintenance.get():
                            file = self._export_maintenance_log_excel(selected_pools, start_date, end_date)
                            if file:
                                exported_files.append(file)
                        
                        if export_costs.get():
                            file = self._export_cost_analysis_excel(selected_pools, start_date, end_date)
                            if file:
                                exported_files.append(file)
                    
                    elif export_type == "csv":
                        for pool_id in selected_pools:
                            if export_readings.get():
                                file = self._export_readings_csv(pool_id, start_date, end_date)
                                if file:
                                    exported_files.append(file)
                            
                            if export_alerts.get():
                                file = self._export_alerts_csv(pool_id, start_date, end_date)
                                if file:
                                    exported_files.append(file)
                    
                    elif export_type == "pdf_batch":
                        template = self.pdf_template_var.get() if hasattr(self, 'pdf_template_var') else 'executive_summary'
                        options = {
                            'include_charts': True,
                            'include_recommendations': True,
                            'include_cost_analysis': True
                        }
                        files = self._batch_generate_reports(selected_pools, start_date, end_date, template, options)
                        exported_files.extend(files)
                    
                    elif export_type == "zip":
                        # Export everything and create archive
                        all_files = []
                        
                        # Excel exports
                        file = self._export_pool_data_excel(selected_pools, start_date, end_date)
                        if file:
                            all_files.append(file)
                        
                        # PDF reports
                        template = self.pdf_template_var.get() if hasattr(self, 'pdf_template_var') else 'executive_summary'
                        options = {'include_charts': True, 'include_recommendations': True, 'include_cost_analysis': True}
                        files = self._batch_generate_reports(selected_pools, start_date, end_date, template, options)
                        all_files.extend(files)
                        
                        # Create archive
                        archive = self._create_report_archive(all_files)
                        if archive:
                            exported_files.append(archive)
                    
                    if exported_files:
                        messagebox.showinfo(
                            "Export Complete",
                            f"Successfully exported {len(exported_files)} file(s)!\n\n"
                            f"Location: {self.data_dir}"
                        )
                        dialog.destroy()
                    else:
                        messagebox.showwarning("Export Failed", "No files were exported.")
                
                except Exception as e:
                    messagebox.showerror("Export Error", f"Failed to export: {str(e)}")
            
            ttk.Button(
                button_frame,
                text="Export",
                command=do_export
            ).pack(side="left", padx=5)
            
            ttk.Button(
                button_frame,
                text="Cancel",
                command=dialog.destroy
            ).pack(side="left", padx=5)
            
        except Exception as e:
            print(f"[Export] Error creating export UI: {e}")
            import traceback
            traceback.print_exc()



    # ============================================================================
    # PHASE 2.3: ADVANCED BRANDING & CUSTOMIZATION (49 methods)
    # ============================================================================

def _create_branding_tab(self):
    """Create the main Branding & Customization tab"""
    branding_frame = ttk.Frame(self.notebook)
    self.notebook.add(branding_frame, text="🎨 Branding")
    
    # Create main container with scrollbar
    canvas = tk.Canvas(branding_frame, bg='white')
    scrollbar = ttk.Scrollbar(branding_frame, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)
    
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    
    # Title
    title_label = tk.Label(scrollable_frame, text="Branding & Customization",
                          font=('Helvetica', 16, 'bold'), bg='white')
    title_label.pack(pady=10)
    
    # Create sections
    sections_frame = ttk.Frame(scrollable_frame)
    sections_frame.pack(fill='both', expand=True, padx=20, pady=10)
    
    # Section buttons
    sections = [
        ("🎨 Color Scheme", self._create_color_scheme_editor),
        ("🖼️ Logo Management", self._create_logo_manager),
        ("🏢 Company Information", self._create_company_info_editor),
        ("📄 Report Templates", self._create_report_template_editor),
        ("📧 Email Templates", self._create_email_template_editor),
        ("💾 Branding Presets", self._create_branding_presets),
        ("🚀 Splash Screen", self._create_splash_screen_editor)
    ]
    
    for i, (text, command) in enumerate(sections):
        btn = tk.Button(sections_frame, text=text, command=command,
                       font=('Helvetica', 12), width=30, height=2)
        btn.grid(row=i//2, column=i%2, padx=10, pady=10, sticky='ew')
    
    # Current branding preview
    preview_frame = ttk.LabelFrame(scrollable_frame, text="Current Branding Preview")
    preview_frame.pack(fill='x', padx=20, pady=10)
    
    self._update_branding_preview(preview_frame)
    
    # Action buttons
    action_frame = ttk.Frame(scrollable_frame)
    action_frame.pack(pady=20)
    
    ttk.Button(action_frame, text="Save Branding",
              command=self._save_branding_config).pack(side='left', padx=5)
    ttk.Button(action_frame, text="Reset to Default",
              command=self._reset_branding_to_default).pack(side='left', padx=5)
    ttk.Button(action_frame, text="Export Config",
              command=self._export_branding_config).pack(side='left', padx=5)
    ttk.Button(action_frame, text="Import Config",
              command=self._import_branding_config).pack(side='left', padx=5)
    
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

def _load_branding_config(self):
    """Load branding configuration from file"""
    config_file = os.path.join(self.data_dir, 'branding_config.json')
    
    # Default branding configuration
    default_config = {
        "company_info": {
            "name": "Deep Blue Pool Chemistry",
            "tagline": "Professional Pool Management",
            "address": "",
            "phone": "",
            "email": "",
            "website": ""
        },
        "colors": {
            "primary": "#1e3a8a",
            "secondary": "#93c5fd",
            "accent": "#3b82f6",
            "text": "#1f2937",
            "background": "#ffffff",
            "success": "#10b981",
            "warning": "#f59e0b",
            "error": "#ef4444"
        },
        "logos": {
            "primary": "logo.png",
            "secondary": "",
            "favicon": "",
            "watermark": ""
        },
        "fonts": {
            "heading": "Helvetica-Bold",
            "body": "Helvetica",
            "monospace": "Courier"
        },
        "report_templates": {
            "header_height": 1.5,
            "footer_height": 0.75,
            "margin_top": 1.0,
            "margin_bottom": 1.0,
            "margin_left": 0.75,
            "margin_right": 0.75,
            "show_watermark": False,
            "watermark_opacity": 0.1
        },
        "email_templates": {
            "header_html": "",
            "footer_html": "",
            "signature": "Best regards,\nDeep Blue Pool Chemistry Team"
        }
    }
    
    try:
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                config = json.load(f)
                # Merge with defaults to ensure all keys exist
                for key in default_config:
                    if key not in config:
                        config[key] = default_config[key]
                    elif isinstance(default_config[key], dict):
                        for subkey in default_config[key]:
                            if subkey not in config[key]:
                                config[key][subkey] = default_config[key][subkey]
                return config
        else:
            return default_config
    except Exception as e:
        print(f"Error loading branding config: {e}")
        return default_config

def _save_branding_config(self):
    """Save branding configuration to file"""
    try:
        config_file = os.path.join(self.data_dir, 'branding_config.json')
        
        with open(config_file, 'w') as f:
            json.dump(self.branding_config, f, indent=2)
        
        messagebox.showinfo("Success", "Branding configuration saved successfully!")
        self._apply_branding()
        
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save branding configuration: {e}")

def _apply_branding(self):
    """Apply branding throughout the application"""
    try:
        # Apply color scheme
        self._apply_color_scheme()
        
        # Update window title with company name
        company_name = self.branding_config['company_info']['name']
        self.root.title(company_name)
        
        # Refresh all UI elements
        self.root.update_idletasks()
        
        messagebox.showinfo("Success", "Branding applied successfully!")
        
    except Exception as e:
        messagebox.showerror("Error", f"Failed to apply branding: {e}")

def _reset_branding_to_default(self):
    """Reset branding to default settings"""
    if messagebox.askyesno("Confirm Reset", 
                          "Are you sure you want to reset all branding to default settings?"):
        try:
            # Remove config file
            config_file = os.path.join(self.data_dir, 'branding_config.json')
            if os.path.exists(config_file):
                os.remove(config_file)
            
            # Reload default config
            self.branding_config = self._load_branding_config()
            self._apply_branding()
            
            messagebox.showinfo("Success", "Branding reset to default!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to reset branding: {e}")

    def _preview_branding(self):
        """Preview branding changes by generating a sample PDF report"""
        # Show info dialog
        response = messagebox.askyesno(
            "Generate Preview",
            "This will generate a sample PDF report with your current branding settings.\n\n"
            "The PDF will include:\n"
            "• Your company logo and information\n"
            "• Your custom color scheme\n"
            "• Sample pool data and charts\n"
            "• All report formatting\n\n"
            "Do you want to continue?",
            icon='question'
        )
        
        if response:
            # Generate and open the preview PDF
            self._generate_preview_pdf()


    def _generate_preview_pdf(self):
        """Generate a sample PDF report with current branding for preview"""
        try:
            from datetime import datetime, timedelta
            import tempfile
            import os
            
            # Create sample data for preview
            sample_pool = {
                'id': 'PREVIEW001',
                'name': 'Sample Pool (Preview)',
                'type': 'Residential',
                'volume': 20000,
                'location': 'Preview Location'
            }
            
            # Create sample readings (last 7 days)
            sample_readings = []
            base_date = datetime.now()
            for i in range(7):
                reading_date = base_date - timedelta(days=i)
                sample_readings.append({
                    'timestamp': reading_date.strftime('%Y-%m-%d %H:%M:%S'),
                    'pool_id': 'PREVIEW001',
                    'fc': 3.0 + (i * 0.2),
                    'ph': 7.4 + (i * 0.05),
                    'ta': 100 + (i * 5),
                    'ch': 250 + (i * 10),
                    'cya': 50,
                    'salt': 3200,
                    'temperature': 78 + (i * 0.5),
                    'tds': 1500,
                    'phosphates': 100
                })
            
            # Create sample alerts
            sample_alerts = [
                {
                    'timestamp': base_date.strftime('%Y-%m-%d %H:%M:%S'),
                    'pool_id': 'PREVIEW001',
                    'parameter': 'Free Chlorine',
                    'severity': 'warning',
                    'message': 'Free Chlorine slightly low (2.8 ppm)',
                    'recommendation': 'Add 1 lb of chlorine'
                },
                {
                    'timestamp': (base_date - timedelta(days=2)).strftime('%Y-%m-%d %H:%M:%S'),
                    'pool_id': 'PREVIEW001',
                    'parameter': 'pH',
                    'severity': 'info',
                    'message': 'pH within optimal range (7.4)',
                    'recommendation': 'No action needed'
                }
            ]
            
            # Create temporary file for preview PDF
            temp_dir = tempfile.gettempdir()
            preview_filename = f"branding_preview_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            preview_path = os.path.join(temp_dir, preview_filename)
            
            # Aggregate data for PDF generation
            aggregated_data = {
                'pools': [sample_pool],
                'readings': sample_readings,
                'alerts': sample_alerts,
                'statistics': {
                    'PREVIEW001': {
                        'fc': {'avg': 3.5, 'min': 3.0, 'max': 4.2, 'current': 3.5},
                        'ph': {'avg': 7.45, 'min': 7.4, 'max': 7.7, 'current': 7.45},
                        'ta': {'avg': 115, 'min': 100, 'max': 130, 'current': 115},
                        'ch': {'avg': 280, 'min': 250, 'max': 310, 'current': 280},
                        'temperature': {'avg': 79, 'min': 78, 'max': 81.5, 'current': 79}
                    }
                },
                'date_range': {
                    'start': (base_date - timedelta(days=7)).strftime('%Y-%m-%d'),
                    'end': base_date.strftime('%Y-%m-%d')
                }
            }
            
            # Generate the PDF using existing PDF generation method
            self._build_pdf_document(
                preview_path,
                aggregated_data,
                'executive',  # Use executive summary template
                'Sample Branding Preview Report'
            )
            
            # Open the PDF automatically
            import platform
            import subprocess
            
            system = platform.system()
            if system == 'Darwin':  # macOS
                subprocess.run(['open', preview_path])
            elif system == 'Windows':
                os.startfile(preview_path)
            else:  # Linux
                subprocess.run(['xdg-open', preview_path])
            
            messagebox.showinfo(
                "Preview Generated",
                f"Preview PDF generated successfully!\n\nFile saved to:\n{preview_path}\n\nThe PDF has been opened automatically."
            )
            
            return preview_path
            
        except Exception as e:
            messagebox.showerror("Preview Error", f"Failed to generate preview PDF:\n{str(e)}")
            return None


    def update_preview():
        preview_text.delete('1.0', tk.END)
        preview_text.insert('1.0', self._format_company_info())
    
    update_preview()
    
    # Action buttons
    action_frame = ttk.Frame(editor_window)
    action_frame.pack(pady=20)
    
    def save_and_close():
        for key, entry in entries.items():
            self.branding_config['company_info'][key] = entry.get()
        self._save_company_info()
        editor_window.destroy()
    
    ttk.Button(action_frame, text="Preview", command=update_preview).pack(side='left', padx=5)
    ttk.Button(action_frame, text="Save", command=save_and_close).pack(side='left', padx=5)
    ttk.Button(action_frame, text="Cancel", command=editor_window.destroy).pack(side='left', padx=5)

def _save_company_info(self):
    """Save company information"""
    try:
        self._save_branding_config()
        messagebox.showinfo("Success", "Company information saved successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save company information: {e}")

def _load_company_info(self):
    """Load company information"""
    return self.branding_config.get('company_info', {})

def _add_company_info_to_reports(self, story):
    """Add company information to PDF reports"""
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import Paragraph, Spacer
    
    styles = getSampleStyleSheet()
    company_info = self._load_company_info()
    
    # Add company name
    if company_info.get('name'):
        story.append(Paragraph(company_info['name'], styles['Heading1']))
        story.append(Spacer(1, 0.2))
    
    # Add tagline
    if company_info.get('tagline'):
        story.append(Paragraph(company_info['tagline'], styles['Italic']))
        story.append(Spacer(1, 0.2))
    
    # Add contact info
    contact_parts = []
    if company_info.get('address'):
        contact_parts.append(company_info['address'])
    if company_info.get('phone'):
        contact_parts.append(f"Phone: {company_info['phone']}")
    if company_info.get('email'):
        contact_parts.append(f"Email: {company_info['email']}")
    if company_info.get('website'):
        contact_parts.append(f"Website: {company_info['website']}")
    
    if contact_parts:
        contact_text = " | ".join(contact_parts)
        story.append(Paragraph(contact_text, styles['Normal']))
        story.append(Spacer(1, 0.3))

def _format_company_info(self):
    """Format company information for display"""
    company_info = self._load_company_info()
    
    lines = []
    if company_info.get('name'):
        lines.append(company_info['name'])
    if company_info.get('tagline'):
        lines.append(company_info['tagline'])
    if company_info.get('address'):
        lines.append(company_info['address'])
    if company_info.get('phone'):
        lines.append(f"Phone: {company_info['phone']}")
    if company_info.get('email'):
        lines.append(f"Email: {company_info['email']}")
    if company_info.get('website'):
        lines.append(f"Website: {company_info['website']}")
    
    return "\n".join(lines)


# ============================================================================
# SECTION 5: REPORT TEMPLATE CUSTOMIZATION (8 methods)
# ============================================================================

def _create_report_template_editor(self):
    """Create report template customization interface"""
    editor_window = tk.Toplevel(self.root)
    editor_window.title("Report Template Editor")
    editor_window.geometry("700x600")
    
    # Title
    title_label = tk.Label(editor_window, text="Report Template Customization",
                          font=('Helvetica', 16, 'bold'))
    title_label.pack(pady=10)
    
    # Notebook for different sections
    notebook = ttk.Notebook(editor_window)
    notebook.pack(fill='both', expand=True, padx=20, pady=10)
    
    # Page Layout tab
    layout_frame = ttk.Frame(notebook)
    notebook.add(layout_frame, text="Page Layout")
    
    # Margins
    margins_frame = ttk.LabelFrame(layout_frame, text="Margins (inches)")
    margins_frame.pack(fill='x', padx=10, pady=10)
    
    margin_fields = [
        ("Top:", "margin_top"),
        ("Bottom:", "margin_bottom"),
        ("Left:", "margin_left"),
        ("Right:", "margin_right")
    ]
    
    margin_entries = {}
    for i, (label, key) in enumerate(margin_fields):
        tk.Label(margins_frame, text=label).grid(row=i, column=0, sticky='w', padx=5, pady=5)
        entry = tk.Entry(margins_frame, width=10)
        entry.grid(row=i, column=1, sticky='w', padx=5, pady=5)
        entry.insert(0, str(self.branding_config['report_templates'].get(key, 1.0)))
        margin_entries[key] = entry
    
    # Header/Footer
    hf_frame = ttk.LabelFrame(layout_frame, text="Header & Footer (inches)")
    hf_frame.pack(fill='x', padx=10, pady=10)
    
    tk.Label(hf_frame, text="Header Height:").grid(row=0, column=0, sticky='w', padx=5, pady=5)
    header_entry = tk.Entry(hf_frame, width=10)
    header_entry.grid(row=0, column=1, sticky='w', padx=5, pady=5)
    header_entry.insert(0, str(self.branding_config['report_templates'].get('header_height', 1.5)))
    
    tk.Label(hf_frame, text="Footer Height:").grid(row=1, column=0, sticky='w', padx=5, pady=5)
    footer_entry = tk.Entry(hf_frame, width=10)
    footer_entry.grid(row=1, column=1, sticky='w', padx=5, pady=5)
    footer_entry.insert(0, str(self.branding_config['report_templates'].get('footer_height', 0.75)))
    
    # Watermark tab
    watermark_frame = ttk.Frame(notebook)
    notebook.add(watermark_frame, text="Watermark")
    
    watermark_check = tk.BooleanVar(value=self.branding_config['report_templates'].get('show_watermark', False))
    tk.Checkbutton(watermark_frame, text="Show Watermark", variable=watermark_check).pack(pady=10)
    
    tk.Label(watermark_frame, text="Watermark Opacity (0.0 - 1.0):").pack(pady=5)
    opacity_entry = tk.Entry(watermark_frame, width=10)
    opacity_entry.pack(pady=5)
    opacity_entry.insert(0, str(self.branding_config['report_templates'].get('watermark_opacity', 0.1)))
    
    # Action buttons
    action_frame = ttk.Frame(editor_window)
    action_frame.pack(pady=20)
    
    def save_template():
        try:
            # Save margins
            for key, entry in margin_entries.items():
                self.branding_config['report_templates'][key] = float(entry.get())
            
            # Save header/footer
            self.branding_config['report_templates']['header_height'] = float(header_entry.get())
            self.branding_config['report_templates']['footer_height'] = float(footer_entry.get())
            
            # Save watermark
            self.branding_config['report_templates']['show_watermark'] = watermark_check.get()
            self.branding_config['report_templates']['watermark_opacity'] = float(opacity_entry.get())
            
            self._save_custom_template()
            editor_window.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save template: {e}")
    
    ttk.Button(action_frame, text="Preview", command=self._preview_custom_template).pack(side='left', padx=5)
    ttk.Button(action_frame, text="Save", command=save_template).pack(side='left', padx=5)
    ttk.Button(action_frame, text="Cancel", command=editor_window.destroy).pack(side='left', padx=5)

def _customize_report_header(self):
    """Customize report header design"""
    messagebox.showinfo("Header Customization", 
                       "Header customization allows you to:\n\n"
                       "• Add custom logo placement\n"
                       "• Change header height\n"
                       "• Add custom text\n"
                       "• Change colors and fonts")

def _customize_report_footer(self):
    """Customize report footer design"""
    messagebox.showinfo("Footer Customization",
                       "Footer customization allows you to:\n\n"
                       "• Add page numbers\n"
                       "• Add company information\n"
                       "• Change footer height\n"
                       "• Add custom text")

def _add_watermark(self):
    """Add watermark to reports"""
    file_path = filedialog.askopenfilename(
        filetypes=[("Image files", "*.png *.jpg *.jpeg"), ("All files", "*.*")],
        title="Select Watermark Image"
    )
    
    if file_path:
        dest_path = os.path.join(self.data_dir, "watermark.png")
        import shutil
        shutil.copy(file_path, dest_path)
        self.branding_config['logos']['watermark'] = dest_path
        self._save_branding_config()
        messagebox.showinfo("Success", "Watermark added successfully!")

def _customize_cover_page(self):
    """Customize cover page design"""
    messagebox.showinfo("Cover Page Customization",
                       "Cover page customization allows you to:\n\n"
                       "• Add custom background\n"
                       "• Change layout\n"
                       "• Add custom text\n"
                       "• Change colors and fonts")

def _save_custom_template(self):
    """Save custom report template"""
    try:
        self._save_branding_config()
        messagebox.showinfo("Success", "Report template saved successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save template: {e}")

def _load_custom_template(self):
    """Load custom report template"""
    return self.branding_config.get('report_templates', {})

def _preview_custom_template(self):
    """Preview custom report template"""
    preview_window = tk.Toplevel(self.root)
    preview_window.title("Template Preview")
    preview_window.geometry("600x800")
    
    canvas = tk.Canvas(preview_window, bg='white')
    canvas.pack(fill='both', expand=True)
    
    # Draw template preview
    template = self._load_custom_template()
    
    # Header
    header_height = template.get('header_height', 1.5) * 72  # Convert to pixels
    canvas.create_rectangle(0, 0, 600, header_height, fill='lightgray', outline='black')
    canvas.create_text(300, header_height/2, text="HEADER", font=('Helvetica', 14, 'bold'))
    
    # Content area
    margin_top = template.get('margin_top', 1.0) * 72
    margin_bottom = template.get('margin_bottom', 1.0) * 72
    margin_left = template.get('margin_left', 0.75) * 72
    margin_right = template.get('margin_right', 0.75) * 72
    
    canvas.create_rectangle(margin_left, header_height + margin_top,
                          600 - margin_right, 800 - margin_bottom,
                          outline='blue', dash=(5, 5))
    canvas.create_text(300, 400, text="CONTENT AREA", font=('Helvetica', 12))
    
    # Footer
    footer_height = template.get('footer_height', 0.75) * 72
    canvas.create_rectangle(0, 800 - footer_height, 600, 800, fill='lightgray', outline='black')
    canvas.create_text(300, 800 - footer_height/2, text="FOOTER", font=('Helvetica', 14, 'bold'))


# ============================================================================
# SECTION 6: EMAIL TEMPLATE CUSTOMIZATION (6 methods)
# ============================================================================

def _create_email_template_editor(self):
    """Create email template customization interface"""
    editor_window = tk.Toplevel(self.root)
    editor_window.title("Email Template Editor")
    editor_window.geometry("700x600")
    
    # Title
    title_label = tk.Label(editor_window, text="Email Template Customization",
                          font=('Helvetica', 16, 'bold'))
    title_label.pack(pady=10)
    
    # Header section
    header_frame = ttk.LabelFrame(editor_window, text="Email Header HTML")
    header_frame.pack(fill='both', expand=True, padx=20, pady=10)
    
    header_text = tk.Text(header_frame, height=8, width=70)
    header_text.pack(padx=10, pady=10)
    header_text.insert('1.0', self.branding_config['email_templates'].get('header_html', ''))
    
    # Footer section
    footer_frame = ttk.LabelFrame(editor_window, text="Email Footer HTML")
    footer_frame.pack(fill='both', expand=True, padx=20, pady=10)
    
    footer_text = tk.Text(footer_frame, height=8, width=70)
    footer_text.pack(padx=10, pady=10)
    footer_text.insert('1.0', self.branding_config['email_templates'].get('footer_html', ''))
    
    # Signature section
    sig_frame = ttk.LabelFrame(editor_window, text="Email Signature")
    sig_frame.pack(fill='x', padx=20, pady=10)
    
    sig_text = tk.Text(sig_frame, height=4, width=70)
    sig_text.pack(padx=10, pady=10)
    sig_text.insert('1.0', self.branding_config['email_templates'].get('signature', ''))
    
    # Action buttons
    action_frame = ttk.Frame(editor_window)
    action_frame.pack(pady=20)
    
    def save_template():
        self.branding_config['email_templates']['header_html'] = header_text.get('1.0', tk.END).strip()
        self.branding_config['email_templates']['footer_html'] = footer_text.get('1.0', tk.END).strip()
        self.branding_config['email_templates']['signature'] = sig_text.get('1.0', tk.END).strip()
        self._save_email_template()
        editor_window.destroy()
    
    ttk.Button(action_frame, text="Preview", command=self._preview_email_template).pack(side='left', padx=5)
    ttk.Button(action_frame, text="Save", command=save_template).pack(side='left', padx=5)
    ttk.Button(action_frame, text="Cancel", command=editor_window.destroy).pack(side='left', padx=5)

def _customize_email_header(self):
    """Customize email header"""
    messagebox.showinfo("Email Header",
                       "Email header customization allows you to:\n\n"
                       "• Add company logo\n"
                       "• Add custom HTML\n"
                       "• Change colors and fonts\n"
                       "• Add branding elements")

def _customize_email_footer(self):
    """Customize email footer"""
    messagebox.showinfo("Email Footer",
                       "Email footer customization allows you to:\n\n"
                       "• Add contact information\n"
                       "• Add social media links\n"
                       "• Add legal disclaimers\n"
                       "• Add unsubscribe links")

def _add_email_signature(self):
    """Add signature to emails"""
    sig_window = tk.Toplevel(self.root)
    sig_window.title("Email Signature")
    sig_window.geometry("500x300")
    
    tk.Label(sig_window, text="Email Signature", font=('Helvetica', 14, 'bold')).pack(pady=10)
    
    sig_text = tk.Text(sig_window, height=10, width=50)
    sig_text.pack(padx=20, pady=10)
    sig_text.insert('1.0', self.branding_config['email_templates'].get('signature', ''))
    
    def save_sig():
        self.branding_config['email_templates']['signature'] = sig_text.get('1.0', tk.END).strip()
        self._save_branding_config()
        messagebox.showinfo("Success", "Email signature saved!")
        sig_window.destroy()
    
    ttk.Button(sig_window, text="Save", command=save_sig).pack(pady=10)

def _preview_email_template(self):
    """Preview email template"""
    preview_window = tk.Toplevel(self.root)
    preview_window.title("Email Preview")
    preview_window.geometry("600x500")
    
    # Create HTML preview
    html_content = f"""
    <html>
    <body>
        {self.branding_config['email_templates'].get('header_html', '')}
        <div style="padding: 20px;">
            <h2>Sample Email Content</h2>
            <p>This is how your email will look with the current template.</p>
        </div>
        {self.branding_config['email_templates'].get('footer_html', '')}
        <div style="padding: 20px; border-top: 1px solid #ccc;">
            <pre>{self.branding_config['email_templates'].get('signature', '')}</pre>
        </div>
    </body>
    </html>
    """
    
    text_widget = tk.Text(preview_window, wrap='word')
    text_widget.pack(fill='both', expand=True, padx=10, pady=10)
    text_widget.insert('1.0', html_content)
    text_widget.config(state='disabled')

def _save_email_template(self):
    """Save email template"""
    try:
        self._save_branding_config()
        messagebox.showinfo("Success", "Email template saved successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save email template: {e}")


# ============================================================================
# SECTION 7: BRANDING PRESETS (5 methods)
# ============================================================================

def _create_branding_presets(self):
    """Create branding presets management interface"""
    presets_window = tk.Toplevel(self.root)
    presets_window.title("Branding Presets")
    presets_window.geometry("600x500")
    
    # Title
    title_label = tk.Label(presets_window, text="Branding Presets",
                          font=('Helvetica', 16, 'bold'))
    title_label.pack(pady=10)
    
    # Presets list
    list_frame = ttk.LabelFrame(presets_window, text="Saved Presets")
    list_frame.pack(fill='both', expand=True, padx=20, pady=10)
    
    presets_listbox = tk.Listbox(list_frame, height=15)
    presets_listbox.pack(fill='both', expand=True, padx=10, pady=10)
    
    # Load presets
    presets_dir = os.path.join(self.data_dir, 'branding_presets')
    if os.path.exists(presets_dir):
        for filename in os.listdir(presets_dir):
            if filename.endswith('.json'):
                presets_listbox.insert(tk.END, filename[:-5])
    
    # Action buttons
    action_frame = ttk.Frame(presets_window)
    action_frame.pack(pady=20)
    
    def load_preset():
        selection = presets_listbox.curselection()
        if selection:
            preset_name = presets_listbox.get(selection[0])
            self._load_branding_preset(preset_name)
    
    def delete_preset():
        selection = presets_listbox.curselection()
        if selection:
            preset_name = presets_listbox.get(selection[0])
            self._delete_branding_preset(preset_name)
            presets_listbox.delete(selection[0])
    
    ttk.Button(action_frame, text="Save Current as Preset",
              command=self._save_branding_preset).pack(side='left', padx=5)
    ttk.Button(action_frame, text="Load Preset",
              command=load_preset).pack(side='left', padx=5)
    ttk.Button(action_frame, text="Delete Preset",
              command=delete_preset).pack(side='left', padx=5)
    ttk.Button(action_frame, text="Share Preset",
              command=self._share_branding_preset).pack(side='left', padx=5)

def _save_branding_preset(self):
    """Save current branding as preset"""
    preset_name = tk.simpledialog.askstring("Save Preset", "Enter preset name:")
    
    if preset_name:
        try:
            presets_dir = os.path.join(self.data_dir, 'branding_presets')
            os.makedirs(presets_dir, exist_ok=True)
            
            preset_file = os.path.join(presets_dir, f"{preset_name}.json")
            with open(preset_file, 'w') as f:
                json.dump(self.branding_config, f, indent=2)
            
            messagebox.showinfo("Success", f"Preset '{preset_name}' saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save preset: {e}")

def _load_branding_preset(self, preset_name):
    """Load saved branding preset"""
    try:
        preset_file = os.path.join(self.data_dir, 'branding_presets', f"{preset_name}.json")
        
        if os.path.exists(preset_file):
            with open(preset_file, 'r') as f:
                self.branding_config = json.load(f)
            
            self._save_branding_config()
            self._apply_branding()
            messagebox.showinfo("Success", f"Preset '{preset_name}' loaded successfully!")
        else:
            messagebox.showerror("Error", f"Preset '{preset_name}' not found!")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load preset: {e}")

def _delete_branding_preset(self, preset_name):
    """Delete branding preset"""
    if messagebox.askyesno("Confirm Delete", f"Delete preset '{preset_name}'?"):
        try:
            preset_file = os.path.join(self.data_dir, 'branding_presets', f"{preset_name}.json")
            if os.path.exists(preset_file):
                os.remove(preset_file)
                messagebox.showinfo("Success", f"Preset '{preset_name}' deleted!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete preset: {e}")

def _share_branding_preset(self):
    """Export preset for sharing"""
    selection = tk.simpledialog.askstring("Share Preset", "Enter preset name to share:")
    
    if selection:
        try:
            preset_file = os.path.join(self.data_dir, 'branding_presets', f"{selection}.json")
            
            if os.path.exists(preset_file):
                dest_file = filedialog.asksaveasfilename(
                    defaultextension=".json",
                    filetypes=[("JSON files", "*.json")],
                    initialfile=f"{selection}_preset.json"
                )
                
                if dest_file:
                    import shutil
                    shutil.copy(preset_file, dest_file)
                    messagebox.showinfo("Success", f"Preset exported to:\n{dest_file}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to share preset: {e}")


# ============================================================================
# SECTION 8: SPLASH SCREEN CUSTOMIZATION (4 methods)
# ============================================================================

def _create_splash_screen_editor(self):
    """Create splash screen customization interface"""
    editor_window = tk.Toplevel(self.root)
    editor_window.title("Splash Screen Editor")
    editor_window.geometry("600x500")
    
    # Title
    title_label = tk.Label(editor_window, text="Splash Screen Customization",
                          font=('Helvetica', 16, 'bold'))
    title_label.pack(pady=10)
    
    # Options
    options_frame = ttk.LabelFrame(editor_window, text="Splash Screen Options")
    options_frame.pack(fill='both', expand=True, padx=20, pady=10)
    
    tk.Label(options_frame, text="Background Color:").pack(pady=5)
    bg_color_btn = tk.Button(options_frame, text="Choose Color", width=20)
    bg_color_btn.pack(pady=5)
    
    tk.Label(options_frame, text="Logo:").pack(pady=5)
    logo_btn = tk.Button(options_frame, text="Upload Logo", width=20)
    logo_btn.pack(pady=5)
    
    tk.Label(options_frame, text="Text:").pack(pady=5)
    text_entry = tk.Entry(options_frame, width=40)
    text_entry.pack(pady=5)
    text_entry.insert(0, "Loading...")
    
    # Action buttons
    action_frame = ttk.Frame(editor_window)
    action_frame.pack(pady=20)
    
    ttk.Button(action_frame, text="Preview",
              command=self._preview_splash_screen).pack(side='left', padx=5)
    ttk.Button(action_frame, text="Apply",
              command=self._apply_splash_screen).pack(side='left', padx=5)
    ttk.Button(action_frame, text="Cancel",
              command=editor_window.destroy).pack(side='left', padx=5)

def _customize_splash_screen(self):
    """Customize splash screen design"""
    self._create_splash_screen_editor()

def _preview_splash_screen(self):
    """Preview splash screen"""
    preview_window = tk.Toplevel(self.root)
    preview_window.title("Splash Screen Preview")
    preview_window.geometry("400x300")
    preview_window.configure(bg='#1e3a8a')
    
    # Company name
    company_name = self.branding_config['company_info'].get('name', 'Deep Blue Pool Chemistry')
    tk.Label(preview_window, text=company_name,
            font=('Helvetica', 20, 'bold'),
            bg='#1e3a8a', fg='white').pack(pady=50)
    
    # Loading text
    tk.Label(preview_window, text="Loading...",
            font=('Helvetica', 12),
            bg='#1e3a8a', fg='white').pack(pady=20)

def _apply_splash_screen(self):
    """Apply custom splash screen"""
    messagebox.showinfo("Success", "Splash screen customization will be applied on next startup!")

def _update_branding_preview(self, preview_frame):
    """Update branding preview display"""
    # Clear existing widgets
    for widget in preview_frame.winfo_children():
        widget.destroy()
    
    # Company info
    company_name = self.branding_config['company_info'].get('name', 'Not Set')
    tk.Label(preview_frame, text=f"Company: {company_name}",
            font=('Helvetica', 12, 'bold')).pack(anchor='w', padx=10, pady=5)
    
    # Colors
    colors_frame = ttk.Frame(preview_frame)
    colors_frame.pack(fill='x', padx=10, pady=5)
    
    tk.Label(colors_frame, text="Primary:").pack(side='left')
    primary_color = self.branding_config['colors'].get('primary', '#1e3a8a')
    tk.Label(colors_frame, bg=primary_color, width=5, relief='solid', borderwidth=1).pack(side='left', padx=5)
    
    tk.Label(colors_frame, text="Secondary:").pack(side='left', padx=(10, 0))
    secondary_color = self.branding_config['colors'].get('secondary', '#93c5fd')
    tk.Label(colors_frame, bg=secondary_color, width=5, relief='solid', borderwidth=1).pack(side='left', padx=5)
    
    # Logo
    logo_path = self.branding_config['logos'].get('primary', '')
    logo_status = "Set" if logo_path and os.path.exists(logo_path) else "Not Set"
    tk.Label(preview_frame, text=f"Primary Logo: {logo_status}",
            font=('Helvetica', 10)).pack(anchor='w', padx=10, pady=5)




    # ============================================================================
    # PHASE 2.4: PDF REPORT BRANDING INTEGRATION (27 methods)
    # ============================================================================

def _get_branding_colors(self):
    """Get color scheme from branding configuration"""
    try:
        if not hasattr(self, 'branding_config'):
            self.branding_config = self._load_branding_config()
        
        color_config = self.branding_config.get('colors', {})
        
        # Convert hex colors to ReportLab colors
        def hex_to_reportlab_color(hex_color):
            """Convert hex color to ReportLab Color object"""
            hex_color = hex_color.lstrip('#')
            r = int(hex_color[0:2], 16) / 255.0
            g = int(hex_color[2:4], 16) / 255.0
            b = int(hex_color[4:6], 16) / 255.0
            return colors.Color(r, g, b)
        
        branding_colors = {
            'primary': hex_to_reportlab_color(color_config.get('primary', '#1e3a8a')),
            'secondary': hex_to_reportlab_color(color_config.get('secondary', '#93c5fd')),
            'accent': hex_to_reportlab_color(color_config.get('accent', '#3b82f6')),
            'text': hex_to_reportlab_color(color_config.get('text', '#1f2937')),
            'background': hex_to_reportlab_color(color_config.get('background', '#ffffff')),
            'success': hex_to_reportlab_color(color_config.get('success', '#10b981')),
            'warning': hex_to_reportlab_color(color_config.get('warning', '#f59e0b')),
            'error': hex_to_reportlab_color(color_config.get('error', '#ef4444'))
        }
        
        return branding_colors
        
    except Exception as e:
        print(f"Error getting branding colors: {e}")
        # Return default colors
        return {
            'primary': colors.HexColor('#1e3a8a'),
            'secondary': colors.HexColor('#93c5fd'),
            'accent': colors.HexColor('#3b82f6'),
            'text': colors.HexColor('#1f2937'),
            'background': colors.white,
            'success': colors.HexColor('#10b981'),
            'warning': colors.HexColor('#f59e0b'),
            'error': colors.HexColor('#ef4444')
        }

def _apply_colors_to_pdf_styles(self, styles):
    """Apply branding colors to ReportLab styles"""
    try:
        brand_colors = self._get_branding_colors()
        
        # Update Heading1 style
        if 'Heading1' in styles:
            styles['Heading1'].textColor = brand_colors['primary']
        
        # Update Heading2 style
        if 'Heading2' in styles:
            styles['Heading2'].textColor = brand_colors['primary']
        
        # Update Heading3 style
        if 'Heading3' in styles:
            styles['Heading3'].textColor = brand_colors['accent']
        
        # Update Normal style
        if 'Normal' in styles:
            styles['Normal'].textColor = brand_colors['text']
        
        return styles
        
    except Exception as e:
        print(f"Error applying colors to styles: {e}")
        return styles

def _create_branded_table_style(self):
    """Create table style with branding colors"""
    try:
        brand_colors = self._get_branding_colors()
        
        table_style = TableStyle([
            # Header row
            ('BACKGROUND', (0, 0), (-1, 0), brand_colors['primary']),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            
            # Data rows
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, -1), brand_colors['text']),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('TOPPADDING', (0, 1), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
            
            # Alternating row colors
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, brand_colors['secondary']]),
            
            # Grid
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ])
        
        return table_style
        
    except Exception as e:
        print(f"Error creating branded table style: {e}")
        # Return default style
        return TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ])

def _get_color_for_severity(self, severity):
    """Get color for alert severity level"""
    try:
        brand_colors = self._get_branding_colors()
        
        severity_colors = {
            'critical': brand_colors['error'],
            'warning': brand_colors['warning'],
            'info': brand_colors['accent'],
            'success': brand_colors['success']
        }
        
        return severity_colors.get(severity.lower(), brand_colors['text'])
        
    except Exception as e:
        print(f"Error getting severity color: {e}")
        return colors.black

def _create_colored_section_header(self, text, level=1):
    """Create colored section header with branding"""
    try:
        brand_colors = self._get_branding_colors()
        styles = getSampleStyleSheet()
        
        if level == 1:
            style = ParagraphStyle(
                'BrandedHeading1',
                parent=styles['Heading1'],
                textColor=brand_colors['primary'],
                fontSize=18,
                spaceAfter=12,
                fontName='Helvetica-Bold'
            )
        elif level == 2:
            style = ParagraphStyle(
                'BrandedHeading2',
                parent=styles['Heading2'],
                textColor=brand_colors['primary'],
                fontSize=14,
                spaceAfter=10,
                fontName='Helvetica-Bold'
            )
        else:
            style = ParagraphStyle(
                'BrandedHeading3',
                parent=styles['Heading3'],
                textColor=brand_colors['accent'],
                fontSize=12,
                spaceAfter=8,
                fontName='Helvetica-Bold'
            )
        
        return Paragraph(text, style)
        
    except Exception as e:
        print(f"Error creating colored section header: {e}")
        styles = getSampleStyleSheet()
        return Paragraph(text, styles['Heading1'])

def _apply_custom_template_to_pdf(self, doc):
    """Apply custom template settings to PDF document"""
    try:
        if not hasattr(self, 'branding_config'):
            self.branding_config = self._load_branding_config()
        
        template_config = self.branding_config.get('report_templates', {})
        
        # Apply custom margins
        margin_top = template_config.get('margin_top', 1.0) * inch
        margin_bottom = template_config.get('margin_bottom', 1.0) * inch
        margin_left = template_config.get('margin_left', 0.75) * inch
        margin_right = template_config.get('margin_right', 0.75) * inch
        
        doc.topMargin = margin_top
        doc.bottomMargin = margin_bottom
        doc.leftMargin = margin_left
        doc.rightMargin = margin_right
        
        return doc
        
    except Exception as e:
        print(f"Error applying custom template: {e}")
        return doc

def _create_custom_header(self, canvas, doc):
    """Create custom header with branding"""
    try:
        if not hasattr(self, 'branding_config'):
            self.branding_config = self._load_branding_config()
        
        brand_colors = self._get_branding_colors()
        company_info = self.branding_config.get('company_info', {})
        template_config = self.branding_config.get('report_templates', {})
        
        # Save canvas state
        canvas.saveState()
        
        # Get header height
        header_height = template_config.get('header_height', 1.5) * inch
        
        # Draw header background
        canvas.setFillColor(brand_colors['primary'])
        canvas.rect(0, letter[1] - header_height, letter[0], header_height, fill=1, stroke=0)
        
        # Add logo if available
        logo_path = self.branding_config.get('logos', {}).get('primary', '')
        if logo_path and os.path.exists(logo_path):
            try:
                logo_width = 1.0 * inch
                logo_height = 1.0 * inch
                x_pos = 0.5 * inch
                y_pos = letter[1] - header_height + 0.25 * inch
                canvas.drawImage(logo_path, x_pos, y_pos, 
                               width=logo_width, height=logo_height, 
                               preserveAspectRatio=True, mask='auto')
            except:
                pass
        
        # Add company name
        canvas.setFillColor(colors.white)
        canvas.setFont('Helvetica-Bold', 16)
        company_name = company_info.get('name', 'Pool Chemistry Report')
        canvas.drawString(2.0 * inch, letter[1] - 0.6 * inch, company_name)
        
        # Add tagline
        canvas.setFont('Helvetica', 10)
        tagline = company_info.get('tagline', '')
        if tagline:
            canvas.drawString(2.0 * inch, letter[1] - 0.9 * inch, tagline)
        
        # Restore canvas state
        canvas.restoreState()
        
    except Exception as e:
        print(f"Error creating custom header: {e}")

def _create_custom_footer(self, canvas, doc):
    """Create custom footer with branding"""
    try:
        if not hasattr(self, 'branding_config'):
            self.branding_config = self._load_branding_config()
        
        brand_colors = self._get_branding_colors()
        company_info = self.branding_config.get('company_info', {})
        template_config = self.branding_config.get('report_templates', {})
        
        # Save canvas state
        canvas.saveState()
        
        # Get footer height
        footer_height = template_config.get('footer_height', 0.75) * inch
        
        # Draw footer background
        canvas.setFillColor(brand_colors['secondary'])
        canvas.rect(0, 0, letter[0], footer_height, fill=1, stroke=0)
        
        # Add page number
        canvas.setFillColor(brand_colors['text'])
        canvas.setFont('Helvetica', 9)
        page_num = canvas.getPageNumber()
        canvas.drawRightString(letter[0] - 0.5 * inch, 0.3 * inch, f"Page {page_num}")
        
        # Add company contact info
        contact_parts = []
        if company_info.get('phone'):
            contact_parts.append(f"Phone: {company_info['phone']}")
        if company_info.get('email'):
            contact_parts.append(f"Email: {company_info['email']}")
        if company_info.get('website'):
            contact_parts.append(company_info['website'])
        
        if contact_parts:
            contact_text = " | ".join(contact_parts)
            canvas.drawString(0.5 * inch, 0.3 * inch, contact_text)
        
        # Restore canvas state
        canvas.restoreState()
        
    except Exception as e:
        print(f"Error creating custom footer: {e}")

def _apply_custom_margins(self, doc):
    """Apply custom margin settings"""
    try:
        if not hasattr(self, 'branding_config'):
            self.branding_config = self._load_branding_config()
        
        template_config = self.branding_config.get('report_templates', {})
        
        doc.topMargin = template_config.get('margin_top', 1.0) * inch
        doc.bottomMargin = template_config.get('margin_bottom', 1.0) * inch
        doc.leftMargin = template_config.get('margin_left', 0.75) * inch
        doc.rightMargin = template_config.get('margin_right', 0.75) * inch
        
        return doc
        
    except Exception as e:
        print(f"Error applying custom margins: {e}")
        return doc

def _add_watermark_to_page(self, canvas, doc):
    """Add watermark to page if enabled"""
    try:
        if not hasattr(self, 'branding_config'):
            self.branding_config = self._load_branding_config()
        
        template_config = self.branding_config.get('report_templates', {})
        
        if not template_config.get('show_watermark', False):
            return
        
        watermark_path = self.branding_config.get('logos', {}).get('watermark', '')
        if not watermark_path or not os.path.exists(watermark_path):
            return
        
        # Save canvas state
        canvas.saveState()
        
        # Set opacity
        opacity = template_config.get('watermark_opacity', 0.1)
        canvas.setFillAlpha(opacity)
        
        # Draw watermark in center
        page_width, page_height = letter
        watermark_size = 4 * inch
        x_pos = (page_width - watermark_size) / 2
        y_pos = (page_height - watermark_size) / 2
        
        canvas.drawImage(watermark_path, x_pos, y_pos,
                        width=watermark_size, height=watermark_size,
                        preserveAspectRatio=True, mask='auto')
        
        # Restore canvas state
        canvas.restoreState()
        
    except Exception as e:
        print(f"Error adding watermark: {e}")

def _create_branded_cover_page(self, story):
    """Create custom branded cover page"""
    try:
        if not hasattr(self, 'branding_config'):
            self.branding_config = self._load_branding_config()
        
        brand_colors = self._get_branding_colors()
        company_info = self.branding_config.get('company_info', {})
        styles = getSampleStyleSheet()
        
        # Add logo
        logo_path = self.branding_config.get('logos', {}).get('primary', '')
        if logo_path and os.path.exists(logo_path):
            try:
                img = Image(logo_path, width=3*inch, height=3*inch)
                story.append(img)
                story.append(Spacer(1, 0.5*inch))
            except:
                pass
        
        # Company name
        company_style = ParagraphStyle(
            'CompanyName',
            parent=styles['Title'],
            fontSize=32,
            textColor=brand_colors['primary'],
            alignment=1,
            spaceAfter=12
        )
        company_name = company_info.get('name', 'Pool Chemistry Report')
        story.append(Paragraph(company_name, company_style))
        
        # Tagline
        if company_info.get('tagline'):
            tagline_style = ParagraphStyle(
                'Tagline',
                parent=styles['Normal'],
                fontSize=16,
                textColor=brand_colors['accent'],
                alignment=1,
                spaceAfter=30
            )
            story.append(Paragraph(company_info['tagline'], tagline_style))
        
        story.append(Spacer(1, 1*inch))
        
        # Report title
        title_style = ParagraphStyle(
            'ReportTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=brand_colors['primary'],
            alignment=1,
            spaceAfter=30
        )
        story.append(Paragraph("Pool Chemistry Report", title_style))
        
        story.append(PageBreak())
        
        return story
        
    except Exception as e:
        print(f"Error creating branded cover page: {e}")
        return story

def _add_company_header_to_pdf(self, story):
    """Add company information to PDF header"""
    try:
        if not hasattr(self, 'branding_config'):
            self.branding_config = self._load_branding_config()
        
        company_info = self.branding_config.get('company_info', {})
        brand_colors = self._get_branding_colors()
        styles = getSampleStyleSheet()
        
        # Company name
        if company_info.get('name'):
            name_style = ParagraphStyle(
                'CompanyHeader',
                parent=styles['Heading1'],
                fontSize=20,
                textColor=brand_colors['primary'],
                spaceAfter=6
            )
            story.append(Paragraph(company_info['name'], name_style))
        
        # Tagline
        if company_info.get('tagline'):
            tagline_style = ParagraphStyle(
                'CompanyTagline',
                parent=styles['Normal'],
                fontSize=12,
                textColor=brand_colors['accent'],
                fontName='Helvetica-Oblique',
                spaceAfter=12
            )
            story.append(Paragraph(company_info['tagline'], tagline_style))
        
        story.append(Spacer(1, 0.2*inch))
        
        return story
        
    except Exception as e:
        print(f"Error adding company header: {e}")
        return story

def _add_company_footer_to_pdf(self, story):
    """Add company information to PDF footer"""
    try:
        if not hasattr(self, 'branding_config'):
            self.branding_config = self._load_branding_config()
        
        company_info = self.branding_config.get('company_info', {})
        styles = getSampleStyleSheet()
        
        contact_info = self._format_company_contact_info()
        if contact_info:
            footer_style = ParagraphStyle(
                'CompanyFooter',
                parent=styles['Normal'],
                fontSize=9,
                alignment=1,
                spaceAfter=12
            )
            story.append(Spacer(1, 0.3*inch))
            story.append(Paragraph(contact_info, footer_style))
        
        return story
        
    except Exception as e:
        print(f"Error adding company footer: {e}")
        return story

def _format_company_contact_info(self):
    """Format company contact information"""
    try:
        if not hasattr(self, 'branding_config'):
            self.branding_config = self._load_branding_config()
        
        company_info = self.branding_config.get('company_info', {})
        
        contact_parts = []
        
        if company_info.get('address'):
            contact_parts.append(company_info['address'])
        
        if company_info.get('phone'):
            contact_parts.append(f"Phone: {company_info['phone']}")
        
        if company_info.get('email'):
            contact_parts.append(f"Email: {company_info['email']}")
        
        if company_info.get('website'):
            contact_parts.append(f"Website: {company_info['website']}")
        
        return " | ".join(contact_parts)
        
    except Exception as e:
        print(f"Error formatting company contact info: {e}")
        return ""

def _create_company_letterhead(self, story):
    """Create full company letterhead style"""
    try:
        if not hasattr(self, 'branding_config'):
            self.branding_config = self._load_branding_config()
        
        brand_colors = self._get_branding_colors()
        company_info = self.branding_config.get('company_info', {})
        styles = getSampleStyleSheet()
        
        # Logo
        logo_path = self.branding_config.get('logos', {}).get('primary', '')
        if logo_path and os.path.exists(logo_path):
            try:
                img = Image(logo_path, width=2*inch, height=2*inch)
                story.append(img)
                story.append(Spacer(1, 0.2*inch))
            except:
                pass
        
        # Company name
        if company_info.get('name'):
            name_style = ParagraphStyle(
                'LetterheadName',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=brand_colors['primary'],
                alignment=1,
                spaceAfter=6
            )
            story.append(Paragraph(company_info['name'], name_style))
        
        # Tagline
        if company_info.get('tagline'):
            tagline_style = ParagraphStyle(
                'LetterheadTagline',
                parent=styles['Normal'],
                fontSize=14,
                textColor=brand_colors['accent'],
                alignment=1,
                fontName='Helvetica-Oblique',
                spaceAfter=12
            )
            story.append(Paragraph(company_info['tagline'], tagline_style))
        
        # Contact info
        contact_info = self._format_company_contact_info()
        if contact_info:
            contact_style = ParagraphStyle(
                'LetterheadContact',
                parent=styles['Normal'],
                fontSize=10,
                alignment=1,
                spaceAfter=20
            )
            story.append(Paragraph(contact_info, contact_style))
        
        # Horizontal line
        from reportlab.platypus import HRFlowable
        story.append(HRFlowable(width="100%", thickness=2, 
                               color=brand_colors['primary'], 
                               spaceAfter=20))
        
        return story
        
    except Exception as e:
        print(f"Error creating company letterhead: {e}")
        return story


# ============================================================================
# SECTION 4: LOGO INTEGRATION ENHANCEMENT (4 methods)
# ============================================================================

def _get_logo_for_report(self, logo_type='primary'):
    """Get appropriate logo for report"""
    try:
        if not hasattr(self, 'branding_config'):
            self.branding_config = self._load_branding_config()
        
        logos = self.branding_config.get('logos', {})
        logo_path = logos.get(logo_type, '')
        
        if logo_path and os.path.exists(logo_path):
            return logo_path
        
        # Fallback to primary logo
        if logo_type != 'primary':
            primary_logo = logos.get('primary', '')
            if primary_logo and os.path.exists(primary_logo):
                return primary_logo
        
        return None
        
    except Exception as e:
        print(f"Error getting logo for report: {e}")
        return None

def _resize_logo_for_pdf(self, logo_path, max_width=2.0, max_height=2.0):
    """Resize logo for PDF with proper aspect ratio"""
    try:
        if not logo_path or not os.path.exists(logo_path):
            return None
        
        img = PILImage.open(logo_path)
        width, height = img.size
        
        # Calculate aspect ratio
        aspect = width / height
        
        # Convert max dimensions to pixels (assuming 72 DPI)
        max_width_px = max_width * 72
        max_height_px = max_height * 72
        
        # Calculate new dimensions
        if width > max_width_px or height > max_height_px:
            if aspect > 1:  # Wider than tall
                new_width = max_width_px
                new_height = new_width / aspect
            else:  # Taller than wide
                new_height = max_height_px
                new_width = new_height * aspect
        else:
            new_width = width
            new_height = height
        
        return (new_width / 72, new_height / 72)  # Convert back to inches
        
    except Exception as e:
        print(f"Error resizing logo: {e}")
        return (max_width, max_height)

def _position_logo_in_header(self, canvas, doc, logo_path):
    """Position logo in header with proper sizing"""
    try:
        if not logo_path or not os.path.exists(logo_path):
            return
        
        # Get logo dimensions
        logo_dims = self._resize_logo_for_pdf(logo_path, max_width=1.5, max_height=1.5)
        if not logo_dims:
            return
        
        logo_width, logo_height = logo_dims
        
        # Position in top-left corner
        x_pos = 0.5 * inch
        y_pos = letter[1] - 0.5 * inch - logo_height * inch
        
        canvas.drawImage(logo_path, x_pos, y_pos,
                        width=logo_width * inch, height=logo_height * inch,
                        preserveAspectRatio=True, mask='auto')
        
    except Exception as e:
        print(f"Error positioning logo in header: {e}")

def _add_watermark_logo(self, canvas, doc):
    """Add logo as watermark"""
    try:
        if not hasattr(self, 'branding_config'):
            self.branding_config = self._load_branding_config()
        
        template_config = self.branding_config.get('report_templates', {})
        
        if not template_config.get('show_watermark', False):
            return
        
        watermark_path = self._get_logo_for_report('watermark')
        if not watermark_path:
            watermark_path = self._get_logo_for_report('primary')
        
        if not watermark_path:
            return
        
        # Save canvas state
        canvas.saveState()
        
        # Set opacity
        opacity = template_config.get('watermark_opacity', 0.1)
        canvas.setFillAlpha(opacity)
        
        # Draw watermark in center
        page_width, page_height = letter
        watermark_size = 4 * inch
        x_pos = (page_width - watermark_size) / 2
        y_pos = (page_height - watermark_size) / 2
        
        canvas.drawImage(watermark_path, x_pos, y_pos,
                        width=watermark_size, height=watermark_size,
                        preserveAspectRatio=True, mask='auto')
        
        # Restore canvas state
        canvas.restoreState()
        
    except Exception as e:
        print(f"Error adding watermark logo: {e}")


# ============================================================================
# SECTION 5: FONT INTEGRATION (3 methods)
# ============================================================================

def _get_branding_fonts(self):
    """Get font settings from branding configuration"""
    try:
        if not hasattr(self, 'branding_config'):
            self.branding_config = self._load_branding_config()
        
        fonts = self.branding_config.get('fonts', {})
        
        return {
            'heading': fonts.get('heading', 'Helvetica-Bold'),
            'body': fonts.get('body', 'Helvetica'),
            'monospace': fonts.get('monospace', 'Courier')
        }
        
    except Exception as e:
        print(f"Error getting branding fonts: {e}")
        return {
            'heading': 'Helvetica-Bold',
            'body': 'Helvetica',
            'monospace': 'Courier'
        }

def _apply_fonts_to_styles(self, styles):
    """Apply branding fonts to ReportLab styles"""
    try:
        brand_fonts = self._get_branding_fonts()
        
        # Update heading styles
        for heading in ['Heading1', 'Heading2', 'Heading3', 'Title']:
            if heading in styles:
                styles[heading].fontName = brand_fonts['heading']
        
        # Update body styles
        for body_style in ['Normal', 'BodyText', 'Italic']:
            if body_style in styles:
                styles[body_style].fontName = brand_fonts['body']
        
        # Update code style
        if 'Code' in styles:
            styles['Code'].fontName = brand_fonts['monospace']
        
        return styles
        
    except Exception as e:
        print(f"Error applying fonts to styles: {e}")
        return styles

def _register_custom_fonts(self):
    """Register custom fonts if provided"""
    try:
        # This would register custom TTF fonts if provided
        # For now, we use built-in ReportLab fonts
        pass
        
    except Exception as e:
        print(f"Error registering custom fonts: {e}")


# ============================================================================
# SECTION 6: REPORT STYLE ENHANCEMENT (5 methods)
# ============================================================================

def _create_branded_paragraph_style(self, name='BrandedNormal'):
    """Create branded paragraph style"""
    try:
        brand_colors = self._get_branding_colors()
        brand_fonts = self._get_branding_fonts()
        styles = getSampleStyleSheet()
        
        branded_style = ParagraphStyle(
            name,
            parent=styles['Normal'],
            fontName=brand_fonts['body'],
            fontSize=10,
            textColor=brand_colors['text'],
            spaceAfter=12,
            leading=14
        )
        
        return branded_style
        
    except Exception as e:
        print(f"Error creating branded paragraph style: {e}")
        return getSampleStyleSheet()['Normal']

def _create_branded_heading_style(self, level=1):
    """Create branded heading style"""
    try:
        brand_colors = self._get_branding_colors()
        brand_fonts = self._get_branding_fonts()
        styles = getSampleStyleSheet()
        
        if level == 1:
            parent = styles['Heading1']
            font_size = 18
            color = brand_colors['primary']
        elif level == 2:
            parent = styles['Heading2']
            font_size = 14
            color = brand_colors['primary']
        else:
            parent = styles['Heading3']
            font_size = 12
            color = brand_colors['accent']
        
        branded_style = ParagraphStyle(
            f'BrandedHeading{level}',
            parent=parent,
            fontName=brand_fonts['heading'],
            fontSize=font_size,
            textColor=color,
            spaceAfter=12,
            spaceBefore=12
        )
        
        return branded_style
        
    except Exception as e:
        print(f"Error creating branded heading style: {e}")
        return getSampleStyleSheet()['Heading1']

def _create_branded_list_style(self):
    """Create branded list style"""
    try:
        brand_colors = self._get_branding_colors()
        brand_fonts = self._get_branding_fonts()
        styles = getSampleStyleSheet()
        
        branded_style = ParagraphStyle(
            'BrandedList',
            parent=styles['Normal'],
            fontName=brand_fonts['body'],
            fontSize=10,
            textColor=brand_colors['text'],
            leftIndent=20,
            bulletIndent=10,
            spaceAfter=6
        )
        
        return branded_style
        
    except Exception as e:
        print(f"Error creating branded list style: {e}")
        return getSampleStyleSheet()['Normal']

def _create_branded_chart_style(self):
    """Create branded chart style settings"""
    try:
        brand_colors = self._get_branding_colors()
        
        chart_colors = [
            brand_colors['primary'],
            brand_colors['accent'],
            brand_colors['secondary'],
            brand_colors['success'],
            brand_colors['warning']
        ]
        
        return {
            'colors': chart_colors,
            'grid_color': brand_colors['text'],
            'text_color': brand_colors['text']
        }
        
    except Exception as e:
        print(f"Error creating branded chart style: {e}")
        return {
            'colors': [colors.blue, colors.green, colors.red],
            'grid_color': colors.black,
            'text_color': colors.black
        }

def _apply_branding_to_all_styles(self):
    """Apply branding to all ReportLab styles"""
    try:
        styles = getSampleStyleSheet()
        
        # Apply colors
        styles = self._apply_colors_to_pdf_styles(styles)
        
        # Apply fonts
        styles = self._apply_fonts_to_styles(styles)
        
        return styles
        
    except Exception as e:
        print(f"Error applying branding to all styles: {e}")
        return getSampleStyleSheet()


def main():
    """Main entry point for the application"""
    app = PoolApp()
    app.mainloop()

# Entry point

if __name__ == "__main__":
    main()
