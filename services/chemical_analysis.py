import logging

logger = logging.getLogger("chemical_analysis")

IDEAL_RANGES = {
    "pH": (7.2, 7.6),
    "free_chlorine": (1.0, 3.0),
    "total_chlorine": (1.0, 3.0),
    "alkalinity": (80, 120),
    "calcium": (200, 400),
    "cyanuric_acid": (30, 50),
    "bromine": (3.0, 5.0),
    "salt": (2700, 3400)
}

CRITICAL_RANGES = {
    "pH": (7.0, 8.0),
    "free_chlorine": (0.5, 5.0),
    "total_chlorine": (0.5, 5.0),
    "alkalinity": (50, 180),
    "calcium": (150, 500),
    "cyanuric_acid": (10, 80),
    "bromine": (2.0, 6.0),
    "salt": (2000, 4000)
}

def evaluate(readings: dict):
    """
    Evaluate pool chemistry readings and return a list of issues and advice.
    """
    report = []

    for key, value_str in readings.items():
        if not value_str:
            continue
        try:
            value = float(value_str)
        except ValueError:
            report.append((key, "Invalid", f"Could not interpret '{value_str}' as a number."))
            continue

        ideal = IDEAL_RANGES.get(key)
        critical = CRITICAL_RANGES.get(key)

        if not ideal or not critical:
            continue

        status = "Good"
        message = "Within ideal range."

        if value < critical[0] or value > critical[1]:
            status = "Critical"
            if key == "pH":
                message = "pH is severely unbalanced. May cause equipment damage or eye irritation."
            elif key == "free_chlorine":
                message = "Free chlorine dangerously low — potential for bacteria growth."
            elif key == "cyanuric_acid":
                message = "CYA too high — may reduce chlorine effectiveness. Consider partial drain."
            elif key == "salt":
                message = "Salt levels outside operational range for salt cell. Check calibration."
            else:
                message = f"{key.replace('_', ' ').title()} critically out of range."

        elif value < ideal[0] or value > ideal[1]:
            status = "Warning"
            if key == "calcium":
                message = "Hardness may cause scaling or corrosion. Consider adjustment."
            elif key == "alkalinity":
                message = "Alkalinity drifting — may destabilize pH."
            else:
                message = f"{key.replace('_', ' ').title()} slightly outside ideal range."

        # Specific: total chlorine far above free chlorine = chloramines
        if key == "total_chlorine" and "free_chlorine" in readings:
            try:
                free = float(readings["free_chlorine"])
                if value - free > 1.5:
                    status = "Warning"
                    message = "Total chlorine too high compared to free — possible chloramine buildup."
            except Exception:
                pass

        report.append((key, status, message))

    return report
