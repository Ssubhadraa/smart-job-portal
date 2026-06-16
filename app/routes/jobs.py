from datetime import datetime, timedelta

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app import db
from app.decorators import company_required
from app.models import Application, CompanyProfile, Job, JobSkill, Skill
from app.services.recommendation import get_match_score
from sqlalchemy import or_

jobs_bp = Blueprint("jobs", __name__)

JOB_TYPES = ["full_time", "part_time", "internship", "contract"]
SORT_OPTIONS = {"date": "posted_at", "relevance": "title"}


@jobs_bp.route("/")
def list_jobs():
    page = request.args.get("page", 1, type=int)
    q = request.args.get("q", "").strip()
    location = request.args.get("location", "").strip()
    job_type = request.args.get("job_type", "").strip()
    experience = request.args.get("experience", type=int)
    salary_min = request.args.get("salary_min", type=int)
    sort = request.args.get("sort", "date")

    query = Job.query.filter_by(status="active")

    if q:
        query = query.join(CompanyProfile).filter(
            or_(
                Job.title.ilike(f"%{q}%"),
                Job.description.ilike(f"%{q}%"),
                CompanyProfile.company_name.ilike(f"%{q}%"),
            )
        )
    else:
        query = query.join(CompanyProfile)

    if location:
        query = query.filter(Job.location.ilike(f"%{location}%"))
    if job_type and job_type in JOB_TYPES:
        query = query.filter(Job.job_type == job_type)
    if experience is not None:
        query = query.filter(Job.experience_min <= experience)
    if salary_min is not None:
        query = query.filter(or_(Job.salary_max >= salary_min, Job.salary_min >= salary_min))

    if sort == "relevance" and q:
        query = query.order_by(Job.title.asc())
    else:
        query = query.order_by(Job.posted_at.desc())

    pagination = query.paginate(page=page, per_page=10, error_out=False)
    jobs_with_scores = []
    student_id = None
    if current_user.is_authenticated and current_user.is_student:
        student_id = current_user.student_profile.id

    for job in pagination.items:
        match_score = None
        if student_id:
            score = get_match_score(student_id, job.id)
            if score >= 30:
                match_score = score
        jobs_with_scores.append({"job": job, "match_score": match_score})

    return render_template(
        "jobs/list.html",
        jobs=jobs_with_scores,
        pagination=pagination,
        q=q,
        location=location,
        job_type=job_type,
        experience=experience,
        salary_min=salary_min,
        sort=sort,
        job_types=JOB_TYPES,
    )


@jobs_bp.route("/<int:job_id>")
def detail(job_id):
    job = Job.query.get_or_404(job_id)
    if job.status != "active" and not (
        current_user.is_authenticated
        and (
            current_user.is_admin
            or (current_user.is_company and current_user.company_profile.id == job.company_id)
        )
    ):
        if job.status == "closed":
            flash("This job listing is closed.", "warning")
        else:
            abort(404)

    existing_application = None
    match_score = None
    if current_user.is_authenticated and current_user.is_student:
        existing_application = Application.query.filter_by(
            job_id=job.id, student_id=current_user.student_profile.id
        ).first()
        score = get_match_score(current_user.student_profile.id, job.id)
        if score >= 30:
            match_score = score

    return render_template(
        "jobs/detail.html",
        job=job,
        existing_application=existing_application,
        match_score=match_score,
    )


@jobs_bp.route("/<int:job_id>/apply", methods=["POST"])
@login_required
def apply(job_id):
    if not current_user.is_student:
        abort(403)

    job = Job.query.get_or_404(job_id)
    if job.status != "active":
        flash("This job is no longer accepting applications.", "error")
        return redirect(url_for("jobs.detail", job_id=job_id))

    profile = current_user.student_profile
    existing = Application.query.filter_by(job_id=job.id, student_id=profile.id).first()
    if existing:
        flash("You have already applied to this job.", "warning")
        return redirect(url_for("jobs.detail", job_id=job_id))

    cover_note = request.form.get("cover_note", "").strip()
    application = Application(
        job_id=job.id,
        student_id=profile.id,
        cover_note=cover_note or None,
    )
    db.session.add(application)
    db.session.commit()
    flash("Application submitted successfully!", "success")
    return redirect(url_for("students.applications"))


@jobs_bp.route("/company/dashboard")
@login_required
@company_required
def company_dashboard():
    company = current_user.company_profile
    jobs = Job.query.filter_by(company_id=company.id).order_by(Job.posted_at.desc()).all()
    total_apps = sum(len(j.applications) for j in jobs)
    return render_template(
        "jobs/company_dashboard.html",
        company=company,
        jobs=jobs,
        total_apps=total_apps,
    )


@jobs_bp.route("/company/profile", methods=["GET", "POST"])
@login_required
@company_required
def company_profile():
    company = current_user.company_profile

    if request.method == "POST":
        company.company_name = request.form.get("company_name", "").strip()
        company.industry = request.form.get("industry", "").strip()
        company.website = request.form.get("website", "").strip()
        company.description = request.form.get("description", "").strip()

        if not company.company_name:
            flash("Company name is required.", "error")
            return render_template("jobs/company_profile.html", company=company)

        db.session.commit()
        flash("Company profile updated.", "success")
        return redirect(url_for("jobs.company_profile"))

    return render_template("jobs/company_profile.html", company=company)


@jobs_bp.route("/company/jobs/new", methods=["GET", "POST"])
@jobs_bp.route("/company/jobs/<int:job_id>/edit", methods=["GET", "POST"])
@login_required
@company_required
def manage_job(job_id=None):
    company = current_user.company_profile
    all_skills = Skill.query.order_by(Skill.name).all()
    job = Job.query.get(job_id) if job_id else None

    if job and job.company_id != company.id:
        abort(403)

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        location = request.form.get("location", "").strip()
        job_type = request.form.get("job_type", "full_time")
        action = request.form.get("action", "publish")

        if not title or not description:
            flash("Title and description are required.", "error")
            return render_template(
                "jobs/form.html", job=job, all_skills=all_skills, job_types=JOB_TYPES
            )

        if job_type not in JOB_TYPES:
            job_type = "full_time"

        try:
            experience_min = int(request.form.get("experience_min", 0) or 0)
        except ValueError:
            experience_min = 0

        salary_min = request.form.get("salary_min")
        salary_max = request.form.get("salary_max")

        if not job:
            job = Job(company_id=company.id)
            db.session.add(job)
            db.session.flush()

        job.title = title
        job.description = description
        job.location = location
        job.job_type = job_type
        job.experience_min = experience_min
        job.salary_min = float(salary_min) if salary_min else None
        job.salary_max = float(salary_max) if salary_max else None
        job.status = "draft" if action == "draft" else "active"
        if action == "publish" and not job.posted_at:
            job.posted_at = datetime.utcnow()
        job.expires_at = datetime.utcnow() + timedelta(days=90)

        JobSkill.query.filter_by(job_id=job.id).delete()
        db.session.flush()

        skill_ids = request.form.getlist("skill_ids")
        for sid in skill_ids:
            try:
                skill_id = int(sid)
            except (TypeError, ValueError):
                continue
            if Skill.query.get(skill_id):
                db.session.add(JobSkill(job_id=job.id, skill_id=skill_id, is_required=True))

        db.session.commit()
        flash("Job saved successfully.", "success")
        return redirect(url_for("jobs.company_dashboard"))

    selected_skill_ids = [js.skill_id for js in job.skills] if job else []
    return render_template(
        "jobs/form.html",
        job=job,
        all_skills=all_skills,
        job_types=JOB_TYPES,
        selected_skill_ids=selected_skill_ids,
    )


@jobs_bp.route("/company/jobs/<int:job_id>/close", methods=["POST"])
@login_required
@company_required
def close_job(job_id):
    company = current_user.company_profile
    job = Job.query.get_or_404(job_id)
    if job.company_id != company.id:
        abort(403)
    job.status = "closed"
    db.session.commit()
    flash("Job closed.", "success")
    return redirect(url_for("jobs.company_dashboard"))


@jobs_bp.route("/company/jobs/<int:job_id>/applicants")
@login_required
@company_required
def applicants(job_id):
    company = current_user.company_profile
    job = Job.query.get_or_404(job_id)
    if job.company_id != company.id:
        abort(403)

    apps = Application.query.filter_by(job_id=job.id).order_by(Application.applied_at.desc()).all()
    return render_template("jobs/applicants.html", job=job, applications=apps)


@jobs_bp.route("/company/applications/<int:app_id>/status", methods=["POST"])
@login_required
@company_required
def update_application_status(app_id):
    company = current_user.company_profile
    application = Application.query.get_or_404(app_id)
    if application.job.company_id != company.id:
        abort(403)

    status = request.form.get("status", "applied")
    if status not in ("applied", "shortlisted", "rejected", "hired"):
        flash("Invalid status.", "error")
        return redirect(url_for("jobs.applicants", job_id=application.job_id))

    application.status = status
    db.session.commit()
    flash(f"Application marked as {status}.", "success")
    return redirect(url_for("jobs.applicants", job_id=application.job_id))
