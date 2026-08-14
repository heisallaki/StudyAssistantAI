import uuid

from sqlalchemy.orm import Session

from app.models.user_profile import UserProfile
from app.repositories import profile_repository
from app.schemas.profile import ProfileUpdate


def get_or_create_profile(db: Session, user_id: uuid.UUID) -> UserProfile:
    profile = profile_repository.get_by_user_id(db, user_id)
    if profile is None:
        profile = profile_repository.create_blank(db, user_id)
    return profile


def update_profile(db: Session, user_id: uuid.UUID, updates: ProfileUpdate) -> UserProfile:
    profile = get_or_create_profile(db, user_id)
    update_data = updates.model_dump(exclude_unset=True)
    return profile_repository.update(db, profile, update_data)