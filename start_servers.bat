@echo off
echo ========================================
echo Korean Stock Backtesting Platform Startup
echo ========================================

:: Start API Server
echo Starting API Server on port 8001...
start cmd /k "cd /d %~dp0 && python api_server.py"

:: Wait a moment for API server to start
timeout /t 3 /nobreak > nul

:: Start Frontend
echo Starting Frontend on port 3000...
start cmd /k "cd /d %~dp0frontend && npm run dev"

echo ========================================
echo All servers started!
echo.
echo API Server: http://localhost:8001
echo API Docs: http://localhost:8001/docs
echo Frontend: http://localhost:3000
echo.
echo Press any key to exit this window...
pause > nul