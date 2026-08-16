import uuid

from sqlalchemy.orm import Session

from app.core.exceptions import SubjectNotFoundError, TopicNotFoundError
from app.models.subject import Subject
from app.models.topic import Topic
from app.repositories import subject_repository, topic_repository
from app.schemas.subject import SubjectCreate, SubjectUpdate, TopicCreate, TopicUpdate


def list_subjects(db: Session, user_id: uuid.UUID) -> list[Subject]:
    return subject_repository.list_for_user(db, user_id)


def get_subject(db: Session, subject_id: uuid.UUID, user_id: uuid.UUID) -> Subject:
    subject = subject_repository.get_by_id_for_user(db, subject_id, user_id)
    if subject is None:
        raise SubjectNotFoundError(subject_id)
    return subject


def create_subject(db: Session, user_id: uuid.UUID, data: SubjectCreate) -> Subject:
    return subject_repository.create(db, user_id, data.model_dump())


def update_subject(db: Session, subject_id: uuid.UUID, user_id: uuid.UUID, data: SubjectUpdate) -> Subject:
    subject = get_subject(db, subject_id, user_id)
    update_data = data.model_dump(exclude_unset=True)
    return subject_repository.update(db, subject, update_data)


def delete_subject(db: Session, subject_id: uuid.UUID, user_id: uuid.UUID) -> None:
    subject = get_subject(db, subject_id, user_id)
    subject_repository.delete(db, subject)


def create_topic(db: Session, subject_id: uuid.UUID, user_id: uuid.UUID, data: TopicCreate) -> Topic:
    subject = get_subject(db, subject_id, user_id)
    return topic_repository.create(db, subject.id, data.model_dump())


def update_topic(
    db: Session, subject_id: uuid.UUID, topic_id: uuid.UUID, user_id: uuid.UUID, data: TopicUpdate
) -> Topic:
    subject = get_subject(db, subject_id, user_id)
    topic = topic_repository.get_by_id_for_subject(db, topic_id, subject.id)
    if topic is None:
        raise TopicNotFoundError(topic_id)
    update_data = data.model_dump(exclude_unset=True)
    return topic_repository.update(db, topic, update_data)


def delete_topic(db: Session, subject_id: uuid.UUID, topic_id: uuid.UUID, user_id: uuid.UUID) -> None:
    subject = get_subject(db, subject_id, user_id)
    topic = topic_repository.get_by_id_for_subject(db, topic_id, subject.id)
    if topic is None:
        raise TopicNotFoundError(topic_id)
    topic_repository.delete(db, topic)