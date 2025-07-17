#!/usr/bin/env python3
"""
Weather Impact Analyzer for Deep Blue Pool Chemistry

This module analyzes how weather conditions affect pool chemistry
and provides recommendations for chemical adjustments.
"""

import logging
import time
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

logger = logging.getLogger("weather_impact_analyzer")

class WeatherImpactAnalyzer:
    def __init__(self):
        logger.info("Weather Impact Analyzer initialized")

    def calculate_score(self, weather_data):
        """
        Simulate a weather impact score based on temperature, humidity, and UV index.
        """
        try:
            temp = float(weather_data.get("temperature", "80°F").replace("°F", ""))
            humidity = float(weather_data.get("humidity", "50%").replace("%", ""))
            uv = weather_data.get("uv_index", "Moderate")

            score = 0
            score += (temp - 70) * 0.5
            score += (humidity - 50) * 0.2
            score += {"Low": 1, "Moderate": 2, "High": 3}.get(uv, 2)

            return round(score, 2)
        except Exception as e:
            logger.warning(f"Failed to calculate weather impact score: {e}")
            return 0.0
    
    def __init__(self, weather_service=None):
        """
        Initialize the weather impact analyzer.
        
        Args:
            weather_service: Optional weather service instance
        """
        self.weather_service = weather_service
        logger.info("Weather Impact Analyzer initialized")
        
    def get_current_impact(self, pool_params: Dict[str, float], sanitizer_type: str = "chlorine") -> Dict[str, Any]:
        """
        Get the current impact of weather on pool chemistry.
        
        Args:
            pool_params: Dictionary of current pool parameters
            sanitizer_type: Type of sanitizer ("chlorine" or "bromine")
            
        Returns:
            Dict[str, Any]: Weather impact information
        """
        if not self.weather_service:
            logger.warning("No weather service available")
            return {"impacts": [], "recommendations": []}
            
        # Get current weather data
        weather_data = self.weather_service.get_weather()
        if not weather_data:
            logger.warning("No weather data available")
            return {"impacts": [], "recommendations": []}
            
        # Analyze impact for each parameter
        impacts = {
            "overall": {
                "impacts": [],
                "recommendations": []
            }
        }
        
        # Add overall weather impacts
        self._add_overall_impacts(impacts["overall"], weather_data, sanitizer_type)
        
        # Analyze each pool parameter
        for param, value in pool_params.items():
            if param in ["ph", "chlorine", "bromine", "alkalinity", "calcium_hardness", "cyanuric_acid"]:
                impacts[param] = self._analyze_parameter_impact(param, value, weather_data, sanitizer_type)
                
        return impacts
        
    def _add_overall_impacts(self, impact_data: Dict[str, List[str]], weather_data: Dict[str, Any], sanitizer_type: str):
        """
        Add overall weather impacts not specific to any parameter.
        
        Args:
            impact_data: Dictionary to add impacts to
            weather_data: Current weather data
            sanitizer_type: Type of sanitizer
        """
        temperature = weather_data.get("temperature", 75)
        conditions = weather_data.get("conditions", "sunny")
        uv_index = weather_data.get("uv_index", 5)
        rainfall = weather_data.get("precipitation", 0)
        
        # Temperature impacts
        if temperature > 90:
            impact_data["impacts"].append(f"Very high temperature ({temperature}\u00b0F) will significantly increase sanitizer consumption")
            impact_data["recommendations"].append("Check sanitizer levels twice daily")
            impact_data["recommendations"].append("Consider adding extra sanitizer in the evening")
        elif temperature > 85:
            impact_data["impacts"].append(f"High temperature ({temperature}\u00b0F) will increase sanitizer consumption")
            impact_data["recommendations"].append("Check sanitizer levels daily")
            
        # UV impacts
        if uv_index > 10:
            impact_data["impacts"].append(f"Extreme UV index ({uv_index}) will cause very rapid sanitizer degradation")
            impact_data["recommendations"].append(f"Increase {sanitizer_type} dosage by 50%")
            impact_data["recommendations"].append("Consider using a pool cover when not in use")
        elif uv_index > 8:
            impact_data["impacts"].append(f"Very high UV index ({uv_index}) will cause rapid sanitizer degradation")
            impact_data["recommendations"].append(f"Increase {sanitizer_type} dosage by 25-30%")
        elif uv_index > 6:
            impact_data["impacts"].append(f"High UV index ({uv_index}) will cause significant sanitizer degradation")
            impact_data["recommendations"].append(f"Increase {sanitizer_type} dosage by 15-20%")
            
        # Rainfall impacts
        if rainfall > 1.0:
            impact_data["impacts"].append(f"Heavy rainfall ({rainfall} inches) will dilute pool chemicals and introduce contaminants")
            impact_data["recommendations"].append("Test and adjust all chemical levels after rain stops")
            impact_data["recommendations"].append("Check for debris in skimmer and pump baskets")
            impact_data["recommendations"].append("Consider shock treatment if water clarity is affected")
        elif rainfall > 0.5:
            impact_data["impacts"].append(f"Moderate rainfall ({rainfall} inches) may dilute pool chemicals")
            impact_data["recommendations"].append("Test sanitizer and pH levels after rain stops")
            
        # Weather condition impacts
        if "storm" in conditions.lower():
            impact_data["impacts"].append("Stormy conditions can introduce significant contaminants and affect water balance")
            impact_data["recommendations"].append("Test all water parameters after storm passes")
            impact_data["recommendations"].append("Check for debris in skimmer and pump baskets")
            impact_data["recommendations"].append("Consider shock treatment after severe storms")
        elif "rain" in conditions.lower():
            impact_data["impacts"].append("Rainy conditions can introduce contaminants and affect water balance")
            impact_data["recommendations"].append("Test water parameters after rain stops")
        elif "wind" in conditions.lower():
            impact_data["impacts"].append("Windy conditions can introduce debris and contaminants")
            impact_data["recommendations"].append("Clean skimmer baskets more frequently")
            impact_data["recommendations"].append("Consider using a pool cover when not in use")
            
    def _analyze_parameter_impact(self, parameter: str, value: float, weather_data: Dict[str, Any], sanitizer_type: str) -> Dict[str, List[str]]:
        """
        Analyze the impact of weather on a specific pool parameter.
        
        Args:
            parameter: Pool parameter name
            value: Current parameter value
            weather_data: Current weather data
            sanitizer_type: Type of sanitizer
            
        Returns:
            Dict[str, List[str]]: Impact information for the parameter
        """
        impact_info = {
            "impacts": [],
            "recommendations": []
        }
        
        # Extract weather data
        temperature = weather_data.get("temperature", 75)
        conditions = weather_data.get("conditions", "sunny")
        uv_index = weather_data.get("uv_index", 5)
        rainfall = weather_data.get("precipitation", 0)
        humidity = weather_data.get("humidity", 50)
        
        # Convert temperature to numeric if it's a string with \u00b0F
        if isinstance(temperature, str) and "\u00b0F" in temperature:
            try:
                temperature = float(temperature.replace("\u00b0F", ""))
            except ValueError:
                temperature = 75
        
        # Chlorine weather impacts
        if parameter == "chlorine" and sanitizer_type == "chlorine":
            # UV impact on chlorine
            if uv_index > 8:
                impact_info["impacts"].append(f"High UV index ({uv_index}) will cause rapid chlorine degradation")
                impact_info["recommendations"].append("Increase chlorine dosage by 25-50%")
                impact_info["recommendations"].append("Add cyanuric acid stabilizer if levels are below 30 ppm")
                impact_info["recommendations"].append("Consider using a pool cover when not in use")
            elif uv_index > 5:
                impact_info["impacts"].append(f"Moderate UV index ({uv_index}) will cause chlorine degradation")
                impact_info["recommendations"].append("Monitor chlorine levels more frequently")
                impact_info["recommendations"].append("Ensure proper stabilizer (cyanuric acid) levels")
            
            # Temperature impact on chlorine
            if temperature > 85:
                impact_info["impacts"].append(f"High temperature ({temperature}\u00b0F) accelerates chlorine consumption")
                impact_info["recommendations"].append("Increase chlorine dosage")
                impact_info["recommendations"].append("Check chlorine levels twice daily")
            
            # Rainfall impact
            if rainfall > 0.5:
                impact_info["impacts"].append(f"Recent rainfall ({rainfall} inches) may dilute chlorine levels")
                impact_info["recommendations"].append("Test and adjust chlorine levels after rain")
                impact_info["recommendations"].append("Check pH and alkalinity as rain can affect these parameters")
            
            # Current chlorine level recommendations
            if value < 1.0 and temperature > 85:
                impact_info["impacts"].append("Low chlorine combined with high temperature creates high risk for algae growth")
                impact_info["recommendations"].append("Shock treat pool immediately")
                
            # Humidity impact
            if humidity > 80 and temperature > 80:
                impact_info["impacts"].append(f"High humidity ({humidity}%) and temperature increase risk of algae growth")
                impact_info["recommendations"].append("Maintain chlorine at the higher end of the ideal range")
        
        # Bromine weather impacts
        elif parameter == "bromine" and sanitizer_type == "bromine":
            # UV impact on bromine
            if uv_index > 8:
                impact_info["impacts"].append(f"High UV index ({uv_index}) will cause bromine degradation (though less than chlorine)")
                impact_info["recommendations"].append("Monitor bromine levels regularly")
            elif uv_index > 5:
                impact_info["impacts"].append(f"Moderate UV index ({uv_index}) has minimal impact on bromine levels")
                impact_info["recommendations"].append("Maintain regular bromine testing schedule")
            
            # Temperature impact on bromine
            if temperature > 85:
                impact_info["impacts"].append(f"High temperature ({temperature}\u00b0F) increases bromine consumption")
                impact_info["recommendations"].append("Check bromine levels daily")
            
            # Rainfall impact
            if rainfall > 0.5:
                impact_info["impacts"].append(f"Recent rainfall ({rainfall} inches) may dilute bromine levels")
                impact_info["recommendations"].append("Test and adjust bromine levels after rain")
            
            # Current bromine level recommendations
            if value < 2.0 and temperature > 85:
                impact_info["impacts"].append("Low bromine combined with high temperature increases risk of bacteria growth")
                impact_info["recommendations"].append("Add bromine shock treatment")
        
        # pH weather impacts
        elif parameter == "ph":
            # Rainfall impact on pH
            if rainfall > 0.5:
                impact_info["impacts"].append(f"Recent rainfall ({rainfall} inches) may lower pH (rain is typically acidic)")
                impact_info["recommendations"].append("Test pH after rainfall and adjust if necessary")
            
            # Temperature impact on pH
            if temperature > 85:
                impact_info["impacts"].append(f"High temperature ({temperature}\u00b0F) can cause pH to rise")
                impact_info["recommendations"].append("Monitor pH more frequently during hot weather")
                
            # High pH with high temperature
            if value > 7.8 and temperature > 85:
                impact_info["impacts"].append("High pH combined with high temperature reduces sanitizer effectiveness")
                impact_info["recommendations"].append("Adjust pH to 7.2-7.6 range for optimal sanitizer performance")
                
            # Low pH with rainfall
            if value < 7.2 and rainfall > 0.5:
                impact_info["impacts"].append("Low pH combined with recent rainfall increases risk of equipment corrosion")
                impact_info["recommendations"].append("Adjust pH to 7.2-7.6 range to protect equipment")
        
        # Alkalinity weather impacts
        elif parameter == "alkalinity":
            # Rainfall impact on alkalinity
            if rainfall > 0.5:
                impact_info["impacts"].append(f"Recent rainfall ({rainfall} inches) may dilute alkalinity")
                impact_info["recommendations"].append("Test alkalinity after significant rainfall")
                
            # Low alkalinity with changing weather
            if value < 80 and ("rain" in conditions.lower() or "storm" in conditions.lower()):
                impact_info["impacts"].append("Low alkalinity with changing weather conditions can cause pH fluctuations")
                impact_info["recommendations"].append("Increase alkalinity to 80-120 ppm for better pH buffering")
        
        # Cyanuric acid weather impacts
        elif parameter == "cyanuric_acid":
            # UV impact with low cyanuric acid
            if value < 30 and uv_index > 6:
                impact_info["impacts"].append(f"Low cyanuric acid with high UV index ({uv_index}) will cause rapid chlorine degradation")
                impact_info["recommendations"].append("Increase cyanuric acid to 30-50 ppm to protect chlorine")
                
            # High cyanuric acid impact
            if value > 70:
                impact_info["impacts"].append("High cyanuric acid levels can reduce sanitizer effectiveness (chlorine lock)")
                impact_info["recommendations"].append("Partially drain and refill pool to reduce cyanuric acid levels")
                
        return impact_info
        
    def forecast_chemical_needs(self, pool_params: Dict[str, float], forecast_days: int = 7, sanitizer_type: str = "chlorine") -> Dict[str, Any]:
        """
        Forecast chemical needs based on weather forecast.
        
        Args:
            pool_params: Dictionary of current pool parameters
            forecast_days: Number of days to forecast
            sanitizer_type: Type of sanitizer
            
        Returns:
            Dict[str, Any]: Forecast information
        """
        if not self.weather_service:
            logger.warning("No weather service available for forecasting")
            return {"forecast": [], "recommendations": []}
            
        # This would use actual forecast data in production
        # For now, we'll generate mock forecast data
        forecast = self._generate_mock_forecast(forecast_days)
        
        # Analyze forecast impact
        forecast_impact = {
            "forecast": [],
            "recommendations": []
        }
        
        # Calculate expected chemical consumption
        sanitizer_consumption = 0
        high_temp_days = 0
        high_uv_days = 0
        rain_days = 0
        
        for day in forecast:
            day_impact = {
                "date": day["date"],
                "impacts": [],
                "recommendations": []
            }
            
            # Analyze temperature impact
            if day["temperature"] > 90:
                day_impact["impacts"].append(f"Very high temperature ({day['temperature']}\u00b0F) will significantly increase sanitizer consumption")
                sanitizer_consumption += 0.5
                high_temp_days += 1
            elif day["temperature"] > 85:
                day_impact["impacts"].append(f"High temperature ({day['temperature']}\u00b0F) will increase sanitizer consumption")
                sanitizer_consumption += 0.3
                high_temp_days += 1
                
            # Analyze UV impact
            if day["uv_index"] > 10:
                day_impact["impacts"].append(f"Extreme UV index ({day['uv_index']}) will cause very rapid sanitizer degradation")
                sanitizer_consumption += 0.6
                high_uv_days += 1
            elif day["uv_index"] > 8:
                day_impact["impacts"].append(f"Very high UV index ({day['uv_index']}) will cause rapid sanitizer degradation")
                sanitizer_consumption += 0.4
                high_uv_days += 1
            elif day["uv_index"] > 6:
                day_impact["impacts"].append(f"High UV index ({day['uv_index']}) will cause significant sanitizer degradation")
                sanitizer_consumption += 0.2
                high_uv_days += 1
                
            # Analyze rainfall impact
            if day["precipitation"] > 1.0:
                day_impact["impacts"].append(f"Heavy rainfall ({day['precipitation']} inches) will dilute pool chemicals")
                day_impact["recommendations"].append("Test and adjust all chemical levels after rain")
                rain_days += 1
            elif day["precipitation"] > 0.5:
                day_impact["impacts"].append(f"Moderate rainfall ({day['precipitation']} inches) may dilute pool chemicals")
                day_impact["recommendations"].append("Test sanitizer and pH levels after rain")
                rain_days += 1
                
            forecast_impact["forecast"].append(day_impact)
            
        # Add overall recommendations based on forecast
        if high_temp_days > 3:
            forecast_impact["recommendations"].append(f"Prepare for increased {sanitizer_type} consumption due to high temperatures")
            forecast_impact["recommendations"].append(f"Consider increasing {sanitizer_type} dosage by 25-30%")
            
        if high_uv_days > 3:
            forecast_impact["recommendations"].append(f"Prepare for increased {sanitizer_type} consumption due to high UV levels")
            if sanitizer_type == "chlorine":
                forecast_impact["recommendations"].append("Ensure cyanuric acid levels are 30-50 ppm to protect chlorine")
                
        if rain_days > 0:
            forecast_impact["recommendations"].append("Be prepared to test and adjust chemicals after rainfall")
            
        # Calculate estimated sanitizer needed
        pool_size = 15000  # Default pool size in gallons
        if sanitizer_type == "chlorine":
            # Estimate for liquid chlorine (10% sodium hypochlorite)
            chlorine_needed = (pool_size / 10000) * sanitizer_consumption
            forecast_impact["estimated_consumption"] = {
                "amount": round(chlorine_needed, 1),
                "unit": "quarts",
                "type": "liquid chlorine (10%)"
            }
        else:  # bromine
            # Estimate for bromine tablets
            bromine_needed = (pool_size / 10000) * (sanitizer_consumption * 0.8)
            forecast_impact["estimated_consumption"] = {
                "amount": round(bromine_needed, 1),
                "unit": "tablets",
                "type": "bromine tablets"
            }
            
        return forecast_impact
        
    def _generate_mock_forecast(self, days: int) -> List[Dict[str, Any]]:
        """
        Generate mock weather forecast data.
        
        Args:
            days: Number of days to forecast
            
        Returns:
            List[Dict[str, Any]]: Mock forecast data
        """
        import random
        
        forecast = []
        start_date = datetime.now()
        
        for i in range(days):
            day_date = start_date + timedelta(days=i)
            
            # Generate random but somewhat realistic weather data
            temp_base = random.uniform(75, 90)
            uv_base = random.uniform(5, 10)
            
            # Add some consistency to the forecast (similar days tend to be similar)
            if i > 0:
                prev_temp = forecast[i-1]["temperature"]
                prev_uv = forecast[i-1]["uv_index"]
                
                temp_base = (temp_base + prev_temp) / 2
                uv_base = (uv_base + prev_uv) / 2
            
            # Determine conditions
            rain_chance = random.random()
            if rain_chance < 0.2:
                conditions = "Rainy"
                precipitation = round(random.uniform(0.5, 2.0), 2)
            elif rain_chance < 0.4:
                conditions = "Partly Cloudy"
                precipitation = round(random.uniform(0, 0.1), 2)
            else:
                conditions = "Sunny"
                precipitation = 0
                
            forecast.append({
                "date": day_date.strftime("%Y-%m-%d"),
                "temperature": round(temp_base, 1),
                "conditions": conditions,
                "uv_index": round(uv_base, 1),
                "precipitation": precipitation,
                "humidity": round(random.uniform(40, 90), 1)
            })
            
        return forecast

# Test function
def test_weather_impact_analyzer():
    """Test the weather impact analyzer."""
    logging.basicConfig(level=logging.INFO)
    
    # Create a mock weather service
    class MockWeatherService:
        def get_weather(self):
            return {
                "temperature": 88,
                "humidity": 75,
                "conditions": "Sunny",
                "wind_speed": 5,
                "precipitation": 0,
                "uv_index": 9
            }
    
    # Create analyzer with mock weather service
    analyzer = WeatherImpactAnalyzer(MockWeatherService())
    
    # Test current impact analysis
    pool_params = {
        "ph": 7.4,
        "chlorine": 1.5,
        "alkalinity": 100,
        "calcium_hardness": 250,
        "cyanuric_acid": 40
    }
    
    impact = analyzer.get_current_impact(pool_params, "chlorine")
    print("Current weather impact:")
    for param, data in impact.items():
        print(f"\
{param.upper()}:")
        print(f"  Impacts: {data['impacts']}")
        print(f"  Recommendations: {data['recommendations']}")
    
    # Test forecast
    forecast = analyzer.forecast_chemical_needs(pool_params, 5, "chlorine")
    print("\
Forecast:")
    for day in forecast["forecast"]:
        print(f"\
{day['date']}:")
        print(f"  Impacts: {day['impacts']}")
        print(f"  Recommendations: {day['recommendations']}")
    
    print(f"\
Overall recommendations: {forecast['recommendations']}")
    if "estimated_consumption" in forecast:
        consumption = forecast["estimated_consumption"]
        print(f"Estimated consumption: {consumption['amount']} {consumption['unit']} of {consumption['type']}")

if __name__ == "__main__":
    test_weather_impact_analyzer()
