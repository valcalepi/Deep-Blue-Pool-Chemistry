
#!/usr/bin/env python3
"""
Run the Deep Blue Pool Chemistry application with proper error handling.
"""

import os
import sys
import traceback

# Change to the Deep-Blue-Pool-Chemistry directory
os.chdir('/workspace/Deep-Blue-Pool-Chemistry')

# Add the current directory to the Python path
sys.path.insert(0, os.getcwd())

# Create a simple ArduinoMonitorApp class if it doesn't exist
arduino_monitor_code = """
import tkinter as tk
from tkinter import ttk
import logging

class ArduinoMonitorApp:
    def __init__(self, parent=None):
        self.logger = logging.getLogger("arduino_monitor")
        self.logger.info("Initializing Arduino Monitor (Placeholder)")
        
        self.main_frame = ttk.Frame(parent)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(self.main_frame, text="Arduino Monitor", font=("Arial", 18)).pack(pady=10)
        ttk.Label(self.main_frame, text="This is a placeholder for the Arduino Monitor.", font=("Arial", 12)).pack(pady=20)
        ttk.Label(self.main_frame, text="The actual monitor functionality is not available in this version.", font=("Arial", 12)).pack(pady=5)
"""

# Create the arduino_monitor_app.py file if it doesn't exist
if not os.path.exists('arduino_monitor_app.py'):
    with open('arduino_monitor_app.py', 'w') as f:
        f.write(arduino_monitor_code)

# Patch the pool_app.py file to use our ArduinoMonitorApp
with open('pool_app.py', 'r') as f:
    pool_app_code = f.read()

if 'from app.arduino_monitor import ArduinoMonitorApp' in pool_app_code:
    pool_app_code = pool_app_code.replace(
        'from app.arduino_monitor import ArduinoMonitorApp',
        'from arduino_monitor_app import ArduinoMonitorApp'
    )
    
    with open('pool_app.py', 'w') as f:
        f.write(pool_app_code)

try:
    # Execute the main.py file
    with open('main.py', 'r') as f:
        code = compile(f.read(), 'main.py', 'exec')
        exec(code, {'__file__': 'main.py'})
except Exception as e:
    print(f"Error: {e}")
    traceback.print_exc()
