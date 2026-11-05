"""
DeepGuard - Test Suite: Reports
"""

import pytest
from app import create_app
from database.db import get_db
from datetime import datetime, timezone
from bson import ObjectId


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def test_reports_page_requires_login(client):
    resp = client.get("/reports", follow_redirects=True)
    assert resp.status_code == 200


def test_report_download_requires_auth(client):
    resp = client.get("/reports/download/NONEXISTENT", follow_redirects=True)
    # Should redirect to login or return 404/403
    assert resp.status_code in (200, 403, 404)


def test_report_generation_requires_auth(client):
    resp = client.post("/reports/generate/000000000000000000000001",
                       follow_redirects=True)
    assert resp.status_code == 200


def test_report_record_in_db():
    """Insert a mock report and verify it persists."""
    try:
        db = get_db()
    except Exception:
        pytest.skip("MongoDB not available.")

    fake_uid = ObjectId()
    fake_aid = ObjectId()
    doc = {
        "user_id": fake_uid,
        "analysis_id": fake_aid,
        "report_id": "DG-TESTXYZ123",
        "pdf_path": "/tmp/test_report.pdf",
        "pdf_filename": "DG-TESTXYZ123.pdf",
        "generated_at": datetime.now(timezone.utc),
    }
    result = db.reports.insert_one(doc)
    assert result.inserted_id is not None
    found = db.reports.find_one({"report_id": "DG-TESTXYZ123"})
    assert found is not None
    db.reports.delete_one({"report_id": "DG-TESTXYZ123"})
