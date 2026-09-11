import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_admin_user
from app.core.exceptions import CannotModifySelfError, LastAdministratorError, UserNotFoundError
from app.db.session import get_db
from app.models.user import User
from app.schemas.admin import (
    AdminSystemStats,
    AdminUserListResponse,
    AdminUserRead,
    AdminUserUpdate,
)
from app.services import admin_service

router = APIRouter()


@router.get("/stats", response_model=AdminSystemStats)
def get_system_stats(
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    return admin_service.get_system_stats(db)


@router.get("/users", response_model=AdminUserListResponse)
def list_users(
    search: str | None = Query(default=None, max_length=255),
    is_active: bool | None = Query(default=None),
    is_superuser: bool | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    return admin_service.list_users(db, search, is_active, is_superuser, page, page_size)


@router.get("/users/{user_id}", response_model=AdminUserRead)
def get_user(
    user_id: uuid.UUID,
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    try:
        return admin_service.get_user_detail(db, user_id)
    except UserNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")


@router.patch("/users/{user_id}", response_model=AdminUserRead)
def update_user(
    user_id: uuid.UUID,
    data: AdminUserUpdate,
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    try:
        return admin_service.update_user(db, current_admin, user_id, data)
    except UserNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    except CannotModifySelfError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Administrators cannot deactivate or revoke their own admin access",
        )
    except LastAdministratorError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot remove admin access from the last remaining administrator",
        )


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: uuid.UUID,
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    try:
        admin_service.delete_user(db, current_admin, user_id)
    except UserNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    except CannotModifySelfError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Administrators cannot delete their own account",
        )
    except LastAdministratorError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete the last remaining administrator",
        )