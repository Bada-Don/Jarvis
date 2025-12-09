@echo off
echo ========================================
echo    Starting JARVIS - AI Assistant
echo ========================================
echo.

:: Use Windows Terminal with tabs (wt command)
:: All three services open as tabs in a single Windows Terminal window

echo Starting all services in Windows Terminal tabs...

wt -w 0 new-tab --title "JARVIS Frontend" -d "%~dp0ChatInterface" cmd /k "npm start" ; ^
   new-tab --title "JARVIS Backend" -d "%~dp0backend" cmd /k "call venv\Scripts\activate && python server.py" ; ^
   new-tab --title "JARVIS Local Client" -d "%~dp0local_client" cmd /k "call ..\backend\venv\Scripts\activate && python client.py"

echo.
echo ========================================
echo    All services started in tabs!
echo ========================================
echo.
echo Frontend:     http://localhost:19006
echo Backend:      http://localhost:5000
echo.
