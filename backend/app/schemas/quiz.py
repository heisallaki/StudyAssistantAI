import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

VALID_QUESTION_TYPES = {"multiple_choice", "true_false", "short_answer"}


class QuizCreate(BaseModel):
    subject_id: uuid.UUID | None = None
    difficulty: str = Field(default="medium", pattern="^(easy|medium|hard)$")
    question_types: list[str] = Field(
        default_factory=lambda: ["multiple_choice", "true_false", "short_answer"]
    )
    question_count: int = Field(default=5, ge=1, le=10)

    @field_validator("question_types")
    @classmethod
    def validate_question_types(cls, value: list[str]) -> list[str]:
        if not value:
            raise ValueError("At least one question type is required")
        invalid = set(value) - VALID_QUESTION_TYPES
        if invalid:
            raise ValueError(f"Invalid question types: {sorted(invalid)}")
        return value


class QuizQuestionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    order_index: int
    question_type: str
    prompt: str
    options: list[str]
    correct_answer: str
    explanation: str


class QuizRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    subject_id: uuid.UUID | None
    title: str
    difficulty: str
    generation_status: str
    generation_error: str | None
    question_count: int
    created_at: datetime
    updated_at: datetime


class QuizDetail(QuizRead):
    questions: list[QuizQuestionRead]