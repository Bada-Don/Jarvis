@echo off
REM Remove JARVIS Client Windows Service
REM Run this as Administrator

echo ========================================
echo JARVIS Client - Remove Windows Service
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

echo Stopping JARVIS Client service...
python install_windows_service.py stop

echo.
echo Removing JARVIS Client service...
python install_windows_service.py remove

echo.
echo ========================================
echo Service removed successfully!
echo ========================================
echo.
pause
