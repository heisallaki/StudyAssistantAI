import httpx

from app.core.config import get_settings
from app.storage.base import StorageBackend, StorageError

settings = get_settings()


class SupabaseStorageBackend(StorageBackend):
    def __init__(
        self,
        supabase_url: str | None = None,
        service_role_key: str | None = None,
        bucket: str | None = None,
    ):
        self.supabase_url = (supabase_url or settings.SUPABASE_URL or "").rstrip("/")
        self.service_role_key = service_role_key or settings.SUPABASE_SERVICE_ROLE_KEY
        self.bucket = bucket or settings.SUPABASE_STORAGE_BUCKET

        if not self.supabase_url or not self.service_role_key:
            raise StorageError(
                "Supabase storage is not configured. Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY."
            )

    def _headers(self, content_type: str | None = None) -> dict[str, str]:
        headers = {
            "apikey": self.service_role_key,
            "Authorization": f"Bearer {self.service_role_key}",
        }
        if content_type:
            headers["Content-Type"] = content_type
        return headers

    def _object_url(self, key: str) -> str:
        return f"{self.supabase_url}/storage/v1/object/{self.bucket}/{key}"

    def save(self, key: str, content: bytes) -> str:
        try:
            response = httpx.post(
                self._object_url(key),
                headers=self._headers("application/octet-stream"),
                content=content,
                timeout=60.0,
            )
            response.raise_for_status()
        except httpx.HTTPError as error:
            raise StorageError(f"Could not upload file to Supabase storage: {error}") from error
        return key

    def read(self, reference: str) -> bytes:
        try:
            response = httpx.get(self._object_url(reference), headers=self._headers(), timeout=60.0)
            response.raise_for_status()
        except httpx.HTTPError as error:
            raise StorageError(f"Could not read file from Supabase storage: {error}") from error
        return response.content

    def delete(self, reference: str) -> None:
        try:
            response = httpx.delete(self._object_url(reference), headers=self._headers(), timeout=60.0)
            if response.status_code not in (200, 404):
                response.raise_for_status()
        except httpx.HTTPError as error:
            raise StorageError(f"Could not delete file from Supabase storage: {error}") from error