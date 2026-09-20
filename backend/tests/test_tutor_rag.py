import io
import uuid

import pytest
from fastapi.testclient import TestClient

from app.ai.providers.base import AIProvider
from app.ai.providers.embedding_base import EmbeddingProvider, EmbeddingProviderError
from app.ai.service import AITutorService
from app.api.deps import get_ai_tutor_service, get_embedding_provider
from app.db.session import SessionLocal
from app.main import app
from app.models.user import User

client = TestClient(app)


class FakeAIProvider(AIProvider):
    def __init__(self, reply: str = "Fake tutor reply."):
        self.reply = reply
        self.received_messages: list[dict[str, str]] | None = None

    async def generate_reply(self, messages: list[dict[str, str]]) -> str:
        self.received_messages = messages
        return self.reply


class FakeEmbeddingProvider(EmbeddingProvider):
    async def embed(self, texts: list[str]) -> list[list[float]]:
        return [self._fake_vector(text) for text in texts]

    @staticmethod
    def _fake_vector(text: str) -> list[float]:
        vector = [0.0] * 384
        lowered = text.lower()
        if "database" in lowered or "normalization" in lowered or "primary key" in lowered:
            vector[0] = 1.0
        elif "cooking" in lowered:
            vector[1] = 1.0
        else:
            vector[2] = 1.0
        return vector


class FailingEmbeddingProvider(EmbeddingProvider):
    async def embed(self, texts: list[str]) -> list[list[float]]:
        raise EmbeddingProviderError("down")


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
def fake_ai_and_embeddings():
    ai_provider = FakeAIProvider()
    app.dependency_overrides[get_ai_tutor_service] = lambda: AITutorService(ai_provider)
    app.dependency_overrides[get_embedding_provider] = lambda: FakeEmbeddingProvider()
    yield ai_provider
    app.dependency_overrides.pop(get_ai_tutor_service, None)
    app.dependency_overrides.pop(get_embedding_provider, None)


def _upload_text(headers, content: bytes, filename="notes.txt"):
    return client.post(
        "/api/v1/documents",
        files={"file": (filename, io.BytesIO(content), "text/plain")},
        headers=headers,
    )


def test_relevant_document_is_retrieved_and_cited(authenticated_user, fake_ai_and_embeddings):
    _upload_text(
        authenticated_user["headers"],
        b"Database normalization removes redundant data by organizing tables carefully.",
        filename="db_notes.txt",
    )

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
    assert "db_notes.txt" in body["sources"]

    system_message = fake_ai_and_embeddings.received_messages[0]["content"]
    assert "db_notes.txt" in system_message
    assert "redundant data" in system_message


def test_unrelated_document_is_not_retrieved(authenticated_user, fake_ai_and_embeddings):
    _upload_text(
        authenticated_user["headers"],
        b"A good recipe for cooking pasta involves boiling water first.",
        filename="recipe.txt",
    )

    conversation_response = client.post(
        "/api/v1/tutor/conversations", json={}, headers=authenticated_user["headers"]
    )
    conversation_id = conversation_response.json()["id"]

    response = client.post(
        f"/api/v1/tutor/conversations/{conversation_id}/messages",
        json={"content": "What is a primary key in a database?"},
        headers=authenticated_user["headers"],
    )
    assert response.status_code == 201
    assert response.json()["sources"] == []

    system_message = fake_ai_and_embeddings.received_messages[0]["content"]
    assert "recipe.txt" not in system_message


def test_no_documents_means_no_document_context(authenticated_user, fake_ai_and_embeddings):
    conversation_response = client.post(
        "/api/v1/tutor/conversations", json={}, headers=authenticated_user["headers"]
    )
    conversation_id = conversation_response.json()["id"]

    client.post(
        f"/api/v1/tutor/conversations/{conversation_id}/messages",
        json={"content": "What is a primary key?"},
        headers=authenticated_user["headers"],
    )

    system_message = fake_ai_and_embeddings.received_messages[0]["content"]
    assert "Excerpt from" not in system_message


def test_reply_still_works_when_embeddings_fail(authenticated_user):
    ai_provider = FakeAIProvider(reply="Reply without document context.")
    app.dependency_overrides[get_ai_tutor_service] = lambda: AITutorService(ai_provider)
    app.dependency_overrides[get_embedding_provider] = lambda: FailingEmbeddingProvider()
    try:
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
        assert response.json()["content"] == "Reply without document context."
        assert response.json()["sources"] == []
    finally:
        app.dependency_overrides.pop(get_ai_tutor_service, None)
        app.dependency_overrides.pop(get_embedding_provider, None)


def test_user_cannot_retrieve_another_users_document_chunks(authenticated_user, fake_ai_and_embeddings):
    other_user = _register_and_login()
    try:
        _upload_text(
            other_user["headers"],
            b"Database normalization removes redundant data.",
            filename="private_notes.txt",
        )

        conversation_response = client.post(
            "/api/v1/tutor/conversations", json={}, headers=authenticated_user["headers"]
        )
        conversation_id = conversation_response.json()["id"]

        response = client.post(
            f"/api/v1/tutor/conversations/{conversation_id}/messages",
            json={"content": "What is a primary key?"},
            headers=authenticated_user["headers"],
        )
        assert response.json()["sources"] == []
    finally:
        db = SessionLocal()
        db.query(User).filter(User.email == other_user["email"]).delete()
        db.commit()
        db.close()