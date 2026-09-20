import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class QuizAttemptAnswerSubmit(BaseModel):
    submitted_answer: str = Field(default="", max_length=2000)


class QuizAttemptQuestionResult(BaseModel):
    question_id: uuid.UUID
    order_index: int
    question_type: str
    prompt: str
    options: list[str]
    submitted_answer: str | None
    is_correct: bool | None
    correct_answer: str | None
    explanation: str | None


class QuizAttemptRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    quiz_id: uuid.UUID
    quiz_title: str
    subject_id: uuid.UUID | None
    status: str
    score: int | None
    total_questions: int
    percentage_score: int | None
    started_at: datetime
    completed_at: datetime | None


class QuizAttemptDetail(QuizAttemptRead):
    answers: list[QuizAttemptQuestionResult]