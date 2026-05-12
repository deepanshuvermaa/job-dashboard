from sqlalchemy import Column, String, Text, Boolean, ForeignKey, JSON, DateTime
from sqlalchemy.orm import relationship
from models.base import Base, TimestampMixin, generate_uuid, utcnow


class Application(Base, TimestampMixin):
    __tablename__ = "applications"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    job_id = Column(String(36), ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    status = Column(String(30), default="applied")  # applied, interview, rejected, offer, withdrawn
    applied_at = Column(DateTime, default=utcnow)
    method = Column(String(30), default="easy_apply")  # easy_apply, direct, referral
    resume_used = Column(String(512))
    cover_letter = Column(Text)
    questions_asked = Column(JSON, default=list)
    answers_provided = Column(JSON, default=list)
    screenshot_path = Column(String(512))
    response_date = Column(DateTime)
    notes = Column(Text)

    job = relationship("Job", back_populates="applications")
    user = relationship("User", back_populates="applications")
