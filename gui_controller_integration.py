"""
GUI Controller Integration Module.

This module integrates the enhanced GUI controller methods with the main PoolChemistryController class.
"""

import logging
import inspect
from gui_controller import PoolChemistryController
import enhanced_gui_controller_part2 as enhanced

# Configure logger
logger = logging.getLogger(__name__)

def integrate_enhanced_controller():
    """
    Integrate methods from enhanced_gui_controller_part2.py into PoolChemistryController.
    
    This function finds all methods in the enhanced_gui_controller_part2 module and
    attaches them to the PoolChemistryController class.
    """
    # Get all functions from enhanced_gui_controller_part2.py
    functions = [name for name, obj in inspect.getmembers(enhanced) 
                if inspect.isfunction(obj) and not name.startswith('__')]
    
    # Attach each function to the PoolChemistryController class
    for func_name in functions:
        func = getattr(enhanced, func_name)
        setattr(PoolChemistryController, func_name, func)
        logger.info(f"Attached {func_name} to PoolChemistryController")
    
    logger.info(f"Successfully integrated {len(functions)} methods from enhanced_gui_controller_part2.py")

# Run the integration when this module is imported
integrate_enhanced_controller()