
#!/usr/bin/env python3
"""
Tab UI Customer Management Integration for Deep Blue Pool Chemistry application.

This module provides integration functions to add the enhanced Customer Management UI
to the existing Tab-based UI in the Deep Blue Pool Chemistry application.
"""

import os
import sys
import logging
import tkinter as tk
from tkinter import ttk, messagebox

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/customer_management.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("TabUICustomerIntegration")

def patch_tab_based_ui():
    """
    Patch the TabBasedUI class to use our enhanced Customer Management UI.
    
    This function modifies the TabBasedUI class to replace the default
    create_customer_management_tab method with our enhanced version.
    """
    try:
        # Import the TabBasedUI class
        from tab_based_ui import TabBasedUI
        
        # Store the original method
        original_method = TabBasedUI.create_customer_management_tab
        
        # Define our enhanced method
        def enhanced_customer_management_tab(self):
            """Create the enhanced customer management tab."""
            # Create the customer management frame
            customer_frame = ttk.Frame(self.notebook, padding=20)
            self.notebook.add(customer_frame, text="Customer Management")
            
            try:
                # Import our enhanced customer management UI
                from components.customer_management.ui import CustomerManagementUI
                
                # Create the customer management UI
                customer_ui = CustomerManagementUI(customer_frame)
                
                logger.info("Enhanced Customer Management UI initialized successfully")
            except Exception as e:
                logger.error(f"Error initializing enhanced Customer Management UI: {e}")
                import traceback
                logger.error(traceback.format_exc())
                
                # Fall back to the original implementation
                self.notebook.forget(self.notebook.index(customer_frame))
                original_method(self)
        
        # Replace the method
        TabBasedUI.create_customer_management_tab = enhanced_customer_management_tab
        
        logger.info("Successfully patched TabBasedUI.create_customer_management_tab")
        return True
    except Exception as e:
        logger.error(f"Error patching TabBasedUI: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def setup_customer_management():
    """
    Set up the Customer Management module.
    
    This function ensures that the necessary directories and files exist.
    """
    # Create necessary directories
    os.makedirs("components/customer_management", exist_ok=True)
    os.makedirs("data/customers", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    
    # Create empty customers file if it doesn't exist
    customers_file = "data/customers/customers.json"
    if not os.path.exists(customers_file):
        with open(customers_file, 'w') as f:
            f.write("{}")
        logger.info(f"Created empty customers file at {customers_file}")

# Apply the patch when this module is imported
setup_customer_management()
patch_success = patch_tab_based_ui()

# Example usage
if __name__ == "__main__":
    if patch_success:
        print("Successfully patched TabBasedUI to use enhanced Customer Management UI.")
        print("Now run your application normally and the enhanced UI will be used.")
    else:
        print("Failed to patch TabBasedUI. Check the logs for details.")
