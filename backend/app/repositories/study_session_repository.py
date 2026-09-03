import uuid
from datetime import date

from sqlalchemy.orm import Session

from app.models.study_session import StudySession


def list_for_user(
    db: Session,
    user_id: uuid.UUID,
    start: date | None = None,
    end: date | None = None,
    subject_id: uuid.UUID | None = None,
    status: str | None = None,
) -> list[StudySession]:
    query = db.query(StudySession).filter(StudySession.user_id == user_id)
    if start is not None:
        query = query.filter(StudySession.scheduled_date >= start)
    if end is not None:
        query = query.filter(StudySession.scheduled_date <= end)
    if subject_id is not None:
        query = query.filter(StudySession.subject_id == subject_id)
    if status is not None:
        query = query.filter(StudySession.status == status)
    return query.order_by(
        StudySession.scheduled_date, StudySession.start_time.is_(None), StudySession.start_time
    ).all()


def get_by_id_for_user(db: Session, session_id: uuid.UUID, user_id: uuid.UUID) -> StudySession | None:
    return db.query(StudySession).filter(StudySession.id == session_id, StudySession.user_id == user_id).first()


def create(db: Session, user_id: uuid.UUID, data: dict) -> StudySession:
    session = StudySession(user_id=user_id, **data)
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def update(db: Session, session: StudySession, data: dict) -> StudySession:
    for field, value in data.items():
        setattr(session, field, value)
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def delete(db: Session, session: StudySession) -> None:
    db.delete(session)
    db.commit()