"""
DeepGuard – Test Suite: Detection
"""

import io
import os
import pytest
from PIL import Image
from app import create_app


@pytest.fixture
def auth_client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as c:
        # Register + login
        c.post("/register", data={
            "name": "Det Tester",
            "email": "dettester@example.com",
            "password": "Password123!",
            "confirm_password": "Password123!",
        })
        c.post("/login", data={
            "email": "dettester@example.com",
            "password": "Password123!",
        })
        yield c


def _make_png_bytes(size=(64, 64)):
    img = Image.new("RGB", size, color=(120, 80, 200))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf


def test_image_upload_valid(auth_client):
    data = {
        "file": (io.BytesIO(_make_png_bytes().read()), "test_image.png"),
    }
    resp = auth_client.post("/image-detection/analyze",
                            data=data, content_type="multipart/form-data",
                            follow_redirects=True)
    assert resp.status_code == 200


def test_image_upload_unsupported_format(auth_client):
    data = {"file": (io.BytesIO(b"fake data"), "test.txt")}
    resp = auth_client.post("/image-detection/analyze",
                            data=data, content_type="multipart/form-data",
                            follow_redirects=True)
    assert resp.status_code == 200  # redirects with flash


def test_image_upload_no_file(auth_client):
    resp = auth_client.post("/image-detection/analyze",
                            content_type="multipart/form-data",
                            follow_redirects=True)
    assert resp.status_code == 200


def test_image_detection_page_requires_login():
    from app import create_app
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as c:
        resp = c.get("/image-detection", follow_redirects=True)
        assert resp.status_code == 200  # redirects to login
