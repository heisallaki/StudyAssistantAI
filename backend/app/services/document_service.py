import logging
import uuid
from pathlib import Path

from sqlalchemy.orm import Session

from app.ai.providers.embedding_base import EmbeddingProvider
from app.core.config import get_settings
from app.core.exceptions import (
    DocumentNotFoundError,
    FileTooLargeError,
    NoTextToIndexError,
    SubjectNotFoundError,
    UnsupportedFileTypeError,
)
from app.models.document import Document
from app.repositories import document_repository, subject_repository
from app.schemas.document import DocumentUpdate
from app.services import document_indexing_service, document_processing

logger = logging.getLogger(__name__)

settings = get_settings()


def _upload_dir() -> Path:
    upload_path = Path(settings.UPLOAD_DIR)
    upload_path.mkdir(parents=True, exist_ok=True)
    return upload_path


def list_documents(db: Session, user_id: uuid.UUID, subject_id: uuid.UUID | None = None) -> list[Document]:
    return document_repository.list_for_user(db, user_id, subject_id)


def get_document(db: Session, document_id: uuid.UUID, user_id: uuid.UUID) -> Document:
    document = document_repository.get_by_id_for_user(db, document_id, user_id)
    if document is None:
        raise DocumentNotFoundError(document_id)
    return document


async def upload_document(
    db: Session,
    embedding_provider: EmbeddingProvider,
    user_id: uuid.UUID,
    original_filename: str,
    content_type: str,
    file_bytes: bytes,
    subject_id: uuid.UUID | None,
) -> Document:
    extension = document_processing.get_extension(original_filename)
    if extension not in document_processing.ALLOWED_EXTENSIONS:
        raise UnsupportedFileTypeError(extension)

    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if len(file_bytes) > max_bytes:
        raise FileTooLargeError(len(file_bytes))

    if subject_id is not None and subject_repository.get_by_id_for_user(db, subject_id, user_id) is None:
        raise SubjectNotFoundError(subject_id)

    document_id = uuid.uuid4()
    storage_path = _upload_dir() / f"{document_id}{extension}"
    storage_path.write_bytes(file_bytes)

    extracted_text, processing_error = document_processing.extract_text(file_bytes, extension)
    processing_status = "processed" if extracted_text is not None else "failed"

    document = Document(
        id=document_id,
        user_id=user_id,
        subject_id=subject_id,
        original_filename=original_filename,
        storage_path=str(storage_path),
        content_type=content_type,
        file_size_bytes=len(file_bytes),
        extracted_text=extracted_text,
        processing_status=processing_status,
        processing_error=processing_error,
        indexing_status="pending" if extracted_text is not None else "not_applicable",
    )
    document = document_repository.create(db, document)

    if extracted_text is not None:
        await document_indexing_service.index_document(db, embedding_provider, document)

    return document


async def reindex_document(
    db: Session, embedding_provider: EmbeddingProvider, document_id: uuid.UUID, user_id: uuid.UUID
) -> Document:
    document = get_document(db, document_id, user_id)
    if not document.extracted_text:
        raise NoTextToIndexError(document_id)
    await document_indexing_service.index_document(db, embedding_provider, document)
    db.refresh(document)
    return document


def update_document(db: Session, document_id: uuid.UUID, user_id: uuid.UUID, data: DocumentUpdate) -> Document:
    document = get_document(db, document_id, user_id)
    update_data = data.model_dump(exclude_unset=True)

    if "subject_id" in update_data and update_data["subject_id"] is not None:
        if subject_repository.get_by_id_for_user(db, update_data["subject_id"], user_id) is None:
            raise SubjectNotFoundError(update_data["subject_id"])

    return document_repository.update(db, document, update_data)


def delete_document(db: Session, document_id: uuid.UUID, user_id: uuid.UUID) -> None:
    document = get_document(db, document_id, user_id)
    storage_path = Path(document.storage_path)
    document_repository.delete(db, document)
    try:
        storage_path.unlink(missing_ok=True)
    except OSError as error:
        logger.warning("Failed to remove document file %s: %s", storage_path, error)