from sqlalchemy.orm import Session

from app.ai.providers.embedding_base import EmbeddingProvider, EmbeddingProviderError
from app.models.document import Document
from app.repositories import document_chunk_repository
from app.services.document_chunking import chunk_text


async def index_document(db: Session, embedding_provider: EmbeddingProvider, document: Document) -> None:
    if not document.extracted_text:
        document.indexing_status = "not_applicable"
        document.indexing_error = None
        db.add(document)
        db.commit()
        return

    chunks = chunk_text(document.extracted_text)
    if not chunks:
        document.indexing_status = "not_applicable"
        document.indexing_error = None
        db.add(document)
        db.commit()
        return

    try:
        embeddings = await embedding_provider.embed(chunks)
    except EmbeddingProviderError as error:
        document.indexing_status = "failed"
        document.indexing_error = str(error)
        db.add(document)
        db.commit()
        return

    document_chunk_repository.replace_chunks(db, document.id, chunks, embeddings)
    document.indexing_status = "indexed"
    document.indexing_error = None
    db.add(document)
    db.commit()