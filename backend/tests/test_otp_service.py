import uuid
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import pytest

from app.core.exceptions import OtpExpiredError, OtpInvalidError, OtpNotFoundError, OtpTooManyAttemptsError
from app.db.session import SessionLocal
from app.models.user import User
from app.services import otp_service
from app.services.email_service import EmailSendError


def _create_user(db) -> User:
    user = User(
        email=f"{uuid.uuid4()}@example.com",
        hashed_password="not-a-real-hash",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def db_session():
    db = SessionLocal()
    yield db
    db.close()


@pytest.fixture
def user(db_session):
    created = _create_user(db_session)
    yield created
    db_session.query(User).filter(User.id == created.id).delete()
    db_session.commit()


def test_request_otp_creates_code_and_sends_email(db_session, user):
    with patch("app.services.otp_service.email_service.send_email") as mock_send:
        otp_service.request_otp(db_session, user, otp_service.PURPOSE_EMAIL_VERIFICATION)

    mock_send.assert_called_once()
    args, _ = mock_send.call_args
    assert args[0] == user.email


def test_verify_otp_succeeds_with_correct_code(db_session, user, monkeypatch):
    monkeypatch.setattr(otp_service, "_generate_code", lambda: "123456")
    with patch("app.services.otp_service.email_service.send_email"):
        otp_service.request_otp(db_session, user, otp_service.PURPOSE_EMAIL_VERIFICATION)

    otp_service.verify_otp(db_session, user, otp_service.PURPOSE_EMAIL_VERIFICATION, "123456")


def test_verify_otp_rejects_wrong_code(db_session, user, monkeypatch):
    monkeypatch.setattr(otp_service, "_generate_code", lambda: "123456")
    with patch("app.services.otp_service.email_service.send_email"):
        otp_service.request_otp(db_session, user, otp_service.PURPOSE_EMAIL_VERIFICATION)

    with pytest.raises(OtpInvalidError):
        otp_service.verify_otp(db_session, user, otp_service.PURPOSE_EMAIL_VERIFICATION, "000000")


def test_verify_otp_raises_when_none_requested(db_session, user):
    with pytest.raises(OtpNotFoundError):
        otp_service.verify_otp(db_session, user, otp_service.PURPOSE_PASSWORD_CHANGE, "123456")


def test_verify_otp_raises_when_expired(db_session, user, monkeypatch):
    monkeypatch.setattr(otp_service, "_generate_code", lambda: "123456")
    with patch("app.services.otp_service.email_service.send_email"):
        otp_service.request_otp(db_session, user, otp_service.PURPOSE_EMAIL_VERIFICATION)

    otp = otp_service.otp_repository.get_latest_active(db_session, user.id, otp_service.PURPOSE_EMAIL_VERIFICATION)
    otp.expires_at = datetime.now(timezone.utc) - timedelta(minutes=1)
    db_session.commit()

    with pytest.raises(OtpExpiredError):
        otp_service.verify_otp(db_session, user, otp_service.PURPOSE_EMAIL_VERIFICATION, "123456")


def test_verify_otp_locks_out_after_max_attempts(db_session, user, monkeypatch):
    monkeypatch.setattr(otp_service, "_generate_code", lambda: "123456")
    monkeypatch.setattr(otp_service.settings, "OTP_MAX_ATTEMPTS", 2)
    with patch("app.services.otp_service.email_service.send_email"):
        otp_service.request_otp(db_session, user, otp_service.PURPOSE_EMAIL_VERIFICATION)

    for _ in range(2):
        with pytest.raises(OtpInvalidError):
            otp_service.verify_otp(db_session, user, otp_service.PURPOSE_EMAIL_VERIFICATION, "000000")

    with pytest.raises(OtpTooManyAttemptsError):
        otp_service.verify_otp(db_session, user, otp_service.PURPOSE_EMAIL_VERIFICATION, "123456")


def test_requesting_new_otp_invalidates_previous_one(db_session, user, monkeypatch):
    codes = iter(["111111", "222222"])
    monkeypatch.setattr(otp_service, "_generate_code", lambda: next(codes))
    with patch("app.services.otp_service.email_service.send_email"):
        otp_service.request_otp(db_session, user, otp_service.PURPOSE_EMAIL_VERIFICATION)
        otp_service.request_otp(db_session, user, otp_service.PURPOSE_EMAIL_VERIFICATION)

    with pytest.raises(OtpInvalidError):
        otp_service.verify_otp(db_session, user, otp_service.PURPOSE_EMAIL_VERIFICATION, "111111")

    otp_service.verify_otp(db_session, user, otp_service.PURPOSE_EMAIL_VERIFICATION, "222222")


def test_request_otp_propagates_email_send_error(db_session, user):
    with patch("app.services.otp_service.email_service.send_email", side_effect=EmailSendError("boom")):
        with pytest.raises(EmailSendError):
            otp_service.request_otp(db_session, user, otp_service.PURPOSE_EMAIL_VERIFICATION)