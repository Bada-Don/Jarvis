@echo off
echo ========================================
echo    Starting JARVIS - AI Assistant
echo ========================================
echo.

:: Terminal 1: Frontend (ChatInterface)
echo Starting Frontend...
start "JARVIS Frontend" cmd /k "cd ChatInterface && npm start"

:: Wait a moment before starting backend
timeout /t 2 /nobreak >nul

:: Terminal 2: Backend Server (with venv)
echo Starting Backend Server...
start "JARVIS Backend" cmd /k "cd backend && call venv\Scripts\activate && python server.py"

:: Wait a moment before starting local client
timeout /t 2 /nobreak >nul

:: Terminal 3: Local Client (using backend venv)
echo Starting Local Client...
start "JARVIS Local Client" cmd /k "cd local_client && call ..\backend\venv\Scripts\activate && python client.py"

echo.
echo ========================================
echo    All services starting...
echo ========================================
echo.
echo Frontend:     http://localhost:19006
echo Backend:      http://localhost:5000
echo.
echo Close this window or press any key to exit.
pause >nul
