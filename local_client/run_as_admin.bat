@echo off
echo Starting JARVIS Local Client with Administrator Privileges...
echo.

REM Check if running as admin
net session >nul 2>&1
if %errorLevel% == 0 (
    echo Already running as Administrator.
    echo.
) else (
    echo Requesting Administrator privileges...
    echo.
    powershell -Command "Start-Process cmd -ArgumentList '/c cd /d %~dp0 && python client.py' -Verb RunAs"
    exit
)

REM If we're here, we have admin rights
cd /d "%~dp0"
python client.py

pause
