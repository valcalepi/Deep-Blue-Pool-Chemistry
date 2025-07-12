Deep Blue Pool Chemistry

A comprehensive pool chemistry management system with GUI interface, Arduino integration, test strip analysis, and web interface.


Features
• **User-friendly GUI**: Easy-to-use interface for managing pool chemistry
• **Web Interface**: Access pool data through a web browser
• **Chemical Analysis**: Calculate chemical adjustments based on test readings
• **Test Strip Analysis**: Analyze test strips using computer vision (requires camera)
• **Arduino Integration**: Connect to Arduino devices for automated sensor readings
• **Weather Integration**: Check weather conditions for optimal pool maintenance
• **Data Logging**: Track pool chemistry over time
• **Recommendations**: Get recommendations for maintaining optimal water balance


Installation

Prerequisites
• Python 3.8 or higher
• Tkinter (usually included with Python)
• Arduino (optional for hardware integration)
• Webcam (optional for test strip analysis)


Setup
1. Clone the repository:
```
git clone https://github.com/valcalepi/Deep-Blue-Pool-Chemistry.git
cd Deep-Blue-Pool-Chemistry
```

2. Install dependencies:
```
pip install -r requirements.txt
```


Running the Application

There are multiple ways to run the application depending on your needs:


1. Integrated Application (Recommended)

This launches both the backend controller and GUI interface:


python integrated_app.py


2. Backend Only (with Web Interface)

This runs the pool controller backend with the web interface:


python main_app.py


The web interface will be available at: http://localhost:8080


3. GUI Only

This runs just the GUI interface:


python app/gui_launcher.py


4. Test Strip Analyzer

To test the test strip analyzer independently:


python test_strip_analyzer.py


5. Arduino Interface

To test the Arduino interface independently:


python arduino_interface.py


Configuration

The application is configured through the `config.json` file. Key settings include:

• `location`: Location for weather data
• `weather_update_interval`: How often to update weather data (in seconds)
• `web_interface_enabled`: Whether to enable the web interface
• `web_interface_port`: Port for the web interface
• `gui_enabled`: Whether to enable the GUI interface
• `database_path`: Path to the SQLite database file


Usage

GUI Interface

The GUI interface provides several tabs:

1. **Dashboard**: Overview of pool status and customer information
2. **Water Testing**: Enter and analyze water test results
3. **History**: View historical test data and trends
4. **Settings**: Configure application settings


Web Interface

The web interface provides access to:

• Current pool status
• Sensor readings
• System controls


Arduino Integration

To use Arduino integration:

1. Connect your Arduino to the computer
2. The application will automatically detect and connect to it
3. Sensor readings will be displayed in real-time


Test Strip Analysis

To analyze test strips:

1. Place a test strip on a well-lit surface
2. Click "Analyze Test Strip" in the Water Testing tab
3. The application will capture and analyze the strip
4. Results will be displayed automatically


Troubleshooting

Application Won't Start

If the application fails to start:

1. Check that all dependencies are installed:
```
pip install -r requirements.txt
```

2. Check the log files in the `logs` directory for error messages

3. Verify that the `config.json` file exists and is valid


GUI Issues

If the GUI doesn't appear:

1. Verify that Tkinter is installed:
```
python -c "import tkinter; print('Tkinter is installed')"
```

2. Try running just the GUI component:
```
python app/gui_launcher.py
```


Arduino Connection Problems

If the Arduino doesn't connect:

1. Check that the Arduino is properly connected to the computer
2. Verify that the correct port is selected
3. Make sure the Arduino has the correct firmware installed


Development

Project Structure
• `main_app.py`: Backend pool controller
• `integrated_app.py`: Combined backend and GUI
• `app/`: GUI components
- `gui_elements.py`: Main GUI implementation
- `gui_controller.py`: Controller for GUI logic
- `gui_launcher.py`: Standalone GUI launcher
• `arduino_interface.py`: Arduino communication module
• `test_strip_analyzer.py`: Test strip analysis module
• `config.json`: Application configuration


Adding New Features
1. For backend features, modify `main_app.py`
2. For GUI features, modify files in the `app` directory
3. For Arduino features, modify `arduino_interface.py`
4. For test strip analysis, modify `test_strip_analyzer.py`


License

This project is licensed under the MIT License - see the LICENSE file for details.


Acknowledgments
• Thanks to the Arduino community for sensor libraries
• OpenCV for computer vision capabilities
• Tkinter for GUI components