from app.ai.providers.base import AIProvider, AIProviderError
from app.ai.providers.embedding_base import EmbeddingProvider
from app.ai.providers.fallback_provider import FallbackAIProvider
from app.ai.providers.gemini_provider import GeminiProvider
from app.ai.providers.groq_provider import GroqProvider
from app.ai.providers.ollama_embedding_provider import OllamaEmbeddingProvider
from app.ai.providers.ollama_provider import OllamaProvider
from app.ai.providers.onnx_embedding_provider import OnnxEmbeddingProvider
from app.core.config import LOCAL_ONLY_AI_PROVIDERS, get_settings

settings = get_settings()

_AI_PROVIDER_BUILDERS = {
    "ollama": OllamaProvider,
    "gemini": GeminiProvider,
    "groq": GroqProvider,
}

_EMBEDDING_PROVIDER_BUILDERS = {
    "ollama": OllamaEmbeddingProvider,
    "onnx": OnnxEmbeddingProvider,
}


def _reject_local_only_provider_outside_development(provider_name: str, setting_name: str) -> None:
    if not settings.is_local_development and provider_name in LOCAL_ONLY_AI_PROVIDERS:
        raise AIProviderError(
            f"{setting_name} is set to 'ollama', which is for local development only and cannot "
            f"be used in the '{settings.ENVIRONMENT}' environment."
        )


def build_ai_provider() -> AIProvider:
    provider_name = settings.AI_PROVIDER.lower()
    builder = _AI_PROVIDER_BUILDERS.get(provider_name)
    if builder is None:
        raise ValueError(f"Unknown AI_PROVIDER '{settings.AI_PROVIDER}'")
    _reject_local_only_provider_outside_development(provider_name, "AI_PROVIDER")

    primary = builder()

    fallback_name = settings.AI_FALLBACK_PROVIDER
    if fallback_name and fallback_name.lower() != provider_name:
        fallback_name_normalized = fallback_name.lower()
        fallback_builder = _AI_PROVIDER_BUILDERS.get(fallback_name_normalized)
        if fallback_builder is None:
            raise ValueError(f"Unknown AI_FALLBACK_PROVIDER '{fallback_name}'")
        _reject_local_only_provider_outside_development(fallback_name_normalized, "AI_FALLBACK_PROVIDER")
        return FallbackAIProvider(primary, fallback_builder())

    return primary


def build_embedding_provider() -> EmbeddingProvider:
    provider_name = settings.EMBEDDING_PROVIDER.lower()
    builder = _EMBEDDING_PROVIDER_BUILDERS.get(provider_name)
    if builder is None:
        raise ValueError(f"Unknown EMBEDDING_PROVIDER '{settings.EMBEDDING_PROVIDER}'")
    return builder()