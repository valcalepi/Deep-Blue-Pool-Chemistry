# pool_controller.py - Last updated: June 25, 2025
import mysql.connector
from models.chemical_calculator import ChemicalCalculator
from database.database_connection import DatabaseConnection
from datetime import datetime

class PoolController:
    def __init__(self, db_connection=None):
        if db_connection is None:
            self.db_connection = DatabaseConnection().get_connection()
        else:
            self.db_connection = db_connection
        self.current_pool_type = None
        self.calculator = ChemicalCalculator()

    def set_pool_type(self, pool_type):
        # Validate pool type
        valid_pool_types = ["Concrete", "Vinyl", "Fiberglass"]
        if pool_type not in valid_pool_types:
            raise ValueError(f"Invalid pool type provided: {pool_type}")
        self.current_pool_type = pool_type
        self.calculator.set_pool_type(pool_type)

    def get_ideal_range(self, parameter, pool_type=None):
        if pool_type:
            return self.calculator.get_ideal_range(parameter, pool_type)
        elif self.current_pool_type:
            return self.calculator.get_ideal_range(parameter, self.current_pool_type)
        else:
            raise ValueError("Pool type is not set.")

    def calculate_adjustments(self, pool_type, pH, chlorine, alkalinity, hardness):
        return self.calculator.calculate_adjustments(pool_type, pH, chlorine, alkalinity, hardness)

    def update_pool_info(self, pool_id, pool_info):
        cursor = self.db_connection.cursor()
        try:
            # Update the pool information with timestamp
            pool_info["last_updated"] = datetime.now().isoformat()
            query = "UPDATE pools SET info = %s WHERE id = %s"
            cursor.execute(query, (pool_info, pool_id))
            self.db_connection.commit()
            return True
        except mysql.connector.Error as error:
            self.db_connection.rollback()
            print(f"Error updating pool info: {error}")
            return False
        finally:
            cursor.close()
