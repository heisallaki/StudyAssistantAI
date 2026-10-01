import logging
from functools import lru_cache
from typing import List

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)

VALID_AI_PROVIDERS = frozenset({"ollama", "gemini", "groq"})
LOCAL_ONLY_AI_PROVIDERS = frozenset({"ollama"})


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    PROJECT_NAME: str = "StudyAssistant AI"
    API_V1_PREFIX: str = "/api/v1"
    ENVIRONMENT: str = "development"
    DATABASE_URL: str
    JWT_SECRET_KEY: str
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.2:3b"
    OLLAMA_EMBEDDING_MODEL: str = "all-minilm"
    AI_PROVIDER: str = "ollama"
    AI_FALLBACK_PROVIDER: str | None = None
    GEMINI_API_KEY: str | None = None
    GEMINI_MODEL: str = "gemini-2.5-flash"
    GEMINI_BASE_URL: str = "https://generativelanguage.googleapis.com/v1beta"
    GROQ_API_KEY: str | None = None
    GROQ_MODEL: str = "llama-3.3-70b-versatile"
    GROQ_BASE_URL: str = "https://api.groq.com/openai/v1"
    EMBEDDING_PROVIDER: str = "ollama"
    EMBEDDING_MODEL_NAME: str = "sentence-transformers/all-MiniLM-L6-v2"
    EMBEDDING_CACHE_DIR: str = "/app/.fastembed_cache"
    STORAGE_BACKEND: str = "local"
    SUPABASE_URL: str | None = None
    SUPABASE_SERVICE_ROLE_KEY: str | None = None
    SUPABASE_STORAGE_BUCKET: str = "documents"
    CORS_ORIGINS: str = "http://localhost:5173"
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE_MB: int = 20
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24
    RATE_LIMIT_ENABLED: bool = True
    LOGIN_RATE_LIMIT: str = "10/minute"
    REGISTER_RATE_LIMIT: str = "5/minute"
    FAILED_LOGIN_LOCKOUT_THRESHOLD: int = 5
    FAILED_LOGIN_LOCKOUT_MINUTES: int = 15
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_POOL_RECYCLE_SECONDS: int = 1800
    EMAIL_VERIFICATION_REQUIRED: bool = True
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: str | None = None
    SMTP_PASSWORD: str | None = None
    SMTP_FROM_EMAIL: str | None = None
    SMTP_FROM_NAME: str = "StudyAssistant AI"
    OTP_LENGTH: int = 6
    OTP_EXPIRE_MINUTES: int = 10
    OTP_MAX_ATTEMPTS: int = 5
    OTP_REQUEST_RATE_LIMIT: str = "5/hour"

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    @property
    def is_local_development(self) -> bool:
        return self.ENVIRONMENT == "development"

    @model_validator(mode="after")
    def _warn_on_risky_ai_provider_configuration(self) -> "Settings":
        if self.is_local_development:
            return self

        provider = self.AI_PROVIDER.strip().lower() if self.AI_PROVIDER else ""
        if provider in LOCAL_ONLY_AI_PROVIDERS:
            logger.warning(
                "AI_PROVIDER is set to 'ollama' in the '%s' environment. Ollama is for local "
                "development only; AI features will refuse to use it and will report as "
                "unavailable until AI_PROVIDER is set to 'gemini' or 'groq'.",
                self.ENVIRONMENT,
            )

        fallback = self.AI_FALLBACK_PROVIDER.strip().lower() if self.AI_FALLBACK_PROVIDER else None
        if fallback in LOCAL_ONLY_AI_PROVIDERS:
            logger.warning(
                "AI_FALLBACK_PROVIDER is set to 'ollama' in the '%s' environment. Ollama is for "
                "local development only and will not be used as a fallback here.",
                self.ENVIRONMENT,
            )

        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()