@echo off
echo ========================================
echo LinkedIn Automation Suite
echo Prerequisites Checker
echo ========================================
echo.

REM Check Python
echo [1/5] Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python NOT installed
    echo    Download: https://www.python.org/downloads/
    echo    IMPORTANT: Check "Add Python to PATH"
    set PYTHON_OK=0
) else (
    for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VER=%%i
    echo ✅ Python %PYTHON_VER% installed
    set PYTHON_OK=1
)
echo.

REM Check Node.js
echo [2/5] Checking Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js NOT installed
    echo    Download: https://nodejs.org/
    set NODE_OK=0
) else (
    for /f %%i in ('node --version') do set NODE_VER=%%i
    echo ✅ Node.js %NODE_VER% installed
    set NODE_OK=1
)
echo.

REM Check npm
echo [3/5] Checking npm...
npm --version >nul 2>&1
if errorlevel 1 (
    echo ❌ npm NOT installed
    set NPM_OK=0
) else (
    for /f %%i in ('npm --version') do set NPM_VER=%%i
    echo ✅ npm %NPM_VER% installed
    set NPM_OK=1
)
echo.

REM Check Docker
echo [4/5] Checking Docker (optional)...
docker --version >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Docker NOT installed (optional)
    echo    For easier setup: https://www.docker.com/products/docker-desktop
    set DOCKER_OK=0
) else (
    for /f "tokens=3" %%i in ('docker --version') do set DOCKER_VER=%%i
    echo ✅ Docker %DOCKER_VER% installed
    set DOCKER_OK=1
)
echo.

REM Check .env
echo [5/5] Checking .env configuration...
if exist .env (
    findstr /C:"LINKEDIN_EMAIL=deepanshuverma966@gmail.com" .env >nul
    if errorlevel 1 (
        echo ⚠️  .env exists but may not be configured
    ) else (
        echo ✅ .env file configured
    )
) else (
    echo ❌ .env file NOT found
    echo    Run: copy .env.example .env
)
echo.

echo ========================================
echo Summary
echo ========================================

if "%PYTHON_OK%"=="1" if "%NODE_OK%"=="1" if "%NPM_OK%"=="1" (
    echo.
    echo ✅ Core prerequisites met! You can proceed with setup.
    echo.
    echo Next steps:
    echo 1. Install backend dependencies:
    echo    cd backend
    echo    python -m venv venv
    echo    venv\Scripts\activate
    echo    pip install -r requirements.txt
    echo.
    echo 2. Install frontend dependencies:
    echo    cd frontend
    echo    npm install
    echo.
    echo 3. Start Docker services (if using Docker):
    echo    docker-compose up -d
    echo.
    echo 4. Or start manually:
    echo    - Backend: cd backend ^&^& venv\Scripts\activate ^&^& uvicorn api.main:app --reload
    echo    - Frontend: cd frontend ^&^& npm run dev
    echo.
    echo See SETUP_GUIDE.md for detailed instructions
) else (
    echo.
    echo ❌ Some prerequisites are missing.
    echo.
    echo Please install:
    if "%PYTHON_OK%"=="0" echo    - Python 3.11+ from https://www.python.org/downloads/
    if "%NODE_OK%"=="0" echo    - Node.js 20+ from https://nodejs.org/
    if "%NPM_OK%"=="0" echo    - npm (comes with Node.js)
    echo.
    echo Then run this script again.
)

echo.
echo Full guide: SETUP_GUIDE.md
echo.
pause
