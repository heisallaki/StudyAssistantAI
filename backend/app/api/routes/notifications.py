import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.exceptions import NotificationNotFoundError
from app.db.session import get_db
from app.models.user import User
from app.schemas.notification import NotificationRead, NotificationUnreadCount, NotificationUpdate
from app.services import notification_service

router = APIRouter()


@router.get("", response_model=list[NotificationRead])
def list_notifications(
    unread_only: bool = Query(default=False),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return notification_service.list_notifications(db, current_user.id, unread_only)


@router.get("/unread-count", response_model=NotificationUnreadCount)
def get_unread_count(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    count = notification_service.get_unread_count(db, current_user.id)
    return NotificationUnreadCount(unread_count=count)


@router.put("/{notification_id}", response_model=NotificationRead)
def update_notification(
    notification_id: uuid.UUID,
    data: NotificationUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        return notification_service.set_read(db, notification_id, current_user.id, data.is_read)
    except NotificationNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")


@router.post("/mark-all-read", response_model=NotificationUnreadCount)
def mark_all_read(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    notification_service.mark_all_read(db, current_user.id)
    return NotificationUnreadCount(unread_count=0)


@router.delete("/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_notification(
    notification_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        notification_service.delete_notification(db, notification_id, current_user.id)
    except NotificationNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")