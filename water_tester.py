# water_tester.py
import logging
import math
from typing import Dict, Tuple, Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)

class WaterTester:
    def __init__(self):
        """Initialize WaterTester with industry standard ranges"""
        logger.info("Initializing WaterTester")
        try:
            # Initialize pool types
            self.pool_types = [
                "Chlorine Pool",
                "Salt Water Pool", 
                "Bromine Pool",
                "Concrete/Gunite",
                "Vinyl Liner",
                "Fiberglass",
                "Above Ground - Metal Wall",
                "Above Ground - Resin",
                "Infinity Pool",
                "Lap Pool",
                "Indoor Pool"
            ]

            # Initialize ideal chemical levels
            self.ideal_levels = {
                "Hardness": (200, 400),      # Range 0-800
                "Free Chlorine": (1.0, 3.0),  # Range 0-6.0
                "Total Chlorine": (1.0, 3.0), # Range 0-6.0
                "Bromine": (3.0, 5.0),        # Range 0-10.0
                "Alkalinity": (80, 120),      # Range 0-240
                "pH": (7.2, 7.8),             # Range 6.2-8.4
                "Cyanuric Acid": (30, 80),    # Range 0-100
                "Salt": (2700, 3400)          # Range 0-6800
            }

            # Initialize chemicals for increasing levels
            self.increase_chemicals = {
                "pH": "Soda Ash",
                "Free Chlorine": "Liquid Chlorine",
                "Total Chlorine": "Shock Treatment",
                "Alkalinity": "Baking Soda",
                "Hardness": "Calcium Chloride",
                "Cyanuric Acid": "Stabilizer",
                "Salt": "Pool Salt",
                "Bromine": "Bromine Tablets"
            }

            # Initialize chemicals for decreasing levels
            self.decrease_chemicals = {
                "pH": "Muriatic Acid",
                "Free Chlorine": "Sodium Thiosulfate",
                "Total Chlorine": "Sodium Thiosulfate",
                "Alkalinity": "Muriatic Acid",
                "Hardness": "Partial Water Change",
                "Cyanuric Acid": "Partial Water Change",
                "Salt": "Partial Water Change",
                "Bromine": "Partial Water Change"
            }

            # Enhanced chemical warnings with more detailed recommendations
            self.chemical_warnings = {
                "Free Chlorine": """
SAFETY WARNING: 
- Always add chlorine to water, never water to chlorine
- Wear protective gloves and eye protection
- Add during evening hours to prevent rapid dissipation
- Keep away from children and pets
- Never mix with other chemicals
- Ensure proper ventilation when handling
- Store in a cool, dry, well-ventilated area
- For indoor pools, ensure adequate ventilation to prevent chlorine gas buildup
- Consider using chlorine stabilizer if the pool is exposed to direct sunlight
""",
                "Salt": """
SAFETY WARNING:
- Always add salt gradually, never all at once
- Dissolve salt completely before adding more
- Keep salt away from metal components when possible
- If using an electronic chlorine generator, ensure salt levels are maintained within manufacturer specifications
- Check your salt cell regularly for calcium buildup
- For salt water pools, ensure the salt level is monitored weekly to maintain proper sanitization
- High salt levels may lead to corrosion of metal pool components
- Low salt levels in salt water pools may cause inadequate sanitization
""",
                # Add other enhanced warnings as needed
            }
            
            # Initialize chemical factors
            self.chemical_factors = {
                "Chlorine Pool": {
                    "pH": 1.0,
                    "Free Chlorine": 1.0,
                    "Total Chlorine": 1.0,
                    "Alkalinity": 1.0,
                    "Hardness": 1.0,
                    "Cyanuric Acid": 1.0
                },
                "Salt Water Pool": {
                    "pH": 1.0,
                    "Free Chlorine": 0.8,
                    "Total Chlorine": 0.8,
                    "Alkalinity": 1.0,
                    "Hardness": 1.0,
                    "Cyanuric Acid": 1.0,
                    "Salt": 1.0
                },
                "Bromine Pool": {
                    "pH": 1.0,
                    "Bromine": 1.0,
                    "Alkalinity": 1.0,
                    "Hardness": 1.0
                }
            }

            # Set default pool volume
            self.pool_volume = 15000  # Default to 15,000 gallons
            
        except Exception as e:
            logger.error(f"Error initializing WaterTester: {str(e)}")
            raise

    def set_pool_volume(self, volume: float):
        """Set the pool volume for calculations"""
        self.pool_volume = volume

    def get_ideal_range(self, parameter: str) -> Tuple[float, float]:
        """Return the ideal range for a given parameter"""
        return self.ideal_levels.get(parameter, (0, 0))

    # Advanced chemical balance algorithms
    def calculate_langelier_saturation_index(self, pH: float, temperature: float, 
                                            calcium_hardness: float, total_alkalinity: float, 
                                            total_dissolved_solids: float = 0) -> float:
        """
        Calculate the Langelier Saturation Index (LSI) for pool water
        LSI = pH + TF + CF + AF + TDS_factor - 12.1
        
        Args:
            pH: Current pH level
            temperature: Water temperature in Fahrenheit
            calcium_hardness: Calcium hardness in ppm
            total_alkalinity: Total alkalinity in ppm
            total_dissolved_solids: TDS in ppm (default 0, will estimate if not provided)
            
        Returns:
            float: LSI value. Positive value indicates scaling tendency,
                  negative value indicates corrosive tendency,
                  value near zero indicates balanced water
        """
        try:
            # Temperature factor
            if temperature <= 32:
                tf = 0.0
            elif temperature <= 37:
                tf = 0.1
            elif temperature <= 46:
                tf = 0.2
            elif temperature <= 53:
                tf = 0.3
            elif temperature <= 60:
                tf = 0.4
            elif temperature <= 66:
                tf = 0.5
            elif temperature <= 76:
                tf = 0.6
            elif temperature <= 84:
                tf = 0.7
            elif temperature <= 94:
                tf = 0.8
            elif temperature <= 105:
                tf = 0.9
            else:
                tf = 1.0
                
            # Calcium hardness factor
            cf = math.log10(calcium_hardness) - 3.0
            
            # Alkalinity factor
            af = math.log10(total_alkalinity) - 3.0
            
            # For salt water pools, estimate TDS if not provided
            if total_dissolved_solids <= 0:
                # Estimate TDS based on average readings or use a default
                total_dissolved_solids = 1000  # Default estimate
            
            # TDS factor
            tds_factor = (math.log10(total_dissolved_solids) - 3.0) / 10
            
            # Calculate LSI
            lsi = pH + tf + cf + af + tds_factor - 12.1
            
            logger.info(f"Calculated LSI: {lsi:.2f}")
            return lsi
            
        except Exception as e:
            logger.error(f"Error calculating LSI: {str(e)}")
            return 0.0

    def get_lsi_recommendation(self, lsi: float) -> str:
        """
        Get recommendation based on Langelier Saturation Index
        
        Args:
            lsi: Langelier Saturation Index value
            
        Returns:
            str: Recommendation based on LSI
        """
        if lsi < -0.5:
            return "Water is very corrosive. Increase pH, alkalinity, or calcium hardness."
        elif -0.5 <= lsi <= -0.3:
            return "Water is slightly corrosive. Consider increasing pH or alkalinity."
        elif -0.3 < lsi < 0.3:
            return "Water is balanced. Maintain current chemistry."
        elif 0.3 <= lsi <= 0.5:
            return "Water has scaling tendency. Consider decreasing pH or alkalinity."
        else:  # lsi > 0.5
            return "Water has high scaling tendency. Decrease pH, alkalinity, or calcium hardness."

    def calculate_salt_needed(self, current_salt: float) -> float:
        """
        Calculate how much salt is needed based on current level
        
        Args:
            current_salt: Current salt level in ppm
            
        Returns:
            float: Amount of salt needed in pounds, or 0 if no salt is needed
        """
        try:
            min_ideal, max_ideal = self.get_ideal_range("Salt")
            
            if current_salt < min_ideal:
                ppm_needed = min_ideal - current_salt
                return self._calculate_salt_dosage(ppm_needed)
            elif current_salt > max_ideal:
                return 0  # No salt needed, levels are high
            else:
                return 0  # Salt level is within ideal range
                
        except Exception as e:
            logger.error(f"Error calculating salt needed: {str(e)}")
            return 0

    def _calculate_salt_dosage(self, ppm_needed: float) -> float:
        """
        Calculate salt dosage with validation
        
        Args:
            ppm_needed: Amount of salt needed in ppm
            
        Returns:
            float: Pounds of salt needed to add to pool
        """
        try:
            if ppm_needed <= 0:
                return 0
                
            # Formula: (ppm needed * pool volume in gallons * 8.34 lbs/gallon) / 1,000,000
            # Simplified formula used here with adjustment factor
            lbs_needed = (ppm_needed * self.pool_volume * 80) / (1000 * 10000)
            
            if lbs_needed > 1000:  # Sanity check
                logger.warning(f"Calculated salt dosage seems high: {lbs_needed} lbs")
                
            return lbs_needed
            
        except Exception as e:
            logger.error(f"Error calculating salt dosage: {str(e)}")
            return 0

    def get_chemical_status(self, param: str, value: float) -> Tuple[str, str]:
        """
        Determine status of chemical parameter (LOW, IDEAL, HIGH)
        
        Args:
            param: Chemical parameter name
            value: Current value
            
        Returns:
            tuple: (Status, Color code)
        """
        try:
            if param not in self.ideal_levels:
                return ("UNKNOWN", "#CCCCCC")
                
            low, high = self.ideal_levels[param]
            
            if value < low:
                return ("LOW", "#FF9999")  # Light red
            elif value > high:
                return ("HIGH", "#FFCC99")  # Light orange
            else:
                return ("IDEAL", "#99FF99")  # Light green
                
        except Exception as e:
            logger.error(f"Error determining chemical status: {str(e)}")
            return ("ERROR", "#CCCCCC")

    # Historical data tracking methods
    def analyze_chemical_trend(self, chemical: str, historical_data: List[Tuple[datetime, float]]) -> Dict:
        """
        Analyze historical trend for a specific chemical
        
        Args:
            chemical: Chemical parameter name
            historical_data: List of (timestamp, value) tuples
            
        Returns:
            dict: Analysis results including trend direction, volatility, etc.
        """
        if not historical_data or len(historical_data) < 2:
            return {
                "trend": "insufficient_data",
                "message": "Insufficient data for trend analysis",
                "volatility": 0,
                "recommendation": "Continue regular testing to build trend data"
            }
            
        # Sort data by timestamp
        sorted_data = sorted(historical_data, key=lambda x: x[0])
        
        # Extract values
        values = [value for _, value in sorted_data]
        
        # Calculate trend
        first_value = values[0]
        last_value = values[-1]
        
        # Calculate percent change
        if first_value > 0:
            percent_change = ((last_value - first_value) / first_value) * 100
        else:
            percent_change = 0
        
        # Calculate volatility (standard deviation)
        if len(values) > 1:
            mean = sum(values) / len(values)
            variance = sum((x - mean) ** 2 for x in values) / len(values)
            volatility = math.sqrt(variance)
        else:
            volatility = 0
            
        # Determine trend direction
        if percent_change > 5:
            trend = "increasing"
        elif percent_change < -5:
            trend = "decreasing"
        else:
            trend = "stable"
            
        # Get ideal range
        min_ideal, max_ideal = self.get_ideal_range(chemical)
        
        # Generate recommendation based on trend and current value
        recommendation = self._get_trend_recommendation(
            chemical, last_value, trend, volatility, min_ideal, max_ideal
        )
        
        return {
            "trend": trend,
            "percent_change": percent_change,
            "volatility": volatility,
            "current_value": last_value,
            "recommendation": recommendation
        }
    
    def _get_trend_recommendation(self, chemical: str, current_value: float, 
                                 trend: str, volatility: float,
                                 min_ideal: float, max_ideal: float) -> str:
        """Generate recommendation based on trend analysis"""
        
        if current_value < min_ideal:
            if trend == "decreasing":
                return f"{chemical} is below ideal range and decreasing. Immediate adjustment recommended."
            elif trend == "stable":
                return f"{chemical} is stable but below ideal range. Adjustment recommended."
            else:  # increasing
                return f"{chemical} is below ideal range but increasing. Monitor closely."
                
        elif current_value > max_ideal:
            if trend == "increasing":
                return f"{chemical} is above ideal range and increasing. Immediate adjustment recommended."
            elif trend == "stable":
                return f"{chemical} is stable but above ideal range. Adjustment recommended."
            else:  # decreasing
                return f"{chemical} is above ideal range but decreasing. Monitor closely."
                
        else:  # within ideal range
            if volatility > (max_ideal - min_ideal) / 2:
                return f"{chemical} is within ideal range but showing high volatility. Check more frequently."
            else:
                return f"{chemical} is within ideal range with stable trend. Maintain current regimen."

    def get_chemical_recommendations(self, current_levels: Dict[str, float], 
                                    pool_type: str, 
                                    historical_data: Optional[Dict[str, List[Tuple[datetime, float]]]] = None,
                                    weather: Optional[Dict] = None) -> Dict[str, str]:
        """
        Get chemical recommendations based on current levels
        
        Args:
            current_levels: Dictionary of current chemical levels
            pool_type: Type of pool
            historical_data: Optional historical data for trend analysis
            weather: Optional weather data for advanced recommendations
            
        Returns:
            dict: Recommendations for each chemical parameter
        """
        try:
            recommendations = {}
            factors = self.get_pool_type_factors(pool_type)
            
            for param, value in current_levels.items():
                if param not in self.ideal_levels:
                    continue
                    
                low, high = self.ideal_levels[param]
                
                # Include trend analysis if historical data is available
                trend_info = ""
                if historical_data and param in historical_data and len(historical_data[param]) > 1:
                    analysis = self.analyze_chemical_trend(param, historical_data[param])
                    trend_info = f" [{analysis['trend']} trend]"
                
                # Apply weather-based adjustments
                adjusted_low, adjusted_high = low, high
                if weather and 'temp_f' in weather:
                    temp = weather['temp_f']
                    # Adjust ideal ranges based on temperature
                    if param == "Free Chlorine" and temp > 85:
                        adjusted_high = high * 1.2  # Higher chlorine demand in hot weather
                    elif param == "pH" and temp > 85:
                        adjusted_low += 0.1  # pH tends to drop in hot weather
                
                if value < adjusted_low:
                    factor = factors.get(param, 1.0)
                    recommendations[param] = self._calculate_increase(param, value, adjusted_low, factors) + trend_info
                elif value > adjusted_high:
                    factor = factors.get(param, 1.0)
                    recommendations[param] = self._calculate_decrease(param, value, adjusted_high, factors) + trend_info
                else:
                    recommendations[param] = f"Level is ideal{trend_info}"
                    
            # Add LSI recommendation if we have the necessary parameters
            required_params = ["pH", "Alkalinity", "Hardness"]
            if all(param in current_levels for param in required_params):
                # Estimate temperature if not provided in weather data
                temp = weather.get('temp_f', 75) if weather else 75
                
                lsi = self.calculate_langelier_saturation_index(
                    current_levels["pH"],
                    temp,
                    current_levels["Hardness"],
                    current_levels["Alkalinity"]
                )
                
                recommendations["LSI"] = f"LSI: {lsi:.2f} - {self.get_lsi_recommendation(lsi)}"
                
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}")
            return {"Error": "Could not generate recommendations"}

    def _calculate_increase(self, param: str, current: float, target: float, factors: Dict[str, float]) -> str:
        """Calculate amount needed to increase a parameter"""
        try:
            if param not in self.increase_chemicals:
                return f"No treatment available to increase {param}"
                
            chemical = self.increase_chemicals[param]
            factor = factors.get(param, 1.0)
            
            # Calculate amount needed
            amount = (target - current) * factor
            
            # Get the dosage
            dosage = self.calculate_dosage(param, amount)
            
            return f"Add {dosage} of {chemical}"
            
        except Exception as e:
            logger.error(f"Error calculating increase for {param}: {str(e)}")
            return f"Error calculating treatment for {param}"

    def _calculate_decrease(self, param: str, current: float, target: float, factors: Dict[str, float]) -> str:
        """Calculate amount needed to decrease a parameter"""
        try:
            if param not in self.decrease_chemicals:
                return f"No treatment available to decrease {param}"
                
            chemical = self.decrease_chemicals[param]
            factor = factors.get(param, 1.0)
            
            # Calculate amount needed
            amount = (current - target) * factor
            
            # Special handling for water changes
            if chemical == "Partial Water Change":
                percent_change = min((amount / current) * 100, 50)  # Cap at 50%
                return f"Perform {percent_change:.1f}% {chemical}"
                
            # Get the dosage
            dosage = self.calculate_dosage(param, amount)
            
            return f"Add {dosage} of {chemical}"
            
        except Exception as e:
            logger.error(f"Error calculating decrease for {param}: {str(e)}")
            return f"Error calculating treatment for {param}"

    def get_pool_type_factors(self, pool_type: str) -> Dict[str, float]:
        """Return chemical factors for a specific pool type"""
        return self.chemical_factors.get(pool_type, self.chemical_factors["Chlorine Pool"])

    def calculate_dosage(self, chemical: str, amount_needed: float) -> str:
        """
        Calculate chemical dosage based on pool volume
        
        Args:
            chemical: Chemical name
            amount_needed: Amount needed in ppm
            
        Returns:
            str: Dosage instructions
        """
        try:
            # Validate inputs
            if amount_needed <= 0:
                return "No adjustment needed"
            
            # Map chemicals to calculation methods
            calculation_methods = {
                "pH": self._calculate_ph_dosage,
                "Free Chlorine": self._calculate_chlorine_dosage,
                "Total Chlorine": self._calculate_chlorine_dosage,
                "Bromine": self._calculate_bromine_dosage,
                "Alkalinity": self._calculate_alkalinity_dosage,
                "Hardness": self._calculate_hardness_dosage,
                "Cyanuric Acid": self._calculate_cyanuric_acid_dosage,
                "Salt": self._calculate_salt_dosage
            }
            
            # Calculate dosage using appropriate method
            if chemical in calculation_methods:
                return calculation_methods[chemical](amount_needed)
            
            return "Dosage calculation not available for this chemical"
            
        except Exception as e:
            logger.error(f"Error calculating dosage: {str(e)}")
            return "Error calculating dosage"

    def _calculate_chlorine_dosage(self, ppm_needed: float) -> str:
        """Calculate chlorine dosage"""
        # Liquid chlorine is typically 10-12% sodium hypochlorite
        # 1 gallon of 10% liquid chlorine will raise chlorine by about 10 ppm in 10,000 gallons
        gallons_needed = (ppm_needed * self.pool_volume) / (10 * 10000)
        
        if gallons_needed < 0.1:
            oz_needed = gallons_needed * 128  # 128 oz in a gallon
            return f"{oz_needed:.1f} oz"
        else:
            return f"{gallons_needed:.2f} gallons"

    def _calculate_ph_dosage(self, ppm_needed: float) -> str:
        """Calculate pH adjuster dosage"""
        # Simplified conversion for pH adjustment
        # These are approximations as pH is logarithmic
        lbs_needed = (ppm_needed * self.pool_volume) / (0.1 * 10000)
        
        if lbs_needed < 1:
            oz_needed = lbs_needed * 16  # 16 oz in a pound
            return f"{oz_needed:.1f} oz"
        else:
            return f"{lbs_needed:.2f} lbs"

    def _calculate_alkalinity_dosage(self, ppm_needed: float) -> str:
        """Calculate alkalinity adjuster dosage"""
        # 1.5 lbs of baking soda raises alkalinity by ~10 ppm in 10,000 gallons
        lbs_needed = (ppm_needed * self.pool_volume * 1.5) / (10 * 10000)
        
        if lbs_needed < 1:
            oz_needed = lbs_needed * 16
            return f"{oz_needed:.1f} oz"
        else:
            return f"{lbs_needed:.2f} lbs"

    def _calculate_hardness_dosage(self, ppm_needed: float) -> str:
        """Calculate hardness adjuster dosage"""
        # 1 lb of calcium chloride raises hardness by ~10 ppm in 10,000 gallons
        lbs_needed = (ppm_needed * self.pool_volume) / (10 * 10000)
        
        if lbs_needed < 1:
            oz_needed = lbs_needed * 16
            return f"{oz_needed:.1f} oz"
        else:
            return f"{lbs_needed:.2f} lbs"

    def _calculate_cyanuric_acid_dosage(self, ppm_needed: float) -> str:
        """Calculate CYA dosage"""
        # 1 lb of CYA raises level by ~30 ppm in 10,000 gallons
        lbs_needed = (ppm_needed * self.pool_volume) / (30 * 10000)
        
        if lbs_needed < 1:
            oz_needed = lbs_needed * 16
            return f"{oz_needed:.1f} oz"
        else:
            return f"{lbs_needed:.2f} lbs"

    def _calculate_bromine_dosage(self, ppm_needed: float) -> str:
        """Calculate bromine dosage"""
        # 1.5 oz of bromine raises level by ~1 ppm in 10,000 gallons
        oz_needed = (ppm_needed * self.pool_volume * 1.5) / 10000
        
        if oz_needed > 16:
            lbs_needed = oz_needed / 16
            return f"{lbs_needed:.2f} lbs"
        else:
            return f"{oz_needed:.1f} oz"

    def calculate_chemical_balance_index(self, levels: Dict[str, float]) -> float:
        """
        Calculate overall chemical balance index
        
        Args:
            levels: Dictionary of current chemical levels
            
        Returns:
            float: Balance index (0-100)
        """
        try:
            # Required parameters for calculation
            required = ["pH", "Free Chlorine", "Alkalinity"]
            
            if not all(param in levels for param in required):
                return 0
                
            # Start with perfect score
            score = 100
            
            # Check each parameter against ideal range
            for param, value in levels.items():
                if param not in self.ideal_levels:
                    continue
                    
                min_ideal, max_ideal = self.ideal_levels[param]
                
                # Calculate how far the value is from ideal range
                if value < min_ideal:
                    # Value is below ideal - percentage below min
                    pct_off = (min_ideal - value) / min_ideal
                    score -= pct_off * 20  # Deduct up to 20 points
                elif value > max_ideal:
                    # Value is above ideal - percentage above max
                    pct_off = (value - max_ideal) / max_ideal
                    score -= pct_off * 20  # Deduct up to 20 points
            
            # Ensure score is between 0 and 100
            return max(0, min(100, score))
            
        except Exception as e:
            logger.error(f"Error calculating balance index: {str(e)}")
            return 0
