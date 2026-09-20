import json

import pytest

from app.services.flashcard_parsing import parse_generated_flashcards


def test_parses_valid_flashcards():
    raw = json.dumps(
        {
            "flashcards": [
                {"front": "What is a primary key?", "back": "A column that uniquely identifies a row."},
                {"front": "What does CPU stand for?", "back": "Central Processing Unit."},
            ]
        }
    )
    cards = parse_generated_flashcards(raw)
    assert len(cards) == 2
    assert cards[0].front == "What is a primary key?"
    assert cards[1].back == "Central Processing Unit."


def test_filters_out_blank_front_or_back():
    raw = json.dumps(
        {
            "flashcards": [
                {"front": "", "back": "Some answer"},
                {"front": "Some question", "back": "   "},
                {"front": "Valid front", "back": "Valid back"},
            ]
        }
    )
    cards = parse_generated_flashcards(raw)
    assert len(cards) == 1
    assert cards[0].front == "Valid front"


def test_empty_flashcards_list_returns_empty():
    raw = json.dumps({"flashcards": []})
    assert parse_generated_flashcards(raw) == []


def test_missing_flashcards_key_defaults_to_empty():
    raw = json.dumps({})
    assert parse_generated_flashcards(raw) == []


def test_invalid_json_raises_json_decode_error():
    with pytest.raises(json.JSONDecodeError):
        parse_generated_flashcards("not valid json")