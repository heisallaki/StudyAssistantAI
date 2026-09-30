import hashlib
import logging
import secrets
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.exceptions import OtpExpiredError, OtpInvalidError, OtpNotFoundError, OtpTooManyAttemptsError
from app.models.user import User
from app.repositories import otp_repository
from app.services import email_service

logger = logging.getLogger(__name__)
security_logger = logging.getLogger("security")

settings = get_settings()

PURPOSE_EMAIL_VERIFICATION = "email_verification"
PURPOSE_PASSWORD_CHANGE = "password_change"
PURPOSE_ACCOUNT_DELETION = "account_deletion"
PURPOSE_PASSWORD_RESET = "password_reset"

_SUBJECTS = {
    PURPOSE_EMAIL_VERIFICATION: "Verify your StudyAssistant AI account",
    PURPOSE_PASSWORD_CHANGE: "Confirm your password change",
    PURPOSE_ACCOUNT_DELETION: "Confirm your account deletion",
    PURPOSE_PASSWORD_RESET: "Reset your StudyAssistant AI password",
}

_INTROS = {
    PURPOSE_EMAIL_VERIFICATION: "Use this code to verify your email address and activate your account.",
    PURPOSE_PASSWORD_CHANGE: "Use this code to confirm you want to change your password.",
    PURPOSE_ACCOUNT_DELETION: "Use this code to confirm you want to permanently delete your account.",
    PURPOSE_PASSWORD_RESET: "Use this code to reset your password.",
}


def _generate_code() -> str:
    return "".join(secrets.choice("0123456789") for _ in range(settings.OTP_LENGTH))


def _hash_code(code: str) -> str:
    return hashlib.sha256(code.encode("utf-8")).hexdigest()


def _build_email_body(purpose: str, code: str) -> str:
    intro = _INTROS.get(purpose, "Use this code to confirm your request.")
    return (
        f"{intro}\n\n"
        f"Your verification code is: {code}\n\n"
        f"This code expires in {settings.OTP_EXPIRE_MINUTES} minutes. "
        "If you did not request this, you can safely ignore this email."
    )


def request_otp(db: Session, user: User, purpose: str) -> None:
    otp_repository.delete_active_for_purpose(db, user.id, purpose)

    code = _generate_code()
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.OTP_EXPIRE_MINUTES)
    otp_repository.create(db, user.id, purpose, _hash_code(code), expires_at)

    subject = _SUBJECTS.get(purpose, "Your StudyAssistant AI verification code")
    body = _build_email_body(purpose, code)
    email_service.send_email(user.email, subject, body)

    security_logger.info("OTP requested for user %s, purpose %s", user.email, purpose)


def verify_otp(db: Session, user: User, purpose: str, code: str) -> None:
    otp = otp_repository.get_latest_active(db, user.id, purpose)
    if otp is None:
        raise OtpNotFoundError(purpose)

    now = datetime.now(timezone.utc)
    expires_at = otp.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    if expires_at < now:
        raise OtpExpiredError(purpose)

    if otp.attempts >= settings.OTP_MAX_ATTEMPTS:
        raise OtpTooManyAttemptsError(purpose)

    if _hash_code(code) != otp.code_hash:
        otp_repository.increment_attempts(db, otp)
        security_logger.warning("Invalid OTP attempt for user %s, purpose %s", user.email, purpose)
        raise OtpInvalidError(purpose)

    otp_repository.mark_consumed(db, otp)