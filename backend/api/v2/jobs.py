"""Jobs API — CRUD, filtering, pagination, stats."""
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, case, and_
from typing import Optional, List
from datetime import datetime, timezone

from core.database import get_db
from core.auth.dependencies import get_current_user
from models.user import User
from models.job import Job, JobEvaluation

router = APIRouter(prefix="/api/jobs", tags=["jobs"])

SCRAPER_EMAIL = "scraper@jobflow.io"

def _shared_owner_id(db, fallback_user_id: str) -> str:
    """Return the scraper account's user_id (shared job pool). Falls back to current user."""
    scraper = db.query(User).filter(User.email == SCRAPER_EMAIL).first()
    return scraper.id if scraper else fallback_user_id


class JobResponse(BaseModel):
    id: str
    title: str
    company: str
    company_logo_url: Optional[str] = None
    location: str
    job_url: str
    description_snippet: Optional[str] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    salary_currency: Optional[str] = "USD"
    salary_period: Optional[str] = "yearly"
    employment_type: Optional[str] = None
    experience_level: Optional[str] = None
    work_mode: Optional[str] = None
    skills_required: Optional[list] = []
    skills_matched: Optional[list] = []
    source: str
    category: Optional[str] = None
    status: str
    is_easy_apply: bool
    is_bookmarked: bool
    is_ignored: bool
    hr_name: Optional[str] = None
    hr_email: Optional[str] = None
    first_seen_at: Optional[str] = None
    last_seen_at: Optional[str] = None
    times_seen: int
    posted_date: Optional[str] = None
    evaluation: Optional[dict] = None

    class Config:
        from_attributes = True


class JobListResponse(BaseModel):
    jobs: List[JobResponse]
    total: int
    page: int
    per_page: int
    total_pages: int


class PatchJobRequest(BaseModel):
    is_bookmarked: Optional[bool] = None
    is_ignored: Optional[bool] = None
    status: Optional[str] = None


def _serialize_job(job: Job) -> dict:
    ev = None
    if job.evaluation:
        ev = {
            "overall_score": job.evaluation.overall_score,
            "grade": job.evaluation.grade,
            "gate_pass": job.evaluation.gate_pass,
            "role_match": job.evaluation.role_match,
            "skills_alignment": job.evaluation.skills_alignment,
            "seniority_fit": job.evaluation.seniority_fit,
            "compensation": job.evaluation.compensation,
            "interview_likelihood": job.evaluation.interview_likelihood,
            "growth_potential": job.evaluation.growth_potential,
            "company_reputation": job.evaluation.company_reputation,
            "location_fit": job.evaluation.location_fit,
            "tech_stack_match": job.evaluation.tech_stack_match,
            "culture_signals": job.evaluation.culture_signals,
            "reasoning": job.evaluation.reasoning,
        }
    return {
        "id": job.id,
        "title": job.title,
        "company": job.company,
        "company_logo_url": job.company_logo_url,
        "location": job.location or "Not specified",
        "job_url": job.job_url,
        "description_snippet": job.description_snippet,
        "salary_min": job.salary_min,
        "salary_max": job.salary_max,
        "salary_currency": job.salary_currency,
        "salary_period": job.salary_period,
        "employment_type": job.employment_type,
        "experience_level": job.experience_level,
        "work_mode": job.work_mode,
        "skills_required": job.skills_required or [],
        "skills_matched": job.skills_matched or [],
        "source": job.source,
        "category": job.category,
        "status": job.status,
        "is_easy_apply": job.is_easy_apply,
        "is_bookmarked": job.is_bookmarked,
        "is_ignored": job.is_ignored,
        "hr_name": job.hr_name,
        "hr_email": job.hr_email,
        "first_seen_at": job.first_seen_at.isoformat() if job.first_seen_at else None,
        "last_seen_at": job.last_seen_at.isoformat() if job.last_seen_at else None,
        "times_seen": job.times_seen or 1,
        "posted_date": job.posted_date.isoformat() if job.posted_date else None,
        "evaluation": ev,
    }


@router.get("", response_model=JobListResponse)
def list_jobs(
    page: int = Query(1, ge=1),
    per_page: int = Query(24, ge=1, le=100),
    status: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    source: Optional[str] = Query(None),
    work_mode: Optional[str] = Query(None),
    grade: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    bookmarked: Optional[bool] = Query(None),
    sort: str = Query("newest"),
    # New filters
    posted_after: Optional[str] = Query(None),  # 1d, 3d, 7d, 30d
    location: Optional[str] = Query(None),
    salary_min: Optional[int] = Query(None),
    experience_level: Optional[str] = Query(None),
    easy_apply: Optional[bool] = Query(None),
    company: Optional[str] = Query(None),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    from datetime import timedelta

    # Jobs are stored under the shared scraper account — visible to all logged-in users
    SCRAPER_EMAIL = "scraper@jobflow.io"
    scraper_user = db.query(User).filter(User.email == SCRAPER_EMAIL).first()
    # Fall back to current user if scraper account doesn't exist
    owner_id = scraper_user.id if scraper_user else user.id

    q = db.query(Job).options(joinedload(Job.evaluation)).filter(
        Job.user_id == owner_id,
        Job.is_ignored == False,
    )

    if status:
        q = q.filter(Job.status == status)
    else:
        q = q.filter(Job.status.in_(["active", "stale"]))

    if category:
        q = q.filter(Job.category == category)
    if source:
        q = q.filter(Job.source == source)
    if work_mode:
        q = q.filter(Job.work_mode == work_mode)
    if bookmarked:
        q = q.filter(Job.is_bookmarked == True)
    if search:
        pattern = f"%{search}%"
        q = q.filter(
            (Job.title.ilike(pattern)) | (Job.company.ilike(pattern))
        )
    if grade:
        q = q.join(Job.evaluation).filter(JobEvaluation.grade == grade.upper())

    # New filters
    if posted_after:
        days_map = {"1d": 1, "3d": 3, "7d": 7, "14d": 14, "30d": 30}
        days = days_map.get(posted_after, 7)
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        q = q.filter(Job.first_seen_at >= cutoff)
    if location:
        # Expand country-level searches to include major cities
        LOCATION_EXPANSIONS = {
            "india": ["india", "bangalore", "bengaluru", "mumbai", "hyderabad", "pune", "delhi", "gurgaon", "gurugram", "noida", "chennai", "kolkata", "ahmedabad", "jaipur", "kochi", "indore", "chandigarh", "remote, india"],
            "united states": ["united states", "usa", "us", "san francisco", "new york", "seattle", "austin", "boston", "chicago", "los angeles", "denver", "atlanta", "remote, us"],
            "united kingdom": ["united kingdom", "uk", "london", "manchester", "edinburgh", "remote, uk"],
        }
        cities = LOCATION_EXPANSIONS.get(location.lower(), [location])
        from sqlalchemy import or_
        q = q.filter(or_(*[Job.location.ilike(f"%{city}%") for city in cities]))
    if salary_min:
        q = q.filter(Job.salary_max >= salary_min)
    if experience_level:
        q = q.filter(Job.experience_level == experience_level)
    if easy_apply:
        q = q.filter(Job.is_easy_apply == True)
    if company:
        q = q.filter(Job.company.ilike(f"%{company}%"))

    total = q.count()

    if sort == "score":
        q = q.outerjoin(Job.evaluation).order_by(
            JobEvaluation.overall_score.desc().nullslast(),
            Job.first_seen_at.desc(),
        )
    elif sort == "company":
        q = q.order_by(Job.company.asc(), Job.first_seen_at.desc())
    else:
        q = q.order_by(Job.first_seen_at.desc())

    jobs = q.offset((page - 1) * per_page).limit(per_page).all()

    return {
        "jobs": [_serialize_job(j) for j in jobs],
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": max(1, -(-total // per_page)),
    }


@router.get("/stats")
def job_stats(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    owner_id = _shared_owner_id(db, user.id)
    base = db.query(Job).filter(Job.user_id == owner_id)

    total = base.count()
    active = base.filter(Job.status == "active").count()
    stale = base.filter(Job.status == "stale").count()
    bookmarked = base.filter(Job.is_bookmarked == True).count()
    applied = base.join(Job.applications).distinct().count()

    grades = (
        db.query(JobEvaluation.grade, func.count(JobEvaluation.id))
        .join(Job, Job.id == JobEvaluation.job_id)
        .filter(Job.user_id == owner_id, Job.status.in_(["active", "stale"]))
        .group_by(JobEvaluation.grade)
        .all()
    )
    sources = (
        base.filter(Job.status.in_(["active", "stale"]))
        .with_entities(Job.source, func.count(Job.id))
        .group_by(Job.source)
        .all()
    )
    categories = (
        base.filter(Job.status.in_(["active", "stale"]))
        .with_entities(Job.category, func.count(Job.id))
        .group_by(Job.category)
        .all()
    )
    return {
        "total": total, "active": active, "stale": stale,
        "bookmarked": bookmarked, "applied": applied,
        "grades": {g: c for g, c in grades if g},
        "sources": {s: c for s, c in sources if s},
        "categories": {c: n for c, n in categories if c},
    }


@router.get("/categories/list")
def list_categories(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    owner_id = _shared_owner_id(db, user.id)
    rows = (
        db.query(Job.category, func.count(Job.id))
        .filter(Job.user_id == owner_id, Job.status.in_(["active", "stale"]), Job.category.isnot(None))
        .group_by(Job.category)
        .order_by(func.count(Job.id).desc())
        .all()
    )
    return [{"name": c, "count": n} for c, n in rows]


# ── Ingest: bridge scraped jobs into the new table ──

class IngestRequest(BaseModel):
    jobs: list
    source: Optional[str] = "manual"


@router.get("/locations/list")
def list_locations(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    owner_id = _shared_owner_id(db, user.id)
    rows = (
        db.query(Job.location, func.count(Job.id))
        .filter(Job.user_id == owner_id, Job.status.in_(["active", "stale"]), Job.location.isnot(None))
        .group_by(Job.location)
        .order_by(func.count(Job.id).desc())
        .limit(50)
        .all()
    )
    return [{"name": loc, "count": n} for loc, n in rows if loc and loc != "Not specified"]


@router.post("/ingest")
def ingest_scraped_jobs(body: IngestRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Ingest raw scraped jobs into the shared job pool (scraper account)."""
    from modules.job_ingestor import ingest_jobs
    owner_id = _shared_owner_id(db, user.id)
    stats = ingest_jobs(db, owner_id, body.jobs, body.source)
    return stats


@router.post("/cleanup")
def run_cleanup(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    from modules.staleness_engine import run_cleanup
    owner_id = _shared_owner_id(db, user.id)
    return run_cleanup(db, owner_id)


# ── Applications (from new table) ──

from models.application import Application

@router.get("/applications")
def list_applications(
    status: Optional[str] = Query(None),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    q = (
        db.query(Application)
        .filter(Application.user_id == user.id)
        .order_by(Application.applied_at.desc())
    )
    if status:
        q = q.filter(Application.status == status)

    apps = q.limit(200).all()
    result = []
    for a in apps:
        job = db.query(Job).filter(Job.id == a.job_id).first()
        result.append({
            "id": a.id,
            "job_id": a.job_id,
            "job_title": job.title if job else "Unknown",
            "company": job.company if job else "Unknown",
            "location": job.location if job else "",
            "job_url": job.job_url if job else "",
            "status": a.status,
            "applied_at": a.applied_at.isoformat() if a.applied_at else None,
            "method": a.method,
            "response_date": a.response_date.isoformat() if a.response_date else None,
            "notes": a.notes,
        })
    return {"applications": result, "total": len(result)}


@router.get("/applications/stats")
def application_stats(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    total = db.query(Application).filter(Application.user_id == user.id).count()
    applied = db.query(Application).filter(Application.user_id == user.id, Application.status == "applied").count()
    interview = db.query(Application).filter(Application.user_id == user.id, Application.status == "interview").count()
    rejected = db.query(Application).filter(Application.user_id == user.id, Application.status == "rejected").count()
    return {
        "total": total,
        "applied": applied,
        "interview": interview,
        "rejected": rejected,
        "response_rate": round(((interview + rejected) / total * 100) if total > 0 else 0, 1),
    }


# ── Wildcard routes LAST to avoid capturing /stats, /applications, etc. ──

@router.get("/{job_id}")
def get_job(job_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    owner_id = _shared_owner_id(db, user.id)
    job = (
        db.query(Job)
        .options(joinedload(Job.evaluation))
        .filter(Job.id == job_id, Job.user_id == owner_id)
        .first()
    )
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    data = _serialize_job(job)
    data["description_full"] = job.description_full
    return data


@router.patch("/{job_id}")
def update_job(job_id: str, body: PatchJobRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    owner_id = _shared_owner_id(db, user.id)
    job = db.query(Job).filter(Job.id == job_id, Job.user_id == owner_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if body.is_bookmarked is not None:
        job.is_bookmarked = body.is_bookmarked
    if body.is_ignored is not None:
        job.is_ignored = body.is_ignored
    if body.status is not None:
        job.status = body.status
    db.flush()
    return {"ok": True}
