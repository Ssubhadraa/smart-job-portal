import os
import uuid

from flask import Blueprint, current_app, flash, jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app import db
from app.decorators import student_required
from app.models import Application, Skill, StudentProfile, StudentSkill
from app.services.recommendation import get_recommendations
from app.utils import allowed_file

students_bp = Blueprint("students", __name__)


@students_bp.route("/dashboard")
@login_required
@student_required
def dashboard():
    profile = current_user.student_profile
    recommendations = get_recommendations(profile.id) if profile else []
    return render_template(
        "students/dashboard.html",
        profile=profile,
        recommendations=recommendations,
    )


@students_bp.route("/profile", methods=["GET", "POST"])
@login_required
@student_required
def profile():
    profile = current_user.student_profile
    all_skills = Skill.query.order_by(Skill.category, Skill.name).all()

    if request.method == "POST":
        profile.full_name = request.form.get("full_name", "").strip()
        profile.phone = request.form.get("phone", "").strip()
        profile.education = request.form.get("education", "").strip()
        profile.bio = request.form.get("bio", "").strip()

        try:
            profile.experience_years = float(request.form.get("experience_years", 0) or 0)
        except ValueError:
            flash("Experience years must be a number.", "error")
            return render_template("students/profile.html", profile=profile, all_skills=all_skills)

        if not profile.full_name:
            flash("Full name is required.", "error")
            return render_template("students/profile.html", profile=profile, all_skills=all_skills)

        profile.calculate_completeness()
        db.session.commit()
        flash("Profile updated successfully.", "success")
        return redirect(url_for("students.profile"))

    return render_template("students/profile.html", profile=profile, all_skills=all_skills)


@students_bp.route("/skills", methods=["POST"])
@login_required
@student_required
def manage_skills():
    profile = current_user.student_profile
    skill_ids = request.form.getlist("skill_ids")
    proficiency = request.form.get("proficiency", "intermediate")

    if proficiency not in ("beginner", "intermediate", "expert"):
        proficiency = "intermediate"

    StudentSkill.query.filter_by(student_id=profile.id).delete()

    for sid in skill_ids:
        try:
            skill_id = int(sid)
        except (TypeError, ValueError):
            continue
        if Skill.query.get(skill_id):
            db.session.add(
                StudentSkill(student_id=profile.id, skill_id=skill_id, proficiency=proficiency)
            )

    profile.calculate_completeness()
    db.session.commit()
    flash("Skills updated successfully.", "success")
    return redirect(url_for("students.profile"))


@students_bp.route("/resume", methods=["POST"])
@login_required
@student_required
def upload_resume():
    profile = current_user.student_profile
    file = request.files.get("resume")

    if not file or not file.filename:
        flash("No file selected.", "error")
        return redirect(url_for("students.profile"))

    if not allowed_file(file.filename, {"pdf"}):
        flash("Only PDF resumes are allowed.", "error")
        return redirect(url_for("students.profile"))

    upload_dir = os.path.join(current_app.config["UPLOAD_FOLDER"], "resumes")
    os.makedirs(upload_dir, exist_ok=True)

    ext = file.filename.rsplit(".", 1)[1].lower()
    filename = f"{uuid.uuid4().hex}.{ext}"
    filepath = os.path.join(upload_dir, filename)
    file.save(filepath)

    profile.resume_path = os.path.join("resumes", filename)
    profile.calculate_completeness()
    db.session.commit()
    flash("Resume uploaded successfully.", "success")
    return redirect(url_for("students.profile"))


@students_bp.route("/applications")
@login_required
@student_required
def applications():
    profile = current_user.student_profile
    apps = (
        Application.query.filter_by(student_id=profile.id)
        .order_by(Application.applied_at.desc())
        .all()
    )
    return render_template("students/applications.html", applications=apps)


@students_bp.route("/api/v1/recommendations")
@login_required
@student_required
def recommendations_api():
    profile = current_user.student_profile
    if not profile.skills:
        return jsonify({"recommendations": [], "message": "Complete your profile to get recommendations."})

    recs = get_recommendations(profile.id)
    return jsonify({"recommendations": recs})
