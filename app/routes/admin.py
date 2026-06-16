from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app import db
from app.decorators import admin_required
from app.models import Application, AuditLog, Job, User

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/dashboard")
@login_required
@admin_required
def dashboard():
    user_count = User.query.count()
    job_count = Job.query.filter_by(status="active").count()
    app_count = Application.query.count()
    recent_logs = AuditLog.query.order_by(AuditLog.created_at.desc()).limit(10).all()
    return render_template(
        "admin/dashboard.html",
        user_count=user_count,
        job_count=job_count,
        app_count=app_count,
        recent_logs=recent_logs,
    )


@admin_bp.route("/users")
@login_required
@admin_required
def users():
    role = request.args.get("role", "")
    q = request.args.get("q", "").strip()

    query = User.query
    if role:
        query = query.filter_by(role=role)
    if q:
        query = query.filter(User.email.ilike(f"%{q}%"))

    users_list = query.order_by(User.created_at.desc()).all()
    return render_template("admin/users.html", users=users_list, role=role, q=q)


@admin_bp.route("/users/<int:user_id>/toggle", methods=["POST"])
@login_required
@admin_required
def toggle_user(user_id):
    user = User.query.get_or_404(user_id)

    if user.id == current_user.id:
        flash("You cannot deactivate your own account.", "error")
        return redirect(url_for("admin.users"))

    user.is_active = not user.is_active
    action = "activate_user" if user.is_active else "deactivate_user"

    log = AuditLog(
        admin_id=current_user.id,
        action=action,
        target_type="user",
        target_id=user.id,
    )
    log.set_details({"email": user.email, "role": user.role, "is_active": user.is_active})
    db.session.add(log)
    db.session.commit()

    status = "activated" if user.is_active else "deactivated"
    flash(f"User {user.email} has been {status}.", "success")
    return redirect(url_for("admin.users"))


@admin_bp.route("/jobs")
@login_required
@admin_required
def jobs():
    status = request.args.get("status", "")
    query = Job.query
    if status:
        query = query.filter_by(status=status)
    jobs_list = query.order_by(Job.posted_at.desc()).all()
    return render_template("admin/jobs.html", jobs=jobs_list, status=status)


@admin_bp.route("/jobs/<int:job_id>/moderate", methods=["POST"])
@login_required
@admin_required
def moderate_job(job_id):
    job = Job.query.get_or_404(job_id)
    action = request.form.get("action", "close")

    if action == "remove":
        job.status = "closed"
        log_action = "remove_job"
    elif action == "approve":
        job.status = "active"
        log_action = "approve_job"
    else:
        job.status = "closed"
        log_action = "close_job"

    log = AuditLog(
        admin_id=current_user.id,
        action=log_action,
        target_type="job",
        target_id=job.id,
    )
    log.set_details({"title": job.title, "new_status": job.status})
    db.session.add(log)
    db.session.commit()

    flash(f"Job '{job.title}' has been moderated.", "success")
    return redirect(url_for("admin.jobs"))
