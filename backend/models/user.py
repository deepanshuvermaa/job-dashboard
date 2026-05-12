from sqlalchemy import Column, String, Text, Integer, ForeignKey, JSON
from sqlalchemy.orm import relationship
from models.base import Base, TimestampMixin, generate_uuid


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    email = Column(String(255), unique=True, nullable=False, index=True)
    full_name = Column(String(255), nullable=False)
    password_hash = Column(String(255), nullable=False)
    avatar_url = Column(String(512))

    profile = relationship("UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    jobs = relationship("Job", back_populates="user", cascade="all, delete-orphan")
    applications = relationship("Application", back_populates="user", cascade="all, delete-orphan")
    resumes = relationship("Resume", back_populates="user", cascade="all, delete-orphan")


class UserProfile(Base, TimestampMixin):
    __tablename__ = "user_profiles"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)

    headline = Column(String(255))
    summary = Column(Text)
    phone = Column(String(50))
    location = Column(String(255))
    linkedin_url = Column(String(512))
    github_url = Column(String(512))
    portfolio_url = Column(String(512))
    skills = Column(JSON, default=list)
    experience = Column(JSON, default=list)
    education = Column(JSON, default=list)
    certifications = Column(JSON, default=list)
    salary_expectation_min = Column(Integer)
    salary_expectation_max = Column(Integer)
    preferred_work_mode = Column(String(20))  # remote, hybrid, onsite
    preferred_locations = Column(JSON, default=list)
    resume_base_path = Column(String(512))

    user = relationship("User", back_populates="profile")
