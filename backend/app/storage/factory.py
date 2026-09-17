from app.core.config import get_settings
from app.storage.base import StorageBackend
from app.storage.local_storage import LocalStorageBackend
from app.storage.supabase_storage import SupabaseStorageBackend

settings = get_settings()

_STORAGE_BACKEND_BUILDERS = {
    "local": LocalStorageBackend,
    "supabase": SupabaseStorageBackend,
}


def build_storage_backend() -> StorageBackend:
    backend_name = settings.STORAGE_BACKEND.lower()
    builder = _STORAGE_BACKEND_BUILDERS.get(backend_name)
    if builder is None:
        raise ValueError(f"Unknown STORAGE_BACKEND '{settings.STORAGE_BACKEND}'")
    return builder()