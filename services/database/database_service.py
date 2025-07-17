import sqlite3
import logging
import csv
from datetime import datetime

logger = logging.getLogger("database_service")

class DatabaseService:
    def __init__(self, db_path="data/pool_chemistry.db"):
        self.conn = sqlite3.connect(db_path)
        self._create_table()

    def _create_table(self):
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
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
            """)
            self.conn.commit()
        except Exception as e:
            logger.error(f"Failed to create table: {e}")

    def insert_reading(self, data):
        try:
            cursor = self.conn.cursor()
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
            self.conn.commit()
        except Exception as e:
            logger.error(f"Failed to insert reading: {e}")

    def get_recent_readings(self, limit=5):
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM chemical_readings ORDER BY timestamp DESC LIMIT ?", (limit,))
            return cursor.fetchall()
        except Exception as e:
            logger.error(f"Failed to fetch readings: {e}")
            return []

    def export_to_csv(self, filename="data/exported_readings.csv"):
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM chemical_readings ORDER BY timestamp DESC")
            rows = cursor.fetchall()
            headers = [desc[0] for desc in cursor.description]

            with open(filename, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(headers)
                writer.writerows(rows)

            logger.info(f"Exported readings to {filename}")
        except Exception as e:
            logger.error(f"Failed to export CSV: {e}")
