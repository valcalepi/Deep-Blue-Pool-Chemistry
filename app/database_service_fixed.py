
"""
Database Service for Deep Blue Pool Chemistry Application
This module provides services for storing and retrieving data.
"""

import os
import json
import logging
import random
from datetime import datetime, timedelta

logger = logging.getLogger("DeepBluePoolApp")

class DatabaseService:
    """Database service for storing and retrieving data."""
    
    def __init__(self, data_dir="data"):
        """
        Initialize the database service.
        
        Args:
            data_dir: Directory to store data files
        """
        logger.info(f"Initializing Database Service with path: {data_dir}")
        self.data_dir = data_dir
        self.customers_file = os.path.join(data_dir, "customers.json")
        self.readings_file = os.path.join(data_dir, "readings.json")
        
        # Create data directory if it doesn't exist
        os.makedirs(data_dir, exist_ok=True)
        
        # Initialize data
        self.customers = []
        self.readings = []
        
        # Load data
        self._load_data()
    
    def _load_data(self):
        """Load data from files."""
        # Load customers
        if os.path.exists(self.customers_file):
            try:
                with open(self.customers_file, 'r') as f:
                    self.customers = json.load(f)
            except Exception as e:
                logger.error(f"Error loading customers data: {e}")
        else:
            # Create sample customers
            self.customers = [
                {
                    "id": 1,
                    "name": "John Smith",
                    "address": "123 Main St",
                    "phone": "555-1234",
                    "email": "john@example.com",
                    "pools": [
                        {
                            "id": 1,
                            "type": "In-ground",
                            "volume": 20000,
                            "volume_unit": "gallons",
                            "surface": "Plaster"
                        }
                    ]
                },
                {
                    "id": 2,
                    "name": "Jane Doe",
                    "address": "456 Oak Ave",
                    "phone": "555-5678",
                    "email": "jane@example.com",
                    "pools": [
                        {
                            "id": 2,
                            "type": "Above-ground",
                            "volume": 10000,
                            "volume_unit": "gallons",
                            "surface": "Vinyl"
                        }
                    ]
                }
            ]
            self._save_customers()
        
        # Load readings
        if os.path.exists(self.readings_file):
            try:
                with open(self.readings_file, 'r') as f:
                    self.readings = json.load(f)
            except Exception as e:
                logger.error(f"Error loading readings data: {e}")
        else:
            # Create sample readings
            self.readings = self._generate_sample_readings()
            self._save_readings()
    
    def _generate_sample_readings(self):
        """Generate sample readings for testing."""
        readings = []
        
        # Generate readings for the past 30 days
        for i in range(30):
            date = datetime.now() - timedelta(days=i)
            
            # Generate readings for each customer
            for customer in self.customers:
                for pool in customer["pools"]:
                    readings.append({
                        "id": len(readings) + 1,
                        "customer_id": customer["id"],
                        "pool_id": pool["id"],
                        "date": date.strftime("%Y-%m-%d"),
                        "ph": round(random.uniform(7.0, 8.0), 1),
                        "free_chlorine": round(random.uniform(1.0, 3.0), 1),
                        "total_alkalinity": round(random.uniform(80, 120)),
                        "calcium_hardness": round(random.uniform(200, 400)),
                        "cyanuric_acid": round(random.uniform(30, 50)),
                        "salt": round(random.uniform(2700, 3400)),
                        "temperature": round(random.uniform(75, 85), 1)
                    })
        return readings
    
    def _save_customers(self):
        """Save customers data to file."""
        try:
            with open(self.customers_file, 'w') as f:
                json.dump(self.customers, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving customers: {e}")
    
    def _save_readings(self):
        """Save readings data to file."""
        try:
            with open(self.readings_file, 'w') as f:
                json.dump(self.readings, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving readings: {e}")
    
    def get_all_customers(self):
        """
        Get all customers.
        
        Returns:
            List of customer dictionaries
        """
        return self.customers
    
    def get_customer(self, customer_id):
        """
        Get a customer by ID.
        
        Args:
            customer_id: Customer ID
        
        Returns:
            Customer dictionary or None if not found
        """
        for customer in self.customers:
            if customer["id"] == customer_id:
                return customer
        return None
    
    def add_customer(self, customer_data):
        """
        Add a new customer.
        
        Args:
            customer_data: Customer data dictionary
        
        Returns:
            New customer dictionary
        """
        # Generate ID
        customer_id = max([c["id"] for c in self.customers], default=0) + 1
        
        # Create new customer
        new_customer = {
            "id": customer_id,
            "name": customer_data.get("name", ""),
            "address": customer_data.get("address", ""),
            "phone": customer_data.get("phone", ""),
            "email": customer_data.get("email", ""),
            "pools": []
        }
        
        # Add pool if provided
        if "pool_type" in customer_data and "pool_volume" in customer_data:
            pool_id = 1
            new_customer["pools"].append({
                "id": pool_id,
                "type": customer_data.get("pool_type", ""),
                "volume": float(customer_data.get("pool_volume", 0)),
                "volume_unit": customer_data.get("volume_unit", "gallons"),
                "surface": customer_data.get("surface", "")
            })
        
        # Add to list
        self.customers.append(new_customer)
        
        # Save to file
        self._save_customers()
        
        return new_customer
    
    def update_customer(self, customer_id, customer_data):
        """
        Update a customer.
        
        Args:
            customer_id: Customer ID
            customer_data: Customer data dictionary
        
        Returns:
            Updated customer dictionary or None if not found
        """
        for i, customer in enumerate(self.customers):
            if customer["id"] == customer_id:
                # Update fields
                self.customers[i]["name"] = customer_data.get("name", customer["name"])
                self.customers[i]["address"] = customer_data.get("address", customer["address"])
                self.customers[i]["phone"] = customer_data.get("phone", customer["phone"])
                self.customers[i]["email"] = customer_data.get("email", customer["email"])
                
                # Save to file
                self._save_customers()
                
                return self.customers[i]
        return None
    
    def delete_customer(self, customer_id):
        """
        Delete a customer.
        
        Args:
            customer_id: Customer ID
        
        Returns:
            True if deleted, False if not found
        """
        for i, customer in enumerate(self.customers):
            if customer["id"] == customer_id:
                # Remove from list
                del self.customers[i]
                
                # Save to file
                self._save_customers()
                
                return True
        return False
    
    def get_readings(self, customer_id=None, pool_id=None, days=30):
        """
        Get readings for a customer and pool.
        
        Args:
            customer_id: Customer ID (optional)
            pool_id: Pool ID (optional)
            days: Number of days to get readings for
        
        Returns:
            List of reading dictionaries
        """
        # Filter by date
        start_date = datetime.now() - timedelta(days=days)
        start_date_str = start_date.strftime("%Y-%m-%d")
        
        # Filter readings
        filtered_readings = []
        for reading in self.readings:
            # Check date
            if reading["date"] < start_date_str:
                continue
            
            # Check customer ID
            if customer_id is not None and reading["customer_id"] != customer_id:
                continue
            
            # Check pool ID
            if pool_id is not None and reading["pool_id"] != pool_id:
                continue
            
            filtered_readings.append(reading)
        
        return filtered_readings
    
    def get_latest_reading(self, customer_id, pool_id=None):
        """
        Get the latest reading for a customer and pool.
        
        Args:
            customer_id: Customer ID
            pool_id: Pool ID (optional)
        
        Returns:
            Reading dictionary or None if not found
        """
        # Get readings for customer
        readings = self.get_readings(customer_id, pool_id)
        
        # Sort by date (newest first)
        readings.sort(key=lambda r: r["date"], reverse=True)
        
        # Return latest reading
        return readings[0] if readings else None
    
    def add_reading(self, reading_data):
        """
        Add a new reading.
        
        Args:
            reading_data: Reading data dictionary
        
        Returns:
            New reading dictionary
        """
        # Generate ID
        reading_id = max([r["id"] for r in self.readings], default=0) + 1
        
        # Create new reading
        new_reading = {
            "id": reading_id,
            "customer_id": reading_data.get("customer_id", 1),
            "pool_id": reading_data.get("pool_id", 1),
            "date": datetime.now().strftime("%Y-%m-%d"),
            "ph": float(reading_data.get("ph", 0)),
            "free_chlorine": float(reading_data.get("free_chlorine", 0)),
            "total_alkalinity": float(reading_data.get("total_alkalinity", 0)),
            "calcium_hardness": float(reading_data.get("calcium_hardness", 0)),
            "cyanuric_acid": float(reading_data.get("cyanuric_acid", 0)),
            "salt": float(reading_data.get("salt", 0)),
            "temperature": float(reading_data.get("temperature", 0))
        }
        
        # Add to the list
        self.readings.append(new_reading)
        
        # Save to file
        self._save_readings()
        
        return new_reading

