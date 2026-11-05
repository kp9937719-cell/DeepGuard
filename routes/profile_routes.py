"""
DeepGuard – Profile settings routes.
"""

from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from bson import ObjectId
from database.db import get_db

profile_bp = Blueprint("profile", __name__)


@profile_bp.route("/profile")
@login_required
def index():
    return render_template("profile.html")


@profile_bp.route("/profile/update", methods=["POST"])
@login_required
def update():
    name = request.form.get("name", "").strip()
    if not name:
        flash("Name cannot be empty.", "error")
        return redirect(url_for("profile.index"))

    db = get_db()
    db.users.update_one(
        {"_id": ObjectId(str(current_user.id))},
        {"$set": {"name": name}},
    )
    current_user.name = name
    flash("Profile updated successfully.", "success")
    return redirect(url_for("profile.index"))


@profile_bp.route("/profile/change-password", methods=["POST"])
@login_required
def change_password():
    current_pw = request.form.get("current_password", "")
    new_pw = request.form.get("new_password", "")
    confirm_pw = request.form.get("confirm_password", "")

    db = get_db()
    user_doc = db.users.find_one({"_id": ObjectId(str(current_user.id))})

    if not check_password_hash(user_doc["password_hash"], current_pw):
        flash("Current password is incorrect.", "error")
        return redirect(url_for("profile.index"))
    if new_pw != confirm_pw:
        flash("New passwords do not match.", "error")
        return redirect(url_for("profile.index"))
    if len(new_pw) < 8:
        flash("Password must be at least 8 characters.", "error")
        return redirect(url_for("profile.index"))

    db.users.update_one(
        {"_id": ObjectId(str(current_user.id))},
        {"$set": {"password_hash": generate_password_hash(new_pw)}},
    )
    flash("Password changed successfully.", "success")
    return redirect(url_for("profile.index"))
