import uuid

from sqlalchemy.orm import Session

from app.ai.prompts.tutor_prompts import build_document_context
from app.ai.providers.embedding_base import EmbeddingProvider, EmbeddingProviderError
from app.ai.service import AITutorService
from app.core.exceptions import ConversationNotFoundError, SubjectNotFoundError
from app.models.conversation import Conversation
from app.models.message import Message
from app.repositories import (
    conversation_repository,
    document_chunk_repository,
    message_repository,
    subject_repository,
)
from app.schemas.conversation import ConversationCreate, ConversationUpdate
from app.services.subject_context import build_subject_context


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


async def _retrieve_relevant_chunks(
    db: Session, embedding_provider: EmbeddingProvider, user_id: uuid.UUID, query: str
) -> list[tuple[str, str, float]]:
    try:
        query_embeddings = await embedding_provider.embed([query])
    except EmbeddingProviderError:
        return []

    if not query_embeddings:
        return []

    return document_chunk_repository.search_similar_chunks(db, user_id, query_embeddings[0])


async def send_message(
    db: Session,
    ai_service: AITutorService,
    embedding_provider: EmbeddingProvider,
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
    subject_context = build_subject_context(db, conversation.subject_id, user_id)

    retrieved_chunks = await _retrieve_relevant_chunks(db, embedding_provider, user_id, content)
    document_context = build_document_context(retrieved_chunks)
    source_filenames = sorted({filename for filename, _content, _distance in retrieved_chunks})

    reply_content = await ai_service.generate_reply(
        history=history,
        explanation_level=conversation.explanation_level,
        mode=conversation.mode,
        subject_context=subject_context,
        document_context=document_context,
    )

    assistant_message = message_repository.create(
        db, conversation.id, "assistant", reply_content, sources=source_filenames
    )

    if conversation.title == "New conversation":
        conversation_repository.update(db, conversation, {"title": content[:60]})

    return assistant_message