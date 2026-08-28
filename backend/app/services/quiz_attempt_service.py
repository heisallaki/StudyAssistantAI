import uuid

from sqlalchemy.orm import Session

from app.core.exceptions import (
    QuizAttemptAlreadyCompletedError,
    QuizAttemptNotFoundError,
    QuizAttemptQuestionNotFoundError,
    QuizNotFoundError,
    QuizNotReadyForAttemptError,
)
from app.models.quiz_attempt import QuizAttempt
from app.repositories import quiz_attempt_repository, quiz_repository
from app.schemas.quiz_attempt import QuizAttemptDetail, QuizAttemptQuestionResult
from app.services.quiz_grading import grade_answer


def start_attempt(db: Session, user_id: uuid.UUID, quiz_id: uuid.UUID) -> QuizAttempt:
    quiz = quiz_repository.get_by_id_for_user(db, quiz_id, user_id)
    if quiz is None:
        raise QuizNotFoundError(quiz_id)
    if quiz.generation_status != "completed" or quiz.question_count == 0:
        raise QuizNotReadyForAttemptError(quiz_id)

    attempt = QuizAttempt(
        quiz_id=quiz.id,
        user_id=user_id,
        status="in_progress",
        total_questions=quiz.question_count,
    )
    return quiz_attempt_repository.create(db, attempt)


def get_attempt(db: Session, attempt_id: uuid.UUID, user_id: uuid.UUID) -> QuizAttempt:
    attempt = quiz_attempt_repository.get_by_id_for_user(db, attempt_id, user_id)
    if attempt is None:
        raise QuizAttemptNotFoundError(attempt_id)
    return attempt


def list_attempts(
    db: Session,
    user_id: uuid.UUID,
    quiz_id: uuid.UUID | None = None,
    subject_id: uuid.UUID | None = None,
) -> list[QuizAttempt]:
    return quiz_attempt_repository.list_for_user(db, user_id, quiz_id, subject_id)


def submit_answer(
    db: Session,
    attempt_id: uuid.UUID,
    user_id: uuid.UUID,
    question_id: uuid.UUID,
    submitted_answer: str,
) -> QuizAttempt:
    attempt = get_attempt(db, attempt_id, user_id)
    if attempt.status == "completed":
        raise QuizAttemptAlreadyCompletedError(attempt_id)

    question_ids = {question.id for question in attempt.quiz.questions}
    if question_id not in question_ids:
        raise QuizAttemptQuestionNotFoundError(question_id)

    quiz_attempt_repository.upsert_answer(db, attempt.id, question_id, submitted_answer)
    db.refresh(attempt)
    return attempt


def complete_attempt(db: Session, attempt_id: uuid.UUID, user_id: uuid.UUID) -> QuizAttempt:
    attempt = get_attempt(db, attempt_id, user_id)
    if attempt.status == "completed":
        return attempt

    answers_by_question = {answer.question_id: answer for answer in attempt.answers}
    score = 0

    for question in attempt.quiz.questions:
        answer = answers_by_question.get(question.id)
        submitted_text = answer.submitted_answer if answer is not None else ""
        is_correct = grade_answer(question.question_type, submitted_text, question.correct_answer)

        if answer is None:
            answer = quiz_attempt_repository.upsert_answer(db, attempt.id, question.id, submitted_text)

        answer.is_correct = is_correct
        db.add(answer)

        if is_correct:
            score += 1

    db.commit()
    return quiz_attempt_repository.complete(db, attempt, score)


def to_detail(attempt: QuizAttempt) -> QuizAttemptDetail:
    is_completed = attempt.status == "completed"
    answers_by_question = {answer.question_id: answer for answer in attempt.answers}

    results: list[QuizAttemptQuestionResult] = []
    for question in attempt.quiz.questions:
        answer = answers_by_question.get(question.id)
        results.append(
            QuizAttemptQuestionResult(
                question_id=question.id,
                order_index=question.order_index,
                question_type=question.question_type,
                prompt=question.prompt,
                options=question.options,
                submitted_answer=answer.submitted_answer if answer is not None else None,
                is_correct=answer.is_correct if (answer is not None and is_completed) else None,
                correct_answer=question.correct_answer if is_completed else None,
                explanation=question.explanation if is_completed else None,
            )
        )

    return QuizAttemptDetail(
        id=attempt.id,
        quiz_id=attempt.quiz_id,
        quiz_title=attempt.quiz_title,
        subject_id=attempt.subject_id,
        status=attempt.status,
        score=attempt.score,
        total_questions=attempt.total_questions,
        percentage_score=attempt.percentage_score,
        started_at=attempt.started_at,
        completed_at=attempt.completed_at,
        answers=results,
    )