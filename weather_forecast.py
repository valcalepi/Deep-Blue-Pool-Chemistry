# weather_forecast.py

import requests
import json
from config import Config

class WeatherForecast:
    def __init__(self):
    	self.api_key = Config.WEATHER_API_KEY
    	self.base_url = "https://api.openweathermap.org/data/2.5/forecast"

    def get_forecast_by_zip(self, zip_code, country_code="us", units="imperial"):
        params = {
            "zip": f"{zip_code},{country_code}",
            "appid": self.api_key,
            "units": units
        }

        response = requests.get(self.base_url, params=params)

        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"API Error: {response.status_code}"}

    def process_forecast_data(self, forecast_data):
        processed_data = []

        for item in forecast_data["list"]:
            day_data = {
                "date": item["dt_txt"].split(" ")[0],
                "time": item["dt_txt"].split(" ")[1],
                "temp": item["main"]["temp"],
                "feels_like": item["main"]["feels_like"],
                "humidity": item["main"]["humidity"],
                "weather_main": item["weather"][0]["main"],
                "weather_desc": item["weather"][0]["description"],
                "precipitation_prob": item["pop"],
                "wind_speed": item["wind"]["speed"]
            }

            # Add rain or snow if present
            if "rain" in item:
                day_data["rain"] = item["rain"].get("3h", 0)
            if "snow" in item:
                day_data["snow"] = item["snow"].get("3h", 0)

            processed_data.append(day_data)

        return processed_data

    def analyze_weather_impacts(self, processed_forecast):
        impacts = []

        for day in processed_forecast:
            day_impacts = {
                "date": day["date"],
                "time": day["time"],
                "impacts": []
            }

            # High temperature impacts
            if day["temp"] > 85:
                day_impacts["impacts"].append({
                    "type": "chlorine_depletion",
                    "severity": "moderate" if day["temp"] < 95 else "high",
                    "message": "High temperatures accelerate chlorine depletion. Check levels more frequently."
                })

            # Rain impacts
            if day.get("rain", 0) > 0:
                rain_amount = day.get("rain", 0)
                severity = "low" if rain_amount < 2.5 else ("moderate" if rain_amount < 5 else "high")
                day_impacts["impacts"].append({
                    "type": "dilution",
                    "severity": severity,
                    "message": f"Expected rainfall may dilute pool water. Check chemistry after rain."
                })

            # Wind impacts
            if day["wind_speed"] > 15:
                day_impacts["impacts"].append({
                    "type": "debris",
                    "severity": "moderate" if day["wind_speed"] < 25 else "high",
                    "message": "High winds may introduce debris. Clean skimmer and filter more frequently."
                })

            impacts.append(day_impacts)

        return impacts
