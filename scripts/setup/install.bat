@echo off
echo 🚀 LinkedIn Automation Suite - Installation Script
echo ==================================================

REM Check Python
echo.
echo 📋 Checking prerequisites...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found. Please install Python 3.11+
    exit /b 1
)
echo ✅ Python installed

REM Check Node
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js not found. Please install Node.js 20+
    exit /b 1
)
echo ✅ Node.js installed

REM Setup environment
echo.
echo ⚙️  Setting up environment...
if not exist .env (
    copy .env.example .env
    echo ✅ Created .env file
    echo ⚠️  Please edit .env and add your credentials
) else (
    echo ✅ .env file already exists
)

REM Install backend dependencies
echo.
echo 📦 Installing backend dependencies...
cd backend
python -m venv venv
call venv\Scripts\activate
pip install -r requirements.txt
cd ..
echo ✅ Backend dependencies installed

REM Install frontend dependencies
echo.
echo 📦 Installing frontend dependencies...
cd frontend
call npm install
cd ..
echo ✅ Frontend dependencies installed

REM Create directories
echo.
echo 📁 Creating directories...
if not exist sessions mkdir sessions
if not exist logs mkdir logs
if not exist temp mkdir temp
echo ✅ Directories created

echo.
echo ✨ Installation complete!
echo.
echo Next steps:
echo 1. Edit .env with your credentials
echo 2. Start PostgreSQL and Redis (or use Docker)
echo 3. Run: docker-compose up -d
echo 4. Visit http://localhost:3000
echo.
pause
