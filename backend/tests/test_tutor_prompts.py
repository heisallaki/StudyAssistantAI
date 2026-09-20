from app.ai.prompts.tutor_prompts import build_system_prompt


def test_beginner_prompt_avoids_jargon_instruction():
    prompt = build_system_prompt("beginner", "tutor", None)
    assert "first time" in prompt


def test_advanced_prompt_requests_rigor():
    prompt = build_system_prompt("advanced", "tutor", None)
    assert "rigorous" in prompt


def test_unknown_level_falls_back_to_intermediate():
    prompt = build_system_prompt("not-a-real-level", "tutor", None)
    assert "standard terminology" in prompt


def test_socratic_mode_instructs_guiding_questions():
    prompt = build_system_prompt("intermediate", "socratic", None)
    assert "guiding question" in prompt


def test_tutor_mode_instructs_direct_answers():
    prompt = build_system_prompt("intermediate", "tutor", None)
    assert "directly" in prompt


def test_subject_context_is_appended_when_present():
    prompt = build_system_prompt("intermediate", "tutor", "The student is currently studying the subject 'Databases'.")
    assert "Databases" in prompt


def test_no_subject_context_when_none():
    prompt = build_system_prompt("intermediate", "tutor", None)
    assert "studying the subject" not in prompt