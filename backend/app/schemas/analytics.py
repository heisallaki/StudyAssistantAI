import uuid
from datetime import date as date_type

from pydantic import BaseModel


class AnalyticsOverview(BaseModel):
    total_study_minutes: int
    total_quizzes_taken: int
    average_quiz_score: int | None
    total_flashcards_reviewed: int
    flashcards_mastered: int
    total_flashcards: int
    subjects_count: int
    active_goals_count: int


class PerformanceTrendPoint(BaseModel):
    date: date_type
    average_score: int
    attempts_count: int


class StudyTimePoint(BaseModel):
    date: date_type
    minutes: int


class SubjectBreakdown(BaseModel):
    subject_id: uuid.UUID
    name: str
    priority: str
    topic_progress_percentage: int
    quiz_average_score: int | None
    flashcard_mastery_percentage: int | None
    study_minutes: int


class WeakArea(BaseModel):
    subject_id: uuid.UUID
    name: str
    reason: str
    metric_value: int