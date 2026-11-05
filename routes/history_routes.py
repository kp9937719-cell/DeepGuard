"""
DeepGuard – Analysis history routes.
"""

from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from services.analysis_service import get_user_analyses

history_bp = Blueprint("history", __name__)
PAGE_SIZE = 15


@history_bp.route("/history")
@login_required
def index():
    page = max(1, int(request.args.get("page", 1)))
    filter_pred = request.args.get("filter", "all")
    search = request.args.get("search", "").strip()

    skip = (page - 1) * PAGE_SIZE
    analyses = get_user_analyses(
        str(current_user.id),
        limit=PAGE_SIZE,
        skip=skip,
        filter_prediction=filter_pred if filter_pred != "all" else None,
    )

    # Basic search filter in Python (MongoDB text index can be added later)
    if search:
        analyses = [a for a in analyses if search.lower() in (a.get("file_name") or "").lower()]

    return render_template(
        "history.html",
        analyses=analyses,
        page=page,
        filter_pred=filter_pred,
        search=search,
        page_size=PAGE_SIZE,
    )
