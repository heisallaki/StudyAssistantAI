import logging

import httpx2

from app.ai.providers.embedding_base import EmbeddingProvider, EmbeddingProviderError
from app.core.config import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()


class OllamaEmbeddingProvider(EmbeddingProvider):
    def __init__(self, base_url: str | None = None, model: str | None = None):
        self.base_url = (base_url or settings.OLLAMA_BASE_URL).rstrip("/")
        self.model = model or settings.OLLAMA_EMBEDDING_MODEL

    async def embed(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        try:
            async with httpx2.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    f"{self.base_url}/api/embed",
                    json={"model": self.model, "input": texts},
                )
                response.raise_for_status()
        except httpx2.ConnectError as error:
            logger.error("Could not connect to Ollama for embeddings at %s: %s", self.base_url, error)
            raise EmbeddingProviderError(
                "Could not reach the local embedding model. Make sure Ollama is installed and running."
            ) from error
        except httpx2.TimeoutException as error:
            logger.error("Ollama embedding request timed out: %s", error)
            raise EmbeddingProviderError("The embedding model took too long to respond.") from error
        except httpx2.HTTPStatusError as error:
            logger.error("Ollama returned an error status for embeddings: %s", error)
            raise EmbeddingProviderError(
                f"The embedding model could not process this request. Is '{self.model}' pulled in Ollama?"
            ) from error

        data = response.json()
        embeddings = data.get("embeddings")
        if not embeddings:
            raise EmbeddingProviderError("The embedding model returned no embeddings.")
        return embeddings