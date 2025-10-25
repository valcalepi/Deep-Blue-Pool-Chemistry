# C:\Scripts\Deep Blue scripts and files\pool_controller\test_import.py
import os
import sys
import importlib

def print_separator():
    print("\n" + "="*50 + "\n")

# Print current directory and Python path
print("Current directory:", os.getcwd())
print("Python executable:", sys.executable)
print("Python version:", sys.version)
print_separator()

# Print the Python path
print("Python path:")
for path in sys.path:
    print(f"  - {path}")
print_separator()

# Check if cryptography is installed
try:
    import cryptography
    print(f"Cryptography is installed (version: {cryptography.__version__})")
except ImportError:
    print("Cryptography is NOT installed")
print_separator()

# Try different import approaches
print("Attempting imports...")

# Approach 1: Direct import
print("\nApproach 1: Direct import")
try:
    from src.utils import encrypt_data
    print("✓ Success! Imported encrypt_data from src.utils")
    print(f"Function: {encrypt_data}")
except ImportError as e:
    print(f"✗ Failed: {e}")

# Approach 2: Import after adding directory to path
print("\nApproach 2: Import after adding directory to path")
try:
    # Add the current directory to the path
    if os.getcwd() not in sys.path:
        sys.path.insert(0, os.getcwd())
    from src.utils import encrypt_data
    print("✓ Success! Imported encrypt_data from src.utils")
    print(f"Function: {encrypt_data}")
except ImportError as e:
    print(f"✗ Failed: {e}")

# Approach 3: Import using importlib
print("\nApproach 3: Import using importlib")
try:
    utils = importlib.import_module("src.utils")
    encrypt_data = getattr(utils, "encrypt_data")
    print("✓ Success! Imported encrypt_data using importlib")
    print(f"Function: {encrypt_data}")
except (ImportError, AttributeError) as e:
    print(f"✗ Failed: {e}")

# Approach 4: Check if the file exists and is accessible
print("\nApproach 4: Check if utils.py exists")
utils_path = os.path.join(os.getcwd(), "src", "utils.py")
if os.path.exists(utils_path):
    print(f"✓ File exists: {utils_path}")
    print(f"  File size: {os.path.getsize(utils_path)} bytes")
    print(f"  Last modified: {os.path.getmtime(utils_path)}")
    
    # Try to read the first few lines
    try:
        with open(utils_path, 'r') as f:
            first_lines = [next(f) for _ in range(10)]
        print("  First few lines:")
        for line in first_lines:
            print(f"    {line.rstrip()}")
    except Exception as e:
        print(f"  Error reading file: {e}")
else:
    print(f"✗ File does not exist: {utils_path}")

print_separator()

# Test if we can create a key and encrypt data
print("Testing encryption functionality:")
try:
    # Try to import the functions directly
    sys.path.insert(0, os.path.join(os.getcwd(), "src"))
    from utils import generate_key, encrypt_data, decrypt_data
    
    # Generate a key
    key = generate_key()
    if key:
        print(f"✓ Generated key: {key[:10]}...{key[-10:]}")
        
        # Encrypt some data
        test_data = "Hello, World!"
        encrypted = encrypt_data(test_data, key)
        if encrypted:
            print(f"✓ Encrypted data: {encrypted[:10]}...{encrypted[-10:]}")
            
            # Decrypt the data
            decrypted = decrypt_data(encrypted, key)
            if decrypted == test_data:
                print(f"✓ Decrypted data matches original: {decrypted}")
            else:
                print(f"✗ Decryption failed or data doesn't match: {decrypted}")
        else:
            print("✗ Encryption failed")
    else:
        print("✗ Key generation failed")
except Exception as e:
    print(f"✗ Error testing encryption: {e}")

print_separator()
print("Test complete!")
