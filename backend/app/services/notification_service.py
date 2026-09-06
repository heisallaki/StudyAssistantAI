import uuid
from datetime import date, timedelta

from sqlalchemy.orm import Session

from app.core.exceptions import NotificationNotFoundError
from app.models.notification import Notification
from app.repositories import deadline_repository, notification_repository, study_session_repository
from app.services import analytics_service
from app.services.notification_rules import (
    DEADLINE_REMINDER_WINDOW_DAYS,
    build_deadline_reminders,
    build_quiz_reminders,
    build_study_session_reminders,
)

WELCOME_NOTIFICATION_TYPE = "system"


def _create_if_new(db: Session, user_id: uuid.UUID, reminder: dict) -> None:
    already_exists = notification_repository.exists_for_related(
        db, user_id, reminder["notification_type"], reminder["related_id"]
    )
    if already_exists:
        return
    notification_repository.create(
        db,
        user_id=user_id,
        notification_type=reminder["notification_type"],
        title=reminder["title"],
        message=reminder["message"],
        related_id=reminder["related_id"],
    )


def _generate_due_notifications(db: Session, user_id: uuid.UUID) -> None:
    today = date.today()

    sessions = study_session_repository.list_for_user(db, user_id, status="planned")
    sessions_data = [
        {
            "id": session.id,
            "title": session.title,
            "status": session.status,
            "scheduled_date": session.scheduled_date,
        }
        for session in sessions
    ]
    for reminder in build_study_session_reminders(sessions_data, today):
        _create_if_new(db, user_id, reminder)

    deadlines = deadline_repository.list_for_user(
        db,
        user_id,
        end=today + timedelta(days=DEADLINE_REMINDER_WINDOW_DAYS),
        include_completed=False,
    )
    deadlines_data = [
        {
            "id": deadline.id,
            "title": deadline.title,
            "due_date": deadline.due_date,
            "is_completed": deadline.is_completed,
        }
        for deadline in deadlines
    ]
    for reminder in build_deadline_reminders(deadlines_data, today):
        _create_if_new(db, user_id, reminder)

    weak_areas = analytics_service.get_weak_areas(db, user_id)
    weak_areas_data = [
        {
            "subject_id": area.subject_id,
            "name": area.name,
            "reason": area.reason,
            "metric_value": area.metric_value,
        }
        for area in weak_areas
    ]
    for reminder in build_quiz_reminders(weak_areas_data):
        _create_if_new(db, user_id, reminder)


def list_notifications(db: Session, user_id: uuid.UUID, unread_only: bool = False) -> list[Notification]:
    _generate_due_notifications(db, user_id)
    return notification_repository.list_for_user(db, user_id, unread_only)


def get_unread_count(db: Session, user_id: uuid.UUID) -> int:
    _generate_due_notifications(db, user_id)
    return notification_repository.count_unread(db, user_id)


def set_read(db: Session, notification_id: uuid.UUID, user_id: uuid.UUID, is_read: bool) -> Notification:
    notification = notification_repository.get_by_id_for_user(db, notification_id, user_id)
    if notification is None:
        raise NotificationNotFoundError(notification_id)
    return notification_repository.mark_read(db, notification, is_read)


def mark_all_read(db: Session, user_id: uuid.UUID) -> int:
    return notification_repository.mark_all_read(db, user_id)


def delete_notification(db: Session, notification_id: uuid.UUID, user_id: uuid.UUID) -> None:
    notification = notification_repository.get_by_id_for_user(db, notification_id, user_id)
    if notification is None:
        raise NotificationNotFoundError(notification_id)
    notification_repository.delete(db, notification)


def create_welcome_notification(db: Session, user_id: uuid.UUID) -> Notification:
    return notification_repository.create(
        db,
        user_id=user_id,
        notification_type=WELCOME_NOTIFICATION_TYPE,
        title="Welcome to StudyAssistant AI",
        message="Set up a subject and start tracking your study progress.",
        related_id=None,
    )