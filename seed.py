"""Seed the database with sample data."""

from datetime import datetime, timedelta

from app import create_app, db
from app.models import (
    Application,
    CompanyProfile,
    Job,
    JobSkill,
    Skill,
    StudentProfile,
    StudentSkill,
    User,
)
from app.utils import hash_password

SKILLS = [
    ("Python", "language"),
    ("Java", "language"),
    ("JavaScript", "language"),
    ("TypeScript", "language"),
    ("React", "framework"),
    ("Node.js", "framework"),
    ("Flask", "framework"),
    ("Django", "framework"),
    ("SQL", "database"),
    ("PostgreSQL", "database"),
    ("MongoDB", "database"),
    ("AWS", "cloud"),
    ("Docker", "devops"),
    ("Kubernetes", "devops"),
    ("Git", "tool"),
    ("HTML/CSS", "frontend"),
    ("Vue.js", "framework"),
    ("Spring Boot", "framework"),
    ("Machine Learning", "data"),
    ("Data Analysis", "data"),
]

COMPANIES = [
    {
        "email": "hr@techcorp.com",
        "password": "Company123",
        "company_name": "TechCorp Solutions",
        "industry": "Technology",
        "website": "https://techcorp.example.com",
        "description": "Leading software development company specializing in enterprise solutions.",
    },
    {
        "email": "jobs@datadrive.io",
        "password": "Company123",
        "company_name": "DataDrive Analytics",
        "industry": "Data & Analytics",
        "website": "https://datadrive.example.com",
        "description": "Data-driven insights and machine learning platforms.",
    },
    {
        "email": "careers@cloudscale.com",
        "password": "Company123",
        "company_name": "CloudScale Systems",
        "industry": "Cloud Infrastructure",
        "website": "https://cloudscale.example.com",
        "description": "Cloud infrastructure and DevOps consulting.",
    },
]

STUDENTS = [
    {
        "email": "alice@student.com",
        "password": "Student123",
        "full_name": "Alice Johnson",
        "phone": "555-0101",
        "education": "B.S. Computer Science, MIT",
        "experience_years": 2,
        "bio": "Full-stack developer passionate about web technologies.",
        "skills": ["Python", "React", "JavaScript", "SQL", "Git"],
    },
    {
        "email": "bob@student.com",
        "password": "Student123",
        "full_name": "Bob Smith",
        "phone": "555-0102",
        "education": "B.S. Software Engineering, Stanford",
        "experience_years": 1,
        "bio": "Backend developer with a focus on Python and databases.",
        "skills": ["Python", "Flask", "Django", "PostgreSQL", "Docker"],
    },
    {
        "email": "carol@student.com",
        "password": "Student123",
        "full_name": "Carol Williams",
        "phone": "555-0103",
        "education": "M.S. Data Science, Berkeley",
        "experience_years": 3,
        "bio": "Data scientist with ML expertise.",
        "skills": ["Python", "Machine Learning", "Data Analysis", "SQL", "AWS"],
    },
    {
        "email": "david@student.com",
        "password": "Student123",
        "full_name": "David Chen",
        "phone": "555-0104",
        "education": "B.S. Information Systems, UCLA",
        "experience_years": 0.5,
        "bio": "Junior developer eager to learn cloud technologies.",
        "skills": ["JavaScript", "Node.js", "React", "HTML/CSS", "Git"],
    },
    {
        "email": "eva@student.com",
        "password": "Student123",
        "full_name": "Eva Martinez",
        "phone": "555-0105",
        "education": "B.S. Computer Engineering, Georgia Tech",
        "experience_years": 4,
        "bio": "Senior developer with Java and cloud experience.",
        "skills": ["Java", "Spring Boot", "AWS", "Docker", "Kubernetes"],
    },
]

JOB_TEMPLATES = [
    {
        "title": "Senior Python Developer",
        "description": "Build scalable backend services using Python and Flask. Work with cross-functional teams.",
        "location": "San Francisco, CA",
        "job_type": "full_time",
        "experience_min": 3,
        "salary_min": 120000,
        "salary_max": 160000,
        "skills": ["Python", "Flask", "SQL", "Docker"],
    },
    {
        "title": "Frontend React Engineer",
        "description": "Create responsive user interfaces with React and modern JavaScript.",
        "location": "Remote",
        "job_type": "full_time",
        "experience_min": 2,
        "salary_min": 100000,
        "salary_max": 140000,
        "skills": ["React", "JavaScript", "TypeScript", "HTML/CSS"],
    },
    {
        "title": "Data Scientist",
        "description": "Develop ML models and analyze large datasets to drive business decisions.",
        "location": "New York, NY",
        "job_type": "full_time",
        "experience_min": 2,
        "salary_min": 110000,
        "salary_max": 150000,
        "skills": ["Python", "Machine Learning", "Data Analysis", "SQL"],
    },
    {
        "title": "DevOps Engineer",
        "description": "Manage CI/CD pipelines and cloud infrastructure on AWS.",
        "location": "Austin, TX",
        "job_type": "full_time",
        "experience_min": 3,
        "salary_min": 115000,
        "salary_max": 155000,
        "skills": ["AWS", "Docker", "Kubernetes", "Python"],
    },
    {
        "title": "Software Engineering Intern",
        "description": "Summer internship program for aspiring developers. Mentorship included.",
        "location": "Remote",
        "job_type": "internship",
        "experience_min": 0,
        "salary_min": 25,
        "salary_max": 35,
        "skills": ["JavaScript", "Python", "Git"],
    },
]


def seed():
    app = create_app()
    with app.app_context():
        db.drop_all()
        db.create_all()

        skill_map = {}
        for name, category in SKILLS:
            skill = Skill(name=name, category=category)
            db.session.add(skill)
            db.session.flush()
            skill_map[name] = skill.id

        admin = User(
            email="admin@portal.com",
            password_hash=hash_password("admin123"),
            role="admin",
        )
        db.session.add(admin)

        company_profiles = []
        for comp_data in COMPANIES:
            user = User(
                email=comp_data["email"],
                password_hash=hash_password(comp_data["password"]),
                role="company",
            )
            db.session.add(user)
            db.session.flush()

            profile = CompanyProfile(
                user_id=user.id,
                company_name=comp_data["company_name"],
                industry=comp_data["industry"],
                website=comp_data["website"],
                description=comp_data["description"],
            )
            db.session.add(profile)
            db.session.flush()
            company_profiles.append(profile)

            for tmpl in JOB_TEMPLATES:
                job = Job(
                    company_id=profile.id,
                    title=f"{tmpl['title']} — {comp_data['company_name'][:10]}",
                    description=tmpl["description"],
                    location=tmpl["location"],
                    job_type=tmpl["job_type"],
                    experience_min=tmpl["experience_min"],
                    salary_min=tmpl["salary_min"],
                    salary_max=tmpl["salary_max"],
                    status="active",
                    posted_at=datetime.utcnow() - timedelta(days=company_profiles.index(profile)),
                    expires_at=datetime.utcnow() + timedelta(days=90),
                )
                db.session.add(job)
                db.session.flush()

                for skill_name in tmpl["skills"]:
                    db.session.add(
                        JobSkill(job_id=job.id, skill_id=skill_map[skill_name], is_required=True)
                    )

        student_profiles = []
        for stu_data in STUDENTS:
            user = User(
                email=stu_data["email"],
                password_hash=hash_password(stu_data["password"]),
                role="student",
            )
            db.session.add(user)
            db.session.flush()

            profile = StudentProfile(
                user_id=user.id,
                full_name=stu_data["full_name"],
                phone=stu_data["phone"],
                education=stu_data["education"],
                experience_years=stu_data["experience_years"],
                bio=stu_data["bio"],
            )
            db.session.add(profile)
            db.session.flush()

            for skill_name in stu_data["skills"]:
                db.session.add(
                    StudentSkill(
                        student_id=profile.id,
                        skill_id=skill_map[skill_name],
                        proficiency="intermediate",
                    )
                )

            profile.calculate_completeness()
            student_profiles.append(profile)

        if student_profiles and company_profiles:
            job = Job.query.filter_by(company_id=company_profiles[0].id).first()
            if job:
                db.session.add(
                    Application(
                        job_id=job.id,
                        student_id=student_profiles[0].id,
                        cover_note="I am excited about this opportunity!",
                        status="applied",
                    )
                )

        db.session.commit()
        print("Database seeded successfully!")
        print(f"  Skills: {len(SKILLS)}")
        print(f"  Admin: admin@portal.com / admin123")
        print(f"  Companies: {len(COMPANIES)} (password: Company123)")
        print(f"  Students: {len(STUDENTS)} (password: Student123)")
        print(f"  Jobs: {Job.query.count()}")


if __name__ == "__main__":
    seed()
