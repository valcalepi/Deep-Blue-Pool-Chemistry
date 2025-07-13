
import os
import re
import sys

def find_python_files(directory):
    """Find all Python files in the given directory and its subdirectories"""
    python_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    return python_files

def extract_imports(file_path):
    """Extract all import statements from a Python file"""
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Find all import statements
    import_pattern = r'^(?:from\s+(\S+)\s+import\s+.*|import\s+(\S+)(?:\s+as\s+\S+)?(?:,\s+(\S+)(?:\s+as\s+\S+)?)*)'
    imports = []
    
    for line in content.split('\
'):
        match = re.match(import_pattern, line)
        if match:
            if match.group(1):  # from X import Y
                imports.append(match.group(1))
            else:  # import X, Y, Z
                for i in range(2, len(match.groups()) + 1):
                    if match.group(i):
                        imports.append(match.group(i))
    
    return imports

def check_imports(directory):
    """Check all imports in Python files in the given directory"""
    python_files = find_python_files(directory)
    print(f"Found {len(python_files)} Python files")
    
    all_imports = {}
    for file_path in python_files:
        imports = extract_imports(file_path)
        all_imports[file_path] = imports
    
    # Check for potential issues
    for file_path, imports in all_imports.items():
        print(f"\
Checking {file_path}:")
        for imp in imports:
            # Skip standard library modules and relative imports
            if imp.startswith('.') or imp in sys.builtin_module_names:
                continue
            
            try:
                __import__(imp.split('.')[0])
                print(f"  \u2713 {imp}")
            except ImportError:
                print(f"  \u2717 {imp} - Import Error")

if __name__ == "__main__":
    check_imports('.')
