MASTERY_STREAK_THRESHOLD = 2


def apply_review_result(
    status: str,
    times_reviewed: int,
    times_correct: int,
    correct_streak: int,
    result: str,
) -> tuple[str, int, int, int]:
    times_reviewed += 1

    if result == "good":
        times_correct += 1
        correct_streak += 1
        status = "mastered" if correct_streak >= MASTERY_STREAK_THRESHOLD else "learning"
    else:
        correct_streak = 0
        status = "learning"

    return status, times_reviewed, times_correct, correct_streak