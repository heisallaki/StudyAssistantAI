import json

import pytest
from pydantic import ValidationError

from app.services.quiz_parsing import parse_generated_quiz


def test_parses_valid_multiple_choice_question():
    raw = json.dumps(
        {
            "questions": [
                {
                    "question_type": "multiple_choice",
                    "prompt": "What is 2+2?",
                    "options": ["3", "4", "5", "6"],
                    "correct_answer": "4",
                    "explanation": "2+2 equals 4.",
                }
            ]
        }
    )
    questions = parse_generated_quiz(raw)
    assert len(questions) == 1
    assert questions[0].correct_answer == "4"


def test_drops_multiple_choice_question_with_answer_not_in_options():
    raw = json.dumps(
        {
            "questions": [
                {
                    "question_type": "multiple_choice",
                    "prompt": "What is 2+2?",
                    "options": ["3", "5", "6"],
                    "correct_answer": "4",
                    "explanation": "...",
                }
            ]
        }
    )
    assert parse_generated_quiz(raw) == []


def test_accepts_true_false_question():
    raw = json.dumps(
        {
            "questions": [
                {
                    "question_type": "true_false",
                    "prompt": "The sky is blue.",
                    "correct_answer": "true",
                    "explanation": "...",
                }
            ]
        }
    )
    assert len(parse_generated_quiz(raw)) == 1


def test_drops_true_false_question_with_invalid_answer():
    raw = json.dumps(
        {
            "questions": [
                {
                    "question_type": "true_false",
                    "prompt": "The sky is blue.",
                    "correct_answer": "maybe",
                    "explanation": "...",
                }
            ]
        }
    )
    assert parse_generated_quiz(raw) == []


def test_accepts_short_answer_question():
    raw = json.dumps(
        {
            "questions": [
                {
                    "question_type": "short_answer",
                    "prompt": "Name the capital of France.",
                    "correct_answer": "Paris",
                    "explanation": "...",
                }
            ]
        }
    )
    assert len(parse_generated_quiz(raw)) == 1


def test_drops_short_answer_question_with_blank_answer():
    raw = json.dumps(
        {
            "questions": [
                {
                    "question_type": "short_answer",
                    "prompt": "Name the capital of France.",
                    "correct_answer": "   ",
                    "explanation": "...",
                }
            ]
        }
    )
    assert parse_generated_quiz(raw) == []


def test_rejects_unknown_question_type():
    raw = json.dumps(
        {"questions": [{"question_type": "essay", "prompt": "...", "correct_answer": "...", "explanation": "..."}]}
    )
    with pytest.raises(ValidationError):
        parse_generated_quiz(raw)


def test_raises_on_invalid_json():
    with pytest.raises(json.JSONDecodeError):
        parse_generated_quiz("not json at all")


def test_filters_partial_batch_keeping_valid_questions():
    raw = json.dumps(
        {
            "questions": [
                {
                    "question_type": "multiple_choice",
                    "prompt": "Q1",
                    "options": ["a", "b"],
                    "correct_answer": "a",
                    "explanation": "e",
                },
                {
                    "question_type": "multiple_choice",
                    "prompt": "Q2",
                    "options": ["a", "b"],
                    "correct_answer": "z",
                    "explanation": "e",
                },
            ]
        }
    )
    questions = parse_generated_quiz(raw)
    assert len(questions) == 1
    assert questions[0].prompt == "Q1"