import uuid

from sqlalchemy.orm import Session

from app.models.user_profile import UserProfile


def get_by_user_id(db: Session, user_id: uuid.UUID) -> UserProfile | None:
    return db.query(UserProfile).filter(UserProfile.user_id == user_id).first()


def create_blank(db: Session, user_id: uuid.UUID) -> UserProfile:
    profile = UserProfile(user_id=user_id, subjects=[])
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


def update(db: Session, profile: UserProfile, updates: dict) -> UserProfile:
    for field, value in updates.items():
        setattr(profile, field, value)
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile