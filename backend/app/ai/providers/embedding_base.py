from abc import ABC, abstractmethod


class EmbeddingProviderError(Exception):
    pass


class EmbeddingProvider(ABC):
    @abstractmethod
    async def embed(self, texts: list[str]) -> list[list[float]]:
        raise NotImplementedError