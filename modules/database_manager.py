# modules/database_manager.py
"""
Database Manager Module
Handles database operations for the Pool Chemistry Manager
"""

import os
import sqlite3
import logging
from datetime import datetime

class DatabaseManager:
    """Database manager for the Pool Chemistry Manager application"""
    
    def __init__(self, config):
        """Initialize the database manager"""
        self.logger = logging.getLogger(__name__)
        self.config = config
        self.db_type = config["database"]["type"]
        self.db_path = config["database"]["path"]
        self.connection = None
        self.cursor = None
    
    def connect(self):
        """Connect to the database"""
        try:
            if self.db_type == "sqlite":
                # Create directory if it doesn't exist
                os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
                
                self.connection = sqlite3.connect(self.db_path)
                self.cursor = self.connection.cursor()
                self.logger.info(f"Connected to SQLite database: {self.db_path}")
                return True
            else:
                self.logger.error(f"Unsupported database type: {self.db_type}")
                return False
        except Exception as e:
            self.logger.error(f"Error connecting to database: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from the database"""
        try:
            if self.connection:
                self.connection.close()
                self.connection = None
                self.cursor = None
                self.logger.info("Disconnected from database")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Error disconnecting from database: {e}")
            return False
    
    def initialize_database(self):
        """Initialize the database schema"""
        try:
            if not self.connection:
                self.connect()
            
            # Create customers table
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT,
                email TEXT,
                address TEXT,
                pool_size INTEGER,
                pool_type TEXT,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            
            # Create water_tests table
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS water_tests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER,
                date_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ph REAL,
                chlorine REAL,
                alkalinity INTEGER,
                hardness INTEGER,
                cyanuric_acid INTEGER,
                notes TEXT,
                FOREIGN KEY (customer_id) REFERENCES customers (id)
            )
            ''')
            
            # Create chemical_additions table
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS chemical_additions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER,
                date_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                chemical_type TEXT,
                amount REAL,
                unit TEXT,
                notes TEXT,
                FOREIGN KEY (customer_id) REFERENCES customers (id)
            )
            ''')
            
            self.connection.commit()
            self.logger.info("Database schema initialized")
            return True
        except Exception as e:
            self.logger.error(f"Error initializing database: {e}")
            return False
    
    def backup_database(self, backup_path=None):
        """Backup the database"""
        try:
            if not backup_path:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = f"data/backups/pool_chemistry_{timestamp}.db"
            
            # Create backup directory if it doesn't exist
            os.makedirs(os.path.dirname(backup_path), exist_ok=True)
            
            if self.db_type == "sqlite":
                # For SQLite, we can just copy the file
                import shutil
                shutil.copy2(self.db_path, backup_path)
                self.logger.info(f"Database backed up to {backup_path}")
                return True
            else:
                self.logger.error(f"Backup not implemented for database type: {self.db_type}")
                return False
        except Exception as e:
            self.logger.error(f"Error backing up database: {e}")
            return False
    
    def restore_database(self, backup_path):
        """Restore the database from a backup"""
        try:
            if self.db_type == "sqlite":
                # Disconnect from current database
                self.disconnect()
                
                # Copy backup file to database path
                import shutil
                shutil.copy2(backup_path, self.db_path)
                
                # Reconnect to database
                self.connect()
                
                self.logger.info(f"Database restored from {backup_path}")
                return True
            else:
                self.logger.error(f"Restore not implemented for database type: {self.db_type}")
                return False
        except Exception as e:
            self.logger.error(f"Error restoring database: {e}")
            return False
    
    # Customer methods
    def add_customer(self, customer_data):
        """Add a new customer to the database"""
        try:
            if not self.connection:
                self.connect()
            
            self.cursor.execute('''
            INSERT INTO customers (name, phone, email, address, pool_size, pool_type, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                customer_data['name'],
                customer_data['phone'],
                customer_data['email'],
                customer_data['address'],
                customer_data['pool_size'],
                customer_data['pool_type'],
                customer_data['notes']
            ))
            
            self.connection.commit()
            customer_id = self.cursor.lastrowid
            self.logger.info(f"Added customer: {customer_data['name']} (ID: {customer_id})")
            return customer_id
        except Exception as e:
            self.logger.error(f"Error adding customer: {e}")
            return None
    
    def update_customer(self, customer_id, customer_data):
        """Update an existing customer"""
        try:
            if not self.connection:
                self.connect()
            
            self.cursor.execute('''
            UPDATE customers
            SET name = ?, phone = ?, email = ?, address = ?, pool_size = ?, pool_type = ?, notes = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            ''', (
                customer_data['name'],
                customer_data['phone'],
                customer_data['email'],
                customer_data['address'],
                customer_data['pool_size'],
                customer_data['pool_type'],
                customer_data['notes'],
                customer_id
            ))
            
            self.connection.commit()
            self.logger.info(f"Updated customer ID: {customer_id}")
            return True
        except Exception as e:
            self.logger.error(f"Error updating customer: {e}")
            return False
    
    def delete_customer(self, customer_id):
        """Delete a customer"""
        try:
            if not self.connection:
                self.connect()
            
            # Delete related records first
            self.cursor.execute("DELETE FROM water_tests WHERE customer_id = ?", (customer_id,))
            self.cursor.execute("DELETE FROM chemical_additions WHERE customer_id = ?", (customer_id,))
            
            # Delete customer
            self.cursor.execute("DELETE FROM customers WHERE id = ?", (customer_id,))
            
            self.connection.commit()
            self.logger.info(f"Deleted customer ID: {customer_id}")
            return True
        except Exception as e:
            self.logger.error(f"Error deleting customer: {e}")
            return False
    
    def get_all_customers(self):
        """Get all customers"""
        try:
            if not self.connection:
                self.connect()
            
            self.cursor.execute("SELECT * FROM customers ORDER BY name")
            columns = [desc[0] for desc in self.cursor.description]
            customers = []
            
            for row in self.cursor.fetchall():
                customer = dict(zip(columns, row))
                customers.append(customer)
            
            return customers
        except Exception as e:
            self.logger.error(f"Error getting customers: {e}")
            return []
    
    def get_customer(self, customer_id):
        """Get a customer by ID"""
        try:
            if not self.connection:
                self.connect()
            
            self.cursor.execute("SELECT * FROM customers WHERE id = ?", (customer_id,))
            columns = [desc[0] for desc in self.cursor.description]
            row = self.cursor.fetchone()
            
            if row:
                customer = dict(zip(columns, row))
                return customer
            else:
                return None
        except Exception as e:
            self.logger.error(f"Error getting customer: {e}")
            return None
    
    # Water test methods
    def add_water_test(self, test_data):
        """Add a new water test"""
        try:
            if not self.connection:
                self.connect()
            
            self.cursor.execute('''
            INSERT INTO water_tests (customer_id, ph, chlorine, alkalinity, hardness, cyanuric_acid, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                test_data.get('customer_id'),
                test_data.get('ph'),
                test_data.get('chlorine'),
                test_data.get('alkalinity'),
                test_data.get('hardness'),
                test_data.get('cyanuric_acid'),
                test_data.get('notes', '')
            ))
            
            self.connection.commit()
            test_id = self.cursor.lastrowid
            self.logger.info(f"Added water test ID: {test_id}")
            return test_id
        except Exception as e:
            self.logger.error(f"Error adding water test: {e}")
            return None
    
    def get_water_tests(self, customer_id=None, limit=None):
        """Get water tests, optionally filtered by customer"""
        try:
            if not self.connection:
                self.connect()
            
            query = "SELECT * FROM water_tests"
            params = []
            
            if customer_id:
                query += " WHERE customer_id = ?"
                params.append(customer_id)
            
            query += " ORDER BY date_time DESC"
            
            if limit:
                query += " LIMIT ?"
                params.append(limit)
            
            self.cursor.execute(query, params)
            columns = [desc[0] for desc in self.cursor.description]
            tests = []
            
            for row in self.cursor.fetchall():
                test = dict(zip(columns, row))
                tests.append(test)
            
            return tests
        except Exception as e:
            self.logger.error(f"Error getting water tests: {e}")
            return []
    
    # Chemical addition methods
    def add_chemical_addition(self, addition_data):
        """Add a new chemical addition record"""
        try:
            if not self.connection:
                self.connect()
            
            self.cursor.execute('''
            INSERT INTO chemical_additions (customer_id, chemical_type, amount, unit, notes)
            VALUES (?, ?, ?, ?, ?)
            ''', (
                addition_data.get('customer_id'),
                addition_data.get('chemical_type'),
                addition_data.get('amount'),
                addition_data.get('unit'),
                addition_data.get('notes', '')
            ))
            
            self.connection.commit()
            addition_id = self.cursor.lastrowid
            self.logger.info(f"Added chemical addition ID: {addition_id}")
            return addition_id
        except Exception as e:
            self.logger.error(f"Error adding chemical addition: {e}")
            return None
    
    def get_chemical_additions(self, customer_id=None, limit=None):
        """Get chemical additions, optionally filtered by customer"""
        try:
            if not self.connection:
                self.connect()
            
            query = "SELECT * FROM chemical_additions"
            params = []
            
            if customer_id:
                query += " WHERE customer_id = ?"
                params.append(customer_id)
            
            query += " ORDER BY date_time DESC"
            
            if limit:
                query += " LIMIT ?"
                params.append(limit)
            
            self.cursor.execute(query, params)
            columns = [desc[0] for desc in self.cursor.description]
            additions = []
            
            for row in self.cursor.fetchall():
                addition = dict(zip(columns, row))
                additions.append(addition)
            
            return additions
        except Exception as e:
            self.logger.error(f"Error getting chemical additions: {e}")
            return []