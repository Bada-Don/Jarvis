@echo off
echo ========================================
echo    Starting JARVIS - AI Assistant
echo ========================================
echo.

:: Check if Windows Terminal is available
where wt >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo Starting all services in Windows Terminal tabs...
    wt -w 0 new-tab --title "JARVIS Frontend" -d "%~dp0ChatInterface" cmd /k "npm start" ; ^
       new-tab --title "JARVIS Backend" -d "%~dp0backend" cmd /k "call ..\venv\Scripts\activate && python server.py" ; ^
       new-tab --title "JARVIS Local Client" -d "%~dp0local_client" cmd /k "call ..\venv\Scripts\activate && python run_client.py"
) else (
    echo Windows Terminal not found. Starting services in separate windows...
    
    :: Start Frontend
    start "JARVIS Frontend" cmd /k "cd /d %~dp0ChatInterface && npm start"
    
    :: Start Backend
    start "JARVIS Backend" cmd /k "cd /d %~dp0backend && call ..\venv\Scripts\activate && python server.py"
    
    :: Start Local Client
    start "JARVIS Local Client" cmd /k "cd /d %~dp0local_client && call ..\venv\Scripts\activate && python run_client.py"
)

echo.
echo ========================================
echo    All services started!
echo ========================================
echo.
echo Frontend:     http://localhost:19006
echo Backend:      http://localhost:5000
echo.
pause
