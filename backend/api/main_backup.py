"""FastAPI main application"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

app = FastAPI(title="LinkedIn Automation Suite", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== Models ====================

class GitHubActivityRequest(BaseModel):
    github_username: str
    days: int = 7

class GeneratePostRequest(BaseModel):
    source_data: dict
    pillar: str = "learning_reflection"

class PostToLinkedInRequest(BaseModel):
    user_id: str
    content: str
    image_path: Optional[str] = None

class JobSearchRequest(BaseModel):
    user_id: str
    keywords: str
    location: str = "United States"
    max_results: int = 30

class ApplyToJobRequest(BaseModel):
    user_id: str
    job_url: str
    user_info: dict
    resume_path: Optional[str] = None

# ==================== Health ====================

@app.get("/")
async def root():
    return {
        "status": "online",
        "version": "1.0.0",
        "services": ["content_engine", "job_applier"],
        "message": "LinkedIn Automation Suite API is running!"
    }

@app.get("/health")
async def health():
    return {"status": "healthy", "backend": "running"}

# ==================== Content Engine ====================

@app.post("/api/content/github-activity")
async def get_github_activity(request: GitHubActivityRequest):
    """Get recent GitHub activities"""
    try:
        from modules.content_engine.sources.github_monitor import GitHubMonitor
        from core.config import settings
        
        monitor = GitHubMonitor(
            github_token=settings.GITHUB_TOKEN,
            username=request.github_username
        )
        activities = await monitor.get_recent_activities(days=request.days)

        return {
            "success": True,
            "activities": activities,
            "count": len(activities)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/content/generate-post")
async def generate_post(request: GeneratePostRequest):
    """Generate LinkedIn post from source"""
    try:
        from modules.content_engine.generators.post_generator import PostGenerator
        
        generator = PostGenerator()
        post = await generator.generate_post(
            source_data=request.source_data,
            pillar=request.pillar
        )

        return {
            "success": True,
            "post": post
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/content/post-to-linkedin")
async def post_to_linkedin(request: PostToLinkedInRequest):
    """Post content to LinkedIn"""
    try:
        from modules.content_engine.scheduler.linkedin_poster import LinkedInPoster
        
        poster = LinkedInPoster(user_id=request.user_id)
        result = await poster.post(
            content=request.content,
            image_path=request.image_path
        )

        if not result['success']:
            raise HTTPException(status_code=500, detail=result['error'])

        return {
            "success": True,
            "result": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== Job Applier ====================

@app.post("/api/jobs/search")
async def search_jobs(request: JobSearchRequest):
    """Search for jobs on LinkedIn"""
    try:
        from modules.job_applier.search.job_finder import JobFinder
        
        finder = JobFinder(user_id=request.user_id)
        jobs = await finder.search_jobs(
            keywords=request.keywords,
            location=request.location,
            max_results=request.max_results
        )

        return {
            "success": True,
            "jobs": jobs,
            "count": len(jobs)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/jobs/apply")
async def apply_to_job(request: ApplyToJobRequest):
    """Apply to job via Easy Apply"""
    try:
        from modules.job_applier.application.easy_apply import EasyApplyBot
        from core.browser.stealth_browser import StealthBrowser
        
        # Create driver
        driver = StealthBrowser.create(headless=False, use_profile=True)

        # Apply
        bot = EasyApplyBot(driver, user_info=request.user_info)
        result = await bot.apply(
            job_url=request.job_url,
            resume_path=request.resume_path
        )

        driver.quit()

        if not result['success']:
            raise HTTPException(status_code=500, detail=result['error'])

        return {
            "success": True,
            "result": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== Analytics ====================

@app.get("/api/analytics/summary")
async def get_analytics_summary():
    """Get analytics summary"""
    return {
        "content": {
            "posts_this_week": 3,
            "avg_engagement": 5.2,
            "total_impressions": 12500
        },
        "jobs": {
            "applications_this_week": 25,
            "responses_received": 3,
            "interviews_scheduled": 1
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
