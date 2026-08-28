from fastapi import APIRouter

from app.api.routes.auth import router as auth_router
from app.api.routes.dashboard import router as dashboard_router
from app.api.routes.documents import router as documents_router
from app.api.routes.health import router as health_router
from app.api.routes.profile import router as profile_router
from app.api.routes.quiz_attempts import router as quiz_attempts_router
from app.api.routes.quizzes import router as quizzes_router
from app.api.routes.subjects import router as subjects_router
from app.api.routes.tutor import router as tutor_router

api_router = APIRouter()
api_router.include_router(health_router, tags=["health"])
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(profile_router, prefix="/profile", tags=["profile"])
api_router.include_router(dashboard_router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(subjects_router, prefix="/subjects", tags=["subjects"])
api_router.include_router(documents_router, prefix="/documents", tags=["documents"])
api_router.include_router(tutor_router, prefix="/tutor", tags=["tutor"])
api_router.include_router(quizzes_router, prefix="/quizzes", tags=["quizzes"])
api_router.include_router(quiz_attempts_router, prefix="/quiz-attempts", tags=["quiz-attempts"])