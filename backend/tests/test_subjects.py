import uuid

import pytest
from fastapi.testclient import TestClient

from app.db.session import SessionLocal
from app.main import app
from app.models.user import User

client = TestClient(app)


def _register_and_login():
    email = f"{uuid.uuid4()}@example.com"
    password = "S3curePassw0rd!"
    client.post("/api/v1/auth/register", json={"email": email, "password": password})
    login_response = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    token = login_response.json()["access_token"]
    return {"email": email, "headers": {"Authorization": f"Bearer {token}"}}


@pytest.fixture
def authenticated_user():
    user = _register_and_login()
    yield user
    db = SessionLocal()
    db.query(User).filter(User.email == user["email"]).delete()
    db.commit()
    db.close()


@pytest.fixture
def other_authenticated_user():
    user = _register_and_login()
    yield user
    db = SessionLocal()
    db.query(User).filter(User.email == user["email"]).delete()
    db.commit()
    db.close()


def test_list_subjects_starts_empty(authenticated_user):
    response = client.get("/api/v1/subjects", headers=authenticated_user["headers"])
    assert response.status_code == 200
    assert response.json() == []


def test_create_subject(authenticated_user):
    response = client.post(
        "/api/v1/subjects",
        json={"name": "Databases", "description": "Relational and NoSQL systems", "color": "#4287f5"},
        headers=authenticated_user["headers"],
    )
    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "Databases"
    assert body["topic_count"] == 0
    assert body["progress_percentage"] == 0


def test_list_subjects_returns_created_subject(authenticated_user):
    client.post("/api/v1/subjects", json={"name": "Databases"}, headers=authenticated_user["headers"])
    response = client.get("/api/v1/subjects", headers=authenticated_user["headers"])
    assert response.status_code == 200
    names = [subject["name"] for subject in response.json()]
    assert "Databases" in names


def test_get_subject_detail_includes_topics(authenticated_user):
    create_response = client.post(
        "/api/v1/subjects", json={"name": "Databases"}, headers=authenticated_user["headers"]
    )
    subject_id = create_response.json()["id"]

    client.post(
        f"/api/v1/subjects/{subject_id}/topics",
        json={"title": "Normalization"},
        headers=authenticated_user["headers"],
    )

    response = client.get(f"/api/v1/subjects/{subject_id}", headers=authenticated_user["headers"])
    assert response.status_code == 200
    body = response.json()
    assert len(body["topics"]) == 1
    assert body["topics"][0]["title"] == "Normalization"


def test_update_subject(authenticated_user):
    create_response = client.post(
        "/api/v1/subjects", json={"name": "Databases"}, headers=authenticated_user["headers"]
    )
    subject_id = create_response.json()["id"]

    response = client.put(
        f"/api/v1/subjects/{subject_id}",
        json={"name": "Advanced Databases"},
        headers=authenticated_user["headers"],
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Advanced Databases"


def test_delete_subject(authenticated_user):
    create_response = client.post(
        "/api/v1/subjects", json={"name": "Temporary"}, headers=authenticated_user["headers"]
    )
    subject_id = create_response.json()["id"]

    delete_response = client.delete(
        f"/api/v1/subjects/{subject_id}", headers=authenticated_user["headers"]
    )
    assert delete_response.status_code == 204

    get_response = client.get(f"/api/v1/subjects/{subject_id}", headers=authenticated_user["headers"])
    assert get_response.status_code == 404


def test_deleting_subject_deletes_its_topics(authenticated_user):
    create_response = client.post(
        "/api/v1/subjects", json={"name": "Temporary"}, headers=authenticated_user["headers"]
    )
    subject_id = create_response.json()["id"]
    client.post(
        f"/api/v1/subjects/{subject_id}/topics",
        json={"title": "Some topic"},
        headers=authenticated_user["headers"],
    )

    client.delete(f"/api/v1/subjects/{subject_id}", headers=authenticated_user["headers"])

    db = SessionLocal()
    from app.models.topic import Topic

    remaining = db.query(Topic).filter(Topic.subject_id == subject_id).count()
    db.close()
    assert remaining == 0


def test_topic_completion_updates_progress_percentage(authenticated_user):
    create_response = client.post(
        "/api/v1/subjects", json={"name": "Databases"}, headers=authenticated_user["headers"]
    )
    subject_id = create_response.json()["id"]

    topic_ids = []
    for title in ["Normalization", "Indexing", "Transactions", "Sharding"]:
        topic_response = client.post(
            f"/api/v1/subjects/{subject_id}/topics",
            json={"title": title},
            headers=authenticated_user["headers"],
        )
        topic_ids.append(topic_response.json()["id"])

    client.put(
        f"/api/v1/subjects/{subject_id}/topics/{topic_ids[0]}",
        json={"is_completed": True},
        headers=authenticated_user["headers"],
    )

    response = client.get(f"/api/v1/subjects/{subject_id}", headers=authenticated_user["headers"])
    body = response.json()
    assert body["completed_topic_count"] == 1
    assert body["topic_count"] == 4
    assert body["progress_percentage"] == 25


def test_delete_topic(authenticated_user):
    create_response = client.post(
        "/api/v1/subjects", json={"name": "Databases"}, headers=authenticated_user["headers"]
    )
    subject_id = create_response.json()["id"]
    topic_response = client.post(
        f"/api/v1/subjects/{subject_id}/topics",
        json={"title": "Normalization"},
        headers=authenticated_user["headers"],
    )
    topic_id = topic_response.json()["id"]

    delete_response = client.delete(
        f"/api/v1/subjects/{subject_id}/topics/{topic_id}", headers=authenticated_user["headers"]
    )
    assert delete_response.status_code == 204

    response = client.get(f"/api/v1/subjects/{subject_id}", headers=authenticated_user["headers"])
    assert response.json()["topics"] == []


def test_user_cannot_access_another_users_subject(authenticated_user, other_authenticated_user):
    create_response = client.post(
        "/api/v1/subjects", json={"name": "Private Subject"}, headers=authenticated_user["headers"]
    )
    subject_id = create_response.json()["id"]

    response = client.get(
        f"/api/v1/subjects/{subject_id}", headers=other_authenticated_user["headers"]
    )
    assert response.status_code == 404


def test_user_cannot_update_another_users_subject(authenticated_user, other_authenticated_user):
    create_response = client.post(
        "/api/v1/subjects", json={"name": "Private Subject"}, headers=authenticated_user["headers"]
    )
    subject_id = create_response.json()["id"]

    response = client.put(
        f"/api/v1/subjects/{subject_id}",
        json={"name": "Hijacked"},
        headers=other_authenticated_user["headers"],
    )
    assert response.status_code == 404


def test_subjects_require_authentication():
    response = client.get("/api/v1/subjects")
    assert response.status_code == 401


def test_create_subject_rejects_blank_name(authenticated_user):
    response = client.post(
        "/api/v1/subjects", json={"name": ""}, headers=authenticated_user["headers"]
    )
    assert response.status_code == 422