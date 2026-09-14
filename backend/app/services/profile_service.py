import uuid

from sqlalchemy.orm import Session

from app.models.user_profile import UserProfile
from app.repositories import profile_repository, subject_repository
from app.schemas.profile import ProfileUpdate

DEFAULT_SUBJECT_PRIORITY = "medium"
SUBJECT_NAME_MAX_LENGTH = 150


def get_or_create_profile(db: Session, user_id: uuid.UUID) -> UserProfile:
    profile = profile_repository.get_by_user_id(db, user_id)
    if profile is None:
        profile = profile_repository.create_blank(db, user_id)
    return profile


def _sync_subjects_from_profile(db: Session, user_id: uuid.UUID, subject_names: list[str]) -> None:
    existing_names = {
        subject.name.strip().lower() for subject in subject_repository.list_for_user(db, user_id)
    }

    for raw_name in subject_names:
        normalized_name = raw_name.strip()[:SUBJECT_NAME_MAX_LENGTH]
        if not normalized_name or normalized_name.lower() in existing_names:
            continue

        subject_repository.create(
            db,
            user_id,
            {"name": normalized_name, "priority": DEFAULT_SUBJECT_PRIORITY},
        )
        existing_names.add(normalized_name.lower())


def update_profile(db: Session, user_id: uuid.UUID, updates: ProfileUpdate) -> UserProfile:
    profile = get_or_create_profile(db, user_id)
    update_data = updates.model_dump(exclude_unset=True)

    if update_data.get("subjects"):
        _sync_subjects_from_profile(db, user_id, update_data["subjects"])

    return profile_repository.update(db, profile, update_data)