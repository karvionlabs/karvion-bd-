Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  Starting KARVION BD - AI Service Platform " -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "[1/2] Starting FastAPI Backend (Port 8000)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd 'd:\KARVION BD\apps\api'; if (Test-Path .\venv\Scripts\Activate.ps1) { .\venv\Scripts\Activate.ps1 }; uvicorn main:app --host 0.0.0.0 --port 8000 --reload" -WindowStyle Normal

Write-Host "[2/2] Starting Next.js Frontend (Port 3000)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd 'd:\KARVION BD\apps\web'; npm run dev" -WindowStyle Normal

Write-Host ""
Write-Host "Services are booting up in separate windows!" -ForegroundColor Green
Write-Host "-> Backend API: http://localhost:8000" -ForegroundColor Gray
Write-Host "-> Frontend UI: http://localhost:3000" -ForegroundColor Gray
Write-Host "-> Please wait a few seconds for Next.js to compile." -ForegroundColor Gray
Write-Host ""
