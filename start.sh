#!/usr/bin/env bash
# LinkedIn Automation Suite - Local Launcher
set -e

PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_ROOT"

echo "============================================"
echo "  LinkedIn Automation Suite - Local Launcher"
echo "============================================"
echo ""

# ---- Check Python venv ----
if [ ! -f "backend/venv/Scripts/python.exe" ] && [ ! -f "backend/venv/bin/python" ]; then
    echo "[!] Python venv not found. Creating..."
    cd backend
    python -m venv venv
    if [ -f "venv/Scripts/activate" ]; then
        source venv/Scripts/activate
    else
        source venv/bin/activate
    fi
    pip install -r requirements.txt
    cd ..
    echo "[OK] Python venv created."
else
    echo "[OK] Python venv found."
fi

# ---- Check node_modules ----
if [ ! -d "frontend/node_modules" ]; then
    echo "[!] node_modules not found. Installing..."
    cd frontend && npm install && cd ..
    echo "[OK] npm dependencies installed."
else
    echo "[OK] node_modules found."
fi

# ---- Create data dirs ----
mkdir -p backend/data/resumes
echo "[OK] Data directories ready."

echo ""
echo "============================================"
echo "  Starting Backend (port 8000)"
echo "  Starting Frontend (port 3000)"
echo "============================================"
echo ""
echo "  Dashboard:  http://localhost:3000"
echo "  API Docs:   http://localhost:8000/docs"
echo "  Job Feed:   http://localhost:3000/jobs/feed"
echo "  Outreach:   http://localhost:3000/outreach"
echo "  Resume:     http://localhost:3000/resume"
echo ""

# ---- Activate venv ----
if [ -f "backend/venv/Scripts/activate" ]; then
    ACTIVATE="backend/venv/Scripts/activate"
else
    ACTIVATE="backend/venv/bin/activate"
fi

# ---- Start Backend ----
echo "[*] Starting backend..."
(cd backend && source "../$ACTIVATE" && python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000) &
BACKEND_PID=$!

# ---- Wait for backend ----
sleep 3

# ---- Start Frontend ----
echo "[*] Starting frontend..."
(cd frontend && npm run dev) &
FRONTEND_PID=$!

# ---- Cleanup on exit ----
trap "echo ''; echo 'Shutting down...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit 0" INT TERM

echo ""
echo "[OK] Both servers running. Press Ctrl+C to stop."
echo ""

# ---- Wait ----
wait
