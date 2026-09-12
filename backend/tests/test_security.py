import uuid

import pytest
from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.db.session import SessionLocal
from app.main import app
from app.models.user import User

client = TestClient(app)
settings = get_settings()


def _register_and_login():
    email = f"{uuid.uuid4()}@example.com"
    password = "S3curePassw0rd!"
    client.post("/api/v1/auth/register", json={"email": email, "password": password})
    login_response = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    token = login_response.json()["access_token"]
    return {"email": email, "password": password, "headers": {"Authorization": f"Bearer {token}"}}


def _promote_to_admin(email: str) -> None:
    db = SessionLocal()
    user = db.query(User).filter(User.email == email).first()
    user.is_superuser = True
    db.commit()
    db.close()


def _cleanup_user(email: str) -> None:
    db = SessionLocal()
    db.query(User).filter(User.email == email).delete()
    db.commit()
    db.close()


@pytest.fixture
def admin_user():
    user = _register_and_login()
    _promote_to_admin(user["email"])
    yield user
    _cleanup_user(user["email"])


@pytest.fixture
def regular_user():
    user = _register_and_login()
    yield user
    _cleanup_user(user["email"])


@pytest.mark.parametrize(
    "weak_password",
    [
        "alllowercase1!",
        "ALLUPPERCASE1!",
        "NoDigitsHere!",
        "NoSpecial1234",
        "Short1!",
    ],
)
def test_registration_rejects_weak_passwords(weak_password):
    email = f"{uuid.uuid4()}@example.com"
    response = client.post("/api/v1/auth/register", json={"email": email, "password": weak_password})
    assert response.status_code == 422


def test_registration_accepts_strong_password():
    email = f"{uuid.uuid4()}@example.com"
    password = "S3curePassw0rd!"
    response = client.post("/api/v1/auth/register", json={"email": email, "password": password})
    assert response.status_code == 201
    _cleanup_user(email)


def test_account_locks_after_repeated_failed_logins():
    email = f"{uuid.uuid4()}@example.com"
    password = "S3curePassw0rd!"
    client.post("/api/v1/auth/register", json={"email": email, "password": password})

    for _ in range(settings.FAILED_LOGIN_LOCKOUT_THRESHOLD):
        response = client.post(
            "/api/v1/auth/login",
            json={"email": email, "password": "wrong-password"},
        )
        assert response.status_code == 401

    locked_response = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert locked_response.status_code == 423

    _cleanup_user(email)


def test_successful_login_resets_failed_attempts():
    email = f"{uuid.uuid4()}@example.com"
    password = "S3curePassw0rd!"
    client.post("/api/v1/auth/register", json={"email": email, "password": password})

    for _ in range(settings.FAILED_LOGIN_LOCKOUT_THRESHOLD - 1):
        client.post("/api/v1/auth/login", json={"email": email, "password": "wrong-password"})

    success_response = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert success_response.status_code == 200

    for _ in range(settings.FAILED_LOGIN_LOCKOUT_THRESHOLD - 1):
        response = client.post("/api/v1/auth/login", json={"email": email, "password": "wrong-password"})
        assert response.status_code == 401

    still_unlocked_response = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert still_unlocked_response.status_code == 200

    _cleanup_user(email)


def test_security_headers_present_on_response():
    response = client.get("/api/v1/health")
    assert response.headers.get("x-content-type-options") == "nosniff"
    assert response.headers.get("x-frame-options") == "DENY"
    assert response.headers.get("referrer-policy") == "strict-origin-when-cross-origin"
    assert "permissions-policy" in response.headers


def test_rate_limiter_disabled_during_tests():
    from app.core.rate_limit import limiter

    assert limiter.enabled is False


def test_audit_log_requires_admin(regular_user):
    response = client.get("/api/v1/admin/audit-log", headers=regular_user["headers"])
    assert response.status_code == 403


def test_admin_user_actions_are_audit_logged(admin_user, regular_user):
    list_response = client.get(
        "/api/v1/admin/users",
        params={"search": regular_user["email"]},
        headers=admin_user["headers"],
    )
    user_id = list_response.json()["items"][0]["id"]

    client.patch(
        f"/api/v1/admin/users/{user_id}",
        json={"is_active": False},
        headers=admin_user["headers"],
    )

    audit_response = client.get("/api/v1/admin/audit-log", headers=admin_user["headers"])
    assert audit_response.status_code == 200
    entries = audit_response.json()["items"]

    matching_entries = [
        entry
        for entry in entries
        if entry["target_email"] == regular_user["email"] and entry["action"] == "deactivate_user"
    ]
    assert len(matching_entries) == 1
    assert matching_entries[0]["actor_email"] == admin_user["email"]