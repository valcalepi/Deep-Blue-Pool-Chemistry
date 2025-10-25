# constants.py
# Updated: July 04, 2025
# This file centralizes all constants used in the Pool Management System application
# to ensure consistency across all screens and windows

# Application metadata
APP_NAME = "Deep Blue Chemistry Pool Management System"
APP_VERSION = "2.0.0"
APP_AUTHOR = "Virtual Control LLC"
APP_COPYRIGHT = "Copyright © 2025 Virtual Control LLC"

# Window dimensions and properties
# Using consistent window size across all screens to fix inconsistency issues
WINDOW_TITLE = "Pool Management System"
DEFAULT_WINDOW_SIZE = (1400, 1000)  # Width, height in pixels
MIN_WINDOW_SIZE = (800, 600)        # Minimum window size (used in gui_elements.py)
WINDOW_WIDTH = 1024                 # Default width for non-resizable windows
WINDOW_HEIGHT = 768                 # Default height for non-resizable windows
WINDOW_MIN_WIDTH = MIN_WINDOW_SIZE[0]  # For backward compatibility
WINDOW_MIN_HEIGHT = MIN_WINDOW_SIZE[1] # For backward compatibility

# Colors
BACKGROUND_COLOR = "#f0f0f0"
PRIMARY_COLOR = "#0078D7"
SECONDARY_COLOR = "#E1E1E1"
TEXT_COLOR = "#333333"
HIGHLIGHT_COLOR = "#0056b3"
ERROR_COLOR = "#FF0000"
SUCCESS_COLOR = "#00AA00"

# Extended color scheme
COLOR_SCHEME = {
    'primary': "#2196F3",    # Material Blue
    'secondary': "#BBDEFB",  # Light Blue
    'success': "#4CAF50",    # Green
    'warning': "#FFC107",    # Yellow
    'danger': "#F44336",     # Red
    'info': "#03A9F4",       # Light Blue
    'background': "#F5F5F5"  # Light Gray
}

# Graph colors
GRAPH_COLORS = {
    'pH': "#2196F3",
    'Chlorine': "#4CAF50",
    'Alkalinity': "#FFC107",
    'Hardness': "#9C27B0",
    'Stabilizer': "#FF5722"
}

# Fonts
FONT_FAMILY = "Arial"
FONT_SIZE_SMALL = 10
FONT_SIZE_NORMAL = 12
FONT_SIZE_LARGE = 14
FONT_SIZE_TITLE = 18
FONT_SIZE_HEADER = 16

# Padding and margins (for consistent UI spacing)
PADDING_SMALL = 5
PADDING_NORMAL = 10
PADDING_LARGE = 20
MARGIN_SMALL = 5
MARGIN_NORMAL = 10
MARGIN_LARGE = 20

# Directory and file paths
BASE_DIR = "."  # Base directory, adjust as needed
DATA_DIR = f"{BASE_DIR}/data"
LOGS_DIR = f"{BASE_DIR}/logs"
BACKUP_DIR = f"{BASE_DIR}/backup"
ASSETS_DIR = f"{BASE_DIR}/assets"
REPORTS_DIR = f"{BASE_DIR}/reports"
TEMP_DIR = f"{BASE_DIR}/temp"

# File paths
DATA_FILE = f"{DATA_DIR}/pool_data.json"
SETTINGS_FILE = f"{DATA_DIR}/settings.json"
ENCRYPTION_KEY_FILE = f"{DATA_DIR}/encryption.key"
TASK_HISTORY_FILE = f"{DATA_DIR}/task_history.json"

# Database configuration
DB_NAME = "pool_management.db"
DB_BACKUP_PATH = "./backups/"

# Application paths (legacy support)
LOG_FILE_PATH = "./logs/app.log"
CONFIG_FILE_PATH = "./config/settings.ini"
REPORTS_PATH = "./reports/"

# Pool parameters
DEFAULT_POOL_LENGTH = 50  # in meters
DEFAULT_POOL_WIDTH = 25   # in meters
DEFAULT_POOL_DEPTH = 2.0  # in meters
DEFAULT_WATER_TEMP = 26.0 # in Celsius

# Chemical parameters - ideal ranges
CHEMICAL_RANGES = {
    "pH": (7.2, 7.8),
    "Free Chlorine": (1.0, 3.0),  # in ppm
    "Total Chlorine": (1.0, 3.0),  # in ppm
    "Bromine": (3.0, 5.0),  # in ppm
    "Alkalinity": (80, 120),  # in ppm
    "Hardness": (200, 400),  # Calcium Hardness in ppm
    "Cyanuric Acid": (30, 80),  # Stabilizer in ppm
    "Salt": (2700, 3400)  # for saltwater pools in ppm
}

# Display ranges for UI (may be wider than ideal ranges)
DISPLAY_RANGES = {
    "pH": (6.8, 8.2),
    "Free Chlorine": (0.0, 5.0),  # in ppm
    "Total Chlorine": (0.0, 5.0),  # in ppm
    "Bromine": (0.0, 10.0),  # in ppm
    "Alkalinity": (0, 240),  # in ppm
    "Hardness": (0, 800),  # Calcium Hardness in ppm
    "Cyanuric Acid": (0, 150),  # Stabilizer in ppm
    "Salt": (0, 5000)  # for saltwater pools in ppm
}

# Chemicals for increasing levels
INCREASE_CHEMICALS = {
    "pH": "Soda Ash",
    "Free Chlorine": "Liquid Chlorine",
    "Total Chlorine": "Shock Treatment",
    "Alkalinity": "Baking Soda",
    "Hardness": "Calcium Chloride",
    "Cyanuric Acid": "Stabilizer",
    "Salt": "Pool Salt",
    "Bromine": "Bromine Tablets"
}

# Chemicals for decreasing levels
DECREASE_CHEMICALS = {
    "pH": "Muriatic Acid",
    "Free Chlorine": "Sodium Thiosulfate",
    "Total Chlorine": "Sodium Thiosulfate",
    "Alkalinity": "Muriatic Acid",
    "Hardness": "Partial Water Change",
    "Cyanuric Acid": "Partial Water Change",
    "Salt": "Partial Water Change",
    "Bromine": "Partial Water Change"
}

# Chemical dosage factors
CHEMICAL_FACTORS = {
    "pH": {"increase_oz_per_0.1": 8, "decrease_oz_per_0.1": 8},
    "Free Chlorine": {"increase_oz_per_1_ppm": 13},
    "Alkalinity": {"increase_lbs_per_10_ppm": 1.5, "decrease_lbs_per_10_ppm": 1.2},
    "Hardness": {"increase_lbs_per_10_ppm": 0.6},
    "Cyanuric Acid": {"increase_lbs_per_10_ppm": 1.3},
    "Salt": {"increase_lbs_per_100_ppm": 8.3},
    "Bromine": {"increase_oz_per_1_ppm": 10}
}

# Individual chemical parameters (legacy support)
PH_MIN = CHEMICAL_RANGES["pH"][0]
PH_MAX = CHEMICAL_RANGES["pH"][1]
CHLORINE_MIN = CHEMICAL_RANGES["Free Chlorine"][0]
CHLORINE_MAX = CHEMICAL_RANGES["Free Chlorine"][1]
ALKALINITY_MIN = CHEMICAL_RANGES["Alkalinity"][0]
ALKALINITY_MAX = CHEMICAL_RANGES["Alkalinity"][1]

# Time intervals
REFRESH_INTERVAL = 5000  # milliseconds
BACKUP_INTERVAL = 86400  # seconds (24 hours)
SENSOR_READ_INTERVAL = 300  # seconds (5 minutes)

# Extended time intervals
TIME_INTERVALS = {
    'WEATHER_UPDATE': 1800000,  # 30 minutes
    'DATETIME_UPDATE': 1000,    # 1 second
    'TASK_CHECK': 60000,        # 1 minute
    'ALERT_CHECK': 300000,      # 5 minutes
    'DATA_BACKUP': 3600000      # 1 hour
}

# Time range options for graphs
TIME_RANGES = {
    "1D": "Last 24 Hours",
    "1W": "Last Week",
    "1M": "Last Month",
    "3M": "Last 3 Months",
    "6M": "Last 6 Months",
    "1Y": "Last Year",
    "ALL": "All Time"
}

# User roles
ROLE_ADMIN = "admin"
ROLE_MANAGER = "manager"
ROLE_STAFF = "staff"
ROLE_VIEWER = "viewer"

# Export formats
EXPORT_FORMATS = [
    "CSV (.csv)",
    "Excel (.xlsx)",
    "PDF (.pdf)",
    "JSON (.json)"
]

# Default settings
DEFAULT_SETTINGS = {
    'email_reminders': True,
    'sms_reminders': False,
    'data_retention': '6M',
    'auto_backup': True,
    'backup_path': BACKUP_DIR,
    'theme': 'default',
    'window_size': DEFAULT_WINDOW_SIZE,
    'auto_update': True,
    'show_tooltips': True,
    'log_level': 'INFO'
}

# Arduino settings
ARDUINO_SETTINGS = {
    'baud_rate': 9600,
    'timeout': 1,
    'auto_connect': True,
    'reconnect_interval': 5  # seconds
}

# Weather API key (should ideally come from environment variables in production)
WEATHER_API_URL = "https://www.weatherapi.com/my/"
WEATHER_API_KEY = "10625f6f69c24caa989234327250407/"
LOCATION = "34773"
