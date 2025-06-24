# test_strip_analyzer.py

class TestStripAnalyzer:
    def __init__(self):
        # Define reference values for chemical levels
        self.reference_values = {
            "chlorine": {
                "low": 1.0,
                "ideal_min": 2.0,
                "ideal_max": 4.0,
                "high": 5.0
            },
            "pH": {
                "low": 7.0,
                "ideal_min": 7.2,
                "ideal_max": 7.6,
                "high": 8.0
            },
            # Add other parameters like alkalinity, hardness, etc.
        }

    def analyze_manual_readings(self, readings):
        results = {}
        recommendations = []

        for param, value in readings.items():
            if param in self.reference_values:
                ref = self.reference_values[param]

                if value < ref["low"]:
                    status = "too_low"
                elif value < ref["ideal_min"]:
                    status = "low"
                elif value <= ref["ideal_max"]:
                    status = "ideal"
                elif value <= ref["high"]:
                    status = "high"
                else:
                    status = "too_high"

                results[param] = {
                    "value": value,
                    "status": status
                }

                # Generate recommendations
                if status == "too_low" or status == "low":
                    recommendations.append(f"Increase {param} level")
                elif status == "high" or status == "too_high":
                    recommendations.append(f"Decrease {param} level")

        return {
            "results": results,
            "recommendations": recommendations
        }
