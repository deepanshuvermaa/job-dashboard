# Setup Guide - LinkedIn Automation Suite

## ✅ Your Credentials Are Configured!

Your `.env` file is ready with:
- ✅ LinkedIn email & password
- ✅ GitHub token
- ✅ OpenAI API key
- ✅ JWT secret (randomly generated)

---

## 📋 Prerequisites to Install

You need these before running the project:

### 1. **Python 3.11+**
**Download:** https://www.python.org/downloads/

**Installation Steps:**
1. Download Python 3.11 or 3.12
2. **IMPORTANT:** Check "Add Python to PATH" during installation
3. Verify: Open new terminal and run:
   ```bash
   python --version
   ```
   Should show: `Python 3.11.x` or higher

### 2. **Node.js 20+**
**Download:** https://nodejs.org/

**Installation Steps:**
1. Download LTS version (20.x)
2. Install with default settings
3. Verify:
   ```bash
   node --version
   npm --version
   ```

### 3. **PostgreSQL** (Database)

**Option A: Use Docker (Easier)**
1. Start Docker Desktop
2. Run:
   ```bash
   cd linkedin-automation-suite
   docker-compose up -d postgres redis
   ```

**Option B: Install Locally**
- **Download:** https://www.postgresql.org/download/windows/
- Install version 15+
- Remember the password you set
- Default port: 5432

**Option C: Use Cloud (Easiest)**
- **Supabase:** https://supabase.com (Free tier)
- Create project → Get connection string
- Update `.env`:
  ```env
  DATABASE_URL=postgresql://user:password@host:5432/database
  ```

### 4. **Redis** (Caching)

**Option A: Docker**
```bash
docker-compose up -d redis
```

**Option B: Use Cloud**
- **Upstash:** https://upstash.com (Free tier)
- Create Redis database
- Update `.env`:
  ```env
  REDIS_URL=redis://default:password@host:6379
  ```

**Option C: Skip for now**
- Comment out Redis in code (non-critical for testing)

---

## 🚀 Quick Start (After Prerequisites)

### Step 1: Install Backend Dependencies

Open terminal in project folder:

```bash
cd linkedin-automation-suite/backend

# Create virtual environment
python -m venv venv

# Activate it (Windows)
venv\Scripts\activate

# Install packages
pip install -r requirements.txt
```

### Step 2: Install Frontend Dependencies

Open **new terminal**:

```bash
cd linkedin-automation-suite/frontend

# Install packages
npm install
```

### Step 3: Initialize Database

If using local PostgreSQL:

```bash
# Connect to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE linkedin_automation;

# Exit
\q

# Import schema
psql -U postgres -d linkedin_automation -f ../database/schema.sql
```

If using Supabase/cloud:
- Copy contents of `database/schema.sql`
- Paste into Supabase SQL Editor
- Run

### Step 4: Start Backend

In backend terminal (with venv activated):

```bash
cd linkedin-automation-suite/backend
venv\Scripts\activate
uvicorn api.main:app --reload
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

### Step 5: Start Frontend

In frontend terminal:

```bash
cd linkedin-automation-suite/frontend
npm run dev
```

You should see:
```
  ▲ Next.js 14.1.0
  - Local:        http://localhost:3000
  - Ready in 2s
```

### Step 6: Open Application

**Open browser:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000/docs

---

## 🎯 First Test - Generate Content

### Test GitHub Integration (API):

```bash
curl -X POST http://localhost:8000/api/content/github-activity \
  -H "Content-Type: application/json" \
  -d "{\"github_username\": \"deepanshuverma966\", \"days\": 7}"
```

Should return your recent GitHub commits!

### Test in Browser:

1. Go to http://localhost:3000
2. Click "Content Engine" card
3. Should fetch your GitHub activity automatically

---

## 🐛 Troubleshooting

### "Python not found"
- Reinstall Python with "Add to PATH" checked
- Restart terminal after installation
- Try: `py --version` instead of `python --version`

### "pip not found"
```bash
python -m ensurepip
python -m pip install --upgrade pip
```

### "Module not found" errors
```bash
# Make sure virtual environment is activated
cd backend
venv\Scripts\activate
pip install -r requirements.txt
```

### "Database connection error"
- Check PostgreSQL is running
- Verify connection string in `.env`
- Try: `psql -U postgres` to test connection

### "Port already in use"
**Backend (port 8000):**
```bash
# Find and kill process on Windows
netstat -ano | findstr :8000
taskkill /PID <process_id> /F
```

**Frontend (port 3000):**
```bash
netstat -ano | findstr :3000
taskkill /PID <process_id> /F
```

### "Docker Desktop not running"
- Start Docker Desktop manually
- Wait for it to fully start (whale icon in taskbar)
- Then run: `docker-compose up -d`

---

## 📱 Without Docker (Manual Setup)

If you can't use Docker, here's the manual way:

### 1. Install PostgreSQL
- Download: https://www.postgresql.org/download/windows/
- Install with default settings
- Remember password

### 2. Install Redis (Windows)
- Download: https://github.com/microsoftarchive/redis/releases
- Or use cloud: https://upstash.com

### 3. Start Services
```bash
# PostgreSQL starts automatically as Windows service
# Redis:
redis-server

# Or use cloud services and update .env
```

### 4. Run Application
```bash
# Terminal 1 - Backend
cd backend
venv\Scripts\activate
uvicorn api.main:app --reload

# Terminal 2 - Frontend
cd frontend
npm run dev
```

---

## 🎉 Success!

When everything is running:

1. **Frontend**: http://localhost:3000
   - Beautiful dashboard with stats
   - Content queue
   - Job search

2. **Backend API**: http://localhost:8000/docs
   - Interactive API documentation
   - Test endpoints

3. **First Login**:
   - Click any automation feature
   - Chrome will open
   - Log in to LinkedIn manually
   - Session will be saved

---

## 📞 Need Help?

**Common Issues:**
1. Python not in PATH → Reinstall with PATH checkbox
2. PostgreSQL connection → Use Supabase cloud instead
3. Redis connection → Use Upstash cloud instead
4. Port conflicts → Change ports in docker-compose.yml

**Still stuck?**
- Check README.md for detailed docs
- Open GitHub issue with error message

---

## 🔒 Security Reminder

Your credentials are in `.env` which is:
- ✅ Already in `.gitignore` (won't be committed)
- ❌ Never share this file
- ❌ Never commit to GitHub
- ✅ Rotate keys if exposed

---

## ⏭️ Next Steps (After Setup Works)

1. **Test Content Generation**
   - Let AI generate posts from GitHub
   - Review in http://localhost:3000/content/queue

2. **Test Job Search**
   - Search jobs at http://localhost:3000/jobs/search
   - Apply to test jobs

3. **Customize**
   - Edit `backend/config/content/pillars.yaml`
   - Update `backend/config/jobs/search_params.yaml`
   - Modify `backend/config/jobs/user_profile.yaml`

4. **Deploy** (Optional)
   - Railway: https://railway.app
   - Render: https://render.com
   - Vercel (frontend only): https://vercel.com

---

**Current Status:** ✅ Credentials configured, ready to install prerequisites and run!
