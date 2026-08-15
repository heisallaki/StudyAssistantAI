from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.user import User
from app.models.user_profile import UserProfile
from app.schemas.dashboard import DashboardOverview
from app.services import profile_service

PROFILE_COMPLETION_FIELDS = (
    "full_name",
    "academic_level",
    "institution",
    "program",
    "subjects",
    "academic_goals",
)


def calculate_profile_completion(profile: UserProfile) -> tuple[int, list[str]]:
    missing_fields: list[str] = []
    filled_count = 0

    for field in PROFILE_COMPLETION_FIELDS:
        value = getattr(profile, field)
        is_filled = bool(value) if field == "subjects" else bool(value)
        if is_filled:
            filled_count += 1
        else:
            missing_fields.append(field)

    percentage = round((filled_count / len(PROFILE_COMPLETION_FIELDS)) * 100)
    return percentage, missing_fields


def get_overview(db: Session, user: User) -> DashboardOverview:
    profile = profile_service.get_or_create_profile(db, user.id)
    completion_percentage, missing_fields = calculate_profile_completion(profile)
    account_age_days = (datetime.now(timezone.utc) - user.created_at).days

    return DashboardOverview(
        member_since=user.created_at,
        account_age_days=account_age_days,
        profile_completion_percentage=completion_percentage,
        profile_completion_missing_fields=missing_fields,
    )