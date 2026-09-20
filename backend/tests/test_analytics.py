import json
import uuid
from datetime import date

import pytest
from fastapi.testclient import TestClient

from app.ai.providers.base import AIProvider
from app.api.deps import get_ai_provider
from app.db.session import SessionLocal
from app.main import app
from app.models.user import User

client = TestClient(app)

VALID_QUIZ_JSON = json.dumps(
    {
        "questions": [
            {
                "question_type": "multiple_choice",
                "prompt": "What does SQL stand for?",
                "options": [
                    "Structured Query Language",
                    "Simple Query Language",
                    "Standard Query Logic",
                    "System Query Language",
                ],
                "correct_answer": "Structured Query Language",
                "explanation": "SQL stands for Structured Query Language.",
            }
        ]
    }
)


class FakeAIProvider(AIProvider):
    def __init__(self, response: str = VALID_QUIZ_JSON):
        self.response = response

    async def generate_reply(self, messages, response_format=None):
        return self.response


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


def _create_subject(headers, name="Databases", priority="high"):
    return client.post("/api/v1/subjects", json={"name": name, "priority": priority}, headers=headers).json()


def _complete_quiz_attempt(headers, subject_id=None):
    quiz = client.post(
        "/api/v1/quizzes", json={"subject_id": subject_id}, headers=headers
    ).json()
    attempt = client.post(f"/api/v1/quizzes/{quiz['id']}/attempts", headers=headers).json()
    question_id = quiz["questions"][0]["id"]
    client.put(
        f"/api/v1/quiz-attempts/{attempt['id']}/answers/{question_id}",
        json={"submitted_answer": "Structured Query Language"},
        headers=headers,
    )
    return client.post(f"/api/v1/quiz-attempts/{attempt['id']}/complete", headers=headers).json()


def _create_mastered_flashcard(headers, deck_title="Deck", subject_id=None):
    deck = client.post(
        "/api/v1/decks", json={"title": deck_title, "subject_id": subject_id}, headers=headers
    ).json()
    card = client.post(
        f"/api/v1/decks/{deck['id']}/flashcards",
        json={"front": "Q", "back": "A"},
        headers=headers,
    ).json()
    client.post(
        f"/api/v1/decks/{deck['id']}/flashcards/{card['id']}/review",
        json={"result": "good"},
        headers=headers,
    )
    client.post(
        f"/api/v1/decks/{deck['id']}/flashcards/{card['id']}/review",
        json={"result": "good"},
        headers=headers,
    )
    return deck, card


def _create_completed_session(headers, subject_id=None, duration_minutes=45):
    session = client.post(
        "/api/v1/planner/sessions",
        json={
            "title": "Study session",
            "subject_id": subject_id,
            "scheduled_date": date.today().isoformat(),
            "duration_minutes": duration_minutes,
        },
        headers=headers,
    ).json()
    return client.put(
        f"/api/v1/planner/sessions/{session['id']}", json={"status": "completed"}, headers=headers
    ).json()


def test_overview_defaults_for_new_user(authenticated_user):
    response = client.get("/api/v1/analytics/overview", headers=authenticated_user["headers"])
    assert response.status_code == 200
    body = response.json()
    assert body == {
        "total_study_minutes": 0,
        "total_quizzes_taken": 0,
        "average_quiz_score": None,
        "total_flashcards_reviewed": 0,
        "flashcards_mastered": 0,
        "total_flashcards": 0,
        "subjects_count": 0,
        "active_goals_count": 0,
    }


def test_overview_aggregates_across_modules(authenticated_user, fake_ai):
    headers = authenticated_user["headers"]
    subject = _create_subject(headers)
    _complete_quiz_attempt(headers, subject_id=subject["id"])
    _create_mastered_flashcard(headers, subject_id=subject["id"])
    _create_completed_session(headers, subject_id=subject["id"], duration_minutes=45)
    client.post("/api/v1/planner/goals", json={"title": "Finish course"}, headers=headers)

    response = client.get("/api/v1/analytics/overview", headers=headers)
    body = response.json()
    assert body["total_study_minutes"] == 45
    assert body["total_quizzes_taken"] == 1
    assert body["average_quiz_score"] == 100
    assert body["total_flashcards_reviewed"] == 2
    assert body["flashcards_mastered"] == 1
    assert body["total_flashcards"] == 1
    assert body["subjects_count"] == 1
    assert body["active_goals_count"] == 1


def test_performance_trend_reflects_completed_attempt(authenticated_user, fake_ai):
    headers = authenticated_user["headers"]
    _complete_quiz_attempt(headers)

    response = client.get("/api/v1/analytics/performance-trend", headers=headers)
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["date"] == date.today().isoformat()
    assert body[0]["average_score"] == 100
    assert body[0]["attempts_count"] == 1


def test_performance_trend_empty_for_new_user(authenticated_user):
    response = client.get("/api/v1/analytics/performance-trend", headers=authenticated_user["headers"])
    assert response.json() == []


def test_study_time_series_only_counts_completed_sessions(authenticated_user):
    headers = authenticated_user["headers"]
    client.post(
        "/api/v1/planner/sessions",
        json={"title": "Still planned", "scheduled_date": date.today().isoformat(), "duration_minutes": 60},
        headers=headers,
    )
    _create_completed_session(headers, duration_minutes=30)

    response = client.get("/api/v1/analytics/study-time", params={"days": 7}, headers=headers)
    body = response.json()
    today_entry = next(entry for entry in body if entry["date"] == date.today().isoformat())
    assert today_entry["minutes"] == 30
    assert len(body) == 7


def test_subject_breakdown_reflects_all_metrics(authenticated_user, fake_ai):
    headers = authenticated_user["headers"]
    subject = _create_subject(headers, priority="high")
    topic = client.post(
        f"/api/v1/subjects/{subject['id']}/topics", json={"title": "Normalization"}, headers=headers
    ).json()
    client.put(
        f"/api/v1/subjects/{subject['id']}/topics/{topic['id']}",
        json={"is_completed": True},
        headers=headers,
    )
    _complete_quiz_attempt(headers, subject_id=subject["id"])
    _create_mastered_flashcard(headers, subject_id=subject["id"])
    _create_completed_session(headers, subject_id=subject["id"], duration_minutes=20)

    response = client.get("/api/v1/analytics/subject-breakdown", headers=headers)
    body = response.json()
    assert len(body) == 1
    entry = body[0]
    assert entry["subject_id"] == subject["id"]
    assert entry["priority"] == "high"
    assert entry["topic_progress_percentage"] == 100
    assert entry["quiz_average_score"] == 100
    assert entry["flashcard_mastery_percentage"] == 100
    assert entry["study_minutes"] == 20


def test_subject_breakdown_handles_subject_with_no_activity(authenticated_user):
    _create_subject(authenticated_user["headers"], name="Untouched")
    response = client.get("/api/v1/analytics/subject-breakdown", headers=authenticated_user["headers"])
    body = response.json()
    assert len(body) == 1
    assert body[0]["quiz_average_score"] is None
    assert body[0]["flashcard_mastery_percentage"] is None
    assert body[0]["topic_progress_percentage"] == 0


def test_weak_areas_flags_low_topic_progress_subject(authenticated_user):
    headers = authenticated_user["headers"]
    subject = _create_subject(headers, name="Neglected Subject")
    client.post(f"/api/v1/subjects/{subject['id']}/topics", json={"title": "Topic 1"}, headers=headers)
    client.post(f"/api/v1/subjects/{subject['id']}/topics", json={"title": "Topic 2"}, headers=headers)

    response = client.get("/api/v1/analytics/weak-areas", headers=headers)
    body = response.json()
    assert any(area["subject_id"] == subject["id"] and area["reason"] == "low_topic_progress" for area in body)


def test_weak_areas_excludes_subject_with_no_topics_or_quizzes(authenticated_user):
    _create_subject(authenticated_user["headers"], name="Fresh Subject")
    response = client.get("/api/v1/analytics/weak-areas", headers=authenticated_user["headers"])
    assert response.json() == []


def test_analytics_requires_authentication():
    response = client.get("/api/v1/analytics/overview")
    assert response.status_code == 401