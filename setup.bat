
@echo off
REM Setup script for Deep Blue Pool Chemistry
REM This script installs all required dependencies and sets up the environment

echo Deep Blue Pool Chemistry - Setup Script
echo This script will install all required dependencies and set up the environment.
echo.

REM Check if Python is installed
echo Checking Python installation...
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Python not found. Please install Python 3.8 or higher.
    exit /b 1
)

REM Check Python version
for /f "tokens=*" %%a in ('python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"') do set PYTHON_VERSION=%%a
echo Python version: %PYTHON_VERSION%

REM Check if pip is installed
echo.
echo Checking pip installation...
where pip >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo pip not found. Attempting to install pip...
    python -m ensurepip --upgrade
    if %ERRORLEVEL% NEQ 0 (
        echo Failed to install pip. Please install pip manually.
        exit /b 1
    )
)
echo pip found.

REM Create virtual environment
echo.
echo Setting up virtual environment...
if exist venv (
    echo Virtual environment already exists.
    set /p RECREATE="Do you want to recreate it? (y/n) "
    if /i "%RECREATE%"=="y" (
        echo Removing existing virtual environment...
        rmdir /s /q venv
        python -m venv venv
        echo Virtual environment created.
    )
) else (
    python -m venv venv
    echo Virtual environment created.
)

REM Activate virtual environment
echo.
echo Activating virtual environment...
call venv\Scripts\activate.bat
if %ERRORLEVEL% NEQ 0 (
    echo Failed to activate virtual environment.
    exit /b 1
)
echo Virtual environment activated.

REM Install dependencies
echo.
echo Installing dependencies...
pip install --upgrade pip
pip install -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo Failed to install dependencies.
    exit /b 1
)
echo Dependencies installed successfully.

REM Create necessary directories
echo.
echo Creating necessary directories...
if not exist logs mkdir logs
if not exist data mkdir data
if not exist cache mkdir cache
if not exist config mkdir config
echo Directories created.

REM Create default configuration if it doesn't exist
echo.
echo Checking configuration...
if not exist config.json (
    echo Configuration file not found. Creating default configuration...
    echo {> config.json
    echo   "location": "Florida",>> config.json
    echo   "weather_update_interval": 3600,>> config.json
    echo   "schedules": [>> config.json
    echo     {>> config.json
    echo       "name": "Daily Filtration",>> config.json
    echo       "type": "recurring",>> config.json
    echo       "days": ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"],>> config.json
    echo       "start_time": "08:00",>> config.json
    echo       "end_time": "16:00",>> config.json
    echo       "actions": ["pump_on"]>> config.json
    echo     },>> config.json
    echo     {>> config.json
    echo       "name": "Weekly Cleaning",>> config.json
    echo       "type": "recurring",>> config.json
    echo       "days": ["saturday"],>> config.json
    echo       "start_time": "10:00",>> config.json
    echo       "end_time": "12:00",>> config.json
    echo       "actions": ["cleaning_mode_on"]>> config.json
    echo     }>> config.json
    echo   ],>> config.json
    echo   "thresholds": {>> config.json
    echo     "temperature_min": 75.0,>> config.json
    echo     "temperature_max": 85.0,>> config.json
    echo     "ph_min": 7.0,>> config.json
    echo     "ph_max": 7.6,>> config.json
    echo     "chlorine_min": 1.0,>> config.json
    echo     "chlorine_max": 3.0>> config.json
    echo   },>> config.json
    echo   "database_path": "pool_data.db",>> config.json
    echo   "web_interface_enabled": true,>> config.json
    echo   "web_interface_host": "0.0.0.0",>> config.json
    echo   "web_interface_port": 8080,>> config.json
    echo   "gui_enabled": true>> config.json
    echo }>> config.json
    echo Default configuration created.
) else (
    echo Configuration file found.
)

REM Final message
echo.
echo Setup complete!
echo You can now run the application using:
echo   run_pool_app.bat - For the integrated application (GUI + backend)
echo   python main_app.py - For the backend only (with web interface)
echo.
echo Remember to activate the virtual environment before running the application:
echo   venv\Scripts\activate
echo.

pause
