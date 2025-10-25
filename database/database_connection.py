import mysql.connector
from mysql.connector import pooling
import logging
import time
from config import DB_CONFIG
from exceptions import ConfigurationError

logger = logging.getLogger(__name__)

class DatabaseConnection:
    """Class for managing database connections with connection pooling."""
    
    _instance = None
    _pool = None
    
    def __new__(cls):
        """Implement the Singleton pattern for database connection."""
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
            cls._setup_connection_pool()
        return cls._instance
    
    @classmethod
    def _setup_connection_pool(cls):
        """Set up the database connection pool."""
        try:
            # Verify that we have all required configuration
            if not all(key in DB_CONFIG for key in ['host', 'database', 'user']):
                raise ConfigurationError("Incomplete database configuration")
                
            logger.info("Setting up database connection pool")
            cls._pool = mysql.connector.pooling.MySQLConnectionPool(
                pool_name="pool_management_pool",
                pool_size=5,
                **DB_CONFIG
            )
            logger.info("Database connection pool established")
        except mysql.connector.Error as err:
            logger.error(f"Failed to set up connection pool: {err}", exc_info=True)
            raise ConfigurationError(f"Database connection error: {err}")
    
    def get_connection(self):
        """Get a connection from the pool with automatic reconnection."""
        max_retry = 3
        retry_count = 0
        
        while retry_count < max_retry:
            try:
                if self._pool is None:
                    self._setup_connection_pool()
                    
                connection = self._pool.get_connection()
                logger.debug("Successfully retrieved connection from pool")
                return connection
            except mysql.connector.Error as err:
                retry_count += 1
                logger.warning(f"Connection attempt {retry_count} failed: {err}")
                if retry_count >= max_retry:
                    logger.error("Max connection attempts reached", exc_info=True)
                    raise
                time.sleep(1)  # Wait before retrying
    
    def execute_query(self, query, params=None, fetch=True):
        """
        Execute a query with error handling and automatic reconnection.
        
        Args:
            query: The SQL query string
            params: Parameters for the query
            fetch: Whether to fetch results (True) or not (False)
            
        Returns:
            Query results if fetch is True, otherwise None
        """
        connection = None
        cursor = None
        try:
            connection = self.get_connection()
            cursor = connection.cursor(dictionary=True)
            
            logger.debug(f"Executing query: {query}")
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
                
            if fetch:
                result = cursor.fetchall()
                logger.debug(f"Query returned {len(result)} rows")
                return result
            else:
                connection.commit()
                logger.debug(f"Query executed successfully, {cursor.rowcount} rows affected")
                return None
                
        except mysql.connector.Error as err:
            logger.error(f"Database error: {err}", exc_info=True)
            if connection:
                connection.rollback()
            raise
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
    
    def insert_pool_data(self, pool_data):
        """Insert or update pool data."""
        query = """
        INSERT INTO pools (id, name, pool_type, size_gallons, surface_material, 
                          use_type, indoor_outdoor, salt_water)
        VALUES (%(id)s, %(name)s, %(pool_type)s, %(size_gallons)s, %(surface_material)s,
                %(use_type)s, %(indoor_outdoor)s, %(salt_water)s)
        ON DUPLICATE KEY UPDATE
        name = VALUES(name),
        pool_type = VALUES(pool_type),
        size_gallons = VALUES(size_gallons),
        surface_material = VALUES(surface_material),
        use_type = VALUES(use_type),
        indoor_outdoor = VALUES(indoor_outdoor),
        salt_water = VALUES(salt_water)
        """
        return self.execute_query(query, pool_data, fetch=False)
    
    def get_pool_by_id(self, pool_id):
        """Retrieve pool data by ID."""
        query = "SELECT * FROM pools WHERE id = %s"
        result = self.execute_query(query, (pool_id,))
        return result[0] if result else None
    
    def insert_test_result(self, test_data):
        """Insert a new test result."""
        query = """
        INSERT INTO test_results (pool_id, test_date, ph, chlorine, alkalinity,
                                calcium_hardness, cyanuric_acid, salt, temperature)
        VALUES (%(pool_id)s, %(test_date)s, %(ph)s, %(chlorine)s, %(alkalinity)s,
                %(calcium_hardness)s, %(cyanuric_acid)s, %(salt)s, %(temperature)s)
        """
        return self.execute_query(query, test_data, fetch=False)
    
    def get_test_history(self, pool_id, limit=10):
        """Get test history for a pool."""
        query = """
        SELECT * FROM test_results 
        WHERE pool_id = %s
        ORDER BY test_date DESC
        LIMIT %s
        """
        return self.execute_query(query, (pool_id, limit))
    
    def insert_recommendation(self, recommendation_data):
        """Insert a chemical recommendation."""
        query = """
        INSERT INTO recommendations (test_result_id, chemical, amount, unit, notes)
        VALUES (%(test_result_id)s, %(chemical)s, %(amount)s, %(unit)s, %(notes)s)
        """
        return self.execute_query(query, recommendation_data, fetch=False)
    
    def store_weather_data(self, weather_data):
        """Store weather data for future reference."""
        query = """
        INSERT INTO weather_data (location, timestamp, temperature, humidity,
                                condition, forecast_data)
        VALUES (%(location)s, %(timestamp)s, %(temperature)s, %(humidity)s,
                %(condition)s, %(forecast_data)s)
        """
        return self.execute_query(query, weather_data, fetch=False)
