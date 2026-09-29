import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.exceptions import (
    AccountLockedError,
    EmailAlreadyRegisteredError,
    EmailNotVerifiedError,
    InactiveUserError,
    InvalidCredentialsError,
    InvalidCurrentPasswordError,
    LastAdministratorError,
)
from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.repositories import admin_repository, user_repository
from app.schemas.user import PasswordChangeRequest, UserCreate, UserLogin
from app.services import notification_service, otp_service
from app.services.email_service import EmailSendError

settings = get_settings()
security_logger = logging.getLogger("security")


def register_user(db: Session, user_in: UserCreate) -> User:
    existing_user = user_repository.get_by_email(db, user_in.email)
    if existing_user is not None:
        raise EmailAlreadyRegisteredError(user_in.email)

    hashed_password = hash_password(user_in.password)
    user = user_repository.create(db, user_in, hashed_password)
    notification_service.create_welcome_notification(db, user.id)

    try:
        otp_service.request_otp(db, user, otp_service.PURPOSE_EMAIL_VERIFICATION)
    except EmailSendError as error:
        security_logger.warning("Could not send verification email to %s: %s", user.email, error)

    return user


def verify_email(db: Session, email: str, code: str) -> User:
    user = user_repository.get_by_email(db, email)
    if user is None:
        raise InvalidCredentialsError(email)

    otp_service.verify_otp(db, user, otp_service.PURPOSE_EMAIL_VERIFICATION, code)
    user_repository.mark_email_verified(db, user)
    return user


def resend_verification_email(db: Session, email: str) -> None:
    user = user_repository.get_by_email(db, email)
    if user is None or user.is_email_verified:
        return
    otp_service.request_otp(db, user, otp_service.PURPOSE_EMAIL_VERIFICATION)


def authenticate_user(db: Session, credentials: UserLogin) -> User:
    user = user_repository.get_by_email(db, credentials.email)
    if user is None:
        raise InvalidCredentialsError(credentials.email)

    now = datetime.now(timezone.utc)
    locked_until = user.locked_until
    if locked_until is not None and locked_until.tzinfo is None:
        locked_until = locked_until.replace(tzinfo=timezone.utc)
    if locked_until is not None and locked_until > now:
        security_logger.warning("Login blocked for locked account: %s", user.email)
        raise AccountLockedError(credentials.email)

    if not verify_password(credentials.password, user.hashed_password):
        failed_attempts = user.failed_login_attempts + 1
        locked_until = None
        if failed_attempts >= settings.FAILED_LOGIN_LOCKOUT_THRESHOLD:
            locked_until = now + timedelta(minutes=settings.FAILED_LOGIN_LOCKOUT_MINUTES)
            security_logger.warning("Account locked after repeated failed logins: %s", user.email)
        user_repository.update_login_state(db, user, failed_attempts, locked_until)
        raise InvalidCredentialsError(credentials.email)

    if settings.EMAIL_VERIFICATION_REQUIRED and not user.is_email_verified:
        raise EmailNotVerifiedError(credentials.email)

    if not user.is_active:
        raise InactiveUserError(credentials.email)

    if user.failed_login_attempts != 0 or user.locked_until is not None:
        user_repository.update_login_state(db, user, 0, None)

    return user


def create_token_for_user(user: User) -> str:
    return create_access_token(subject=str(user.id))


def request_password_change_otp(db: Session, user: User) -> None:
    otp_service.request_otp(db, user, otp_service.PURPOSE_PASSWORD_CHANGE)


def change_password(db: Session, user: User, data: PasswordChangeRequest) -> None:
    if not verify_password(data.current_password, user.hashed_password):
        raise InvalidCurrentPasswordError(user.email)

    otp_service.verify_otp(db, user, otp_service.PURPOSE_PASSWORD_CHANGE, data.code)

    new_hashed_password = hash_password(data.new_password)
    user_repository.update_password(db, user, new_hashed_password)
    security_logger.info("Password changed for user %s", user.email)


def request_account_deletion_otp(db: Session, user: User) -> None:
    otp_service.request_otp(db, user, otp_service.PURPOSE_ACCOUNT_DELETION)


def delete_own_account(db: Session, user: User, code: str) -> None:
    otp_service.verify_otp(db, user, otp_service.PURPOSE_ACCOUNT_DELETION, code)

    if user.is_superuser and admin_repository.count_admins(db) <= 1:
        raise LastAdministratorError(user.email)

    security_logger.info("Account deleted by owner: %s", user.email)
    user_repository.delete(db, user)