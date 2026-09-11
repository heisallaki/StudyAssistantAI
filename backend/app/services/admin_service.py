import uuid

from sqlalchemy.orm import Session

from app.core.exceptions import CannotModifySelfError, LastAdministratorError, UserNotFoundError
from app.models.user import User
from app.repositories import admin_repository
from app.schemas.admin import AdminSystemStats, AdminUserListResponse, AdminUserRead, AdminUserUpdate

MAX_PAGE_SIZE = 100


def _to_admin_user_read(user: User, counts: dict) -> AdminUserRead:
    return AdminUserRead(
        id=user.id,
        email=user.email,
        is_active=user.is_active,
        is_superuser=user.is_superuser,
        created_at=user.created_at,
        updated_at=user.updated_at,
        subject_count=counts["subject_count"],
        document_count=counts["document_count"],
        conversation_count=counts["conversation_count"],
        quiz_count=counts["quiz_count"],
        quiz_attempt_count=counts["quiz_attempt_count"],
        flashcard_deck_count=counts["flashcard_deck_count"],
    )


def list_users(
    db: Session,
    search: str | None,
    is_active: bool | None,
    is_superuser: bool | None,
    page: int,
    page_size: int,
) -> AdminUserListResponse:
    normalized_page = max(page, 1)
    normalized_page_size = min(max(page_size, 1), MAX_PAGE_SIZE)

    users, total = admin_repository.list_users(
        db, search, is_active, is_superuser, normalized_page, normalized_page_size
    )
    counts_by_user = admin_repository.get_activity_counts_for_users(db, [user.id for user in users])
    items = [_to_admin_user_read(user, counts_by_user[user.id]) for user in users]
    total_pages = (total + normalized_page_size - 1) // normalized_page_size if total else 0

    return AdminUserListResponse(
        items=items,
        total=total,
        page=normalized_page,
        page_size=normalized_page_size,
        total_pages=total_pages,
    )


def get_user_detail(db: Session, user_id: uuid.UUID) -> AdminUserRead:
    user = admin_repository.get_by_id(db, user_id)
    if user is None:
        raise UserNotFoundError(str(user_id))
    counts = admin_repository.get_user_activity_counts(db, user_id)
    return _to_admin_user_read(user, counts)


def update_user(db: Session, actor: User, user_id: uuid.UUID, data: AdminUserUpdate) -> AdminUserRead:
    user = admin_repository.get_by_id(db, user_id)
    if user is None:
        raise UserNotFoundError(str(user_id))

    if user.id == actor.id and (data.is_active is False or data.is_superuser is False):
        raise CannotModifySelfError(str(user_id))

    if data.is_superuser is False and user.is_superuser and admin_repository.count_admins(db) <= 1:
        raise LastAdministratorError(str(user_id))

    if data.is_active is not None:
        user.is_active = data.is_active
    if data.is_superuser is not None:
        user.is_superuser = data.is_superuser

    db.commit()
    db.refresh(user)

    counts = admin_repository.get_user_activity_counts(db, user_id)
    return _to_admin_user_read(user, counts)


def delete_user(db: Session, actor: User, user_id: uuid.UUID) -> None:
    user = admin_repository.get_by_id(db, user_id)
    if user is None:
        raise UserNotFoundError(str(user_id))

    if user.id == actor.id:
        raise CannotModifySelfError(str(user_id))

    if user.is_superuser and admin_repository.count_admins(db) <= 1:
        raise LastAdministratorError(str(user_id))

    admin_repository.delete_user(db, user)


def get_system_stats(db: Session) -> AdminSystemStats:
    stats = admin_repository.get_system_stats(db)
    return AdminSystemStats(**stats)