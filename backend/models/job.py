from sqlalchemy import (
    Column, String, Text, Integer, Float, Boolean,
    ForeignKey, JSON, DateTime, Index
)
from sqlalchemy.orm import relationship
from models.base import Base, TimestampMixin, generate_uuid, utcnow


class Job(Base, TimestampMixin):
    __tablename__ = "jobs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    external_id = Column(String(255))
    title = Column(String(500), nullable=False)
    company = Column(String(255), nullable=False)
    company_logo_url = Column(String(512))
    location = Column(String(255), default="Not specified")
    job_url = Column(String(1024), nullable=False)
    normalized_key = Column(String(512), nullable=False, index=True)
    description_full = Column(Text)
    description_snippet = Column(String(500))
    salary_min = Column(Integer)
    salary_max = Column(Integer)
    salary_currency = Column(String(10), default="USD")
    salary_period = Column(String(20), default="yearly")  # yearly, monthly, hourly
    employment_type = Column(String(50), default="full-time")
    experience_level = Column(String(50))  # entry, mid, senior, lead, director
    work_mode = Column(String(20))  # remote, hybrid, onsite
    department = Column(String(255))
    skills_required = Column(JSON, default=list)
    skills_matched = Column(JSON, default=list)
    posted_date = Column(DateTime)
    source = Column(String(50), nullable=False)  # linkedin, greenhouse, lever, etc.
    ats_type = Column(String(50))
    category = Column(String(50))  # backend, frontend, fullstack, devops, data, ai_ml, design, product, other
    status = Column(String(20), default="active", index=True)  # active, stale, expired, archived
    is_easy_apply = Column(Boolean, default=False)
    is_bookmarked = Column(Boolean, default=False)
    is_ignored = Column(Boolean, default=False)
    first_seen_at = Column(DateTime, default=utcnow)
    last_seen_at = Column(DateTime, default=utcnow)
    times_seen = Column(Integer, default=1)

    user = relationship("User", back_populates="jobs")
    evaluation = relationship("JobEvaluation", back_populates="job", uselist=False, cascade="all, delete-orphan")
    sources = relationship("JobSource", back_populates="job", cascade="all, delete-orphan")
    applications = relationship("Application", back_populates="job", cascade="all, delete-orphan")
    resumes = relationship("Resume", back_populates="job", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_jobs_user_url", "user_id", "job_url", unique=True),
        Index("ix_jobs_user_normalized", "user_id", "normalized_key"),
        Index("ix_jobs_user_status", "user_id", "status"),
    )


class JobEvaluation(Base):
    __tablename__ = "job_evaluations"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    job_id = Column(String(36), ForeignKey("jobs.id", ondelete="CASCADE"), unique=True, nullable=False)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    overall_score = Column(Float)
    grade = Column(String(2))  # A, B, C, D, F
    gate_pass = Column(Boolean, default=False)
    role_match = Column(Float)
    skills_alignment = Column(Float)
    seniority_fit = Column(Float)
    compensation = Column(Float)
    interview_likelihood = Column(Float)
    growth_potential = Column(Float)
    company_reputation = Column(Float)
    location_fit = Column(Float)
    tech_stack_match = Column(Float)
    culture_signals = Column(Float)
    reasoning = Column(Text)
    evaluated_at = Column(DateTime, default=utcnow)

    job = relationship("Job", back_populates="evaluation")


class JobSource(Base):
    __tablename__ = "job_sources"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    job_id = Column(String(36), ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    source = Column(String(50), nullable=False)
    source_url = Column(String(1024))
    first_seen_at = Column(DateTime, default=utcnow)
    last_seen_at = Column(DateTime, default=utcnow)

    job = relationship("Job", back_populates="sources")
