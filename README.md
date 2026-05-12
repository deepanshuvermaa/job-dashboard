# LinkedIn Automation Suite

Complete automation platform for LinkedIn content creation and job applications. Combines AI-powered content generation with intelligent job search and application automation.

## 🚀 Features

### Content Engine
- **GitHub Integration**: Automatically monitors your repos for content-worthy activities
- **AI Content Generation**: Creates authentic LinkedIn posts from your work
- **Multi-LLM Support**: OpenAI GPT-4, Google Gemini, Anthropic Claude
- **5 Content Pillars**: Project breakdowns, debugging stories, how-tos, reflections, hot takes
- **Voice Learning**: AI learns your writing style
- **Smart Scheduling**: Posts at optimal times

### Job Application Automation
- **Intelligent Job Search**: Finds relevant positions on LinkedIn
- **AI Relevance Scoring**: Ranks jobs by fit
- **Easy Apply Bot**: Automates application submission
- **Question Answering**: AI fills out application forms
- **Resume Customization**: Tailors resume per job
- **Application Tracking**: Monitors responses and interviews

### Safety & Stealth
- **Anti-Detection Browser**: Undetected Chrome with human-like behavior
- **Rate Limiting**: Never exceeds LinkedIn's limits
- **Session Management**: Persistent login with cookies
- **Human Simulation**: Random delays, smooth scrolling, natural typing

## 📋 Prerequisites

- Python 3.11+
- Node.js 20+
- PostgreSQL 15+
- Redis 7+
- Google Chrome (latest)
- Docker & Docker Compose (optional)

## 🛠️ Installation

### Option 1: Docker (Recommended)

1. **Clone repository**
```bash
git clone <your-repo>
cd linkedin-automation-suite
```

2. **Create environment file**
```bash
cp .env.example .env
```

Edit `.env` and add your credentials:
```env
# LinkedIn
LINKEDIN_EMAIL=your_email@example.com
LINKEDIN_PASSWORD=your_password

# GitHub
GITHUB_TOKEN=your_github_token
GITHUB_USERNAME=your_username

# AI Providers (at least one required)
OPENAI_API_KEY=your_openai_key
GEMINI_API_KEY=your_gemini_key
ANTHROPIC_API_KEY=your_claude_key
```

3. **Start services**
```bash
docker-compose up -d
```

4. **Initialize database**
```bash
docker-compose exec postgres psql -U postgres -d linkedin_automation -f /docker-entrypoint-initdb.d/schema.sql
```

5. **Access application**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Option 2: Manual Setup

#### Backend

1. **Create virtual environment**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Setup database**
```bash
# Start PostgreSQL and Redis (or use cloud services)
psql -U postgres -d linkedin_automation -f ../database/schema.sql
```

4. **Run backend**
```bash
python -m uvicorn api.main:app --reload
```

#### Frontend

1. **Install dependencies**
```bash
cd frontend
npm install
```

2. **Run frontend**
```bash
npm run dev
```

## 🎯 Quick Start

### 1. First Time Setup

**Login to LinkedIn:**
- The first time you use any automation feature, a Chrome browser will open
- Log in to LinkedIn manually
- Complete 2FA if required
- The session will be saved for future use

**Configure Content Pillars:**
- Go to Settings > Content Pillars
- Review and customize the 5 default pillars
- Add example posts in your voice

### 2. Content Automation

**Monitor GitHub Activity:**
```bash
# API endpoint
POST http://localhost:8000/api/content/github-activity
{
  "github_username": "your_username",
  "days": 7
}
```

**Generate Post:**
```bash
POST http://localhost:8000/api/content/generate-post
{
  "source_data": {
    "type": "commit",
    "message": "Fixed async bug in data pipeline",
    "repo": "my-project"
  },
  "pillar": "debugging_story"
}
```

**Review & Post:**
- Visit http://localhost:3000/content/queue
- Review AI-generated posts
- Select hook, edit if needed
- Approve to schedule

### 3. Job Application Automation

**Search Jobs:**
```bash
POST http://localhost:8000/api/jobs/search
{
  "user_id": "your_user_id",
  "keywords": "Full Stack Engineer",
  "location": "United States",
  "max_results": 30
}
```

**Apply to Job:**
```bash
POST http://localhost:8000/api/jobs/apply
{
  "user_id": "your_user_id",
  "job_url": "https://linkedin.com/jobs/view/123456",
  "user_info": {
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "555-0100",
    "years_experience": 5
  },
  "resume_path": "/path/to/resume.pdf"
}
```

**Track Applications:**
- Visit http://localhost:3000/jobs/applications
- Monitor responses
- Schedule interviews

## 📊 Usage Examples

### Generate Content from GitHub

```python
from backend.modules.content_engine.sources.github_monitor import GitHubMonitor
from backend.modules.content_engine.generators.post_generator import PostGenerator

# Monitor GitHub
monitor = GitHubMonitor(github_token="...", username="...")
activities = await monitor.get_recent_activities(days=7)

# Generate post
generator = PostGenerator()
for activity in activities:
    if activity['content_potential'] == 'high':
        post = await generator.generate_post(
            source_data=activity,
            pillar='project_breakdown'
        )
        print(post)
```

### Automate Job Applications

```python
from backend.modules.job_applier.search.job_finder import JobFinder
from backend.modules.job_applier.application.easy_apply import EasyApplyBot

# Search jobs
finder = JobFinder(user_id="user_123")
jobs = await finder.search_jobs(
    keywords="React Developer",
    location="Remote",
    max_results=50
)

# Apply to relevant jobs
for job in jobs:
    if job.get('relevance_score', 0) > 0.7:
        # Apply
        result = await bot.apply(job['job_url'])
        if result['success']:
            print(f"✅ Applied to {job['title']}")
```

## ⚙️ Configuration

### Content Pillars

Edit `backend/config/content/pillars.yaml`:

```yaml
project_breakdown:
  tone: "technical but accessible"
  structure: "problem → approach → result → learning"
  example_posts:
    - "Built a rate limiter that handles 10k requests/sec..."

debugging_story:
  tone: "frustrated → curious → triumphant"
  structure: "bug symptom → investigation → aha moment"
  example_posts:
    - "Spent 3 hours on this bug. The fix was one line..."
```

### Job Search Preferences

Edit `backend/config/jobs/search_params.yaml`:

```yaml
keywords:
  - "Full Stack Engineer"
  - "React Developer"
  - "Python Developer"

locations:
  - "United States"
  - "Remote"

blacklist:
  - "Crossover"
  - "Turing"

filters:
  experience_level: ["entry", "mid", "senior"]
  job_type: ["full-time"]
  easy_apply_only: true
```

### Rate Limits

Modify `backend/core/config.py`:

```python
# LinkedIn Rate Limits
POSTS_PER_DAY = 5
POSTS_PER_HOUR = 1
MIN_POST_INTERVAL_MINUTES = 120

APPLICATIONS_PER_DAY = 30
APPLICATIONS_PER_HOUR = 5
MIN_APPLICATION_INTERVAL_SECONDS = 180
```

## 🛡️ Safety & Best Practices

### LinkedIn Terms of Service

⚠️ **Important:** This tool automates LinkedIn interactions which may violate their Terms of Service. Use at your own risk.

**Recommendations:**
- Start with conservative rate limits
- Always review AI-generated content before posting
- Don't auto-post without human approval
- Use the tool responsibly
- Take breaks between automation sessions

### Anti-Detection

The system includes multiple anti-detection measures:
- Undetected Chrome driver
- Human-like behavior simulation
- Random delays and timing
- Session persistence
- Real Chrome profile usage

**Best practices:**
- Don't run 24/7
- Use realistic application volumes (20-30/day max)
- Post 3-5 times per week max
- Manually interact with LinkedIn occasionally
- Monitor for warning emails from LinkedIn

## 📈 Analytics

View analytics at http://localhost:3000/analytics

**Content Metrics:**
- Posts per week
- Engagement rate (likes, comments, shares)
- Profile views spike
- Best performing content pillars
- Optimal posting times

**Job Application Metrics:**
- Applications per week
- Response rate
- Interview conversion rate
- Companies most responsive
- Skill gaps identified

## 🔧 Troubleshooting

### LinkedIn Login Issues

**Problem:** Can't log in / cookies expire
**Solution:**
```bash
# Clear saved session
rm -rf sessions/your_user_id/

# Login again manually when browser opens
```

### Chrome Driver Issues

**Problem:** Chrome driver version mismatch
**Solution:**
```bash
# undetected-chromedriver auto-downloads
# If issues persist:
pip uninstall undetected-chromedriver
pip install undetected-chromedriver --upgrade
```

### AI Generation Errors

**Problem:** API key errors
**Solution:**
- Verify API keys in `.env`
- Check API quotas/credits
- System will fallback to alternative provider automatically

### Database Connection

**Problem:** Can't connect to PostgreSQL
**Solution:**
```bash
# Check if PostgreSQL is running
docker-compose ps

# Restart services
docker-compose restart postgres
```

## 📚 API Documentation

Full API documentation available at: http://localhost:8000/docs

### Key Endpoints

**Content Engine:**
- `POST /api/content/github-activity` - Get GitHub activities
- `POST /api/content/generate-post` - Generate LinkedIn post
- `POST /api/content/post-to-linkedin` - Publish post

**Job Applier:**
- `POST /api/jobs/search` - Search for jobs
- `POST /api/jobs/apply` - Apply to job
- `GET /api/jobs/applications` - List applications

**Analytics:**
- `GET /api/analytics/summary` - Get overview
- `GET /api/analytics/content` - Content metrics
- `GET /api/analytics/jobs` - Job metrics

## 🤝 Contributing

This is a personal automation tool. Feel free to fork and customize for your needs.

## ⚖️ License

MIT License - Use at your own risk

## ⚠️ Disclaimer

This tool is provided "as-is" without any warranties. Automating LinkedIn may violate their Terms of Service. The authors are not responsible for any account restrictions or bans resulting from use of this software.

Use responsibly and at your own risk.

## 🙋 Support

For issues or questions:
- Check existing GitHub issues
- Review troubleshooting section
- Open a new issue with details

## 🗺️ Roadmap

- [ ] Voice note transcription (Whisper)
- [ ] Notion integration
- [ ] Carousel PDF generation
- [ ] Advanced analytics dashboard
- [ ] Multi-user support
- [ ] Resume builder
- [ ] Interview preparation assistant
- [ ] Salary negotiation insights

---

**Built with:** Python FastAPI, Next.js, PostgreSQL, Redis, Selenium, OpenAI, Google Gemini, Anthropic Claude

**Status:** Production-ready with active development
