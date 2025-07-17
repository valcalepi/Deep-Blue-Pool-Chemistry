
#!/usr/bin/env python3
"""
Setup script for Deep Blue Pool Chemistry application.

This script helps users install the application and its dependencies.
"""

import os
import sys
import json
import subprocess
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("Error: Python 3.8 or higher is required.")
        sys.exit(1)
    print(f"Python version {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro} detected.")

def install_dependencies():
    """Install required dependencies."""
    print("Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("Dependencies installed successfully.")
    except subprocess.CalledProcessError:
        print("Error: Failed to install dependencies.")
        sys.exit(1)

def create_directories():
    """Create necessary directories."""
    print("Creating directories...")
    directories = ["data", "services/image_processing"]
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    print("Directories created successfully.")

def create_default_config():
    """Create default configuration file if it doesn't exist."""
    config_path = Path("config.json")
    if not config_path.exists():
        print("Creating default configuration...")
        default_config = {
            "database": {
                "path": "data/pool_data.db"
            },
            "chemical_safety": {
                "data_file": "data/chemical_safety_data.json"
            },
            "test_strip": {
                "brand": "default",
                "calibration_file": "data/calibration.json"
            },
            "weather": {
                "location": "Florida",
                "update_interval": 3600,
                "cache_file": "data/weather_cache.json",
                "zip_code": "33101"
            },
            "general": {
                "user_name": "Pool Owner",
                "data_directory": "data",
                "auto_backup": False
            },
            "pool": {
                "size": "10000",
                "type": "chlorine",
                "test_strip_brand": "default"
            },
            "display": {
                "theme": "light",
                "font_size": "normal",
                "chart_dpi": "100"
            }
        }
        with open(config_path, "w") as f:
            json.dump(default_config, f, indent=4)
        print("Default configuration created.")
    else:
        print("Configuration file already exists.")

def create_default_calibration():
    """Create default calibration file if it doesn't exist."""
    calibration_path = Path("data/calibration.json")
    if not calibration_path.exists():
        print("Creating default calibration data...")
        default_calibration = {
            "pH": [
                {"rgb": [180, 100, 90], "value": 6.8},
                {"rgb": [200, 120, 100], "value": 7.2},
                {"rgb": [220, 140, 110], "value": 7.6}
            ],
            "free_chlorine": [
                {"rgb": [100, 200, 180], "value": 0.5},
                {"rgb": [120, 220, 200], "value": 1.0},
                {"rgb": [140, 240, 220], "value": 2.0}
            ],
            "total_chlorine": [
                {"rgb": [150, 150, 100], "value": 0.5},
                {"rgb": [170, 170, 120], "value": 1.0},
                {"rgb": [190, 190, 140], "value": 2.0}
            ],
            "alkalinity": [
                {"rgb": [200, 100, 200], "value": 40},
                {"rgb": [220, 120, 220], "value": 80},
                {"rgb": [240, 140, 240], "value": 120}
            ],
            "calcium": [
                {"rgb": [100, 100, 200], "value": 100},
                {"rgb": [120, 120, 220], "value": 200},
                {"rgb": [140, 140, 240], "value": 300}
            ],
            "cyanuric_acid": [
                {"rgb": [200, 200, 100], "value": 20},
                {"rgb": [220, 220, 120], "value": 40},
                {"rgb": [240, 240, 140], "value": 60}
            ],
            "bromine": [
                {"rgb": [150, 100, 150], "value": 1.0},
                {"rgb": [170, 120, 170], "value": 3.0},
                {"rgb": [190, 140, 190], "value": 5.0}
            ],
            "salt": [
                {"rgb": [100, 150, 150], "value": 1000},
                {"rgb": [120, 170, 170], "value": 2000},
                {"rgb": [140, 190, 190], "value": 3000}
            ]
        }
        with open(calibration_path, "w") as f:
            json.dump(default_calibration, f, indent=4)
        print("Default calibration data created.")
    else:
        print("Calibration file already exists.")

def create_default_pad_zones():
    """Create default pad zones file if it doesn't exist."""
    pad_zones_path = Path("data/pad_zones.json")
    if not pad_zones_path.exists():
        print("Creating default pad zones data...")
        default_pad_zones = {
            "default": {
                "pH": [50, 50, 40, 40],
                "free_chlorine": [100, 50, 40, 40],
                "total_chlorine": [150, 50, 40, 40],
                "alkalinity": [200, 50, 40, 40],
                "calcium": [250, 50, 40, 40],
                "cyanuric_acid": [300, 50, 40, 40],
                "bromine": [350, 50, 40, 40],
                "salt": [400, 50, 40, 40]
            }
        }
        with open(pad_zones_path, "w") as f:
            json.dump(default_pad_zones, f, indent=4)
        print("Default pad zones data created.")
    else:
        print("Pad zones file already exists.")

def create_default_chemical_safety_data():
    """Create default chemical safety data file if it doesn't exist."""
    safety_path = Path("data/chemical_safety_data.json")
    if not safety_path.exists():
        print("Creating default chemical safety data...")
        default_safety_data = {
            "chemicals": {
                "chlorine": {
                    "name": "Chlorine",
                    "chemical_formula": "Cl\u2082",
                    "hazard_rating": 3,
                    "safety_precautions": [
                        "Wear protective gloves and eye protection",
                        "Use in well-ventilated areas",
                        "Keep away from acids to prevent chlorine gas formation"
                    ],
                    "storage_guidelines": "Store in cool, dry place away from direct sunlight and incompatible materials",
                    "emergency_procedures": "In case of exposure, move to fresh air and seek medical attention"
                },
                "muriatic_acid": {
                    "name": "Muriatic Acid (Hydrochloric Acid)",
                    "chemical_formula": "HCl",
                    "hazard_rating": 3,
                    "safety_precautions": [
                        "Always add acid to water, never water to acid",
                        "Wear chemical-resistant gloves, goggles, and protective clothing",
                        "Use in well-ventilated areas"
                    ],
                    "storage_guidelines": "Store in original container in cool, well-ventilated area away from bases",
                    "emergency_procedures": "For skin contact, flush with water for 15 minutes and seek medical attention"
                },
                "sodium_bicarbonate": {
                    "name": "Sodium Bicarbonate (Baking Soda)",
                    "chemical_formula": "NaHCO\u2083",
                    "hazard_rating": 1,
                    "safety_precautions": [
                        "Minimal safety equipment required",
                        "Avoid generating dust"
                    ],
                    "storage_guidelines": "Store in dry area in sealed container",
                    "emergency_procedures": "If in eyes, rinse with water"
                },
                "calcium_hypochlorite": {
                    "name": "Calcium Hypochlorite",
                    "chemical_formula": "Ca(ClO)\u2082",
                    "hazard_rating": 3,
                    "safety_precautions": [
                        "Wear protective gloves, clothing, and eye protection",
                        "Keep away from heat and combustible materials",
                        "Never mix with acids or ammonia"
                    ],
                    "storage_guidelines": "Store in cool, dry place away from acids and organic materials",
                    "emergency_procedures": "In case of fire, use water spray. For exposure, seek medical attention"
                },
                "cyanuric_acid": {
                    "name": "Cyanuric Acid",
                    "chemical_formula": "C\u2083H\u2083N\u2083O\u2083",
                    "hazard_rating": 1,
                    "safety_precautions": [
                        "Avoid dust formation",
                        "Use with adequate ventilation"
                    ],
                    "storage_guidelines": "Store in dry, cool place in closed containers",
                    "emergency_procedures": "If inhaled, move to fresh air"
                }
            },
            "compatibility": {
                "chlorine": {
                    "muriatic_acid": 0,
                    "sodium_bicarbonate": 1,
                    "calcium_hypochlorite": 1,
                    "cyanuric_acid": 1
                },
                "muriatic_acid": {
                    "chlorine": 0,
                    "sodium_bicarbonate": 0,
                    "calcium_hypochlorite": 0,
                    "cyanuric_acid": 1
                },
                "sodium_bicarbonate": {
                    "chlorine": 1,
                    "muriatic_acid": 0,
                    "calcium_hypochlorite": 1,
                    "cyanuric_acid": 1
                },
                "calcium_hypochlorite": {
                    "chlorine": 1,
                    "muriatic_acid": 0,
                    "sodium_bicarbonate": 1,
                    "cyanuric_acid": 1
                },
                "cyanuric_acid": {
                    "chlorine": 1,
                    "muriatic_acid": 1,
                    "sodium_bicarbonate": 1,
                    "calcium_hypochlorite": 1
                }
            }
        }
        with open(safety_path, "w") as f:
            json.dump(default_safety_data, f, indent=4)
        print("Default chemical safety data created.")
    else:
        print("Chemical safety data file already exists.")

def initialize_database():
    """Initialize the database."""
    print("Initializing database...")
    try:
        from database_service import DatabaseService
        db_path = "data/pool_data.db"
        db = DatabaseService(db_path)
        print("Database initialized successfully.")
    except Exception as e:
        print(f"Error initializing database: {e}")
        sys.exit(1)

def run_tests():
    """Run tests to verify installation."""
    print("Running tests...")
    try:
        import unittest
        from comprehensive_test import DeepBluePoolChemistryTests
        
        # Run only the database test as a quick verification
        suite = unittest.TestSuite()
        suite.addTest(DeepBluePoolChemistryTests("test_database_service"))
        
        runner = unittest.TextTestRunner()
        result = runner.run(suite)
        
        if result.wasSuccessful():
            print("Tests passed successfully.")
        else:
            print("Some tests failed. Please check the output above for details.")
    except Exception as e:
        print(f"Error running tests: {e}")

def main():
    """Main setup function."""
    print("Setting up Deep Blue Pool Chemistry application...")
    
    check_python_version()
    install_dependencies()
    create_directories()
    create_default_config()
    create_default_calibration()
    create_default_pad_zones()
    create_default_chemical_safety_data()
    initialize_database()
    run_tests()
    
    print("\
Setup completed successfully!")
    print("\
To run the application:")
    print("  GUI mode: python main.py")
    print("  CLI mode: python main.py --cli")
    print("\
For more information, see the documentation in the docs/ directory.")

if __name__ == "__main__":
    main()
