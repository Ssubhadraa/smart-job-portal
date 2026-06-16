# Smart Job Portal

A Flask-based job portal with skill-based job recommendations, role-based dashboards for students, companies, and admins.

## Tech Stack

- Python Flask
- SQLAlchemy + Flask-Migrate
- Flask-Login
- bcrypt
- SQLite
- Jinja2, HTML/CSS/JS

## Setup

```bash
cd smart-job-portal
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
python seed.py
flask run
```

Open http://127.0.0.1:5000

## Default Credentials

| Role    | Email              | Password    |
|---------|--------------------|-------------|
| Admin   | admin@portal.com   | admin123    |
| Company | hr@techcorp.com    | Company123  |
| Company | jobs@datadrive.io  | Company123  |
| Company | careers@cloudscale.com | Company123 |
| Student | alice@student.com  | Student123  |
| Student | bob@student.com    | Student123  |
| Student | carol@student.com  | Student123  |
| Student | david@student.com  | Student123  |
| Student | eva@student.com    | Student123  |

## Features

- **Auth**: Register as student/company, login/logout with password validation
- **Student**: Profile CRUD, skills management, resume upload, profile completeness, recommendations
- **Company**: Profile CRUD, job posting with skill tags, applicant management
- **Jobs**: Public listing with search, filters, pagination, and job detail pages
- **Recommendations**: Skill-based matching (≥30% threshold) on student dashboard
- **Applications**: Apply with cover note, track status, company status updates
- **Admin**: Dashboard metrics, user activate/deactivate with audit logs, job moderation

## Project Structure

```
smart-job-portal/
├── app/
│   ├── __init__.py          # App factory
│   ├── models/              # SQLAlchemy models
│   ├── routes/              # auth, students, jobs, admin blueprints
│   ├── services/            # Recommendation engine
│   ├── templates/           # Jinja2 templates
│   └── static/              # CSS and JS
├── migrations/              # Flask-Migrate
├── uploads/                 # Resume uploads
├── seed.py                  # Database seeder
├── app.py                   # Entry point
├── requirements.txt
├── .env.example
└── readme.md
```

## API Endpoints

- `GET /students/api/v1/recommendations` — JSON job recommendations for logged-in students

## Environment Variables

| Variable     | Default                      | Description        |
|-------------|------------------------------|--------------------|
| SECRET_KEY  | (required in production)     | Flask secret key   |
| DATABASE_URL| sqlite:///smart_job_portal.db| Database URI       |
| UPLOAD_FOLDER | uploads                    | File upload path   |
