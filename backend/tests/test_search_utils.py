from app.services.search_utils import build_snippet, distance_to_similarity_percentage


def test_build_snippet_centers_on_match():
    text = "The mitochondria is the powerhouse of the cell and produces ATP for the organism."
    snippet = build_snippet(text, "powerhouse", context_chars=10)
    assert "powerhouse" in snippet
    assert snippet.startswith("...")


def test_build_snippet_match_at_start_has_no_leading_ellipsis():
    text = "Powerhouse of the cell."
    snippet = build_snippet(text, "Powerhouse", context_chars=10)
    assert not snippet.startswith("...")


def test_build_snippet_no_match_falls_back_to_truncation():
    text = "A" * 300
    snippet = build_snippet(text, "zzz", context_chars=20)
    assert snippet.endswith("...")
    assert len(snippet) <= 44


def test_build_snippet_short_text_returned_whole():
    text = "Short text."
    snippet = build_snippet(text, "zzz", context_chars=80)
    assert snippet == "Short text."


def test_build_snippet_normalizes_whitespace():
    text = "Line one\n\nLine   two"
    snippet = build_snippet(text, "zzz", context_chars=80)
    assert snippet == "Line one Line two"


def test_distance_to_similarity_percentage_zero_distance_is_full_match():
    assert distance_to_similarity_percentage(0.0) == 100


def test_distance_to_similarity_percentage_full_distance_is_no_match():
    assert distance_to_similarity_percentage(1.0) == 0


def test_distance_to_similarity_percentage_midpoint():
    assert distance_to_similarity_percentage(0.3) == 70


def test_distance_to_similarity_percentage_clamps_negative_distance():
    assert distance_to_similarity_percentage(-0.2) == 100


def test_distance_to_similarity_percentage_clamps_over_one():
    assert distance_to_similarity_percentage(1.5) == 0