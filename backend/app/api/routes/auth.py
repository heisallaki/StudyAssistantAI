from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.config import get_settings
from app.core.exceptions import (
    AccountLockedError,
    EmailAlreadyRegisteredError,
    EmailNotVerifiedError,
    InactiveUserError,
    InvalidCredentialsError,
    InvalidCurrentPasswordError,
    LastAdministratorError,
    OtpExpiredError,
    OtpInvalidError,
    OtpNotFoundError,
    OtpTooManyAttemptsError,
)
from app.core.rate_limit import limiter
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import (
    AccountDeletionRequest,
    EmailVerificationRequest,
    MessageResponse,
    OtpRequestByEmail,
    PasswordChangeRequest,
    Token,
    UserCreate,
    UserLogin,
    UserRead,
)
from app.services import auth_service
from app.services.email_service import EmailSendError

settings = get_settings()
router = APIRouter()


def _raise_for_otp_error(error: Exception) -> None:
    if isinstance(error, OtpNotFoundError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No verification code was requested. Please request a new code.",
        ) from error
    if isinstance(error, OtpExpiredError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This verification code has expired. Please request a new one.",
        ) from error
    if isinstance(error, OtpTooManyAttemptsError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Too many incorrect attempts. Please request a new verification code.",
        ) from error
    if isinstance(error, OtpInvalidError):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect verification code.") from error


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


@router.post("/verify-email", response_model=UserRead)
def verify_email(
    data: EmailVerificationRequest,
    db: Session = Depends(get_db),
):
    try:
        return auth_service.verify_email(db, data.email, data.code)
    except InvalidCredentialsError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")
    except (OtpNotFoundError, OtpExpiredError, OtpInvalidError, OtpTooManyAttemptsError) as error:
        _raise_for_otp_error(error)


@router.post("/resend-verification", response_model=MessageResponse)
@limiter.limit(settings.OTP_REQUEST_RATE_LIMIT)
def resend_verification(
    request: Request,
    data: OtpRequestByEmail,
    db: Session = Depends(get_db),
):
    try:
        auth_service.resend_verification_email(db, data.email)
    except EmailSendError:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Could not send the verification email right now. Please try again shortly.",
        )
    return MessageResponse(message="If an account with that email exists, a verification code has been sent.")


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
    except EmailNotVerifiedError as error:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": "email_not_verified",
                "message": "Please verify your email address before logging in.",
            },
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


@router.post("/request-password-change-otp", response_model=MessageResponse)
@limiter.limit(settings.OTP_REQUEST_RATE_LIMIT)
def request_password_change_otp(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        auth_service.request_password_change_otp(db, current_user)
    except EmailSendError:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Could not send the verification email right now. Please try again shortly.",
        )
    return MessageResponse(message="A verification code has been sent to your email.")


@router.post("/change-password", response_model=MessageResponse)
def change_password(
    data: PasswordChangeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        auth_service.change_password(db, current_user, data)
    except InvalidCurrentPasswordError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Current password is incorrect")
    except (OtpNotFoundError, OtpExpiredError, OtpInvalidError, OtpTooManyAttemptsError) as error:
        _raise_for_otp_error(error)
    return MessageResponse(message="Your password has been changed.")


@router.post("/request-account-deletion-otp", response_model=MessageResponse)
@limiter.limit(settings.OTP_REQUEST_RATE_LIMIT)
def request_account_deletion_otp(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        auth_service.request_account_deletion_otp(db, current_user)
    except EmailSendError:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Could not send the verification email right now. Please try again shortly.",
        )
    return MessageResponse(message="A verification code has been sent to your email.")


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
def delete_own_account(
    data: AccountDeletionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        auth_service.delete_own_account(db, current_user, data.code)
    except (OtpNotFoundError, OtpExpiredError, OtpInvalidError, OtpTooManyAttemptsError) as error:
        _raise_for_otp_error(error)
    except LastAdministratorError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete the last remaining administrator. Promote another user to admin first.",
        )