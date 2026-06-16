from app import db


class Skill(db.Model):
    __tablename__ = "skills"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    category = db.Column(db.String(50))


class StudentSkill(db.Model):
    __tablename__ = "student_skills"

    student_id = db.Column(db.Integer, db.ForeignKey("student_profiles.id"), primary_key=True)
    skill_id = db.Column(db.Integer, db.ForeignKey("skills.id"), primary_key=True)
    proficiency = db.Column(db.String(20), default="intermediate")

    student = db.relationship("StudentProfile", back_populates="skills")
    skill = db.relationship("Skill")
