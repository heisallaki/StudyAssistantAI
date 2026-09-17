from pathlib import Path

from app.core.config import get_settings
from app.storage.base import StorageBackend, StorageError

settings = get_settings()


class LocalStorageBackend(StorageBackend):
    def __init__(self, base_dir: str | None = None):
        self.base_dir = Path(base_dir or settings.UPLOAD_DIR)

    def _resolve(self, key: str) -> Path:
        self.base_dir.mkdir(parents=True, exist_ok=True)
        return self.base_dir / key

    def save(self, key: str, content: bytes) -> str:
        path = self._resolve(key)
        path.write_bytes(content)
        return str(path)

    def read(self, reference: str) -> bytes:
        path = Path(reference)
        try:
            return path.read_bytes()
        except OSError as error:
            raise StorageError(f"Could not read file at {reference}") from error

    def delete(self, reference: str) -> None:
        path = Path(reference)
        path.unlink(missing_ok=True)