import uuid

from sqlalchemy.orm import Session, selectinload

from app.models.conversation import Conversation


def list_for_user(db: Session, user_id: uuid.UUID) -> list[Conversation]:
    return (
        db.query(Conversation)
        .filter(Conversation.user_id == user_id)
        .order_by(Conversation.updated_at.desc())
        .all()
    )


def get_by_id_for_user(db: Session, conversation_id: uuid.UUID, user_id: uuid.UUID) -> Conversation | None:
    return (
        db.query(Conversation)
        .options(selectinload(Conversation.messages))
        .filter(Conversation.id == conversation_id, Conversation.user_id == user_id)
        .first()
    )


def create(db: Session, conversation: Conversation) -> Conversation:
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    return conversation


def update(db: Session, conversation: Conversation, data: dict) -> Conversation:
    for field, value in data.items():
        setattr(conversation, field, value)
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    return conversation


def delete(db: Session, conversation: Conversation) -> None:
    db.delete(conversation)
    db.commit()