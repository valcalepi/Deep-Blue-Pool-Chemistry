# /tests/integration/test_pool_system.py
import unittest
import os
import tempfile
import sqlite3
from controllers.pool_controller import PoolController
from models.pool_model import PoolModel

class TestPoolSystemIntegration(unittest.TestCase):
    """Integration tests for the pool system components."""
    
    def setUp(self):
        """Set up test environment with temporary database."""
        # Create a temporary database
        self.db_fd, self.db_path = tempfile.mkstemp()
        
        # Create test table
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE pool_chemistry (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ph REAL,
            chlorine REAL,
            alkalinity REAL,
            timestamp TEXT
        )
        ''')
        conn.commit()
        conn.close()
        
        # Initialize components with test database
        self.model = PoolModel(db_path=self.db_path)
        self.controller = PoolController()
        self.controller.model = self.model
    
    def tearDown(self):
        """Clean up test environment."""
        os.close(self.db_fd)
        os.unlink(self.db_path)
    
    def test_end_to_end_data_flow(self):
        """Test end-to-end data flow from controller to model and back."""
        # Test data
        test_data = {'ph': 7.6, 'chlorine': 2.5, 'alkalinity': 110}
        
        # Update data through controller
        result = self.controller.update_chemistry_data(test_data)
        self.assertTrue(result)
        
        # Retrieve data through controller
        retrieved_data = self.controller.get_chemistry_data()
        
        # Verify core data values match (ignoring timestamp)
        self.assertEqual(retrieved_data['ph'], test_data['ph'])
        self.assertEqual(retrieved_data['chlorine'], test_data['chlorine'])
        self.assertEqual(retrieved_data['alkalinity'], test_data['alkalinity'])
