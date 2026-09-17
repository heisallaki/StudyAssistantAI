from abc import ABC, abstractmethod


class StorageError(Exception):
    pass


class StorageBackend(ABC):
    @abstractmethod
    def save(self, key: str, content: bytes) -> str:
        raise NotImplementedError

    @abstractmethod
    def read(self, reference: str) -> bytes:
        raise NotImplementedError

    @abstractmethod
    def delete(self, reference: str) -> None:
        raise NotImplementedError