import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class MessageRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    role: str
    content: str
    sources: list[str]
    created_at: datetime


class ConversationCreate(BaseModel):
    subject_id: uuid.UUID | None = None
    mode: str = Field(default="tutor", pattern="^(tutor|socratic)$")
    explanation_level: str = Field(default="intermediate", pattern="^(beginner|intermediate|advanced)$")


class ConversationUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    mode: str | None = Field(default=None, pattern="^(tutor|socratic)$")
    explanation_level: str | None = Field(default=None, pattern="^(beginner|intermediate|advanced)$")


class ConversationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    subject_id: uuid.UUID | None
    title: str
    mode: str
    explanation_level: str
    created_at: datetime
    updated_at: datetime


class ConversationDetail(ConversationRead):
    messages: list[MessageRead]


class SendMessageRequest(BaseModel):
    content: str = Field(min_length=1, max_length=4000)