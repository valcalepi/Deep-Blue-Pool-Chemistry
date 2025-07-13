Pool Controller System

A comprehensive system for monitoring and controlling swimming pool parameters, including water quality, temperature, and equipment operation.


Features
• **Real-time Monitoring**: Track water temperature, pH levels, and chlorine levels
• **Automated Control**: Automatically adjust pool equipment based on conditions
• **Weather Integration**: Adapt pool operations based on weather forecasts
• **Data Logging**: Store historical data for analysis and reporting
• **Web Interface**: Control and monitor your pool from any device
• **GUI Application**: Desktop application for local control
• **Arduino Integration**: Connect to pool sensors and equipment via Arduino
• **Chemical Management**: Calculate chemical additions based on water test results
• **Maintenance Scheduling**: Track and schedule regular maintenance tasks


System Requirements
• Python 3.8 or higher
• Arduino (for hardware integration)
• SQLite3 (for data storage)
• Flask (for web interface)
• Tkinter (for GUI application)


Installation
1. Clone the repository:
```
git clone https://github.com/yourusername/pool-controller.git
cd pool-controller
```

2. Install dependencies:
```
pip install -r requirements.txt
```

3. Configure the system:
- Edit `config/config.json` with your pool specifications
- Set up Arduino connections if using hardware integration


Running the Application

Web Interface

Run the web interface for remote access:


python main_app.py


The web interface will be available at http://localhost:8080


Desktop GUI

Run the desktop application for local control:


python integrated_app.py


Project Structure

pool_controller/
\u251c\u2500\u2500 app/                    # Application core
\u2502   \u251c\u2500\u2500 controllers/        # Business logic controllers
\u2502   \u251c\u2500\u2500 models/             # Data models
\u2502   \u2514\u2500\u2500 views/              # User interfaces
\u2502       \u251c\u2500\u2500 gui/            # Desktop GUI components
\u2502       \u2514\u2500\u2500 web/            # Web interface components
\u251c\u2500\u2500 services/               # External service integrations
\u2502   \u251c\u2500\u2500 arduino/            # Arduino communication
\u2502   \u251c\u2500\u2500 database/           # Database operations
\u2502   \u251c\u2500\u2500 weather/            # Weather data services
\u2502   \u2514\u2500\u2500 image_processing/   # Test strip image analysis
\u251c\u2500\u2500 utils/                  # Utility functions
\u251c\u2500\u2500 tests/                  # Test suite
\u251c\u2500\u2500 data/                   # Data storage
\u251c\u2500\u2500 logs/                   # Application logs
\u251c\u2500\u2500 config/                 # Configuration files
\u251c\u2500\u2500 integrated_app.py       # Desktop application entry point
\u251c\u2500\u2500 main_app.py             # Web application entry point
\u2514\u2500\u2500 README.md               # This file


Configuration

The system is configured via `config/config.json`:


{
    "pool": {
        "size": 15000,
        "type": "chlorine"
    },
    "arduino": {
        "port": "COM3",
        "baud_rate": 9600
    },
    "weather": {
        "location": "Florida",
        "update_interval": 3600
    },
    "gui": {
        "theme": "blue",
        "refresh_rate": 5000
    }
}


Development

To contribute to the project:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `python -m unittest discover tests`
5. Submit a pull request


License

This project is licensed under the MIT License - see the LICENSE file for details.


Acknowledgments
• Thanks to all contributors
• Special thanks to the Arduino and Flask communities