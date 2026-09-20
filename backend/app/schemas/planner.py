import uuid
from datetime import date, datetime, time

from pydantic import BaseModel, ConfigDict, Field


class StudyGoalCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    subject_id: uuid.UUID | None = None
    description: str | None = Field(default=None, max_length=2000)
    target_date: date | None = None


class StudyGoalUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    subject_id: uuid.UUID | None = None
    description: str | None = Field(default=None, max_length=2000)
    target_date: date | None = None
    status: str | None = Field(default=None, pattern="^(active|completed|abandoned)$")


class StudyGoalRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    subject_id: uuid.UUID | None
    title: str
    description: str | None
    target_date: date | None
    status: str
    created_at: datetime
    updated_at: datetime


class StudySessionCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    subject_id: uuid.UUID | None = None
    goal_id: uuid.UUID | None = None
    scheduled_date: date
    start_time: time | None = None
    duration_minutes: int = Field(gt=0, le=600)
    notes: str | None = Field(default=None, max_length=2000)


class StudySessionUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    subject_id: uuid.UUID | None = None
    goal_id: uuid.UUID | None = None
    scheduled_date: date | None = None
    start_time: time | None = None
    duration_minutes: int | None = Field(default=None, gt=0, le=600)
    status: str | None = Field(default=None, pattern="^(planned|completed|skipped)$")
    notes: str | None = Field(default=None, max_length=2000)


class StudySessionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    subject_id: uuid.UUID | None
    goal_id: uuid.UUID | None
    title: str
    scheduled_date: date
    start_time: time | None
    duration_minutes: int
    status: str
    notes: str | None
    created_at: datetime
    updated_at: datetime


class DeadlineCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    subject_id: uuid.UUID | None = None
    due_date: date
    notes: str | None = Field(default=None, max_length=2000)


class DeadlineUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    subject_id: uuid.UUID | None = None
    due_date: date | None = None
    is_completed: bool | None = None
    notes: str | None = Field(default=None, max_length=2000)


class DeadlineRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    subject_id: uuid.UUID | None
    title: str
    due_date: date
    is_completed: bool
    notes: str | None
    created_at: datetime
    updated_at: datetime


class CalendarEntry(BaseModel):
    entry_type: str
    id: uuid.UUID
    title: str
    date: date
    subject_id: uuid.UUID | None
    status: str | None = None
    start_time: time | None = None
    duration_minutes: int | None = None
    is_completed: bool | None = None


class PlannerRecommendation(BaseModel):
    subject: str
    action: str
    reason: str


class PlannerRecommendationResponse(BaseModel):
    recommendations: list[PlannerRecommendation]