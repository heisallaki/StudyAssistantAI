import uuid

from sqlalchemy.orm import Session, selectinload

from app.models.flashcard import Flashcard
from app.models.flashcard_progress import FlashcardProgress


def get_by_id_for_deck(db: Session, flashcard_id: uuid.UUID, deck_id: uuid.UUID) -> Flashcard | None:
    return (
        db.query(Flashcard)
        .options(selectinload(Flashcard.progress))
        .filter(Flashcard.id == flashcard_id, Flashcard.deck_id == deck_id)
        .first()
    )


def create(db: Session, deck_id: uuid.UUID, front: str, back: str) -> Flashcard:
    flashcard = Flashcard(deck_id=deck_id, front=front, back=back)
    db.add(flashcard)
    db.flush()
    db.add(FlashcardProgress(flashcard_id=flashcard.id))
    db.commit()
    db.refresh(flashcard)
    return flashcard


def create_many(db: Session, deck_id: uuid.UUID, cards: list[dict]) -> list[Flashcard]:
    created: list[Flashcard] = []
    for card in cards:
        flashcard = Flashcard(deck_id=deck_id, front=card["front"], back=card["back"])
        db.add(flashcard)
        created.append(flashcard)
    db.flush()
    for flashcard in created:
        db.add(FlashcardProgress(flashcard_id=flashcard.id))
    db.commit()
    for flashcard in created:
        db.refresh(flashcard)
    return created


def update(db: Session, flashcard: Flashcard, data: dict) -> Flashcard:
    for field, value in data.items():
        setattr(flashcard, field, value)
    db.add(flashcard)
    db.commit()
    db.refresh(flashcard)
    return flashcard


def delete(db: Session, flashcard: Flashcard) -> None:
    db.delete(flashcard)
    db.commit()


def list_due_for_deck(db: Session, deck_id: uuid.UUID) -> list[Flashcard]:
    return (
        db.query(Flashcard)
        .join(FlashcardProgress, FlashcardProgress.flashcard_id == Flashcard.id)
        .options(selectinload(Flashcard.progress))
        .filter(Flashcard.deck_id == deck_id, FlashcardProgress.status != "mastered")
        .order_by(Flashcard.created_at)
        .all()
    )