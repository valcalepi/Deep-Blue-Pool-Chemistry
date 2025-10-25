# pool_controller/database/run_migrations.py
import os
import logging
from pathlib import Path
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import Error

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Database configuration from environment variables
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', '3306')),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'pool_management')
}

def run_migrations():
    """Run all SQL migrations in the migrations directory."""
    conn = None
    cursor = None
    
    try:
        # Connect to the database
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Create migrations table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS migrations (
                id INT AUTO_INCREMENT PRIMARY KEY,
                filename VARCHAR(255) NOT NULL,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        
        # Get list of applied migrations
        cursor.execute("SELECT filename FROM migrations")
        applied_migrations = {row[0] for row in cursor.fetchall()}
        
        # Get migration files
        migrations_dir = Path(__file__).parent / "migrations"
        migration_files = sorted([
            f for f in os.listdir(migrations_dir) 
            if f.endswith('.sql') and f not in applied_migrations
        ])
        
        if not migration_files:
            logger.info("No new migrations to apply")
            return True
        
        # Apply migrations
        for migration_file in migration_files:
            file_path = migrations_dir / migration_file
            
            try:
                logger.info(f"Applying migration: {migration_file}")
                
                # Read migration SQL
                with open(file_path, 'r') as f:
                    migration_sql = f.read()
                
                # Execute migration
                # Split SQL by semicolons and execute each statement
                for statement in migration_sql.split(';'):
                    if statement.strip():
                        cursor.execute(statement)
                
                # Record migration
                cursor.execute(
                    "INSERT INTO migrations (filename) VALUES (%s)",
                    (migration_file,)
                )
                conn.commit()
                
                logger.info(f"Successfully applied migration: {migration_file}")
                
            except Exception as e:
                conn.rollback()
                logger.error(f"Error applying migration {migration_file}: {str(e)}")
                return False
        
        return True
        
    except Error as e:
        logger.error(f"Database error: {str(e)}")
        return False
        
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

if __name__ == "__main__":
    success = run_migrations()
    if success:
        logger.info("All migrations completed successfully")
    else:
        logger.error("Migration process failed")
