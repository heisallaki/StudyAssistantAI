import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class NotificationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    notification_type: str
    title: str
    message: str
    related_id: uuid.UUID | None
    is_read: bool
    created_at: datetime


class NotificationUpdate(BaseModel):
    is_read: bool


class NotificationUnreadCount(BaseModel):
    unread_count: int