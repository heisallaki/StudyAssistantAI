import logging

import httpx

from app.ai.providers.base import AIProvider, AIProviderError
from app.core.config import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()


class GroqProvider(AIProvider):
    def __init__(self, api_key: str | None = None, model: str | None = None, base_url: str | None = None):
        self.api_key = api_key or settings.GROQ_API_KEY
        self.model = model or settings.GROQ_MODEL
        self.base_url = (base_url or settings.GROQ_BASE_URL).rstrip("/")

    async def generate_reply(self, messages: list[dict[str, str]], response_format: str | None = None) -> str:
        if not self.api_key:
            raise AIProviderError("Groq is not configured. Set GROQ_API_KEY.")

        payload: dict = {"model": self.model, "messages": messages}
        if response_format == "json":
            payload["response_format"] = {"type": "json_object"}

        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    json=payload,
                )
                response.raise_for_status()
        except httpx.ConnectError as error:
            logger.error("Could not connect to Groq API: %s", error)
            raise AIProviderError("Could not reach the Groq API. Please try again shortly.") from error
        except httpx.TimeoutException as error:
            logger.error("Groq request timed out: %s", error)
            raise AIProviderError("The AI model took too long to respond. Please try again.") from error
        except httpx.HTTPStatusError as error:
            status_code = error.response.status_code
            logger.error("Groq returned an error status %s: %s", status_code, error.response.text)
            if status_code == 429:
                raise AIProviderError(
                    "The Groq free-tier rate limit was reached. Please wait a moment and try again."
                ) from error
            raise AIProviderError("The Groq API could not process this request.") from error

        data = response.json()
        choices = data.get("choices") or []
        if not choices:
            raise AIProviderError("The AI model returned an empty response.")

        content = choices[0].get("message", {}).get("content")
        if not content:
            raise AIProviderError("The AI model returned an empty response.")
        return content