import uuid
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app.db.session import SessionLocal
from app.main import app
from app.models.user import User
from app.services import auth_service, otp_service

client = TestClient(app)


@pytest.fixture(autouse=True)
def mock_email_sending():
    with patch("app.services.otp_service.email_service.send_email") as mock_send:
        yield mock_send


def _register(email: str, password: str = "S3curePassw0rd!"):
    return client.post("/api/v1/auth/register", json={"email": email, "password": password})


@pytest.fixture
def registered_user(monkeypatch):
    monkeypatch.setattr(otp_service, "_generate_code", lambda: "123456")
    email = f"{uuid.uuid4()}@example.com"
    password = "S3curePassw0rd!"
    _register(email, password)
    yield {"email": email, "password": password}
    db = SessionLocal()
    db.query(User).filter(User.email == email).delete()
    db.commit()
    db.close()


@pytest.fixture
def verified_user(registered_user):
    client.post(
        "/api/v1/auth/verify-email",
        json={"email": registered_user["email"], "code": "123456"},
    )
    return registered_user


@pytest.fixture
def logged_in_user(verified_user):
    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": verified_user["email"], "password": verified_user["password"]},
    )
    token = login_response.json()["access_token"]
    return {**verified_user, "headers": {"Authorization": f"Bearer {token}"}}


def test_register_sends_verification_otp(registered_user, mock_email_sending):
    mock_email_sending.assert_called_once()
    args, _ = mock_email_sending.call_args
    assert args[0] == registered_user["email"]


def test_login_blocked_before_email_verified(registered_user, monkeypatch):
    monkeypatch.setattr(auth_service.settings, "EMAIL_VERIFICATION_REQUIRED", True)

    response = client.post(
        "/api/v1/auth/login",
        json={"email": registered_user["email"], "password": registered_user["password"]},
    )
    assert response.status_code == 403
    assert response.json()["detail"]["error"] == "email_not_verified"


def test_verify_email_with_correct_code_succeeds(registered_user):
    response = client.post(
        "/api/v1/auth/verify-email",
        json={"email": registered_user["email"], "code": "123456"},
    )
    assert response.status_code == 200
    assert response.json()["is_email_verified"] is True


def test_verify_email_with_wrong_code_fails(registered_user):
    response = client.post(
        "/api/v1/auth/verify-email",
        json={"email": registered_user["email"], "code": "000000"},
    )
    assert response.status_code == 400


def test_login_succeeds_after_email_verified(verified_user, monkeypatch):
    monkeypatch.setattr(auth_service.settings, "EMAIL_VERIFICATION_REQUIRED", True)

    response = client.post(
        "/api/v1/auth/login",
        json={"email": verified_user["email"], "password": verified_user["password"]},
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_resend_verification_sends_new_otp(registered_user, mock_email_sending):
    response = client.post("/api/v1/auth/resend-verification", json={"email": registered_user["email"]})
    assert response.status_code == 200
    assert mock_email_sending.call_count == 2


def test_resend_verification_is_silent_for_unknown_email():
    response = client.post(
        "/api/v1/auth/resend-verification", json={"email": f"{uuid.uuid4()}@example.com"}
    )
    assert response.status_code == 200


def test_change_password_flow(logged_in_user, monkeypatch):
    monkeypatch.setattr(otp_service, "_generate_code", lambda: "654321")
    otp_response = client.post(
        "/api/v1/auth/request-password-change-otp", headers=logged_in_user["headers"]
    )
    assert otp_response.status_code == 200

    change_response = client.post(
        "/api/v1/auth/change-password",
        json={
            "current_password": logged_in_user["password"],
            "new_password": "N3wSecurePassw0rd!",
            "code": "654321",
        },
        headers=logged_in_user["headers"],
    )
    assert change_response.status_code == 200

    old_login = client.post(
        "/api/v1/auth/login",
        json={"email": logged_in_user["email"], "password": logged_in_user["password"]},
    )
    assert old_login.status_code == 401

    new_login = client.post(
        "/api/v1/auth/login",
        json={"email": logged_in_user["email"], "password": "N3wSecurePassw0rd!"},
    )
    assert new_login.status_code == 200


def test_change_password_rejects_wrong_current_password(logged_in_user, monkeypatch):
    monkeypatch.setattr(otp_service, "_generate_code", lambda: "654321")
    client.post("/api/v1/auth/request-password-change-otp", headers=logged_in_user["headers"])

    response = client.post(
        "/api/v1/auth/change-password",
        json={
            "current_password": "totally-wrong-password",
            "new_password": "N3wSecurePassw0rd!",
            "code": "654321",
        },
        headers=logged_in_user["headers"],
    )
    assert response.status_code == 401


def test_change_password_rejects_wrong_otp(logged_in_user, monkeypatch):
    monkeypatch.setattr(otp_service, "_generate_code", lambda: "654321")
    client.post("/api/v1/auth/request-password-change-otp", headers=logged_in_user["headers"])

    response = client.post(
        "/api/v1/auth/change-password",
        json={
            "current_password": logged_in_user["password"],
            "new_password": "N3wSecurePassw0rd!",
            "code": "000000",
        },
        headers=logged_in_user["headers"],
    )
    assert response.status_code == 400


def test_delete_own_account_flow(logged_in_user, monkeypatch):
    monkeypatch.setattr(otp_service, "_generate_code", lambda: "789012")
    otp_response = client.post(
        "/api/v1/auth/request-account-deletion-otp", headers=logged_in_user["headers"]
    )
    assert otp_response.status_code == 200

    delete_response = client.request(
        "DELETE",
        "/api/v1/auth/me",
        json={"code": "789012"},
        headers=logged_in_user["headers"],
    )
    assert delete_response.status_code == 204

    db = SessionLocal()
    remaining = db.query(User).filter(User.email == logged_in_user["email"]).first()
    db.close()
    assert remaining is None


def test_delete_own_account_rejects_wrong_otp(logged_in_user, monkeypatch):
    monkeypatch.setattr(otp_service, "_generate_code", lambda: "789012")
    client.post("/api/v1/auth/request-account-deletion-otp", headers=logged_in_user["headers"])

    response = client.request(
        "DELETE",
        "/api/v1/auth/me",
        json={"code": "000000"},
        headers=logged_in_user["headers"],
    )
    assert response.status_code == 400


def test_delete_own_account_blocks_last_administrator(logged_in_user, monkeypatch):
    db = SessionLocal()
    user = db.query(User).filter(User.email == logged_in_user["email"]).first()
    user.is_superuser = True
    db.commit()
    db.close()

    monkeypatch.setattr(otp_service, "_generate_code", lambda: "789012")
    client.post("/api/v1/auth/request-account-deletion-otp", headers=logged_in_user["headers"])

    response = client.request(
        "DELETE",
        "/api/v1/auth/me",
        json={"code": "789012"},
        headers=logged_in_user["headers"],
    )
    assert response.status_code == 400