FLASHCARD_GENERATION_INSTRUCTIONS = (
    "You are generating study flashcards for a student. Respond with ONLY a JSON object "
    "(no markdown, no commentary, no code fences) matching exactly this structure:\n\n"
    '{"flashcards": [{"front": "...", "back": "..."}]}\n\n'
    "Rules:\n"
    '- "front" is a short question, term, or prompt the student should recognize\n'
    '- "back" is the concise answer or definition\n'
    "- Keep each side to at most two sentences\n"
    "- Base every flashcard only on the given subject or material. Never invent specific facts "
    "you were not given context for; if you lack enough context, write general but accurate "
    "flashcards about the named subject instead of fabricating specifics."
)


def build_flashcard_prompt(
    subject_context: str | None,
    document_context: str | None,
    deck_title: str,
    count: int,
) -> str:
    parts = [
        FLASHCARD_GENERATION_INSTRUCTIONS,
        f'Generate exactly {count} flashcards for a deck titled "{deck_title}".',
    ]
    if subject_context:
        parts.append(subject_context)
    if document_context:
        parts.append(document_context)
    return "\n\n".join(parts)