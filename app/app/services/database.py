
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
        
        # Ensure data directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
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
            
            # Create customers table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT,
                phone TEXT,
                address TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            ''')
            
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
            
            # Create chemical readings table with customer_id foreign key
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS chemical_readings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER,
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
                source TEXT,
                FOREIGN KEY (customer_id) REFERENCES customers(id)
            )
            ''')
            
            # Create pool_info table with customer_id foreign key
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS pool_info (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER NOT NULL,
                pool_type TEXT,
                pool_size TEXT,
                pool_shape TEXT,
                pool_material TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (customer_id) REFERENCES customers(id)
            )
            ''')
            
            conn.commit()
            logger.info("Database initialized successfully")
        except sqlite3.Error as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
    
    # Customer Management Methods
    
    def add_customer(self, name: str, email: str = "", phone: str = "", address: str = "") -> int:
        """
        Add a new customer to the database.
        
        Args:
            name: Customer name
            email: Customer email
            phone: Customer phone number
            address: Customer address
            
        Returns:
            The ID of the newly created customer
            
        Raises:
            sqlite3.Error: If there's an error inserting data
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            timestamp = datetime.now().isoformat()
            
            cursor.execute(
                "INSERT INTO customers (name, email, phone, address, created_at, updated_at) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (name, email, phone, address, timestamp, timestamp)
            )
            
            conn.commit()
            customer_id = cursor.lastrowid
            logger.info(f"Added new customer with ID {customer_id}: {name}")
            return customer_id
        except sqlite3.Error as e:
            logger.error(f"Failed to add customer: {e}")
            raise
    
    def update_customer(self, customer_id: int, name: str = None, email: str = None, 
                       phone: str = None, address: str = None) -> bool:
        """
        Update customer information.
        
        Args:
            customer_id: ID of the customer to update
            name: New customer name (or None to keep current)
            email: New customer email (or None to keep current)
            phone: New customer phone number (or None to keep current)
            address: New customer address (or None to keep current)
            
        Returns:
            True if successful, False otherwise
            
        Raises:
            sqlite3.Error: If there's an error updating data
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Get current customer data
            cursor.execute("SELECT name, email, phone, address FROM customers WHERE id = ?", (customer_id,))
            row = cursor.fetchone()
            
            if not row:
                logger.error(f"Customer with ID {customer_id} not found")
                return False
            
            current_name, current_email, current_phone, current_address = row
            
            # Update with new values or keep current ones
            new_name = name if name is not None else current_name
            new_email = email if email is not None else current_email
            new_phone = phone if phone is not None else current_phone
            new_address = address if address is not None else current_address
            
            timestamp = datetime.now().isoformat()
            
            cursor.execute(
                "UPDATE customers SET name = ?, email = ?, phone = ?, address = ?, updated_at = ? "
                "WHERE id = ?",
                (new_name, new_email, new_phone, new_address, timestamp, customer_id)
            )
            
            conn.commit()
            logger.info(f"Updated customer with ID {customer_id}")
            return True
        except sqlite3.Error as e:
            logger.error(f"Failed to update customer: {e}")
            return False
    
    def delete_customer(self, customer_id: int) -> bool:
        """
        Delete a customer from the database.
        
        Args:
            customer_id: ID of the customer to delete
            
        Returns:
            True if successful, False otherwise
            
        Raises:
            sqlite3.Error: If there's an error deleting data
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM customers WHERE id = ?", (customer_id,))
            
            if cursor.rowcount == 0:
                logger.error(f"Customer with ID {customer_id} not found")
                return False
            
            conn.commit()
            logger.info(f"Deleted customer with ID {customer_id}")
            return True
        except sqlite3.Error as e:
            logger.error(f"Failed to delete customer: {e}")
            return False
    
    def get_customer(self, customer_id: int) -> Optional[Dict[str, Any]]:
        """
        Get customer information by ID.
        
        Args:
            customer_id: ID of the customer to retrieve
            
        Returns:
            Dictionary containing customer information, or None if not found
            
        Raises:
            sqlite3.Error: If there's an error retrieving data
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT id, name, email, phone, address, created_at, updated_at "
                "FROM customers WHERE id = ?",
                (customer_id,)
            )
            
            row = cursor.fetchone()
            
            if not row:
                return None
            
            return {
                "id": row[0],
                "name": row[1],
                "email": row[2],
                "phone": row[3],
                "address": row[4],
                "created_at": row[5],
                "updated_at": row[6]
            }
        except sqlite3.Error as e:
            logger.error(f"Failed to get customer: {e}")
            return None
    
    def get_all_customers(self) -> List[Dict[str, Any]]:
        """
        Get all customers from the database.
        
        Returns:
            List of dictionaries containing customer information
            
        Raises:
            sqlite3.Error: If there's an error retrieving data
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT id, name, email, phone, address, created_at, updated_at "
                "FROM customers ORDER BY name"
            )
            
            rows = cursor.fetchall()
            
            return [
                {
                    "id": row[0],
                    "name": row[1],
                    "email": row[2],
                    "phone": row[3],
                    "address": row[4],
                    "created_at": row[5],
                    "updated_at": row[6]
                }
                for row in rows
            ]
        except sqlite3.Error as e:
            logger.error(f"Failed to get customers: {e}")
            return []
    
    def search_customers(self, search_term: str) -> List[Dict[str, Any]]:
        """
        Search for customers by name, email, or phone.
        
        Args:
            search_term: Term to search for
            
        Returns:
            List of dictionaries containing customer information
            
        Raises:
            sqlite3.Error: If there's an error retrieving data
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            search_pattern = f"%{search_term}%"
            
            cursor.execute(
                "SELECT id, name, email, phone, address, created_at, updated_at "
                "FROM customers "
                "WHERE name LIKE ? OR email LIKE ? OR phone LIKE ? "
                "ORDER BY name",
                (search_pattern, search_pattern, search_pattern)
            )
            
            rows = cursor.fetchall()
            
            return [
                {
                    "id": row[0],
                    "name": row[1],
                    "email": row[2],
                    "phone": row[3],
                    "address": row[4],
                    "created_at": row[5],
                    "updated_at": row[6]
                }
                for row in rows
            ]
        except sqlite3.Error as e:
            logger.error(f"Failed to search customers: {e}")
            return []
    
    # Pool Info Methods
    
    def add_pool_info(self, customer_id: int, pool_type: str, pool_size: str, 
                     pool_shape: str = "", pool_material: str = "") -> int:
        """
        Add pool information for a customer.
        
        Args:
            customer_id: ID of the customer
            pool_type: Type of pool (e.g., "Inground", "Above Ground")
            pool_size: Size of pool in gallons
            pool_shape: Shape of pool (e.g., "Rectangle", "Oval")
            pool_material: Material of pool (e.g., "Concrete", "Vinyl")
            
        Returns:
            The ID of the newly created pool info record
            
        Raises:
            sqlite3.Error: If there's an error inserting data
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            timestamp = datetime.now().isoformat()
            
            cursor.execute(
                "INSERT INTO pool_info (customer_id, pool_type, pool_size, pool_shape, pool_material, created_at, updated_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)",
                (customer_id, pool_type, pool_size, pool_shape, pool_material, timestamp, timestamp)
            )
            
            conn.commit()
            pool_info_id = cursor.lastrowid
            logger.info(f"Added pool info with ID {pool_info_id} for customer {customer_id}")
            return pool_info_id
        except sqlite3.Error as e:
            logger.error(f"Failed to add pool info: {e}")
            raise
    
    def get_customer_pool_info(self, customer_id: int) -> Optional[Dict[str, Any]]:
        """
        Get pool information for a customer.
        
        Args:
            customer_id: ID of the customer
            
        Returns:
            Dictionary containing pool information, or None if not found
            
        Raises:
            sqlite3.Error: If there's an error retrieving data
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT id, pool_type, pool_size, pool_shape, pool_material, created_at, updated_at "
                "FROM pool_info WHERE customer_id = ?",
                (customer_id,)
            )
            
            row = cursor.fetchone()
            
            if not row:
                return None
            
            return {
                "id": row[0],
                "pool_type": row[1],
                "pool_size": row[2],
                "pool_shape": row[3],
                "pool_material": row[4],
                "created_at": row[5],
                "updated_at": row[6]
            }
        except sqlite3.Error as e:
            logger.error(f"Failed to get pool info: {e}")
            return None
    
    # Enhanced Chemical Readings Methods
    
    def insert_reading(self, data: Dict[str, Any], customer_id: Optional[int] = None) -> bool:
        """
        Insert chemical reading into the database.
        
        Args:
            data: Dictionary containing chemical reading data
            customer_id: Optional ID of the customer associated with this reading
            
        Returns:
            True if successful, False otherwise
            
        Raises:
            sqlite3.Error: If there's an error inserting data
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            values = (
                customer_id,
                datetime.now().isoformat(),
                data.get("pH"), data.get("free_chlorine"), data.get("total_chlorine"),
                data.get("alkalinity"), data.get("calcium"), data.get("cyanuric_acid"),
                data.get("bromine"), data.get("salt"), data.get("temperature"),
                data.get("water_volume"), data.get("source")
            )
            
            cursor.execute("""
                INSERT INTO chemical_readings (
                    customer_id, timestamp, pH, free_chlorine, total_chlorine, alkalinity,
                    calcium, cyanuric_acid, bromine, salt, temperature,
                    water_volume, source
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, values)
            
            conn.commit()
            return True
        except sqlite3.Error as e:
            logger.error(f"Failed to insert reading: {e}")
            return False
    
    def get_customer_readings(self, customer_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get chemical readings for a specific customer.
        
        Args:
            customer_id: ID of the customer
            limit: Maximum number of readings to retrieve
            
        Returns:
            List of dictionaries containing reading data
            
        Raises:
            sqlite3.Error: If there's an error retrieving data
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT * FROM chemical_readings WHERE customer_id = ? ORDER BY timestamp DESC LIMIT ?",
                (customer_id, limit)
            )
            
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            
            return [dict(zip(columns, row)) for row in rows]
        except sqlite3.Error as e:
            logger.error(f"Failed to get customer readings: {e}")
            return []
    
    # Original Methods
    
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
    
    def get_recent_readings(self, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Get recent chemical readings from the database.
        
        Args:
            limit: Maximum number of readings to retrieve
            
        Returns:
            List of dictionaries containing reading data
            
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
            
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            
            return [dict(zip(columns, row)) for row in rows]
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
