import json
import logging
import uuid
from datetime import date, time, timedelta

from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.ai.prompts.planner_prompts import build_planner_recommendation_prompt
from app.ai.providers.base import AIProvider, AIProviderError
from app.core.exceptions import (
    DeadlineNotFoundError,
    PlannerRecommendationFailedError,
    StudyGoalNotFoundError,
    StudySessionNotFoundError,
    SubjectNotFoundError,
)
from app.models.deadline import Deadline
from app.models.study_goal import StudyGoal
from app.models.study_session import StudySession
from app.repositories import (
    deadline_repository,
    quiz_attempt_repository,
    study_goal_repository,
    study_session_repository,
    subject_repository,
)
from app.schemas.planner import (
    CalendarEntry,
    DeadlineCreate,
    DeadlineUpdate,
    PlannerRecommendation,
    StudyGoalCreate,
    StudyGoalUpdate,
    StudySessionCreate,
    StudySessionUpdate,
)
from app.services.planner_parsing import parse_generated_recommendations
from app.services.planner_summary import (
    format_deadlines_summary,
    format_goals_summary,
    format_quiz_performance_summary,
    format_subjects_summary,
)

logger = logging.getLogger(__name__)

UPCOMING_DEADLINE_WINDOW_DAYS = 14


def list_goals(db: Session, user_id: uuid.UUID, status: str | None = None) -> list[StudyGoal]:
    return study_goal_repository.list_for_user(db, user_id, status)


def get_goal(db: Session, goal_id: uuid.UUID, user_id: uuid.UUID) -> StudyGoal:
    goal = study_goal_repository.get_by_id_for_user(db, goal_id, user_id)
    if goal is None:
        raise StudyGoalNotFoundError(goal_id)
    return goal


def create_goal(db: Session, user_id: uuid.UUID, data: StudyGoalCreate) -> StudyGoal:
    if data.subject_id is not None and subject_repository.get_by_id_for_user(db, data.subject_id, user_id) is None:
        raise SubjectNotFoundError(data.subject_id)
    return study_goal_repository.create(db, user_id, data.model_dump())


def update_goal(db: Session, goal_id: uuid.UUID, user_id: uuid.UUID, data: StudyGoalUpdate) -> StudyGoal:
    goal = get_goal(db, goal_id, user_id)
    update_data = data.model_dump(exclude_unset=True)
    new_subject_id = update_data.get("subject_id")
    if new_subject_id is not None and subject_repository.get_by_id_for_user(db, new_subject_id, user_id) is None:
        raise SubjectNotFoundError(new_subject_id)
    return study_goal_repository.update(db, goal, update_data)


def delete_goal(db: Session, goal_id: uuid.UUID, user_id: uuid.UUID) -> None:
    goal = get_goal(db, goal_id, user_id)
    study_goal_repository.delete(db, goal)


def list_sessions(
    db: Session,
    user_id: uuid.UUID,
    start: date | None = None,
    end: date | None = None,
    subject_id: uuid.UUID | None = None,
    status: str | None = None,
) -> list[StudySession]:
    return study_session_repository.list_for_user(db, user_id, start, end, subject_id, status)


def get_session(db: Session, session_id: uuid.UUID, user_id: uuid.UUID) -> StudySession:
    session = study_session_repository.get_by_id_for_user(db, session_id, user_id)
    if session is None:
        raise StudySessionNotFoundError(session_id)
    return session


def create_session(db: Session, user_id: uuid.UUID, data: StudySessionCreate) -> StudySession:
    if data.subject_id is not None and subject_repository.get_by_id_for_user(db, data.subject_id, user_id) is None:
        raise SubjectNotFoundError(data.subject_id)
    if data.goal_id is not None and study_goal_repository.get_by_id_for_user(db, data.goal_id, user_id) is None:
        raise StudyGoalNotFoundError(data.goal_id)
    return study_session_repository.create(db, user_id, data.model_dump())


def update_session(
    db: Session, session_id: uuid.UUID, user_id: uuid.UUID, data: StudySessionUpdate
) -> StudySession:
    session = get_session(db, session_id, user_id)
    update_data = data.model_dump(exclude_unset=True)
    new_subject_id = update_data.get("subject_id")
    if new_subject_id is not None and subject_repository.get_by_id_for_user(db, new_subject_id, user_id) is None:
        raise SubjectNotFoundError(new_subject_id)
    new_goal_id = update_data.get("goal_id")
    if new_goal_id is not None and study_goal_repository.get_by_id_for_user(db, new_goal_id, user_id) is None:
        raise StudyGoalNotFoundError(new_goal_id)
    return study_session_repository.update(db, session, update_data)


def delete_session(db: Session, session_id: uuid.UUID, user_id: uuid.UUID) -> None:
    session = get_session(db, session_id, user_id)
    study_session_repository.delete(db, session)


def list_deadlines(
    db: Session,
    user_id: uuid.UUID,
    start: date | None = None,
    end: date | None = None,
    include_completed: bool = True,
) -> list[Deadline]:
    return deadline_repository.list_for_user(db, user_id, start, end, include_completed)


def get_deadline(db: Session, deadline_id: uuid.UUID, user_id: uuid.UUID) -> Deadline:
    deadline = deadline_repository.get_by_id_for_user(db, deadline_id, user_id)
    if deadline is None:
        raise DeadlineNotFoundError(deadline_id)
    return deadline


def create_deadline(db: Session, user_id: uuid.UUID, data: DeadlineCreate) -> Deadline:
    if data.subject_id is not None and subject_repository.get_by_id_for_user(db, data.subject_id, user_id) is None:
        raise SubjectNotFoundError(data.subject_id)
    return deadline_repository.create(db, user_id, data.model_dump())


def update_deadline(db: Session, deadline_id: uuid.UUID, user_id: uuid.UUID, data: DeadlineUpdate) -> Deadline:
    deadline = get_deadline(db, deadline_id, user_id)
    update_data = data.model_dump(exclude_unset=True)
    new_subject_id = update_data.get("subject_id")
    if new_subject_id is not None and subject_repository.get_by_id_for_user(db, new_subject_id, user_id) is None:
        raise SubjectNotFoundError(new_subject_id)
    return deadline_repository.update(db, deadline, update_data)


def delete_deadline(db: Session, deadline_id: uuid.UUID, user_id: uuid.UUID) -> None:
    deadline = get_deadline(db, deadline_id, user_id)
    deadline_repository.delete(db, deadline)


def get_calendar(db: Session, user_id: uuid.UUID, start: date, end: date) -> list[CalendarEntry]:
    sessions = study_session_repository.list_for_user(db, user_id, start=start, end=end)
    deadlines = deadline_repository.list_for_user(db, user_id, start=start, end=end)

    entries = [
        CalendarEntry(
            entry_type="session",
            id=session.id,
            title=session.title,
            date=session.scheduled_date,
            subject_id=session.subject_id,
            status=session.status,
            start_time=session.start_time,
            duration_minutes=session.duration_minutes,
        )
        for session in sessions
    ]
    entries += [
        CalendarEntry(
            entry_type="deadline",
            id=deadline.id,
            title=deadline.title,
            date=deadline.due_date,
            subject_id=deadline.subject_id,
            is_completed=deadline.is_completed,
        )
        for deadline in deadlines
    ]
    entries.sort(key=lambda entry: (entry.date, entry.start_time is None, entry.start_time or time.min))
    return entries


async def generate_recommendations(
    db: Session, ai_provider: AIProvider, user_id: uuid.UUID
) -> list[PlannerRecommendation]:
    today = date.today()

    subjects = subject_repository.list_for_user(db, user_id)
    goals = study_goal_repository.list_for_user(db, user_id)
    deadlines = deadline_repository.list_for_user(
        db, user_id, start=today, end=today + timedelta(days=UPCOMING_DEADLINE_WINDOW_DAYS)
    )
    attempts = quiz_attempt_repository.list_for_user(db, user_id)

    subjects_data = [
        {
            "name": subject.name,
            "priority": subject.priority,
            "topic_count": subject.topic_count,
            "completed_topic_count": subject.completed_topic_count,
            "progress_percentage": subject.progress_percentage,
        }
        for subject in subjects
    ]
    goals_data = [
        {"title": goal.title, "status": goal.status, "target_date": goal.target_date} for goal in goals
    ]
    deadlines_data = [
        {"title": deadline.title, "due_date": deadline.due_date, "is_completed": deadline.is_completed}
        for deadline in deadlines
    ]

    subject_names = {subject.id: subject.name for subject in subjects}
    scores_by_subject: dict[str, list[int]] = {}
    for attempt in attempts:
        if attempt.status != "completed" or attempt.percentage_score is None:
            continue
        label = subject_names.get(attempt.subject_id, "General") if attempt.subject_id else "General"
        scores_by_subject.setdefault(label, []).append(attempt.percentage_score)

    subjects_summary = format_subjects_summary(subjects_data)
    goals_summary = format_goals_summary(goals_data, today)
    deadlines_summary = format_deadlines_summary(deadlines_data, today)
    quiz_summary = format_quiz_performance_summary(scores_by_subject)

    prompt = build_planner_recommendation_prompt(subjects_summary, goals_summary, deadlines_summary, quiz_summary)
    messages = [{"role": "user", "content": prompt}]

    try:
        raw_response = await ai_provider.generate_reply(messages, response_format="json")
    except AIProviderError as error:
        raise PlannerRecommendationFailedError(str(error))

    try:
        generated = parse_generated_recommendations(raw_response)
    except (json.JSONDecodeError, ValidationError) as error:
        logger.warning("Failed to parse planner recommendation response: %s", error)
        raise PlannerRecommendationFailedError("The AI returned an unexpected response format.")

    if not generated:
        raise PlannerRecommendationFailedError("The AI did not return any recommendations.")

    return [
        PlannerRecommendation(subject=item.subject, action=item.action, reason=item.reason)
        for item in generated
    ]