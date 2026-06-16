from datetime import datetime

from app import db


class StudentProfile(db.Model):
    __tablename__ = "student_profiles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False)
    full_name = db.Column(db.String(150), nullable=False)
    phone = db.Column(db.String(20))
    education = db.Column(db.Text)
    experience_years = db.Column(db.Numeric(3, 1), default=0)
    bio = db.Column(db.Text)
    resume_path = db.Column(db.String(500))
    profile_complete_pct = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship("User", back_populates="student_profile")
    skills = db.relationship("StudentSkill", back_populates="student", cascade="all, delete-orphan")
    applications = db.relationship("Application", back_populates="student", cascade="all, delete-orphan")

    def calculate_completeness(self):
        fields = [
            bool(self.full_name and self.full_name.strip()),
            bool(self.phone),
            bool(self.education),
            float(self.experience_years or 0) >= 0,
            bool(self.bio),
            bool(self.resume_path),
            len(self.skills) > 0,
        ]
        pct = int((sum(fields) / len(fields)) * 100)
        self.profile_complete_pct = pct
        return pct


class CompanyProfile(db.Model):
    __tablename__ = "company_profiles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False)
    company_name = db.Column(db.String(200), nullable=False)
    industry = db.Column(db.String(100))
    website = db.Column(db.String(255))
    description = db.Column(db.Text)
    logo_path = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship("User", back_populates="company_profile")
    jobs = db.relationship("Job", back_populates="company", cascade="all, delete-orphan")
