import tkinter as tk
from app.views.dashboard_view import DashboardView
from services.database.database_service import DatabaseService
from services.image_processing.test_strip_analyzer import TestStripAnalyzer
from services.image_processing.color_calibration import ColorCalibrator
from app.settings.settings_manager import SettingsManager

class MainController:
    def __init__(self, config):
        self.config = config
        self.services = self._initialize_services()
        self.root = tk.Tk()
        self.root.title(self.config.get("app_name", "Deep Blue Pool Chemistry"))
        self.root.geometry("1024x768")

    def _initialize_services(self):
        return {
            "database": DatabaseService(self.config.get("database_path", "data/pool_chemistry.db")),
            "test_strip": TestStripAnalyzer(self.config),
            "calibrator": ColorCalibrator(self.config.get("calibration_file", "data/strip_calibration.json")),
            "settings": SettingsManager()
        }

    def initialize_views(self, basic_mode=False):
        self.dashboard = DashboardView(self.root, self.services)

    def run(self):
        self.root.mainloop()
