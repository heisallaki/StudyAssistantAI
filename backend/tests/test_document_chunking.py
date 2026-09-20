from app.services.document_chunking import chunk_text


def test_empty_text_returns_no_chunks():
    assert chunk_text("") == []
    assert chunk_text("   ") == []


def test_short_text_returns_single_chunk():
    chunks = chunk_text("one two three", chunk_size=200, overlap=40)
    assert chunks == ["one two three"]


def test_long_text_splits_into_overlapping_chunks():
    text = " ".join(f"word{i}" for i in range(450))
    chunks = chunk_text(text, chunk_size=200, overlap=40)
    assert len(chunks) == 3
    assert chunks[0].split()[0] == "word0"
    assert chunks[0].split()[-1] == "word199"
    assert chunks[1].split()[0] == "word160"
    assert chunks[2].split()[-1] == "word449"


def test_chunks_cover_entire_text_without_gaps():
    text = " ".join(f"word{i}" for i in range(450))
    chunks = chunk_text(text, chunk_size=200, overlap=40)
    covered_words: set[str] = set()
    for chunk in chunks:
        covered_words.update(chunk.split())
    assert covered_words == {f"word{i}" for i in range(450)}