import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class FlashcardCreate(BaseModel):
    front: str = Field(min_length=1, max_length=1000)
    back: str = Field(min_length=1, max_length=1000)


class FlashcardUpdate(BaseModel):
    front: str | None = Field(default=None, min_length=1, max_length=1000)
    back: str | None = Field(default=None, min_length=1, max_length=1000)


class FlashcardGenerateRequest(BaseModel):
    count: int = Field(default=10, ge=1, le=20)


class FlashcardReviewRequest(BaseModel):
    result: str = Field(pattern="^(again|good)$")


class FlashcardProgressRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    status: str
    times_reviewed: int
    times_correct: int
    correct_streak: int
    last_reviewed_at: datetime | None


class FlashcardRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    deck_id: uuid.UUID
    front: str
    back: str
    created_at: datetime
    updated_at: datetime
    progress: FlashcardProgressRead


class DeckCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    subject_id: uuid.UUID | None = None
    description: str | None = Field(default=None, max_length=2000)


class DeckUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    subject_id: uuid.UUID | None = None
    description: str | None = Field(default=None, max_length=2000)


class DeckRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    subject_id: uuid.UUID | None
    title: str
    description: str | None
    card_count: int
    mastered_count: int
    mastery_percentage: int
    created_at: datetime
    updated_at: datetime


class DeckDetail(DeckRead):
    flashcards: list[FlashcardRead]