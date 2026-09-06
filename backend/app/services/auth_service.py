from sqlalchemy.orm import Session

from app.core.exceptions import EmailAlreadyRegisteredError, InactiveUserError, InvalidCredentialsError
from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.repositories import user_repository
from app.schemas.user import UserCreate, UserLogin
from app.services import notification_service


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
    if user is None or not verify_password(credentials.password, user.hashed_password):
        raise InvalidCredentialsError(credentials.email)
    if not user.is_active:
        raise InactiveUserError(credentials.email)
    return user


def create_token_for_user(user: User) -> str:
    return create_access_token(subject=str(user.id))