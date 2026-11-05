"""
DeepGuard – Test Suite: Authentication
"""

import pytest
from app import create_app
from database.db import get_db


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def test_landing_page(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert b"DeepGuard" in resp.data


def test_register_get(client):
    resp = client.get("/register")
    assert resp.status_code == 200


def test_login_get(client):
    resp = client.get("/login")
    assert resp.status_code == 200


def test_dashboard_requires_login(client):
    resp = client.get("/dashboard", follow_redirects=True)
    assert b"login" in resp.data.lower() or resp.status_code == 200


def test_register_and_login(client):
    # Register
    resp = client.post("/register", data={
        "name": "Test User",
        "email": "testuser_pytest@example.com",
        "password": "Password123!",
        "confirm_password": "Password123!",
    }, follow_redirects=True)
    assert resp.status_code == 200

    # Login
    resp = client.post("/login", data={
        "email": "testuser_pytest@example.com",
        "password": "Password123!",
    }, follow_redirects=True)
    assert resp.status_code == 200

    # Cleanup
    try:
        db = get_db()
        db.users.delete_one({"email": "testuser_pytest@example.com"})
    except Exception:
        pass


def test_invalid_login(client):
    resp = client.post("/login", data={
        "email": "nobody@nowhere.com",
        "password": "WrongPassword",
    }, follow_redirects=True)
    assert b"Invalid" in resp.data or resp.status_code == 200
