import logging

import httpx2

from app.ai.providers.base import AIProvider, AIProviderError
from app.core.config import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()


class OllamaProvider(AIProvider):
    def __init__(self, base_url: str | None = None, model: str | None = None):
        self.base_url = (base_url or settings.OLLAMA_BASE_URL).rstrip("/")
        self.model = model or settings.OLLAMA_MODEL

    async def generate_reply(self, messages: list[dict[str, str]], response_format: str | None = None) -> str:
        payload: dict = {"model": self.model, "messages": messages, "stream": False}
        if response_format == "json":
            payload["format"] = "json"

        try:
            async with httpx2.AsyncClient(timeout=120.0) as client:
                response = await client.post(f"{self.base_url}/api/chat", json=payload)
                response.raise_for_status()
        except httpx2.ConnectError as error:
            logger.error("Could not connect to Ollama at %s: %s", self.base_url, error)
            raise AIProviderError(
                "Could not reach the local AI model. Make sure Ollama is installed and running."
            ) from error
        except httpx2.TimeoutException as error:
            logger.error("Ollama request timed out: %s", error)
            raise AIProviderError("The AI model took too long to respond. Please try again.") from error
        except httpx2.HTTPStatusError as error:
            logger.error("Ollama returned an error status: %s", error)
            raise AIProviderError(
                f"The AI model could not process this request. Is '{self.model}' pulled in Ollama?"
            ) from error

        data = response.json()
        content = data.get("message", {}).get("content")
        if not content:
            raise AIProviderError("The AI model returned an empty response.")
        return content