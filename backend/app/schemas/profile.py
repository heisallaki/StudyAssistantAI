import uuid
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class AcademicLevel(str, Enum):
    HIGH_SCHOOL = "high_school"
    UNDERGRADUATE = "undergraduate"
    GRADUATE = "graduate"
    POSTGRADUATE = "postgraduate"
    OTHER = "other"


class ProfileUpdate(BaseModel):
    full_name: str | None = Field(default=None, max_length=255)
    academic_level: AcademicLevel | None = None
    institution: str | None = Field(default=None, max_length=255)
    program: str | None = Field(default=None, max_length=255)
    subjects: list[str] | None = Field(default=None, max_length=20)
    academic_goals: str | None = Field(default=None, max_length=2000)


class ProfileRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    full_name: str | None
    academic_level: AcademicLevel | None
    institution: str | None
    program: str | None
    subjects: list[str]
    academic_goals: str | None
    created_at: datetime
    updated_at: datetime