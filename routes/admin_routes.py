"""
DeepGuard – Admin dashboard routes.
Access restricted to users with role == "admin".
"""

from functools import wraps
from flask import Blueprint, render_template, abort, request
from flask_login import login_required, current_user
from bson import ObjectId
from database.db import get_db
from models.model_loader import get_model_status

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


def admin_required(f):
    @wraps(f)
    @login_required
    def decorated(*args, **kwargs):
        if current_user.role != "admin":
            abort(403)
        return f(*args, **kwargs)
    return decorated


@admin_bp.route("/")
@admin_required
def index():
    db = get_db()

    stats = {
        "total_users": db.users.count_documents({}),
        "total_analyses": db.analyses.count_documents({}),
        "total_images": db.analyses.count_documents({"file_type": "image"}),
        "total_videos": db.analyses.count_documents({"file_type": "video"}),
        "total_real": db.analyses.count_documents({"prediction": {"$regex": "REAL", "$options": "i"}}),
        "total_fake": db.analyses.count_documents({"prediction": {"$regex": "AI-GENERATED|DEEPFAKE|MANIPULATED", "$options": "i"}}),
        "total_inconclusive": db.analyses.count_documents({"prediction": {"$regex": "INCONCLUSIVE", "$options": "i"}}),
        "total_reports": db.reports.count_documents({}),
    }

    recent_analyses = list(db.analyses.find({}).sort("created_at", -1).limit(20))
    for a in recent_analyses:
        a["_id"] = str(a["_id"])
        a["user_id"] = str(a["user_id"])

    model_status = get_model_status()

    return render_template("admin_dashboard.html", stats=stats,
                           recent_analyses=recent_analyses,
                           model_status=model_status)


@admin_bp.route("/users")
@admin_required
def users():
    db = get_db()
    page = max(1, int(request.args.get("page", 1)))
    per_page = 20
    skip = (page - 1) * per_page
    all_users = list(db.users.find({}, {"password_hash": 0}).skip(skip).limit(per_page))
    for u in all_users:
        u["_id"] = str(u["_id"])
    total = db.users.count_documents({})
    return render_template("admin_users.html", users=all_users, page=page,
                           total=total, per_page=per_page)
