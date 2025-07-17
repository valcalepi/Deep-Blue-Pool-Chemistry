import traceback
import sys
import os
import json
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("TestStartMethod")

try:
    logger.info("Importing integrated_app...")
    import integrated_app
    
    logger.info("Creating IntegratedApp instance...")
    app = integrated_app.IntegratedApp()
    
    logger.info("Calling start method...")
    try:
        app.start()
        logger.info("Start method completed successfully")
    except Exception as e:
        logger.error(f"Error in start method: {e}")
        traceback.print_exc()
        
        # Check if the error is related to tk.Tk()
        if "Tk" in str(e):
            logger.info("The error appears to be related to Tkinter initialization")
            logger.info("Checking if we can create a basic Tk window...")
            
            import tkinter as tk
            try:
                root = tk.Tk()
                logger.info("Basic Tk window created successfully")
                root.destroy()
            except Exception as tk_error:
                logger.error(f"Error creating basic Tk window: {tk_error}")
                traceback.print_exc()
        
except Exception as e:
    logger.error(f"Error: {e}")
    traceback.print_exc()
