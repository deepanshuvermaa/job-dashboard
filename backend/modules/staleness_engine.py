"""Staleness engine — hard-deletes jobs not seen in the last 7 days."""
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from models.job import Job

PURGE_DAYS = 7


def run_cleanup(db: Session, user_id: str) -> dict:
    """
    Delete all jobs for this user that haven't been seen in PURGE_DAYS days.
    Jobs with active applications are preserved.
    Returns count of deleted jobs.
    """
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(days=PURGE_DAYS)

    from models.application import Application
    applied_job_ids = (
        db.query(Application.job_id)
        .filter(Application.user_id == user_id)
        .subquery()
    )

    deleted = (
        db.query(Job)
        .filter(
            Job.user_id == user_id,
            Job.last_seen_at < cutoff,
            ~Job.id.in_(applied_job_ids),
        )
        .delete(synchronize_session=False)
    )

    db.commit()
    return {"deleted": deleted, "cutoff_days": PURGE_DAYS}
