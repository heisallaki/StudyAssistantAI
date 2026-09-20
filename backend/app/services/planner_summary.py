from datetime import date


def format_subjects_summary(subjects: list[dict]) -> str:
    if not subjects:
        return "The student has no subjects set up yet."
    lines = ["Subjects (name, priority, topic progress):"]
    for subject in subjects:
        lines.append(
            f"- {subject['name']}: priority={subject['priority']}, "
            f"{subject['completed_topic_count']}/{subject['topic_count']} topics complete "
            f"({subject['progress_percentage']}%)"
        )
    return "\n".join(lines)


def format_goals_summary(goals: list[dict], today: date) -> str:
    active_goals = [goal for goal in goals if goal["status"] == "active"]
    if not active_goals:
        return "The student has no active study goals."
    lines = ["Active goals:"]
    for goal in active_goals:
        if goal["target_date"] is not None:
            days_left = (goal["target_date"] - today).days
            lines.append(f"- {goal['title']}: target in {days_left} day(s) ({goal['target_date'].isoformat()})")
        else:
            lines.append(f"- {goal['title']}: no target date")
    return "\n".join(lines)


def format_deadlines_summary(deadlines: list[dict], today: date) -> str:
    upcoming = [deadline for deadline in deadlines if not deadline["is_completed"]]
    if not upcoming:
        return "The student has no upcoming deadlines."
    lines = ["Upcoming deadlines:"]
    for deadline in upcoming:
        days_left = (deadline["due_date"] - today).days
        lines.append(f"- {deadline['title']}: due in {days_left} day(s) ({deadline['due_date'].isoformat()})")
    return "\n".join(lines)


def format_quiz_performance_summary(scores_by_subject: dict[str, list[int]]) -> str | None:
    if not scores_by_subject:
        return None
    lines = ["Recent quiz performance (subject, average score):"]
    for label, scores in scores_by_subject.items():
        average = round(sum(scores) / len(scores))
        lines.append(f"- {label}: {average}% average over {len(scores)} attempt(s)")
    return "\n".join(lines)