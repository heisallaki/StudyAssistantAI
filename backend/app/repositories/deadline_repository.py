import uuid
from datetime import date

from sqlalchemy.orm import Session

from app.models.deadline import Deadline


def list_for_user(
    db: Session,
    user_id: uuid.UUID,
    start: date | None = None,
    end: date | None = None,
    include_completed: bool = True,
) -> list[Deadline]:
    query = db.query(Deadline).filter(Deadline.user_id == user_id)
    if start is not None:
        query = query.filter(Deadline.due_date >= start)
    if end is not None:
        query = query.filter(Deadline.due_date <= end)
    if not include_completed:
        query = query.filter(Deadline.is_completed.is_(False))
    return query.order_by(Deadline.due_date).all()


def get_by_id_for_user(db: Session, deadline_id: uuid.UUID, user_id: uuid.UUID) -> Deadline | None:
    return db.query(Deadline).filter(Deadline.id == deadline_id, Deadline.user_id == user_id).first()


def create(db: Session, user_id: uuid.UUID, data: dict) -> Deadline:
    deadline = Deadline(user_id=user_id, **data)
    db.add(deadline)
    db.commit()
    db.refresh(deadline)
    return deadline


def update(db: Session, deadline: Deadline, data: dict) -> Deadline:
    for field, value in data.items():
        setattr(deadline, field, value)
    db.add(deadline)
    db.commit()
    db.refresh(deadline)
    return deadline


def delete(db: Session, deadline: Deadline) -> None:
    db.delete(deadline)
    db.commit()