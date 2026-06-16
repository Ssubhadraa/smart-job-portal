from functools import wraps

from flask import abort
from flask_login import current_user


def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(403)
            if current_user.role not in roles:
                abort(403)
            if not current_user.is_active:
                abort(403)
            return f(*args, **kwargs)

        return wrapped

    return decorator


def admin_required(f):
    return role_required("admin")(f)


def student_required(f):
    return role_required("student")(f)


def company_required(f):
    return role_required("company")(f)
