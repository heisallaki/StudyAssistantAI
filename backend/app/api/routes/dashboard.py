from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.dashboard import DashboardOverview
from app.services import dashboard_service

router = APIRouter()


@router.get("/overview", response_model=DashboardOverview)
def read_dashboard_overview(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return dashboard_service.get_overview(db, current_user)