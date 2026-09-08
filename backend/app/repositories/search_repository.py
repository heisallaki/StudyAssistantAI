import uuid

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.document import Document
from app.models.flashcard_deck import FlashcardDeck
from app.models.quiz import Quiz
from app.models.subject import Subject
from app.models.topic import Topic

PER_TYPE_RESULT_LIMIT = 8


def search_subjects(db: Session, user_id: uuid.UUID, query: str) -> list[Subject]:
    pattern = f"%{query}%"
    return (
        db.query(Subject)
        .filter(
            Subject.user_id == user_id,
            or_(Subject.name.ilike(pattern), Subject.description.ilike(pattern)),
        )
        .order_by(Subject.name)
        .limit(PER_TYPE_RESULT_LIMIT)
        .all()
    )


def search_topics(db: Session, user_id: uuid.UUID, query: str) -> list[Topic]:
    pattern = f"%{query}%"
    return (
        db.query(Topic)
        .join(Subject, Subject.id == Topic.subject_id)
        .filter(
            Subject.user_id == user_id,
            or_(Topic.title.ilike(pattern), Topic.description.ilike(pattern)),
        )
        .order_by(Topic.title)
        .limit(PER_TYPE_RESULT_LIMIT)
        .all()
    )


def search_documents(db: Session, user_id: uuid.UUID, query: str) -> list[Document]:
    pattern = f"%{query}%"
    return (
        db.query(Document)
        .filter(
            Document.user_id == user_id,
            or_(Document.original_filename.ilike(pattern), Document.extracted_text.ilike(pattern)),
        )
        .order_by(Document.created_at.desc())
        .limit(PER_TYPE_RESULT_LIMIT)
        .all()
    )


def search_quizzes(db: Session, user_id: uuid.UUID, query: str) -> list[Quiz]:
    pattern = f"%{query}%"
    return (
        db.query(Quiz)
        .filter(Quiz.user_id == user_id, Quiz.title.ilike(pattern))
        .order_by(Quiz.created_at.desc())
        .limit(PER_TYPE_RESULT_LIMIT)
        .all()
    )


def search_flashcard_decks(db: Session, user_id: uuid.UUID, query: str) -> list[FlashcardDeck]:
    pattern = f"%{query}%"
    return (
        db.query(FlashcardDeck)
        .filter(
            FlashcardDeck.user_id == user_id,
            or_(FlashcardDeck.title.ilike(pattern), FlashcardDeck.description.ilike(pattern)),
        )
        .order_by(FlashcardDeck.created_at.desc())
        .limit(PER_TYPE_RESULT_LIMIT)
        .all()
    )