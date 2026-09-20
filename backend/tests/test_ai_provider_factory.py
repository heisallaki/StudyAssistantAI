import asyncio

import pytest

from app.ai.providers import factory
from app.ai.providers.base import AIProvider, AIProviderError
from app.ai.providers.embedding_base import EmbeddingProvider
from app.ai.providers.fallback_provider import FallbackAIProvider
from app.ai.providers.gemini_provider import GeminiProvider
from app.ai.providers.groq_provider import GroqProvider
from app.ai.providers.ollama_embedding_provider import OllamaEmbeddingProvider
from app.ai.providers.ollama_provider import OllamaProvider
from app.ai.providers.onnx_embedding_provider import OnnxEmbeddingProvider


class FakeAIProvider(AIProvider):
    def __init__(self, reply: str = "ok", should_fail: bool = False):
        self.reply = reply
        self.should_fail = should_fail
        self.was_called = False

    async def generate_reply(self, messages, response_format=None):
        self.was_called = True
        if self.should_fail:
            raise AIProviderError("simulated failure")
        return self.reply


def test_build_ai_provider_defaults_to_ollama(monkeypatch):
    monkeypatch.setattr(factory.settings, "AI_PROVIDER", "ollama")
    monkeypatch.setattr(factory.settings, "AI_FALLBACK_PROVIDER", None)
    provider = factory.build_ai_provider()
    assert isinstance(provider, OllamaProvider)


def test_build_ai_provider_returns_gemini(monkeypatch):
    monkeypatch.setattr(factory.settings, "AI_PROVIDER", "gemini")
    monkeypatch.setattr(factory.settings, "AI_FALLBACK_PROVIDER", None)
    provider = factory.build_ai_provider()
    assert isinstance(provider, GeminiProvider)


def test_build_ai_provider_returns_groq(monkeypatch):
    monkeypatch.setattr(factory.settings, "AI_PROVIDER", "groq")
    monkeypatch.setattr(factory.settings, "AI_FALLBACK_PROVIDER", None)
    provider = factory.build_ai_provider()
    assert isinstance(provider, GroqProvider)


def test_build_ai_provider_wraps_fallback_when_configured(monkeypatch):
    monkeypatch.setattr(factory.settings, "AI_PROVIDER", "gemini")
    monkeypatch.setattr(factory.settings, "AI_FALLBACK_PROVIDER", "groq")
    provider = factory.build_ai_provider()
    assert isinstance(provider, FallbackAIProvider)
    assert isinstance(provider.primary, GeminiProvider)
    assert isinstance(provider.fallback, GroqProvider)


def test_build_ai_provider_ignores_fallback_matching_primary(monkeypatch):
    monkeypatch.setattr(factory.settings, "AI_PROVIDER", "gemini")
    monkeypatch.setattr(factory.settings, "AI_FALLBACK_PROVIDER", "gemini")
    provider = factory.build_ai_provider()
    assert isinstance(provider, GeminiProvider)


def test_build_ai_provider_rejects_unknown_provider(monkeypatch):
    monkeypatch.setattr(factory.settings, "AI_PROVIDER", "not-a-real-provider")
    with pytest.raises(ValueError):
        factory.build_ai_provider()


def test_build_embedding_provider_defaults_to_ollama(monkeypatch):
    monkeypatch.setattr(factory.settings, "EMBEDDING_PROVIDER", "ollama")
    provider = factory.build_embedding_provider()
    assert isinstance(provider, OllamaEmbeddingProvider)


def test_build_embedding_provider_returns_onnx(monkeypatch):
    monkeypatch.setattr(factory.settings, "EMBEDDING_PROVIDER", "onnx")
    provider = factory.build_embedding_provider()
    assert isinstance(provider, OnnxEmbeddingProvider)
    assert isinstance(provider, EmbeddingProvider)


def test_build_embedding_provider_rejects_unknown_provider(monkeypatch):
    monkeypatch.setattr(factory.settings, "EMBEDDING_PROVIDER", "not-a-real-provider")
    with pytest.raises(ValueError):
        factory.build_embedding_provider()


def test_fallback_provider_uses_primary_when_it_succeeds():
    primary = FakeAIProvider(reply="from primary")
    fallback = FakeAIProvider(reply="from fallback")
    provider = FallbackAIProvider(primary, fallback)

    reply = asyncio.run(provider.generate_reply([{"role": "user", "content": "hi"}]))

    assert reply == "from primary"
    assert fallback.was_called is False


def test_fallback_provider_falls_back_when_primary_fails():
    primary = FakeAIProvider(should_fail=True)
    fallback = FakeAIProvider(reply="from fallback")
    provider = FallbackAIProvider(primary, fallback)

    reply = asyncio.run(provider.generate_reply([{"role": "user", "content": "hi"}]))

    assert reply == "from fallback"


def test_fallback_provider_raises_when_both_fail():
    primary = FakeAIProvider(should_fail=True)
    fallback = FakeAIProvider(should_fail=True)
    provider = FallbackAIProvider(primary, fallback)

    with pytest.raises(AIProviderError):
        asyncio.run(provider.generate_reply([{"role": "user", "content": "hi"}]))