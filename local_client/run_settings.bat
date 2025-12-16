@echo off
REM Launcher batch file for JARVIS Settings Interface (Windows)
REM This provides a convenient way to launch the settings interface on Windows

echo Starting JARVIS Settings Interface...
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher
    pause
    exit /b 1
)

REM Launch the settings interface
python "%~dp0run_settings.py" %*

REM Pause if there was an error
if errorlevel 1 (
    echo.
    echo Press any key to exit...
    pause >nul
)
