from sqlalchemy import Column, String, ForeignKey, JSON, DateTime
from sqlalchemy.orm import relationship
from models.base import Base, generate_uuid, utcnow


class Resume(Base):
    __tablename__ = "resumes"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    job_id = Column(String(36), ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    file_path = Column(String(512))
    file_url = Column(String(1024))  # for Supabase Storage later
    archetype_used = Column(String(50))
    keywords_injected = Column(JSON, default=list)
    created_at = Column(DateTime, default=utcnow)

    job = relationship("Job", back_populates="resumes")
    user = relationship("User", back_populates="resumes")
