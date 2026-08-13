import uuid

import pytest
from fastapi.testclient import TestClient

from app.db.session import SessionLocal
from app.main import app
from app.models.user import User

client = TestClient(app)


@pytest.fixture
def test_user_credentials():
    email = f"{uuid.uuid4()}@example.com"
    password = "S3curePassw0rd!"
    yield {"email": email, "password": password}
    db = SessionLocal()
    db.query(User).filter(User.email == email).delete()
    db.commit()
    db.close()


def test_register_creates_user(test_user_credentials):
    response = client.post("/api/v1/auth/register", json=test_user_credentials)
    assert response.status_code == 201
    body = response.json()
    assert body["email"] == test_user_credentials["email"]
    assert "hashed_password" not in body
    assert "password" not in body


def test_register_rejects_duplicate_email(test_user_credentials):
    client.post("/api/v1/auth/register", json=test_user_credentials)
    response = client.post("/api/v1/auth/register", json=test_user_credentials)
    assert response.status_code == 409


def test_login_returns_token_for_valid_credentials(test_user_credentials):
    client.post("/api/v1/auth/register", json=test_user_credentials)
    response = client.post("/api/v1/auth/login", json=test_user_credentials)
    assert response.status_code == 200
    body = response.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"


def test_login_rejects_wrong_password(test_user_credentials):
    client.post("/api/v1/auth/register", json=test_user_credentials)
    response = client.post(
        "/api/v1/auth/login",
        json={"email": test_user_credentials["email"], "password": "wrong-password"},
    )
    assert response.status_code == 401


def test_me_returns_current_user_with_valid_token(test_user_credentials):
    client.post("/api/v1/auth/register", json=test_user_credentials)
    login_response = client.post("/api/v1/auth/login", json=test_user_credentials)
    token = login_response.json()["access_token"]

    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["email"] == test_user_credentials["email"]


def test_me_rejects_missing_token():
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401


def test_me_rejects_invalid_token():
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer not-a-real-token"},
    )
    assert response.status_code == 401