# database/insert_test_results.py
import os
import mysql.connector
from mysql.connector import Error
from datetime import datetime
import csv
import logging
from contextlib import contextmanager
from dotenv import load_dotenv
from typing import Dict, List, Any, Optional, Tuple

# Configure logging
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Database configuration from environment variables
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'pool_db')
}

# Safe ranges for chemical parameters
SAFE_RANGES = {
    "pH": (7.2, 7.8),
    "Chlorine": (1.0, 3.0),
    "Alkalinity": (80, 120)
}

class DatabaseManager:
    """
    Manager for database operations related to pool test results.
    """
    
    def __init__(self, config: Optional[Dict[str, str]] = None):
        """
        Initialize the database manager.
        
        Args:
            config: Optional database configuration dictionary
        """
        self.config = config or DB_CONFIG
        self.conn = None
        logger.info("DatabaseManager initialized")
    
    @contextmanager
    def get_connection(self):
        """
        Context manager for database connections.
        
        Yields:
            mysql.connector.connection.MySQLConnection: Database connection
            
        Raises:
            Error: If connection fails
        """
        conn = None
        try:
            conn = mysql.connector.connect(**self.config)
            logger.debug("Database connection established")
            yield conn
        except Error as e:
            logger.error(f"Database connection error: {str(e)}")
            raise
        finally:
            if conn and conn.is_connected():
                conn.close()
                logger.debug("Database connection closed")
    
    @contextmanager
    def get_cursor(self, commit: bool = False):
        """
        Context manager for database cursors.
        
        Args:
            commit: Whether to commit changes after operations
            
        Yields:
            mysql.connector.cursor.MySQLCursor: Database cursor
            
        Raises:
            Error: If cursor operations fail
        """
        with self.get_connection() as conn:
            cursor = None
            try:
                cursor = conn.cursor(dictionary=True)
                yield cursor
                if commit:
                    conn.commit()
                    logger.debug("Changes committed to database")
            except Error as e:
                if commit:
                    conn.rollback()
                    logger.debug("Changes rolled back")
                logger.error(f"Database cursor error: {str(e)}")
                raise
            finally:
                if cursor:
                    cursor.close()
                    logger.debug("Database cursor closed")
    
    def check_health(self) -> bool:
        """
        Check if the database connection is healthy.
        
        Returns:
            bool: True if healthy, False otherwise
        """
        try:
            with self.get_cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                return result is not None and result['1'] == 1
        except Error as e:
            logger.error(f"Database health check failed: {str(e)}")
            return False
    
    def run_migrations(self, migrations_dir: str = "database/migrations") -> bool:
        """
        Run database migrations from SQL files.
        
        Args:
            migrations_dir: Directory containing migration SQL files
            
        Returns:
            bool: True if migrations were successful, False otherwise
        """
        try:
            # Check if migrations table exists, create if not
            with self.get_cursor(commit=True) as cursor:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS migrations (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        filename VARCHAR(255) NOT NULL,
                        applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
            
            # Get list of applied migrations
            with self.get_cursor() as cursor:
                cursor.execute("SELECT filename FROM migrations")
                applied_migrations = {row['filename'] for row in cursor.fetchall()}
            
            # Check for migration files
            if not os.path.exists(migrations_dir):
                logger.warning(f"Migrations directory not found: {migrations_dir}")
                return False
            
            # Get list of migration files
            migration_files = sorted([
                f for f in os.listdir(migrations_dir) 
                if f.endswith('.sql') and f not in applied_migrations
            ])
            
            if not migration_files:
                logger.info("No new migrations to apply")
                return True
            
            # Apply migrations
            for migration_file in migration_files:
                file_path = os.path.join(migrations_dir, migration_file)
                
                try:
                    # Read migration SQL
                    with open(file_path, 'r') as f:
                        migration_sql = f.read()
                    
                    # Execute migration
                    with self.get_cursor(commit=True) as cursor:
                        # Split SQL by semicolons and execute each statement
                        for statement in migration_sql.split(';'):
                            if statement.strip():
                                cursor.execute(statement)
                        
                        # Record migration
                        cursor.execute(
                            "INSERT INTO migrations (filename) VALUES (%s)",
                            (migration_file,)
                        )
                    
                    logger.info(f"Applied migration: {migration_file}")
                    
                except Exception as e:
                    logger.error(f"Error applying migration {migration_file}: {str(e)}")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error running migrations: {str(e)}")
            return False
    
    def insert_test(self, location_name: str) -> Optional[int]:
        """
        Insert a new test record.
        
        Args:
            location_name: Name of the pool location
            
        Returns:
            Optional[int]: ID of the inserted test, or None if failed
        """
        try:
            with self.get_cursor(commit=True) as cursor:
                cursor.execute(
                    "INSERT INTO tests (test_date, location_name) VALUES (%s, %s)",
                    (datetime.now(), location_name)
                )
                return cursor.lastrowid
        except Error as e:
            logger.error(f"Error inserting test: {str(e)}")
            return None
    
    def insert_test_result(self, test_id: int, parameter: str, value: float, unit: str) -> bool:
        """
        Insert a test result.
        
        Args:
            test_id: ID of the test
            parameter: Chemical parameter name
            value: Reading value
            unit: Unit of measurement
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with self.get_cursor(commit=True) as cursor:
                cursor.execute(
                    "INSERT INTO test_results (test_id, parameter, value, unit) VALUES (%s, %s, %s, %s)",
                    (test_id, parameter, value, unit)
                )
                return True
        except Error as e:
            logger.error(f"Error inserting test result: {str(e)}")
            return False
    
        def insert_recommendation(self, test_id: int, parameter: str, value: float, 
                             recommendation: str) -> bool:
        """
        Insert a recommendation.
        
        Args:
            test_id: ID of the test
            parameter: Chemical parameter name
            value: Reading value
            recommendation: Recommendation text
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with self.get_cursor(commit=True) as cursor:
                cursor.execute(
                    "INSERT INTO recommendations (test_id, parameter, value, recommendation) VALUES (%s, %s, %s, %s)",
                    (test_id, parameter, value, recommendation)
                )
                return True
        except Error as e:
            logger.error(f"Error inserting recommendation: {str(e)}")
            return False
    
    def export_to_csv(self, test_id: int, filename: str = "test_report.csv") -> bool:
        """
        Export test results and recommendations to CSV.
        
        Args:
            test_id: ID of the test
            filename: Output CSV filename
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Get test results
            with self.get_cursor() as cursor:
                cursor.execute("""
                    SELECT tr.parameter, tr.value, tr.unit, r.recommendation
                    FROM test_results tr
                    LEFT JOIN recommendations r ON tr.test_id = r.test_id AND tr.parameter = r.parameter
                    WHERE tr.test_id = %s
                """, (test_id,))
                results = cursor.fetchall()
            
            if not results:
                logger.warning(f"No results found for test ID {test_id}")
                return False
            
            # Write to CSV
            with open(filename, mode="w", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(["Parameter", "Value", "Unit", "Recommendation"])
                
                for row in results:
                    writer.writerow([
                        row["parameter"],
                        row["value"],
                        row["unit"],
                        row["recommendation"] or "No recommendation"
                    ])
            
            logger.info(f"Test report exported to {filename}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting to CSV: {str(e)}")
            return False
    
    def get_recommendation(self, parameter: str, value: float) -> str:
        """
        Get a recommendation based on parameter value.
        
        Args:
            parameter: Chemical parameter name
            value: Reading value
            
        Returns:
            str: Recommendation text
        """
        low, high = SAFE_RANGES.get(parameter, (None, None))
        
        if low is None:
            return "No recommendation available"
            
        if value < low:
            return f"Increase {parameter}"
        elif value > high:
            return f"Decrease {parameter}"
        else:
            return "OK"

