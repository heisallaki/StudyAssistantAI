DOCUMENT_CONTEXT_INSTRUCTION = (
    "The following excerpts are from the student's own uploaded documents. Use them if "
    "they are relevant, and say which document you drew from. If these excerpts do not "
    "contain what you need, say so honestly instead of guessing or pretending the "
    "document covers something it does not."
)


def build_document_context(chunks: list[tuple[str, str, float]]) -> str | None:
    if not chunks:
        return None

    excerpts = [f'Excerpt from "{filename}":\n{content}' for filename, content, _distance in chunks]
    joined = "\n\n".join(excerpts)
    return f"{DOCUMENT_CONTEXT_INSTRUCTION}\n\n{joined}"