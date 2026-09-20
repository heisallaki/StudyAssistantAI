import io
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


def _upload_text_file(headers, content=b"Chapter 1: Normal forms in relational databases.", filename="notes.txt"):
    return client.post(
        "/api/v1/documents",
        files={"file": (filename, io.BytesIO(content), "text/plain")},
        headers=headers,
    )


def test_list_documents_starts_empty(authenticated_user):
    response = client.get("/api/v1/documents", headers=authenticated_user["headers"])
    assert response.status_code == 200
    assert response.json() == []


def test_upload_text_document_extracts_text(authenticated_user):
    response = _upload_text_file(authenticated_user["headers"])
    assert response.status_code == 201
    body = response.json()
    assert body["original_filename"] == "notes.txt"
    assert body["processing_status"] == "processed"
    assert body["processing_error"] is None
    assert "Normal forms" in body["extracted_text"]
    assert body["file_size_bytes"] > 0


def test_upload_rejects_unsupported_extension(authenticated_user):
    response = client.post(
        "/api/v1/documents",
        files={"file": ("virus.exe", io.BytesIO(b"not a real exe"), "application/octet-stream")},
        headers=authenticated_user["headers"],
    )
    assert response.status_code == 422


def test_upload_rejects_oversized_file(authenticated_user):
    oversized_content = b"x" * (21 * 1024 * 1024)
    response = client.post(
        "/api/v1/documents",
        files={"file": ("big.txt", io.BytesIO(oversized_content), "text/plain")},
        headers=authenticated_user["headers"],
    )
    assert response.status_code == 413


def test_upload_empty_pdf_marks_processing_failed(authenticated_user):
    minimal_empty_pdf = (
        b"%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n"
        b"2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n"
        b"3 0 obj<</Type/Page/Parent 2 0 R/MediaBox[0 0 612 792]>>endobj\n"
        b"xref\n0 4\n0000000000 65535 f \n"
        b"trailer<</Size 4/Root 1 0 R>>\nstartxref\n0\n%%EOF"
    )
    response = client.post(
        "/api/v1/documents",
        files={"file": ("scan.pdf", io.BytesIO(minimal_empty_pdf), "application/pdf")},
        headers=authenticated_user["headers"],
    )
    assert response.status_code == 201
    body = response.json()
    assert body["processing_status"] == "failed"
    assert body["extracted_text"] is None
    assert body["processing_error"] is not None


def test_list_documents_returns_uploaded_document(authenticated_user):
    _upload_text_file(authenticated_user["headers"])
    response = client.get("/api/v1/documents", headers=authenticated_user["headers"])
    assert response.status_code == 200
    filenames = [doc["original_filename"] for doc in response.json()]
    assert "notes.txt" in filenames


def test_list_documents_does_not_include_extracted_text(authenticated_user):
    _upload_text_file(authenticated_user["headers"])
    response = client.get("/api/v1/documents", headers=authenticated_user["headers"])
    assert "extracted_text" not in response.json()[0]


def test_get_document_detail_includes_extracted_text(authenticated_user):
    upload_response = _upload_text_file(authenticated_user["headers"])
    document_id = upload_response.json()["id"]
    response = client.get(f"/api/v1/documents/{document_id}", headers=authenticated_user["headers"])
    assert response.status_code == 200
    assert "Normal forms" in response.json()["extracted_text"]


def test_download_document_returns_original_content(authenticated_user):
    original_bytes = b"Chapter 1: Normal forms in relational databases."
    upload_response = _upload_text_file(authenticated_user["headers"], content=original_bytes)
    document_id = upload_response.json()["id"]

    response = client.get(
        f"/api/v1/documents/{document_id}/download", headers=authenticated_user["headers"]
    )
    assert response.status_code == 200
    assert response.content == original_bytes


def test_delete_document(authenticated_user):
    upload_response = _upload_text_file(authenticated_user["headers"])
    document_id = upload_response.json()["id"]

    delete_response = client.delete(
        f"/api/v1/documents/{document_id}", headers=authenticated_user["headers"]
    )
    assert delete_response.status_code == 204

    get_response = client.get(f"/api/v1/documents/{document_id}", headers=authenticated_user["headers"])
    assert get_response.status_code == 404


def test_upload_document_with_subject_association(authenticated_user):
    subject_response = client.post(
        "/api/v1/subjects", json={"name": "Databases"}, headers=authenticated_user["headers"]
    )
    subject_id = subject_response.json()["id"]

    response = client.post(
        "/api/v1/documents",
        files={"file": ("notes.txt", io.BytesIO(b"Some notes"), "text/plain")},
        data={"subject_id": subject_id},
        headers=authenticated_user["headers"],
    )
    assert response.status_code == 201
    assert response.json()["subject_id"] == subject_id


def test_upload_document_rejects_another_users_subject(authenticated_user, other_authenticated_user):
    subject_response = client.post(
        "/api/v1/subjects", json={"name": "Private Subject"}, headers=authenticated_user["headers"]
    )
    subject_id = subject_response.json()["id"]

    response = client.post(
        "/api/v1/documents",
        files={"file": ("notes.txt", io.BytesIO(b"Some notes"), "text/plain")},
        data={"subject_id": subject_id},
        headers=other_authenticated_user["headers"],
    )
    assert response.status_code == 404


def test_deleting_subject_nulls_out_document_subject_id(authenticated_user):
    subject_response = client.post(
        "/api/v1/subjects", json={"name": "Databases"}, headers=authenticated_user["headers"]
    )
    subject_id = subject_response.json()["id"]

    upload_response = client.post(
        "/api/v1/documents",
        files={"file": ("notes.txt", io.BytesIO(b"Some notes"), "text/plain")},
        data={"subject_id": subject_id},
        headers=authenticated_user["headers"],
    )
    document_id = upload_response.json()["id"]

    client.delete(f"/api/v1/subjects/{subject_id}", headers=authenticated_user["headers"])

    response = client.get(f"/api/v1/documents/{document_id}", headers=authenticated_user["headers"])
    assert response.status_code == 200
    assert response.json()["subject_id"] is None


def test_user_cannot_access_another_users_document(authenticated_user, other_authenticated_user):
    upload_response = _upload_text_file(authenticated_user["headers"])
    document_id = upload_response.json()["id"]

    response = client.get(
        f"/api/v1/documents/{document_id}", headers=other_authenticated_user["headers"]
    )
    assert response.status_code == 404


def test_documents_require_authentication():
    response = client.get("/api/v1/documents")
    assert response.status_code == 401