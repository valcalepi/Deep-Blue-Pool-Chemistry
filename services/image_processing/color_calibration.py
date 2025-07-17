import json
import math
import logging

logger = logging.getLogger("color_calibration")

class ColorCalibrator:
    def __init__(self, calibration_file="services/image_processing/calibration.json"):
        self.calibration_data = {}
        self._load_calibration(calibration_file)

    def _load_calibration(self, path):
        try:
            with open(path, "r") as f:
                self.calibration_data = json.load(f)
            logger.info(f"Loaded calibration data from {path}")
        except Exception as e:
            logger.error(f"Failed to load calibration data: {e}")
            self.calibration_data = {}

    def _distance(self, rgb1, rgb2):
        return math.sqrt(sum((a - b) ** 2 for a, b in zip(rgb1, rgb2)))

    def map_rgb_to_value(self, chemical, rgb_sample):
        samples = self.calibration_data.get(chemical, [])
        if not samples:
            return None, 0.0

        distances = [(self._distance(rgb_sample, s["rgb"]), s["value"]) for s in samples]
        distances.sort(key=lambda x: x[0])
        top = distances[:3]

        weights = [1 / (d + 1e-6) for d, _ in top]
        total_weight = sum(weights)
        interpolated = sum(v * w for (_, v), w in zip(top, weights)) / total_weight
        confidence = max(0.0, 100 - top[0][0] / math.sqrt(3 * 255 ** 2) * 100)

        return round(interpolated, 2), round(confidence, 1)

    def rgb_confidence(self, sample, reference):
        dist = self._distance(sample, reference)
        max_dist = math.sqrt(3 * 255 ** 2)
        score = max(0, 100 - (dist / max_dist) * 100)
        return round(score, 1)
