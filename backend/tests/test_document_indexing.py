import io
import uuid

import pytest
from fastapi.testclient import TestClient

from app.ai.providers.embedding_base import EmbeddingProvider, EmbeddingProviderError
from app.api.deps import get_embedding_provider
from app.db.session import SessionLocal
from app.main import app
from app.models.document_chunk import DocumentChunk
from app.models.user import User

client = TestClient(app)


class FakeEmbeddingProvider(EmbeddingProvider):
    async def embed(self, texts: list[str]) -> list[list[float]]:
        return [self._fake_vector(text) for text in texts]

    @staticmethod
    def _fake_vector(text: str) -> list[float]:
        vector = [0.0] * 384
        lowered = text.lower()
        if "database" in lowered or "normalization" in lowered:
            vector[0] = 1.0
        elif "cooking" in lowered:
            vector[1] = 1.0
        else:
            vector[2] = 1.0
        return vector


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


@pytest.fixture
def authenticated_user():
    user = _register_and_login()
    yield user
    db = SessionLocal()
    db.query(User).filter(User.email == user["email"]).delete()
    db.commit()
    db.close()


@pytest.fixture
def fake_embeddings():
    provider = FakeEmbeddingProvider()
    app.dependency_overrides[get_embedding_provider] = lambda: provider
    yield provider
    app.dependency_overrides.pop(get_embedding_provider, None)


@pytest.fixture
def failing_embeddings():
    app.dependency_overrides[get_embedding_provider] = lambda: FailingEmbeddingProvider()
    yield
    app.dependency_overrides.pop(get_embedding_provider, None)


def _upload_text(headers, content: bytes, filename="notes.txt"):
    return client.post(
        "/api/v1/documents",
        files={"file": (filename, io.BytesIO(content), "text/plain")},
        headers=headers,
    )


def test_upload_indexes_document_when_embeddings_available(authenticated_user, fake_embeddings):
    response = _upload_text(
        authenticated_user["headers"],
        b"Chapter 1: Database normalization explained in detail.",
    )
    assert response.status_code == 201
    body = response.json()
    assert body["indexing_status"] == "indexed"
    assert body["indexing_error"] is None


def test_upload_marks_indexing_failed_when_embeddings_unavailable(authenticated_user, failing_embeddings):
    response = _upload_text(
        authenticated_user["headers"],
        b"Chapter 1: Database normalization explained in detail.",
    )
    assert response.status_code == 201
    body = response.json()
    assert body["processing_status"] == "processed"
    assert body["indexing_status"] == "failed"
    assert body["indexing_error"] is not None


def test_reindex_recovers_after_embeddings_become_available(authenticated_user, failing_embeddings):
    response = _upload_text(
        authenticated_user["headers"],
        b"Chapter 1: Database normalization explained in detail.",
    )
    document_id = response.json()["id"]
    assert response.json()["indexing_status"] == "failed"

    app.dependency_overrides[get_embedding_provider] = lambda: FakeEmbeddingProvider()
    try:
        reindex_response = client.post(
            f"/api/v1/documents/{document_id}/reindex", headers=authenticated_user["headers"]
        )
    finally:
        app.dependency_overrides.pop(get_embedding_provider, None)

    assert reindex_response.status_code == 200
    assert reindex_response.json()["indexing_status"] == "indexed"


def test_reindex_rejects_document_with_no_extracted_text(authenticated_user, fake_embeddings):
    minimal_empty_pdf = (
        b"%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n"
        b"2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n"
        b"3 0 obj<</Type/Page/Parent 2 0 R/MediaBox[0 0 612 792]>>endobj\n"
        b"xref\n0 4\n0000000000 65535 f \n"
        b"trailer<</Size 4/Root 1 0 R>>\nstartxref\n0\n%%EOF"
    )
    upload_response = client.post(
        "/api/v1/documents",
        files={"file": ("scan.pdf", io.BytesIO(minimal_empty_pdf), "application/pdf")},
        headers=authenticated_user["headers"],
    )
    document_id = upload_response.json()["id"]
    assert upload_response.json()["indexing_status"] == "not_applicable"

    response = client.post(
        f"/api/v1/documents/{document_id}/reindex", headers=authenticated_user["headers"]
    )
    assert response.status_code == 422


def test_deleting_document_removes_its_chunks(authenticated_user, fake_embeddings):
    upload_response = _upload_text(
        authenticated_user["headers"],
        b"Chapter 1: Database normalization explained in detail.",
    )
    document_id = upload_response.json()["id"]

    client.delete(f"/api/v1/documents/{document_id}", headers=authenticated_user["headers"])

    db = SessionLocal()
    remaining = db.query(DocumentChunk).filter(DocumentChunk.document_id == uuid.UUID(document_id)).count()
    db.close()
    assert remaining == 0