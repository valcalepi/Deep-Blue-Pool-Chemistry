# In screens.py
from weather_api import update_weather

def show_dashboard_content(self):
    # Existing dashboard setup code...
    
    # Add weather data panel
    weather_frame = StyledFrame(dashboard_container, padding=PADDING_LARGE)
    weather_frame.grid(row=0, column=2, padx=PADDING_NORMAL, pady=PADDING_NORMAL, sticky="nsew")
    
    weather_header = ttk.Label(weather_frame, text="Weather Conditions", font=(FONT_FAMILY, FONT_SIZE_LARGE, 'bold'))
    weather_header.grid(row=0, column=0, pady=(0, PADDING_NORMAL), sticky="nw")
    
    # Fetch current weather data
    weather_data = update_weather()
    
    if weather_data:
        # Display weather information
        # Implementation depends on the structure of your weather API response
        # Example assuming a simple weather API response
        try:
            temp = weather_data.get('current', {}).get('temp_c', 'N/A')
            condition = weather_data.get('current', {}).get('condition', {}).get('text', 'N/A')
            humidity = weather_data.get('current', {}).get('humidity', 'N/A')
            
            weather_info = [
                ("Temperature", f"{temp}°C"),
                ("Condition", condition),
                ("Humidity", f"{humidity}%")
            ]
            
            for i, (label_text, value_text) in enumerate(weather_info):
                label = ttk.Label(weather_frame, text=f"{label_text}:")
                label.grid(row=i+1, column=0, padx=(0, PADDING_NORMAL), pady=PADDING_SMALL, sticky="nw")
                
                value = ttk.Label(weather_frame, text=value_text)
                value.grid(row=i+1, column=1, pady=PADDING_SMALL, sticky="nw")
        except Exception as e:
            logging.error(f"Error displaying weather data: {e}")
            error_label = ttk.Label(weather_frame, text="Weather data unavailable", foreground=ERROR_COLOR)
            error_label.grid(row=1, column=0, pady=PADDING_SMALL, sticky="nw")
    else:
        # Display error message if weather data couldn't be retrieved
        error_label = ttk.Label(weather_frame, text="Weather data unavailable", foreground=ERROR_COLOR)
        error_label.grid(row=1, column=0, pady=PADDING_SMALL, sticky="nw")
