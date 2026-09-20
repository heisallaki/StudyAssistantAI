from datetime import date

from app.services.notification_rules import (
    build_deadline_reminders,
    build_quiz_reminders,
    build_study_session_reminders,
)


def test_study_reminder_skipped_for_future_session():
    sessions = [{"id": "s1", "title": "Algebra", "status": "planned", "scheduled_date": date(2026, 6, 5)}]
    reminders = build_study_session_reminders(sessions, date(2026, 6, 1))
    assert reminders == []


def test_study_reminder_fires_for_today():
    sessions = [{"id": "s1", "title": "Algebra", "status": "planned", "scheduled_date": date(2026, 6, 1)}]
    reminders = build_study_session_reminders(sessions, date(2026, 6, 1))
    assert len(reminders) == 1
    assert "is scheduled for today" in reminders[0]["message"]
    assert reminders[0]["related_id"] == "s1"


def test_study_reminder_fires_for_overdue_session():
    sessions = [{"id": "s1", "title": "Algebra", "status": "planned", "scheduled_date": date(2026, 5, 29)}]
    reminders = build_study_session_reminders(sessions, date(2026, 6, 1))
    assert len(reminders) == 1
    assert "3 day(s) ago" in reminders[0]["message"]


def test_study_reminder_skipped_for_completed_session():
    sessions = [{"id": "s1", "title": "Algebra", "status": "completed", "scheduled_date": date(2026, 5, 29)}]
    reminders = build_study_session_reminders(sessions, date(2026, 6, 1))
    assert reminders == []


def test_deadline_reminder_skipped_outside_window():
    deadlines = [{"id": "d1", "title": "Exam", "due_date": date(2026, 6, 10), "is_completed": False}]
    reminders = build_deadline_reminders(deadlines, date(2026, 6, 1))
    assert reminders == []


def test_deadline_reminder_fires_within_window():
    deadlines = [{"id": "d1", "title": "Exam", "due_date": date(2026, 6, 3), "is_completed": False}]
    reminders = build_deadline_reminders(deadlines, date(2026, 6, 1))
    assert len(reminders) == 1
    assert "due in 2 day(s)" in reminders[0]["message"]


def test_deadline_reminder_fires_for_today():
    deadlines = [{"id": "d1", "title": "Exam", "due_date": date(2026, 6, 1), "is_completed": False}]
    reminders = build_deadline_reminders(deadlines, date(2026, 6, 1))
    assert "is due today" in reminders[0]["message"]


def test_deadline_reminder_fires_for_overdue():
    deadlines = [{"id": "d1", "title": "Exam", "due_date": date(2026, 5, 30), "is_completed": False}]
    reminders = build_deadline_reminders(deadlines, date(2026, 6, 1))
    assert "was due 2 day(s) ago" in reminders[0]["message"]


def test_deadline_reminder_skipped_when_completed():
    deadlines = [{"id": "d1", "title": "Exam", "due_date": date(2026, 6, 1), "is_completed": True}]
    reminders = build_deadline_reminders(deadlines, date(2026, 6, 1))
    assert reminders == []


def test_quiz_reminder_for_low_quiz_scores():
    weak_areas = [{"subject_id": "subj-1", "name": "Databases", "reason": "low_quiz_scores", "metric_value": 40}]
    reminders = build_quiz_reminders(weak_areas)
    assert len(reminders) == 1
    assert "quiz average" in reminders[0]["message"]
    assert reminders[0]["related_id"] == "subj-1"


def test_quiz_reminder_for_low_topic_progress():
    weak_areas = [
        {"subject_id": "subj-1", "name": "Databases", "reason": "low_topic_progress", "metric_value": 10}
    ]
    reminders = build_quiz_reminders(weak_areas)
    assert "progress is at 10%" in reminders[0]["message"]


def test_quiz_reminder_deduplicates_same_subject():
    weak_areas = [
        {"subject_id": "subj-1", "name": "Databases", "reason": "low_quiz_scores", "metric_value": 40},
        {"subject_id": "subj-1", "name": "Databases", "reason": "low_topic_progress", "metric_value": 10},
    ]
    reminders = build_quiz_reminders(weak_areas)
    assert len(reminders) == 1