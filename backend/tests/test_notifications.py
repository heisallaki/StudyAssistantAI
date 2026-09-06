import uuid
from datetime import date, timedelta

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


def test_registration_creates_welcome_notification(authenticated_user):
    response = client.get("/api/v1/notifications", headers=authenticated_user["headers"])
    assert response.status_code == 200
    body = response.json()
    assert any(item["notification_type"] == "system" for item in body)


def test_unread_count_reflects_welcome_notification(authenticated_user):
    response = client.get("/api/v1/notifications/unread-count", headers=authenticated_user["headers"])
    assert response.status_code == 200
    assert response.json()["unread_count"] == 1


def test_mark_notification_read(authenticated_user):
    headers = authenticated_user["headers"]
    notification = client.get("/api/v1/notifications", headers=headers).json()[0]

    response = client.put(
        f"/api/v1/notifications/{notification['id']}", json={"is_read": True}, headers=headers
    )
    assert response.status_code == 200
    assert response.json()["is_read"] is True

    unread = client.get("/api/v1/notifications/unread-count", headers=headers).json()
    assert unread["unread_count"] == 0


def test_mark_notification_unread(authenticated_user):
    headers = authenticated_user["headers"]
    notification = client.get("/api/v1/notifications", headers=headers).json()[0]
    client.put(f"/api/v1/notifications/{notification['id']}", json={"is_read": True}, headers=headers)

    response = client.put(
        f"/api/v1/notifications/{notification['id']}", json={"is_read": False}, headers=headers
    )
    assert response.json()["is_read"] is False


def test_list_notifications_unread_only_filter(authenticated_user):
    headers = authenticated_user["headers"]
    notification = client.get("/api/v1/notifications", headers=headers).json()[0]
    client.put(f"/api/v1/notifications/{notification['id']}", json={"is_read": True}, headers=headers)

    response = client.get("/api/v1/notifications", params={"unread_only": True}, headers=headers)
    assert response.json() == []


def test_mark_all_read(authenticated_user):
    headers = authenticated_user["headers"]
    client.post(
        "/api/v1/planner/deadlines",
        json={"title": "Exam", "due_date": date.today().isoformat()},
        headers=headers,
    )
    client.get("/api/v1/notifications", headers=headers)

    response = client.post("/api/v1/notifications/mark-all-read", headers=headers)
    assert response.status_code == 200
    assert response.json()["unread_count"] == 0

    unread_after = client.get("/api/v1/notifications/unread-count", headers=headers).json()
    assert unread_after["unread_count"] == 0


def test_delete_notification(authenticated_user):
    headers = authenticated_user["headers"]
    notification = client.get("/api/v1/notifications", headers=headers).json()[0]

    response = client.delete(f"/api/v1/notifications/{notification['id']}", headers=headers)
    assert response.status_code == 204

    remaining = client.get("/api/v1/notifications", headers=headers).json()
    assert all(item["id"] != notification["id"] for item in remaining)


def test_notification_not_found_returns_404(authenticated_user):
    response = client.put(
        f"/api/v1/notifications/{uuid.uuid4()}", json={"is_read": True}, headers=authenticated_user["headers"]
    )
    assert response.status_code == 404


def test_study_session_reminder_generated_for_today(authenticated_user):
    headers = authenticated_user["headers"]
    client.post(
        "/api/v1/planner/sessions",
        json={"title": "Study SQL", "scheduled_date": date.today().isoformat(), "duration_minutes": 30},
        headers=headers,
    )

    response = client.get("/api/v1/notifications", headers=headers)
    body = response.json()
    assert any(item["notification_type"] == "study_reminder" for item in body)


def test_study_session_reminder_not_duplicated_on_repeated_calls(authenticated_user):
    headers = authenticated_user["headers"]
    client.post(
        "/api/v1/planner/sessions",
        json={"title": "Study SQL", "scheduled_date": date.today().isoformat(), "duration_minutes": 30},
        headers=headers,
    )

    client.get("/api/v1/notifications", headers=headers)
    second_call = client.get("/api/v1/notifications", headers=headers).json()
    study_reminders = [item for item in second_call if item["notification_type"] == "study_reminder"]
    assert len(study_reminders) == 1


def test_deadline_reminder_generated_within_window(authenticated_user):
    headers = authenticated_user["headers"]
    client.post(
        "/api/v1/planner/deadlines",
        json={"title": "Assignment", "due_date": (date.today() + timedelta(days=2)).isoformat()},
        headers=headers,
    )

    response = client.get("/api/v1/notifications", headers=headers)
    body = response.json()
    assert any(item["notification_type"] == "deadline_reminder" for item in body)


def test_deadline_reminder_not_generated_outside_window(authenticated_user):
    headers = authenticated_user["headers"]
    client.post(
        "/api/v1/planner/deadlines",
        json={"title": "Far off assignment", "due_date": (date.today() + timedelta(days=30)).isoformat()},
        headers=headers,
    )

    response = client.get("/api/v1/notifications", headers=headers)
    body = response.json()
    assert not any(item["notification_type"] == "deadline_reminder" for item in body)


def test_quiz_reminder_generated_for_low_topic_progress(authenticated_user):
    headers = authenticated_user["headers"]
    subject = client.post("/api/v1/subjects", json={"name": "Neglected Subject"}, headers=headers).json()
    client.post(f"/api/v1/subjects/{subject['id']}/topics", json={"title": "Topic 1"}, headers=headers)
    client.post(f"/api/v1/subjects/{subject['id']}/topics", json={"title": "Topic 2"}, headers=headers)

    response = client.get("/api/v1/notifications", headers=headers)
    body = response.json()
    assert any(item["notification_type"] == "quiz_reminder" for item in body)


def test_notifications_require_authentication():
    response = client.get("/api/v1/notifications")
    assert response.status_code == 401