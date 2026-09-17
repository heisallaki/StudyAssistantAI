from app.ai.providers.base import AIProvider
from app.ai.providers.embedding_base import EmbeddingProvider
from app.ai.providers.fallback_provider import FallbackAIProvider
from app.ai.providers.gemini_provider import GeminiProvider
from app.ai.providers.groq_provider import GroqProvider
from app.ai.providers.ollama_embedding_provider import OllamaEmbeddingProvider
from app.ai.providers.ollama_provider import OllamaProvider
from app.ai.providers.onnx_embedding_provider import OnnxEmbeddingProvider
from app.core.config import get_settings

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


def build_ai_provider() -> AIProvider:
    provider_name = settings.AI_PROVIDER.lower()
    builder = _AI_PROVIDER_BUILDERS.get(provider_name)
    if builder is None:
        raise ValueError(f"Unknown AI_PROVIDER '{settings.AI_PROVIDER}'")

    primary = builder()

    fallback_name = settings.AI_FALLBACK_PROVIDER
    if fallback_name and fallback_name.lower() != provider_name:
        fallback_builder = _AI_PROVIDER_BUILDERS.get(fallback_name.lower())
        if fallback_builder is None:
            raise ValueError(f"Unknown AI_FALLBACK_PROVIDER '{fallback_name}'")
        return FallbackAIProvider(primary, fallback_builder())

    return primary


def build_embedding_provider() -> EmbeddingProvider:
    provider_name = settings.EMBEDDING_PROVIDER.lower()
    builder = _EMBEDDING_PROVIDER_BUILDERS.get(provider_name)
    if builder is None:
        raise ValueError(f"Unknown EMBEDDING_PROVIDER '{settings.EMBEDDING_PROVIDER}'")
    return builder()