import json
import os

SETTINGS_FILE = "data/user_preferences.json"

class SettingsManager:
    def __init__(self):
        self.data = {
            "dark_mode": False,
            "last_theme": "ocean",
            "export_path": "data/exported_readings.csv"
        }
        self._load()

    def _load(self):
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, "r") as f:
                    self.data.update(json.load(f))
            except Exception:
                pass

    def save(self):
        try:
            with open(SETTINGS_FILE, "w") as f:
                json.dump(self.data, f, indent=4)
        except Exception:
            pass

    def get(self, key):
        return self.data.get(key)

    def set(self, key, value):
        self.data[key] = value
        self.save()
