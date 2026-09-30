import uuid

import pytest
from fastapi.testclient import TestClient

from app.ai.providers.base import AIProvider, AIProviderError
from app.ai.service import AITutorService
from app.api.deps import get_ai_tutor_service
from app.api.routes.tutor import AI_TUTOR_UNAVAILABLE_MESSAGE
from app.db.session import SessionLocal
from app.main import app
from app.models.user import User

client = TestClient(app)


class FakeAIProvider(AIProvider):
    def __init__(self, reply: str = "This is a fake tutor reply."):
        self.reply = reply
        self.received_messages: list[dict[str, str]] | None = None

    async def generate_reply(self, messages: list[dict[str, str]]) -> str:
        self.received_messages = messages
        return self.reply


class FailingAIProvider(AIProvider):
    async def generate_reply(self, messages: list[dict[str, str]]) -> str:
        raise AIProviderError("Could not reach the local AI model. Make sure Ollama is installed and running.")


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


@pytest.fixture
def fake_provider():
    provider = FakeAIProvider()
    app.dependency_overrides[get_ai_tutor_service] = lambda: AITutorService(provider)
    yield provider
    app.dependency_overrides.pop(get_ai_tutor_service, None)


@pytest.fixture
def failing_provider():
    app.dependency_overrides[get_ai_tutor_service] = lambda: AITutorService(FailingAIProvider())
    yield
    app.dependency_overrides.pop(get_ai_tutor_service, None)


def test_list_conversations_starts_empty(authenticated_user):
    response = client.get("/api/v1/tutor/conversations", headers=authenticated_user["headers"])
    assert response.status_code == 200
    assert response.json() == []


def test_create_conversation_defaults(authenticated_user):
    response = client.post(
        "/api/v1/tutor/conversations", json={}, headers=authenticated_user["headers"]
    )
    assert response.status_code == 201


def test_send_message_preserves_user_message_when_ai_unavailable(authenticated_user, failing_provider):
    conversation_response = client.post(
        "/api/v1/tutor/conversations", json={}, headers=authenticated_user["headers"]
    )
    conversation_id = conversation_response.json()["id"]

    response = client.post(
        f"/api/v1/tutor/conversations/{conversation_id}/messages",
        json={"content": "What is a primary key?"},
        headers=authenticated_user["headers"],
    )
    assert response.status_code == 503
    body = response.json()
    assert body["detail"] == AI_TUTOR_UNAVAILABLE_MESSAGE
    assert "ollama" not in body["detail"].lower()

    detail_response = client.get(
        f"/api/v1/tutor/conversations/{conversation_id}", headers=authenticated_user["headers"]
    )
    messages = detail_response.json()["messages"]
    assert len(messages) == 1
    assert messages[0]["role"] == "user"
    assert messages[0]["content"] == "What is a primary key?"


def test_update_conversation_mode_and_level(authenticated_user):
    conversation_response = client.post(
        "/api/v1/tutor/conversations", json={}, headers=authenticated_user["headers"]
    )