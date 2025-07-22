# modules/config_manager.py
"""
Configuration Manager Module
Handles loading, saving, and managing application configuration
"""

import os
import json
import logging

class ConfigManager:
    """Configuration manager for the Pool Chemistry Manager application"""
    
    def __init__(self, config_file):
        """Initialize the configuration manager"""
        self.logger = logging.getLogger(__name__)
        self.config_file = config_file
        self.config = self._get_default_config()
        self._load_config()
    
    def _get_default_config(self):
        """Get default configuration"""
        return {
            "database": {
                "type": "sqlite",
                "path": "data/pool_chemistry.db",
                "backup_interval": 24
            },
            "pool_defaults": {
                "size": 20000,
                "type": "Chlorine",
                "target_ph": 7.2,
                "target_chlorine": 2.0,
                "target_alkalinity": 100,
                "target_hardness": 200,
                "target_cyanuric": 40
            },
            "chemicals": {
                "ph_increaser": "Sodium Carbonate",
                "ph_decreaser": "Muriatic Acid",
                "chlorine_type": "Liquid Chlorine",
                "alkalinity_increaser": "Sodium Bicarbonate"
            },
            "safety": {
                "max_adjustments": 3,
                "min_time_hours": 4,
                "safety_warnings": True,
                "dosage_limits": True
            },
            "application": {
                "theme": "default",
                "window_size": "1200x800",
                "autosave_minutes": 5,
                "startup_check": True,
                "confirm_exit": True,
                "log_level": "INFO",
                "log_file": "logs/pool_app.log",
                "log_size_mb": 10
            }
        }
    
    def _load_config(self):
        """Load configuration from file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    loaded_config = json.load(f)
                    # Merge with defaults to ensure all keys exist
                    self._merge_config(self.config, loaded_config)
                self.logger.info("Configuration loaded successfully")
            else:
                self.logger.info("No config file found, using defaults")
                # Create config directory if it doesn't exist
                os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
                self.save_config()
        except Exception as e:
            self.logger.error(f"Error loading config: {e}")
    
    def save_config(self):
        """Save configuration to file"""
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
            self.logger.info("Configuration saved successfully")
            return True
        except Exception as e:
            self.logger.error(f"Error saving config: {e}")
            return False
    
    def _merge_config(self, default, loaded):
        """Merge loaded config with defaults"""
        for key, value in loaded.items():
            if key in default:
                if isinstance(value, dict) and isinstance(default[key], dict):
                    self._merge_config(default[key], value)
                else:
                    default[key] = value
    
    def get_config(self):
        """Get the current configuration"""
        return self.config
    
    def update_config(self, new_config):
        """Update configuration with new values"""
        try:
            self.config = new_config
            return True
        except Exception as e:
            self.logger.error(f"Error updating config: {e}")
            return False
    
    def export_config(self, filename):
        """Export configuration to a file"""
        try:
            with open(filename, 'w') as f:
                json.dump(self.config, f, indent=2)
            return True
        except Exception as e:
            self.logger.error(f"Error exporting config: {e}")
            return False
    
    def import_config(self, filename):
        """Import configuration from a file"""
        try:
            with open(filename, 'r') as f:
                imported_config = json.load(f)
            
            # Validate and merge config
            self._merge_config(self.config, imported_config)
            return True
        except Exception as e:
            self.logger.error(f"Error importing config: {e}")
            return False
    
    def reset_to_defaults(self):
        """Reset configuration to defaults"""
        try:
            self.config = self._get_default_config()
            return True
        except Exception as e:
            self.logger.error(f"Error resetting config: {e}")
            return False