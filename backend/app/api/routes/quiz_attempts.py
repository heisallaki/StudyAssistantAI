import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.exceptions import (
    QuizAttemptAlreadyCompletedError,
    QuizAttemptNotFoundError,
    QuizAttemptQuestionNotFoundError,
)
from app.db.session import get_db
from app.models.user import User
from app.schemas.quiz_attempt import QuizAttemptAnswerSubmit, QuizAttemptDetail, QuizAttemptRead
from app.services import quiz_attempt_service

router = APIRouter()


@router.get("", response_model=list[QuizAttemptRead])
def list_quiz_attempts(
    quiz_id: uuid.UUID | None = Query(default=None),
    subject_id: uuid.UUID | None = Query(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return quiz_attempt_service.list_attempts(db, current_user.id, quiz_id, subject_id)


@router.get("/{attempt_id}", response_model=QuizAttemptDetail)
def get_quiz_attempt(
    attempt_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        attempt = quiz_attempt_service.get_attempt(db, attempt_id, current_user.id)
    except QuizAttemptNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quiz attempt not found")
    return quiz_attempt_service.to_detail(attempt)


@router.put("/{attempt_id}/answers/{question_id}", response_model=QuizAttemptDetail)
def submit_quiz_attempt_answer(
    attempt_id: uuid.UUID,
    question_id: uuid.UUID,
    data: QuizAttemptAnswerSubmit,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        attempt = quiz_attempt_service.submit_answer(
            db, attempt_id, current_user.id, question_id, data.submitted_answer
        )
    except QuizAttemptNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quiz attempt not found")
    except QuizAttemptAlreadyCompletedError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This quiz attempt has already been completed.",
        )
    except QuizAttemptQuestionNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question not found in this quiz")
    return quiz_attempt_service.to_detail(attempt)


@router.post("/{attempt_id}/complete", response_model=QuizAttemptDetail)
def complete_quiz_attempt(
    attempt_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        attempt = quiz_attempt_service.complete_attempt(db, attempt_id, current_user.id)
    except QuizAttemptNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quiz attempt not found")
    return quiz_attempt_service.to_detail(attempt)