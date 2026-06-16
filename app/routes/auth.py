from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from app import db
from app.models import CompanyProfile, StudentProfile, User
from app.utils import check_password, hash_password, validate_email, validate_password

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(_dashboard_url(current_user))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")
        role = request.form.get("role", "student")

        if role not in ("student", "company"):
            flash("Invalid role selected.", "error")
            return render_template("auth/register.html")

        if not validate_email(email):
            flash("Please enter a valid email address.", "error")
            return render_template("auth/register.html")

        valid, msg = validate_password(password)
        if not valid:
            flash(msg, "error")
            return render_template("auth/register.html")

        if password != confirm:
            flash("Passwords do not match.", "error")
            return render_template("auth/register.html")

        if User.query.filter_by(email=email).first():
            flash("An account with this email already exists.", "error")
            return render_template("auth/register.html")

        user = User(
            email=email,
            password_hash=hash_password(password),
            role=role,
        )
        db.session.add(user)
        db.session.flush()

        if role == "student":
            full_name = request.form.get("full_name", "").strip() or email.split("@")[0]
            profile = StudentProfile(user_id=user.id, full_name=full_name)
            db.session.add(profile)
        else:
            company_name = request.form.get("company_name", "").strip() or "My Company"
            profile = CompanyProfile(user_id=user.id, company_name=company_name)
            db.session.add(profile)

        db.session.commit()
        flash("Registration successful! Please log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(_dashboard_url(current_user))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        remember = request.form.get("remember") == "on"

        user = User.query.filter_by(email=email).first()

        if not user or not check_password(password, user.password_hash):
            flash("Invalid email or password.", "error")
            return render_template("auth/login.html")

        if not user.is_active:
            flash("Your account has been deactivated. Contact support.", "error")
            return render_template("auth/login.html")

        login_user(user, remember=remember)
        flash(f"Welcome back, {user.email}!", "success")
        next_page = request.args.get("next")
        if next_page:
            return redirect(next_page)
        return redirect(_dashboard_url(user))

    return render_template("auth/login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "success")
    return redirect(url_for("index"))


def _dashboard_url(user):
    if user.is_admin:
        return url_for("admin.dashboard")
    if user.is_company:
        return url_for("jobs.company_dashboard")
    return url_for("students.dashboard")
