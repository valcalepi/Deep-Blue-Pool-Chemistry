import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import PatternFill
from datetime import datetime
import requests

EXCEL_FILE = 'pool_log.xlsx'
SHEET_NAME = 'PoolData'
THRESHOLDS = {
    'pH': (7.2, 7.8),
    'chlorine': (1.0, 3.0),
    'temperature': (70, 90)
}

def get_weather_adjustments():
    # Replace with your actual API key and location
    API_KEY = 'your_openweather_api_key'
    LOCATION = 'St. Cloud, FL'
    url = f'https://api.openweathermap.org/data/2.5/forecast?q={LOCATION}&appid={API_KEY}&units=imperial'

    try:
        response = requests.get(url)
        data = response.json()
        rain_forecast = any('rain' in entry['weather'][0]['main'].lower() for entry in data['list'][:5])
        uv_index = 8  # Placeholder; OpenWeather UV API is separate

        adjustments = []
        if rain_forecast:
            adjustments.append("Rain expected: increase stabilizer or shock dose.")
        if uv_index > 7:
            adjustments.append("High UV: consider adding stabilizer or reducing chlorine loss.")
        return " | ".join(adjustments) if adjustments else "No weather-based adjustments needed."
    except Exception:
        return "Weather data unavailable."

def append_to_excel(data):
    timestamp = datetime.now().isoformat()
    weather_note = get_weather_adjustments()
    row = {'Timestamp': timestamp, **data, 'Notes': weather_note}

    try:
        book = load_workbook(EXCEL_FILE)
        sheet = book[SHEET_NAME]
    except FileNotFoundError:
        df = pd.DataFrame([row])
        with pd.ExcelWriter(EXCEL_FILE, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name=SHEET_NAME, index=False)
        return

    next_row = sheet.max_row + 1
    for col_index, key in enumerate(row.keys(), start=1):
        sheet.cell(row=next_row, column=col_index).value = row[key]
        if key in THRESHOLDS:
            val = row[key]
            low, high = THRESHOLDS[key]
            if val < low or val > high:
                sheet.cell(row=next_row, column=col_index).fill = PatternFill(start_color="FFC7CE", end_color="FFC7CE", fill_type="solid")

    book.save(EXCEL_FILE)
