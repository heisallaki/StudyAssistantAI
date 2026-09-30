import pytest
from pydantic import ValidationError

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


def test_production_rejects_missing_ai_provider_defaulting_to_ollama():
    with pytest.raises(ValidationError, match="AI_PROVIDER cannot be 'ollama'"):
        _build_settings(ENVIRONMENT="production")


def test_production_rejects_explicit_ollama():
    with pytest.raises(ValidationError, match="AI_PROVIDER cannot be 'ollama'"):
        _build_settings(ENVIRONMENT="production", AI_PROVIDER="ollama")


def test_production_rejects_ollama_fallback():
    with pytest.raises(ValidationError, match="AI_FALLBACK_PROVIDER cannot be 'ollama'"):
        _build_settings(ENVIRONMENT="production", AI_PROVIDER="gemini", AI_FALLBACK_PROVIDER="ollama")


def test_production_accepts_gemini_primary_with_groq_fallback():
    settings = _build_settings(ENVIRONMENT="production", AI_PROVIDER="gemini", AI_FALLBACK_PROVIDER="groq")
    assert settings.AI_PROVIDER == "gemini"
    assert settings.AI_FALLBACK_PROVIDER == "groq"
    assert settings.is_local_development is False


def test_production_accepts_groq_primary_with_no_fallback():
    settings = _build_settings(ENVIRONMENT="production", AI_PROVIDER="groq")
    assert settings.AI_PROVIDER == "groq"
    assert settings.AI_FALLBACK_PROVIDER is None


def test_staging_environment_also_rejects_ollama():
    with pytest.raises(ValidationError, match="AI_PROVIDER cannot be 'ollama'"):
        _build_settings(ENVIRONMENT="staging", AI_PROVIDER="ollama")


def test_rejects_unknown_ai_provider_name():
    with pytest.raises(ValidationError, match="AI_PROVIDER must be one of"):
        _build_settings(ENVIRONMENT="development", AI_PROVIDER="chatgpt")


def test_rejects_unknown_ai_fallback_provider_name():
    with pytest.raises(ValidationError, match="AI_FALLBACK_PROVIDER must be one of"):
        _build_settings(ENVIRONMENT="production", AI_PROVIDER="gemini", AI_FALLBACK_PROVIDER="chatgpt")


def test_provider_names_are_case_insensitive():
    settings = _build_settings(ENVIRONMENT="production", AI_PROVIDER="Gemini", AI_FALLBACK_PROVIDER="GROQ")
    assert settings.AI_PROVIDER == "Gemini"
    assert settings.AI_FALLBACK_PROVIDER == "GROQ"