@echo off
title KARVION BD - 1-Click Startup System
color 0B

echo ========================================================
echo         KARVION BD - AI Life & Service Automation
echo ========================================================
echo.
echo [1/2] Starting FastAPI Backend on Port 8000...
start "KARVION BD Backend" cmd /k "cd /d "%~dp0apps\api" && if exist venv\Scripts\activate.bat (call venv\Scripts\activate.bat) else (echo VENV missing! Run setup first.) && python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload"

echo [2/2] Starting Next.js Frontend on Port 3005...
start "KARVION BD Frontend" cmd /k "cd /d "%~dp0apps\web" && npm run dev"

echo.
echo All services launched! 
echo Frontend URL: http://localhost:3005
echo Backend API: http://localhost:8000
echo.
echo Please do not close this window to keep the system running.
pause
