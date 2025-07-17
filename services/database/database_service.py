
"""
Database service module for the Deep Blue Pool Chemistry application.

This module provides database access and operations for storing and retrieving
pool chemistry data, maintenance logs, and chemical additions.
"""

import logging
import sqlite3
import json
import threading
import os
from datetime import datetime
from typing import Dict, List, Optional, Any, Union

# Configure logger
logger = logging.getLogger("database_service")


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
            from datetime import timedelta
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
