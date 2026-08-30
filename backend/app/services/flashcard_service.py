import json
import logging
import uuid

from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.ai.prompts.flashcard_prompts import build_flashcard_prompt
from app.ai.prompts.rag_prompts import build_document_context
from app.ai.providers.base import AIProvider, AIProviderError
from app.ai.providers.embedding_base import EmbeddingProvider, EmbeddingProviderError
from app.core.exceptions import (
    FlashcardDeckNotFoundError,
    FlashcardGenerationFailedError,
    FlashcardNotFoundError,
    SubjectNotFoundError,
)
from app.models.flashcard import Flashcard
from app.models.flashcard_deck import FlashcardDeck
from app.repositories import (
    document_chunk_repository,
    flashcard_deck_repository,
    flashcard_progress_repository,
    flashcard_repository,
    subject_repository,
)
from app.schemas.flashcard import DeckCreate, DeckUpdate, FlashcardCreate, FlashcardUpdate
from app.services.flashcard_parsing import parse_generated_flashcards
from app.services.subject_context import build_subject_context

logger = logging.getLogger(__name__)


def list_decks(db: Session, user_id: uuid.UUID) -> list[FlashcardDeck]:
    return flashcard_deck_repository.list_for_user(db, user_id)


def get_deck(db: Session, deck_id: uuid.UUID, user_id: uuid.UUID) -> FlashcardDeck:
    deck = flashcard_deck_repository.get_by_id_for_user(db, deck_id, user_id)
    if deck is None:
        raise FlashcardDeckNotFoundError(deck_id)
    return deck


def create_deck(db: Session, user_id: uuid.UUID, data: DeckCreate) -> FlashcardDeck:
    if data.subject_id is not None and subject_repository.get_by_id_for_user(db, data.subject_id, user_id) is None:
        raise SubjectNotFoundError(data.subject_id)
    return flashcard_deck_repository.create(db, user_id, data.model_dump())


def update_deck(db: Session, deck_id: uuid.UUID, user_id: uuid.UUID, data: DeckUpdate) -> FlashcardDeck:
    deck = get_deck(db, deck_id, user_id)
    update_data = data.model_dump(exclude_unset=True)
    new_subject_id = update_data.get("subject_id")
    if new_subject_id is not None and subject_repository.get_by_id_for_user(db, new_subject_id, user_id) is None:
        raise SubjectNotFoundError(new_subject_id)
    return flashcard_deck_repository.update(db, deck, update_data)


def delete_deck(db: Session, deck_id: uuid.UUID, user_id: uuid.UUID) -> None:
    deck = get_deck(db, deck_id, user_id)
    flashcard_deck_repository.delete(db, deck)


def add_flashcard(db: Session, deck_id: uuid.UUID, user_id: uuid.UUID, data: FlashcardCreate) -> Flashcard:
    deck = get_deck(db, deck_id, user_id)
    return flashcard_repository.create(db, deck.id, data.front, data.back)


def update_flashcard(
    db: Session, deck_id: uuid.UUID, flashcard_id: uuid.UUID, user_id: uuid.UUID, data: FlashcardUpdate
) -> Flashcard:
    deck = get_deck(db, deck_id, user_id)
    flashcard = flashcard_repository.get_by_id_for_deck(db, flashcard_id, deck.id)
    if flashcard is None:
        raise FlashcardNotFoundError(flashcard_id)
    update_data = data.model_dump(exclude_unset=True)
    return flashcard_repository.update(db, flashcard, update_data)


def delete_flashcard(db: Session, deck_id: uuid.UUID, flashcard_id: uuid.UUID, user_id: uuid.UUID) -> None:
    deck = get_deck(db, deck_id, user_id)
    flashcard = flashcard_repository.get_by_id_for_deck(db, flashcard_id, deck.id)
    if flashcard is None:
        raise FlashcardNotFoundError(flashcard_id)
    flashcard_repository.delete(db, flashcard)


def get_review_queue(db: Session, deck_id: uuid.UUID, user_id: uuid.UUID) -> list[Flashcard]:
    deck = get_deck(db, deck_id, user_id)
    return flashcard_repository.list_due_for_deck(db, deck.id)


def review_flashcard(
    db: Session, deck_id: uuid.UUID, flashcard_id: uuid.UUID, user_id: uuid.UUID, result: str
) -> Flashcard:
    deck = get_deck(db, deck_id, user_id)
    flashcard = flashcard_repository.get_by_id_for_deck(db, flashcard_id, deck.id)
    if flashcard is None:
        raise FlashcardNotFoundError(flashcard_id)
    flashcard_progress_repository.record_review(db, flashcard.progress, result)
    db.refresh(flashcard)
    return flashcard


async def _retrieve_document_context(
    db: Session, embedding_provider: EmbeddingProvider, user_id: uuid.UUID, subject_context: str | None
) -> str | None:
    if subject_context is None:
        return None

    try:
        query_embeddings = await embedding_provider.embed([subject_context])
    except EmbeddingProviderError:
        return None

    if not query_embeddings:
        return None

    chunks = document_chunk_repository.search_similar_chunks(
        db, user_id, query_embeddings[0], limit=6, max_distance=0.7
    )
    return build_document_context(chunks) if chunks else None


async def generate_flashcards(
    db: Session,
    ai_provider: AIProvider,
    embedding_provider: EmbeddingProvider,
    deck_id: uuid.UUID,
    user_id: uuid.UUID,
    count: int,
) -> list[Flashcard]:
    deck = get_deck(db, deck_id, user_id)

    subject_context = build_subject_context(db, deck.subject_id, user_id)
    document_context = await _retrieve_document_context(db, embedding_provider, user_id, subject_context)

    prompt = build_flashcard_prompt(subject_context, document_context, deck.title, count)
    messages = [{"role": "user", "content": prompt}]

    try:
        raw_response = await ai_provider.generate_reply(messages, response_format="json")
    except AIProviderError as error:
        raise FlashcardGenerationFailedError(str(error))

    try:
        generated_cards = parse_generated_flashcards(raw_response)
    except (json.JSONDecodeError, ValidationError) as error:
        logger.warning("Failed to parse flashcard generation response: %s", error)
        raise FlashcardGenerationFailedError("The AI returned an unexpected response format.")

    if not generated_cards:
        raise FlashcardGenerationFailedError("The AI did not return any valid flashcards.")

    return flashcard_repository.create_many(db, deck.id, [card.model_dump() for card in generated_cards])