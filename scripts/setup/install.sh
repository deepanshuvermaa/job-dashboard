#!/bin/bash

echo "🚀 LinkedIn Automation Suite - Installation Script"
echo "=================================================="

# Check prerequisites
echo "\n📋 Checking prerequisites..."

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.11+"
    exit 1
fi
echo "✅ Python $(python3 --version)"

# Check Node
if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found. Please install Node.js 20+"
    exit 1
fi
echo "✅ Node.js $(node --version)"

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "⚠️  Docker not found. Install Docker for easier setup."
else
    echo "✅ Docker $(docker --version)"
fi

# Setup environment
echo "\n⚙️  Setting up environment..."

if [ ! -f .env ]; then
    cp .env.example .env
    echo "✅ Created .env file"
    echo "⚠️  Please edit .env and add your credentials"
else
    echo "✅ .env file already exists"
fi

# Install backend dependencies
echo "\n📦 Installing backend dependencies..."
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cd ..
echo "✅ Backend dependencies installed"

# Install frontend dependencies
echo "\n📦 Installing frontend dependencies..."
cd frontend
npm install
cd ..
echo "✅ Frontend dependencies installed"

# Create directories
echo "\n📁 Creating directories..."
mkdir -p sessions
mkdir -p logs
mkdir -p temp
echo "✅ Directories created"

echo "\n✨ Installation complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env with your credentials"
echo "2. Start PostgreSQL and Redis (or use Docker)"
echo "3. Run database migrations: psql -U postgres -d linkedin_automation -f database/schema.sql"
echo "4. Start backend: cd backend && source venv/bin/activate && python -m uvicorn api.main:app --reload"
echo "5. Start frontend: cd frontend && npm run dev"
echo "6. Visit http://localhost:3000"
echo ""
echo "Or use Docker:"
echo "docker-compose up -d"
