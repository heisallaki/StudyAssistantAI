import uuid

import pytest
from fastapi.testclient import TestClient

from app.ai.providers.base import AIProvider, AIProviderError
from app.ai.service import AITutorService
from app.api.deps import get_ai_tutor_service
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
    body = response.json()
    assert body["mode"] == "tutor"
    assert body["explanation_level"] == "intermediate"
    assert body["subject_id"] is None


def test_create_conversation_rejects_invalid_mode(authenticated_user):
    response = client.post(
        "/api/v1/tutor/conversations",
        json={"mode": "not-a-real-mode"},
        headers=authenticated_user["headers"],
    )
    assert response.status_code == 422


def test_create_conversation_with_subject(authenticated_user):
    subject_response = client.post(
        "/api/v1/subjects", json={"name": "Databases"}, headers=authenticated_user["headers"]
    )
    subject_id = subject_response.json()["id"]

    response = client.post(
        "/api/v1/tutor/conversations",
        json={"subject_id": subject_id, "explanation_level": "beginner"},
        headers=authenticated_user["headers"],
    )
    assert response.status_code == 201
    assert response.json()["subject_id"] == subject_id


def test_create_conversation_rejects_another_users_subject(authenticated_user, other_authenticated_user):
    subject_response = client.post(
        "/api/v1/subjects", json={"name": "Private"}, headers=authenticated_user["headers"]
    )
    subject_id = subject_response.json()["id"]

    response = client.post(
        "/api/v1/tutor/conversations",
        json={"subject_id": subject_id},
        headers=other_authenticated_user["headers"],
    )
    assert response.status_code == 404


def test_send_message_persists_and_returns_assistant_reply(authenticated_user, fake_provider):
    conversation_response = client.post(
        "/api/v1/tutor/conversations", json={}, headers=authenticated_user["headers"]
    )
    conversation_id = conversation_response.json()["id"]

    response = client.post(
        f"/api/v1/tutor/conversations/{conversation_id}/messages",
        json={"content": "What is a primary key?"},
        headers=authenticated_user["headers"],
    )
    assert response.status_code == 201
    body = response.json()
    assert body["role"] == "assistant"
    assert body["content"] == "This is a fake tutor reply."

    detail_response = client.get(
        f"/api/v1/tutor/conversations/{conversation_id}", headers=authenticated_user["headers"]
    )
    messages = detail_response.json()["messages"]
    assert len(messages) == 2
    assert messages[0]["role"] == "user"
    assert messages[0]["content"] == "What is a primary key?"
    assert messages[1]["role"] == "assistant"


def test_send_message_includes_system_prompt_and_history(authenticated_user, fake_provider):
    conversation_response = client.post(
        "/api/v1/tutor/conversations", json={"explanation_level": "beginner"}, headers=authenticated_user["headers"]
    )
    conversation_id = conversation_response.json()["id"]

    client.post(
        f"/api/v1/tutor/conversations/{conversation_id}/messages",
        json={"content": "What is a primary key?"},
        headers=authenticated_user["headers"],
    )
    client.post(
        f"/api/v1/tutor/conversations/{conversation_id}/messages",
        json={"content": "Can you give an example?"},
        headers=authenticated_user["headers"],
    )

    assert fake_provider.received_messages is not None
    assert fake_provider.received_messages[0]["role"] == "system"
    assert "first time" in fake_provider.received_messages[0]["content"]
    roles = [message["role"] for message in fake_provider.received_messages]
    assert roles == ["system", "user", "assistant", "user"]


def test_send_message_sets_conversation_title_from_first_message(authenticated_user, fake_provider):
    conversation_response = client.post(
        "/api/v1/tutor/conversations", json={}, headers=authenticated_user["headers"]
    )
    conversation_id = conversation_response.json()["id"]

    client.post(
        f"/api/v1/tutor/conversations/{conversation_id}/messages",
        json={"content": "Explain database normalization"},
        headers=authenticated_user["headers"],
    )

    response = client.get(
        f"/api/v1/tutor/conversations/{conversation_id}", headers=authenticated_user["headers"]
    )
    assert response.json()["title"] == "Explain database normalization"


def test_send_message_with_subject_includes_subject_context(authenticated_user, fake_provider):
    subject_response = client.post(
        "/api/v1/subjects", json={"name": "Databases"}, headers=authenticated_user["headers"]
    )
    subject_id = subject_response.json()["id"]
    client.post(
        f"/api/v1/subjects/{subject_id}/topics",
        json={"title": "Normalization"},
        headers=authenticated_user["headers"],
    )

    conversation_response = client.post(
        "/api/v1/tutor/conversations",
        json={"subject_id": subject_id},
        headers=authenticated_user["headers"],
    )
    conversation_id = conversation_response.json()["id"]

    client.post(
        f"/api/v1/tutor/conversations/{conversation_id}/messages",
        json={"content": "Help me study"},
        headers=authenticated_user["headers"],
    )

    system_message = fake_provider.received_messages[0]["content"]
    assert "Databases" in system_message
    assert "Normalization" in system_message


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
    conversation_id = conversation_response.json()["id"]

    response = client.put(
        f"/api/v1/tutor/conversations/{conversation_id}",
        json={"mode": "socratic", "explanation_level": "advanced"},
        headers=authenticated_user["headers"],
    )
    assert response.status_code == 200
    assert response.json()["mode"] == "socratic"
    assert response.json()["explanation_level"] == "advanced"


def test_delete_conversation_removes_messages(authenticated_user, fake_provider):
    conversation_response = client.post(
        "/api/v1/tutor/conversations", json={}, headers=authenticated_user["headers"]
    )
    conversation_id = conversation_response.json()["id"]
    client.post(
        f"/api/v1/tutor/conversations/{conversation_id}/messages",
        json={"content": "Hello"},
        headers=authenticated_user["headers"],
    )

    delete_response = client.delete(
        f"/api/v1/tutor/conversations/{conversation_id}", headers=authenticated_user["headers"]
    )
    assert delete_response.status_code == 204

    get_response = client.get(
        f"/api/v1/tutor/conversations/{conversation_id}", headers=authenticated_user["headers"]
    )
    assert get_response.status_code == 404


def test_user_cannot_access_another_users_conversation(authenticated_user, other_authenticated_user, fake_provider):
    conversation_response = client.post(
        "/api/v1/tutor/conversations", json={}, headers=authenticated_user["headers"]
    )
    conversation_id = conversation_response.json()["id"]

    response = client.get(
        f"/api/v1/tutor/conversations/{conversation_id}", headers=other_authenticated_user["headers"]
    )
    assert response.status_code == 404


def test_tutor_requires_authentication():
    response = client.get("/api/v1/tutor/conversations")
    assert response.status_code == 401