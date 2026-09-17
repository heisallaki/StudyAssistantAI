import asyncio
import logging

from app.ai.providers.embedding_base import EmbeddingProvider, EmbeddingProviderError
from app.core.config import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()

_model = None
_model_lock = asyncio.Lock()


def _load_model(model_name: str, cache_dir: str):
    from fastembed import TextEmbedding

    return TextEmbedding(model_name=model_name, cache_dir=cache_dir)


def _encode(model, texts: list[str]) -> list[list[float]]:
    return [embedding.tolist() for embedding in model.embed(texts)]


class OnnxEmbeddingProvider(EmbeddingProvider):
    def __init__(self, model_name: str | None = None, cache_dir: str | None = None):
        self.model_name = model_name or settings.EMBEDDING_MODEL_NAME
        self.cache_dir = cache_dir or settings.EMBEDDING_CACHE_DIR

    async def _get_model(self):
        global _model
        if _model is None:
            async with _model_lock:
                if _model is None:
                    try:
                        _model = await asyncio.to_thread(_load_model, self.model_name, self.cache_dir)
                    except Exception as error:
                        logger.error("Failed to load local embedding model %s: %s", self.model_name, error)
                        raise EmbeddingProviderError(
                            "The local embedding model could not be loaded."
                        ) from error
        return _model

    async def embed(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []

        model = await self._get_model()
        try:
            return await asyncio.to_thread(_encode, model, texts)
        except Exception as error:
            logger.error("Local embedding generation failed: %s", error)
            raise EmbeddingProviderError("The local embedding model could not process this request.") from error