import uuid

from sqlalchemy.orm import Session

from app.models.message import Message


def list_for_conversation(db: Session, conversation_id: uuid.UUID) -> list[Message]:
    return (
        db.query(Message)
        .filter(Message.conversation_id == conversation_id)
        .order_by(Message.created_at)
        .all()
    )


def create(
    db: Session, conversation_id: uuid.UUID, role: str, content: str, sources: list[str] | None = None
) -> Message:
    message = Message(conversation_id=conversation_id, role=role, content=content, sources=sources or [])
    db.add(message)
    db.commit()
    db.refresh(message)
    return message