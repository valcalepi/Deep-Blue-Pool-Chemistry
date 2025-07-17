import os
import cv2
import json
import logging
from PIL import Image
from services.image_processing.color_calibration import ColorCalibrator

logger = logging.getLogger("test_strip_analyzer")

class TestStripAnalyzer:
    def __init__(self, config=None):
        self.latest_image_path = None
        self.brand = (config or {}).get("strip_brand", "default")
        calib_file = (config or {}).get("calibration_file", "services/image_processing/calibration.json")
        self.calibrator = ColorCalibrator(calib_file)
        self.pad_zones = self._load_pad_zones()

    def _load_pad_zones(self):
        try:
            with open("services/image_processing/pad_zones.json", "r") as f:
                brands = json.load(f)
                zones = brands.get(self.brand)
                if not zones:
                    logger.warning(f"No pad zones found for brand '{self.brand}', using default layout")
                return zones or {}
        except Exception as e:
            logger.error(f"Failed to load pad zones: {e}")
            return {}

    def capture_image(self):
        test_image_path = "assets/images/test_strip.jpg"
        if not os.path.exists(test_image_path):
            logger.error(f"Test strip image not found: {test_image_path}")
            self.latest_image_path = None
            return None

        self.latest_image_path = test_image_path
        logger.info(f"Captured image: {self.latest_image_path}")
        return self.latest_image_path

    def get_image_preview(self):
        if not self.latest_image_path:
            return None
        try:
            image = cv2.imread(self.latest_image_path)
            if image is None:
                return None
            for chem, (x, y, w, h) in self.pad_zones.items():
                cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(image, chem, (x, y - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
            preview = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            return preview.resize((300, 200))
        except Exception as e:
            logger.error(f"Failed to generate image preview: {e}")
            return None

    def analyze(self):
        if not self.latest_image_path:
            logger.error("No image captured for analysis")
            return {}

        image = cv2.imread(self.latest_image_path)
        if image is None:
            logger.error("Failed to load image for analysis")
            return {}

        results = {}
        for chem, (x, y, w, h) in self.pad_zones.items():
            roi = image[y:y + h, x:x + w]
            avg_color = cv2.mean(roi)[:3]  # BGR
            rgb = [int(avg_color[2]), int(avg_color[1]), int(avg_color[0])]  # Convert to RGB
            value, confidence = self.calibrator.map_rgb_to_value(chem, rgb)
            results[chem] = {
                "value": value,
                "confidence": confidence,
                "rgb": rgb
            }
            logger.debug(f"{chem}: RGB={rgb}, Value={value}, Confidence={confidence}%")

        logger.info("Test strip analysis completed")
        return results
