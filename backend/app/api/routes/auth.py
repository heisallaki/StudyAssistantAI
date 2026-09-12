from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.config import get_settings
from app.core.exceptions import (
    AccountLockedError,
    EmailAlreadyRegisteredError,
    InactiveUserError,
    InvalidCredentialsError,
)
from app.core.rate_limit import limiter
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import Token, UserCreate, UserLogin, UserRead
from app.services import auth_service

settings = get_settings()
router = APIRouter()


@router.post(
    "/register",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
)
@limiter.limit(settings.REGISTER_RATE_LIMIT)
def register(
    request: Request,
    user_in: UserCreate,
    db: Session = Depends(get_db),
):
    try:
        return auth_service.register_user(db, user_in)
    except EmailAlreadyRegisteredError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error


@router.post(
    "/login",
    response_model=Token,
)
@limiter.limit(settings.LOGIN_RATE_LIMIT)
def login(
    request: Request,
    credentials: UserLogin,
    db: Session = Depends(get_db),
):
    try:
        user = auth_service.authenticate_user(db, credentials)
    except InvalidCredentialsError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        ) from error
    except AccountLockedError as error:
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail="Too many failed login attempts. Please try again later.",
        ) from error
    except InactiveUserError as error:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(error),
        ) from error

    return Token(
        access_token=auth_service.create_token_for_user(user),
        token_type="bearer",
    )


@router.get(
    "/me",
    response_model=UserRead,
)
def get_me(
    current_user: User = Depends(get_current_user),
):
    return current_user