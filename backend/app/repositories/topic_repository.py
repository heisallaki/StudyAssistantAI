import uuid

from sqlalchemy.orm import Session

from app.models.topic import Topic


def get_by_id_for_subject(db: Session, topic_id: uuid.UUID, subject_id: uuid.UUID) -> Topic | None:
    return db.query(Topic).filter(Topic.id == topic_id, Topic.subject_id == subject_id).first()


def create(db: Session, subject_id: uuid.UUID, data: dict) -> Topic:
    topic = Topic(subject_id=subject_id, **data)
    db.add(topic)
    db.commit()
    db.refresh(topic)
    return topic


def update(db: Session, topic: Topic, data: dict) -> Topic:
    for field, value in data.items():
        setattr(topic, field, value)
    db.add(topic)
    db.commit()
    db.refresh(topic)
    return topic


def delete(db: Session, topic: Topic) -> None:
    db.delete(topic)
    db.commit()