@echo off
color 0B
echo ==================================================
echo   Starting KARVION BD - AI Service Platform
echo ==================================================
echo.

echo [1/2] Starting FastAPI Backend on Port 8000...
start cmd /k "title FastAPI Backend && cd /d "%~dp0apps\api" && if exist venv\Scripts\activate.bat (call venv\Scripts\activate.bat) else (echo VENV not found!) && python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload"

echo [2/2] Starting Next.js Frontend on Port 3005...
start cmd /k "title Next.js Frontend && cd /d "%~dp0apps\web" && npm run dev"

echo.
echo Services are starting in separate windows.
echo - Backend: http://localhost:8000
echo - Frontend: http://localhost:3005
echo.
pause
