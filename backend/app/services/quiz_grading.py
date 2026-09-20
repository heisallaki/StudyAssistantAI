def _normalize(text: str) -> str:
    return " ".join(text.strip().lower().split())


def grade_answer(question_type: str, submitted_answer: str, correct_answer: str) -> bool:
    if not submitted_answer.strip():
        return False

    normalized_submitted = _normalize(submitted_answer)
    normalized_correct = _normalize(correct_answer)

    if question_type == "multiple_choice":
        return normalized_submitted == normalized_correct
    if question_type == "true_false":
        return normalized_submitted == normalized_correct
    if question_type == "short_answer":
        return normalized_submitted == normalized_correct
    return False