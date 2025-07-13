
#!/usr/bin/env python3
"""
Script to update import statements in the reorganized Deep Blue Pool Chemistry project.
This script will scan all Python files in the new structure and update import statements
to reflect the new file locations.
"""
import os
import re
import sys
from pathlib import Path

def update_imports(file_path, import_mappings):
    """Update import statements in a file based on the provided mappings."""
    try:
        # Read the file content
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Track if any changes were made
        original_content = content
        
        # Apply each import mapping
        for old_import, new_import in import_mappings.items():
            # Create regex patterns to match different import styles
            patterns = [
                rf"from\s+{re.escape(old_import)}\s+import",  # from old_import import ...
                rf"import\s+{re.escape(old_import)}(\s|$)",   # import old_import
                rf"import\s+{re.escape(old_import)}\.",       # import old_import.something
            ]
            
            replacements = [
                f"from {new_import} import",  # from new_import import ...
                f"import {new_import}\\1",    # import new_import
                f"import {new_import}.",      # import new_import.something
            ]
            
            # Apply each pattern
            for pattern, replacement in zip(patterns, replacements):
                content = re.sub(pattern, replacement, content)
        
        # Write the updated content back to the file if changes were made
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Updated imports in: {file_path}")
        else:
            print(f"No import changes needed in: {file_path}")
            
    except Exception as e:
        print(f"Error updating imports in {file_path}: {e}")

def main():
    # Get the project root directory
    project_root = os.path.dirname(os.path.abspath(__file__))
    new_structure_root = os.path.join(project_root, "new_structure")
    
    # Define import mappings (old_import -> new_import)
    import_mappings = {
        # App imports
        "src.gui": "app.gui_elements",
        "src.gui_elements": "app.gui_elements",
        "gui_elements": "app.gui_elements",
        "src.api_integrations.arduino_interface": "services.arduino.arduino_interface",
        "src.api_integrations.weather_api": "services.weather.weather_service",
        "weather_forecast": "services.weather.weather_service",
        "services.arduino_service": "services.arduino.arduino_interface",
        "controllers.pool_controller": "app.controllers.pool_controller",
        "controllers.weather_controller": "app.controllers.weather_controller",
        "database.database_connection": "services.database.database_connection",
        "test_strip_analyzer": "services.image_processing.test_strip_analyzer",
        
        # Models
        "app.models.pool_model": "app.models.pool",
        "src.chemistry": "app.models.chemical_calculator",
        
        # Utils
        "src.utils": "utils",
        "src.constants": "utils.constants",
        "src.exceptions": "utils.exceptions",
    }
    
    # Find all Python files in the new structure
    python_files = []
    for root, _, files in os.walk(new_structure_root):
        for file in files:
            if file.endswith(".py"):
                python_files.append(os.path.join(root, file))
    
    # Update imports in each file
    for file_path in python_files:
        update_imports(file_path, import_mappings)
    
    print("\
Import updates complete!")
    print("Please review the changes and test the application.")

if __name__ == "__main__":
    main()
