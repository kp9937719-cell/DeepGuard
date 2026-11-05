"""
DeepGuard Configuration Module
Loads settings from environment variables / .env file.
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # ── Core Flask ──────────────────────────────────────────────
    SECRET_KEY = os.getenv("SECRET_KEY", "deepguard-fallback-secret")
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"

    # ── MongoDB ─────────────────────────────────────────────────
    MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
    DATABASE_NAME = os.getenv("DATABASE_NAME", "deepguard_db")

    # ── File uploads ────────────────────────────────────────────
    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "uploads")
    REPORTS_FOLDER = os.getenv("REPORTS_FOLDER", "reports")
    MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", 100 * 1024 * 1024))  # 100 MB

    ALLOWED_IMAGE_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}
    ALLOWED_VIDEO_EXTENSIONS = {"mp4", "avi", "mov", "mkv"}

    # ── Model settings ──────────────────────────────────────────
    MODEL_DIR = "models"
    IMAGE_MODEL_PATH = os.path.join(MODEL_DIR, "image_detector.keras")
    VIDEO_MODEL_PATH = os.path.join(MODEL_DIR, "video_detector.keras")
    IMAGE_MODEL_INPUT_SIZE = (224, 224)
    VIDEO_FRAME_SAMPLE_RATE = 30   # analyse every 30th frame
    VIDEO_MAX_FRAMES = 100         # cap frames analysed per video
