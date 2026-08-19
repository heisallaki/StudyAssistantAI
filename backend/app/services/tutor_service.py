import uuid

from sqlalchemy.orm import Session

from app.ai.service import AITutorService
from app.core.exceptions import ConversationNotFoundError, SubjectNotFoundError
from app.models.conversation import Conversation
from app.models.message import Message
from app.repositories import conversation_repository, message_repository, subject_repository
from app.schemas.conversation import ConversationCreate, ConversationUpdate


def list_conversations(db: Session, user_id: uuid.UUID) -> list[Conversation]:
    return conversation_repository.list_for_user(db, user_id)


def get_conversation(db: Session, conversation_id: uuid.UUID, user_id: uuid.UUID) -> Conversation:
    conversation = conversation_repository.get_by_id_for_user(db, conversation_id, user_id)
    if conversation is None:
        raise ConversationNotFoundError(conversation_id)
    return conversation


def create_conversation(db: Session, user_id: uuid.UUID, data: ConversationCreate) -> Conversation:
    if data.subject_id is not None and subject_repository.get_by_id_for_user(db, data.subject_id, user_id) is None:
        raise SubjectNotFoundError(data.subject_id)

    conversation = Conversation(
        user_id=user_id,
        subject_id=data.subject_id,
        mode=data.mode,
        explanation_level=data.explanation_level,
    )
    return conversation_repository.create(db, conversation)


def update_conversation(
    db: Session, conversation_id: uuid.UUID, user_id: uuid.UUID, data: ConversationUpdate
) -> Conversation:
    conversation = get_conversation(db, conversation_id, user_id)
    update_data = data.model_dump(exclude_unset=True)
    return conversation_repository.update(db, conversation, update_data)


def delete_conversation(db: Session, conversation_id: uuid.UUID, user_id: uuid.UUID) -> None:
    conversation = get_conversation(db, conversation_id, user_id)
    conversation_repository.delete(db, conversation)


def _build_subject_context(db: Session, conversation: Conversation) -> str | None:
    if conversation.subject_id is None:
        return None

    subject = subject_repository.get_by_id_for_user(db, conversation.subject_id, conversation.user_id)
    if subject is None:
        return None

    context = f"The student is currently studying the subject '{subject.name}'."
    if subject.description:
        context += f" Description: {subject.description}."

    topic_titles = [topic.title for topic in subject.topics]
    if topic_titles:
        context += f" Topics in this subject: {', '.join(topic_titles)}."

    return context


async def send_message(
    db: Session,
    ai_service: AITutorService,
    conversation_id: uuid.UUID,
    user_id: uuid.UUID,
    content: str,
) -> Message:
    conversation = get_conversation(db, conversation_id, user_id)

    message_repository.create(db, conversation.id, "user", content)

    history = [
        {"role": message.role, "content": message.content}
        for message in message_repository.list_for_conversation(db, conversation.id)
    ]
    subject_context = _build_subject_context(db, conversation)

    reply_content = await ai_service.generate_reply(
        history=history,
        explanation_level=conversation.explanation_level,
        mode=conversation.mode,
        subject_context=subject_context,
    )

    assistant_message = message_repository.create(db, conversation.id, "assistant", reply_content)

    if conversation.title == "New conversation":
        conversation_repository.update(db, conversation, {"title": content[:60]})

    return assistant_message