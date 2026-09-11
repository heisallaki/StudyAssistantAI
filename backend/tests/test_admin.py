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


def _promote_to_admin(email: str) -> None:
    db = SessionLocal()
    user = db.query(User).filter(User.email == email).first()
    user.is_superuser = True
    db.commit()
    db.close()


@pytest.fixture
def admin_user():
    user = _register_and_login()
    _promote_to_admin(user["email"])
    yield user
    db = SessionLocal()
    db.query(User).filter(User.email == user["email"]).delete()
    db.commit()
    db.close()


@pytest.fixture
def regular_user():
    user = _register_and_login()
    yield user
    db = SessionLocal()
    db.query(User).filter(User.email == user["email"]).delete()
    db.commit()
    db.close()


def test_admin_endpoints_reject_unauthenticated_requests():
    response = client.get("/api/v1/admin/users")
    assert response.status_code == 401


def test_admin_endpoints_reject_non_admin_users(regular_user):
    response = client.get("/api/v1/admin/users", headers=regular_user["headers"])
    assert response.status_code == 403


def test_admin_can_list_users(admin_user, regular_user):
    response = client.get("/api/v1/admin/users", headers=admin_user["headers"])
    assert response.status_code == 200
    body = response.json()
    emails = [item["email"] for item in body["items"]]
    assert admin_user["email"] in emails
    assert regular_user["email"] in emails
    assert body["total"] >= 2


def test_admin_can_search_users_by_email(admin_user, regular_user):
    response = client.get(
        "/api/v1/admin/users",
        params={"search": regular_user["email"]},
        headers=admin_user["headers"],
    )
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert body["items"][0]["email"] == regular_user["email"]


def test_admin_can_get_single_user(admin_user, regular_user):
    list_response = client.get(
        "/api/v1/admin/users",
        params={"search": regular_user["email"]},
        headers=admin_user["headers"],
    )
    user_id = list_response.json()["items"][0]["id"]

    response = client.get(f"/api/v1/admin/users/{user_id}", headers=admin_user["headers"])
    assert response.status_code == 200
    body = response.json()
    assert body["email"] == regular_user["email"]
    assert body["is_active"] is True
    assert body["is_superuser"] is False
    assert body["subject_count"] == 0


def test_admin_get_user_returns_404_for_missing_user(admin_user):
    response = client.get(f"/api/v1/admin/users/{uuid.uuid4()}", headers=admin_user["headers"])
    assert response.status_code == 404


def test_admin_can_deactivate_and_reactivate_user(admin_user, regular_user):
    list_response = client.get(
        "/api/v1/admin/users",
        params={"search": regular_user["email"]},
        headers=admin_user["headers"],
    )
    user_id = list_response.json()["items"][0]["id"]

    deactivate_response = client.patch(
        f"/api/v1/admin/users/{user_id}",
        json={"is_active": False},
        headers=admin_user["headers"],
    )
    assert deactivate_response.status_code == 200
    assert deactivate_response.json()["is_active"] is False

    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": regular_user["email"], "password": "S3curePassw0rd!"},
    )
    assert login_response.status_code == 403

    reactivate_response = client.patch(
        f"/api/v1/admin/users/{user_id}",
        json={"is_active": True},
        headers=admin_user["headers"],
    )
    assert reactivate_response.status_code == 200
    assert reactivate_response.json()["is_active"] is True


def test_admin_can_grant_and_revoke_admin_access(admin_user, regular_user):
    list_response = client.get(
        "/api/v1/admin/users",
        params={"search": regular_user["email"]},
        headers=admin_user["headers"],
    )
    user_id = list_response.json()["items"][0]["id"]

    grant_response = client.patch(
        f"/api/v1/admin/users/{user_id}",
        json={"is_superuser": True},
        headers=admin_user["headers"],
    )
    assert grant_response.status_code == 200
    assert grant_response.json()["is_superuser"] is True

    revoke_response = client.patch(
        f"/api/v1/admin/users/{user_id}",
        json={"is_superuser": False},
        headers=admin_user["headers"],
    )
    assert revoke_response.status_code == 200
    assert revoke_response.json()["is_superuser"] is False


def test_admin_cannot_deactivate_own_account(admin_user):
    me_response = client.get("/api/v1/auth/me", headers=admin_user["headers"])
    user_id = me_response.json()["id"]

    response = client.patch(
        f"/api/v1/admin/users/{user_id}",
        json={"is_active": False},
        headers=admin_user["headers"],
    )
    assert response.status_code == 400


def test_admin_cannot_revoke_own_admin_access(admin_user):
    me_response = client.get("/api/v1/auth/me", headers=admin_user["headers"])
    user_id = me_response.json()["id"]

    response = client.patch(
        f"/api/v1/admin/users/{user_id}",
        json={"is_superuser": False},
        headers=admin_user["headers"],
    )
    assert response.status_code == 400


def test_admin_cannot_delete_own_account(admin_user):
    me_response = client.get("/api/v1/auth/me", headers=admin_user["headers"])
    user_id = me_response.json()["id"]

    response = client.delete(f"/api/v1/admin/users/{user_id}", headers=admin_user["headers"])
    assert response.status_code == 400


def test_admin_can_delete_another_user(admin_user, regular_user):
    list_response = client.get(
        "/api/v1/admin/users",
        params={"search": regular_user["email"]},
        headers=admin_user["headers"],
    )
    user_id = list_response.json()["items"][0]["id"]

    delete_response = client.delete(f"/api/v1/admin/users/{user_id}", headers=admin_user["headers"])
    assert delete_response.status_code == 204

    get_response = client.get(f"/api/v1/admin/users/{user_id}", headers=admin_user["headers"])
    assert get_response.status_code == 404


def test_admin_stats_returns_system_counts(admin_user, regular_user):
    response = client.get("/api/v1/admin/stats", headers=admin_user["headers"])
    assert response.status_code == 200
    body = response.json()
    assert body["total_users"] >= 2
    assert body["admin_users"] >= 1
    assert "total_subjects" in body
    assert "total_documents" in body