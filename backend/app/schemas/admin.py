import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr


class AdminUserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: EmailStr
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime
    subject_count: int
    document_count: int
    conversation_count: int
    quiz_count: int
    quiz_attempt_count: int
    flashcard_deck_count: int


class AdminUserListResponse(BaseModel):
    items: list[AdminUserRead]
    total: int
    page: int
    page_size: int
    total_pages: int


class AdminUserUpdate(BaseModel):
    is_active: bool | None = None
    is_superuser: bool | None = None


class AdminSystemStats(BaseModel):
    total_users: int
    active_users: int
    inactive_users: int
    admin_users: int
    new_users_last_7_days: int
    new_users_last_30_days: int
    total_subjects: int
    total_topics: int
    total_documents: int
    total_conversations: int
    total_messages: int
    total_quizzes: int
    total_quiz_attempts: int
    total_flashcard_decks: int
    total_flashcards: int
    total_study_goals: int
    total_study_sessions: int
    total_deadlines: int
    total_notifications: int