from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.profile import ProfileRead, ProfileUpdate
from app.services import profile_service

router = APIRouter()


@router.get("/me", response_model=ProfileRead)
def read_my_profile(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return profile_service.get_or_create_profile(db, current_user.id)


@router.patch("/me", response_model=ProfileRead)
def update_my_profile(
    updates: ProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return profile_service.update_profile(db, current_user.id, updates)