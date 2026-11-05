"""
DeepGuard – Analysis result route.
"""

from flask import Blueprint, render_template, abort
from flask_login import login_required, current_user
from services.analysis_service import get_analysis_by_id

result_bp = Blueprint("result", __name__)


@result_bp.route("/result/<analysis_id>")
@login_required
def show(analysis_id):
    analysis = get_analysis_by_id(analysis_id, str(current_user.id))
    if not analysis:
        abort(404)
    return render_template("result.html", analysis=analysis)
