import uuid
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.ai.providers.base import AIProvider
from app.api.deps import get_ai_provider, get_current_user
from app.core.exceptions import (
    DeadlineNotFoundError,
    PlannerRecommendationFailedError,
    StudyGoalNotFoundError,
    StudySessionNotFoundError,
    SubjectNotFoundError,
)
from app.db.session import get_db
from app.models.user import User
from app.schemas.planner import (
    CalendarEntry,
    DeadlineCreate,
    DeadlineRead,
    DeadlineUpdate,
    PlannerRecommendationResponse,
    StudyGoalCreate,
    StudyGoalRead,
    StudyGoalUpdate,
    StudySessionCreate,
    StudySessionRead,
    StudySessionUpdate,
)
from app.services import planner_service

router = APIRouter()


@router.get("/goals", response_model=list[StudyGoalRead])
def list_goals(
    status_filter: str | None = Query(default=None, alias="status"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return planner_service.list_goals(db, current_user.id, status_filter)


@router.post("/goals", response_model=StudyGoalRead, status_code=status.HTTP_201_CREATED)
def create_goal(
    data: StudyGoalCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        return planner_service.create_goal(db, current_user.id, data)
    except SubjectNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subject not found")


@router.get("/goals/{goal_id}", response_model=StudyGoalRead)
def get_goal(
    goal_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        return planner_service.get_goal(db, goal_id, current_user.id)
    except StudyGoalNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Study goal not found")


@router.put("/goals/{goal_id}", response_model=StudyGoalRead)
def update_goal(
    goal_id: uuid.UUID,
    data: StudyGoalUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        return planner_service.update_goal(db, goal_id, current_user.id, data)
    except StudyGoalNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Study goal not found")
    except SubjectNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subject not found")


@router.delete("/goals/{goal_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_goal(
    goal_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        planner_service.delete_goal(db, goal_id, current_user.id)
    except StudyGoalNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Study goal not found")


@router.get("/sessions", response_model=list[StudySessionRead])
def list_sessions(
    start: date | None = Query(default=None),
    end: date | None = Query(default=None),
    subject_id: uuid.UUID | None = Query(default=None),
    status_filter: str | None = Query(default=None, alias="status"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return planner_service.list_sessions(db, current_user.id, start, end, subject_id, status_filter)


@router.post("/sessions", response_model=StudySessionRead, status_code=status.HTTP_201_CREATED)
def create_session(
    data: StudySessionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        return planner_service.create_session(db, current_user.id, data)
    except SubjectNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subject not found")
    except StudyGoalNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Study goal not found")


@router.get("/sessions/{session_id}", response_model=StudySessionRead)
def get_session(
    session_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        return planner_service.get_session(db, session_id, current_user.id)
    except StudySessionNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Study session not found")


@router.put("/sessions/{session_id}", response_model=StudySessionRead)
def update_session(
    session_id: uuid.UUID,
    data: StudySessionUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        return planner_service.update_session(db, session_id, current_user.id, data)
    except StudySessionNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Study session not found")
    except SubjectNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subject not found")
    except StudyGoalNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Study goal not found")


@router.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_session(
    session_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        planner_service.delete_session(db, session_id, current_user.id)
    except StudySessionNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Study session not found")


@router.get("/deadlines", response_model=list[DeadlineRead])
def list_deadlines(
    start: date | None = Query(default=None),
    end: date | None = Query(default=None),
    include_completed: bool = Query(default=True),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return planner_service.list_deadlines(db, current_user.id, start, end, include_completed)


@router.post("/deadlines", response_model=DeadlineRead, status_code=status.HTTP_201_CREATED)
def create_deadline(
    data: DeadlineCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        return planner_service.create_deadline(db, current_user.id, data)
    except SubjectNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subject not found")


@router.get("/deadlines/{deadline_id}", response_model=DeadlineRead)
def get_deadline(
    deadline_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        return planner_service.get_deadline(db, deadline_id, current_user.id)
    except DeadlineNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Deadline not found")


@router.put("/deadlines/{deadline_id}", response_model=DeadlineRead)
def update_deadline(
    deadline_id: uuid.UUID,
    data: DeadlineUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        return planner_service.update_deadline(db, deadline_id, current_user.id, data)
    except DeadlineNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Deadline not found")
    except SubjectNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subject not found")


@router.delete("/deadlines/{deadline_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_deadline(
    deadline_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        planner_service.delete_deadline(db, deadline_id, current_user.id)
    except DeadlineNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Deadline not found")


@router.get("/calendar", response_model=list[CalendarEntry])
def get_calendar(
    start: date = Query(...),
    end: date = Query(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return planner_service.get_calendar(db, current_user.id, start, end)


@router.post("/recommendations", response_model=PlannerRecommendationResponse)
async def get_recommendations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    ai_provider: AIProvider = Depends(get_ai_provider),
):
    try:
        recommendations = await planner_service.generate_recommendations(db, ai_provider, current_user.id)
    except PlannerRecommendationFailedError as error:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(error))
    return PlannerRecommendationResponse(recommendations=recommendations)