import uuid

from sqlalchemy.orm import Session

from app.repositories import subject_repository


def build_subject_context(db: Session, subject_id: uuid.UUID | None, user_id: uuid.UUID) -> str | None:
    if subject_id is None:
        return None

    subject = subject_repository.get_by_id_for_user(db, subject_id, user_id)
    if subject is None:
        return None

    context = f"The student is currently studying the subject '{subject.name}'."
    if subject.description:
        context += f" Description: {subject.description}."

    topic_titles = [topic.title for topic in subject.topics]
    if topic_titles:
        context += f" Topics in this subject: {', '.join(topic_titles)}."

    return context