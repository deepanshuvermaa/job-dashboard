@echo off
title LinkedIn Automation Suite
color 0A
cd /d "%~dp0"

echo.
echo  ========================================
echo   LinkedIn Automation Suite - Launcher
echo  ========================================
echo.

:: ===== Step 1: Setup Python venv =====
if not exist "backend\venv\Scripts\python.exe" (
    echo [1/4] Creating Python virtual environment...
    cd backend
    python -m venv venv
    cd ..
) else (
    echo [1/4] Python venv found.
)

:: ===== Step 2: Install Python deps =====
echo [2/4] Installing Python dependencies...
backend\venv\Scripts\pip.exe install --quiet ^
    fastapi uvicorn[standard] pydantic python-dotenv pyyaml ^
    beautifulsoup4 requests httpx python-multipart ^
    openai google-generativeai anthropic ^
    pillow openpyxl selenium undetected-chromedriver ^
    jinja2
if errorlevel 1 (
    echo [ERROR] pip install failed. Check your internet connection.
    pause
    exit /b 1
)
echo        Done.

:: ===== Step 3: Install Node deps =====
if not exist "frontend\node_modules\next" (
    echo [3/4] Installing Node.js dependencies...
    cd frontend
    call npm install --silent
    cd ..
) else (
    echo [3/4] Node modules found.
)

:: ===== Step 4: Create data dirs =====
if not exist "backend\data" mkdir "backend\data"
if not exist "backend\data\resumes" mkdir "backend\data\resumes"
echo [4/4] Data directories ready.

echo.
echo  ========================================
echo   Starting servers...
echo  ========================================
echo.
echo   Frontend:   http://localhost:3000
echo   Backend:    http://localhost:8000
echo   API Docs:   http://localhost:8000/docs
echo.
echo   Job Feed:   http://localhost:3000/jobs/feed
echo   Outreach:   http://localhost:3000/outreach
echo   Resume:     http://localhost:3000/resume
echo   Hacks:      http://localhost:3000/hacks
echo.

:: ===== Start Backend =====
start "Backend" cmd /k "cd /d %~dp0backend && venv\Scripts\python.exe -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000"

:: ===== Wait for backend to boot =====
timeout /t 4 /noq >nul

:: ===== Start Frontend =====
start "Frontend" cmd /k "cd /d %~dp0frontend && npm run dev"

:: ===== Open browser after frontend boots =====
timeout /t 5 /noq >nul
start http://localhost:3000

echo.
echo  [OK] Both servers running in separate windows.
echo  Close this window whenever you want.
echo.
pause
