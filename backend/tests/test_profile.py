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


def test_get_profile_creates_blank_profile_on_first_access(authenticated_user):
    response = client.get("/api/v1/profile/me", headers=authenticated_user["headers"])
    assert response.status_code == 200
    body = response.json()
    assert body["full_name"] is None
    assert body["academic_level"] is None
    assert body["subjects"] == []


def test_update_profile_persists_fields(authenticated_user):
    payload = {
        "full_name": "Alvin Njoroge",
        "academic_level": "undergraduate",
        "institution": "University of Nairobi",
        "program": "Bachelor of Business Information Technology",
        "subjects": ["Databases", "Software Engineering"],
        "academic_goals": "Graduate with first class honours",
    }
    response = client.patch(
        "/api/v1/profile/me", json=payload, headers=authenticated_user["headers"]
    )
    assert response.status_code == 200
    body = response.json()
    assert body["full_name"] == "Alvin Njoroge"
    assert body["academic_level"] == "undergraduate"
    assert body["subjects"] == ["Databases", "Software Engineering"]

    follow_up = client.get("/api/v1/profile/me", headers=authenticated_user["headers"])
    assert follow_up.json()["institution"] == "University of Nairobi"


def test_update_profile_rejects_invalid_academic_level(authenticated_user):
    response = client.patch(
        "/api/v1/profile/me",
        json={"academic_level": "not-a-real-level"},
        headers=authenticated_user["headers"],
    )
    assert response.status_code == 422


def test_update_profile_creates_matching_subjects(authenticated_user):
    response = client.patch(
        "/api/v1/profile/me",
        json={"subjects": ["Databases", "Software Engineering"]},
        headers=authenticated_user["headers"],
    )
    assert response.status_code == 200

    subjects_response = client.get("/api/v1/subjects", headers=authenticated_user["headers"])
    assert subjects_response.status_code == 200
    names = {subject["name"] for subject in subjects_response.json()}
    assert {"Databases", "Software Engineering"}.issubset(names)

    created_subject = next(
        subject for subject in subjects_response.json() if subject["name"] == "Databases"
    )
    assert created_subject["priority"] == "medium"
    assert created_subject["description"] is None


def test_update_profile_does_not_duplicate_existing_subjects(authenticated_user):
    client.post("/api/v1/subjects", json={"name": "Databases"}, headers=authenticated_user["headers"])

    client.patch(
        "/api/v1/profile/me",
        json={"subjects": ["databases", "New Subject"]},
        headers=authenticated_user["headers"],
    )

    subjects_response = client.get("/api/v1/subjects", headers=authenticated_user["headers"])
    names = [subject["name"] for subject in subjects_response.json()]
    assert names.count("Databases") == 1
    assert "New Subject" in names


def test_update_profile_does_not_remove_subjects_when_list_shrinks(authenticated_user):
    client.patch(
        "/api/v1/profile/me",
        json={"subjects": ["Databases", "Software Engineering"]},
        headers=authenticated_user["headers"],
    )
    client.patch(
        "/api/v1/profile/me",
        json={"subjects": ["Databases"]},
        headers=authenticated_user["headers"],
    )

    subjects_response = client.get("/api/v1/subjects", headers=authenticated_user["headers"])
    names = {subject["name"] for subject in subjects_response.json()}
    assert {"Databases", "Software Engineering"}.issubset(names)


def test_profile_requires_authentication():
    response = client.get("/api/v1/profile/me")
    assert response.status_code == 401