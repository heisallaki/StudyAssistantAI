QUIZ_GENERATION_INSTRUCTIONS = (
    "You are generating a quiz for a student. Respond with ONLY a JSON object "
    "(no markdown, no commentary, no code fences) matching exactly this structure:\n\n"
    '{"questions": [{"question_type": "multiple_choice", "prompt": "...", '
    '"options": ["...", "...", "...", "..."], "correct_answer": "...", "explanation": "..."}]}\n\n'
    "Rules:\n"
    '- question_type must be exactly one of: "multiple_choice", "true_false", "short_answer"\n'
    '- For "multiple_choice": provide exactly 4 "options" and set "correct_answer" to the '
    "exact text of the correct option\n"
    '- For "true_false": omit "options" and set "correct_answer" to exactly "true" or "false"\n'
    '- For "short_answer": omit "options" and set "correct_answer" to a concise expected answer\n'
    '- Every question must include a short "explanation" of why the answer is correct\n'
    "- Base every question only on the given subject or material. Never invent specific facts "
    "you were not given context for; if you lack enough context, write general but accurate "
    "questions about the named subject instead of fabricating specifics."
)


def build_quiz_prompt(
    subject_context: str | None,
    document_context: str | None,
    difficulty: str,
    question_types: list[str],
    question_count: int,
) -> str:
    parts = [
        QUIZ_GENERATION_INSTRUCTIONS,
        f"Generate exactly {question_count} questions at {difficulty} difficulty.",
        f"Use only these question types, distributed roughly evenly: {', '.join(question_types)}.",
    ]
    if subject_context:
        parts.append(subject_context)
    if document_context:
        parts.append(document_context)
    return "\n\n".join(parts)