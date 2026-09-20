def build_snippet(text: str, query: str, context_chars: int = 80) -> str:
    normalized_text = " ".join(text.split())
    lowered = normalized_text.lower()
    match_index = lowered.find(query.lower())

    if match_index == -1:
        window = normalized_text[: context_chars * 2].rstrip()
        if len(normalized_text) > context_chars * 2:
            window += "..."
        return window

    start = max(0, match_index - context_chars)
    end = min(len(normalized_text), match_index + len(query) + context_chars)
    snippet = normalized_text[start:end].strip()

    if start > 0:
        snippet = "..." + snippet
    if end < len(normalized_text):
        snippet = snippet + "..."
    return snippet


def distance_to_similarity_percentage(distance: float) -> int:
    similarity = max(0.0, min(1.0, 1 - distance))
    return round(similarity * 100)