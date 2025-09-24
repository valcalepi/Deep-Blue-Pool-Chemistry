"""
Configuration File for Pool Management System

This file centralizes all configuration settings for the Pool Management System application.
It addresses window dimension inconsistencies, adds required chemical constants, 
and improves overall code organization through logical sectioning.

All variable names are fully spelled out with no abbreviations to improve readability.
"""

# ===============================================================================
# GUI CONFIGURATION
# ===============================================================================
# Settings related to the user interface dimensions, colors, and appearance

# Window dimensions standardized across all screens
WINDOW_WIDTH = 1024
WINDOW_HEIGHT = 768
WINDOW_MINIMUM_WIDTH = 800
WINDOW_MINIMUM_HEIGHT = 600

# Color scheme
BACKGROUND_COLOR = "#f5f5f5"
PRIMARY_COLOR = "#0066cc"
SECONDARY_COLOR = "#009688"
WARNING_COLOR = "#ff9800"
ERROR_COLOR = "#f44336"
SUCCESS_COLOR = "#4caf50"

# Font settings
FONT_FAMILY = "Arial"
FONT_SIZE_SMALL = 10
FONT_SIZE_NORMAL = 12
FONT_SIZE_LARGE = 16
FONT_SIZE_EXTRA_LARGE = 24

# Dashboard layout
DASHBOARD_REFRESH_RATE = 60  # seconds
CHART_HEIGHT = 300
CHART_WIDTH = 450

# ===============================================================================
# CHEMISTRY CONFIGURATION
# ===============================================================================
# Constants and thresholds for pool chemical management

# Ideal ranges for pool chemistry
PH_MINIMUM = 7.2
PH_MAXIMUM = 7.8
PH_IDEAL = 7.4

CHLORINE_MINIMUM = 1.0  # ppm
CHLORINE_MAXIMUM = 3.0  # ppm
CHLORINE_IDEAL = 2.0    # ppm

ALKALINITY_MINIMUM = 80.0  # ppm
ALKALINITY_MAXIMUM = 120.0  # ppm
ALKALINITY_IDEAL = 100.0    # ppm

CALCIUM_HARDNESS_MINIMUM = 200.0  # ppm
CALCIUM_HARDNESS_MAXIMUM = 400.0  # ppm
CALCIUM_HARDNESS_IDEAL = 300.0    # ppm

CYANURIC_ACID_MINIMUM = 30.0  # ppm
CYANURIC_ACID_MAXIMUM = 50.0  # ppm
CYANURIC_ACID_IDEAL = 40.0    # ppm

# Chemical correction rates
PH_DECREASE_RATE = 0.2  # pH decrease per standard dose of acid
PH_INCREASE_RATE = 0.2  # pH increase per standard dose of base
CHLORINE_INCREASE_RATE = 0.5  # ppm increase per standard dose of chlorine

# Temperature influence on chemical behavior
TEMPERATURE_CORRECTION_FACTOR = 0.1  # per 10°F above 80°F

# ===============================================================================
# SYSTEM CONFIGURATION
# ===============================================================================
# Core system settings and operational parameters

# Database configuration
DATABASE_HOST = "localhost"
DATABASE_PORT = 5432
DATABASE_NAME = "pool_management"
DATABASE_USER = "pool_admin"
DATABASE_PASSWORD = "secure_password"

# Logging configuration
LOG_LEVEL = "INFO"  # Options: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FILE_PATH = "/var/log/pool_management.log"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_RETENTION_DAYS = 30

# Backup configuration
BACKUP_ENABLED = True
BACKUP_DIRECTORY = "/var/backups/pool_management"
BACKUP_FREQUENCY = 24  # hours
BACKUP_RETENTION_COUNT = 7  # Keep last 7 backups

# Sensor configuration
TEMPERATURE_SENSOR_ENABLED = True
TEMPERATURE_SENSOR_PORT = "/dev/ttyUSB0"
TEMPERATURE_READING_INTERVAL = 300  # seconds

PH_SENSOR_ENABLED = True
PH_SENSOR_PORT = "/dev/ttyUSB1"
PH_READING_INTERVAL = 300  # seconds

CHLORINE_SENSOR_ENABLED = True
CHLORINE_SENSOR_PORT = "/dev/ttyUSB2"
CHLORINE_READING_INTERVAL = 300  # seconds

# ===============================================================================
# MAINTENANCE CONFIGURATION
# ===============================================================================
# Settings related to pool maintenance schedules and tasks

# Filter maintenance
FILTER_CLEANING_INTERVAL = 30  # days
FILTER_REPLACEMENT_INTERVAL = 365  # days

# Pump maintenance
PUMP_RUNNING_HOURS = 8  # hours per day
PUMP_MAINTENANCE_INTERVAL = 90  # days
PUMP_SCHEDULE_START = "08:00"  # 24-hour format
PUMP_SCHEDULE_END = "16:00"    # 24-hour format

# Chemical management
CHEMICAL_CHECK_FREQUENCY = 2  # times per week
CHEMICAL_DOSAGE_ADJUSTMENT_ENABLED = True
AUTOMATIC_CHLORINE_DOSING = True
AUTOMATIC_PH_ADJUSTMENT = True

# Water level management
WATER_LEVEL_CHECK_ENABLED = True
WATER_LEVEL_CHECK_INTERVAL = 24  # hours
AUTOMATIC_REFILL_ENABLED = True
REFILL_THRESHOLD_PERCENTAGE = 90  # % of optimal level

# ===============================================================================
# DEVELOPMENT SETTINGS
# ===============================================================================
# Settings specific to development environment, debugging and testing

# Debug and testing
DEBUG_MODE = False
TESTING_MODE = False
MOCK_SENSORS = False

# Development server
DEVELOPMENT_SERVER_HOST = "127.0.0.1"
DEVELOPMENT_SERVER_PORT = 8000

# Performance monitoring
ENABLE_PERFORMANCE_LOGGING = False
SLOW_QUERY_THRESHOLD = 1.0  # seconds

# API settings
API_RATE_LIMIT = 100  # requests per minute
API_TIMEOUT = 30  # seconds

# ===============================================================================
# FEATURE FLAGS
# ===============================================================================
# Toggles for enabling/disabling specific features

# Core features
ENABLE_DASHBOARD = True
ENABLE_CHEMICAL_MONITORING = True
ENABLE_PUMP_CONTROL = True
ENABLE_FILTER_MONITORING = True
ENABLE_HEATING_CONTROL = True
ENABLE_REPORTING = True
ENABLE_NOTIFICATIONS = True

# Advanced features
ENABLE_MOBILE_APP_SYNC = True
ENABLE_WEATHER_INTEGRATION = True
ENABLE_PREDICTIVE_MAINTENANCE = False
ENABLE_MULTI_USER_SUPPORT = True
ENABLE_REMOTE_ACCESS = True

# Experimental features
ENABLE_VOICE_CONTROL = False
ENABLE_AI_OPTIMIZATION = False
ENABLE_SOLAR_INTEGRATION = False
