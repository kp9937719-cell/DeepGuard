"""
DeepGuard - Main Flask Application Entry Point.
"""

import os
import logging
from flask import Flask, render_template, send_from_directory, abort
from flask_login import LoginManager, UserMixin, current_user
from flask_cors import CORS
from bson import ObjectId
from config import Config
from database.db import get_db

# Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


class DeepGuardUser(UserMixin):
    """Thin wrapper around a MongoDB user document for Flask-Login."""

    def __init__(self, user_doc: dict):
        self.id = str(user_doc["_id"])
        self.name = user_doc.get("name", "")
        self.email = user_doc.get("email", "")
        self.role = user_doc.get("role", "user")

    def get_id(self):
        return self.id


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)
    app.secret_key = Config.SECRET_KEY

    CORS(app)

    # Ensure upload and report directories exist
    os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(Config.REPORTS_FOLDER, exist_ok=True)

    # Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Please log in to access this page."
    login_manager.login_message_category = "info"

    @login_manager.user_loader
    def load_user(user_id: str):
        try:
            db = get_db()
            doc = db.users.find_one({"_id": ObjectId(user_id)})
            if doc:
                return DeepGuardUser(doc)
        except Exception as exc:
            logger.error("load_user error: %s", exc)
        return None

    # Blueprint registration
    from routes.auth_routes import auth_bp
    from routes.dashboard_routes import dashboard_bp
    from routes.image_routes import image_bp
    from routes.video_routes import video_bp
    from routes.result_routes import result_bp
    from routes.history_routes import history_bp
    from routes.report_routes import report_bp
    from routes.profile_routes import profile_bp
    from routes.admin_routes import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(image_bp)
    app.register_blueprint(video_bp)
    app.register_blueprint(result_bp)
    app.register_blueprint(history_bp)
    app.register_blueprint(report_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(admin_bp)

    # Landing page
    @app.route("/")
    def index():
        return render_template("index.html")

    # Serve uploaded files (user-isolated access)
    @app.route("/uploads/<user_id>/<filename>")
    def serve_upload(user_id, filename):
        """Serve an uploaded file. Only the owning user may access it."""
        if not current_user.is_authenticated or str(current_user.id) != user_id:
            abort(403)
        upload_dir = os.path.join(Config.UPLOAD_FOLDER, user_id)
        return send_from_directory(upload_dir, filename)

    # Error handlers
    @app.errorhandler(403)
    def forbidden(e):
        return render_template("errors/403.html"), 403

    @app.errorhandler(404)
    def not_found(e):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def server_error(e):
        logger.error("500 error: %s", e)
        return render_template("errors/500.html"), 500

    return app


# Entry point
app = create_app()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
