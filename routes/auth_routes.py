"""
DeepGuard – Authentication routes.
Handles registration, login, logout, and password-change.
"""

import logging
from datetime import datetime, timezone
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from bson import ObjectId
from database.db import get_db

logger = logging.getLogger(__name__)
auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")

        # Validation
        if not all([name, email, password, confirm]):
            flash("All fields are required.", "error")
            return render_template("register.html")
        if password != confirm:
            flash("Passwords do not match.", "error")
            return render_template("register.html")
        if len(password) < 8:
            flash("Password must be at least 8 characters.", "error")
            return render_template("register.html")

        db = get_db()
        if db.users.find_one({"email": email}):
            flash("An account with this email already exists.", "error")
            return render_template("register.html")

        password_hash = generate_password_hash(password)
        user_doc = {
            "name": name,
            "email": email,
            "password_hash": password_hash,
            "role": "user",
            "created_at": datetime.now(timezone.utc),
        }
        result = db.users.insert_one(user_doc)
        logger.info("New user registered: %s", email)
        flash("Account created successfully! Please log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        remember = bool(request.form.get("remember"))

        if not email or not password:
            flash("Email and password are required.", "error")
            return render_template("login.html")

        db = get_db()
        user_doc = db.users.find_one({"email": email})

        if not user_doc or not check_password_hash(user_doc["password_hash"], password):
            flash("Invalid email or password.", "error")
            return render_template("login.html")

        from app import DeepGuardUser
        user_obj = DeepGuardUser(user_doc)
        login_user(user_obj, remember=remember)
        logger.info("User logged in: %s", email)

        next_page = request.args.get("next")
        return redirect(next_page or url_for("dashboard.index"))

    return render_template("login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))


@auth_bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    """Placeholder – implement email reset in production."""
    if request.method == "POST":
        flash("Password reset functionality requires email configuration. Please contact support.", "info")
    return render_template("login.html")
