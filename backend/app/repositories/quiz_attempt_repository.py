import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import Session, selectinload

from app.models.quiz import Quiz
from app.models.quiz_attempt import QuizAttempt
from app.models.quiz_attempt_answer import QuizAttemptAnswer


def create(db: Session, attempt: QuizAttempt) -> QuizAttempt:
    db.add(attempt)
    db.commit()
    db.refresh(attempt)
    return attempt


def get_by_id_for_user(db: Session, attempt_id: uuid.UUID, user_id: uuid.UUID) -> QuizAttempt | None:
    return (
        db.query(QuizAttempt)
        .options(
            selectinload(QuizAttempt.quiz).selectinload(Quiz.questions),
            selectinload(QuizAttempt.answers),
        )
        .filter(QuizAttempt.id == attempt_id, QuizAttempt.user_id == user_id)
        .first()
    )


def list_for_user(
    db: Session,
    user_id: uuid.UUID,
    quiz_id: uuid.UUID | None = None,
    subject_id: uuid.UUID | None = None,
) -> list[QuizAttempt]:
    query = (
        db.query(QuizAttempt)
        .join(Quiz, QuizAttempt.quiz_id == Quiz.id)
        .options(selectinload(QuizAttempt.quiz))
        .filter(QuizAttempt.user_id == user_id)
    )

    if quiz_id is not None:
        query = query.filter(QuizAttempt.quiz_id == quiz_id)

    if subject_id is not None:
        query = query.filter(Quiz.subject_id == subject_id)

    return query.order_by(QuizAttempt.started_at.desc()).all()


def get_answer_for_question(
    db: Session, attempt_id: uuid.UUID, question_id: uuid.UUID
) -> QuizAttemptAnswer | None:
    return (
        db.query(QuizAttemptAnswer)
        .filter(QuizAttemptAnswer.attempt_id == attempt_id, QuizAttemptAnswer.question_id == question_id)
        .first()
    )


def upsert_answer(
    db: Session, attempt_id: uuid.UUID, question_id: uuid.UUID, submitted_answer: str
) -> QuizAttemptAnswer:
    answer = get_answer_for_question(db, attempt_id, question_id)
    if answer is None:
        answer = QuizAttemptAnswer(
            attempt_id=attempt_id, question_id=question_id, submitted_answer=submitted_answer
        )
        db.add(answer)
    else:
        answer.submitted_answer = submitted_answer
        answer.is_correct = None
    db.commit()
    db.refresh(answer)
    return answer


def complete(db: Session, attempt: QuizAttempt, score: int) -> QuizAttempt:
    attempt.status = "completed"
    attempt.score = score
    attempt.completed_at = datetime.now(timezone.utc)
    db.add(attempt)
    db.commit()
    db.refresh(attempt)
    return attempt