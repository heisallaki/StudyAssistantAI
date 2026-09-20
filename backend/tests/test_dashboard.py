import uuid

import pytest
from fastapi.testclient import TestClient

from app.db.session import SessionLocal
from app.main import app
from app.models.user import User

client = TestClient(app)


@pytest.fixture
def authenticated_user():
    email = f"{uuid.uuid4()}@example.com"
    password = "S3curePassw0rd!"
    client.post("/api/v1/auth/register", json={"email": email, "password": password})
    login_response = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    token = login_response.json()["access_token"]

    yield {"headers": {"Authorization": f"Bearer {token}"}, "email": email}

    db = SessionLocal()
    db.query(User).filter(User.email == email).delete()
    db.commit()
    db.close()


def test_dashboard_overview_for_new_user_shows_zero_percent_completion(authenticated_user):
    response = client.get("/api/v1/dashboard/overview", headers=authenticated_user["headers"])
    assert response.status_code == 200
    body = response.json()
    assert body["profile_completion_percentage"] == 0
    assert set(body["profile_completion_missing_fields"]) == {
        "full_name",
        "academic_level",
        "institution",
        "program",
        "subjects",
        "academic_goals",
    }
    assert body["account_age_days"] == 0


def test_dashboard_overview_reflects_profile_updates(authenticated_user):
    client.patch(
        "/api/v1/profile/me",
        json={
            "full_name": "Alvin Njoroge",
            "academic_level": "undergraduate",
            "institution": "University of Nairobi",
        },
        headers=authenticated_user["headers"],
    )

    response = client.get("/api/v1/dashboard/overview", headers=authenticated_user["headers"])
    assert response.status_code == 200
    body = response.json()
    assert body["profile_completion_percentage"] == 50
    assert "full_name" not in body["profile_completion_missing_fields"]
    assert "program" in body["profile_completion_missing_fields"]


def test_dashboard_overview_requires_authentication():
    response = client.get("/api/v1/dashboard/overview")
    assert response.status_code == 401