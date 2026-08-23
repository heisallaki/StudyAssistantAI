import uuid

from sqlalchemy import delete
from sqlalchemy.orm import Session

from app.models.document import Document
from app.models.document_chunk import DocumentChunk


def replace_chunks(db: Session, document_id: uuid.UUID, chunks: list[str], embeddings: list[list[float]]) -> None:
    db.execute(delete(DocumentChunk).where(DocumentChunk.document_id == document_id))
    for index, (content, embedding) in enumerate(zip(chunks, embeddings)):
        db.add(
            DocumentChunk(document_id=document_id, chunk_index=index, content=content, embedding=embedding)
        )
    db.commit()


def search_similar_chunks(
    db: Session,
    user_id: uuid.UUID,
    query_embedding: list[float],
    limit: int = 4,
    max_distance: float = 0.6,
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