import uuid

from sqlalchemy.orm import Session

from app.models.document import Document
from app.models.document_chunk import DocumentChunk


def replace_chunks_for_document(
    db: Session, document_id: uuid.UUID, chunks: list[tuple[int, str, list[float]]]
) -> list[DocumentChunk]:
    db.query(DocumentChunk).filter(DocumentChunk.document_id == document_id).delete()

    created = []
    for chunk_index, content, embedding in chunks:
        chunk = DocumentChunk(
            document_id=document_id, chunk_index=chunk_index, content=content, embedding=embedding
        )
        db.add(chunk)
        created.append(chunk)

    db.commit()
    for chunk in created:
        db.refresh(chunk)
    return created


def search_similar_chunks(
    db: Session,
    user_id: uuid.UUID,
    query_embedding: list[float],
    limit: int = 6,
    max_distance: float = 0.7,
) -> list[tuple[str, str, float]]:
    results = (
        db.query(
            Document.original_filename,
            DocumentChunk.content,
            DocumentChunk.embedding.cosine_distance(query_embedding).label("distance"),
        )
        .join(Document, Document.id == DocumentChunk.document_id)
        .filter(Document.user_id == user_id)
        .order_by(DocumentChunk.embedding.cosine_distance(query_embedding))
        .limit(limit)
        .all()
    )

    return [(filename, content, distance) for filename, content, distance in results if distance <= max_distance]


def search_chunks_for_query(
    db: Session,
    user_id: uuid.UUID,
    query_embedding: list[float],
    subject_id: uuid.UUID | None = None,
    limit: int = 10,
    max_distance: float = 0.8,
) -> list[tuple[uuid.UUID, str, uuid.UUID | None, str, float]]:
    query = (
        db.query(
            Document.id,
            Document.original_filename,
            Document.subject_id,
            DocumentChunk.content,
            DocumentChunk.embedding.cosine_distance(query_embedding).label("distance"),
        )
        .join(Document, Document.id == DocumentChunk.document_id)
        .filter(Document.user_id == user_id)
    )
    if subject_id is not None:
        query = query.filter(Document.subject_id == subject_id)

    results = (
        query.order_by(DocumentChunk.embedding.cosine_distance(query_embedding)).limit(limit).all()
    )
    return [
        (document_id, filename, doc_subject_id, content, distance)
        for document_id, filename, doc_subject_id, content, distance in results
        if distance <= max_distance
    ]