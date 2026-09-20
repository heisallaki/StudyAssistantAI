import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.flashcard_progress import FlashcardProgress
from app.services.flashcard_review import apply_review_result


def get_by_flashcard_id(db: Session, flashcard_id: uuid.UUID) -> FlashcardProgress | None:
    return db.query(FlashcardProgress).filter(FlashcardProgress.flashcard_id == flashcard_id).first()


def record_review(db: Session, progress: FlashcardProgress, result: str) -> FlashcardProgress:
    status, times_reviewed, times_correct, correct_streak = apply_review_result(
        progress.status, progress.times_reviewed, progress.times_correct, progress.correct_streak, result
    )
    progress.status = status
    progress.times_reviewed = times_reviewed
    progress.times_correct = times_correct
    progress.correct_streak = correct_streak
    progress.last_reviewed_at = datetime.now(timezone.utc)
    db.add(progress)
    db.commit()
    db.refresh(progress)
    return progress