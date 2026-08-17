import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DocumentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    subject_id: uuid.UUID | None
    original_filename: str
    content_type: str
    file_size_bytes: int
    processing_status: str
    processing_error: str | None
    created_at: datetime
    updated_at: datetime


class DocumentDetail(DocumentRead):
    extracted_text: str | None


class DocumentUpdate(BaseModel):
    subject_id: uuid.UUID | None = None