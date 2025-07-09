# /models/pool_model.py
import logging
import sqlite3
from utils.error_handler import handle_error, DatabaseError

class PoolModel:
    """Model for pool-related data operations."""
    
    def __init__(self, db_path='pool_data.db'):
        self.logger = logging.getLogger(__name__)
        self.db_path = db_path
    
    @handle_error
    def _get_connection(self):
        """Get a database connection."""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row  # Return rows as dictionaries
            return conn
        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to connect to database: {e}")
    
    @handle_error
    def get_chemistry_data(self):
        """Retrieve pool chemistry data from database."""
        self.logger.debug("Retrieving pool chemistry data from database")
        
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            query = """
            SELECT * FROM pool_chemistry 
            ORDER BY timestamp DESC LIMIT 1
            """
            
            cursor.execute(query)
            result = cursor.fetchone()
            
            conn.close()
            
            if result:
                return dict(result)
            return None
            
        except sqlite3.Error as e:
            raise DatabaseError(f"Error retrieving pool chemistry data: {e}")
    
    @handle_error
    def update_chemistry_data(self, data):
        """Update pool chemistry data in database."""
        self.logger.debug(f"Updating pool chemistry data: {data}")
        
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            query = """
            INSERT INTO pool_chemistry 
            (ph, chlorine, alkalinity, timestamp) 
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            """
            
            cursor.execute(query, (
                data.get('ph'), 
                data.get('chlorine'),
                data.get('alkalinity')
            ))
            
            conn.commit()
            conn.close()
            
            return True
            
        except sqlite3.Error as e:
            raise DatabaseError(f"Error updating pool chemistry data: {e}")
