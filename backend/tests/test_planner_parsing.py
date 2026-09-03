import json

import pytest

from app.services.planner_parsing import parse_generated_recommendations


def test_parses_valid_recommendations():
    raw = json.dumps(
        {
            "recommendations": [
                {"subject": "Databases", "action": "Review normalization", "reason": "Only 25% mastered."},
                {"subject": "General", "action": "Plan a review session", "reason": "Exam in 3 days."},
            ]
        }
    )
    recommendations = parse_generated_recommendations(raw)
    assert len(recommendations) == 2
    assert recommendations[0].subject == "Databases"
    assert recommendations[1].action == "Plan a review session"


def test_filters_out_blank_fields():
    raw = json.dumps(
        {
            "recommendations": [
                {"subject": "", "action": "Do something", "reason": "Because"},
                {"subject": "Databases", "action": "  ", "reason": "Because"},
                {"subject": "Databases", "action": "Study", "reason": "Because"},
            ]
        }
    )
    recommendations = parse_generated_recommendations(raw)
    assert len(recommendations) == 1
    assert recommendations[0].action == "Study"


def test_caps_at_five_recommendations():
    raw = json.dumps(
        {
            "recommendations": [
                {"subject": f"Subject {i}", "action": "Study", "reason": "Because"} for i in range(8)
            ]
        }
    )
    recommendations = parse_generated_recommendations(raw)
    assert len(recommendations) == 5


def test_missing_recommendations_key_defaults_to_empty():
    assert parse_generated_recommendations(json.dumps({})) == []


def test_invalid_json_raises_json_decode_error():
    with pytest.raises(json.JSONDecodeError):
        parse_generated_recommendations("not valid json")