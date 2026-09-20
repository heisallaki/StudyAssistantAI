import uuid
from datetime import datetime

from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserCreate


def get_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()


def get_by_id(db: Session, user_id: uuid.UUID) -> User | None:
    return db.query(User).filter(User.id == user_id).first()


def create(db: Session, user_in: UserCreate, hashed_password: str) -> User:
    user = User(email=user_in.email, hashed_password=hashed_password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def update_login_state(
    db: Session, user: User, failed_login_attempts: int, locked_until: datetime | None
) -> None:
    user.failed_login_attempts = failed_login_attempts
    user.locked_until = locked_until
    db.commit()