from app.services.quiz_grading import grade_answer


def test_multiple_choice_exact_match_is_correct():
    assert grade_answer("multiple_choice", "Structured Query Language", "Structured Query Language") is True


def test_multiple_choice_wrong_option_is_incorrect():
    assert grade_answer("multiple_choice", "Simple Query Language", "Structured Query Language") is False


def test_multiple_choice_ignores_case_and_surrounding_whitespace():
    assert grade_answer("multiple_choice", "  structured query language  ", "Structured Query Language") is True


def test_true_false_matches_regardless_of_case():
    assert grade_answer("true_false", "True", "true") is True
    assert grade_answer("true_false", "false", "true") is False


def test_short_answer_normalizes_internal_whitespace():
    assert grade_answer("short_answer", "  Paris   France ", "Paris France") is True


def test_short_answer_wrong_text_is_incorrect():
    assert grade_answer("short_answer", "London", "Paris") is False


def test_blank_submission_is_always_incorrect():
    assert grade_answer("multiple_choice", "", "4") is False
    assert grade_answer("short_answer", "   ", "Paris") is False


def test_unknown_question_type_is_incorrect():
    assert grade_answer("essay", "anything", "anything") is False