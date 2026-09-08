import json
import uuid

import pytest
from fastapi.testclient import TestClient

from app.ai.providers.base import AIProvider
from app.ai.providers.embedding_base import EmbeddingProvider, EmbeddingProviderError
from app.api.deps import get_ai_provider, get_embedding_provider
from app.db.session import SessionLocal
from app.main import app
from app.models.document import Document
from app.models.document_chunk import EMBEDDING_DIMENSIONS, DocumentChunk
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
    async def generate_reply(self, messages, response_format=None):
        return VALID_QUIZ_JSON


class FakeEmbeddingProvider(EmbeddingProvider):
    def __init__(self, vector: list[float] | None = None):
        self.vector = vector or [0.1] * EMBEDDING_DIMENSIONS

    async def embed(self, texts: list[str]) -> list[list[float]]:
        return [self.vector for _ in texts]


class FailingEmbeddingProvider(EmbeddingProvider):
    async def embed(self, texts: list[str]) -> list[list[float]]:
        raise EmbeddingProviderError("Could not reach the local embedding model.")


def _register_and_login():
    email = f"{uuid.uuid4()}@example.com"
    password = "S3curePassw0rd!"
    client.post("/api/v1/auth/register", json={"email": email, "password": password})
    login_response = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    token = login_response.json()["access_token"]
    return {"email": email, "headers": {"Authorization": f"Bearer {token}"}}


def _get_user_id(email: str) -> uuid.UUID:
    db = SessionLocal()
    user = db.query(User).filter(User.email == email).first()
    user_id = user.id
    db.close()
    return user_id


def _seed_document_with_chunk(
    user_id: uuid.UUID, subject_id: uuid.UUID | None, content: str, vector: list[float]
) -> uuid.UUID:
    db = SessionLocal()
    document = Document(
        user_id=user_id,
        subject_id=subject_id,
        original_filename="biology_notes.pdf",
        storage_path="/tmp/biology_notes.pdf",
        content_type="application/pdf",
        file_size_bytes=1024,
        extracted_text=content,
        processing_status="completed",
        indexing_status="completed",
    )
    db.add(document)
    db.commit()
    db.refresh(document)
    chunk = DocumentChunk(document_id=document.id, chunk_index=0, content=content, embedding=vector)
    db.add(chunk)
    db.commit()
    document_id = document.id
    db.close()
    return document_id


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
    app.dependency_overrides[get_ai_provider] = lambda: FakeAIProvider()
    yield
    app.dependency_overrides.pop(get_ai_provider, None)


def test_search_finds_subject_by_name(authenticated_user):
    headers = authenticated_user["headers"]
    client.post("/api/v1/subjects", json={"name": "Advanced Databases"}, headers=headers)

    response = client.get("/api/v1/search", params={"q": "databases"}, headers=headers)
    assert response.status_code == 200
    body = response.json()
    assert any(item["result_type"] == "subject" and item["title"] == "Advanced Databases" for item in body["results"])


def test_search_finds_topic_by_title(authenticated_user):
    headers = authenticated_user["headers"]
    subject = client.post("/api/v1/subjects", json={"name": "Databases"}, headers=headers).json()
    client.post(f"/api/v1/subjects/{subject['id']}/topics", json={"title": "Normalization"}, headers=headers)

    response = client.get("/api/v1/search", params={"q": "normal"}, headers=headers)
    body = response.json()
    assert any(item["result_type"] == "topic" and item["title"] == "Normalization" for item in body["results"])


def test_search_finds_document_by_filename(authenticated_user):
    headers = authenticated_user["headers"]
    user_id = _get_user_id(authenticated_user["email"])
    _seed_document_with_chunk(user_id, None, "Some notes about cells.", [0.1] * EMBEDDING_DIMENSIONS)

    response = client.get("/api/v1/search", params={"q": "biology"}, headers=headers)
    body = response.json()
    assert any(item["result_type"] == "document" for item in body["results"])


def test_search_finds_quiz_by_title(authenticated_user, fake_ai):
    headers = authenticated_user["headers"]
    quiz = client.post("/api/v1/quizzes", json={}, headers=headers).json()

    response = client.get("/api/v1/search", params={"q": quiz["title"][:6]}, headers=headers)
    body = response.json()
    assert any(item["result_type"] == "quiz" and item["id"] == quiz["id"] for item in body["results"])


def test_search_finds_flashcard_deck_by_title(authenticated_user):
    headers = authenticated_user["headers"]
    client.post("/api/v1/decks", json={"title": "Spanish Vocabulary"}, headers=headers)

    response = client.get("/api/v1/search", params={"q": "spanish"}, headers=headers)
    body = response.json()
    assert any(item["result_type"] == "flashcard_deck" and item["title"] == "Spanish Vocabulary" for item in body["results"])


def test_search_returns_empty_for_no_matches(authenticated_user):
    response = client.get(
        "/api/v1/search", params={"q": "zzz_no_such_thing_zzz"}, headers=authenticated_user["headers"]
    )
    assert response.json()["results"] == []


def test_search_only_returns_current_users_data(authenticated_user):
    other_user = _register_and_login()
    try:
        client.post("/api/v1/subjects", json={"name": "Secret Subject"}, headers=other_user["headers"])

        response = client.get(
            "/api/v1/search", params={"q": "secret"}, headers=authenticated_user["headers"]
        )
        assert response.json()["results"] == []
    finally:
        db = SessionLocal()
        db.query(User).filter(User.email == other_user["email"]).delete()
        db.commit()
        db.close()


def test_search_requires_authentication():
    response = client.get("/api/v1/search", params={"q": "anything"})
    assert response.status_code == 401


def test_semantic_search_returns_matching_chunks(authenticated_user):
    headers = authenticated_user["headers"]
    user_id = _get_user_id(authenticated_user["email"])
    matching_vector = [0.2] * EMBEDDING_DIMENSIONS
    _seed_document_with_chunk(
        user_id, None, "Photosynthesis converts sunlight into chemical energy.", matching_vector
    )

    app.dependency_overrides[get_embedding_provider] = lambda: FakeEmbeddingProvider(matching_vector)
    try:
        response = client.post(
            "/api/v1/search/semantic", json={"query": "how do plants make energy"}, headers=headers
        )
        assert response.status_code == 200
        body = response.json()
        assert len(body["results"]) == 1
        assert body["results"][0]["similarity_percentage"] == 100
        assert "Photosynthesis" in body["results"][0]["chunk_text"]
    finally:
        app.dependency_overrides.pop(get_embedding_provider, None)


def test_semantic_search_filters_by_subject(authenticated_user):
    headers = authenticated_user["headers"]
    user_id = _get_user_id(authenticated_user["email"])
    subject = client.post("/api/v1/subjects", json={"name": "Biology"}, headers=headers).json()
    vector = [0.3] * EMBEDDING_DIMENSIONS
    _seed_document_with_chunk(user_id, None, "Unrelated general notes.", vector)
    _seed_document_with_chunk(user_id, subject["id"], "Biology specific notes on cells.", vector)

    app.dependency_overrides[get_embedding_provider] = lambda: FakeEmbeddingProvider(vector)
    try:
        response = client.post(
            "/api/v1/search/semantic",
            json={"query": "cells", "subject_id": subject["id"]},
            headers=headers,
        )
        body = response.json()
        assert len(body["results"]) == 1
        assert body["results"][0]["subject_id"] == subject["id"]
    finally:
        app.dependency_overrides.pop(get_embedding_provider, None)


def test_semantic_search_upstream_failure_returns_502(authenticated_user):
    app.dependency_overrides[get_embedding_provider] = lambda: FailingEmbeddingProvider()
    try:
        response = client.post(
            "/api/v1/search/semantic", json={"query": "anything"}, headers=authenticated_user["headers"]
        )
        assert response.status_code == 502
    finally:
        app.dependency_overrides.pop(get_embedding_provider, None)


def test_semantic_search_requires_authentication():
    response = client.post("/api/v1/search/semantic", json={"query": "anything"})
    assert response.status_code == 401