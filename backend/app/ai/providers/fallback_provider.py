import logging

from app.ai.providers.base import AIProvider, AIProviderError

logger = logging.getLogger(__name__)


class FallbackAIProvider(AIProvider):
    def __init__(self, primary: AIProvider, fallback: AIProvider):
        self.primary = primary
        self.fallback = fallback

    async def generate_reply(self, messages: list[dict[str, str]], response_format: str | None = None) -> str:
        try:
            return await self.primary.generate_reply(messages, response_format)
        except AIProviderError as primary_error:
            logger.warning(
                "Primary AI provider (%s) failed, falling back to %s: %s",
                type(self.primary).__name__,
                type(self.fallback).__name__,
                primary_error,
            )
            try:
                return await self.fallback.generate_reply(messages, response_format)
            except AIProviderError as fallback_error:
                logger.error(
                    "Fallback AI provider (%s) also failed: %s",
                    type(self.fallback).__name__,
                    fallback_error,
                )
                raise fallback_error