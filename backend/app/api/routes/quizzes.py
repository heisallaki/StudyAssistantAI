import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.ai.providers.base import AIProvider
from app.ai.providers.embedding_base import EmbeddingProvider
from app.api.deps import get_ai_provider, get_current_user, get_embedding_provider
from app.core.exceptions import QuizNotFoundError, QuizNotReadyForAttemptError, SubjectNotFoundError
from app.db.session import get_db
from app.models.user import User
from app.schemas.quiz import QuizCreate, QuizDetail, QuizRead
from app.schemas.quiz_attempt import QuizAttemptDetail
from app.services import quiz_attempt_service, quiz_service

router = APIRouter()


@router.get("", response_model=list[QuizRead])
def list_quizzes(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return quiz_service.list_quizzes(db, current_user.id)


@router.post("", response_model=QuizDetail, status_code=status.HTTP_201_CREATED)
async def create_quiz(
    data: QuizCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    ai_provider: AIProvider = Depends(get_ai_provider),
    embedding_provider: EmbeddingProvider = Depends(get_embedding_provider),
):
    try:
        return await quiz_service.generate_quiz(db, ai_provider, embedding_provider, current_user.id, data)
    except SubjectNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subject not found")


@router.get("/{quiz_id}", response_model=QuizDetail)
def get_quiz(
    quiz_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        return quiz_service.get_quiz(db, quiz_id, current_user.id)
    except QuizNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quiz not found")


@router.delete("/{quiz_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_quiz(
    quiz_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        quiz_service.delete_quiz(db, quiz_id, current_user.id)
    except QuizNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quiz not found")


@router.post("/{quiz_id}/attempts", response_model=QuizAttemptDetail, status_code=status.HTTP_201_CREATED)
def start_quiz_attempt(
    quiz_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        attempt = quiz_attempt_service.start_attempt(db, current_user.id, quiz_id)
    except QuizNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quiz not found")
    except QuizNotReadyForAttemptError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This quiz is not ready to be attempted yet.",
        )
    return quiz_attempt_service.to_detail(attempt)