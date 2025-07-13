import os
import re

def fix_imports(directory):
    """Fix import statements in Python files"""
    for root, dirs, files in os.walk(directory):
        # Skip venv directory
        if 'venv' in dirs:
            dirs.remove('venv')
            
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                fix_file_imports(file_path)

def fix_file_imports(file_path):
    """Fix import statements in a single Python file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Fix specific import issues
        
        # 1. Fix services.weather_service to services.weather.weather_service
        content = re.sub(
            r'from services\.weather_service import', 
            'from services.weather.weather_service import', 
            content
        )
        
        # 2. Fix app.gui_controller to use relative imports
        if 'app/gui_elements.py' in file_path or 'app\\gui_elements.py' in file_path:
            content = re.sub(
                r'from app\.gui_controller import', 
                'from .gui_controller import', 
                content
            )
        
        # 3. Fix config path in integrated_app.py
        if 'integrated_app.py' in file_path:
            content = re.sub(
                r"with open\('config/config\.json', 'r'\) as f:", 
                "with open('config.json', 'r') as f:", 
                content
            )
        
        # Write the fixed content back to the file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"Fixed imports in {file_path}")
    except UnicodeDecodeError:
        print(f"Skipping {file_path} - encoding issue")
    except Exception as e:
        print(f"Error processing {file_path}: {e}")

if __name__ == "__main__":
    fix_imports('.')