import uuid
from datetime import date, timedelta

from sqlalchemy.orm import Session

from app.repositories import (
    flashcard_deck_repository,
    quiz_attempt_repository,
    study_goal_repository,
    study_session_repository,
    subject_repository,
)
from app.schemas.analytics import (
    AnalyticsOverview,
    PerformanceTrendPoint,
    StudyTimePoint,
    SubjectBreakdown,
    WeakArea,
)
from app.services.analytics_aggregation import (
    compute_overview,
    compute_performance_trend,
    compute_study_time_series,
    compute_subject_breakdown,
    compute_weak_areas,
)


def get_overview(db: Session, user_id: uuid.UUID) -> AnalyticsOverview:
    subjects = subject_repository.list_for_user(db, user_id)
    attempts = quiz_attempt_repository.list_for_user(db, user_id)
    decks = flashcard_deck_repository.list_for_user(db, user_id)
    sessions = study_session_repository.list_for_user(db, user_id, status="completed")
    goals = study_goal_repository.list_for_user(db, user_id, status="active")

    session_minutes = [session.duration_minutes for session in sessions]
    quiz_scores = [
        attempt.percentage_score
        for attempt in attempts
        if attempt.status == "completed" and attempt.percentage_score is not None
    ]
    flashcard_progress = [
        {"status": card.progress.status, "times_reviewed": card.progress.times_reviewed}
        for deck in decks
        for card in deck.flashcards
    ]

    result = compute_overview(session_minutes, quiz_scores, flashcard_progress, len(subjects), len(goals))
    return AnalyticsOverview(**result)


def get_performance_trend(db: Session, user_id: uuid.UUID, days: int) -> list[PerformanceTrendPoint]:
    attempts = quiz_attempt_repository.list_for_user(db, user_id)
    cutoff = date.today() - timedelta(days=days)

    filtered = [
        {"completed_date": attempt.completed_at.date(), "score_percentage": attempt.percentage_score}
        for attempt in attempts
        if attempt.status == "completed"
        and attempt.percentage_score is not None
        and attempt.completed_at is not None
        and attempt.completed_at.date() >= cutoff
    ]

    result = compute_performance_trend(filtered)
    return [PerformanceTrendPoint(**point) for point in result]


def get_study_time_series(db: Session, user_id: uuid.UUID, days: int) -> list[StudyTimePoint]:
    end = date.today()
    start = end - timedelta(days=days - 1)
    sessions = study_session_repository.list_for_user(db, user_id, start=start, end=end, status="completed")

    minutes_by_date: dict[date, int] = {}
    for session in sessions:
        minutes_by_date[session.scheduled_date] = (
            minutes_by_date.get(session.scheduled_date, 0) + session.duration_minutes
        )

    result = compute_study_time_series(minutes_by_date, start, end)
    return [StudyTimePoint(**point) for point in result]


def _build_subject_data(db: Session, user_id: uuid.UUID) -> list[dict]:
    subjects = subject_repository.list_for_user(db, user_id)
    attempts = quiz_attempt_repository.list_for_user(db, user_id)
    decks = flashcard_deck_repository.list_for_user(db, user_id)
    sessions = study_session_repository.list_for_user(db, user_id, status="completed")

    quiz_scores_by_subject: dict[uuid.UUID | None, list[int]] = {}
    for attempt in attempts:
        if attempt.status == "completed" and attempt.percentage_score is not None:
            quiz_scores_by_subject.setdefault(attempt.subject_id, []).append(attempt.percentage_score)

    flashcard_statuses_by_subject: dict[uuid.UUID | None, list[str]] = {}
    for deck in decks:
        for card in deck.flashcards:
            flashcard_statuses_by_subject.setdefault(deck.subject_id, []).append(card.progress.status)

    study_minutes_by_subject: dict[uuid.UUID | None, int] = {}
    for session in sessions:
        study_minutes_by_subject[session.subject_id] = (
            study_minutes_by_subject.get(session.subject_id, 0) + session.duration_minutes
        )

    return [
        {
            "id": subject.id,
            "name": subject.name,
            "priority": subject.priority,
            "topic_count": subject.topic_count,
            "topic_progress_percentage": subject.progress_percentage,
            "quiz_scores": quiz_scores_by_subject.get(subject.id, []),
            "flashcard_statuses": flashcard_statuses_by_subject.get(subject.id, []),
            "study_minutes": study_minutes_by_subject.get(subject.id, 0),
        }
        for subject in subjects
    ]


def get_subject_breakdown(db: Session, user_id: uuid.UUID) -> list[SubjectBreakdown]:
    subjects_data = _build_subject_data(db, user_id)
    result = compute_subject_breakdown(subjects_data)
    return [SubjectBreakdown(**item) for item in result]


def get_weak_areas(db: Session, user_id: uuid.UUID) -> list[WeakArea]:
    subjects_data = _build_subject_data(db, user_id)
    breakdown = compute_subject_breakdown(subjects_data)
    topic_counts = {item["id"]: item["topic_count"] for item in subjects_data}
    result = compute_weak_areas(breakdown, topic_counts)
    return [WeakArea(**item) for item in result]