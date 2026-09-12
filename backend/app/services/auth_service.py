import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.exceptions import (
    AccountLockedError,
    EmailAlreadyRegisteredError,
    InactiveUserError,
    InvalidCredentialsError,
)
from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.repositories import user_repository
from app.schemas.user import UserCreate, UserLogin
from app.services import notification_service

settings = get_settings()
security_logger = logging.getLogger("security")


def register_user(db: Session, user_in: UserCreate) -> User:
    existing_user = user_repository.get_by_email(db, user_in.email)
    if existing_user is not None:
        raise EmailAlreadyRegisteredError(user_in.email)

    hashed_password = hash_password(user_in.password)
    user = user_repository.create(db, user_in, hashed_password)
    notification_service.create_welcome_notification(db, user.id)
    return user


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

    if not user.is_active:
        raise InactiveUserError(credentials.email)

    if user.failed_login_attempts != 0 or user.locked_until is not None:
        user_repository.update_login_state(db, user, 0, None)

    return user


def create_token_for_user(user: User) -> str:
    return create_access_token(subject=str(user.id))