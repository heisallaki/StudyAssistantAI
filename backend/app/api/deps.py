import uuid

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.ai.providers.base import AIProvider
from app.ai.providers.embedding_base import EmbeddingProvider
from app.ai.providers.factory import build_ai_provider, build_embedding_provider
from app.ai.service import AITutorService
from app.core.security import decode_access_token
from app.db.session import get_db
from app.models.user import User
from app.repositories import user_repository
from app.storage.base import StorageBackend
from app.storage.factory import build_storage_backend

bearer_scheme = HTTPBearer(auto_error=False)


def get_ai_provider() -> AIProvider:
    return build_ai_provider()


def get_ai_tutor_service() -> AITutorService:
    return AITutorService(build_ai_provider())


def get_embedding_provider() -> EmbeddingProvider:
    return build_embedding_provider()


def get_storage_backend() -> StorageBackend:
    return build_storage_backend()


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if credentials is None:
        raise credentials_error

    try:
        payload = decode_access_token(credentials.credentials)
        subject = payload.get("sub")
        if subject is None:
            raise credentials_error
        user_id = uuid.UUID(subject)
    except (jwt.PyJWTError, ValueError):
        raise credentials_error

    user = user_repository.get_by_id(db, user_id)
    if user is None:
        raise credentials_error
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user")

    return user


def get_current_admin_user(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This action requires administrator privileges",
        )
    return current_user