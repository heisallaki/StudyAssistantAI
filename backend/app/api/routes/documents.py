import uuid

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.ai.providers.embedding_base import EmbeddingProvider
from app.api.deps import get_current_user, get_embedding_provider
from app.core.exceptions import (
    DocumentNotFoundError,
    FileTooLargeError,
    NoTextToIndexError,
    SubjectNotFoundError,
    UnsupportedFileTypeError,
)
from app.db.session import get_db
from app.models.user import User
from app.schemas.document import DocumentDetail, DocumentRead, DocumentUpdate
from app.services import document_service

router = APIRouter()


@router.get("", response_model=list[DocumentRead])
def list_documents(
    subject_id: uuid.UUID | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return document_service.list_documents(db, current_user.id, subject_id)


@router.post("", response_model=DocumentDetail, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    subject_id: uuid.UUID | None = Form(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    embedding_provider: EmbeddingProvider = Depends(get_embedding_provider),
):
    if not file.filename:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="A file is required")

    file_bytes = await file.read()

    try:
        return await document_service.upload_document(
            db,
            embedding_provider,
            current_user.id,
            file.filename,
            file.content_type or "application/octet-stream",
            file_bytes,
            subject_id,
        )
    except UnsupportedFileTypeError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Unsupported file type. Allowed types: PDF, TXT, MD",
        )
    except FileTooLargeError:
        raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            detail="File is too large",
        )
    except SubjectNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subject not found")


@router.get("/{document_id}", response_model=DocumentDetail)
def get_document(
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        return document_service.get_document(db, document_id, current_user.id)
    except DocumentNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")


@router.put("/{document_id}", response_model=DocumentRead)
def update_document(
    document_id: uuid.UUID,
    data: DocumentUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        return document_service.update_document(db, document_id, current_user.id, data)
    except DocumentNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    except SubjectNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subject not found")


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        document_service.delete_document(db, document_id, current_user.id)
    except DocumentNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")


@router.post("/{document_id}/reindex", response_model=DocumentDetail)
async def reindex_document(
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    embedding_provider: EmbeddingProvider = Depends(get_embedding_provider),
):
    try:
        return await document_service.reindex_document(db, embedding_provider, document_id, current_user.id)
    except DocumentNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    except NoTextToIndexError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="This document has no extracted text to index",
        )


@router.get("/{document_id}/download")
def download_document(
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        document = document_service.get_document(db, document_id, current_user.id)
    except DocumentNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    return FileResponse(
        path=document.storage_path,
        media_type=document.content_type,
        filename=document.original_filename,
    )