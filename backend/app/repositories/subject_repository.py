import uuid

from sqlalchemy.orm import Session, selectinload

from app.models.subject import Subject


def list_for_user(db: Session, user_id: uuid.UUID) -> list[Subject]:
    return (
        db.query(Subject)
        .options(selectinload(Subject.topics))
        .filter(Subject.user_id == user_id)
        .order_by(Subject.created_at)
        .all()
    )


def get_by_id_for_user(db: Session, subject_id: uuid.UUID, user_id: uuid.UUID) -> Subject | None:
    return (
        db.query(Subject)
        .options(selectinload(Subject.topics))
        .filter(Subject.id == subject_id, Subject.user_id == user_id)
        .first()
    )


def create(db: Session, user_id: uuid.UUID, data: dict) -> Subject:
    subject = Subject(user_id=user_id, **data)
    db.add(subject)
    db.commit()
    db.refresh(subject)
    return subject


def update(db: Session, subject: Subject, data: dict) -> Subject:
    for field, value in data.items():
        setattr(subject, field, value)
    db.add(subject)
    db.commit()
    db.refresh(subject)
    return subject


def delete(db: Session, subject: Subject) -> None:
    db.delete(subject)
    db.commit()