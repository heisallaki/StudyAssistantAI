from unittest.mock import MagicMock, patch

import httpx
import pytest

from app.storage.base import StorageError
from app.storage.local_storage import LocalStorageBackend
from app.storage.supabase_storage import SupabaseStorageBackend


def test_local_storage_save_and_read_roundtrip(tmp_path):
    backend = LocalStorageBackend(base_dir=str(tmp_path))

    reference = backend.save("notes.txt", b"hello world")
    content = backend.read(reference)

    assert content == b"hello world"


def test_local_storage_delete_removes_file(tmp_path):
    backend = LocalStorageBackend(base_dir=str(tmp_path))
    reference = backend.save("notes.txt", b"hello world")

    backend.delete(reference)

    with pytest.raises(StorageError):
        backend.read(reference)


def test_local_storage_delete_is_idempotent(tmp_path):
    backend = LocalStorageBackend(base_dir=str(tmp_path))
    backend.delete("does-not-exist.txt")


def test_local_storage_read_missing_file_raises_storage_error(tmp_path):
    backend = LocalStorageBackend(base_dir=str(tmp_path))
    with pytest.raises(StorageError):
        backend.read(str(tmp_path / "missing.txt"))


def _supabase_backend():
    return SupabaseStorageBackend(
        supabase_url="https://example.supabase.co",
        service_role_key="test-service-role-key",
        bucket="documents",
    )


def test_supabase_storage_requires_configuration():
    with pytest.raises(StorageError):
        SupabaseStorageBackend(supabase_url=None, service_role_key=None)


def test_supabase_storage_save_posts_to_object_endpoint():
    backend = _supabase_backend()
    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()

    with patch("app.storage.supabase_storage.httpx.post", return_value=mock_response) as mock_post:
        key = backend.save("abc123.pdf", b"file bytes")

    assert key == "abc123.pdf"
    mock_post.assert_called_once()
    called_url = mock_post.call_args.args[0]
    assert called_url == "https://example.supabase.co/storage/v1/object/documents/abc123.pdf"


def test_supabase_storage_read_returns_bytes():
    backend = _supabase_backend()
    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    mock_response.content = b"file bytes"

    with patch("app.storage.supabase_storage.httpx.get", return_value=mock_response):
        content = backend.read("abc123.pdf")

    assert content == b"file bytes"


def test_supabase_storage_delete_ignores_missing_object():
    backend = _supabase_backend()
    mock_response = MagicMock()
    mock_response.status_code = 404

    with patch("app.storage.supabase_storage.httpx.delete", return_value=mock_response):
        backend.delete("missing.pdf")


def test_supabase_storage_save_wraps_connection_errors():
    backend = _supabase_backend()

    with patch("app.storage.supabase_storage.httpx.post", side_effect=httpx.ConnectError("boom")):
        with pytest.raises(StorageError):
            backend.save("abc123.pdf", b"file bytes")


def test_supabase_storage_read_wraps_http_status_errors():
    backend = _supabase_backend()
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "not found", request=MagicMock(), response=MagicMock(status_code=404)
    )

    with patch("app.storage.supabase_storage.httpx.get", return_value=mock_response):
        with pytest.raises(StorageError):
            backend.read("missing.pdf")