from datetime import date

from app.services.analytics_aggregation import (
    compute_overview,
    compute_performance_trend,
    compute_study_time_series,
    compute_subject_breakdown,
    compute_weak_areas,
)


def test_compute_overview_with_no_data():
    result = compute_overview([], [], [], 0, 0)
    assert result["total_study_minutes"] == 0
    assert result["total_quizzes_taken"] == 0
    assert result["average_quiz_score"] is None
    assert result["total_flashcards_reviewed"] == 0
    assert result["flashcards_mastered"] == 0
    assert result["total_flashcards"] == 0


def test_compute_overview_aggregates_across_sources():
    result = compute_overview(
        session_minutes=[30, 45],
        quiz_scores=[80, 60],
        flashcard_progress=[
            {"status": "mastered", "times_reviewed": 3},
            {"status": "learning", "times_reviewed": 1},
            {"status": "new", "times_reviewed": 0},
        ],
        subjects_count=2,
        active_goals_count=1,
    )
    assert result["total_study_minutes"] == 75
    assert result["total_quizzes_taken"] == 2
    assert result["average_quiz_score"] == 70
    assert result["total_flashcards_reviewed"] == 4
    assert result["flashcards_mastered"] == 1
    assert result["total_flashcards"] == 3
    assert result["subjects_count"] == 2
    assert result["active_goals_count"] == 1


def test_compute_performance_trend_groups_and_averages_by_date():
    attempts = [
        {"completed_date": date(2026, 1, 1), "score_percentage": 80},
        {"completed_date": date(2026, 1, 1), "score_percentage": 60},
        {"completed_date": date(2026, 1, 3), "score_percentage": 100},
    ]
    trend = compute_performance_trend(attempts)
    assert trend == [
        {"date": date(2026, 1, 1), "average_score": 70, "attempts_count": 2},
        {"date": date(2026, 1, 3), "average_score": 100, "attempts_count": 1},
    ]


def test_compute_performance_trend_empty():
    assert compute_performance_trend([]) == []


def test_compute_study_time_series_fills_zero_days():
    minutes_by_date = {date(2026, 1, 2): 45}
    series = compute_study_time_series(minutes_by_date, date(2026, 1, 1), date(2026, 1, 3))
    assert series == [
        {"date": date(2026, 1, 1), "minutes": 0},
        {"date": date(2026, 1, 2), "minutes": 45},
        {"date": date(2026, 1, 3), "minutes": 0},
    ]


def test_compute_subject_breakdown_handles_subject_with_no_data():
    subjects = [
        {
            "id": "subj-1",
            "name": "New Subject",
            "priority": "medium",
            "topic_progress_percentage": 0,
            "quiz_scores": [],
            "flashcard_statuses": [],
            "study_minutes": 0,
        }
    ]
    breakdown = compute_subject_breakdown(subjects)
    assert breakdown[0]["quiz_average_score"] is None
    assert breakdown[0]["flashcard_mastery_percentage"] is None
    assert breakdown[0]["study_minutes"] == 0


def test_compute_subject_breakdown_computes_averages():
    subjects = [
        {
            "id": "subj-1",
            "name": "Databases",
            "priority": "high",
            "topic_progress_percentage": 50,
            "quiz_scores": [80, 60],
            "flashcard_statuses": ["mastered", "mastered", "learning", "new"],
            "study_minutes": 90,
        }
    ]
    breakdown = compute_subject_breakdown(subjects)
    assert breakdown[0]["quiz_average_score"] == 70
    assert breakdown[0]["flashcard_mastery_percentage"] == 50
    assert breakdown[0]["study_minutes"] == 90


def test_compute_weak_areas_flags_low_quiz_score():
    breakdown = [
        {
            "subject_id": "subj-1",
            "name": "Databases",
            "topic_progress_percentage": 80,
            "quiz_average_score": 40,
        }
    ]
    weak_areas = compute_weak_areas(breakdown, {"subj-1": 5})
    assert len(weak_areas) == 1
    assert weak_areas[0]["reason"] == "low_quiz_scores"
    assert weak_areas[0]["metric_value"] == 40


def test_compute_weak_areas_flags_low_topic_progress():
    breakdown = [
        {
            "subject_id": "subj-1",
            "name": "Databases",
            "topic_progress_percentage": 10,
            "quiz_average_score": None,
        }
    ]
    weak_areas = compute_weak_areas(breakdown, {"subj-1": 5})
    assert len(weak_areas) == 1
    assert weak_areas[0]["reason"] == "low_topic_progress"
    assert weak_areas[0]["metric_value"] == 10


def test_compute_weak_areas_excludes_subject_with_no_topics():
    breakdown = [
        {
            "subject_id": "subj-1",
            "name": "Empty Subject",
            "topic_progress_percentage": 0,
            "quiz_average_score": None,
        }
    ]
    weak_areas = compute_weak_areas(breakdown, {"subj-1": 0})
    assert weak_areas == []


def test_compute_weak_areas_excludes_healthy_subject():
    breakdown = [
        {
            "subject_id": "subj-1",
            "name": "Healthy Subject",
            "topic_progress_percentage": 90,
            "quiz_average_score": 85,
        }
    ]
    weak_areas = compute_weak_areas(breakdown, {"subj-1": 5})
    assert weak_areas == []


def test_compute_weak_areas_can_flag_same_subject_twice():
    breakdown = [
        {
            "subject_id": "subj-1",
            "name": "Struggling Subject",
            "topic_progress_percentage": 10,
            "quiz_average_score": 30,
        }
    ]
    weak_areas = compute_weak_areas(breakdown, {"subj-1": 5})
    reasons = {area["reason"] for area in weak_areas}
    assert reasons == {"low_quiz_scores", "low_topic_progress"}