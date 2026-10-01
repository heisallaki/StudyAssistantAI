import logging

from app.core.config import Settings


def _build_settings(**overrides):
    return Settings(
        DATABASE_URL="postgresql+psycopg2://user:pass@localhost:5432/db",
        JWT_SECRET_KEY="test-secret",
        **overrides,
    )


def test_development_defaults_to_ollama():
    settings = _build_settings(ENVIRONMENT="development")
    assert settings.AI_PROVIDER == "ollama"
    assert settings.is_local_development is True


def test_development_allows_explicit_ollama():
    settings = _build_settings(ENVIRONMENT="development", AI_PROVIDER="ollama")
    assert settings.AI_PROVIDER == "ollama"


def test_production_never_fails_to_construct_with_missing_ai_provider():
    settings = _build_settings(ENVIRONMENT="production")
    assert settings.AI_PROVIDER == "ollama"
    assert settings.is_local_development is False


def test_production_never_fails_to_construct_with_explicit_ollama():
    settings = _build_settings(ENVIRONMENT="production", AI_PROVIDER="ollama")
    assert settings.AI_PROVIDER == "ollama"


def test_production_never_fails_to_construct_with_ollama_fallback():
    settings = _build_settings(ENVIRONMENT="production", AI_PROVIDER="gemini", AI_FALLBACK_PROVIDER="ollama")
    assert settings.AI_FALLBACK_PROVIDER == "ollama"


def test_production_logs_a_warning_for_ollama_as_primary(caplog):
    with caplog.at_level(logging.WARNING, logger="app.core.config"):
        _build_settings(ENVIRONMENT="production", AI_PROVIDER="ollama")
    assert any("AI_PROVIDER is set to 'ollama'" in record.message for record in caplog.records)


def test_production_logs_a_warning_for_ollama_as_fallback(caplog):
    with caplog.at_level(logging.WARNING, logger="app.core.config"):
        _build_settings(ENVIRONMENT="production", AI_PROVIDER="gemini", AI_FALLBACK_PROVIDER="ollama")
    assert any("AI_FALLBACK_PROVIDER is set to 'ollama'" in record.message for record in caplog.records)


def test_development_does_not_log_a_warning(caplog):
    with caplog.at_level(logging.WARNING, logger="app.core.config"):
        _build_settings(ENVIRONMENT="development", AI_PROVIDER="ollama")
    assert caplog.records == []


def test_production_accepts_gemini_primary_with_groq_fallback():
    settings = _build_settings(ENVIRONMENT="production", AI_PROVIDER="gemini", AI_FALLBACK_PROVIDER="groq")
    assert settings.AI_PROVIDER == "gemini"
    assert settings.AI_FALLBACK_PROVIDER == "groq"
    assert settings.is_local_development is False


def test_production_accepts_groq_primary_with_no_fallback():
    settings = _build_settings(ENVIRONMENT="production", AI_PROVIDER="groq")
    assert settings.AI_PROVIDER == "groq"
    assert settings.AI_FALLBACK_PROVIDER is None


def test_staging_environment_is_treated_as_non_development():
    settings = _build_settings(ENVIRONMENT="staging", AI_PROVIDER="ollama")
    assert settings.is_local_development is False