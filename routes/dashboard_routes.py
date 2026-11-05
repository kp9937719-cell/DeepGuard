"""
DeepGuard – Dashboard routes.
"""

from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from services.analysis_service import get_user_stats, get_weekly_activity, get_user_analyses

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/dashboard")
@login_required
def index():
    stats = get_user_stats(str(current_user.id))
    recent = get_user_analyses(str(current_user.id), limit=10)
    return render_template("dashboard.html", stats=stats, recent=recent)


@dashboard_bp.route("/api/dashboard/weekly-activity")
@login_required
def weekly_activity():
    data = get_weekly_activity(str(current_user.id))
    return jsonify(data)


@dashboard_bp.route("/api/dashboard/stats")
@login_required
def stats_api():
    stats = get_user_stats(str(current_user.id))
    return jsonify(stats)
