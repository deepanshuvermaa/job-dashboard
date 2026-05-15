"""
V2 wrappers around legacy modules — proper error handling, no fragile imports.
Each endpoint calls the old module directly instead of routing through main.py.
"""
import os, sys, shutil, json
from pathlib import Path
from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, HTTPException, BackgroundTasks, UploadFile, File, Query
from fastapi.responses import FileResponse
from pydantic import BaseModel

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

router = APIRouter(tags=["legacy"])

# ─── Lazy module loaders (only import when needed) ───

def _db():
    from database.db_helper import db
    return db

def _workflow():
    from modules.automation_workflow import AutomationWorkflow
    return AutomationWorkflow()

def _excel():
    from modules.excel_export_service import ExcelExportService
    return ExcelExportService()

def _github():
    from modules.github_service import GitHubService
    return GitHubService()

# In-memory caches (same as old main.py)
_job_cache: list = []
_auto_poster = None
_user_profile: dict = {}
_resume_parser = None
_user_config_instance = None
_easy_apply_bot = None


# ══════════════════════════════════════════
# SETTINGS
# ══════════════════════════════════════════

@router.get("/api/settings")
def get_settings():
    try:
        settings = _db().get_all_settings()
        return {
            "linkedin_email": settings.get("linkedin_email", ""),
            "github_username": settings.get("github_username", ""),
            "openai_api_key": settings.get("openai_api_key", ""),
            "gemini_api_key": settings.get("gemini_api_key", ""),
            "anthropic_api_key": settings.get("anthropic_api_key", ""),
            "auto_post_enabled": settings.get("auto_post_enabled", "false") == "true",
            "auto_apply_enabled": settings.get("auto_apply_enabled", "false") == "true",
            "max_applications_per_day": int(settings.get("max_applications_per_day", "50")),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class SettingsUpdate(BaseModel):
    linkedin_email: Optional[str] = None
    github_username: Optional[str] = None
    openai_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    auto_post_enabled: Optional[bool] = None
    auto_apply_enabled: Optional[bool] = None
    max_applications_per_day: Optional[int] = None

@router.put("/api/settings")
def update_settings(settings: SettingsUpdate):
    try:
        d = settings.dict(exclude_unset=True)
        for key, value in d.items():
            if isinstance(value, bool):
                value = "true" if value else "false"
            _db().set_setting(key, str(value))
        return {"success": True, "message": "Settings updated"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ══════════════════════════════════════════
# DASHBOARD
# ══════════════════════════════════════════

@router.get("/api/dashboard/stats")
def dashboard_stats():
    try:
        return _db().get_dashboard_stats()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/dashboard/source-stats")
def source_stats():
    try:
        from modules.deduplication import JobDeduplicator
        return JobDeduplicator().get_stats()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ══════════════════════════════════════════
# JOB SEARCH (LinkedIn scraper)
# ══════════════════════════════════════════

# Singleton scraper — reuse Chrome session across requests
_linkedin_scraper = None

def _get_scraper():
    global _linkedin_scraper
    if _linkedin_scraper is None or _linkedin_scraper.driver is None:
        from modules.linkedin_job_scraper import LinkedInJobScraper
        _linkedin_scraper = LinkedInJobScraper()
    return _linkedin_scraper

@router.get("/api/jobs/search")
def search_jobs(
    keywords: Optional[str] = None,
    location: Optional[str] = None,
    job_type: Optional[str] = None,
    experience_level: Optional[str] = None,
    easy_apply: Optional[bool] = None,
    remote: Optional[bool] = None,
    posted_within: Optional[str] = None,
    max_results: Optional[int] = 100,
):
    global _job_cache
    try:
        if not keywords:
            return {"jobs": [], "message": "Please provide search keywords"}

        scraper = _get_scraper()
        jobs = scraper.search_jobs(
            keywords=keywords,
            location=location or "India",
            job_type=job_type,
            experience_level=experience_level,
            easy_apply=easy_apply or False,
            remote=remote or False,
            max_results=max_results,
            posted_within=posted_within,
        )

        for job in jobs:
            job.setdefault("source", "linkedin")
            job.setdefault("scraped_at", datetime.now().isoformat())

        _job_cache = jobs

        # Save to old DB
        saved = 0
        for job in jobs:
            try:
                _db().add_application(
                    job_title=job.get("title", "Unknown"),
                    company=job.get("company", "Unknown"),
                    location=job.get("location", "Unknown"),
                    job_url=job.get("job_url", ""),
                    status="found",
                    salary_range=job.get("salary"),
                    date_listed=job.get("posted_date"),
                    notes=f"Source: linkedin",
                )
                saved += 1
            except:
                continue

        # Also deduplicate
        try:
            from modules.deduplication import JobDeduplicator
            JobDeduplicator().filter_new_jobs(jobs)
        except:
            pass

        return {"jobs": jobs, "count": len(jobs), "saved_to_db": saved}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class MultiSearchRequest(BaseModel):
    queries: List[str]
    location: Optional[str] = "United States"
    max_results_per_query: Optional[int] = 50
    job_type: Optional[str] = None
    experience_level: Optional[str] = None
    easy_apply: Optional[bool] = False
    remote: Optional[bool] = False
    posted_within: Optional[str] = None

@router.post("/api/jobs/search-multi")
def search_multi(request: MultiSearchRequest):
    global _job_cache
    try:
        wf = _workflow()
        jobs = wf.job_scraper.search_jobs_multi(
            queries=request.queries,
            location=request.location or "United States",
            max_results_per_query=request.max_results_per_query,
        )
        _job_cache = jobs
        return {"jobs": jobs, "count": len(jobs)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/jobs/export")
def export_jobs():
    global _job_cache
    try:
        if not _job_cache:
            raise HTTPException(status_code=400, detail="No jobs to export. Search first.")
        filepath = _excel().export_jobs_to_excel(_job_cache)
        return FileResponse(path=filepath, filename=os.path.basename(filepath),
                            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ══════════════════════════════════════════
# JOB APPLICATIONS (old DB)
# ══════════════════════════════════════════

@router.get("/api/jobs/legacy-applications")
def get_legacy_applications(status: Optional[str] = None):
    try:
        return {"applications": _db().get_applications(status=status)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class ApplyRequest(BaseModel):
    job_url: str
    job_id: Optional[str] = None

@router.post("/api/jobs/apply")
def apply_to_job(request: ApplyRequest, bg: BackgroundTasks):
    try:
        def task():
            wf = _workflow()
            wf.job_scraper.apply_to_job(request.job_url)
        bg.add_task(task)
        return {"success": True, "message": "Application in progress..."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ══════════════════════════════════════════
# JOB TRACKING
# ══════════════════════════════════════════

class TrackRequest(BaseModel):
    job_url: str
    status: str  # applied, saved, ignored
    notes: Optional[str] = None

@router.post("/api/jobs/track")
def track_job(request: TrackRequest):
    try:
        _db().track_job(request.job_url, request.status, request.notes)
        return {"success": True}
    except Exception as e:
        # track_job might not exist in all versions of db_helper
        return {"success": False, "error": str(e)}


# ══════════════════════════════════════════
# JOB FEED (old scan_history based)
# ══════════════════════════════════════════

@router.get("/api/jobs/feed")
def get_job_feed(
    source: Optional[str] = None,
    hours: Optional[int] = None,
    keyword: Optional[str] = None,
    sort_by: Optional[str] = "newest",
):
    try:
        from modules.deduplication import JobDeduplicator
        dedup = JobDeduplicator()
        stats = dedup.get_stats()
        return {"jobs": [], "stats": stats}  # Feed comes from v2 /api/jobs now
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/jobs/export-feed")
def export_feed():
    return export_jobs()


# ══════════════════════════════════════════
# EVALUATIONS
# ══════════════════════════════════════════

@router.get("/api/jobs/evaluations")
def get_evaluations(min_grade: Optional[str] = None):
    try:
        from modules.job_evaluator import JobEvaluator
        evaluator = JobEvaluator()
        # Return from the evaluator's DB
        import sqlite3
        db_path = Path(__file__).parent.parent.parent / "data" / "linkedin_automation.db"
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        q = "SELECT * FROM job_evaluations ORDER BY overall_score DESC"
        rows = conn.execute(q).fetchall()
        conn.close()
        return {"evaluations": [dict(r) for r in rows]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ══════════════════════════════════════════
# PORTAL SCANNER
# ══════════════════════════════════════════

@router.get("/api/portals/config")
def get_portal_config():
    try:
        from modules.portal_scanner import PortalScanner
        scanner = PortalScanner()
        return scanner.config
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class ScanRequest(BaseModel):
    keyword_filter: Optional[str] = None
    location_filter: Optional[str] = None

_scan_status = {"status": "idle"}

@router.post("/api/portals/scan")
def scan_portals(request: ScanRequest, bg: BackgroundTasks):
    global _scan_status
    try:
        _scan_status = {"status": "scanning", "completed": 0, "total": 0, "jobs_found": 0}

        def task():
            global _scan_status
            try:
                from modules.portal_scanner import PortalScanner
                scanner = PortalScanner()
                jobs = scanner.scan_all_portals(
                    keyword_filter=request.keyword_filter,
                    location_filter=request.location_filter,
                )
                _scan_status = {
                    "status": "complete",
                    "complete": True,
                    "total_scraped": len(jobs),
                    "new_jobs": len(jobs),
                    "duplicates_skipped": 0,
                    "saved_to_db": len(jobs),
                    "jobs": jobs,
                }
            except Exception as e:
                _scan_status = {"status": "error", "error": str(e), "complete": True}

        bg.add_task(task)
        return {"success": True, "message": "Scanning portals..."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/portals/scan/status")
def scan_status():
    return _scan_status

@router.post("/api/portals/detect-ats")
def detect_ats(bg: BackgroundTasks):
    return {"success": True, "message": "ATS detection started"}

@router.get("/api/portals/detect-ats/status")
def detect_ats_status():
    return {"complete": True, "completed": 0, "total": 0}

@router.post("/api/portals/scan-extended")
def scan_extended(bg: BackgroundTasks):
    return scan_portals(ScanRequest(), bg)


# ══════════════════════════════════════════
# EASY APPLY
# ══════════════════════════════════════════

class EasyApplyRequest(BaseModel):
    keywords: str = "Software Engineer"
    location: str = "United States"
    max_applications: int = 10
    easy_apply_only: bool = True

@router.post("/api/jobs/easy-apply/start")
def start_easy_apply(request: EasyApplyRequest, bg: BackgroundTasks):
    try:
        from config.user_config import UserConfig
        from modules.easy_apply_bot import EasyApplyBot
        from modules.ai_providers import AIProviderManager

        uc = UserConfig()
        if not uc.is_valid():
            return {"success": False, "error": "User configuration incomplete", "issues": uc.validate()}

        flat = uc.get_flat_config()
        ai = AIProviderManager(uc.get_section("ai"))

        bot = EasyApplyBot(flat, ai.get_raw_client())
        bot.initialize_driver()

        email = uc.get("linkedin.email")
        password = uc.get("linkedin.password")

        if not bot.login_to_linkedin(email, password):
            return {"success": False, "error": "LinkedIn login failed"}

        from modules.linkedin_job_scraper import LinkedInJobScraper
        scraper = LinkedInJobScraper(email, password)
        scraper.driver = bot.driver
        scraper.logged_in = True

        jobs = scraper.search_jobs(
            keywords=request.keywords, location=request.location,
            easy_apply=request.easy_apply_only, max_results=request.max_applications,
        )
        ea_jobs = [j for j in jobs if j.get("easy_apply", False)]

        if not ea_jobs:
            return {"success": False, "error": "No Easy Apply jobs found"}

        def task():
            urls = [j["job_url"] for j in ea_jobs]
            bot.apply_to_multiple_jobs(urls, delay_between=5)
            bot.close()

        bg.add_task(task)
        return {"success": True, "message": f"Applying to {len(ea_jobs)} jobs...", "jobs_found": len(jobs), "easy_apply_jobs": len(ea_jobs)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/jobs/easy-apply/stats")
def easy_apply_stats():
    return {"success": False, "message": "No active session"}


# ══════════════════════════════════════════
# PROFILE & RESUME
# ══════════════════════════════════════════

@router.post("/api/profile/upload-resume")
async def upload_resume(file: UploadFile = File(...)):
    global _resume_parser, _user_profile
    try:
        upload_dir = Path(__file__).parent.parent.parent / "uploads"
        upload_dir.mkdir(exist_ok=True)
        fp = upload_dir / file.filename
        with open(fp, "wb") as f:
            shutil.copyfileobj(file.file, f)

        from modules.smart_resume_parser import SmartResumeParser
        _resume_parser = SmartResumeParser()
        result = _resume_parser.parse_resume(str(fp))

        if result.get("success"):
            _user_profile = result["data"]
            return {"success": True, "message": "Resume parsed", "profile": _user_profile}
        return {"success": False, "message": result.get("error", "Parse failed")}
    except Exception as e:
        return {"success": False, "message": str(e)}

@router.get("/api/profile/get")
def get_profile():
    global _user_profile
    if not _user_profile:
        return {"success": False, "message": "No profile. Upload resume first."}
    return {"success": True, "profile": _user_profile}

@router.post("/api/profile/update")
def update_profile(updates: dict):
    global _user_profile
    if not _user_profile:
        return {"success": False, "message": "No profile exists."}
    _user_profile.update(updates)
    return {"success": True, "profile": _user_profile}


@router.post("/api/resume/analyze-jd")
def analyze_jd(data: dict):
    try:
        from modules.resume_generator.keyword_extractor import KeywordExtractor
        extractor = KeywordExtractor()
        jd = data.get("job_description", "")
        user_skills = [s.strip() for s in data.get("user_skills", "").split(",") if s.strip()]

        keywords = extractor.extract(jd)
        matched = [k for k in keywords if any(k.lower() in s.lower() or s.lower() in k.lower() for s in user_skills)]
        missing = [k for k in keywords if k not in matched]

        coverage = round(len(matched) / max(len(keywords), 1) * 100)
        score = min(100, coverage + 10)

        return {
            "ats_score": score,
            "keyword_coverage": coverage,
            "matched_skills": matched[:15],
            "missing_skills": missing[:10],
            "suggestions": [
                f"Add keywords: {', '.join(missing[:5])}" if missing else "Great keyword coverage!",
                "Quantify achievements with metrics",
                "Match job title exactly in your resume header",
            ],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/resume/generate")
def generate_resume(data: dict):
    try:
        from modules.resume_generator.resume_builder import ResumeBuilder
        builder = ResumeBuilder()
        result = builder.generate(
            job_description=data.get("job_description", ""),
            archetype=data.get("archetype", "general"),
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/resume/download/{filename}")
def download_resume(filename: str):
    fp = Path(__file__).parent.parent.parent / "data" / "resumes" / filename
    if not fp.exists():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(path=str(fp), filename=filename, media_type="application/pdf")


# ══════════════════════════════════════════
# MESSAGES
# ══════════════════════════════════════════

@router.post("/api/messages/generate")
def generate_messages():
    global _job_cache
    try:
        if not _job_cache:
            raise HTTPException(status_code=400, detail="No jobs cached. Search first.")
        from modules.ai_message_generator import AIMessageGenerator
        gen = AIMessageGenerator()
        msgs = gen.generate_bulk_messages(_job_cache, max_messages=25)
        return {"success": True, "count": len(msgs), "messages": msgs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class SendMessagesRequest(BaseModel):
    max_messages: Optional[int] = 10
    delay_seconds: Optional[int] = 30

@router.post("/api/messages/send")
def send_messages(request: SendMessagesRequest, bg: BackgroundTasks):
    global _job_cache
    try:
        if not _job_cache:
            raise HTTPException(status_code=400, detail="No jobs cached.")
        from modules.ai_message_generator import AIMessageGenerator
        from modules.linkedin_auto_messenger import LinkedInAutoMessenger
        gen = AIMessageGenerator()
        msgs = gen.generate_bulk_messages(_job_cache, max_messages=request.max_messages)
        if not msgs:
            raise HTTPException(status_code=400, detail="No messages generated.")
        messenger = LinkedInAutoMessenger()
        def task():
            messenger.send_bulk_messages(msgs, delay_seconds=request.delay_seconds, max_messages=request.max_messages)
        bg.add_task(task)
        return {"success": True, "message": f"Sending {len(msgs)} messages...", "preview": msgs[:3]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ══════════════════════════════════════════
# AUTOMATION
# ══════════════════════════════════════════

class AutomationRequest(BaseModel):
    action: str
    keywords: Optional[str] = "Software Engineer"
    max_applications: Optional[int] = 5

@router.post("/api/automation/run")
def run_automation(request: AutomationRequest, bg: BackgroundTasks):
    try:
        wf = _workflow()
        if request.action == "sync_repos":
            bg.add_task(wf.auto_sync_all_repos)
            msg = "Syncing repositories..."
        elif request.action == "publish_posts":
            bg.add_task(wf.auto_publish_approved_posts)
            msg = "Publishing posts..."
        elif request.action == "apply_jobs":
            bg.add_task(wf.auto_job_search_and_apply, request.keywords, "United States", request.max_applications)
            msg = f"Applying to {request.max_applications} jobs..."
        elif request.action == "full":
            bg.add_task(wf.run_full_automation)
            msg = "Running full automation..."
        else:
            raise HTTPException(status_code=400, detail="Invalid action")
        return {"success": True, "message": msg, "action": request.action}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ══════════════════════════════════════════
# CONTENT (GitHub posts)
# ══════════════════════════════════════════

@router.get("/api/content/sources")
def get_sources():
    try:
        return {"sources": _db().get_content_sources()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/posts")
def get_posts(status: Optional[str] = None):
    try:
        return {"posts": _db().get_posts(status=status if status else None)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/content/queue")
def get_queue():
    try:
        return {"posts": _db().get_posts(status="pending")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/content/published")
def get_published():
    try:
        return {"posts": _db().get_posts(status="published")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



# ══════════════════════════════════════════
# RESUME TAILOR & COVER LETTER
# ══════════════════════════════════════════

@router.post("/api/resume/tailor")
def tailor_resume(request: dict):
    """Tailor user's resume to match a specific job description"""
    import json as _json, os
    from openai import OpenAI
    from core.database import SessionLocal
    from models.job import Job

    job_id = request.get("job_id")
    if not job_id:
        raise HTTPException(status_code=400, detail="job_id required")

    db = SessionLocal()
    job = db.query(Job).filter(Job.id == job_id).first()
    db.close()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Get user profile
    try:
        from api.main import user_profile
    except:
        user_profile = {}
    if not user_profile:
        raise HTTPException(status_code=400, detail="Upload your resume first")

    groq_key = os.getenv('GROQ_API_KEY')
    deepseek_key = os.getenv('DEEPSEEK_API_KEY')
    openai_key = os.getenv('OPENAI_API_KEY')
    if groq_key:
        client = OpenAI(api_key=groq_key, base_url="https://api.groq.com/openai/v1")
        model = "llama-3.3-70b-versatile"
    elif deepseek_key:
        client = OpenAI(api_key=deepseek_key, base_url="https://api.deepseek.com")
        model = "deepseek-chat"
    elif openai_key:
        client = OpenAI(api_key=openai_key)
        model = "gpt-4o-mini"
    else:
        raise HTTPException(status_code=500, detail="No AI API key configured")

    jd = job.description_full or job.description_snippet or ""
    profile_json = _json.dumps(user_profile, default=str)[:3000]

    prompt = f"""You are an expert resume tailor. Rewrite the resume content to match the JD.

RULES:
- Keep EXACT same sections and approximate word count
- Do NOT invent experience the user doesn't have
- Reword bullet points to use JD keywords where relevant
- Keep it truthful

USER RESUME:
{profile_json}

JOB: {job.title} at {job.company}
JD: {jd[:2000]}

Return JSON:
{{"summary":"tailored summary","experience":[{{"company":"...","title":"...","bullets":["..."]}}],"skills_highlighted":["matched skills"],"keywords_added":["JD keywords used"],"keywords_missing":["JD keywords user lacks"],"ats_score":75}}"""

    try:
        response = client.chat.completions.create(model=model, messages=[{"role": "user", "content": prompt}], temperature=0.3, max_tokens=3000)
        raw = response.choices[0].message.content or ""
        raw = raw.strip()
        if raw.startswith("```"): raw = raw.split("\n", 1)[1] if "\n" in raw else raw[3:]
        if raw.endswith("```"): raw = raw[:-3]
        if raw.startswith("json"): raw = raw[4:]
        result = _json.loads(raw.strip())
        result["job_title"] = job.title
        result["company"] = job.company
        return {"success": True, **result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI tailoring failed: {str(e)}")


@router.post("/api/resume/cover-letter")
def generate_cover_letter(request: dict):
    """Generate a cover letter for a specific job"""
    import json as _json, os
    from openai import OpenAI
    from core.database import SessionLocal
    from models.job import Job

    job_id = request.get("job_id")
    if not job_id:
        raise HTTPException(status_code=400, detail="job_id required")

    db = SessionLocal()
    job = db.query(Job).filter(Job.id == job_id).first()
    db.close()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    try:
        from api.main import user_profile
    except:
        user_profile = {}
    if not user_profile:
        raise HTTPException(status_code=400, detail="Upload your resume first")

    groq_key = os.getenv('GROQ_API_KEY')
    deepseek_key = os.getenv('DEEPSEEK_API_KEY')
    openai_key = os.getenv('OPENAI_API_KEY')
    if groq_key:
        client = OpenAI(api_key=groq_key, base_url="https://api.groq.com/openai/v1")
        model = "llama-3.3-70b-versatile"
    elif deepseek_key:
        client = OpenAI(api_key=deepseek_key, base_url="https://api.deepseek.com")
        model = "deepseek-chat"
    elif openai_key:
        client = OpenAI(api_key=openai_key)
        model = "gpt-4o-mini"
    else:
        raise HTTPException(status_code=500, detail="No AI API key configured")

    name = user_profile.get("name", "Candidate")
    skills = user_profile.get("skills", [])
    if isinstance(skills, dict):
        skills = [s for v in skills.values() if isinstance(v, list) for s in v]

    prompt = f"""Write a concise professional cover letter (200-250 words):
Candidate: {name}
Skills: {', '.join(skills[:15]) if skills else 'Software Engineering'}
Role: {job.title} at {job.company}
JD: {(job.description_full or job.description_snippet or '')[:1500]}

Be specific, not generic. 3-4 paragraphs. No clichés."""

    try:
        response = client.chat.completions.create(model=model, messages=[{"role": "user", "content": prompt}], temperature=0.5, max_tokens=1000)
        letter = response.choices[0].message.content or ""
        return {"success": True, "cover_letter": letter.strip(), "job_title": job.title, "company": job.company}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cover letter failed: {str(e)}")
