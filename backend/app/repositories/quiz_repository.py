import uuid

from sqlalchemy.orm import Session, selectinload

from app.models.quiz import Quiz
from app.models.quiz_question import QuizQuestion


def list_for_user(db: Session, user_id: uuid.UUID) -> list[Quiz]:
    return (
        db.query(Quiz)
        .options(selectinload(Quiz.questions))
        .filter(Quiz.user_id == user_id)
        .order_by(Quiz.created_at.desc())
        .all()
    )


def get_by_id_for_user(db: Session, quiz_id: uuid.UUID, user_id: uuid.UUID) -> Quiz | None:
    return (
        db.query(Quiz)
        .options(selectinload(Quiz.questions))
        .filter(Quiz.id == quiz_id, Quiz.user_id == user_id)
        .first()
    )


def create(db: Session, quiz: Quiz) -> Quiz:
    db.add(quiz)
    db.commit()
    db.refresh(quiz)
    return quiz


def set_generation_status(db: Session, quiz: Quiz, status: str, error: str | None) -> None:
    quiz.generation_status = status
    quiz.generation_error = error
    db.add(quiz)
    db.commit()


def add_questions(db: Session, quiz_id: uuid.UUID, questions: list[dict]) -> None:
    for index, question in enumerate(questions):
        db.add(
            QuizQuestion(
                quiz_id=quiz_id,
                order_index=index,
                question_type=question["question_type"],
                prompt=question["prompt"],
                options=question["options"],
                correct_answer=question["correct_answer"],
                explanation=question["explanation"],
            )
        )
    db.commit()


def delete(db: Session, quiz: Quiz) -> None:
    db.delete(quiz)
    db.commit()