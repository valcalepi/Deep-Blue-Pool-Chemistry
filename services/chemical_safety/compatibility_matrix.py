import logging

logger = logging.getLogger("compatibility_matrix")

class CompatibilityMatrix:
    def __init__(self):
        self.rules = {
            ("Chlorine", "Ammonia"): "⚠️ Dangerous: May produce toxic chloramines",
            ("Acid", "Base"): "⚠️ Violent reaction: Heat and gas release",
            ("Hydrogen Peroxide", "Ethanol"): "⚠️ Fire risk: Highly reactive",
            ("Chlorine", "Bromine"): "⚠️ Unstable: May reduce sanitizer effectiveness",
            ("Salt", "Calcium"): "⚠️ Scaling risk: May cause deposits in salt cell"
        }
        logger.info("Compatibility Matrix initialized")

    def check(self, chem_a, chem_b):
        if not chem_a or not chem_b:
            return "Please select two chemicals."
        result = self.rules.get((chem_a, chem_b)) or self.rules.get((chem_b, chem_a))
        return result or "✅ Compatible"
