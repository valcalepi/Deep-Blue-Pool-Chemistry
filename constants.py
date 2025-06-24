# src/constants.py

# Version information
__version__ = "2.0.0"
__author__ = "Virtual Control LLC"
__copyright__ = "Copyright © 2025 Virtual Control LLC"

# Constants
DEFAULT_WINDOW_SIZE = (1400, 1000)
MIN_WINDOW_SIZE = (1200, 800)
WEATHER_API_KEY = "" # CRITICAL: This should be loaded from environment variables!

# Chemical ranges and thresholds
CHEMICAL_RANGES = {
    'pH': (7.2, 7.8),
    'Free Chlorine': (1.0, 3.0),
    'Total Chlorine': (1.0, 3.0),
    'Alkalinity': (80, 120),
    'Hardness': (200, 400),
    'Cyanuric Acid': (30, 80),
    'Salt': (2700, 3400)
}

DISPLAY_RANGES = {
    'pH': (6.0, 8.0),
    'Free Chlorine': (0.0, 5.0),
    'Total Chlorine': (0.0, 5.0),
    'Alkalinity': (0, 240),
    'Hardness': (0, 1000),
    'Cyanuric Acid': (0, 100),
    'Salt': (0, 5000)
}

# Color schemes
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

# Chemical adjustment factors
CHEMICAL_FACTORS = {
    'Chlorine': {
        'pH': 0.5,
        'Free Chlorine': 1.0,
        'Alkalinity': 0.1
    },
    'Salt': {
        'pH': 0.5,
        'Salt': 1.0,
        'Alkalinity': 0.1
    },
    'Bromine': {
        'pH': 0.5,
        'Bromine': 1.0,
        'Alkalinity': 0.1
    }
}

# Chemical treatment options
INCREASE_CHEMICALS = {
    'pH': 'Soda Ash',
    'Free Chlorine': 'Liquid Chlorine',
    'Total Chlorine': 'Shock Treatment',
    'Alkalinity': 'Baking Soda',
    'Hardness': 'Calcium Chloride',
    'Cyanuric Acid': 'Stabilizer',
    'Salt': 'Pool Salt'
}

DECREASE_CHEMICALS = {
    'pH': 'Muriatic Acid',
    'Free Chlorine': 'Sodium Thiosulfate',
    'Total Chlorine': 'Sodium Thiosulfate',
    'Alkalinity': 'Muriatic Acid',
    'Hardness': 'Partial Water Change',
    'Cyanuric Acid': 'Partial Water Change',
    'Salt': 'Partial Water Change'
}

# Time intervals (in seconds)
TIME_INTERVALS = {
    'WEATHER_UPDATE': 1800,  # 30 minutes
    'TASK_CHECK': 60,        # 1 minute
    'ALERT_CHECK': 300,      # 5 minutes
    'DATA_BACKUP': 3600      # 1 hour
}
