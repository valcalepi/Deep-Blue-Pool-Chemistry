#!/usr/bin/env python3
"""
Test script to run the Deep Blue Pool Chemistry application and catch any errors.
"""

import sys
import traceback
import os

try:
    # Add the repository directory to the Python path
    repo_path = os.path.abspath("C:\\Scripts\\deepbluepool")
    sys.path.append(repo_path)
    
    # Import the main function
    from main import main
    
    # Run the main function
    main()
except Exception as e:
    print(f"Error: {e}")
    traceback.print_exc()
