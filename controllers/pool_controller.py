# /controllers/pool_controller.py
import logging
from models.pool_model import PoolModel
from utils.error_handler import handle_error

class PoolController:
    """Controller for pool-related operations."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.model = PoolModel()
        
    @handle_error
    def get_chemistry_data(self):
        """Retrieves current pool chemistry data."""
        self.logger.info("Retrieving pool chemistry data")
        return self.model.get_chemistry_data()
    
    @handle_error
    def update_chemistry_data(self, data):
        """Updates pool chemistry data."""
        self.logger.info(f"Updating pool chemistry data: {data}")
        return self.model.update_chemistry_data(data)
