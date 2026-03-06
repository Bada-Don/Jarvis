@echo off
REM Install JARVIS Client as Windows Service
REM Run this as Administrator

echo ========================================
echo JARVIS Client - Windows Service Setup
echo ========================================
echo.

REM Check for admin privileges
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: This script must be run as Administrator
    echo Right-click and select "Run as administrator"
    pause
    exit /b 1
)

echo Installing JARVIS Client as Windows Service...
python install_windows_service.py install

echo.
echo Starting JARVIS Client service...
python install_windows_service.py start

echo.
echo ========================================
echo Service installed and started!
echo ========================================
echo.
echo Service Name: JarvisClient
echo Display Name: JARVIS Local Client
echo.
echo To manage the service:
echo   Start:   python install_windows_service.py start
echo   Stop:    python install_windows_service.py stop
echo   Remove:  python install_windows_service.py remove
echo.
echo Or use Windows Services (services.msc)
echo.
pause
