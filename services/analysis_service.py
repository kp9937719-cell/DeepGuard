"""
DeepGuard – Analysis service.
Persists analysis records and provides retrieval helpers.
"""

import logging
from datetime import datetime, timezone
from bson import ObjectId
from database.db import get_db

logger = logging.getLogger(__name__)


def save_analysis(user_id: str, file_info: dict, prediction_result: dict) -> str:
    """
    Persist an analysis record in MongoDB.
    Returns the string form of the inserted _id.
    """
    db = get_db()
    doc = {
        "user_id": ObjectId(user_id),
        "file_name": file_info.get("file_name"),
        "file_type": file_info.get("file_type"),          # "image" | "video"
        "file_format": file_info.get("file_format"),
        "file_size": file_info.get("file_size"),
        "file_hash": file_info.get("file_hash"),
        "file_path": file_info.get("file_path"),
        "prediction": prediction_result.get("prediction"),
        "confidence": prediction_result.get("confidence"),
        "real_probability": prediction_result.get("real_probability"),
        "fake_probability": prediction_result.get("fake_probability"),
        "risk": prediction_result.get("risk"),
        "model_name": prediction_result.get("model_name"),
        "model_version": prediction_result.get("model_version"),
        "processing_time": prediction_result.get("processing_time"),
        "frame_analysis": prediction_result.get("frame_results"),       # video only
        "video_info": prediction_result.get("video_info"),              # video only
        "image_metadata": prediction_result.get("image_metadata"),      # image only
        "status": prediction_result.get("status"),
        "is_demo": prediction_result.get("is_demo", False),
        "message": prediction_result.get("message"),
        "created_at": datetime.now(timezone.utc),
    }
    result = db.analyses.insert_one(doc)
    return str(result.inserted_id)


def get_analysis_by_id(analysis_id: str, user_id: str) -> dict | None:
    """Fetch one analysis; returns None if not found or not owned by user."""
    db = get_db()
    try:
        doc = db.analyses.find_one({
            "_id": ObjectId(analysis_id),
            "user_id": ObjectId(user_id),
        })
        if doc:
            doc["_id"] = str(doc["_id"])
            doc["user_id"] = str(doc["user_id"])
        return doc
    except Exception as exc:
        logger.error("get_analysis_by_id error: %s", exc)
        return None


def get_user_analyses(user_id: str, limit: int = 50, skip: int = 0,
                      filter_prediction: str = None) -> list:
    """Return paginated analyses for a user, optionally filtered."""
    db = get_db()
    query = {"user_id": ObjectId(user_id)}
    if filter_prediction and filter_prediction != "all":
        query["prediction"] = {"$regex": filter_prediction, "$options": "i"}

    cursor = db.analyses.find(query).sort("created_at", -1).skip(skip).limit(limit)
    results = []
    for doc in cursor:
        doc["_id"] = str(doc["_id"])
        doc["user_id"] = str(doc["user_id"])
        results.append(doc)
    return results


def get_user_stats(user_id: str) -> dict:
    """Compute dashboard statistics from MongoDB for a specific user."""
    db = get_db()
    uid = ObjectId(user_id)

    total = db.analyses.count_documents({"user_id": uid})
    images = db.analyses.count_documents({"user_id": uid, "file_type": "image"})
    videos = db.analyses.count_documents({"user_id": uid, "file_type": "video"})
    real = db.analyses.count_documents({
        "user_id": uid, "prediction": {"$regex": "REAL", "$options": "i"}
    })
    fake = db.analyses.count_documents({
        "user_id": uid,
        "prediction": {"$regex": "AI-GENERATED|DEEPFAKE|MANIPULATED", "$options": "i"}
    })
    inconclusive = db.analyses.count_documents({
        "user_id": uid, "prediction": {"$regex": "INCONCLUSIVE", "$options": "i"}
    })
    reports = db.reports.count_documents({"user_id": uid})

    return {
        "total_analyses": total,
        "total_images": images,
        "total_videos": videos,
        "total_real": real,
        "total_fake": fake,
        "total_inconclusive": inconclusive,
        "total_reports": reports,
    }


def get_weekly_activity(user_id: str) -> list:
    """Return count of analyses per day for the last 7 days."""
    from datetime import timedelta
    db = get_db()
    uid = ObjectId(user_id)
    today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    result = []
    for i in range(6, -1, -1):
        day_start = today - timedelta(days=i)
        day_end = day_start + timedelta(days=1)
        count = db.analyses.count_documents({
            "user_id": uid,
            "created_at": {"$gte": day_start, "$lt": day_end},
        })
        result.append({"date": day_start.strftime("%a"), "count": count})
    return result
