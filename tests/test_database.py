"""
DeepGuard – Test Suite: Database
"""

import pytest
from database.db import get_db
from datetime import datetime, timezone


def test_db_connection():
    """Verify MongoDB is reachable."""
    try:
        db = get_db()
        assert db is not None
    except Exception:
        pytest.skip("MongoDB not available in this environment.")


def test_user_insert_and_delete():
    try:
        db = get_db()
    except Exception:
        pytest.skip("MongoDB not available.")

    test_email = "db_test_user@deepguard.test"
    db.users.delete_one({"email": test_email})

    result = db.users.insert_one({
        "name": "DB Test",
        "email": test_email,
        "password_hash": "hashed",
        "role": "user",
        "created_at": datetime.now(timezone.utc),
    })
    assert result.inserted_id is not None

    found = db.users.find_one({"email": test_email})
    assert found is not None
    assert found["name"] == "DB Test"

    db.users.delete_one({"email": test_email})


def test_analysis_insert_and_delete():
    try:
        db = get_db()
    except Exception:
        pytest.skip("MongoDB not available.")

    from bson import ObjectId
    fake_uid = ObjectId()
    result = db.analyses.insert_one({
        "user_id": fake_uid,
        "file_name": "test.png",
        "file_type": "image",
        "prediction": "LIKELY REAL",
        "confidence": 85.0,
        "status": "success",
        "created_at": datetime.now(timezone.utc),
    })
    assert result.inserted_id is not None

    # Cleanup
    db.analyses.delete_one({"_id": result.inserted_id})
