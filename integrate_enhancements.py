
#!/usr/bin/env python3
"""
Integration script for Deep Blue Pool Chemistry application enhancements.

This script integrates the new features (unified launcher, notification system,
maintenance scheduler) into the existing application.
"""

import os
import sys
import logging
import shutil
from typing import List, Dict, Any, Optional
import importlib.util
import tkinter as tk

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/integration.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("Integration")

def check_dependencies() -> bool:
    """
    Check if all required dependencies are installed.
    
    Returns:
        True if all dependencies are installed, False otherwise
    """
    required_modules = [
        "tkinter",
        "matplotlib",
        "numpy",
        "PIL",  # Pillow
        "requests",
        "sqlalchemy"
    ]
    
    missing_modules = []
    
    for module in required_modules:
        try:
            importlib.import_module(module)
        except ImportError:
            missing_modules.append(module)
    
    if missing_modules:
        logger.error(f"Missing dependencies: {', '.join(missing_modules)}")
        logger.error("Please install missing dependencies using pip:")
        logger.error(f"pip install {' '.join(missing_modules)}")
        return False
    
    logger.info("All dependencies are installed")
    return True

def create_directories() -> bool:
    """
    Create required directories if they don't exist.
    
    Returns:
        True if successful, False otherwise
    """
    required_dirs = [
        "logs",
        "config",
        "data",
        "data/maintenance_tasks",
        "data/notifications"
    ]
    
    try:
        for directory in required_dirs:
            os.makedirs(directory, exist_ok=True)
            logger.info(f"Created directory: {directory}")
        return True
    except Exception as e:
        logger.error(f"Error creating directories: {e}")
        return False

def backup_files(files_to_backup: List[str]) -> bool:
    """
    Backup existing files before modifying them.
    
    Args:
        files_to_backup: List of files to backup
        
    Returns:
        True if successful, False otherwise
    """
    backup_dir = "backup_" + datetime.now().strftime("%Y%m%d_%H%M%S")
    os.makedirs(backup_dir, exist_ok=True)
    
    try:
        for file_path in files_to_backup:
            if os.path.exists(file_path):
                backup_path = os.path.join(backup_dir, os.path.basename(file_path))
                shutil.copy2(file_path, backup_path)
                logger.info(f"Backed up {file_path} to {backup_path}")
        
        logger.info(f"All files backed up to {backup_dir}")
        return True
    except Exception as e:
        logger.error(f"Error backing up files: {e}")
        return False

def update_main_script() -> bool:
    """
    Update the main script to use the unified launcher.
    
    Returns:
        True if successful, False otherwise
    """
    main_script_path = "main.py"
    
    # Check if main.py exists
    if not os.path.exists(main_script_path):
        logger.warning(f"{main_script_path} not found, creating new file")
        
        # Create new main.py
        try:
            with open(main_script_path, "w") as f:
                f.write("""#!/usr/bin/env python3
\"\"\"
Main entry point for Deep Blue Pool Chemistry application.

This script initializes and runs the application using the unified launcher.
\"\"\"

import os
import sys
import logging
from datetime import datetime

# Configure logging with timestamp in filename
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
log_file = f"logs/pool_app_{timestamp}.log"
os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("PoolApp")

def main():
    \"\"\"Main function.\"\"\"
    # Add the current directory to the Python path
    sys.path.insert(0, os.getcwd())
    
    # Import the unified launcher
    try:
        from unified_launcher import main as run_launcher
        return run_launcher()
    except Exception as e:
        logger.error(f"Error running unified launcher: {e}")
        import traceback
        logger.error(traceback.format_exc())
        
        # Fall back to original main function if unified launcher fails
        try:
            from pool_app import PoolChemistryApp
            app = PoolChemistryApp()
            app.run_gui()
            return 0
        except Exception as e2:
            logger.error(f"Error running fallback: {e2}")
            logger.error(traceback.format_exc())
            return 1

if __name__ == "__main__":
    sys.exit(main())
""")
            logger.info(f"Created new {main_script_path}")
            return True
        except Exception as e:
            logger.error(f"Error creating {main_script_path}: {e}")
            return False
    else:
        # Backup existing main.py
        backup_files([main_script_path])
        
        # Update existing main.py
        try:
            with open(main_script_path, "r") as f:
                content = f.read()
            
            # Check if the file already imports unified_launcher
            if "unified_launcher" in content:
                logger.info(f"{main_script_path} already updated")
                return True
            
            # Update the file
            with open(main_script_path, "w") as f:
                f.write("""#!/usr/bin/env python3
\"\"\"
Main entry point for Deep Blue Pool Chemistry application.

This script initializes and runs the application using the unified launcher.
\"\"\"

import os
import sys
import logging
from datetime import datetime

# Configure logging with timestamp in filename
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
log_file = f"logs/pool_app_{timestamp}.log"
os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("PoolApp")

def main():
    \"\"\"Main function.\"\"\"
    # Add the current directory to the Python path
    sys.path.insert(0, os.getcwd())
    
    # Import the unified launcher
    try:
        from unified_launcher import main as run_launcher
        return run_launcher()
    except Exception as e:
        logger.error(f"Error running unified launcher: {e}")
        import traceback
        logger.error(traceback.format_exc())
        
        # Fall back to original main function
        try:
            # Original main function from previous version
""")
                
                # Extract the original main function
                if "def main():" in content:
                    original_main = content.split("def main():")[1]
                    if "if __name__ == \"__main__\":" in original_main:
                        original_main = original_main.split("if __name__ == \"__main__\":")[0]
                    
                    # Indent the original main function
                    indented_main = "\
".join("            " + line for line in original_main.strip().split("\
"))
                    f.write(indented_main)
                    f.write("\
            return 0\
")
                else:
                    f.write("""
            # Fallback to basic functionality
            from pool_app import PoolChemistryApp
            app = PoolChemistryApp()
            app.run_gui()
            return 0
""")
                
                f.write("""        except Exception as e2:
            logger.error(f"Error running fallback: {e2}")
            logger.error(traceback.format_exc())
            return 1

if __name__ == "__main__":
    sys.exit(main())
""")
            
            logger.info(f"Updated {main_script_path}")
            return True
        except Exception as e:
            logger.error(f"Error updating {main_script_path}: {e}")
            return False

def update_pool_app() -> bool:
    """
    Update the pool_app.py file to integrate the new features.
    
    Returns:
        True if successful, False otherwise
    """
    pool_app_path = "pool_app.py"
    
    # Check if pool_app.py exists
    if not os.path.exists(pool_app_path):
        logger.warning(f"{pool_app_path} not found, cannot update")
        return False
    
    # Backup existing pool_app.py
    backup_files([pool_app_path])
    
    try:
        # Read the file
        with open(pool_app_path, "r") as f:
            content = f.read()
        
        # Check if the file already has the enhancements
        if "notification_system" in content and "maintenance_scheduler" in content:
            logger.info(f"{pool_app_path} already updated")
            return True
        
        # Find the imports section
        import_section_end = content.find("# Configure logging")
        if import_section_end == -1:
            import_section_end = content.find("logging.basicConfig")
        
        if import_section_end == -1:
            logger.warning(f"Could not find import section in {pool_app_path}")
            return False
        
        # Add new imports
        new_imports = """
# Import enhancement modules
from notification_system import NotificationManager, NotificationCenter, ChemicalAlertMonitor
from maintenance_scheduler import MaintenanceScheduler, MaintenanceSchedulerUI
"""
        
        updated_content = content[:import_section_end] + new_imports + content[import_section_end:]
        
        # Find the PoolChemistryApp class
        class_start = updated_content.find("class PoolChemistryApp:")
        if class_start == -1:
            logger.warning(f"Could not find PoolChemistryApp class in {pool_app_path}")
            return False
        
        # Find the __init__ method
        init_start = updated_content.find("def __init__", class_start)
        if init_start == -1:
            logger.warning(f"Could not find __init__ method in {pool_app_path}")
            return False
        
        # Find the end of the __init__ method
        init_end = updated_content.find("def ", init_start + 1)
        if init_end == -1:
            init_end = len(updated_content)
        
        # Add notification and maintenance scheduler initialization
        init_code = updated_content[init_start:init_end]
        
        # Check if the last line is indented
        last_lines = init_code.strip().split("\
")
        if last_lines and last_lines[-1].startswith("        "):
            indent = "        "
        else:
            indent = "    "
        
        # Add new initialization code
        new_init_code = f"""
{indent}# Initialize notification system
{indent}self.notification_manager = NotificationManager()
{indent}
{indent}# Initialize maintenance scheduler
{indent}self.maintenance_scheduler = MaintenanceScheduler()
"""
        
        updated_init = init_code + new_init_code
        updated_content = updated_content[:init_start] + updated_init + updated_content[init_end:]
        
        # Find the run_gui method
        run_gui_start = updated_content.find("def run_gui", init_end)
        if run_gui_start == -1:
            logger.warning(f"Could not find run_gui method in {pool_app_path}")
            return False
        
        # Find the end of the run_gui method
        run_gui_end = updated_content.find("def ", run_gui_start + 1)
        if run_gui_end == -1:
            run_gui_end = len(updated_content)
        
        # Add notification center and maintenance scheduler UI initialization
        run_gui_code = updated_content[run_gui_start:run_gui_end]
        
        # Find where to insert the new code
        # Look for mainloop() call
        mainloop_pos = run_gui_code.find("mainloop()")
        if mainloop_pos == -1:
            logger.warning(f"Could not find mainloop() call in run_gui method")
            return False
        
        # Find the line with mainloop()
        lines = run_gui_code[:mainloop_pos].split("\
")
        mainloop_line = -1
        for i, line in enumerate(lines):
            if "mainloop()" in line:
                mainloop_line = i
                break
        
        if mainloop_line == -1:
            logger.warning(f"Could not find mainloop() line in run_gui method")
            return False
        
        # Get the indentation
        indent = ""
        for char in lines[mainloop_line]:
            if char.isspace():
                indent += char
            else:
                break
        
        # Add new UI initialization code before mainloop()
        new_run_gui_code = f"""
{indent}# Initialize notification center
{indent}self.notification_center = NotificationCenter(root, self.notification_manager)
{indent}
{indent}# Initialize maintenance scheduler UI
{indent}self.maintenance_scheduler_ui = MaintenanceSchedulerUI(root, self.maintenance_scheduler)
{indent}
{indent}# Start monitoring for notifications
{indent}self.chemical_alert_monitor = ChemicalAlertMonitor(
{indent}    self.notification_manager,
{indent}    self.db_service
{indent})
{indent}self.chemical_alert_monitor.start()
"""
        
        # Insert the new code before mainloop()
        updated_run_gui = run_gui_code[:mainloop_pos - len(lines[mainloop_line])] + new_run_gui_code + run_gui_code[mainloop_pos - len(lines[mainloop_line]):]
        updated_content = updated_content[:run_gui_start] + updated_run_gui + updated_content[run_gui_end:]
        
        # Write the updated content
        with open(pool_app_path, "w") as f:
            f.write(updated_content)
        
        logger.info(f"Updated {pool_app_path}")
        return True
    except Exception as e:
        logger.error(f"Error updating {pool_app_path}: {e}")
        return False

def create_run_all_script() -> bool:
    """
    Create a script to run all versions of the application.
    
    Returns:
        True if successful, False otherwise
    """
    run_all_script_path = "run_all.py"
    
    try:
        with open(run_all_script_path, "w") as f:
            f.write("""#!/usr/bin/env python3
\"\"\"
Run script for Deep Blue Pool Chemistry application.

This script runs the unified launcher, which provides access to all versions
of the application.
\"\"\"

import os
import sys
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/run_all.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("RunAll")

def main():
    \"\"\"Main function.\"\"\"
    # Add the current directory to the Python path
    sys.path.insert(0, os.getcwd())
    
    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)
    
    # Import and run the unified launcher
    try:
        from unified_launcher import main as run_launcher
        return run_launcher()
    except Exception as e:
        logger.error(f"Error running unified launcher: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return 1

if __name__ == "__main__":
    sys.exit(main())
""")
        
        # Make the script executable
        os.chmod(run_all_script_path, 0o755)
        
        logger.info(f"Created {run_all_script_path}")
        return True
    except Exception as e:
        logger.error(f"Error creating {run_all_script_path}: {e}")
        return False

def create_config_files() -> bool:
    """
    Create configuration files for the new features.
    
    Returns:
        True if successful, False otherwise
    """
    config_files = {
        "config/launcher_config.json": """{
    "theme": "light",
    "last_used_version": "standard",
    "show_welcome": true,
    "check_updates": true,
    "recent_files": []
}""",
        "config/notification_config.json": """{
    "enabled": true,
    "display_time": 5,
    "max_notifications": 100,
    "auto_cleanup_days": 30,
    "notification_sound": true,
    "desktop_notifications": true,
    "email_notifications": false,
    "email_settings": {
        "smtp_server": "",
        "smtp_port": 587,
        "username": "",
        "password": "",
        "from_address": "",
        "to_address": ""
    },
    "notification_levels": {
        "info": true,
        "warning": true,
        "alert": true,
        "critical": true
    },
    "notification_categories": {
        "chemistry": true,
        "maintenance": true,
        "system": true,
        "weather": true,
        "custom": true
    }
}""",
        "config/maintenance_config.json": """{
    "data_file": "data/maintenance_tasks.json",
    "default_categories": [
        "chemical",
        "equipment",
        "cleaning",
        "inspection",
        "general"
    ],
    "default_priorities": [
        "low",
        "medium",
        "high"
    ],
    "default_frequencies": {
        "daily": 1,
        "weekly": 7,
        "biweekly": 14,
        "monthly": 30,
        "quarterly": 90,
        "semiannually": 182,
        "annually": 365
    },
    "reminder_days": [1, 3, 7],
    "auto_suggest": true,
    "enable_notifications": true
}"""
    }
    
    try:
        for file_path, content in config_files.items():
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Only create the file if it doesn't exist
            if not os.path.exists(file_path):
                with open(file_path, "w") as f:
                    f.write(content)
                logger.info(f"Created {file_path}")
            else:
                logger.info(f"{file_path} already exists, skipping")
        
        return True
    except Exception as e:
        logger.error(f"Error creating config files: {e}")
        return False

def create_documentation() -> bool:
    """
    Create documentation for the new features.
    
    Returns:
        True if successful, False otherwise
    """
    docs_dir = "docs"
    os.makedirs(docs_dir, exist_ok=True)
    
    doc_files = {
        "docs/unified_launcher.md": """# Unified Launcher

The Unified Launcher is a central hub for accessing all versions of the Deep Blue Pool Chemistry application.

## Features

- Access to all versions of the application (Standard UI, Responsive UI, Enhanced Data Visualization)
- Settings management
- Recent files tracking
- Documentation access
- Theme customization

## Usage

To start the Unified Launcher, run:

```bash
python run_all.py
```

Or directly:

```bash
python unified_launcher.py
```

## Configuration

The Unified Launcher can be configured by editing the `config/launcher_config.json` file.

Available settings:
- `theme`: UI theme ("light" or "dark")
- `last_used_version`: Last used application version
- `show_welcome`: Whether to show the welcome screen at startup
- `check_updates`: Whether to check for updates at startup
- `recent_files`: List of recently opened files
""",
        "docs/notification_system.md": """# Notification System

The Notification System provides alerts for important events in the Deep Blue Pool Chemistry application.

## Features

- Chemical alerts when pool chemistry is out of balance
- Maintenance reminders for scheduled tasks
- System notifications for application events
- Weather alerts for conditions affecting pool chemistry
- Custom notifications for user-defined events

## Notification Levels

- **Info**: General information
- **Warning**: Potential issues that should be addressed
- **Alert**: Important issues that require attention
- **Critical**: Urgent issues that require immediate attention

## Configuration

The Notification System can be configured by editing the `config/notification_config.json` file.

Available settings:
- `enabled`: Whether notifications are enabled
- `display_time`: How long notifications are displayed (in seconds)
- `max_notifications`: Maximum number of notifications to store
- `auto_cleanup_days`: Number of days after which old notifications are automatically deleted
- `notification_sound`: Whether to play a sound when a notification is received
- `desktop_notifications`: Whether to show desktop notifications
- `email_notifications`: Whether to send email notifications
- `email_settings`: Email notification settings
- `notification_levels`: Which notification levels are enabled
- `notification_categories`: Which notification categories are enabled
""",
        "docs/maintenance_scheduler.md": """# Maintenance Scheduler

The Maintenance Scheduler helps you keep track of regular pool maintenance tasks.

## Features

- Schedule recurring maintenance tasks
- Track task completion
- View upcoming and overdue tasks
- Calendar view for task scheduling
- Statistics on maintenance history
- Task categories and priorities

## Task Properties

- **Name**: Task name
- **Description**: Task description
- **Frequency**: How often the task should be performed (in days)
- **Last Completed**: When the task was last completed
- **Next Due**: When the task is next due
- **Priority**: Task priority (low, medium, high)
- **Category**: Task category (chemical, equipment, cleaning, inspection, general)
- **Notes**: Additional notes about the task

## Configuration

The Maintenance Scheduler can be configured by editing the `config/maintenance_config.json` file.

Available settings:
- `data_file`: File where maintenance tasks are stored
- `default_categories`: Default task categories
- `default_priorities`: Default task priorities
- `default_frequencies`: Default task frequencies
- `reminder_days`: Days before due date to send reminders
- `auto_suggest`: Whether to auto-suggest tasks based on pool type
- `enable_notifications`: Whether to send notifications for due tasks
"""
    }
    
    try:
        for file_path, content in doc_files.items():
            with open(file_path, "w") as f:
                f.write(content)
            logger.info(f"Created {file_path}")
        
        return True
    except Exception as e:
        logger.error(f"Error creating documentation: {e}")
        return False

def update_readme() -> bool:
    """
    Update the README.md file to include information about the new features.
    
    Returns:
        True if successful, False otherwise
    """
    readme_path = "README.md"
    
    if not os.path.exists(readme_path):
        logger.warning(f"{readme_path} not found, creating new file")
        
        try:
            with open(readme_path, "w") as f:
                f.write("""# Deep Blue Pool Chemistry

A comprehensive application for managing pool chemistry and maintenance.

## Features

- **Pool Chemistry Management**: Test and track pool chemistry parameters
- **Chemical Dosage Calculator**: Calculate chemical dosages based on test results
- **Test Strip Analyzer**: Analyze test strips using your camera
- **Weather Impact Analysis**: Analyze weather impact on pool chemistry
- **Maintenance Scheduler**: Schedule and track regular maintenance tasks
- **Notification System**: Get alerts for chemical issues and maintenance tasks
- **Data Visualization**: Visualize pool chemistry data with interactive charts
- **Mobile Responsive UI**: Use the application on any device

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/valcalepi/Deep-Blue-Pool-Chemistry.git
   cd Deep-Blue-Pool-Chemistry
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python run_all.py
   ```

## Documentation

- [Unified Launcher](docs/unified_launcher.md)
- [Notification System](docs/notification_system.md)
- [Maintenance Scheduler](docs/maintenance_scheduler.md)

## License

This project is licensed under the MIT License - see the LICENSE file for details.
""")
            logger.info(f"Created new {readme_path}")
            return True
        except Exception as e:
            logger.error(f"Error creating {readme_path}: {e}")
            return False
    else:
        # Backup existing README.md
        backup_files([readme_path])
        
        try:
            # Read the file
            with open(readme_path, "r") as f:
                content = f.read()
            
            # Check if the file already has the new features
            if "Maintenance Scheduler" in content and "Notification System" in content:
                logger.info(f"{readme_path} already updated")
                return True
            
            # Find the features section
            features_start = content.find("## Features")
            if features_start == -1:
                # No features section, add it
                features_section = """
## Features

- **Pool Chemistry Management**: Test and track pool chemistry parameters
- **Chemical Dosage Calculator**: Calculate chemical dosages based on test results
- **Test Strip Analyzer**: Analyze test strips using your camera
- **Weather Impact Analysis**: Analyze weather impact on pool chemistry
- **Maintenance Scheduler**: Schedule and track regular maintenance tasks
- **Notification System**: Get alerts for chemical issues and maintenance tasks
- **Data Visualization**: Visualize pool chemistry data with interactive charts
- **Mobile Responsive UI**: Use the application on any device
"""
                
                # Find a good place to insert the features section
                installation_start = content.find("## Installation")
                if installation_start != -1:
                    updated_content = content[:installation_start] + features_section + content[installation_start:]
                else:
                    updated_content = content + "\
" + features_section
            else:
                # Find the end of the features section
                next_section = content.find("##", features_start + 10)
                if next_section == -1:
                    next_section = len(content)
                
                features_section = content[features_start:next_section]
                
                # Add new features if they don't exist
                new_features = []
                if "Maintenance Scheduler" not in features_section:
                    new_features.append("- **Maintenance Scheduler**: Schedule and track regular maintenance tasks")
                if "Notification System" not in features_section:
                    new_features.append("- **Notification System**: Get alerts for chemical issues and maintenance tasks")
                
                if new_features:
                    # Add new features to the end of the features section
                    updated_features = features_section.rstrip() + "\
" + "\
".join(new_features) + "\
"
                    updated_content = content[:features_start] + updated_features + content[next_section:]
                else:
                    updated_content = content
            
            # Add documentation section if it doesn't exist
            if "## Documentation" not in updated_content:
                docs_section = """
## Documentation

- [Unified Launcher](docs/unified_launcher.md)
- [Notification System](docs/notification_system.md)
- [Maintenance Scheduler](docs/maintenance_scheduler.md)
"""
                
                # Find a good place to insert the documentation section
                license_start = updated_content.find("## License")
                if license_start != -1:
                    updated_content = updated_content[:license_start] + docs_section + updated_content[license_start:]
                else:
                    updated_content = updated_content + "\
" + docs_section
            
            # Write the updated content
            with open(readme_path, "w") as f:
                f.write(updated_content)
            
            logger.info(f"Updated {readme_path}")
            return True
        except Exception as e:
            logger.error(f"Error updating {readme_path}: {e}")
            return False

def update_requirements() -> bool:
    """
    Update the requirements.txt file to include new dependencies.
    
    Returns:
        True if successful, False otherwise
    """
    requirements_path = "requirements.txt"
    
    if not os.path.exists(requirements_path):
        logger.warning(f"{requirements_path} not found, creating new file")
        
        try:
            with open(requirements_path, "w") as f:
                f.write("""# Core dependencies
numpy>=1.20.0
opencv-python>=4.5.0
Pillow>=8.0.0
matplotlib>=3.4.0
requests>=2.25.0

# Database
SQLAlchemy>=1.4.0

# GUI
tk>=0.1.0  # This is part of Python's standard library but listed for clarity

# Testing
pytest>=6.2.0
pytest-cov>=2.12.0

# Documentation
Sphinx>=4.0.0
sphinx-rtd-theme>=0.5.0

# Development tools
black>=21.5b2
flake8>=3.9.0
mypy>=0.812
isort>=5.8.0
""")
            logger.info(f"Created new {requirements_path}")
            return True
        except Exception as e:
            logger.error(f"Error creating {requirements_path}: {e}")
            return False
    else:
        # No need to update requirements.txt as we're not adding new dependencies
        logger.info(f"{requirements_path} already exists, no updates needed")
        return True

def main():
    """Main function."""
    from datetime import datetime
    
    logger.info("Starting integration of enhancements")
    
    # Check dependencies
    if not check_dependencies():
        logger.error("Missing dependencies, please install them and try again")
        return 1
    
    # Create directories
    if not create_directories():
        logger.error("Failed to create directories")
        return 1
    
    # Create config files
    if not create_config_files():
        logger.error("Failed to create config files")
        return 1
    
    # Update main script
    if not update_main_script():
        logger.warning("Failed to update main script")
    
    # Update pool_app.py
    if not update_pool_app():
        logger.warning("Failed to update pool_app.py")
    
    # Create run_all script
    if not create_run_all_script():
        logger.warning("Failed to create run_all script")
    
    # Create documentation
    if not create_documentation():
        logger.warning("Failed to create documentation")
    
    # Update README
    if not update_readme():
        logger.warning("Failed to update README")
    
    # Update requirements
    if not update_requirements():
        logger.warning("Failed to update requirements")
    
    logger.info("Integration completed successfully")
    logger.info("To run the application with the new features, use: python run_all.py")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
