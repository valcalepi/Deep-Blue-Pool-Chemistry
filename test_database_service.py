
#!/usr/bin/env python3
"""
Test script for the enhanced database service.

This script tests the customer management functionality added to the database service.
"""

import os
import sys
import logging

# Add the Deep-Blue-Pool-Chemistry directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'Deep-Blue-Pool-Chemistry'))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("TestDatabaseService")

# Import the DatabaseService class
from database_service import DatabaseService

def test_customer_management():
    """Test customer management functionality."""
    logger.info("Testing customer management functionality...")
    
    # Create a test database
    db_path = "test_database.db"
    if os.path.exists(db_path):
        os.remove(db_path)
    
    # Initialize database service
    db_service = DatabaseService(db_path)
    
    # Test adding customers
    logger.info("Testing add_customer...")
    customer1_id = db_service.add_customer(
        name="John Doe",
        email="john.doe@example.com",
        phone="555-123-4567",
        address="123 Main St, Anytown, USA"
    )
    
    customer2_id = db_service.add_customer(
        name="Jane Smith",
        email="jane.smith@example.com",
        phone="555-987-6543",
        address="456 Oak Ave, Somewhere, USA"
    )
    
    # Test getting customer
    logger.info("Testing get_customer...")
    customer1 = db_service.get_customer(customer1_id)
    if customer1 and customer1["name"] == "John Doe":
        logger.info(f"Successfully retrieved customer: {customer1['name']}")
    else:
        logger.error("Failed to retrieve customer")
    
    # Test getting all customers
    logger.info("Testing get_all_customers...")
    customers = db_service.get_all_customers()
    if len(customers) == 2:
        logger.info(f"Successfully retrieved {len(customers)} customers")
    else:
        logger.error(f"Expected 2 customers, got {len(customers)}")
    
    # Test updating customer
    logger.info("Testing update_customer...")
    db_service.update_customer(
        customer_id=customer1_id,
        phone="555-111-2222"
    )
    
    updated_customer = db_service.get_customer(customer1_id)
    if updated_customer and updated_customer["phone"] == "555-111-2222":
        logger.info("Successfully updated customer phone number")
    else:
        logger.error("Failed to update customer")
    
    # Test searching customers
    logger.info("Testing search_customers...")
    search_results = db_service.search_customers("Jane")
    if len(search_results) == 1 and search_results[0]["name"] == "Jane Smith":
        logger.info("Successfully searched for customers")
    else:
        logger.error("Failed to search customers")
    
    # Test adding pool info
    logger.info("Testing add_pool_info...")
    pool_info_id = db_service.add_pool_info(
        customer_id=customer1_id,
        pool_type="Inground",
        pool_size="15000",
        pool_shape="Rectangle",
        pool_material="Concrete"
    )
    
    # Test getting pool info
    logger.info("Testing get_customer_pool_info...")
    pool_info = db_service.get_customer_pool_info(customer1_id)
    if pool_info and pool_info["pool_size"] == "15000":
        logger.info("Successfully retrieved pool info")
    else:
        logger.error("Failed to retrieve pool info")
    
    # Test adding chemical readings
    logger.info("Testing insert_reading with customer_id...")
    reading_data = {
        "pH": "7.4",
        "free_chlorine": "3.0",
        "total_chlorine": "3.5",
        "alkalinity": "120",
        "calcium": "250",
        "cyanuric_acid": "40",
        "temperature": "82",
        "water_volume": "15000",
        "source": "manual"
    }
    
    success = db_service.insert_reading(reading_data, customer1_id)
    if success:
        logger.info("Successfully inserted reading with customer_id")
    else:
        logger.error("Failed to insert reading")
    
    # Test getting customer readings
    logger.info("Testing get_customer_readings...")
    readings = db_service.get_customer_readings(customer1_id)
    if len(readings) == 1:
        logger.info("Successfully retrieved customer readings")
    else:
        logger.error(f"Expected 1 reading, got {len(readings)}")
    
    # Test deleting customer
    logger.info("Testing delete_customer...")
    success = db_service.delete_customer(customer2_id)
    if success:
        logger.info("Successfully deleted customer")
    else:
        logger.error("Failed to delete customer")
    
    # Verify customer was deleted
    remaining_customers = db_service.get_all_customers()
    if len(remaining_customers) == 1:
        logger.info("Customer deletion verified")
    else:
        logger.error(f"Expected 1 customer after deletion, got {len(remaining_customers)}")
    
    # Clean up
    db_service.close_all_connections()
    if os.path.exists(db_path):
        os.remove(db_path)
    
    logger.info("Customer management tests completed")

if __name__ == "__main__":
    test_customer_management()
