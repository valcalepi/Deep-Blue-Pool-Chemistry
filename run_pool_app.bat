
@echo off
REM Run script for Deep Blue Pool Chemistry
REM This script activates the virtual environment and runs the integrated application

echo Starting Deep Blue Pool Chemistry...

REM Check if virtual environment exists
if not exist venv (
    echo Virtual environment not found. Please run setup.bat first.
    pause
    exit /b 1
)

REM Activate virtual environment
call venv\Scripts\activate.bat
if %ERRORLEVEL% NEQ 0 (
    echo Failed to activate virtual environment.
    pause
    exit /b 1
)

REM Run the application
python integrated_app.py
if %ERRORLEVEL% NEQ 0 (
    echo Application exited with error code %ERRORLEVEL%.
    pause
    exit /b %ERRORLEVEL%
)

REM Deactivate virtual environment
call venv\Scripts\deactivate.bat

pause
