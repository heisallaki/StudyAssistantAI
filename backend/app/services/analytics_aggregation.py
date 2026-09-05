from datetime import date, timedelta

WEAK_QUIZ_SCORE_THRESHOLD = 60
WEAK_TOPIC_PROGRESS_THRESHOLD = 40


def compute_overview(
    session_minutes: list[int],
    quiz_scores: list[int],
    flashcard_progress: list[dict],
    subjects_count: int,
    active_goals_count: int,
) -> dict:
    average_quiz_score = round(sum(quiz_scores) / len(quiz_scores)) if quiz_scores else None
    total_flashcards_reviewed = sum(card["times_reviewed"] for card in flashcard_progress)
    flashcards_mastered = sum(1 for card in flashcard_progress if card["status"] == "mastered")

    return {
        "total_study_minutes": sum(session_minutes),
        "total_quizzes_taken": len(quiz_scores),
        "average_quiz_score": average_quiz_score,
        "total_flashcards_reviewed": total_flashcards_reviewed,
        "flashcards_mastered": flashcards_mastered,
        "total_flashcards": len(flashcard_progress),
        "subjects_count": subjects_count,
        "active_goals_count": active_goals_count,
    }


def compute_performance_trend(attempts: list[dict]) -> list[dict]:
    scores_by_date: dict[date, list[int]] = {}
    for attempt in attempts:
        scores_by_date.setdefault(attempt["completed_date"], []).append(attempt["score_percentage"])

    return [
        {
            "date": day,
            "average_score": round(sum(scores) / len(scores)),
            "attempts_count": len(scores),
        }
        for day, scores in sorted(scores_by_date.items())
    ]


def compute_study_time_series(minutes_by_date: dict[date, int], start: date, end: date) -> list[dict]:
    result = []
    current = start
    while current <= end:
        result.append({"date": current, "minutes": minutes_by_date.get(current, 0)})
        current += timedelta(days=1)
    return result


def compute_subject_breakdown(subjects: list[dict]) -> list[dict]:
    breakdown = []
    for subject in subjects:
        quiz_scores = subject["quiz_scores"]
        flashcard_statuses = subject["flashcard_statuses"]
        breakdown.append(
            {
                "subject_id": subject["id"],
                "name": subject["name"],
                "priority": subject["priority"],
                "topic_progress_percentage": subject["topic_progress_percentage"],
                "quiz_average_score": (
                    round(sum(quiz_scores) / len(quiz_scores)) if quiz_scores else None
                ),
                "flashcard_mastery_percentage": (
                    round(
                        sum(1 for status in flashcard_statuses if status == "mastered")
                        / len(flashcard_statuses)
                        * 100
                    )
                    if flashcard_statuses
                    else None
                ),
                "study_minutes": subject["study_minutes"],
            }
        )
    return breakdown


def compute_weak_areas(subject_breakdown: list[dict], topic_counts: dict) -> list[dict]:
    weak_areas = []
    for subject in subject_breakdown:
        if (
            subject["quiz_average_score"] is not None
            and subject["quiz_average_score"] < WEAK_QUIZ_SCORE_THRESHOLD
        ):
            weak_areas.append(
                {
                    "subject_id": subject["subject_id"],
                    "name": subject["name"],
                    "reason": "low_quiz_scores",
                    "metric_value": subject["quiz_average_score"],
                }
            )

        topic_count = topic_counts.get(subject["subject_id"], 0)
        if topic_count > 0 and subject["topic_progress_percentage"] < WEAK_TOPIC_PROGRESS_THRESHOLD:
            weak_areas.append(
                {
                    "subject_id": subject["subject_id"],
                    "name": subject["name"],
                    "reason": "low_topic_progress",
                    "metric_value": subject["topic_progress_percentage"],
                }
            )
    return weak_areas