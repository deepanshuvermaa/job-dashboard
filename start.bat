@echo off
title LinkedIn Automation Suite - Launcher
color 0A

echo ============================================
echo   LinkedIn Automation Suite - Local Launcher
echo ============================================
echo.

:: Set project root
set PROJECT_ROOT=%~dp0
cd /d "%PROJECT_ROOT%"

:: ---- Check Python venv ----
if not exist "backend\venv\Scripts\python.exe" (
    echo [!] Python venv not found. Creating...
    cd backend
    python -m venv venv
    call venv\Scripts\activate.bat
    pip install -r requirements.txt
    cd ..
    echo [OK] Python venv created and dependencies installed.
) else (
    echo [OK] Python venv found.
)

:: ---- Check node_modules ----
if not exist "frontend\node_modules" (
    echo [!] node_modules not found. Installing...
    cd frontend
    call npm install
    cd ..
    echo [OK] npm dependencies installed.
) else (
    echo [OK] node_modules found.
)

:: ---- Create data directories ----
if not exist "backend\data" mkdir "backend\data"
if not exist "backend\data\resumes" mkdir "backend\data\resumes"
echo [OK] Data directories ready.

echo.
echo ============================================
echo   Starting Backend (FastAPI on port 8000)
echo   Starting Frontend (Next.js on port 3000)
echo ============================================
echo.
echo   Dashboard:  http://localhost:3000
echo   API Docs:   http://localhost:8000/docs
echo   Job Feed:   http://localhost:3000/jobs/feed
echo   Outreach:   http://localhost:3000/outreach
echo   Resume:     http://localhost:3000/resume
echo.
echo   Press Ctrl+C in each window to stop.
echo ============================================
echo.

:: ---- Start Backend in new terminal ----
start "Backend - FastAPI" cmd /k "cd /d %PROJECT_ROOT%backend && call venv\Scripts\activate.bat && python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000"

:: ---- Wait 2 seconds for backend to initialize ----
timeout /t 3 /noq >nul

:: ---- Start Frontend in new terminal ----
start "Frontend - Next.js" cmd /k "cd /d %PROJECT_ROOT%frontend && npm run dev"

:: ---- Wait then open browser ----
timeout /t 5 /noq >nul
start http://localhost:3000

echo.
echo [OK] Both servers launched in separate windows.
echo     Close this window or press any key to exit.
echo.
pause
