"""
Job Ingestor — Bridge between scrapers and the new jobs table.
Takes raw scraped job dicts (from any scraper) and upserts into the SQLAlchemy Job model.
"""
import re
from html import unescape
from datetime import datetime, timezone
from typing import List, Dict, Optional
from sqlalchemy.orm import Session

from models.job import Job, JobEvaluation, JobSource


def strip_html(text: str) -> str:
    """Remove HTML tags and decode entities from text."""
    if not text:
        return ""
    # Decode HTML entities (&lt; &gt; &amp; &quot; etc.)
    text = unescape(text)
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', ' ', text)
    # Collapse whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def normalize_key(company: str, title: str) -> str:
    c = re.sub(r'[^a-z0-9]', '', (company or '').lower())
    t = re.sub(r'[^a-z0-9]', '', (title or '').lower())
    return f"{c}|{t}"


def classify_category(title: str, description: str = "") -> str:
    """Auto-classify job into category based on title and description."""
    text = f"{title} {description}".lower()

    if any(k in text for k in ["machine learning", "ml engineer", "ai engineer", "deep learning", "nlp", "computer vision"]):
        return "ai_ml"
    if any(k in text for k in ["data engineer", "data scientist", "data analyst", "analytics"]):
        return "data"
    if any(k in text for k in ["devops", "sre", "site reliability", "platform engineer", "infrastructure", "security engineer"]):
        return "devops"
    if any(k in text for k in ["full stack", "fullstack", "full-stack"]):
        return "fullstack"
    if any(k in text for k in ["frontend", "front-end", "front end", "ui engineer", "react", "angular", "vue"]):
        return "frontend"
    if any(k in text for k in ["backend", "back-end", "back end", "server-side", "api engineer"]):
        return "backend"
    if any(k in text for k in ["product designer", "ux", "ui/ux", "design"]):
        return "design"
    if any(k in text for k in ["product manager", "program manager", "project manager"]):
        return "product"

    # Default: check description for backend/frontend signals
    if any(k in text for k in ["python", "go ", "golang", "java ", "rust", "postgresql", "microservices"]):
        return "backend"
    if any(k in text for k in ["react", "typescript", "css", "next.js", "tailwind"]):
        return "frontend"

    return "other"


def detect_work_mode(text: str) -> Optional[str]:
    text_lower = text.lower()
    if "remote" in text_lower:
        return "remote"
    if "hybrid" in text_lower:
        return "hybrid"
    if any(k in text_lower for k in ["onsite", "on-site", "in-office", "in office"]):
        return "onsite"
    return None


def detect_experience_level(text: str) -> Optional[str]:
    text_lower = text.lower()
    if any(k in text_lower for k in ["staff", "principal", "distinguished"]):
        return "lead"
    if any(k in text_lower for k in ["senior", "sr.", "sr "]):
        return "senior"
    if any(k in text_lower for k in ["junior", "jr.", "jr ", "entry", "associate", "intern"]):
        return "entry"
    if any(k in text_lower for k in ["lead", "director", "head of", "vp"]):
        return "lead"
    return "mid"


def parse_salary(salary_str: str) -> tuple:
    """Parse salary string into (min, max, currency, period)."""
    if not salary_str:
        return None, None, "USD", "yearly"

    # Remove commas and extra spaces
    s = salary_str.replace(",", "").strip()

    # Find all numbers
    numbers = re.findall(r'[\d]+(?:\.[\d]+)?', s.replace("k", "000").replace("K", "000"))
    if not numbers:
        return None, None, "USD", "yearly"

    nums = [int(float(n)) for n in numbers]

    # Detect period
    period = "yearly"
    if any(k in s.lower() for k in ["/hr", "hour", "/h"]):
        period = "hourly"
    elif any(k in s.lower() for k in ["/mo", "month", "/m"]):
        period = "monthly"

    # Handle k notation before it was expanded
    if "k" in salary_str.lower() or "K" in salary_str:
        nums = [n if n > 1000 else n * 1000 for n in nums]

    if len(nums) >= 2:
        return min(nums[0], nums[1]), max(nums[0], nums[1]), "USD", period
    elif len(nums) == 1:
        return nums[0], None, "USD", period

    return None, None, "USD", "yearly"


def ingest_jobs(db: Session, user_id: str, raw_jobs: List[Dict], source_name: str = "unknown") -> Dict:
    """
    Ingest a list of raw scraped jobs into the jobs table.
    Returns stats: {new, updated, skipped}
    """
    now = datetime.now(timezone.utc)
    stats = {"new": 0, "updated": 0, "skipped": 0, "errors": 0}

    for raw in raw_jobs:
        try:
            title = raw.get("title", "").strip()
            company = raw.get("company", "").strip()
            job_url = raw.get("job_url", "").strip()

            if not title or not company or not job_url:
                stats["skipped"] += 1
                continue

            nkey = normalize_key(company, title)

            # Check if job already exists for this user
            existing = (
                db.query(Job)
                .filter(Job.user_id == user_id, Job.normalized_key == nkey)
                .first()
            )

            if existing:
                # Update last_seen and bump times_seen
                existing.last_seen_at = now
                existing.times_seen = (existing.times_seen or 1) + 1
                if existing.status in ("stale", "expired"):
                    existing.status = "active"  # Revive

                # Add source if new
                src = raw.get("source", source_name)
                existing_sources = [s.source for s in existing.sources]
                if src not in existing_sources:
                    db.add(JobSource(job_id=existing.id, source=src, source_url=job_url))

                stats["updated"] += 1
                continue

            # Parse fields — strip HTML from descriptions
            location = raw.get("location", "Not specified")
            description = strip_html(raw.get("description_snippet", "") or raw.get("description", "") or "")
            full_desc = strip_html(raw.get("description_full", "") or raw.get("description", "") or description)
            sal_min, sal_max, sal_curr, sal_period = parse_salary(raw.get("salary", ""))
            src = raw.get("source", source_name)
            domain = re.sub(r'[^a-z0-9.]', '', company.lower().replace(" ", "")) + ".com"

            job = Job(
                user_id=user_id,
                external_id=raw.get("id", ""),
                title=title,
                company=company,
                company_logo_url=f"https://logo.clearbit.com/{domain}",
                location=location,
                job_url=job_url,
                normalized_key=nkey,
                description_full=full_desc[:10000] if full_desc else None,
                description_snippet=description[:500] if description else None,
                salary_min=sal_min,
                salary_max=sal_max,
                salary_currency=sal_curr,
                salary_period=sal_period,
                employment_type=raw.get("employment_type", "full-time"),
                experience_level=detect_experience_level(title + " " + description),
                work_mode=detect_work_mode(location + " " + title + " " + description),
                department=raw.get("department"),
                skills_required=raw.get("skills_required", []),
                posted_date=_parse_date(raw.get("posted_date")),
                source=src,
                ats_type=raw.get("ats_type"),
                category=classify_category(title, description),
                status="active",
                is_easy_apply=raw.get("easy_apply", False),
                hr_name=raw.get("hr_name"),
                hr_email=raw.get("hr_email"),
                first_seen_at=now,
                last_seen_at=now,
                times_seen=1,
            )
            db.add(job)
            db.flush()

            # Add source record
            db.add(JobSource(job_id=job.id, source=src, source_url=job_url, first_seen_at=now, last_seen_at=now))

            stats["new"] += 1

        except Exception as e:
            stats["errors"] += 1
            print(f"[WARN] Ingest error for {raw.get('title', '?')}: {e}")
            continue

    db.commit()
    return stats


def _parse_date(date_val) -> Optional[datetime]:
    if not date_val:
        return None
    if isinstance(date_val, datetime):
        return date_val
    try:
        return datetime.fromisoformat(str(date_val).replace("Z", "+00:00"))
    except Exception:
        return None
