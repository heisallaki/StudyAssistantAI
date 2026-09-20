import uuid

from sqlalchemy.orm import Session, selectinload

from app.models.flashcard import Flashcard
from app.models.flashcard_deck import FlashcardDeck


def list_for_user(db: Session, user_id: uuid.UUID) -> list[FlashcardDeck]:
    return (
        db.query(FlashcardDeck)
        .options(selectinload(FlashcardDeck.flashcards).selectinload(Flashcard.progress))
        .filter(FlashcardDeck.user_id == user_id)
        .order_by(FlashcardDeck.created_at.desc())
        .all()
    )


def get_by_id_for_user(db: Session, deck_id: uuid.UUID, user_id: uuid.UUID) -> FlashcardDeck | None:
    return (
        db.query(FlashcardDeck)
        .options(selectinload(FlashcardDeck.flashcards).selectinload(Flashcard.progress))
        .filter(FlashcardDeck.id == deck_id, FlashcardDeck.user_id == user_id)
        .first()
    )


def create(db: Session, user_id: uuid.UUID, data: dict) -> FlashcardDeck:
    deck = FlashcardDeck(user_id=user_id, **data)
    db.add(deck)
    db.commit()
    db.refresh(deck)
    return deck


def update(db: Session, deck: FlashcardDeck, data: dict) -> FlashcardDeck:
    for field, value in data.items():
        setattr(deck, field, value)
    db.add(deck)
    db.commit()
    db.refresh(deck)
    return deck


def delete(db: Session, deck: FlashcardDeck) -> None:
    db.delete(deck)
    db.commit()