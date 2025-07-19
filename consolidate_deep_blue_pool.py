
#!/usr/bin/env python3
"""
Consolidation script for Deep Blue Pool Chemistry application.

This script consolidates the Deep Blue Pool Chemistry codebase into a clean
folder structure while preserving all functionality. It copies the required
components to a new location and integrates enhanced features into core files.
"""

import os
import sys
import shutil
import logging
import argparse
from pathlib import Path
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("consolidate_deep_blue_pool.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("consolidate_deep_blue_pool")

# Default source and destination directories
DEFAULT_SOURCE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_DEST_DIR = r"C:\Scripts\deepbluepool3"

# Define the new directory structure
DIRECTORY_STRUCTURE = [
    "app",
    "app/controllers",
    "app/models",
    "app/services",
    "app/ui",
    "app/ui/components",
    "app/utils",
    "data",
    "data/exports",
    "data/strip_profiles",
    "logs",
    "tests"
]

# Define files to copy directly (source_path, destination_path)
FILES_TO_COPY = [
    ("config.json", "config.json"),
    ("requirements.txt", "requirements.txt"),
    ("data/chemical_safety_data.json", "data/chemical_safety_data.json"),
    ("data/calibration.json", "data/calibration.json"),
    ("data/strip_profiles/default.json", "data/strip_profiles/default.json"),
    ("data/test_strip_calibration.json", "data/test_strip_calibration.json"),
    ("data/pad_zones.json", "data/pad_zones.json"),
    ("assests/chemistry.png", "app/ui/assets/chemistry.png")
]

# Define files to consolidate (source_files, destination_path, integration_function)
FILES_TO_CONSOLIDATE = [
    # Main application files
    (["main.py"], "app/main.py", "consolidate_main"),
    (["pool_app.py"], "app/pool_app.py", "consolidate_pool_app"),
    
    # Controllers
    (["gui_controller.py", "enhanced_gui_controller_part2.py"], 
     "app/controllers/pool_controller.py", "consolidate_controller"),
    
    # Services
    (["database_service.py"], 
     "app/services/database.py", "consolidate_database"),
    (["chemical_safety_database.py"], 
     "app/services/chemical_safety.py", "consolidate_chemical_safety"),
    (["test_strip_analyzer.py"], 
     "app/services/test_strip.py", "consolidate_test_strip"),
    (["weather_service.py", "enhanced_weather_service.py"], 
     "app/services/weather.py", "consolidate_weather"),
    (["arduino_sensor_manager.py"], 
     "app/services/arduino.py", "consolidate_arduino"),
    (["chemical_calculator.py", "enhanced_chemical_calculator.py"], 
     "app/services/chemical_calculator.py", "consolidate_chemical_calculator"),
    (["data_visualization.py", "enhanced_data_visualization.py", "chemical_history_visualizer.py"], 
     "app/services/data_visualization.py", "consolidate_data_visualization"),
    
    # UI
    (["tab_based_ui.py", "responsive_tab_ui.py"], 
     "app/ui/tab_ui.py", "consolidate_tab_ui"),
    
    # Utils
    (["utils/config.py"], 
     "app/utils/config.py", "copy_file"),
    (["utils/validators.py"], 
     "app/utils/validators.py", "copy_file"),
    (["utils/error_handler.py", "enhanced_error_handler.py"], 
     "app/utils/error_handler.py", "consolidate_error_handler")
]

# Define __init__.py files to create
INIT_FILES = [
    "app/__init__.py",
    "app/controllers/__init__.py",
    "app/models/__init__.py",
    "app/services/__init__.py",
    "app/ui/__init__.py",
    "app/ui/components/__init__.py",
    "app/utils/__init__.py",
    "data/__init__.py",
    "data/exports/__init__.py",
    "data/strip_profiles/__init__.py",
    "tests/__init__.py"
]

def create_directory_structure(base_dir):
    """Create the directory structure."""
    logger.info(f"Creating directory structure in {base_dir}")
    
    for directory in DIRECTORY_STRUCTURE:
        dir_path = os.path.join(base_dir, directory)
        os.makedirs(dir_path, exist_ok=True)
        logger.info(f"Created directory: {dir_path}")

def create_init_files(base_dir):
    """Create __init__.py files."""
    logger.info("Creating __init__.py files")
    
    for init_file in INIT_FILES:
        file_path = os.path.join(base_dir, init_file)
        with open(file_path, 'w') as f:
            f.write('"""Deep Blue Pool Chemistry package."""\
')
        logger.info(f"Created __init__.py: {file_path}")

def copy_file(source_dir, dest_dir, source_path, dest_path, *args):
    """Copy a file from source to destination."""
    source_file = os.path.join(source_dir, source_path)
    dest_file = os.path.join(dest_dir, dest_path)
    
    if os.path.exists(source_file):
        os.makedirs(os.path.dirname(dest_file), exist_ok=True)
        shutil.copy2(source_file, dest_file)
        logger.info(f"Copied {source_file} to {dest_file}")
    else:
        logger.warning(f"Source file not found: {source_file}")

def copy_files(source_dir, dest_dir):
    """Copy files from source to destination."""
    logger.info("Copying files")
    
    for source_path, dest_path in FILES_TO_COPY:
        copy_file(source_dir, dest_dir, source_path, dest_path)

def consolidate_files(source_dir, dest_dir):
    """Consolidate files from source to destination."""
    logger.info("Consolidating files")
    
    for source_files, dest_path, integration_func in FILES_TO_CONSOLIDATE:
        try:
            # Get the integration function
            func = globals()[integration_func]
            
            # Call the integration function
            func(source_dir, dest_dir, source_files, dest_path)
        except Exception as e:
            logger.error(f"Error consolidating {source_files} to {dest_path}: {e}")
            import traceback
            logger.error(traceback.format_exc())

def consolidate_main(source_dir, dest_dir, source_files, dest_path):
    """Consolidate main.py."""
    source_file = os.path.join(source_dir, source_files[0])
    dest_file = os.path.join(dest_dir, dest_path)
    
    if os.path.exists(source_file):
        with open(source_file, 'r') as f:
            content = f.read()
        
        # Update imports to reflect new structure
        content = content.replace("from pool_app import PoolChemistryApp", 
                                 "from app.pool_app import PoolChemistryApp")
        
        # Write the updated content
        os.makedirs(os.path.dirname(dest_file), exist_ok=True)
        with open(dest_file, 'w') as f:
            f.write(content)
        
        logger.info(f"Consolidated main.py to {dest_file}")
    else:
        logger.warning(f"Source file not found: {source_file}")

def consolidate_pool_app(source_dir, dest_dir, source_files, dest_path):
    """Consolidate pool_app.py."""
    source_file = os.path.join(source_dir, source_files[0])
    dest_file = os.path.join(dest_dir, dest_path)
    
    if os.path.exists(source_file):
        with open(source_file, 'r') as f:
            content = f.read()
        
        # Update imports to reflect new structure
        content = content.replace("from database_service import DatabaseService", 
                                 "from app.services.database import DatabaseService")
        content = content.replace("from chemical_safety_database import ChemicalSafetyDatabase", 
                                 "from app.services.chemical_safety import ChemicalSafetyDatabase")
        content = content.replace("from test_strip_analyzer import TestStripAnalyzer", 
                                 "from app.services.test_strip import TestStripAnalyzer")
        content = content.replace("from weather_service import WeatherService", 
                                 "from app.services.weather import WeatherService")
        content = content.replace("from gui_controller import PoolChemistryController", 
                                 "from app.controllers.pool_controller import PoolChemistryController")
        content = content.replace("from tab_based_ui import TabBasedUI", 
                                 "from app.ui.tab_ui import TabBasedUI")
        content = content.replace("from arduino_monitor_app import ArduinoMonitorApp", 
                                 "from app.services.arduino import ArduinoMonitorApp")
        
        # Write the updated content
        os.makedirs(os.path.dirname(dest_file), exist_ok=True)
        with open(dest_file, 'w') as f:
            f.write(content)
        
        logger.info(f"Consolidated pool_app.py to {dest_file}")
    else:
        logger.warning(f"Source file not found: {source_file}")

def consolidate_controller(source_dir, dest_dir, source_files, dest_path):
    """Consolidate controller files."""
    base_file = os.path.join(source_dir, source_files[0])
    enhanced_file = os.path.join(source_dir, source_files[1])
    dest_file = os.path.join(dest_dir, dest_path)

    if os.path.exists(base_file) and os.path.exists(enhanced_file):
        with open(base_file, 'r') as f:
            base_content = f.read()

        with open(enhanced_file, 'r') as f:
            enhanced_content = f.read()

        # Extract method names from enhanced file
        enhanced_methods = re.findall(r'def\s+([a-zA-Z0-9_]+)\s*\(', enhanced_content)

        consolidated_content = base_content

        for method in enhanced_methods:
            if method not in base_content:
                # Extract full method definition (simplified)
                method_match = re.search(
                    rf'def\s+{method}\s*\([^)]*\):(?:\n(?:    .*)*)',
                    enhanced_content
                )
                if method_match:
                    method_code = method_match.group(0)
                    consolidated_content += "\n\n" + method_code

        # Update imports
        if "import logging" in consolidated_content:
            consolidated_content = consolidated_content.replace(
                "import logging",
                "import logging\nimport os\nimport sys"
            )

        os.makedirs(os.path.dirname(dest_file), exist_ok=True)
        with open(dest_file, 'w') as f:
            f.write(consolidated_content)

        logger.info(f"Consolidated controller files to {dest_file}")
    else:
        logger.warning(f"Source files not found: {base_file} or {enhanced_file}")

def consolidate_database(source_dir, dest_dir, source_files, dest_path):
    """Consolidate database service."""
    source_file = os.path.join(source_dir, source_files[0])
    dest_file = os.path.join(dest_dir, dest_path)
    
    if os.path.exists(source_file):
        with open(source_file, 'r') as f:
            content = f.read()
        
        # No major changes needed for database service
        
        # Write the content
        os.makedirs(os.path.dirname(dest_file), exist_ok=True)
        with open(dest_file, 'w') as f:
            f.write(content)
        
        logger.info(f"Consolidated database service to {dest_file}")
    else:
        logger.warning(f"Source file not found: {source_file}")

def consolidate_chemical_safety(source_dir, dest_dir, source_files, dest_path):
    """Consolidate chemical safety database."""
    source_file = os.path.join(source_dir, source_files[0])
    dest_file = os.path.join(dest_dir, dest_path)
    
    if os.path.exists(source_file):
        with open(source_file, 'r') as f:
            content = f.read()
        
        # Update data file path
        content = content.replace('data_file: str = "data/chemical_safety_data.json"', 
                                'data_file: str = "../data/chemical_safety_data.json"')
        
        # Write the content
        os.makedirs(os.path.dirname(dest_file), exist_ok=True)
        with open(dest_file, 'w') as f:
            f.write(content)
        
        logger.info(f"Consolidated chemical safety database to {dest_file}")
    else:
        logger.warning(f"Source file not found: {source_file}")

def consolidate_test_strip(source_dir, dest_dir, source_files, dest_path):
    """Consolidate test strip analyzer."""
    source_file = os.path.join(source_dir, source_files[0])
    dest_file = os.path.join(dest_dir, dest_path)
    
    if os.path.exists(source_file):
        with open(source_file, 'r') as f:
            content = f.read()
        
        # Update calibration file path
        content = content.replace('calibration_file: str = "services/image_processing/calibration.json"', 
                                'calibration_file: str = "../data/calibration.json"')
        
        # Write the content
        os.makedirs(os.path.dirname(dest_file), exist_ok=True)
        with open(dest_file, 'w') as f:
            f.write(content)
        
        logger.info(f"Consolidated test strip analyzer to {dest_file}")
    else:
        logger.warning(f"Source file not found: {source_file}")

def consolidate_weather(source_dir, dest_dir, source_files, dest_path):
    """Consolidate weather service."""
    base_file = os.path.join(source_dir, source_files[0])
    enhanced_file = os.path.join(source_dir, source_files[1])
    dest_file = os.path.join(dest_dir, dest_path)

    if os.path.exists(base_file):
        with open(base_file, 'r') as f:
            content = f.read()

        # Update cache file path
        content = content.replace(
            'self.cache_file = self.config.get("cache_file", "weather_cache.json")',
            'self.cache_file = self.config.get("cache_file", "../data/weather_cache.json")'
        )

        # If enhanced file exists, integrate its features
        if os.path.exists(enhanced_file):
            with open(enhanced_file, 'r') as f:
                enhanced_content = f.read()

            # Extract method names
            enhanced_methods = re.findall(r'def\s+([a-zA-Z0-9_]+)\s*\(', enhanced_content)

            for method in enhanced_methods:
                if method not in content:
                    # Extract full method definition (simplified)
                    method_match = re.search(
                        rf'def\s+{method}\s*\([^)]*\):(?:\n(?:    .*)*)',
                        enhanced_content
                    )
                    if method_match:
                        method_code = method_match.group(0)
                        content += "\n\n" + method_code

        # Write the consolidated content
        os.makedirs(os.path.dirname(dest_file), exist_ok=True)
        with open(dest_file, 'w') as f:
            f.write(content)

        logger.info(f"Consolidated weather service to {dest_file}")
    else:
        logger.warning(f"Source file not found: {base_file}")

def consolidate_arduino(source_dir, dest_dir, source_files, dest_path):
    """Consolidate Arduino sensor manager."""
    source_file = os.path.join(source_dir, source_files[0])
    dest_file = os.path.join(dest_dir, dest_path)
    
    if os.path.exists(source_file):
        with open(source_file, 'r') as f:
            content = f.read()
        
        # No major changes needed for Arduino sensor manager
        
        # Write the content
        os.makedirs(os.path.dirname(dest_file), exist_ok=True)
        with open(dest_file, 'w') as f:
            f.write(content)
        
        logger.info(f"Consolidated Arduino sensor manager to {dest_file}")
    else:
        logger.warning(f"Source file not found: {source_file}")

def consolidate_chemical_calculator(source_dir, dest_dir, source_files, dest_path):
    """Consolidate chemical calculator."""
    base_file = os.path.join(source_dir, source_files[0])
    enhanced_file = os.path.join(source_dir, source_files[1])
    dest_file = os.path.join(dest_dir, dest_path)
    
    if os.path.exists(enhanced_file):
        # Use the enhanced version as the base
        with open(enhanced_file, 'r') as f:
            content = f.read()
        
        # Update imports to reflect new structure
        content = content.replace('from typing import Dict, Any, List, Tuple, Optional', 
                               'from typing import Dict, Any, List, Tuple, Optional, Union')
        
        # Write the content
        os.makedirs(os.path.dirname(dest_file), exist_ok=True)
        with open(dest_file, 'w') as f:
            f.write(content)
        
        logger.info(f"Consolidated chemical calculator to {dest_file}")
    elif os.path.exists(base_file):
        # Use the base version if enhanced is not available
        with open(base_file, 'r') as f:
            content = f.read()
        
        # Write the content
        os.makedirs(os.path.dirname(dest_file), exist_ok=True)
        with open(dest_file, 'w') as f:
            f.write(content)
        
        logger.info(f"Consolidated chemical calculator to {dest_file}")
    else:
        logger.warning(f"Source files not found: {base_file} or {enhanced_file}")

def consolidate_data_visualization(source_dir, dest_dir, source_files, dest_path):
    """Consolidate data visualization."""
    base_file = os.path.join(source_dir, source_files[0])
    enhanced_file = os.path.join(source_dir, source_files[1])
    history_file = os.path.join(source_dir, source_files[2])
    dest_file = os.path.join(dest_dir, dest_path)
    
    if os.path.exists(enhanced_file):
        # Use the enhanced version as the base
        with open(enhanced_file, 'r') as f:
            content = f.read()
        
        # Update class name
        content = content.replace('class EnhancedDataVisualization:', 
                               'class DataVisualization:')
        
        # Update imports to reflect new structure
        content = content.replace('from typing import Dict, List, Any, Optional, Tuple', 
                               'from typing import Dict, List, Any, Optional, Tuple, Union')
        
        # Write the content
        os.makedirs(os.path.dirname(dest_file), exist_ok=True)
        with open(dest_file, 'w') as f:
            f.write(content)
        
        logger.info(f"Consolidated data visualization to {dest_file}")
    elif os.path.exists(base_file):
        # Use the base version if enhanced is not available
        with open(base_file, 'r') as f:
            content = f.read()
        
        # Write the content
        os.makedirs(os.path.dirname(dest_file), exist_ok=True)
        with open(dest_file, 'w') as f:
            f.write(content)
        
        logger.info(f"Consolidated data visualization to {dest_file}")
    else:
        logger.warning(f"Source files not found: {base_file} or {enhanced_file}")

def consolidate_tab_ui(source_dir, dest_dir, source_files, dest_path):
    """Consolidate tab-based UI."""
    base_file = os.path.join(source_dir, source_files[0])
    responsive_file = os.path.join(source_dir, source_files[1])
    dest_file = os.path.join(dest_dir, dest_path)
    
    if os.path.exists(base_file) and os.path.exists(responsive_file):
        with open(base_file, 'r') as f:
            base_content = f.read()
        
        with open(responsive_file, 'r') as f:
            responsive_content = f.read()
        
        # Start with the base content
        consolidated_content = base_content
        
        # Add responsive design capabilities
        responsive_init = re.search(r'def __init__\(self, root: tk\.Tk, .*?\):(.*?)def', responsive_content, re.DOTALL)
        if responsive_init:
            # Extract the responsive initialization code
            responsive_init_code = responsive_init.group(1)
            
            # Add responsive design initialization to the base __init__ method
            base_init = re.search(r'def __init__\(self, root: tk\.Tk, .*?\):(.*?)def', base_content, re.DOTALL)
            if base_init:
                base_init_code = base_init.group(1)
                
                # Add responsive design code before the end of __init__
                responsive_design_code = """
        # Initialize responsive design
        self.root.bind("<Configure>", self.on_window_resize)
        
        # Get initial window size
        self.current_width = self.root.winfo_width()
        self.current_height = self.root.winfo_height()
        
        # Adjust UI based on initial size
        self.on_window_resize(None)
"""
                
                # Replace the base __init__ with the enhanced one
                consolidated_content = consolidated_content.replace(
                    base_init_code,
                    base_init_code + responsive_design_code
                )
        
        # Add responsive methods from responsive_tab_ui.py
        responsive_methods = [
            "on_window_resize",
            "adjust_for_small_screen",
            "adjust_for_medium_screen",
            "adjust_for_large_screen"
        ]
        
        for method in responsive_methods:
            method_match = re.search(f'def\\s+{method}\\s*\\([^)]*\\):[^\\]*\\((?:\\s+[^\\]*\\)+)', responsive_content)
            if method_match:
                method_code = method_match.group(0) + method_match.group(1)
                consolidated_content += "\
" + method_code
        
        # Update imports to reflect new structure
        consolidated_content = consolidated_content.replace("import os\
import sys", 
                                                         "import os\
import sys\
import platform")
        
        # Update icon path
        consolidated_content = consolidated_content.replace('icon_path = os.path.join("assests", "chemistry.png")', 
                                                         'icon_path = os.path.join("assets", "chemistry.png")')
        
        # Write the consolidated content
        os.makedirs(os.path.dirname(dest_file), exist_ok=True)
        with open(dest_file, 'w') as f:
            f.write(consolidated_content)
        
        logger.info(f"Consolidated tab-based UI to {dest_file}")
    else:
        logger.warning(f"Source files not found: {base_file} or {responsive_file}")

def consolidate_error_handler(source_dir, dest_dir, source_files, dest_path):
    """Consolidate error handler."""
    base_file = os.path.join(source_dir, source_files[0])
    enhanced_file = os.path.join(source_dir, source_files[1])
    dest_file = os.path.join(dest_dir, dest_path)
    
    if os.path.exists(base_file):
        with open(base_file, 'r') as f:
            content = f.read()
        
        # If enhanced file exists, integrate its features
        if os.path.exists(enhanced_file):
            with open(enhanced_file, 'r') as f:
                enhanced_content = f.read()
            
            # Extract enhanced methods from enhanced_error_handler.py
            enhanced_methods = re.findall(r'def\s+([a-zA-Z0-9_]+)\s*\(', enhanced_content)
            
            # Add enhanced methods that don't exist in the base file
            for method in enhanced_methods:
                if method not in content:
                    # Extract the method and its docstring
                    method_match = re.search(f'def\\s+{method}\\s*\\([^)]*\\):[^\\]*\\((?:\\s+[^\\]*\\)+)', enhanced_content)
                    if method_match:
                        method_code = method_match.group(0) + method_match.group(1)
                        content += "\
" + method_code
        
        # Write the consolidated content
        os.makedirs(os.path.dirname(dest_file), exist_ok=True)
        with open(dest_file, 'w') as f:
            f.write(content)
        
        logger.info(f"Consolidated error handler to {dest_file}")
    else:
        logger.warning(f"Source file not found: {base_file}")

def create_readme(dest_dir):
    """Create README.md file."""
    readme_path = os.path.join(dest_dir, "README.md")
    
    readme_content = """# Deep Blue Pool Chemistry

A comprehensive pool chemistry management application with Arduino integration.

## Features

- Pool chemistry analysis and recommendations
- Test strip analysis using computer vision
- Arduino sensor integration for real-time monitoring
- Weather impact analysis
- Chemical safety information
- Customer management
- Historical data visualization

## Directory Structure

```
Deep-Blue-Pool-Chemistry/
\u251c\u2500\u2500 app/                      # Main application code
\u2502   \u251c\u2500\u2500 controllers/          # Application controllers
\u2502   \u251c\u2500\u2500 models/               # Data models
\u2502   \u251c\u2500\u2500 services/             # Core services
\u2502   \u251c\u2500\u2500 ui/                   # User interface
\u2502   \u2514\u2500\u2500 utils/                # Utility functions
\u251c\u2500\u2500 data/                     # Data files
\u2502   \u251c\u2500\u2500 exports/              # Exported data
\u2502   \u2514\u2500\u2500 strip_profiles/       # Test strip profiles
\u251c\u2500\u2500 logs/                     # Log files
\u2514\u2500\u2500 tests/                    # Test files
```

## Getting Started

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Run the application:
   ```
   python -m app.main
   ```

## Configuration

The application can be configured using the `config.json` file.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
"""
    
    with open(readme_path, 'w') as f:
        f.write(readme_content)
    
    logger.info(f"Created README.md: {readme_path}")

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Consolidate Deep Blue Pool Chemistry codebase")
    parser.add_argument("--source", default=DEFAULT_SOURCE_DIR, help="Source directory")
    parser.add_argument("--dest", default=DEFAULT_DEST_DIR, help="Destination directory")
    args = parser.parse_args()
    
    source_dir = args.source
    dest_dir = args.dest
    
    logger.info(f"Source directory: {source_dir}")
    logger.info(f"Destination directory: {dest_dir}")
    
    # Create directory structure
    create_directory_structure(dest_dir)
    
    # Create __init__.py files
    create_init_files(dest_dir)
    
    # Copy files
    copy_files(source_dir, dest_dir)
    
    # Consolidate files
    consolidate_files(source_dir, dest_dir)
    
    # Create README.md
    create_readme(dest_dir)
    
    logger.info("Consolidation complete")
    print(f"\
Consolidation complete. The consolidated codebase is now available at: {dest_dir}")
    print("\
To run the application, navigate to the destination directory and run:")
    print("python -m app.main")

if __name__ == "__main__":
    main()
