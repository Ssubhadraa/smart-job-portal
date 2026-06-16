from datetime import datetime

from app import db


class Job(db.Model):
    __tablename__ = "jobs"

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey("company_profiles.id"), nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(150))
    job_type = db.Column(db.String(20), nullable=False)
    experience_min = db.Column(db.Integer, default=0)
    salary_min = db.Column(db.Numeric(12, 2))
    salary_max = db.Column(db.Numeric(12, 2))
    status = db.Column(db.String(20), default="active", index=True)
    posted_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    expires_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    company = db.relationship("CompanyProfile", back_populates="jobs")
    skills = db.relationship("JobSkill", back_populates="job", cascade="all, delete-orphan")
    applications = db.relationship("Application", back_populates="job", cascade="all, delete-orphan")


class JobSkill(db.Model):
    __tablename__ = "job_skills"

    job_id = db.Column(db.Integer, db.ForeignKey("jobs.id"), primary_key=True)
    skill_id = db.Column(db.Integer, db.ForeignKey("skills.id"), primary_key=True)
    is_required = db.Column(db.Boolean, default=True)

    job = db.relationship("Job", back_populates="skills")
    skill = db.relationship("Skill")
