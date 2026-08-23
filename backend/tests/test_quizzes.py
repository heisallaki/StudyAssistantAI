import json
import uuid

import pytest
from fastapi.testclient import TestClient

from app.ai.providers.base import AIProvider, AIProviderError
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
            },
            {
                "question_type": "true_false",
                "prompt": "A primary key can contain duplicate values.",
                "correct_answer": "false",
                "explanation": "Primary keys must be unique.",
            },
        ]
    }
)


class FakeAIProvider(AIProvider):
    def __init__(self, response: str = VALID_QUIZ_JSON):
        self.response = response
        self.received_messages: list[dict[str, str]] | None = None
        self.received_format: str | None = None

    async def generate_reply(self, messages, response_format=None):
        self.received_messages = messages
        self.received_format = response_format
        return self.response


class FailingAIProvider(AIProvider):
    async def generate_reply(self, messages, response_format=None):
        raise AIProviderError("Could not reach the local AI model.")


class MalformedAIProvider(AIProvider):
    async def generate_reply(self, messages, response_format=None):
        return "this is not json"


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


@pytest.fixture
def malformed_ai():
    app.dependency_overrides[get_ai_provider] = lambda: MalformedAIProvider()
    yield
    app.dependency_overrides.pop(get_ai_provider, None)


def test_generate_quiz_creates_completed_quiz_with_questions(authenticated_user, fake_ai):
    response = client.post(
        "/api/v1/quizzes",
        json={"difficulty": "medium", "question_count": 2},
        headers=authenticated_user["headers"],
    )
    assert response.status_code == 201
    body = response.json()
    assert body["generation_status"] == "completed"
    assert body["generation_error"] is None
    assert len(body["questions"]) == 2
    assert body["questions"][0]["question_type"] == "multiple_choice"
    assert fake_ai.received_format == "json"


def test_generate_quiz_with_subject_includes_context_in_title_and_prompt(authenticated_user, fake_ai):
    subject_response = client.post(
        "/api/v1/subjects", json={"name": "Databases"}, headers=authenticated_user["headers"]
    )
    subject_id = subject_response.json()["id"]

    response = client.post(
        "/api/v1/quizzes",
        json={"subject_id": subject_id, "difficulty": "hard"},
        headers=authenticated_user["headers"],
    )
    assert response.status_code == 201
    assert "Databases" in response.json()["title"]
    assert "Databases" in fake_ai.received_messages[0]["content"]


def test_generate_quiz_rejects_another_users_subject(authenticated_user, fake_ai):
    other_user = _register_and_login()
    try:
        subject_response = client.post(
            "/api/v1/subjects", json={"name": "Private"}, headers=other_user["headers"]
        )
        subject_id = subject_response.json()["id"]

        response = client.post(
            "/api/v1/quizzes",
            json={"subject_id": subject_id},
            headers=authenticated_user["headers"],
        )
        assert response.status_code == 404
    finally:
        db = SessionLocal()
        db.query(User).filter(User.email == other_user["email"]).delete()
        db.commit()
        db.close()


def test_generate_quiz_marks_failed_when_ai_unavailable(authenticated_user, failing_ai):
    response = client.post("/api/v1/quizzes", json={}, headers=authenticated_user["headers"])
    assert response.status_code == 201
    body = response.json()
    assert body["generation_status"] == "failed"
    assert body["generation_error"] is not None
    assert body["questions"] == []


def test_generate_quiz_marks_failed_on_malformed_ai_response(authenticated_user, malformed_ai):
    response = client.post("/api/v1/quizzes", json={}, headers=authenticated_user["headers"])
    assert response.status_code == 201
    body = response.json()
    assert body["generation_status"] == "failed"
    assert body["questions"] == []


def test_list_quizzes_returns_created_quiz(authenticated_user, fake_ai):
    client.post("/api/v1/quizzes", json={}, headers=authenticated_user["headers"])
    response = client.get("/api/v1/quizzes", headers=authenticated_user["headers"])
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_list_quizzes_does_not_include_questions_but_has_count(authenticated_user, fake_ai):
    client.post("/api/v1/quizzes", json={}, headers=authenticated_user["headers"])
    response = client.get("/api/v1/quizzes", headers=authenticated_user["headers"])
    body = response.json()[0]
    assert "questions" not in body
    assert body["question_count"] == 2


def test_get_quiz_detail_includes_questions(authenticated_user, fake_ai):
    create_response = client.post("/api/v1/quizzes", json={}, headers=authenticated_user["headers"])
    quiz_id = create_response.json()["id"]

    response = client.get(f"/api/v1/quizzes/{quiz_id}", headers=authenticated_user["headers"])
    assert response.status_code == 200
    assert len(response.json()["questions"]) == 2


def test_delete_quiz(authenticated_user, fake_ai):
    create_response = client.post("/api/v1/quizzes", json={}, headers=authenticated_user["headers"])
    quiz_id = create_response.json()["id"]

    delete_response = client.delete(f"/api/v1/quizzes/{quiz_id}", headers=authenticated_user["headers"])
    assert delete_response.status_code == 204

    get_response = client.get(f"/api/v1/quizzes/{quiz_id}", headers=authenticated_user["headers"])
    assert get_response.status_code == 404


def test_user_cannot_access_another_users_quiz(authenticated_user, fake_ai):
    other_user = _register_and_login()
    try:
        app.dependency_overrides[get_ai_provider] = lambda: FakeAIProvider()
        create_response = client.post("/api/v1/quizzes", json={}, headers=other_user["headers"])
        quiz_id = create_response.json()["id"]

        response = client.get(f"/api/v1/quizzes/{quiz_id}", headers=authenticated_user["headers"])
        assert response.status_code == 404
    finally:
        db = SessionLocal()
        db.query(User).filter(User.email == other_user["email"]).delete()
        db.commit()
        db.close()


def test_quiz_create_rejects_invalid_question_type(authenticated_user, fake_ai):
    response = client.post(
        "/api/v1/quizzes",
        json={"question_types": ["essay"]},
        headers=authenticated_user["headers"],
    )
    assert response.status_code == 422


def test_quiz_create_rejects_invalid_difficulty(authenticated_user, fake_ai):
    response = client.post(
        "/api/v1/quizzes",
        json={"difficulty": "impossible"},
        headers=authenticated_user["headers"],
    )
    assert response.status_code == 422


def test_quizzes_require_authentication():
    response = client.get("/api/v1/quizzes")
    assert response.status_code == 401