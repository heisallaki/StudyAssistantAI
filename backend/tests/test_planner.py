import json
import uuid
from datetime import date, timedelta

import pytest
from fastapi.testclient import TestClient

from app.ai.providers.base import AIProvider, AIProviderError
from app.api.deps import get_ai_provider
from app.db.session import SessionLocal
from app.main import app
from app.models.user import User

client = TestClient(app)

VALID_RECOMMENDATIONS_JSON = json.dumps(
    {
        "recommendations": [
            {
                "subject": "Databases",
                "action": "Review normalization",
                "reason": "Only 25% of topics are complete and the exam is in 5 days.",
            }
        ]
    }
)


class FakeAIProvider(AIProvider):
    def __init__(self, response: str = VALID_RECOMMENDATIONS_JSON):
        self.response = response

    async def generate_reply(self, messages, response_format=None):
        return self.response


class FailingAIProvider(AIProvider):
    async def generate_reply(self, messages, response_format=None):
        raise AIProviderError("Could not reach the local AI model.")


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
def fake_ai():
    provider = FakeAIProvider()
    app.dependency_overrides[get_ai_provider] = lambda: provider
    yield provider
    app.dependency_overrides.pop(get_ai_provider, None)


@pytest.fixture
def failing_ai():
    app.dependency_overrides[get_ai_provider] = lambda: FailingAIProvider()
    yield
    app.dependency_overrides.pop(get_ai_provider, None)


def _create_subject(headers, name="Databases", priority="high"):
    response = client.post("/api/v1/subjects", json={"name": name, "priority": priority}, headers=headers)
    return response.json()


def test_create_and_get_goal(authenticated_user):
    response = client.post(
        "/api/v1/planner/goals",
        json={"title": "Finish React course", "target_date": "2026-12-01"},
        headers=authenticated_user["headers"],
    )
    assert response.status_code == 201
    goal = response.json()
    assert goal["title"] == "Finish React course"
    assert goal["status"] == "active"

    get_response = client.get(f"/api/v1/planner/goals/{goal['id']}", headers=authenticated_user["headers"])
    assert get_response.status_code == 200
    assert get_response.json()["target_date"] == "2026-12-01"


def test_create_goal_with_invalid_subject_returns_404(authenticated_user):
    response = client.post(
        "/api/v1/planner/goals",
        json={"title": "Orphan goal", "subject_id": str(uuid.uuid4())},
        headers=authenticated_user["headers"],
    )
    assert response.status_code == 404


def test_update_goal_status(authenticated_user):
    goal = client.post(
        "/api/v1/planner/goals", json={"title": "Learn Rust"}, headers=authenticated_user["headers"]
    ).json()
    response = client.put(
        f"/api/v1/planner/goals/{goal['id']}", json={"status": "completed"}, headers=authenticated_user["headers"]
    )
    assert response.status_code == 200
    assert response.json()["status"] == "completed"


def test_delete_goal(authenticated_user):
    goal = client.post(
        "/api/v1/planner/goals", json={"title": "Temp goal"}, headers=authenticated_user["headers"]
    ).json()
    delete_response = client.delete(f"/api/v1/planner/goals/{goal['id']}", headers=authenticated_user["headers"])
    assert delete_response.status_code == 204
    get_response = client.get(f"/api/v1/planner/goals/{goal['id']}", headers=authenticated_user["headers"])
    assert get_response.status_code == 404


def test_list_goals_filters_by_status(authenticated_user):
    active = client.post(
        "/api/v1/planner/goals", json={"title": "Active goal"}, headers=authenticated_user["headers"]
    ).json()
    done = client.post(
        "/api/v1/planner/goals", json={"title": "Done goal"}, headers=authenticated_user["headers"]
    ).json()
    client.put(f"/api/v1/planner/goals/{done['id']}", json={"status": "completed"}, headers=authenticated_user["headers"])

    response = client.get(
        "/api/v1/planner/goals", params={"status": "active"}, headers=authenticated_user["headers"]
    )
    titles = [goal["title"] for goal in response.json()]
    assert titles == ["Active goal"]
    assert active["id"]


def test_create_session(authenticated_user):
    response = client.post(
        "/api/v1/planner/sessions",
        json={"title": "Study SQL joins", "scheduled_date": "2026-06-01", "duration_minutes": 45},
        headers=authenticated_user["headers"],
    )
    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "planned"
    assert body["duration_minutes"] == 45


def test_create_session_with_invalid_goal_returns_404(authenticated_user):
    response = client.post(
        "/api/v1/planner/sessions",
        json={
            "title": "Study session",
            "scheduled_date": "2026-06-01",
            "duration_minutes": 30,
            "goal_id": str(uuid.uuid4()),
        },
        headers=authenticated_user["headers"],
    )
    assert response.status_code == 404


def test_update_session_status_to_completed(authenticated_user):
    session = client.post(
        "/api/v1/planner/sessions",
        json={"title": "Study session", "scheduled_date": "2026-06-01", "duration_minutes": 30},
        headers=authenticated_user["headers"],
    ).json()
    response = client.put(
        f"/api/v1/planner/sessions/{session['id']}",
        json={"status": "completed"},
        headers=authenticated_user["headers"],
    )
    assert response.status_code == 200
    assert response.json()["status"] == "completed"


def test_list_sessions_filters_by_date_range(authenticated_user):
    client.post(
        "/api/v1/planner/sessions",
        json={"title": "Early session", "scheduled_date": "2026-01-01", "duration_minutes": 30},
        headers=authenticated_user["headers"],
    )
    client.post(
        "/api/v1/planner/sessions",
        json={"title": "In range session", "scheduled_date": "2026-06-15", "duration_minutes": 30},
        headers=authenticated_user["headers"],
    )

    response = client.get(
        "/api/v1/planner/sessions",
        params={"start": "2026-06-01", "end": "2026-06-30"},
        headers=authenticated_user["headers"],
    )
    titles = [session["title"] for session in response.json()]
    assert titles == ["In range session"]


def test_delete_session(authenticated_user):
    session = client.post(
        "/api/v1/planner/sessions",
        json={"title": "Temp session", "scheduled_date": "2026-06-01", "duration_minutes": 30},
        headers=authenticated_user["headers"],
    ).json()
    response = client.delete(f"/api/v1/planner/sessions/{session['id']}", headers=authenticated_user["headers"])
    assert response.status_code == 204


def test_create_deadline(authenticated_user):
    response = client.post(
        "/api/v1/planner/deadlines",
        json={"title": "Assignment 2", "due_date": "2026-06-10"},
        headers=authenticated_user["headers"],
    )
    assert response.status_code == 201
    assert response.json()["is_completed"] is False


def test_update_deadline_mark_completed(authenticated_user):
    deadline = client.post(
        "/api/v1/planner/deadlines",
        json={"title": "Assignment 2", "due_date": "2026-06-10"},
        headers=authenticated_user["headers"],
    ).json()
    response = client.put(
        f"/api/v1/planner/deadlines/{deadline['id']}",
        json={"is_completed": True},
        headers=authenticated_user["headers"],
    )
    assert response.status_code == 200
    assert response.json()["is_completed"] is True


def test_list_deadlines_excludes_completed_when_requested(authenticated_user):
    done = client.post(
        "/api/v1/planner/deadlines",
        json={"title": "Done deadline", "due_date": "2026-06-10"},
        headers=authenticated_user["headers"],
    ).json()
    client.put(
        f"/api/v1/planner/deadlines/{done['id']}", json={"is_completed": True}, headers=authenticated_user["headers"]
    )
    client.post(
        "/api/v1/planner/deadlines",
        json={"title": "Open deadline", "due_date": "2026-06-11"},
        headers=authenticated_user["headers"],
    )

    response = client.get(
        "/api/v1/planner/deadlines",
        params={"include_completed": False},
        headers=authenticated_user["headers"],
    )
    titles = [deadline["title"] for deadline in response.json()]
    assert titles == ["Open deadline"]


def test_delete_deadline(authenticated_user):
    deadline = client.post(
        "/api/v1/planner/deadlines",
        json={"title": "Temp deadline", "due_date": "2026-06-10"},
        headers=authenticated_user["headers"],
    ).json()
    response = client.delete(
        f"/api/v1/planner/deadlines/{deadline['id']}", headers=authenticated_user["headers"]
    )
    assert response.status_code == 204


def test_calendar_combines_sessions_and_deadlines(authenticated_user):
    client.post(
        "/api/v1/planner/sessions",
        json={"title": "Study session", "scheduled_date": "2026-07-05", "duration_minutes": 30},
        headers=authenticated_user["headers"],
    )
    client.post(
        "/api/v1/planner/deadlines",
        json={"title": "Project due", "due_date": "2026-07-07"},
        headers=authenticated_user["headers"],
    )

    response = client.get(
        "/api/v1/planner/calendar",
        params={"start": "2026-07-01", "end": "2026-07-31"},
        headers=authenticated_user["headers"],
    )
    assert response.status_code == 200
    entries = response.json()
    assert len(entries) == 2
    types = {entry["entry_type"] for entry in entries}
    assert types == {"session", "deadline"}
    assert entries[0]["date"] <= entries[1]["date"]


def test_calendar_requires_start_and_end(authenticated_user):
    response = client.get("/api/v1/planner/calendar", headers=authenticated_user["headers"])
    assert response.status_code == 422


def test_subject_create_with_priority(authenticated_user):
    subject = _create_subject(authenticated_user["headers"], priority="high")
    assert subject["priority"] == "high"


def test_subject_update_priority(authenticated_user):
    subject = _create_subject(authenticated_user["headers"], priority="medium")
    response = client.put(
        f"/api/v1/subjects/{subject['id']}", json={"priority": "low"}, headers=authenticated_user["headers"]
    )
    assert response.status_code == 200
    assert response.json()["priority"] == "low"


def test_recommendations_success(authenticated_user, fake_ai):
    _create_subject(authenticated_user["headers"])
    client.post(
        "/api/v1/planner/deadlines",
        json={"title": "Exam", "due_date": (date.today() + timedelta(days=5)).isoformat()},
        headers=authenticated_user["headers"],
    )

    response = client.post("/api/v1/planner/recommendations", headers=authenticated_user["headers"])
    assert response.status_code == 200
    body = response.json()
    assert len(body["recommendations"]) == 1
    assert body["recommendations"][0]["subject"] == "Databases"


def test_recommendations_upstream_failure_returns_502(authenticated_user, failing_ai):
    response = client.post("/api/v1/planner/recommendations", headers=authenticated_user["headers"])
    assert response.status_code == 502


def test_recommendations_invalid_ai_response_returns_502(authenticated_user):
    app.dependency_overrides[get_ai_provider] = lambda: FakeAIProvider(response="not valid json")
    try:
        response = client.post("/api/v1/planner/recommendations", headers=authenticated_user["headers"])
        assert response.status_code == 502
    finally:
        app.dependency_overrides.pop(get_ai_provider, None)


def test_planner_requires_authentication():
    response = client.get("/api/v1/planner/goals")
    assert response.status_code == 401