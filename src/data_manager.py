import sqlite3
import pandas as pd
from datetime import datetime

class DataManager:
    def __init__(self, db_name):
        self.db_name = db_name
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        
        # Create tables if they don't exist
        self.create_tables()
        
    def create_tables(self):
        # Create the 'readings' table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS readings (
                id INTEGER PRIMARY KEY,
                timestamp TEXT NOT NULL,
                temperature REAL NOT NULL,
                ph REAL NOT NULL,
                chlorine REAL NOT NULL
            )
        ''')
        
        # Create the 'settings' table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                id INTEGER PRIMARY KEY,
                temperature_setpoint REAL NOT NULL,
                ph_setpoint REAL NOT NULL,
                chlorine_setpoint REAL NOT NULL
            )
        ''')
        
        self.conn.commit()
        
    def insert_reading(self, temperature, ph, chlorine):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.cursor.execute('''
            INSERT INTO readings (timestamp, temperature, ph, chlorine)
            VALUES (?, ?, ?, ?)
        ''', (timestamp, temperature, ph, chlorine))
        self.conn.commit()
        
    def get_readings(self):
        self.cursor.execute('SELECT * FROM readings')
        return self.cursor.fetchall()
        
    def get_latest_reading(self):
        self.cursor.execute('SELECT * FROM readings ORDER BY id DESC LIMIT 1')
        return self.cursor.fetchone()
        
    def update_settings(self, temperature_setpoint, ph_setpoint, chlorine_setpoint):
        self.cursor.execute('''
            UPDATE settings
            SET temperature_setpoint = ?, ph_setpoint = ?, chlorine_setpoint = ?
            WHERE id = 1
        ''', (temperature_setpoint, ph_setpoint, chlorine_setpoint))
        self.conn.commit()
        
    def get_settings(self):
        self.cursor.execute('SELECT * FROM settings WHERE id = 1')
        return self.cursor.fetchone()
        
    def close_connection(self):
        self.conn.close()
