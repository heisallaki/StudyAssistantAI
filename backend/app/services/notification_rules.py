from datetime import date

STUDY_REMINDER_TYPE = "study_reminder"
DEADLINE_REMINDER_TYPE = "deadline_reminder"
QUIZ_REMINDER_TYPE = "quiz_reminder"

DEADLINE_REMINDER_WINDOW_DAYS = 3


def build_study_session_reminders(sessions: list[dict], today: date) -> list[dict]:
    reminders = []
    for session in sessions:
        if session["status"] != "planned" or session["scheduled_date"] > today:
            continue

        if session["scheduled_date"] == today:
            message = f"'{session['title']}' is scheduled for today."
        else:
            days_overdue = (today - session["scheduled_date"]).days
            message = (
                f"'{session['title']}' was scheduled {days_overdue} day(s) ago "
                "and hasn't been marked complete."
            )

        reminders.append(
            {
                "notification_type": STUDY_REMINDER_TYPE,
                "title": "Study session reminder",
                "message": message,
                "related_id": session["id"],
            }
        )
    return reminders


def build_deadline_reminders(deadlines: list[dict], today: date) -> list[dict]:
    reminders = []
    for deadline in deadlines:
        if deadline["is_completed"]:
            continue

        days_left = (deadline["due_date"] - today).days
        if days_left > DEADLINE_REMINDER_WINDOW_DAYS:
            continue

        if days_left < 0:
            message = f"'{deadline['title']}' was due {abs(days_left)} day(s) ago."
        elif days_left == 0:
            message = f"'{deadline['title']}' is due today."
        else:
            message = f"'{deadline['title']}' is due in {days_left} day(s)."

        reminders.append(
            {
                "notification_type": DEADLINE_REMINDER_TYPE,
                "title": "Deadline reminder",
                "message": message,
                "related_id": deadline["id"],
            }
        )
    return reminders


def build_quiz_reminders(weak_areas: list[dict]) -> list[dict]:
    reminders = []
    seen_subjects = set()
    for area in weak_areas:
        if area["subject_id"] in seen_subjects:
            continue
        seen_subjects.add(area["subject_id"])

        if area["reason"] == "low_quiz_scores":
            message = (
                f"Your quiz average in '{area['name']}' is {area['metric_value']}%. "
                "A bit more practice could help."
            )
        else:
            message = (
                f"'{area['name']}' progress is at {area['metric_value']}%. "
                "Consider reviewing with a quiz."
            )

        reminders.append(
            {
                "notification_type": QUIZ_REMINDER_TYPE,
                "title": "Quiz reminder",
                "message": message,
                "related_id": area["subject_id"],
            }
        )
    return reminders