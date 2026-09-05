from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.analytics import (
    AnalyticsOverview,
    PerformanceTrendPoint,
    StudyTimePoint,
    SubjectBreakdown,
    WeakArea,
)
from app.services import analytics_service

router = APIRouter()


@router.get("/overview", response_model=AnalyticsOverview)
def get_overview(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return analytics_service.get_overview(db, current_user.id)


@router.get("/performance-trend", response_model=list[PerformanceTrendPoint])
def get_performance_trend(
    days: int = Query(default=30, ge=1, le=365),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return analytics_service.get_performance_trend(db, current_user.id, days)


@router.get("/study-time", response_model=list[StudyTimePoint])
def get_study_time(
    days: int = Query(default=30, ge=1, le=365),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return analytics_service.get_study_time_series(db, current_user.id, days)


@router.get("/subject-breakdown", response_model=list[SubjectBreakdown])
def get_subject_breakdown(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return analytics_service.get_subject_breakdown(db, current_user.id)


@router.get("/weak-areas", response_model=list[WeakArea])
def get_weak_areas(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return analytics_service.get_weak_areas(db, current_user.id)