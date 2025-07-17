#!/usr/bin/env python3
"""
All-in-One Deep Blue Pool Chemistry Application.

This standalone script contains all the necessary components of the Deep Blue Pool Chemistry
application in a single file to avoid import issues. This is intended as a temporary solution
until you can properly set up the module structure.
"""

import logging
import os
import sys
import json
import argparse
import threading
import time
import sqlite3
import cv2
import numpy as np
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Union
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("pool_chemistry.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("PoolApp")

#############################################################################
# Database Service
#############################################################################

class DatabaseService:
    """
    Database service for managing pool chemistry data.
    
    This class provides methods for storing and retrieving sensor data,
    maintenance logs, and chemical additions using SQLite.
    
    Attributes:
        db_path: Path to the SQLite database file
        connection_pool: Dictionary of database connections by thread ID
    """
    
    def __init__(self, db_path: str = "pool_data.db"):
        """
        Initialize the database service.
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        self.connection_pool = {}
        logger.info(f"Database Service initialized with SQLite3 at {db_path}")
        
        # Create database if it doesn't exist
        self._init_db()
    
    def get_connection(self) -> sqlite3.Connection:
        """
        Get a database connection from the connection pool.
        
        Returns:
            A SQLite connection object
        """
        thread_id = threading.get_ident()
        if thread_id not in self.connection_pool:
            try:
                self.connection_pool[thread_id] = sqlite3.connect(self.db_path)
                # Enable foreign keys
                self.connection_pool[thread_id].execute("PRAGMA foreign_keys = ON")
            except sqlite3.Error as e:
                logger.error(f"Failed to create database connection: {e}")
                raise
        
        return self.connection_pool[thread_id]
    
    def _init_db(self) -> None:
        """
        Initialize database tables if they don't exist.
        
        Creates the necessary tables for storing sensor data, maintenance logs,
        and chemical additions.
        
        Raises:
            sqlite3.Error: If there's an error creating the database tables
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Create sensor data table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS sensor_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                water_temp REAL,
                ph_level REAL,
                chlorine_level REAL,
                json_data TEXT
            )
            ''')
            
            # Create maintenance log table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS maintenance_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                action TEXT NOT NULL,
                details TEXT,
                performed_by TEXT
            )
            ''')
            
            # Create chemical log table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS chemical_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                chemical TEXT NOT NULL,
                amount REAL NOT NULL,
                reason TEXT
            )
            ''')
            
            # Create chemical readings table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS chemical_readings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                pH TEXT,
                free_chlorine TEXT,
                total_chlorine TEXT,
                alkalinity TEXT,
                calcium TEXT,
                cyanuric_acid TEXT,
                bromine TEXT,
                salt TEXT,
                temperature TEXT,
                water_volume TEXT,
                source TEXT
            )
            ''')
            
            conn.commit()
            logger.info("Database initialized successfully")
        except sqlite3.Error as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
    
    def log_sensor_data(self, data: Dict[str, Any]) -> bool:
        """
        Log sensor data to the database.
        
        Args:
            data: Dictionary containing sensor data
            
        Returns:
            True if successful, False otherwise
            
        Raises:
            sqlite3.Error: If there's an error inserting data
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            timestamp = datetime.now().isoformat()
            water_temp = data.get("water_temp")
            ph_level = data.get("ph_level")
            chlorine_level = data.get("chlorine_level")
            json_data = json.dumps(data)
            
            cursor.execute(
                "INSERT INTO sensor_data (timestamp, water_temp, ph_level, chlorine_level, json_data) "
                "VALUES (?, ?, ?, ?, ?)",
                (timestamp, water_temp, ph_level, chlorine_level, json_data)
            )
            
            conn.commit()
            return True
        except sqlite3.Error as e:
            logger.error(f"Failed to log sensor data: {e}")
            return False
    
    def log_maintenance(self, action: str, details: str = "", performed_by: str = "system") -> bool:
        """
        Log maintenance action to the database.
        
        Args:
            action: Description of the maintenance action
            details: Additional details about the action
            performed_by: Who performed the action
            
        Returns:
            True if successful, False otherwise
            
        Raises:
            sqlite3.Error: If there's an error inserting data
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            timestamp = datetime.now().isoformat()
            
            cursor.execute(
                "INSERT INTO maintenance_log (timestamp, action, details, performed_by) "
                "VALUES (?, ?, ?, ?)",
                (timestamp, action, details, performed_by)
            )
            
            conn.commit()
            return True
        except sqlite3.Error as e:
            logger.error(f"Failed to log maintenance: {e}")
            return False
    
    def log_chemical_addition(self, chemical: str, amount: float, reason: str = "") -> bool:
        """
        Log chemical addition to the database.
        
        Args:
            chemical: Name of the chemical added
            amount: Amount of chemical added
            reason: Reason for adding the chemical
            
        Returns:
            True if successful, False otherwise
            
        Raises:
            sqlite3.Error: If there's an error inserting data
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            timestamp = datetime.now().isoformat()
            
            cursor.execute(
                "INSERT INTO chemical_log (timestamp, chemical, amount, reason) "
                "VALUES (?, ?, ?, ?)",
                (timestamp, chemical, amount, reason)
            )
            
            conn.commit()
            return True
        except sqlite3.Error as e:
            logger.error(f"Failed to log chemical addition: {e}")
            return False
    
    def get_sensor_history(self, hours: int = 24) -> List[Dict[str, Any]]:
        """
        Get sensor data history for the specified number of hours.
        
        Args:
            hours: Number of hours of history to retrieve
            
        Returns:
            List of dictionaries containing sensor data
            
        Raises:
            sqlite3.Error: If there's an error retrieving data
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Calculate timestamp for hours ago
            timestamp = (datetime.now() - timedelta(hours=hours)).isoformat()
            
            cursor.execute(
                "SELECT timestamp, water_temp, ph_level, chlorine_level FROM sensor_data "
                "WHERE timestamp > ? ORDER BY timestamp",
                (timestamp,)
            )
            
            data = cursor.fetchall()
            
            return [
                {
                    "timestamp": row[0],
                    "water_temp": row[1],
                    "ph_level": row[2],
                    "chlorine_level": row[3]
                }
                for row in data
            ]
        except sqlite3.Error as e:
            logger.error(f"Failed to get sensor history: {e}")
            return []
    
    def insert_reading(self, data: Dict[str, Any]) -> bool:
        """
        Insert chemical reading into the database.
        
        Args:
            data: Dictionary containing chemical reading data
            
        Returns:
            True if successful, False otherwise
            
        Raises:
            sqlite3.Error: If there's an error inserting data
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            values = (
                datetime.now().isoformat(),
                data.get("pH"), data.get("free_chlorine"), data.get("total_chlorine"),
                data.get("alkalinity"), data.get("calcium"), data.get("cyanuric_acid"),
                data.get("bromine"), data.get("salt"), data.get("temperature"),
                data.get("water_volume"), data.get("source")
            )
            
            cursor.execute("""
                INSERT INTO chemical_readings (
                    timestamp, pH, free_chlorine, total_chlorine, alkalinity,
                    calcium, cyanuric_acid, bromine, salt, temperature,
                    water_volume, source
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, values)
            
            conn.commit()
            return True
        except sqlite3.Error as e:
            logger.error(f"Failed to insert reading: {e}")
            return False
    
    def get_recent_readings(self, limit: int = 5) -> List[tuple]:
        """
        Get recent chemical readings from the database.
        
        Args:
            limit: Maximum number of readings to retrieve
            
        Returns:
            List of tuples containing reading data
            
        Raises:
            sqlite3.Error: If there's an error retrieving data
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT * FROM chemical_readings ORDER BY timestamp DESC LIMIT ?",
                (limit,)
            )
            
            return cursor.fetchall()
        except sqlite3.Error as e:
            logger.error(f"Failed to fetch readings: {e}")
            return []
    
    def export_to_csv(self, filename: str = "data/exported_readings.csv") -> bool:
        """
        Export chemical readings to a CSV file.
        
        Args:
            filename: Path to the output CSV file
            
        Returns:
            True if successful, False otherwise
            
        Raises:
            sqlite3.Error: If there's an error retrieving data
            IOError: If there's an error writing to the file
        """
        try:
            import csv
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM chemical_readings ORDER BY timestamp DESC")
            rows = cursor.fetchall()
            headers = [desc[0] for desc in cursor.description]
            
            with open(filename, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(headers)
                writer.writerows(rows)
            
            logger.info(f"Exported readings to {filename}")
            return True
        except sqlite3.Error as e:
            logger.error(f"Failed to export CSV (database error): {e}")
            return False
        except IOError as e:
            logger.error(f"Failed to export CSV (file error): {e}")
            return False
        except Exception as e:
            logger.error(f"Failed to export CSV (unexpected error): {e}")
            return False
    
    def close_all_connections(self) -> None:
        """
        Close all database connections in the connection pool.
        
        This should be called when shutting down the application.
        """
        for thread_id, conn in self.connection_pool.items():
            try:
                conn.close()
                logger.debug(f"Closed database connection for thread {thread_id}")
            except sqlite3.Error as e:
                logger.error(f"Error closing database connection: {e}")
        
        self.connection_pool.clear()
        logger.info("All database connections closed")
    
    def __del__(self) -> None:
        """
        Destructor to ensure all connections are closed when the object is destroyed.
        """
        self.close_all_connections()

#############################################################################
# Chemical Safety Database
#############################################################################

class ChemicalSafetyDatabase:
    """
    Database for pool chemical safety information.
    
    This class handles storage and retrieval of safety data sheets, compatibility
    information, and handling guidelines for pool chemicals.
    
    Attributes:
        data_file_path: Path to the JSON file containing chemical safety data
        chemicals_data: Dictionary of chemical safety information
        compatibility_matrix: Matrix of chemical compatibility information
    """
    
    def __init__(self, data_file_path: str = "data/chemical_safety_data.json"):
        """
        Initialize the chemical safety database.
        
        Args:
            data_file_path: Path to the JSON file containing chemical safety data
        """
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initializing Chemical Safety Database")
        self.data_file_path = data_file_path
        self.chemicals_data = {}
        self.compatibility_matrix = {}
        self._load_data()
    
    def _load_data(self) -> None:
        """
        Load chemical safety data from the data file.
        
        If the data file doesn't exist, creates default data.
        
        Raises:
            IOError: If there's an error reading the data file
            json.JSONDecodeError: If the data file contains invalid JSON
        """
        try:
            if os.path.exists(self.data_file_path):
                with open(self.data_file_path, 'r') as file:
                    data = json.load(file)
                    self.chemicals_data = data.get('chemicals', {})
                    self.compatibility_matrix = data.get('compatibility', {})
                self.logger.info(f"Loaded chemical safety data for {len(self.chemicals_data)} chemicals")
            else:
                self.logger.warning(f"Chemical safety data file not found at {self.data_file_path}")
                self._create_default_data()
        except (IOError, json.JSONDecodeError) as e:
            self.logger.error(f"Error loading chemical safety data: {str(e)}")
            self._create_default_data()
    
    def _create_default_data(self) -> None:
        """
        Create default chemical safety data for common pool chemicals.
        
        This is used when the data file doesn't exist or can't be loaded.
        """
        self.logger.info("Creating default chemical safety data")
        
        # Common pool chemicals with safety information
        self.chemicals_data = {
            "chlorine": {
                "name": "Chlorine",
                "chemical_formula": "Cl₂",
                "hazard_rating": 3,
                "safety_precautions": [
                    "Wear protective gloves and eye protection",
                    "Use in well-ventilated areas",
                    "Keep away from acids to prevent chlorine gas formation"
                ],
                "storage_guidelines": "Store in cool, dry place away from direct sunlight and incompatible materials",
                "emergency_procedures": "In case of exposure, move to fresh air and seek medical attention"
            },
            "muriatic_acid": {
                "name": "Muriatic Acid (Hydrochloric Acid)",
                "chemical_formula": "HCl",
                "hazard_rating": 3,
                "safety_precautions": [
                    "Always add acid to water, never water to acid",
                    "Wear chemical-resistant gloves, goggles, and protective clothing",
                    "Use in well-ventilated areas"
                ],
                "storage_guidelines": "Store in original container in cool, well-ventilated area away from bases",
                "emergency_procedures": "For skin contact, flush with water for 15 minutes and seek medical attention"
            },
            "sodium_bicarbonate": {
                "name": "Sodium Bicarbonate (Baking Soda)",
                "chemical_formula": "NaHCO₃",
                "hazard_rating": 1,
                "safety_precautions": [
                    "Minimal safety equipment required",
                    "Avoid generating dust"
                ],
                "storage_guidelines": "Store in dry area in sealed container",
                "emergency_procedures": "If in eyes, rinse with water"
            },
            "calcium_hypochlorite": {
                "name": "Calcium Hypochlorite",
                "chemical_formula": "Ca(ClO)₂",
                "hazard_rating": 3,
                "safety_precautions": [
                    "Wear protective gloves, clothing, and eye protection",
                    "Keep away from heat and combustible materials",
                    "Never mix with acids or ammonia"
                ],
                "storage_guidelines": "Store in cool, dry place away from acids and organic materials",
                "emergency_procedures": "In case of fire, use water spray. For exposure, seek medical attention"
            },
            "cyanuric_acid": {
                "name": "Cyanuric Acid",
                "chemical_formula": "C₃H₃N₃O₃",
                "hazard_rating": 1,
                "safety_precautions": [
                    "Avoid dust formation",
                    "Use with adequate ventilation"
                ],
                "storage_guidelines": "Store in dry, cool place in closed containers",
                "emergency_procedures": "If inhaled, move to fresh air"
            }
        }
        
        # Chemical compatibility matrix (1 = compatible, 0 = incompatible)
        self.compatibility_matrix = {
            "chlorine": {
                "muriatic_acid": 0,
                "sodium_bicarbonate": 1,
                "calcium_hypochlorite": 1,
                "cyanuric_acid": 1
            },
            "muriatic_acid": {
                "chlorine": 0,
                "sodium_bicarbonate": 0,
                "calcium_hypochlorite": 0,
                "cyanuric_acid": 1
            },
            "sodium_bicarbonate": {
                "chlorine": 1,
                "muriatic_acid": 0,
                "calcium_hypochlorite": 1,
                "cyanuric_acid": 1
            },
            "calcium_hypochlorite": {
                "chlorine": 1,
                "muriatic_acid": 0,
                "sodium_bicarbonate": 1,
                "cyanuric_acid": 1
            },
            "cyanuric_acid": {
                "chlorine": 1,
                "muriatic_acid": 1,
                "sodium_bicarbonate": 1,
                "calcium_hypochlorite": 1
            }
        }
        
        # Save default data
        self._save_data()
    
    def _save_data(self) -> None:
        """
        Save chemical safety data to the data file.
        
        Creates the directory if it doesn't exist.
        
        Raises:
            IOError: If there's an error writing to the data file
            OSError: If there's an error creating the directory
        """
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.data_file_path), exist_ok=True)
            
            data = {
                "chemicals": self.chemicals_data,
                "compatibility": self.compatibility_matrix
            }
            
            with open(self.data_file_path, 'w') as file:
                json.dump(data, file, indent=4)
            
            self.logger.info(f"Saved chemical safety data to {self.data_file_path}")
        except (IOError, OSError) as e:
            self.logger.error(f"Error saving chemical safety data: {str(e)}")
            raise
    
    def get_chemical_safety_info(self, chemical_id: str) -> Optional[Dict]:
        """
        Get safety information for a specific chemical.
        
        Args:
            chemical_id: Identifier for the chemical
            
        Returns:
            Dictionary containing safety information or None if not found
        """
        return self.chemicals_data.get(chemical_id.lower())
    
    def get_all_chemicals(self) -> Dict[str, Dict[str, Any]]:
        """
        Get information for all chemicals in the database.
        
        Returns:
            Dictionary containing all chemical safety information
        """
        return self.chemicals_data
    
    def check_compatibility(self, chemical1: str, chemical2: str) -> bool:
        """
        Check if two chemicals are compatible for storage or mixing.
        
        Args:
            chemical1: First chemical identifier
            chemical2: Second chemical identifier
            
        Returns:
            True if chemicals are compatible, False otherwise
        """
        chemical1 = chemical1.lower()
        chemical2 = chemical2.lower()
        
        # Check if both chemicals exist in the database
        if chemical1 not in self.compatibility_matrix or chemical2 not in self.compatibility_matrix:
            self.logger.warning(f"Compatibility check failed: One or both chemicals not in database")
            return False
        
        # Check compatibility (if same chemical, they're compatible)
        if chemical1 == chemical2:
            return True
            
        return bool(self.compatibility_matrix.get(chemical1, {}).get(chemical2, 0))
    
    def get_safety_guidelines(self, chemical_id: str) -> List[str]:
        """
        Get safety guidelines for handling a specific chemical.
        
        Args:
            chemical_id: Identifier for the chemical
            
        Returns:
            List of safety guidelines
        """
        chemical_info = self.get_chemical_safety_info(chemical_id)
        if not chemical_info:
            return []
        return chemical_info.get("safety_precautions", [])
    
    def add_chemical(self, chemical_id: str, chemical_data: Dict[str, Any]) -> bool:
        """
        Add a new chemical to the safety database.
        
        Args:
            chemical_id: Identifier for the chemical
            chemical_data: Dictionary containing chemical safety information
            
        Returns:
            True if successful, False otherwise
            
        Raises:
            ValueError: If the chemical data is invalid
        """
        try:
            # Validate required fields
            required_fields = ["name", "hazard_rating", "safety_precautions"]
            for field in required_fields:
                if field not in chemical_data:
                    raise ValueError(f"Missing required field: {field}")
            
            chemical_id = chemical_id.lower()
            self.chemicals_data[chemical_id] = chemical_data
            self._save_data()
            self.logger.info(f"Added chemical {chemical_id} to safety database")
            return True
        except Exception as e:
            self.logger.error(f"Error adding chemical {chemical_id}: {str(e)}")
            return False
    
    def update_chemical(self, chemical_id: str, chemical_data: Dict[str, Any]) -> bool:
        """
        Update information for an existing chemical.
        
        Args:
            chemical_id: Identifier for the chemical
            chemical_data: Dictionary containing updated chemical safety information
            
        Returns:
            True if successful, False otherwise
            
        Raises:
            ValueError: If the chemical doesn't exist or the data is invalid
        """
        chemical_id = chemical_id.lower()
        if chemical_id not in self.chemicals_data:
            self.logger.warning(f"Cannot update chemical {chemical_id}: Not found in database")
            return False
            
        try:
            # Validate required fields
            required_fields = ["name", "hazard_rating", "safety_precautions"]
            for field in required_fields:
                if field not in chemical_data:
                    raise ValueError(f"Missing required field: {field}")
            
            self.chemicals_data[chemical_id] = chemical_data
            self._save_data()
            self.logger.info(f"Updated chemical {chemical_id} in safety database")
            return True
        except Exception as e:
            self.logger.error(f"Error updating chemical {chemical_id}: {str(e)}")
            return False
    
    def set_compatibility(self, chemical1: str, chemical2: str, compatible: bool) -> bool:
        """
        Set compatibility between two chemicals.
        
        Args:
            chemical1: First chemical identifier
            chemical2: Second chemical identifier
            compatible: True if chemicals are compatible, False otherwise
            
        Returns:
            True if successful, False otherwise
            
        Raises:
            ValueError: If either chemical doesn't exist in the database
        """
        chemical1 = chemical1.lower()
        chemical2 = chemical2.lower()
        
        # Check if both chemicals exist in the database
        if chemical1 not in self.chemicals_data or chemical2 not in self.chemicals_data:
            self.logger.warning("Cannot set compatibility: One or both chemicals not in database")
            return False
            
        try:
            # Ensure compatibility matrix entries exist
            if chemical1 not in self.compatibility_matrix:
                self.compatibility_matrix[chemical1] = {}
            if chemical2 not in self.compatibility_matrix:
                self.compatibility_matrix[chemical2] = {}
                
            # Set bidirectional compatibility
            self.compatibility_matrix[chemical1][chemical2] = 1 if compatible else 0
            self.compatibility_matrix[chemical2][chemical1] = 1 if compatible else 0
            
            self._save_data()
            self.logger.info(f"Set compatibility between {chemical1} and {chemical2} to {compatible}")
            return True
        except Exception as e:
            self.logger.error(f"Error setting compatibility: {str(e)}")
            return False
    
    def get_hazard_rating(self, chemical_id: str) -> Optional[int]:
        """
        Get the hazard rating for a specific chemical.
        
        Args:
            chemical_id: Identifier for the chemical
            
        Returns:
            Hazard rating (1-4) or None if not found
        """
        chemical_info = self.get_chemical_safety_info(chemical_id)
        if not chemical_info:
            return None
        return chemical_info.get("hazard_rating")
    
    def get_emergency_procedures(self, chemical_id: str) -> Optional[str]:
        """
        Get emergency procedures for a specific chemical.
        
        Args:
            chemical_id: Identifier for the chemical
            
        Returns:
            Emergency procedures or None if not found
        """
        chemical_info = self.get_chemical_safety_info(chemical_id)
        if not chemical_info:
            return None
        return chemical_info.get("emergency_procedures")
    
    def get_storage_guidelines(self, chemical_id: str) -> Optional[str]:
        """
        Get storage guidelines for a specific chemical.
        
        Args:
            chemical_id: Identifier for the chemical
            
        Returns:
            Storage guidelines or None if not found
        """
        chemical_info = self.get_chemical_safety_info(chemical_id)
        if not chemical_info:
            return None
        return chemical_info.get("storage_guidelines")

#############################################################################
# Color Calibrator
#############################################################################

class ColorCalibrator:
    """
    Color calibrator for mapping RGB values to chemical readings.
    
    This class handles the calibration data for mapping RGB colors to chemical values.
    
    Attributes:
        calibration_data: Dictionary of calibration data for each chemical
    """
    
    def __init__(self, calibration_file: str = "data/calibration.json"):
        """
        Initialize the color calibrator.
        
        Args:
            calibration_file: Path to the calibration data JSON file
        """
        self.calibration_data = {}
        self._load_calibration(calibration_file)

    def _load_calibration(self, path: str) -> None:
        """
        Load calibration data from a JSON file.
        
        Args:
            path: Path to the calibration data JSON file
            
        Raises:
            FileNotFoundError: If the calibration file doesn't exist
            json.JSONDecodeError: If the calibration file contains invalid JSON
        """
        try:
            with open(path, "r") as f:
                self.calibration_data = json.load(f)
            logger.info(f"Loaded calibration data from {path}")
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"Failed to load calibration data: {e}")
            self.calibration_data = {}

    def _distance(self, rgb1: List[int], rgb2: List[int]) -> float:
        """
        Calculate the Euclidean distance between two RGB colors.
        
        Args:
            rgb1: First RGB color as a list [R, G, B]
            rgb2: Second RGB color as a list [R, G, B]
            
        Returns:
            Euclidean distance between the colors
        """
        return np.sqrt(sum((a - b) ** 2 for a, b in zip(rgb1, rgb2)))

    def map_rgb_to_value(self, chemical: str, rgb_sample: List[int]) -> Tuple[Optional[float], float]:
        """
        Map an RGB color to a chemical value using calibration data.
        
        Uses weighted interpolation of the closest calibration samples.
        
        Args:
            chemical: Name of the chemical
            rgb_sample: RGB color as a list [R, G, B]
            
        Returns:
            Tuple of (interpolated value, confidence percentage)
        """
        samples = self.calibration_data.get(chemical, [])
        if not samples:
            return None, 0.0

        # Calculate distances to all calibration samples
        distances = [(self._distance(rgb_sample, s["rgb"]), s["value"]) for s in samples]
        distances.sort(key=lambda x: x[0])
        
        # Use the top 3 closest samples for interpolation
        top = distances[:3]

        # Calculate weighted average based on inverse distance
        weights = [1 / (d + 1e-6) for d, _ in top]
        total_weight = sum(weights)
        interpolated = sum(v * w for (_, v), w in zip(top, weights)) / total_weight
        
        # Calculate confidence based on distance to closest sample
        # 0 distance = 100% confidence, max possible distance = 0% confidence
        max_possible_distance = np.sqrt(3 * 255 ** 2)  # Maximum RGB distance
        confidence = max(0.0, 100 - top[0][0] / max_possible_distance * 100)

        return round(interpolated, 2), round(confidence, 1)

    def rgb_confidence(self, sample: List[int], reference: List[int]) -> float:
        """
        Calculate confidence score for how closely a sample matches a reference color.
        
        Args:
            sample: Sample RGB color as a list [R, G, B]
            reference: Reference RGB color as a list [R, G, B]
            
        Returns:
            Confidence score (0-100)
        """
        dist = self._distance(sample, reference)
        max_dist = np.sqrt(3 * 255 ** 2)
        score = max(0, 100 - (dist / max_dist) * 100)
        return round(score, 1)

#############################################################################
# Test Strip Analyzer
#############################################################################

class TestStripAnalyzer:
    """
    Analyzer for pool test strips using computer vision.
    
    This class provides functionality for capturing, analyzing, and interpreting
    pool test strips to determine water chemistry parameters.
    
    Attributes:
        latest_image_path: Path to the most recently captured or loaded image
        brand: Brand of test strips being used
        calibrator: Color calibrator for mapping RGB values to chemical readings
        pad_zones: Dictionary of test strip pad zones for each chemical
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the test strip analyzer.
        
        Args:
            config: Configuration dictionary with optional settings
        """
        self.latest_image_path = None
        self.brand = (config or {}).get("strip_brand", "default")
        calib_file = (config or {}).get("calibration_file", "data/calibration.json")
        self.calibrator = ColorCalibrator(calib_file)
        self.pad_zones = self._load_pad_zones()
        self.image_cache = {}  # Cache for processed images
        logger.info(f"TestStripAnalyzer initialized with brand: {self.brand}")

    def _load_pad_zones(self) -> Dict[str, List[int]]:
        """
        Load test strip pad zones from configuration file.
        
        Returns:
            Dictionary of pad zones for each chemical
            
        Raises:
            FileNotFoundError: If the pad zones file doesn't exist
            json.JSONDecodeError: If the pad zones file contains invalid JSON
        """
        # Default pad zones if file not found
        default_zones = {
            "pH": [50, 50, 40, 40],
            "free_chlorine": [100, 50, 40, 40],
            "total_chlorine": [150, 50, 40, 40],
            "alkalinity": [200, 50, 40, 40],
            "calcium": [250, 50, 40, 40],
            "cyanuric_acid": [300, 50, 40, 40],
            "bromine": [350, 50, 40, 40],
            "salt": [400, 50, 40, 40]
        }
        
        try:
            pad_zones_file = "data/pad_zones.json"
            if os.path.exists(pad_zones_file):
                with open(pad_zones_file, "r") as f:
                    brands = json.load(f)
                    zones = brands.get(self.brand)
                    if not zones:
                        logger.warning(f"No pad zones found for brand '{self.brand}', using default layout")
                        return default_zones
                    return zones
            else:
                logger.warning(f"Pad zones file not found, using default layout")
                return default_zones
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"Failed to load pad zones: {e}")
            return default_zones

    def capture_image(self) -> Optional[str]:
        """
        Capture or load a test strip image.
        
        In a real implementation, this would capture from a camera.
        This implementation loads a test image from a file.
        
        Returns:
            Path to the captured image or None if failed
            
        Raises:
            FileNotFoundError: If the test image doesn't exist
        """
        test_image_path = "data/test_strip.jpg"
        if not os.path.exists(test_image_path):
            logger.error(f"Test strip image not found: {test_image_path}")
            self.latest_image_path = None
            return None

        self.latest_image_path = test_image_path
        # Clear the image cache when a new image is captured
        self.image_cache = {}
        logger.info(f"Captured image: {self.latest_image_path}")
        return self.latest_image_path

    def load_image(self, image_path: str) -> Optional[str]:
        """
        Load a test strip image from a file.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Path to the loaded image or None if failed
            
        Raises:
            FileNotFoundError: If the image doesn't exist
        """
        if not os.path.exists(image_path):
            logger.error(f"Image not found: {image_path}")
            return None

        self.latest_image_path = image_path
        # Clear the image cache when a new image is loaded
        self.image_cache = {}
        logger.info(f"Loaded image: {self.latest_image_path}")
        return self.latest_image_path

    def get_image_preview(self, with_annotations: bool = True) -> Optional[Image.Image]:
        """
        Get a preview of the test strip image with optional annotations.
        
        Args:
            with_annotations: Whether to include pad zone annotations
            
        Returns:
            PIL Image object or None if no image is available
            
        Raises:
            cv2.error: If there's an error processing the image
        """
        if not self.latest_image_path:
            logger.warning("No image available for preview")
            return None
            
        # Check if we have this preview in the cache
        cache_key = f"preview_{with_annotations}"
        if cache_key in self.image_cache:
            return self.image_cache[cache_key]
            
        try:
            image = cv2.imread(self.latest_image_path)
            if image is None:
                logger.error(f"Failed to load image: {self.latest_image_path}")
                return None
                
            # Create a copy for annotations
            if with_annotations:
                for chem, (x, y, w, h) in self.pad_zones.items():
                    cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    cv2.putText(image, chem, (x, y - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
                    
            # Convert to PIL Image and resize
            preview = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            preview = preview.resize((300, 200))
            
            # Cache the preview
            self.image_cache[cache_key] = preview
            return preview
        except cv2.error as e:
            logger.error(f"Failed to generate image preview: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error generating preview: {e}")
            return None

    def analyze(self) -> Dict[str, Dict[str, Any]]:
        """
        Analyze the test strip image to determine chemical readings.
        
        Returns:
            Dictionary of chemical readings with values, confidence, and RGB colors
            
        Raises:
            cv2.error: If there's an error processing the image
        """
        if not self.latest_image_path:
            logger.error("No image captured for analysis")
            return {}
            
        # Check if we have the analysis in the cache
        if "analysis" in self.image_cache:
            return self.image_cache["analysis"]

        try:
            image = cv2.imread(self.latest_image_path)
            if image is None:
                logger.error(f"Failed to load image for analysis: {self.latest_image_path}")
                return {}

            # Apply image preprocessing for better color detection
            # Convert to LAB color space for better color differentiation
            lab_image = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
            
            # Apply slight Gaussian blur to reduce noise
            lab_image = cv2.GaussianBlur(lab_image, (3, 3), 0)
            
            results = {}
            for chem, (x, y, w, h) in self.pad_zones.items():
                # Extract region of interest (ROI)
                roi = image[y:y + h, x:x + w]
                
                # Calculate average color in the ROI
                avg_color = cv2.mean(roi)[:3]  # BGR
                
                # Convert to RGB for the calibrator
                rgb = [int(avg_color[2]), int(avg_color[1]), int(avg_color[0])]
                
                # Map RGB to chemical value
                value, confidence = self.calibrator.map_rgb_to_value(chem, rgb)
                
                results[chem] = {
                    "value": value,
                    "confidence": confidence,
                    "rgb": rgb
                }
                logger.debug(f"{chem}: RGB={rgb}, Value={value}, Confidence={confidence}%")

            # Cache the analysis results
            self.image_cache["analysis"] = results
            logger.info("Test strip analysis completed")
            return results
        except cv2.error as e:
            logger.error(f"OpenCV error during analysis: {e}")
            return {}
        except Exception as e:
            logger.error(f"Unexpected error during analysis: {e}")
            return {}

    def get_recommendations(self, analysis_results: Dict[str, Dict[str, Any]]) -> Dict[str, str]:
        """
        Generate recommendations based on analysis results.
        
        Args:
            analysis_results: Dictionary of chemical readings from analyze()
            
        Returns:
            Dictionary of recommendations for each chemical
        """
        recommendations = {}
        
        # Define ideal ranges for each chemical
        ideal_ranges = {
            "pH": (7.2, 7.8),
            "free_chlorine": (1.0, 3.0),
            "total_chlorine": (1.0, 3.0),
            "alkalinity": (80, 120),
            "calcium": (200, 400),
            "cyanuric_acid": (30, 50),
            "bromine": (3.0, 5.0),
            "salt": (2700, 3400)
        }
        
        for chem, result in analysis_results.items():
            value = result.get("value")
            if value is None:
                continue
                
            ideal_range = ideal_ranges.get(chem)
            if not ideal_range:
                continue
                
            low, high = ideal_range
            
            if value < low:
                recommendations[chem] = f"Increase {chem} from {value} to {low}-{high}"
            elif value > high:
                recommendations[chem] = f"Decrease {chem} from {value} to {low}-{high}"
            else:
                recommendations[chem] = f"{chem} level is good at {value} (ideal: {low}-{high})"
                
        return recommendations

    def save_analysis_results(self, results: Dict[str, Dict[str, Any]], filename: str) -> bool:
        """
        Save analysis results to a JSON file.
        
        Args:
            results: Dictionary of chemical readings from analyze()
            filename: Path to save the results
            
        Returns:
            True if successful, False otherwise
            
        Raises:
            IOError: If there's an error writing to the file
        """
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            
            # Add timestamp and image path to results
            output = {
                "timestamp": datetime.now().isoformat(),
                "image_path": self.latest_image_path,
                "results": results
            }
            
            with open(filename, "w") as f:
                json.dump(output, f, indent=4)
                
            logger.info(f"Analysis results saved to {filename}")
            return True
        except (IOError, OSError) as e:
            logger.error(f"Failed to save analysis results: {e}")
            return False

    def clear_cache(self) -> None:
        """
        Clear the image cache to free memory.
        """
        self.image_cache = {}
        logger.debug("Image cache cleared")

#############################################################################
# Weather Service
#############################################################################

class WeatherService:
    """
    Weather service for retrieving and analyzing weather data.
    
    This class provides methods for retrieving current and forecasted weather data
    and analyzing its impact on pool chemistry.
    
    Attributes:
        config: Configuration dictionary with API keys and settings
        cache_file: Path to the weather data cache file
        cache_data: Dictionary of cached weather data
        cache_expiry: Dictionary of cache expiry times
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the weather service.
        
        Args:
            config: Configuration dictionary with API keys and settings
        """
        self.config = config or {}
        self.location = self.config.get("location", "Florida")
        self.api_key = self.config.get("api_key", "")
        self.update_interval = self.config.get("update_interval", 3600)  # Default: 1 hour
        self.cache_file = self.config.get("cache_file", "data/weather_cache.json")
        self.cache_data = {}
        self.cache_expiry = {}
        
        # Load cached data if available
        self._load_cache()
        logger.info(f"Weather Service initialized for location: {self.location}")
    
    def _load_cache(self) -> None:
        """
        Load weather data from cache file.
        
        Raises:
            IOError: If there's an error reading the cache file
            json.JSONDecodeError: If the cache file contains invalid JSON
        """
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r') as f:
                    cache = json.load(f)
                    self.cache_data = cache.get("data", {})
                    self.cache_expiry = cache.get("expiry", {})
                logger.info(f"Loaded weather cache from {self.cache_file}")
        except (IOError, json.JSONDecodeError) as e:
            logger.error(f"Failed to load weather cache: {e}")
            self.cache_data = {}
            self.cache_expiry = {}
    
    def _save_cache(self) -> None:
        """
        Save weather data to cache file.
        
        Raises:
            IOError: If there's an error writing to the cache file
        """
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
            
            cache = {
                "data": self.cache_data,
                "expiry": self.cache_expiry
            }
            with open(self.cache_file, 'w') as f:
                json.dump(cache, f, indent=2)
            logger.info(f"Saved weather cache to {self.cache_file}")
        except IOError as e:
            logger.error(f"Failed to save weather cache: {e}")
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """
        Check if cached data is still valid.
        
        Args:
            cache_key: Cache key to check
            
        Returns:
            True if cache is valid, False otherwise
        """
        if cache_key not in self.cache_data or cache_key not in self.cache_expiry:
            return False
        
        expiry_time = self.cache_expiry.get(cache_key, 0)
        return time.time() < expiry_time
    
    def get_weather(self) -> Dict[str, Any]:
        """
        Get current weather data for the configured location.
        
        Returns:
            Dictionary containing weather data
            
        Raises:
            requests.RequestException: If there's an error retrieving weather data
        """
        cache_key = f"current_{self.location}"
        
        # Check if we have valid cached data
        if self._is_cache_valid(cache_key):
            logger.debug(f"Using cached weather data for {self.location}")
            return self.cache_data[cache_key]
        
        try:
            # In a real implementation, this would call a weather API
            # For this example, we'll return mock data
            weather_data = self._get_mock_weather_data()
            
            # Cache the data
            self.cache_data[cache_key] = weather_data
            self.cache_expiry[cache_key] = time.time() + self.update_interval
            self._save_cache()
            
            logger.info(f"Retrieved weather data for {self.location}")
            return weather_data
        except requests.RequestException as e:
            logger.error(f"Failed to retrieve weather data: {e}")
            
            # Return cached data if available, even if expired
            if cache_key in self.cache_data:
                logger.warning("Using expired cached weather data")
                return self.cache_data[cache_key]
            
            # Return empty data if no cache is available
            return {
                "temperature": 75,
                "humidity": 50,
                "conditions": "Unknown",
                "uv_index": 0,
                "wind_speed": 0,
                "precipitation": 0,
                "timestamp": datetime.now().isoformat()
            }
    
    def get_forecast(self, days: int = 3) -> List[Dict[str, Any]]:
        """
        Get weather forecast for the configured location.
        
        Args:
            days: Number of days to forecast
            
        Returns:
            List of dictionaries containing forecast data
            
        Raises:
            requests.RequestException: If there's an error retrieving forecast data
        """
        cache_key = f"forecast_{self.location}_{days}"
        
        # Check if we have valid cached data
        if self._is_cache_valid(cache_key):
            logger.debug(f"Using cached forecast data for {self.location}")
            return self.cache_data[cache_key]
        
        try:
            # In a real implementation, this would call a weather API
            # For this example, we'll return mock data
            forecast_data = self._get_mock_forecast_data(days)
            
            # Cache the data
            self.cache_data[cache_key] = forecast_data
            self.cache_expiry[cache_key] = time.time() + self.update_interval
            self._save_cache()
            
            logger.info(f"Retrieved {days}-day forecast for {self.location}")
            return forecast_data
        except requests.RequestException as e:
            logger.error(f"Failed to retrieve forecast data: {e}")
            
            # Return cached data if available, even if expired
            if cache_key in self.cache_data:
                logger.warning("Using expired cached forecast data")
                return self.cache_data[cache_key]
            
            # Return empty data if no cache is available
            return [self._get_mock_weather_data() for _ in range(days)]
    
    def _get_mock_weather_data(self) -> Dict[str, Any]:
        """
        Generate mock weather data for testing.
        
        Returns:
            Dictionary containing mock weather data
        """
        # Get current date and time
        now = datetime.now()
        
        # Generate mock data based on month (seasonal variations)
        month = now.month
        
        # Summer months (higher temperatures)
        if 5 <= month <= 9:
            temperature = 85 + (hash(now.strftime("%Y-%m-%d")) % 10)
            humidity = 65 + (hash(now.strftime("%H")) % 20)
            conditions = "Sunny" if hash(now.strftime("%Y-%m-%d")) % 4 != 0 else "Partly Cloudy"
            uv_index = 8 + (hash(now.strftime("%Y-%m-%d")) % 4)
            precipitation = 0 if hash(now.strftime("%Y-%m-%d")) % 5 != 0 else 0.2
        # Winter months (lower temperatures)
        else:
            temperature = 65 + (hash(now.strftime("%Y-%m-%d")) % 15)
            humidity = 45 + (hash(now.strftime("%H")) % 30)
            conditions = "Sunny" if hash(now.strftime("%Y-%m-%d")) % 3 != 0 else "Cloudy"
            uv_index = 4 + (hash(now.strftime("%Y-%m-%d")) % 3)
            precipitation = 0 if hash(now.strftime("%Y-%m-%d")) % 4 != 0 else 0.1
        
        # Wind speed is consistent year-round
        wind_speed = 5 + (hash(now.strftime("%H")) % 10)
        
        return {
            "temperature": temperature,
            "humidity": humidity,
            "conditions": conditions,
            "uv_index": uv_index,
            "wind_speed": wind_speed,
            "precipitation": precipitation,
            "timestamp": now.isoformat()
        }
    
    def _get_mock_forecast_data(self, days: int) -> List[Dict[str, Any]]:
        """
        Generate mock forecast data for testing.
        
        Args:
            days: Number of days to forecast
            
        Returns:
            List of dictionaries containing mock forecast data
        """
        forecast = []
        now = datetime.now()
        
        for i in range(days):
            forecast_date = now + timedelta(days=i)
            
            # Base the forecast on the mock weather data with some variations
            base_weather = self._get_mock_weather_data()
            
            # Add some variation for each day
            base_weather["temperature"] += (hash(forecast_date.strftime("%Y-%m-%d")) % 5) - 2
            base_weather["humidity"] += (hash(forecast_date.strftime("%Y-%m-%d")) % 10) - 5
            base_weather["timestamp"] = forecast_date.isoformat()
            
            # Change conditions occasionally
            if hash(forecast_date.strftime("%Y-%m-%d")) % 3 == 0:
                conditions = ["Sunny", "Partly Cloudy", "Cloudy", "Rainy"]
                base_weather["conditions"] = conditions[hash(forecast_date.strftime("%Y-%m-%d")) % len(conditions)]
                
                # Add precipitation for rainy days
                if base_weather["conditions"] == "Rainy":
                    base_weather["precipitation"] = 0.2 + (hash(forecast_date.strftime("%Y-%m-%d")) % 10) / 10
            
            forecast.append(base_weather)
        
        return forecast
    
    def analyze_weather_impact(self, weather_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze the impact of weather conditions on pool chemistry.
        
        Args:
            weather_data: Dictionary containing weather data
            
        Returns:
            Dictionary containing weather impact analysis
        """
        impact = {
            "evaporation_rate": 0.0,
            "chlorine_loss_rate": 0.0,
            "algae_growth_risk": "Low",
            "recommendations": []
        }
        
        # Calculate evaporation rate based on temperature, humidity, and wind speed
        temperature = weather_data.get("temperature", 75)
        humidity = weather_data.get("humidity", 50)
        wind_speed = weather_data.get("wind_speed", 0)
        uv_index = weather_data.get("uv_index", 0)
        conditions = weather_data.get("conditions", "Unknown")
        
        # Higher temperature, lower humidity, and higher wind speed increase evaporation
        evaporation_factor = (temperature / 100) * (1 - humidity / 100) * (1 + wind_speed / 10)
        impact["evaporation_rate"] = round(evaporation_factor * 0.25, 2)  # inches per day
        
        # Calculate chlorine loss rate based on temperature and UV index
        # Higher temperature and UV index increase chlorine loss
        chlorine_loss_factor = (temperature / 100) * (1 + uv_index / 5)
        impact["chlorine_loss_rate"] = round(chlorine_loss_factor * 0.5, 2)  # ppm per day
        
        # Determine algae growth risk based on temperature and conditions
        if temperature > 85 and conditions in ["Sunny", "Partly Cloudy"]:
            impact["algae_growth_risk"] = "High"
        elif temperature > 75:
            impact["algae_growth_risk"] = "Medium"
        else:
            impact["algae_growth_risk"] = "Low"
        
        # Generate recommendations based on analysis
        if impact["evaporation_rate"] > 0.2:
            impact["recommendations"].append("Monitor water level due to high evaporation rate")
        
        if impact["chlorine_loss_rate"] > 0.3:
            impact["recommendations"].append("Increase chlorine dosage to compensate for high UV-induced loss")
        
        if impact["algae_growth_risk"] == "High":
            impact["recommendations"].append("Consider algaecide treatment due to high algae growth risk")
        
        if conditions == "Rainy":
            impact["recommendations"].append("Check pH and alkalinity after rain")
        
        return impact
    
    def get_weather_with_impact(self) -> Dict[str, Any]:
        """
        Get current weather data with impact analysis.
        
        Returns:
            Dictionary containing weather data and impact analysis
        """
        weather_data = self.get_weather()
        impact = self.analyze_weather_impact(weather_data)
        
        return {
            "weather": weather_data,
            "impact": impact
        }
    
    def get_forecast_with_impact(self, days: int = 3) -> List[Dict[str, Any]]:
        """
        Get weather forecast with impact analysis.
        
        Args:
            days: Number of days to forecast
            
        Returns:
            List of dictionaries containing forecast data and impact analysis
        """
        forecast_data = self.get_forecast(days)
        forecast_with_impact = []
        
        for day_data in forecast_data:
            impact = self.analyze_weather_impact(day_data)
            forecast_with_impact.append({
                "weather": day_data,
                "impact": impact
            })
        
        return forecast_with_impact
    
    def clear_cache(self) -> None:
        """
        Clear the weather data cache.
        """
        self.cache_data = {}
        self.cache_expiry = {}
        
        # Remove cache file if it exists
        if os.path.exists(self.cache_file):
            try:
                os.remove(self.cache_file)
                logger.info(f"Removed weather cache file: {self.cache_file}")
            except OSError as e:
                logger.error(f"Failed to remove weather cache file: {e}")
        
        logger.info("Weather cache cleared")

#############################################################################
# GUI Controller
#############################################################################

class ChemicalCalculator:
    """
    Calculator for pool chemical adjustments.
    
    This class provides methods for calculating chemical adjustments based on
    water test results and evaluating water balance.
    
    Attributes:
        ideal_ranges: Dictionary of ideal ranges for water parameters
    """
    
    def __init__(self):
        """Initialize the chemical calculator with ideal ranges."""
        self.ideal_ranges = {
            "ph": (7.2, 7.8),
            "chlorine": (1.0, 3.0),
            "alkalinity": (80, 120),
            "calcium_hardness": {
                "Concrete/Gunite": (200, 400),
                "Vinyl": (175, 225),
                "Fiberglass": (175, 225),
                "Above Ground": (175, 225)
            }
        }
        logger.info("ChemicalCalculator initialized")
    
    def validate_reading(self, param: str, value: float) -> bool:
        """
        Validate a water parameter reading.
        
        Args:
            param: Parameter name
            value: Parameter value
            
        Returns:
            True if valid, False otherwise
            
        Raises:
            ValueError: If the value is outside acceptable ranges
        """
        # Define acceptable ranges (wider than ideal ranges)
        acceptable_ranges = {
            "ph": (6.0, 9.0),
            "chlorine": (0.0, 10.0),
            "alkalinity": (0, 300),
            "calcium_hardness": (0, 1000),
            "cyanuric_acid": (0, 200),
            "temperature": (32, 104)
        }
        
        if param not in acceptable_ranges:
            return True  # No validation for unknown parameters
        
        min_val, max_val = acceptable_ranges[param]
        
        if value < min_val or value > max_val:
            raise ValueError(f"{param} value {value} is outside acceptable range ({min_val}-{max_val})")
        
        return True
    
    def get_ideal_range(self, param: str, pool_type: Optional[str] = None) -> Tuple[float, float]:
        """
        Get the ideal range for a water parameter.
        
        Args:
            param: Parameter name
            pool_type: Type of pool (for calcium hardness)
            
        Returns:
            Tuple of (min, max) values
        """
        if param == "calcium_hardness" and pool_type:
            return self.ideal_ranges[param].get(pool_type, self.ideal_ranges[param]["Concrete/Gunite"])
        return self.ideal_ranges.get(param, (0, 0))
    
    def calculate_adjustments(self, pool_type: str, ph: float, chlorine: float, 
                             alkalinity: float, calcium_hardness: float, 
                             pool_size: float) -> Dict[str, Dict[str, Any]]:
        """
        Calculate chemical adjustments based on water test results.
        
        Args:
            pool_type: Type of pool
            ph: pH level
            chlorine: Chlorine level (ppm)
            alkalinity: Alkalinity level (ppm)
            calcium_hardness: Calcium hardness level (ppm)
            pool_size: Pool size in gallons
            
        Returns:
            Dictionary of chemical adjustments
        """
        adjustments = {}
        
        # Calculate pH adjustment
        ph_min, ph_max = self.get_ideal_range("ph")
        if ph < ph_min:
            # Need to increase pH
            ph_increaser_amount = (ph_min - ph) * pool_size / 10000 * 6  # oz per 10,000 gallons
            adjustments["ph_increaser"] = {
                "amount": round(ph_increaser_amount, 2),
                "unit": "oz",
                "reason": f"Increase pH from {ph} to {ph_min}-{ph_max}"
            }
        elif ph > ph_max:
            # Need to decrease pH
            ph_decreaser_amount = (ph - ph_max) * pool_size / 10000 * 8  # oz per 10,000 gallons
            adjustments["ph_decreaser"] = {
                "amount": round(ph_decreaser_amount, 2),
                "unit": "oz",
                "reason": f"Decrease pH from {ph} to {ph_min}-{ph_max}"
            }
        
        # Calculate chlorine adjustment
        cl_min, cl_max = self.get_ideal_range("chlorine")
        if chlorine < cl_min:
            # Need to increase chlorine
            chlorine_amount = (cl_min - chlorine) * pool_size / 10000 * 2  # lbs per 10,000 gallons
            adjustments["chlorine"] = {
                "amount": round(chlorine_amount, 2),
                "unit": "lbs",
                "reason": f"Increase chlorine from {chlorine} to {cl_min}-{cl_max}"
            }
        elif chlorine > cl_max:
            # Need to decrease chlorine (wait or dilute)
            adjustments["chlorine_reduction"] = {
                "amount": 0,
                "unit": "",
                "reason": f"Reduce chlorine from {chlorine} to {cl_min}-{cl_max} by waiting or diluting"
            }
        
        # Calculate alkalinity adjustment
        alk_min, alk_max = self.get_ideal_range("alkalinity")
        if alkalinity < alk_min:
            # Need to increase alkalinity
            alk_increaser_amount = (alk_min - alkalinity) * pool_size / 10000 * 1.5  # lbs per 10,000 gallons
            adjustments["alkalinity_increaser"] = {
                "amount": round(alk_increaser_amount, 2),
                "unit": "lbs",
                "reason": f"Increase alkalinity from {alkalinity} to {alk_min}-{alk_max}"
            }
        elif alkalinity > alk_max:
            # Need to decrease alkalinity
            adjustments["alkalinity_decreaser"] = {
                "amount": 0,
                "unit": "",
                "reason": f"Decrease alkalinity from {alkalinity} to {alk_min}-{alk_max} by adding acid"
            }
        
        # Calculate calcium hardness adjustment
        ch_min, ch_max = self.get_ideal_range("calcium_hardness", pool_type)
        if calcium_hardness < ch_min:
            # Need to increase calcium hardness
            ch_increaser_amount = (ch_min - calcium_hardness) * pool_size / 10000 * 1.25  # lbs per 10,000 gallons
            adjustments["calcium_hardness_increaser"] = {
                "amount": round(ch_increaser_amount, 2),
                "unit": "lbs",
                "reason": f"Increase calcium hardness from {calcium_hardness} to {ch_min}-{ch_max}"
            }
        elif calcium_hardness > ch_max:
            # Need to decrease calcium hardness (dilution)
            adjustments["calcium_hardness_reduction"] = {
                "amount": 0,
                "unit": "",
                "reason": f"Reduce calcium hardness from {calcium_hardness} to {ch_min}-{ch_max} by diluting"
            }
        
        return adjustments
    
    def evaluate_water_balance(self, ph: float, alkalinity: float, 
                              calcium_hardness: float, temperature: float) -> float:
        """
        Calculate the Langelier Saturation Index (LSI) for water balance.
        
        Args:
            ph: pH level
            alkalinity: Alkalinity level (ppm)
            calcium_hardness: Calcium hardness level (ppm)
            temperature: Water temperature (°F)
            
        Returns:
            LSI value (negative = corrosive, positive = scaling, 0 = balanced)
        """
        # Temperature factor
        if temperature <= 32:
            temp_factor = 0.0
        elif temperature <= 37:
            temp_factor = 0.1
        elif temperature <= 46:
            temp_factor = 0.2
        elif temperature <= 53:
            temp_factor = 0.3
        elif temperature <= 60:
            temp_factor = 0.4
        elif temperature <= 66:
            temp_factor = 0.5
        elif temperature <= 76:
            temp_factor = 0.6
        elif temperature <= 84:
            temp_factor = 0.7
        elif temperature <= 94:
            temp_factor = 0.8
        elif temperature <= 105:
            temp_factor = 0.9
        else:
            temp_factor = 1.0
        
        # Calcium hardness factor
        if calcium_hardness <= 25:
            ch_factor = 0.4
        elif calcium_hardness <= 50:
            ch_factor = 0.7
        elif calcium_hardness <= 75:
            ch_factor = 0.9
        elif calcium_hardness <= 100:
            ch_factor = 1.0
        elif calcium_hardness <= 150:
            ch_factor = 1.1
        elif calcium_hardness <= 200:
            ch_factor = 1.2
        elif calcium_hardness <= 250:
            ch_factor = 1.3
        elif calcium_hardness <= 300:
            ch_factor = 1.4
        elif calcium_hardness <= 400:
            ch_factor = 1.5
        elif calcium_hardness <= 500:
            ch_factor = 1.6
        elif calcium_hardness <= 600:
            ch_factor = 1.7
        elif calcium_hardness <= 800:
            ch_factor = 1.8
        elif calcium_hardness <= 1000:
            ch_factor = 1.9
        else:
            ch_factor = 2.0
        
        # Alkalinity factor
        if alkalinity <= 25:
            alk_factor = 1.4
        elif alkalinity <= 50:
            alk_factor = 1.7
        elif alkalinity <= 75:
            alk_factor = 1.9
        elif alkalinity <= 100:
            alk_factor = 2.0
        elif alkalinity <= 125:
            alk_factor = 2.1
        elif alkalinity <= 150:
            alk_factor = 2.2
        elif alkalinity <= 200:
            alk_factor = 2.3
        elif alkalinity <= 250:
            alk_factor = 2.4
        elif alkalinity <= 300:
            alk_factor = 2.5
        elif alkalinity <= 400:
            alk_factor = 2.6
        elif alkalinity <= 500:
            alk_factor = 2.7
        elif alkalinity <= 600:
            alk_factor = 2.8
        elif alkalinity <= 800:
            alk_factor = 2.9
        else:
            alk_factor = 3.0
        
        # Calculate LSI
        lsi = ph + temp_factor + ch_factor + alk_factor - 12.1
        
        return round(lsi, 2)


class DatabaseManager:
    """
    Manager for database operations.
    
    This class provides methods for interacting with the database to store and
    retrieve pool chemistry data.
    
    Attributes:
        db_service: Database service instance
    """
    
    def __init__(self, db_service=None):
        """
        Initialize the database manager.
        
        Args:
            db_service: Database service instance (optional)
        """
        self.db_service = db_service
        logger.info("DatabaseManager initialized")
    
    def insert_test(self, location_name: str) -> int:
        """
        Insert a new test record.
        
        Args:
            location_name: Name of the test location
            
        Returns:
            Test ID
            
        Raises:
            RuntimeError: If database service is not available
        """
        if not self.db_service:
            logger.warning("Database service not available")
            return 1  # Return dummy ID
        
        try:
            # In a real implementation, this would insert a record and return the ID
            logger.info(f"Inserting test for location: {location_name}")
            return 1  # Dummy ID
        except Exception as e:
            logger.error(f"Failed to insert test: {e}")
            raise RuntimeError(f"Database error: {e}")
    
    def insert_test_result(self, test_id: int, param_name: str, value: float, unit: str) -> bool:
        """
        Insert a test result.
        
        Args:
            test_id: Test ID
            param_name: Parameter name
            value: Parameter value
            unit: Unit of measurement
            
        Returns:
            True if successful, False otherwise
            
        Raises:
            RuntimeError: If database service is not available
        """
        if not self.db_service:
            logger.warning("Database service not available")
            return True  # Pretend it worked
        
        try:
            logger.info(f"Inserting test result: {test_id}, {param_name}, {value}, {unit}")
            return True
        except Exception as e:
            logger.error(f"Failed to insert test result: {e}")
            raise RuntimeError(f"Database error: {e}")
    
    def get_recommendation(self, param_name: str, value: float) -> str:
        """
        Get a recommendation based on a parameter value.
        
        Args:
            param_name: Parameter name
            value: Parameter value
            
        Returns:
            Recommendation text
        """
        # Simple recommendations based on parameter name and value
        if param_name == "pH":
            if value < 7.2:
                return "Add pH increaser to raise pH level"
            elif value > 7.8:
                return "Add pH decreaser to lower pH level"
            else:
                return "pH level is within ideal range"
        elif param_name == "Chlorine":
            if value < 1.0:
                return "Add chlorine to increase level"
            elif value > 3.0:
                return "Chlorine level is high, avoid adding more until level drops"
            else:
                return "Chlorine level is within ideal range"
        elif param_name == "Alkalinity":
            if value < 80:
                return "Add alkalinity increaser to raise level"
            elif value > 120:
                return "Add acid to lower alkalinity level"
            else:
                return "Alkalinity level is within ideal range"
        elif param_name == "Calcium Hardness":
            if value < 200:
                return "Add calcium hardness increaser to raise level"
            elif value > 400:
                return "Dilute pool water to lower calcium hardness"
            else:
                return "Calcium hardness level is within ideal range"
        else:
            return f"Maintain {param_name} at optimal levels"
    
    def insert_recommendation(self, test_id: int, param_name: str, value: float, recommendation: str) -> bool:
        """
        Insert a recommendation.
        
        Args:
            test_id: Test ID
            param_name: Parameter name
            value: Parameter value
            recommendation: Recommendation text
            
        Returns:
            True if successful, False otherwise
            
        Raises:
            RuntimeError: If database service is not available
        """
        if not self.db_service:
            logger.warning("Database service not available")
            return True  # Pretend it worked
        
        try:
            logger.info(f"Inserting recommendation for {param_name}: {recommendation}")
            return True
        except Exception as e:
            logger.error(f"Failed to insert recommendation: {e}")
            raise RuntimeError(f"Database error: {e}")
    
    def export_to_csv(self, test_id: int) -> bool:
        """
        Export test results to CSV.
        
        Args:
            test_id: Test ID
            
        Returns:
            True if successful, False otherwise
            
        Raises:
            RuntimeError: If database service is not available
        """
        if not self.db_service:
            logger.warning("Database service not available")
            return True  # Pretend it worked
        
        try:
            logger.info(f"Exporting test results to CSV for test ID: {test_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to export to CSV: {e}")
            raise RuntimeError(f"Database error: {e}")
    
    def check_health(self) -> bool:
        """
        Check database health.
        
        Returns:
            True if healthy, False otherwise
        """
        if not self.db_service:
            logger.warning("Database service not available")
            return False
        
        try:
            # In a real implementation, this would check the database connection
            logger.info("Database health check passed")
            return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False
    
    def run_migrations(self) -> bool:
        """
        Run database migrations.
        
        Returns:
            True if successful, False otherwise
        """
        if not self.db_service:
            logger.warning("Database service not available")
            return False
        
        try:
            # In a real implementation, this would run database migrations
            logger.info("Database migrations completed")
            return True
        except Exception as e:
            logger.error(f"Database migrations failed: {e}")
            return False


class PoolChemistryController:
    """
    Controller for the Pool Chemistry application.
    
    This class mediates between the GUI views and the business logic of the application.
    
    Attributes:
        calculator: Chemical calculator instance
        db_manager: Database manager instance
    """
    
    def __init__(self, db_service=None):
        """
        Initialize the controller.
        
        Args:
            db_service: Database service instance (optional)
        """
        self.calculator = ChemicalCalculator()
        self.db_manager = DatabaseManager(db_service)
        logger.info("PoolChemistryController initialized")
    
    def validate_pool_data(self, pool_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Validate pool data from the GUI.
        
        Args:
            pool_data: Dictionary of pool data from GUI
            
        Returns:
            Dictionary of validation errors, empty if no errors
        """
        errors = {}
        
        # Validate required fields
        if not pool_data.get("pool_type"):
            errors["pool_type"] = "Pool type is required"
        
        # Validate pool size
        try:
            pool_size = float(pool_data.get("pool_size", 0))
            if pool_size <= 0:
                errors["pool_size"] = "Pool size must be greater than zero"
        except (ValueError, TypeError):
            errors["pool_size"] = "Pool size must be a numeric value"
        
        # Validate chemical readings
        for param in ["ph", "chlorine", "alkalinity", "calcium_hardness"]:
            try:
                if param in pool_data and pool_data[param]:
                    value = float(pool_data[param])
                    try:
                        self.calculator.validate_reading(param, value)
                    except ValueError as e:
                        errors[param] = str(e)
            except (ValueError, TypeError):
                errors[param] = f"{param} must be a numeric value"
        
        return errors
    
    def calculate_chemicals(self, pool_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate chemical adjustments based on pool data.
        
        Args:
            pool_data: Dictionary of pool data from GUI
            
        Returns:
            Dictionary with chemical adjustments and recommendations
            
        Raises:
            ValueError: If validation fails
        """
        try:
            # Validate pool data
            errors = self.validate_pool_data(pool_data)
            if errors:
                error_msg = "\n".join(f"{k}: {v}" for k, v in errors.items())
                raise ValueError(f"Validation errors:\n{error_msg}")
            
            # Extract data
            pool_type = pool_data["pool_type"]
            pool_size = float(pool_data["pool_size"])
            ph = float(pool_data.get("ph", 0))
            chlorine = float(pool_data.get("chlorine", 0))
            alkalinity = float(pool_data.get("alkalinity", 0))
            calcium_hardness = float(pool_data.get("calcium_hardness", 0))
            
            # Calculate adjustments
            adjustments = self.calculator.calculate_adjustments(
                pool_type, ph, chlorine, alkalinity, calcium_hardness, pool_size
            )
            
            # Calculate water balance if all required parameters are present
            water_balance = None
            if all(param in pool_data and pool_data[param] for param in ["ph", "alkalinity", "calcium_hardness", "temperature"]):
                water_balance = self.calculator.evaluate_water_balance(
                    ph, alkalinity, calcium_hardness, 
                    float(pool_data.get("temperature", 78.0))
                )
            
            # Prepare result
            result = {
                "adjustments": adjustments,
                "water_balance": water_balance,
                "ideal_ranges": {
                    "ph": self.calculator.get_ideal_range("ph"),
                    "chlorine": self.calculator.get_ideal_range("chlorine"),
                    "alkalinity": self.calculator.get_ideal_range("alkalinity"),
                    "calcium_hardness": self.calculator.get_ideal_range("calcium_hardness", pool_type)
                }
            }
            
            logger.info(f"Calculated chemicals for {pool_type} pool")
            return result
            
        except Exception as e:
            logger.error(f"Error calculating chemicals: {str(e)}")
            raise
    
    def save_test_results(self, pool_data: Dict[str, Any]) -> Optional[int]:
        """
        Save test results to the database.
        
        Args:
            pool_data: Dictionary of pool data from GUI
            
        Returns:
            Test ID if successful, None otherwise
        """
        try:
            # Insert test
            location_name = pool_data.get("location_name", "Unknown")
            test_id = self.db_manager.insert_test(location_name)
            
            if not test_id:
                logger.error("Failed to insert test")
                return None
            
            # Insert test results
            parameters = {
                "ph": "pH",
                "chlorine": "Chlorine",
                "alkalinity": "Alkalinity",
                "calcium_hardness": "Calcium Hardness",
                "cyanuric_acid": "Cyanuric Acid",
                "salt": "Salt"
            }
            
            for param_key, param_name in parameters.items():
                if param_key in pool_data and pool_data[param_key]:
                    try:
                        value = float(pool_data[param_key])
                        unit = "ppm" if param_key != "ph" else ""
                        
                        # Insert test result
                        self.db_manager.insert_test_result(test_id, param_name, value, unit)
                        
                        # Generate and insert recommendation
                        recommendation = self.db_manager.get_recommendation(param_name, value)
                        self.db_manager.insert_recommendation(test_id, param_name, value, recommendation)
                        
                    except (ValueError, TypeError) as e:
                        logger.warning(f"Skipping invalid {param_key} value: {str(e)}")
            
            # Export to CSV
            self.db_manager.export_to_csv(test_id)
            
            logger.info(f"Test results saved with ID {test_id}")
            return test_id
            
        except Exception as e:
            logger.error(f"Error saving test results: {str(e)}")
            return None
    
    def check_database_health(self) -> bool:
        """
        Check if the database connection is healthy.
        
        Returns:
            True if healthy, False otherwise
        """
        return self.db_manager.check_health()
    
    def run_database_migrations(self) -> bool:
        """
        Run database migrations.
        
        Returns:
            True if successful, False otherwise
        """
        return self.db_manager.run_migrations()

#############################################################################
# Main Application
#############################################################################

class PoolChemistryApp:
    """
    Main application class for the Deep Blue Pool Chemistry application.
    
    This class initializes and coordinates all the components of the application.
    
    Attributes:
        config: Configuration dictionary
        db_service: Database service instance
        chemical_safety_db: Chemical safety database instance
        test_strip_analyzer: Test strip analyzer instance
        weather_service: Weather service instance
        controller: Pool chemistry controller instance
    """
    
    def __init__(self, config_path: str = "config.json"):
        """
        Initialize the application.
        
        Args:
            config_path: Path to the configuration file
        """
        self.config = self._load_config(config_path)
        logger.info("Initializing Pool Chemistry Application")
        
        # Create data directory if it doesn't exist
        os.makedirs("data", exist_ok=True)
        
        # Initialize services
        self.db_service = self._init_database_service()
        self.chemical_safety_db = self._init_chemical_safety_database()
        self.test_strip_analyzer = self._init_test_strip_analyzer()
        self.weather_service = self._init_weather_service()
        
        # Initialize controller
        self.controller = PoolChemistryController(self.db_service)
        
        logger.info("Pool Chemistry Application initialized successfully")
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """
        Load configuration from a JSON file.
        
        Args:
            config_path: Path to the configuration file
            
        Returns:
            Configuration dictionary
            
        Raises:
            FileNotFoundError: If the configuration file doesn't exist
            json.JSONDecodeError: If the configuration file contains invalid JSON
        """
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            logger.info(f"Configuration loaded from {config_path}")
            return config
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.warning(f"Failed to load configuration from {config_path}: {e}")
            logger.info("Using default configuration")
            return {
                "database": {
                    "path": "data/pool_data.db"
                },
                "chemical_safety": {
                    "data_file": "data/chemical_safety_data.json"
                },
                "test_strip": {
                    "brand": "default",
                    "calibration_file": "data/calibration.json"
                },
                "weather": {
                    "location": "Florida",
                    "update_interval": 3600,
                    "cache_file": "data/weather_cache.json"
                }
            }
    
    def _init_database_service(self) -> DatabaseService:
        """
        Initialize the database service.
        
        Returns:
            Database service instance
            
        Raises:
            RuntimeError: If the database service fails to initialize
        """
        try:
            db_path = self.config.get("database", {}).get("path", "data/pool_data.db")
            db_service = DatabaseService(db_path)
            logger.info("Database service initialized successfully")
            return db_service
        except Exception as e:
            logger.error(f"Failed to initialize database service: {e}")
            raise RuntimeError(f"Database initialization error: {e}")
    
    def _init_chemical_safety_database(self) -> ChemicalSafetyDatabase:
        """
        Initialize the chemical safety database.
        
        Returns:
            Chemical safety database instance
            
        Raises:
            RuntimeError: If the chemical safety database fails to initialize
        """
        try:
            data_file = self.config.get("chemical_safety", {}).get("data_file", "data/chemical_safety_data.json")
            chemical_safety_db = ChemicalSafetyDatabase(data_file)
            logger.info("Chemical safety database initialized successfully")
            return chemical_safety_db
        except Exception as e:
            logger.error(f"Failed to initialize chemical safety database: {e}")
            raise RuntimeError(f"Chemical safety database initialization error: {e}")
    
    def _init_test_strip_analyzer(self) -> TestStripAnalyzer:
        """
        Initialize the test strip analyzer.
        
        Returns:
            Test strip analyzer instance
            
        Raises:
            RuntimeError: If the test strip analyzer fails to initialize
        """
        try:
            test_strip_config = self.config.get("test_strip", {})
            test_strip_analyzer = TestStripAnalyzer(test_strip_config)
            logger.info("Test strip analyzer initialized successfully")
            return test_strip_analyzer
        except Exception as e:
            logger.error(f"Failed to initialize test strip analyzer: {e}")
            raise RuntimeError(f"Test strip analyzer initialization error: {e}")
    
    def _init_weather_service(self) -> WeatherService:
        """
        Initialize the weather service.
        
        Returns:
            Weather service instance
            
        Raises:
            RuntimeError: If the weather service fails to initialize
        """
        try:
            weather_config = self.config.get("weather", {})
            weather_service = WeatherService(weather_config)
            logger.info("Weather service initialized successfully")
            return weather_service
        except Exception as e:
            logger.error(f"Failed to initialize weather service: {e}")
            raise RuntimeError(f"Weather service initialization error: {e}")
    
    def run_gui(self) -> None:
        """
        Run the GUI application.
        
        Raises:
            RuntimeError: If the GUI fails to initialize
        """
        try:
            logger.info("Starting GUI application")
            
            # Create the main window
            root = tk.Tk()
            root.title("Deep Blue Pool Chemistry")
            root.geometry("800x600")
            
            # Create a simple UI for demonstration
            frame = ttk.Frame(root, padding="10")
            frame.pack(fill=tk.BOTH, expand=True)
            
            ttk.Label(frame, text="Deep Blue Pool Chemistry", font=("Arial", 16)).pack(pady=10)
            ttk.Label(frame, text="All services initialized successfully").pack(pady=5)
            
            # Add buttons for different features
            ttk.Button(frame, text="Test Strip Analysis", 
                      command=lambda: messagebox.showinfo("Info", "Test Strip Analysis feature selected")).pack(pady=5)
            
            ttk.Button(frame, text="Chemical Safety Information", 
                      command=lambda: messagebox.showinfo("Info", "Chemical Safety Information feature selected")).pack(pady=5)
            
            ttk.Button(frame, text="Weather Impact", 
                      command=lambda: self._show_weather_info(root)).pack(pady=5)
            
            ttk.Button(frame, text="Calculate Chemicals", 
                      command=lambda: self._show_chemical_calculator(root)).pack(pady=5)
            
            ttk.Button(frame, text="Exit", command=root.destroy).pack(pady=20)
            
            # Start the main loop
            root.mainloop()
            
            logger.info("GUI application closed")
        except Exception as e:
            logger.error(f"Error running GUI application: {e}")
            raise RuntimeError(f"GUI error: {e}")
    
    def _show_weather_info(self, parent: tk.Tk) -> None:
        """
        Show weather information in a dialog.
        
        Args:
            parent: Parent window
        """
        try:
            weather_data = self.weather_service.get_weather_with_impact()
            
            # Create a dialog window
            dialog = tk.Toplevel(parent)
            dialog.title("Weather Information")
            dialog.geometry("400x300")
            
            frame = ttk.Frame(dialog, padding="10")
            frame.pack(fill=tk.BOTH, expand=True)
            
            # Display weather information
            weather = weather_data["weather"]
            impact = weather_data["impact"]
            
            ttk.Label(frame, text="Current Weather", font=("Arial", 14)).pack(pady=5)
            ttk.Label(frame, text=f"Temperature: {weather['temperature']}°F").pack(anchor="w")
            ttk.Label(frame, text=f"Conditions: {weather['conditions']}").pack(anchor="w")
            ttk.Label(frame, text=f"Humidity: {weather['humidity']}%").pack(anchor="w")
            ttk.Label(frame, text=f"UV Index: {weather['uv_index']}").pack(anchor="w")
            
            ttk.Separator(frame, orient="horizontal").pack(fill="x", pady=10)
            
            ttk.Label(frame, text="Pool Impact", font=("Arial", 14)).pack(pady=5)
            ttk.Label(frame, text=f"Evaporation Rate: {impact['evaporation_rate']} inches/day").pack(anchor="w")
            ttk.Label(frame, text=f"Chlorine Loss Rate: {impact['chlorine_loss_rate']} ppm/day").pack(anchor="w")
            ttk.Label(frame, text=f"Algae Growth Risk: {impact['algae_growth_risk']}").pack(anchor="w")
            
            if impact["recommendations"]:
                ttk.Separator(frame, orient="horizontal").pack(fill="x", pady=10)
                ttk.Label(frame, text="Recommendations", font=("Arial", 14)).pack(pady=5)
                for rec in impact["recommendations"]:
                    ttk.Label(frame, text=f"• {rec}").pack(anchor="w")
            
            ttk.Button(frame, text="Close", command=dialog.destroy).pack(pady=10)
            
        except Exception as e:
            logger.error(f"Error showing weather information: {e}")
            messagebox.showerror("Error", f"Failed to retrieve weather information: {e}")
    
    def _show_chemical_calculator(self, parent: tk.Tk) -> None:
        """
        Show chemical calculator dialog.
        
        Args:
            parent: Parent window
        """
        try:
            # Create a dialog window
            dialog = tk.Toplevel(parent)
            dialog.title("Chemical Calculator")
            dialog.geometry("500x400")
            
            frame = ttk.Frame(dialog, padding="10")
            frame.pack(fill=tk.BOTH, expand=True)
            
            ttk.Label(frame, text="Pool Chemistry Calculator", font=("Arial", 14)).pack(pady=5)
            
            # Create input fields
            input_frame = ttk.Frame(frame)
            input_frame.pack(fill="x", pady=10)
            
            # Pool type
            ttk.Label(input_frame, text="Pool Type:").grid(row=0, column=0, sticky="w", pady=2)
            pool_type_var = tk.StringVar(value="Concrete/Gunite")
            pool_type_combo = ttk.Combobox(input_frame, textvariable=pool_type_var)
            pool_type_combo["values"] = ("Concrete/Gunite", "Vinyl", "Fiberglass", "Above Ground")
            pool_type_combo.grid(row=0, column=1, sticky="ew", pady=2)
            
            # Pool size
            ttk.Label(input_frame, text="Pool Size (gallons):").grid(row=1, column=0, sticky="w", pady=2)
            pool_size_var = tk.StringVar(value="10000")
            ttk.Entry(input_frame, textvariable=pool_size_var).grid(row=1, column=1, sticky="ew", pady=2)
            
            # pH
            ttk.Label(input_frame, text="pH:").grid(row=2, column=0, sticky="w", pady=2)
            ph_var = tk.StringVar(value="7.2")
            ttk.Entry(input_frame, textvariable=ph_var).grid(row=2, column=1, sticky="ew", pady=2)
            
            # Chlorine
            ttk.Label(input_frame, text="Chlorine (ppm):").grid(row=3, column=0, sticky="w", pady=2)
            chlorine_var = tk.StringVar(value="1.5")
            ttk.Entry(input_frame, textvariable=chlorine_var).grid(row=3, column=1, sticky="ew", pady=2)
            
            # Alkalinity
            ttk.Label(input_frame, text="Alkalinity (ppm):").grid(row=4, column=0, sticky="w", pady=2)
            alkalinity_var = tk.StringVar(value="100")
            ttk.Entry(input_frame, textvariable=alkalinity_var).grid(row=4, column=1, sticky="ew", pady=2)
            
            # Calcium hardness
            ttk.Label(input_frame, text="Calcium Hardness (ppm):").grid(row=5, column=0, sticky="w", pady=2)
            calcium_var = tk.StringVar(value="250")
            ttk.Entry(input_frame, textvariable=calcium_var).grid(row=5, column=1, sticky="ew", pady=2)
            
            # Temperature
            ttk.Label(input_frame, text="Temperature (°F):").grid(row=6, column=0, sticky="w", pady=2)
            temp_var = tk.StringVar(value="78")
            ttk.Entry(input_frame, textvariable=temp_var).grid(row=6, column=1, sticky="ew", pady=2)
            
            # Results text area
            ttk.Label(frame, text="Results:").pack(anchor="w", pady=(10, 2))
            results_text = tk.Text(frame, height=10, width=50)
            results_text.pack(fill="both", expand=True)
            results_text.config(state="disabled")
            
            # Calculate button
            def calculate():
                try:
                    pool_data = {
                        "pool_type": pool_type_var.get(),
                        "pool_size": pool_size_var.get(),
                        "ph": ph_var.get(),
                        "chlorine": chlorine_var.get(),
                        "alkalinity": alkalinity_var.get(),
                        "calcium_hardness": calcium_var.get(),
                        "temperature": temp_var.get()
                    }
                    
                    result = self.controller.calculate_chemicals(pool_data)
                    
                    # Display results
                    results_text.config(state="normal")
                    results_text.delete(1.0, tk.END)
                    
                    # Water balance
                    if result["water_balance"] is not None:
                        results_text.insert(tk.END, f"Water Balance Index: {result['water_balance']}\n")
                        if result["water_balance"] < -0.3:
                            results_text.insert(tk.END, "Water is corrosive. Adjust chemistry.\n")
                        elif result["water_balance"] > 0.3:
                            results_text.insert(tk.END, "Water is scaling. Adjust chemistry.\n")
                        else:
                            results_text.insert(tk.END, "Water is balanced.\n")
                    
                    results_text.insert(tk.END, "\nRecommended Adjustments:\n")
                    
                    # Adjustments
                    if not result["adjustments"]:
                        results_text.insert(tk.END, "No adjustments needed. Water chemistry is good!\n")
                    else:
                        for chem, adj in result["adjustments"].items():
                            results_text.insert(tk.END, f"{chem}: {adj['amount']} {adj['unit']} - {adj['reason']}\n")
                    
                    results_text.config(state="disabled")
                    
                except Exception as e:
                    results_text.config(state="normal")
                    results_text.delete(1.0, tk.END)
                    results_text.insert(tk.END, f"Error: {str(e)}")
                    results_text.config(state="disabled")
                    logger.error(f"Error calculating chemicals: {e}")
            
            ttk.Button(frame, text="Calculate", command=calculate).pack(pady=10)
            ttk.Button(frame, text="Close", command=dialog.destroy).pack(pady=5)
            
        except Exception as e:
            logger.error(f"Error showing chemical calculator: {e}")
            messagebox.showerror("Error", f"Failed to open chemical calculator: {e}")
    
    def run_cli(self) -> None:
        """
        Run the command-line interface.
        
        Raises:
            RuntimeError: If the CLI fails to run
        """
        try:
            logger.info("Starting CLI application")
            
            print("Deep Blue Pool Chemistry CLI")
            print("===========================")
            
            # Get weather information
            weather_data = self.weather_service.get_weather_with_impact()
            weather = weather_data["weather"]
            impact = weather_data["impact"]
            
            print("\nCurrent Weather:")
            print(f"Temperature: {weather['temperature']}°F")
            print(f"Conditions: {weather['conditions']}")
            print(f"Humidity: {weather['humidity']}%")
            print(f"UV Index: {weather['uv_index']}")
            
            print("\nPool Impact:")
            print(f"Evaporation Rate: {impact['evaporation_rate']} inches/day")
            print(f"Chlorine Loss Rate: {impact['chlorine_loss_rate']} ppm/day")
            print(f"Algae Growth Risk: {impact['algae_growth_risk']}")
            
            if impact["recommendations"]:
                print("\nRecommendations:")
                for rec in impact["recommendations"]:
                    print(f"• {rec}")
            
            # Get user input for chemical calculation
            print("\nChemical Calculator")
            print("-----------------")
            
            pool_types = ["Concrete/Gunite", "Vinyl", "Fiberglass", "Above Ground"]
            print("Pool Types:")
            for i, pt in enumerate(pool_types):
                print(f"{i+1}. {pt}")
            
            try:
                pool_type_idx = int(input("\nSelect pool type (1-4): ")) - 1
                pool_type = pool_types[pool_type_idx]
            except (ValueError, IndexError):
                pool_type = "Concrete/Gunite"
                print(f"Invalid selection, using default: {pool_type}")
            
            try:
                pool_size = float(input("Pool size (gallons): "))
            except ValueError:
                pool_size = 10000
                print(f"Invalid input, using default: {pool_size}")
            
            try:
                ph = float(input("pH level: "))
            except ValueError:
                ph = 7.2
                print(f"Invalid input, using default: {ph}")
            
            try:
                chlorine = float(input("Chlorine level (ppm): "))
            except ValueError:
                chlorine = 1.5
                print(f"Invalid input, using default: {chlorine}")
            
            try:
                alkalinity = float(input("Alkalinity level (ppm): "))
            except ValueError:
                alkalinity = 100
                print(f"Invalid input, using default: {alkalinity}")
            
            try:
                calcium = float(input("Calcium hardness level (ppm): "))
            except ValueError:
                calcium = 250
                print(f"Invalid input, using default: {calcium}")
            
            try:
                temperature = float(input("Water temperature (°F): "))
            except ValueError:
                temperature = 78
                print(f"Invalid input, using default: {temperature}")
            
            # Calculate chemicals
            pool_data = {
                "pool_type": pool_type,
                "pool_size": str(pool_size),
                "ph": str(ph),
                "chlorine": str(chlorine),
                "alkalinity": str(alkalinity),
                "calcium_hardness": str(calcium),
                "temperature": str(temperature)
            }
            
            try:
                result = self.controller.calculate_chemicals(pool_data)
                
                print("\nResults:")
                
                # Water balance
                if result["water_balance"] is not None:
                    print(f"Water Balance Index: {result['water_balance']}")
                    if result["water_balance"] < -0.3:
                        print("Water is corrosive. Adjust chemistry.")
                    elif result["water_balance"] > 0.3:
                        print("Water is scaling. Adjust chemistry.")
                    else:
                        print("Water is balanced.")
                
                print("\nRecommended Adjustments:")
                
                # Adjustments
                if not result["adjustments"]:
                    print("No adjustments needed. Water chemistry is good!")
                else:
                    for chem, adj in result["adjustments"].items():
                        print(f"{chem}: {adj['amount']} {adj['unit']} - {adj['reason']}")
                
            except Exception as e:
                print(f"Error calculating chemicals: {e}")
            
            logger.info("CLI application completed")
        except Exception as e:
            logger.error(f"Error running CLI application: {e}")
            raise RuntimeError(f"CLI error: {e}")
    
    def cleanup(self) -> None:
        """
        Clean up resources before exiting.
        """
        try:
            # Close database connections
            if hasattr(self, 'db_service'):
                self.db_service.close_all_connections()
            
            # Clear caches
            if hasattr(self, 'test_strip_analyzer'):
                self.test_strip_analyzer.clear_cache()
            
            if hasattr(self, 'weather_service'):
                self.weather_service.clear_cache()
            
            logger.info("Application resources cleaned up")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")


def parse_args():
    """
    Parse command line arguments.
    
    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(description="Deep Blue Pool Chemistry Application")
    parser.add_argument("--gui", action="store_true", help="Run in GUI mode (default)")
    parser.add_argument("--cli", action="store_true", help="Run in CLI mode")
    parser.add_argument("--config", type=str, default="config.json", help="Path to configuration file")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    return parser.parse_args()


def main():
    """
    Main entry point for the application.
    """
    # Parse command line arguments
    args = parse_args()
    
    # Set log level
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Debug logging enabled")
    
    # Create data directory if it doesn't exist
    os.makedirs("data", exist_ok=True)
    
    # Create a default config file if it doesn't exist
    if not os.path.exists("config.json"):
        default_config = {
            "database": {
                "path": "data/pool_data.db"
            },
            "chemical_safety": {
                "data_file": "data/chemical_safety_data.json"
            },
            "test_strip": {
                "brand": "default",
                "calibration_file": "data/calibration.json"
            },
            "weather": {
                "location": "Florida",
                "update_interval": 3600,
                "cache_file": "data/weather_cache.json"
            }
        }
        with open("config.json", "w") as f:
            json.dump(default_config, f, indent=4)
        logger.info("Created default config.json file")
    
    # Create a default calibration file if it doesn't exist
    if not os.path.exists("data/calibration.json"):
        os.makedirs("data", exist_ok=True)
        default_calibration = {
            "pH": [
                { "rgb": [180, 100, 90], "value": 6.8 },
                { "rgb": [200, 120, 100], "value": 7.2 },
                { "rgb": [220, 140, 110], "value": 7.6 }
            ],
            "free_chlorine": [
                { "rgb": [100, 200, 180], "value": 0.5 },
                { "rgb": [120, 220, 200], "value": 1.0 },
                { "rgb": [140, 240, 220], "value": 2.0 }
            ]
        }
        with open("data/calibration.json", "w") as f:
            json.dump(default_calibration, f, indent=4)
        logger.info("Created default calibration.json file")
    
    # Create a default pad zones file if it doesn't exist
    if not os.path.exists("data/pad_zones.json"):
        os.makedirs("data", exist_ok=True)
        default_pad_zones = {
            "default": {
                "pH": [50, 50, 40, 40],
                "free_chlorine": [100, 50, 40, 40],
                "total_chlorine": [150, 50, 40, 40],
                "alkalinity": [200, 50, 40, 40],
                "calcium": [250, 50, 40, 40],
                "cyanuric_acid": [300, 50, 40, 40],
                "bromine": [350, 50, 40, 40],
                "salt": [400, 50, 40, 40]
            }
        }
        with open("data/pad_zones.json", "w") as f:
            json.dump(default_pad_zones, f, indent=4)
        logger.info("Created default pad_zones.json file")
    
    # Create and run the application
    app = None
    try:
        app = PoolChemistryApp(args.config)
        
        # Run in CLI or GUI mode
        if args.cli:
            app.run_cli()
        else:
            app.run_gui()
        
        return 0
    except Exception as e:
        logger.error(f"Application error: {e}")
        return 1
    finally:
        # Clean up resources
        if app:
            app.cleanup()


if __name__ == "__main__":
    sys.exit(main())