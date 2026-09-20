import logging

import httpx

from app.ai.providers.base import AIProvider, AIProviderError
from app.core.config import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()


def _to_gemini_contents(messages: list[dict[str, str]]) -> tuple[str | None, list[dict]]:
    system_instruction: str | None = None
    contents: list[dict] = []

    for message in messages:
        role = message.get("role")
        content = message.get("content", "")

        if role == "system":
            system_instruction = f"{system_instruction}\n\n{content}" if system_instruction else content
            continue

        gemini_role = "model" if role == "assistant" else "user"
        contents.append({"role": gemini_role, "parts": [{"text": content}]})

    return system_instruction, contents


class GeminiProvider(AIProvider):
    def __init__(self, api_key: str | None = None, model: str | None = None, base_url: str | None = None):
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.model = model or settings.GEMINI_MODEL
        self.base_url = (base_url or settings.GEMINI_BASE_URL).rstrip("/")

    async def generate_reply(self, messages: list[dict[str, str]], response_format: str | None = None) -> str:
        if not self.api_key:
            raise AIProviderError("Gemini is not configured. Set GEMINI_API_KEY.")

        system_instruction, contents = _to_gemini_contents(messages)

        payload: dict = {"contents": contents}
        if system_instruction:
            payload["systemInstruction"] = {"parts": [{"text": system_instruction}]}
        if response_format == "json":
            payload["generationConfig"] = {"responseMimeType": "application/json"}

        url = f"{self.base_url}/models/{self.model}:generateContent"

        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    url,
                    params={"key": self.api_key},
                    json=payload,
                )
                response.raise_for_status()
        except httpx.ConnectError as error:
            logger.error("Could not connect to Gemini API: %s", error)
            raise AIProviderError("Could not reach the Gemini API. Please try again shortly.") from error
        except httpx.TimeoutException as error:
            logger.error("Gemini request timed out: %s", error)
            raise AIProviderError("The AI model took too long to respond. Please try again.") from error
        except httpx.HTTPStatusError as error:
            status_code = error.response.status_code
            logger.error("Gemini returned an error status %s: %s", status_code, error.response.text)
            if status_code == 429:
                raise AIProviderError(
                    "The Gemini free-tier rate limit was reached. Please wait a moment and try again."
                ) from error
            raise AIProviderError("The Gemini API could not process this request.") from error

        data = response.json()
        candidates = data.get("candidates") or []
        if not candidates:
            raise AIProviderError("The AI model returned an empty response.")

        parts = candidates[0].get("content", {}).get("parts", [])
        text = "".join(part.get("text", "") for part in parts)
        if not text:
            raise AIProviderError("The AI model returned an empty response.")
        return text