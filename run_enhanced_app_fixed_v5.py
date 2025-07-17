#!/usr/bin/env python3
"""
Compatibility wrapper for run_enhanced_app.py

This script maintains backward compatibility with the original run_enhanced_app.py
by forwarding to the consolidated_pool_app_fixed_v5.py with appropriate arguments.
"""

import sys
import os
import subprocess

def main():
    """Forward to consolidated_pool_app_fixed_v5.py with enhanced mode."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    consolidated_script = os.path.join(script_dir, "consolidated_pool_app_fixed_v5.py")
    
    # Build arguments list
    args = [sys.executable, consolidated_script, "--enhanced"]
    
    # Forward any additional arguments
    args.extend(sys.argv[1:])
    
    print("Deep Blue Pool Chemistry Application - Enhanced Mode")
    print("Note: This script is a compatibility wrapper for the consolidated application.")
    print(f"Running: {' '.join(args)}")
    
    # Execute the consolidated script
    return subprocess.call(args)

if __name__ == "__main__":
    sys.exit(main())