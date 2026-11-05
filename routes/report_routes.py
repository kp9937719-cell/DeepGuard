"""
DeepGuard – Report routes.
"""

import os
import logging
from flask import Blueprint, render_template, request, send_file, flash, redirect, url_for, abort
from flask_login import login_required, current_user
from bson import ObjectId
from database.db import get_db
from services.analysis_service import get_analysis_by_id
from services.report_generator import generate_report, save_report_record
from config import Config

logger = logging.getLogger(__name__)
report_bp = Blueprint("report", __name__)
PAGE_SIZE = 15


@report_bp.route("/reports")
@login_required
def index():
    db = get_db()
    page = max(1, int(request.args.get("page", 1)))
    search = request.args.get("search", "").strip()
    filter_status = request.args.get("status", "all")

    skip = (page - 1) * PAGE_SIZE
    query = {"user_id": ObjectId(str(current_user.id))}

    cursor = db.reports.find(query).sort("generated_at", -1).skip(skip).limit(PAGE_SIZE)
    reports = []
    for doc in cursor:
        doc["_id"] = str(doc["_id"])
        doc["user_id"] = str(doc["user_id"])
        doc["analysis_id"] = str(doc["analysis_id"])
        # Fetch prediction from analysis
        try:
            analysis = db.analyses.find_one({"_id": ObjectId(doc["analysis_id"])})
            if analysis:
                doc["prediction"] = analysis.get("prediction", "N/A")
                doc["confidence"] = analysis.get("confidence", 0)
                doc["file_name"] = analysis.get("file_name", "N/A")
                doc["file_type"] = analysis.get("file_type", "N/A")
        except Exception:
            pass
        reports.append(doc)

    # Python-level search on file_name
    if search:
        reports = [r for r in reports if search.lower() in (r.get("file_name") or "").lower()]
    if filter_status != "all":
        reports = [r for r in reports
                   if filter_status.upper() in (r.get("prediction") or "").upper()]

    return render_template("reports.html", reports=reports, page=page,
                           search=search, filter_status=filter_status)


@report_bp.route("/reports/generate/<analysis_id>", methods=["POST"])
@login_required
def generate(analysis_id):
    analysis = get_analysis_by_id(analysis_id, str(current_user.id))
    if not analysis:
        abort(404)

    # Allow both successful and demo analyses to generate reports
    allowed_statuses = {"success", "demo"}
    if analysis.get("status") not in allowed_statuses and not analysis.get("is_demo"):
        flash("Cannot generate report for an incomplete or failed analysis.", "error")
        return redirect(url_for("result.show", analysis_id=analysis_id))

    db = get_db()
    user_doc = db.users.find_one({"_id": ObjectId(str(current_user.id))})
    user = {"name": user_doc.get("name", ""), "email": user_doc.get("email", "")}

    try:
        report_data = generate_report(analysis, user, Config.REPORTS_FOLDER)
        save_report_record(db, str(current_user.id), analysis_id, report_data)
        flash("PDF report generated successfully!", "success")
        return redirect(url_for("report.download", report_id=report_data["report_id"]))
    except Exception as exc:
        logger.error("Report generation failed: %s", exc)
        flash(f"Report generation failed: {exc}", "error")
        return redirect(url_for("result.show", analysis_id=analysis_id))


@report_bp.route("/reports/download/<report_id>")
@login_required
def download(report_id):
    db = get_db()
    doc = db.reports.find_one({
        "report_id": report_id,
        "user_id": ObjectId(str(current_user.id)),
    })
    if not doc:
        abort(404)

    pdf_path = doc.get("pdf_path")
    if not pdf_path or not os.path.exists(pdf_path):
        abort(404)

    return send_file(pdf_path, as_attachment=True,
                     download_name=f"DeepGuard_{report_id}.pdf",
                     mimetype="application/pdf")
