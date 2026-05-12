# Quick Start Guide

Get up and running in 5 minutes.

## 1. Clone & Install

```bash
git clone <your-repo>
cd linkedin-automation-suite

# Windows
scripts\setup\install.bat

# Mac/Linux
chmod +x scripts/setup/install.sh
./scripts/setup/install.sh
```

## 2. Configure

Edit `.env` with your credentials:

```env
# Required
LINKEDIN_EMAIL=your_email@example.com
LINKEDIN_PASSWORD=your_password
GITHUB_TOKEN=your_github_token
GITHUB_USERNAME=your_username

# At least one AI provider
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=...
ANTHROPIC_API_KEY=sk-ant-...
```

## 3. Start Services

### Option A: Docker (Easiest)

```bash
docker-compose up -d
```

### Option B: Manual

**Terminal 1 - Database:**
```bash
# Start PostgreSQL (port 5432) and Redis (port 6379)
# Or use cloud services
```

**Terminal 2 - Backend:**
```bash
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate
python -m uvicorn api.main:app --reload
```

**Terminal 3 - Frontend:**
```bash
cd frontend
npm run dev
```

## 4. First Login

1. Open http://localhost:3000
2. Click any automation feature
3. Chrome will open automatically
4. **Log in to LinkedIn manually**
5. Complete 2FA if required
6. Session will be saved

## 5. Generate Your First Post

**Via UI:**
1. Go to http://localhost:3000
2. Click "Content Engine"
3. System will fetch your GitHub activity
4. Review AI-generated posts at http://localhost:3000/content/queue
5. Approve and schedule

**Via API:**
```bash
curl -X POST http://localhost:8000/api/content/github-activity \
  -H "Content-Type: application/json" \
  -d '{
    "github_username": "your_username",
    "days": 7
  }'
```

## 6. Apply to Jobs

**Via UI:**
1. Go to http://localhost:3000/jobs/search
2. Enter keywords: "Full Stack Engineer"
3. Click "Search Jobs"
4. Review results
5. Click "Quick Apply"

**Via API:**
```bash
curl -X POST http://localhost:8000/api/jobs/search \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_123",
    "keywords": "React Developer",
    "location": "United States",
    "max_results": 30
  }'
```

## 7. View Analytics

Go to http://localhost:3000/analytics to see:
- Post performance
- Application metrics
- Engagement trends
- Success rates

## Troubleshooting

**Port already in use:**
```bash
# Change ports in docker-compose.yml or use:
docker-compose down
```

**Can't login to LinkedIn:**
```bash
# Clear session and try again:
rm -rf sessions/
```

**Chrome driver issues:**
```bash
pip uninstall undetected-chromedriver
pip install undetected-chromedriver --upgrade
```

**AI generation fails:**
- Check API keys in `.env`
- Verify API credits/quota
- System will auto-fallback to alternative provider

## What's Next?

- **Customize Content Pillars**: Settings > Content Pillars
- **Set Rate Limits**: `backend/core/config.py`
- **Configure Job Filters**: `backend/config/jobs/search_params.yaml`
- **Schedule Automation**: Set up cron jobs or use background workers

## Daily Usage

**Morning routine (5-10 minutes):**
1. Open http://localhost:3000
2. Review 2-3 generated posts → Approve one
3. Check job applications queue → Approve 5-10
4. Done!

System handles:
- Posting at optimal times
- Applying to jobs throughout the day
- Tracking engagement
- Generating tomorrow's content

---

**Need help?** Check the full README.md or open an issue.

**Ready to scale?** Deploy to Railway/Render for 24/7 automation.
