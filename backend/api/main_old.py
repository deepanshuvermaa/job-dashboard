"""FastAPI main application with database integration"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import sys
import os
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_helper import db

app = FastAPI(title="LinkedIn Automation Suite", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== Models ====================

class ContentSourceRequest(BaseModel):
    repo_url: str

class ContentSourceUpdate(BaseModel):
    is_active: Optional[bool] = None

class JobApplicationRequest(BaseModel):
    job_url: str
    job_id: Optional[str] = None

class PostUpdate(BaseModel):
    status: Optional[str] = None
    published_at: Optional[str] = None
    linkedin_url: Optional[str] = None

class SettingsUpdate(BaseModel):
    linkedin_email: Optional[str] = None
    github_username: Optional[str] = None
    openai_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    auto_post_enabled: Optional[bool] = None
    auto_apply_enabled: Optional[bool] = None
    max_applications_per_day: Optional[int] = None

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

# ==================== Dashboard ====================

@app.get("/api/dashboard/stats")
async def get_dashboard_stats():
    """Get dashboard statistics"""
    try:
        stats = db.get_dashboard_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== Settings ====================

@app.get("/api/settings")
async def get_settings():
    """Get all settings"""
    try:
        settings = db.get_all_settings()
        return {
            "linkedin_email": settings.get("linkedin_email", ""),
            "github_username": settings.get("github_username", ""),
            "openai_api_key": settings.get("openai_api_key", ""),
            "gemini_api_key": settings.get("gemini_api_key", ""),
            "anthropic_api_key": settings.get("anthropic_api_key", ""),
            "auto_post_enabled": settings.get("auto_post_enabled", "false") == "true",
            "auto_apply_enabled": settings.get("auto_apply_enabled", "false") == "true",
            "max_applications_per_day": int(settings.get("max_applications_per_day", "50"))
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/settings")
async def update_settings(settings: SettingsUpdate):
    """Update settings"""
    try:
        settings_dict = settings.dict(exclude_unset=True)
        for key, value in settings_dict.items():
            if isinstance(value, bool):
                value = "true" if value else "false"
            db.set_setting(key, str(value))
        return {"success": True, "message": "Settings updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== Content Sources ====================

@app.get("/api/content/sources")
async def get_content_sources():
    """Get all content sources"""
    try:
        sources = db.get_content_sources()
        return {"sources": sources}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/content/sources")
async def add_content_source(request: ContentSourceRequest):
    """Add new content source"""
    try:
        repo_url = request.repo_url.strip()
        if "github.com" in repo_url:
            parts = repo_url.rstrip('/').split('/')
            repo_name = f"{parts[-2]}/{parts[-1]}"
        else:
            repo_name = repo_url
            repo_url = f"https://github.com/{repo_url}"
        source_id = db.add_content_source(repo_name, repo_url)
        return {"success": True, "source_id": source_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/content/sources/{source_id}")
async def update_content_source(source_id: int, update: ContentSourceUpdate):
    """Update content source"""
    try:
        update_data = update.dict(exclude_unset=True)
        db.update_content_source(source_id, **update_data)
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/content/sources/{source_id}")
async def delete_content_source(source_id: int):
    """Delete content source"""
    try:
        db.delete_content_source(source_id)
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/content/sources/{source_id}/sync")
async def sync_content_source(source_id: int):
    """Sync content from source"""
    try:
        db.update_content_source(source_id, last_synced=datetime.now().isoformat())
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== Content Posts ====================

@app.get("/api/content/queue")
async def get_content_queue():
    """Get pending posts"""
    try:
        posts = db.get_posts(status='pending')
        return {"posts": posts}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/content/published")
async def get_published_posts():
    """Get published posts"""
    try:
        posts = db.get_posts(status='published')
        return {"posts": posts}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/content/posts/{post_id}")
async def update_post(post_id: int, update: PostUpdate):
    """Update post"""
    try:
        update_data = update.dict(exclude_unset=True)
        db.update_post(post_id, **update_data)
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== Job Search ====================

@app.get("/api/jobs/search")
async def search_jobs(
    keywords: Optional[str] = None,
    location: Optional[str] = None,
    job_type: Optional[str] = None,
    experience_level: Optional[str] = None,
    easy_apply: Optional[bool] = None,
    remote: Optional[bool] = None,
    posted_within: Optional[str] = None
):
    """Search for jobs"""
    try:
        return {"jobs": []}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== Job Applications ====================

@app.post("/api/jobs/apply")
async def apply_to_job(request: JobApplicationRequest):
    """Apply to job"""
    try:
        app_id = db.add_application(
            job_title="Software Engineer",
            company="Company Name",
            location="Remote",
            job_url=request.job_url
        )
        return {"success": True, "application_id": app_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/jobs/applications")
async def get_applications(status: Optional[str] = None):
    """Get applications"""
    try:
        applications = db.get_applications(status=status)
        return {"applications": applications}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
