import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.ai.providers.base import AIProvider
from app.ai.providers.embedding_base import EmbeddingProvider
from app.api.deps import get_ai_provider, get_current_user, get_embedding_provider
from app.core.exceptions import (
    FlashcardDeckNotFoundError,
    FlashcardGenerationFailedError,
    FlashcardNotFoundError,
    SubjectNotFoundError,
)
from app.db.session import get_db
from app.models.user import User
from app.schemas.flashcard import (
    DeckCreate,
    DeckDetail,
    DeckRead,
    DeckUpdate,
    FlashcardCreate,
    FlashcardGenerateRequest,
    FlashcardRead,
    FlashcardReviewRequest,
    FlashcardUpdate,
)
from app.services import flashcard_service

router = APIRouter()


@router.get("", response_model=list[DeckRead])
def list_decks(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return flashcard_service.list_decks(db, current_user.id)


@router.post("", response_model=DeckRead, status_code=status.HTTP_201_CREATED)
def create_deck(
    data: DeckCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        return flashcard_service.create_deck(db, current_user.id, data)
    except SubjectNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subject not found")


@router.get("/{deck_id}", response_model=DeckDetail)
def get_deck(
    deck_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        return flashcard_service.get_deck(db, deck_id, current_user.id)
    except FlashcardDeckNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Deck not found")


@router.put("/{deck_id}", response_model=DeckRead)
def update_deck(
    deck_id: uuid.UUID,
    data: DeckUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        return flashcard_service.update_deck(db, deck_id, current_user.id, data)
    except FlashcardDeckNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Deck not found")
    except SubjectNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subject not found")


@router.delete("/{deck_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_deck(
    deck_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        flashcard_service.delete_deck(db, deck_id, current_user.id)
    except FlashcardDeckNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Deck not found")


@router.post("/{deck_id}/flashcards", response_model=FlashcardRead, status_code=status.HTTP_201_CREATED)
def add_flashcard(
    deck_id: uuid.UUID,
    data: FlashcardCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        return flashcard_service.add_flashcard(db, deck_id, current_user.id, data)
    except FlashcardDeckNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Deck not found")


@router.post(
    "/{deck_id}/flashcards/generate",
    response_model=list[FlashcardRead],
    status_code=status.HTTP_201_CREATED,
)
async def generate_flashcards(
    deck_id: uuid.UUID,
    data: FlashcardGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    ai_provider: AIProvider = Depends(get_ai_provider),
    embedding_provider: EmbeddingProvider = Depends(get_embedding_provider),
):
    try:
        return await flashcard_service.generate_flashcards(
            db, ai_provider, embedding_provider, deck_id, current_user.id, data.count
        )
    except FlashcardDeckNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Deck not found")
    except FlashcardGenerationFailedError as error:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(error))


@router.put("/{deck_id}/flashcards/{flashcard_id}", response_model=FlashcardRead)
def update_flashcard(
    deck_id: uuid.UUID,
    flashcard_id: uuid.UUID,
    data: FlashcardUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        return flashcard_service.update_flashcard(db, deck_id, flashcard_id, current_user.id, data)
    except FlashcardDeckNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Deck not found")
    except FlashcardNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Flashcard not found")


@router.delete("/{deck_id}/flashcards/{flashcard_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_flashcard(
    deck_id: uuid.UUID,
    flashcard_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        flashcard_service.delete_flashcard(db, deck_id, flashcard_id, current_user.id)
    except FlashcardDeckNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Deck not found")
    except FlashcardNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Flashcard not found")


@router.get("/{deck_id}/review-queue", response_model=list[FlashcardRead])
def get_review_queue(
    deck_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        return flashcard_service.get_review_queue(db, deck_id, current_user.id)
    except FlashcardDeckNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Deck not found")


@router.post("/{deck_id}/flashcards/{flashcard_id}/review", response_model=FlashcardRead)
def review_flashcard(
    deck_id: uuid.UUID,
    flashcard_id: uuid.UUID,
    data: FlashcardReviewRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        return flashcard_service.review_flashcard(db, deck_id, flashcard_id, current_user.id, data.result)
    except FlashcardDeckNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Deck not found")
    except FlashcardNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Flashcard not found")