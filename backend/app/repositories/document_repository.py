import uuid

from sqlalchemy.orm import Session

from app.models.document import Document


def list_for_user(db: Session, user_id: uuid.UUID, subject_id: uuid.UUID | None = None) -> list[Document]:
    query = db.query(Document).filter(Document.user_id == user_id)
    if subject_id is not None:
        query = query.filter(Document.subject_id == subject_id)
    return query.order_by(Document.created_at.desc()).all()


def get_by_id_for_user(db: Session, document_id: uuid.UUID, user_id: uuid.UUID) -> Document | None:
    return db.query(Document).filter(Document.id == document_id, Document.user_id == user_id).first()


def create(db: Session, document: Document) -> Document:
    db.add(document)
    db.commit()
    db.refresh(document)
    return document


def update(db: Session, document: Document, data: dict) -> Document:
    for field, value in data.items():
        setattr(document, field, value)
    db.add(document)
    db.commit()
    db.refresh(document)
    return document


def delete(db: Session, document: Document) -> None:
    db.delete(document)
    db.commit()