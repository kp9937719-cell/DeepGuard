"""
DeepGuard - Image detection routes.
"""

import os
import logging
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from config import Config
from services.image_prediction import predict_image
from services.hash_service import compute_sha256
from services.analysis_service import save_analysis

logger = logging.getLogger(__name__)
image_bp = Blueprint("image", __name__)


def _allowed_image(filename: str) -> bool:
    return "." in filename and \
           filename.rsplit(".", 1)[1].lower() in Config.ALLOWED_IMAGE_EXTENSIONS


@image_bp.route("/image-detection")
@login_required
def upload_page():
    return render_template("image_detection.html")


@image_bp.route("/image-detection/analyze", methods=["POST"])
@login_required
def analyze():
    if "file" not in request.files:
        flash("No file selected.", "error")
        return redirect(url_for("image.upload_page"))

    file = request.files["file"]
    if not file or file.filename == "":
        flash("No file selected.", "error")
        return redirect(url_for("image.upload_page"))

    if not _allowed_image(file.filename):
        flash(
            f"Unsupported file type. Allowed: {', '.join(Config.ALLOWED_IMAGE_EXTENSIONS).upper()}",
            "error"
        )
        return redirect(url_for("image.upload_page"))

    # Check content length
    file.seek(0, 2)
    size = file.tell()
    file.seek(0)
    if size > Config.MAX_CONTENT_LENGTH:
        flash("File too large. Maximum allowed size is 100 MB.", "error")
        return redirect(url_for("image.upload_page"))

    filename = secure_filename(file.filename)
    upload_dir = os.path.join(Config.UPLOAD_FOLDER, str(current_user.id))
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, filename)
    file.save(file_path)

    file_size = os.path.getsize(file_path)
    file_hash = compute_sha256(file_path)
    file_format = filename.rsplit(".", 1)[1].lower()

    try:
        from services.metadata_analysis import analyse_metadata
        meta_info = analyse_metadata(file_path)
    except Exception as exc:
        logger.warning("Could not extract image metadata: %s", exc)
        meta_info = {}

    try:
        result = predict_image(file_path)
        if "image_metadata" not in result:
            result["image_metadata"] = meta_info
    except Exception as exc:
        logger.error("Image prediction error: %s", exc)
        result = {
            "status": "prediction_error",
            "message": f"An error occurred during prediction: {exc}",
        }

    file_info = {
        "file_name": filename,
        "file_type": "image",
        "file_format": file_format,
        "file_size": file_size,
        "file_hash": file_hash,
        "file_path": file_path,
    }

    analysis_id = save_analysis(str(current_user.id), file_info, result)
    return redirect(url_for("result.show", analysis_id=analysis_id))
