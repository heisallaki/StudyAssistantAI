import json
import logging
import uuid

from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.ai.prompts.quiz_prompts import build_quiz_prompt
from app.ai.prompts.rag_prompts import build_document_context
from app.ai.providers.base import AIProvider, AIProviderError
from app.ai.providers.embedding_base import EmbeddingProvider, EmbeddingProviderError
from app.core.exceptions import QuizNotFoundError, SubjectNotFoundError
from app.models.quiz import Quiz
from app.repositories import document_chunk_repository, quiz_repository, subject_repository
from app.schemas.quiz import QuizCreate
from app.services.quiz_parsing import parse_generated_quiz
from app.services.subject_context import build_subject_context

logger = logging.getLogger(__name__)


def list_quizzes(db: Session, user_id: uuid.UUID) -> list[Quiz]:
    return quiz_repository.list_for_user(db, user_id)


def get_quiz(db: Session, quiz_id: uuid.UUID, user_id: uuid.UUID) -> Quiz:
    quiz = quiz_repository.get_by_id_for_user(db, quiz_id, user_id)
    if quiz is None:
        raise QuizNotFoundError(quiz_id)
    return quiz


def delete_quiz(db: Session, quiz_id: uuid.UUID, user_id: uuid.UUID) -> None:
    quiz = get_quiz(db, quiz_id, user_id)
    quiz_repository.delete(db, quiz)


def _build_title(db: Session, subject_id: uuid.UUID | None, user_id: uuid.UUID, difficulty: str) -> str:
    subject_name = "General"
    if subject_id is not None:
        subject = subject_repository.get_by_id_for_user(db, subject_id, user_id)
        if subject is not None:
            subject_name = subject.name
    return f"{subject_name} Quiz ({difficulty.capitalize()})"


async def _retrieve_document_context(
    db: Session, embedding_provider: EmbeddingProvider, user_id: uuid.UUID, subject_context: str | None
) -> str | None:
    if subject_context is None:
        return None

    try:
        query_embeddings = await embedding_provider.embed([subject_context])
    except EmbeddingProviderError:
        return None

    if not query_embeddings:
        return None

    chunks = document_chunk_repository.search_similar_chunks(
        db, user_id, query_embeddings[0], limit=6, max_distance=0.7
    )
    return build_document_context(chunks) if chunks else None


async def generate_quiz(
    db: Session,
    ai_provider: AIProvider,
    embedding_provider: EmbeddingProvider,
    user_id: uuid.UUID,
    data: QuizCreate,
) -> Quiz:
    if data.subject_id is not None and subject_repository.get_by_id_for_user(db, data.subject_id, user_id) is None:
        raise SubjectNotFoundError(data.subject_id)

    subject_context = build_subject_context(db, data.subject_id, user_id)
    document_context = await _retrieve_document_context(db, embedding_provider, user_id, subject_context)
    title = _build_title(db, data.subject_id, user_id, data.difficulty)

    quiz = Quiz(
        user_id=user_id,
        subject_id=data.subject_id,
        title=title,
        difficulty=data.difficulty,
        generation_status="pending",
    )
    quiz = quiz_repository.create(db, quiz)

    prompt = build_quiz_prompt(
        subject_context, document_context, data.difficulty, data.question_types, data.question_count
    )
    messages = [{"role": "user", "content": prompt}]

    try:
        raw_response = await ai_provider.generate_reply(messages, response_format="json")
    except AIProviderError as error:
        quiz_repository.set_generation_status(db, quiz, "failed", str(error))
        return quiz

    try:
        generated_questions = parse_generated_quiz(raw_response)
    except (json.JSONDecodeError, ValidationError) as error:
        logger.warning("Failed to parse quiz generation response: %s", error)
        quiz_repository.set_generation_status(db, quiz, "failed", "The AI returned an unexpected response format.")
        return quiz

    if not generated_questions:
        quiz_repository.set_generation_status(db, quiz, "failed", "The AI did not return any valid questions.")
        return quiz

    quiz_repository.add_questions(db, quiz.id, [question.model_dump() for question in generated_questions])
    quiz_repository.set_generation_status(db, quiz, "completed", None)
    db.refresh(quiz)
    return quiz