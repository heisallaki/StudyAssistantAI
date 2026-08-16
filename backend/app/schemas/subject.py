import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TopicCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)
    order_index: int = 0


class TopicUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)
    is_completed: bool | None = None
    order_index: int | None = None


class TopicRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    subject_id: uuid.UUID
    title: str
    description: str | None
    is_completed: bool
    order_index: int
    created_at: datetime
    updated_at: datetime


class SubjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    description: str | None = Field(default=None, max_length=2000)
    color: str | None = Field(default=None, max_length=20)


class SubjectUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=150)
    description: str | None = Field(default=None, max_length=2000)
    color: str | None = Field(default=None, max_length=20)


class SubjectRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    description: str | None
    color: str | None
    topic_count: int
    completed_topic_count: int
    progress_percentage: int
    created_at: datetime
    updated_at: datetime


class SubjectDetail(SubjectRead):
    topics: list[TopicRead]