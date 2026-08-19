from abc import ABC, abstractmethod


class AIProviderError(Exception):
    pass


class AIProvider(ABC):
    @abstractmethod
    async def generate_reply(self, messages: list[dict[str, str]]) -> str:
        raise NotImplementedError