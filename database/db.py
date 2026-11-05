"""
DeepGuard – MongoDB connection and collection helpers.
"""

from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import ConnectionFailure
from config import Config
import logging

logger = logging.getLogger(__name__)

_client = None
_db = None


def get_db():
    """Return a live MongoDB database handle (lazy singleton)."""
    global _client, _db
    if _db is None:
        try:
            _client = MongoClient(Config.MONGODB_URI, serverSelectionTimeoutMS=5000)
            _client.admin.command("ping")  # raises ConnectionFailure if down
            _db = _client[Config.DATABASE_NAME]
            _ensure_indexes(_db)
            logger.info("MongoDB connected – database: %s", Config.DATABASE_NAME)
        except ConnectionFailure as exc:
            logger.error("MongoDB connection failed: %s", exc)
            raise
    return _db


def _ensure_indexes(db):
    """Create indexes once on first connection."""
    db.users.create_index([("email", ASCENDING)], unique=True)
    db.analyses.create_index([("user_id", ASCENDING), ("created_at", DESCENDING)])
    db.analyses.create_index([("file_hash", ASCENDING)])
    db.reports.create_index([("user_id", ASCENDING), ("generated_at", DESCENDING)])
    db.reports.create_index([("report_id", ASCENDING)], unique=True)
    db.model_versions.create_index([("model_name", ASCENDING)])
