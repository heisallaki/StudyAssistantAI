from datetime import date

from app.services.planner_summary import (
    format_deadlines_summary,
    format_goals_summary,
    format_quiz_performance_summary,
    format_subjects_summary,
)


def test_format_subjects_summary_empty():
    assert format_subjects_summary([]) == "The student has no subjects set up yet."


def test_format_subjects_summary_includes_priority_and_progress():
    subjects = [
        {"name": "Databases", "priority": "high", "topic_count": 4, "completed_topic_count": 1, "progress_percentage": 25}
    ]
    summary = format_subjects_summary(subjects)
    assert "Databases" in summary
    assert "priority=high" in summary
    assert "1/4 topics complete" in summary
    assert "25%" in summary


def test_format_goals_summary_no_active_goals():
    goals = [{"title": "Old goal", "status": "completed", "target_date": None}]
    assert format_goals_summary(goals, date(2026, 1, 1)) == "The student has no active study goals."


def test_format_goals_summary_computes_days_remaining():
    goals = [{"title": "Finish React course", "status": "active", "target_date": date(2026, 1, 11)}]
    summary = format_goals_summary(goals, date(2026, 1, 1))
    assert "Finish React course" in summary
    assert "target in 10 day(s)" in summary


def test_format_goals_summary_handles_no_target_date():
    goals = [{"title": "Learn Rust", "status": "active", "target_date": None}]
    summary = format_goals_summary(goals, date(2026, 1, 1))
    assert "Learn Rust: no target date" in summary


def test_format_deadlines_summary_excludes_completed():
    deadlines = [
        {"title": "Assignment 1", "due_date": date(2026, 1, 5), "is_completed": True},
        {"title": "Exam", "due_date": date(2026, 1, 8), "is_completed": False},
    ]
    summary = format_deadlines_summary(deadlines, date(2026, 1, 1))
    assert "Assignment 1" not in summary
    assert "Exam" in summary
    assert "due in 7 day(s)" in summary


def test_format_deadlines_summary_none_upcoming():
    deadlines = [{"title": "Old", "due_date": date(2026, 1, 1), "is_completed": True}]
    assert format_deadlines_summary(deadlines, date(2026, 1, 1)) == "The student has no upcoming deadlines."


def test_format_quiz_performance_summary_empty_returns_none():
    assert format_quiz_performance_summary({}) is None


def test_format_quiz_performance_summary_averages_scores():
    summary = format_quiz_performance_summary({"Databases": [80, 60], "General": [50]})
    assert "Databases: 70% average over 2 attempt(s)" in summary
    assert "General: 50% average over 1 attempt(s)" in summary