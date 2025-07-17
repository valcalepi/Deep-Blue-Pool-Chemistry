
import logging
import sqlite3
import os
import json
from datetime import datetime

logger = logging.getLogger("database_service")

class DatabaseService:
    def __init__(self, db_path="pool_data.db"):
        """Initialize Database service with database path"""
        self.db_path = db_path
        logger.info(f"Database Service initialized with SQLite3 at {db_path}")
        
        # Create database if it doesn't exist
        self._init_db()
        
    def _init_db(self):
        """Initialize database tables"""
        try:
            conn = sqlite3.connect(self.db_path)
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
            
            conn.commit()
            conn.close()
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            
    def log_sensor_data(self, data):
        """Log sensor data to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            timestamp = datetime.now().isoformat()
            water_temp = data.get("water_temp")
            ph_level = data.get("ph_level")
            chlorine_level = data.get("chlorine_level")
            json_data = json.dumps(data)
            
            cursor.execute(
                "INSERT INTO sensor_data (timestamp, water_temp, ph_level, chlorine_level, json_data) VALUES (?, ?, ?, ?, ?)",
                (timestamp, water_temp, ph_level, chlorine_level, json_data)
            )
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Failed to log sensor data: {e}")
            return False
            
    def log_maintenance(self, action, details="", performed_by="system"):
        """Log maintenance action to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            timestamp = datetime.now().isoformat()
            
            cursor.execute(
                "INSERT INTO maintenance_log (timestamp, action, details, performed_by) VALUES (?, ?, ?, ?)",
                (timestamp, action, details, performed_by)
            )
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Failed to log maintenance: {e}")
            return False
            
    def log_chemical_addition(self, chemical, amount, reason=""):
        """Log chemical addition to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            timestamp = datetime.now().isoformat()
            
            cursor.execute(
                "INSERT INTO chemical_log (timestamp, chemical, amount, reason) VALUES (?, ?, ?, ?)",
                (timestamp, chemical, amount, reason)
            )
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Failed to log chemical addition: {e}")
            return False
            
    def get_sensor_history(self, hours=24):
        """Get sensor data history for the specified number of hours"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            timestamp = (datetime.now() - datetime.timedelta(hours=hours)).isoformat()
            
            cursor.execute(
                "SELECT timestamp, water_temp, ph_level, chlorine_level FROM sensor_data WHERE timestamp > ? ORDER BY timestamp",
                (timestamp,)
            )
            
            data = cursor.fetchall()
            conn.close()
            
            return [
                {
                    "timestamp": row[0],
                    "water_temp": row[1],
                    "ph_level": row[2],
                    "chlorine_level": row[3]
                }
                for row in data
            ]
        except Exception as e:
            logger.error(f"Failed to get sensor history: {e}")
            return []
