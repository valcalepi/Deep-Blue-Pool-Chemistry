
#!/usr/bin/env python3
"""
Test script for the Arduino Monitor App.
"""

import os
import sys
import tkinter as tk

# Add the Deep-Blue-Pool-Chemistry directory to the path
sys.path.append('/workspace/Deep-Blue-Pool-Chemistry')

# Import the ArduinoMonitorApp class
from arduino_monitor_app import ArduinoMonitorApp

# Create a simple Tkinter window
root = tk.Tk()
root.title("Arduino Monitor Test")
root.geometry("800x600")

# Create an instance of ArduinoMonitorApp
app = ArduinoMonitorApp(root)

# Run the Tkinter main loop
root.mainloop()
