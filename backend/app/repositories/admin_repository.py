import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.conversation import Conversation
from app.models.deadline import Deadline
from app.models.document import Document
from app.models.flashcard import Flashcard
from app.models.flashcard_deck import FlashcardDeck
from app.models.message import Message
from app.models.notification import Notification
from app.models.quiz import Quiz
from app.models.quiz_attempt import QuizAttempt
from app.models.study_goal import StudyGoal
from app.models.study_session import StudySession
from app.models.subject import Subject
from app.models.topic import Topic
from app.models.user import User


def list_users(
    db: Session,
    search: str | None,
    is_active: bool | None,
    is_superuser: bool | None,
    page: int,
    page_size: int,
) -> tuple[list[User], int]:
    query = db.query(User)

    if search:
        query = query.filter(User.email.ilike(f"%{search}%"))
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    if is_superuser is not None:
        query = query.filter(User.is_superuser == is_superuser)

    total = query.count()
    users = (
        query.order_by(User.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return users, total


def get_by_id(db: Session, user_id: uuid.UUID) -> User | None:
    return db.query(User).filter(User.id == user_id).first()


def count_admins(db: Session) -> int:
    return db.query(User).filter(User.is_superuser.is_(True)).count()


def delete_user(db: Session, user: User) -> None:
    db.delete(user)
    db.commit()


def get_user_activity_counts(db: Session, user_id: uuid.UUID) -> dict:
    return {
        "subject_count": db.query(Subject).filter(Subject.user_id == user_id).count(),
        "document_count": db.query(Document).filter(Document.user_id == user_id).count(),
        "conversation_count": db.query(Conversation).filter(Conversation.user_id == user_id).count(),
        "quiz_count": db.query(Quiz).filter(Quiz.user_id == user_id).count(),
        "quiz_attempt_count": db.query(QuizAttempt).filter(QuizAttempt.user_id == user_id).count(),
        "flashcard_deck_count": db.query(FlashcardDeck).filter(FlashcardDeck.user_id == user_id).count(),
    }


def get_activity_counts_for_users(db: Session, user_ids: list[uuid.UUID]) -> dict[uuid.UUID, dict]:
    counts: dict[uuid.UUID, dict] = {
        user_id: {
            "subject_count": 0,
            "document_count": 0,
            "conversation_count": 0,
            "quiz_count": 0,
            "quiz_attempt_count": 0,
            "flashcard_deck_count": 0,
        }
        for user_id in user_ids
    }

    if not user_ids:
        return counts

    aggregates = (
        ("subject_count", Subject),
        ("document_count", Document),
        ("conversation_count", Conversation),
        ("quiz_count", Quiz),
        ("quiz_attempt_count", QuizAttempt),
        ("flashcard_deck_count", FlashcardDeck),
    )

    for field_name, model in aggregates:
        rows = (
            db.query(model.user_id, func.count(model.id))
            .filter(model.user_id.in_(user_ids))
            .group_by(model.user_id)
            .all()
        )
        for user_id, count in rows:
            counts[user_id][field_name] = count

    return counts


def get_system_stats(db: Session) -> dict:
    now = datetime.now(timezone.utc)
    seven_days_ago = now - timedelta(days=7)
    thirty_days_ago = now - timedelta(days=30)

    return {
        "total_users": db.query(User).count(),
        "active_users": db.query(User).filter(User.is_active.is_(True)).count(),
        "inactive_users": db.query(User).filter(User.is_active.is_(False)).count(),
        "admin_users": db.query(User).filter(User.is_superuser.is_(True)).count(),
        "new_users_last_7_days": db.query(User).filter(User.created_at >= seven_days_ago).count(),
        "new_users_last_30_days": db.query(User).filter(User.created_at >= thirty_days_ago).count(),
        "total_subjects": db.query(Subject).count(),
        "total_topics": db.query(Topic).count(),
        "total_documents": db.query(Document).count(),
        "total_conversations": db.query(Conversation).count(),
        "total_messages": db.query(Message).count(),
        "total_quizzes": db.query(Quiz).count(),
        "total_quiz_attempts": db.query(QuizAttempt).count(),
        "total_flashcard_decks": db.query(FlashcardDeck).count(),
        "total_flashcards": db.query(Flashcard).count(),
        "total_study_goals": db.query(StudyGoal).count(),
        "total_study_sessions": db.query(StudySession).count(),
        "total_deadlines": db.query(Deadline).count(),
        "total_notifications": db.query(Notification).count(),
    }