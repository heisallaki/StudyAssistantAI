import uuid

from sqlalchemy.orm import Session

from app.ai.providers.embedding_base import EmbeddingProvider, EmbeddingProviderError
from app.core.exceptions import SemanticSearchFailedError
from app.repositories import document_chunk_repository, search_repository
from app.schemas.search import SearchResponse, SearchResult, SemanticSearchResponse, SemanticSearchResult
from app.services.search_utils import build_snippet, distance_to_similarity_percentage


def search(db: Session, user_id: uuid.UUID, query: str) -> SearchResponse:
    results: list[SearchResult] = []

    for subject in search_repository.search_subjects(db, user_id, query):
        results.append(
            SearchResult(
                result_type="subject",
                id=subject.id,
                title=subject.name,
                snippet=build_snippet(subject.description, query) if subject.description else None,
                subject_id=subject.id,
            )
        )

    for topic in search_repository.search_topics(db, user_id, query):
        results.append(
            SearchResult(
                result_type="topic",
                id=topic.id,
                title=topic.title,
                snippet=build_snippet(topic.description, query) if topic.description else None,
                subject_id=topic.subject_id,
            )
        )

    for document in search_repository.search_documents(db, user_id, query):
        results.append(
            SearchResult(
                result_type="document",
                id=document.id,
                title=document.original_filename,
                snippet=build_snippet(document.extracted_text, query) if document.extracted_text else None,
                subject_id=document.subject_id,
            )
        )

    for quiz in search_repository.search_quizzes(db, user_id, query):
        results.append(
            SearchResult(
                result_type="quiz",
                id=quiz.id,
                title=quiz.title,
                snippet=None,
                subject_id=quiz.subject_id,
            )
        )

    for deck in search_repository.search_flashcard_decks(db, user_id, query):
        results.append(
            SearchResult(
                result_type="flashcard_deck",
                id=deck.id,
                title=deck.title,
                snippet=build_snippet(deck.description, query) if deck.description else None,
                subject_id=deck.subject_id,
            )
        )

    return SearchResponse(query=query, results=results)


async def semantic_search(
    db: Session,
    embedding_provider: EmbeddingProvider,
    user_id: uuid.UUID,
    query: str,
    subject_id: uuid.UUID | None,
) -> SemanticSearchResponse:
    try:
        query_embeddings = await embedding_provider.embed([query])
    except EmbeddingProviderError as error:
        raise SemanticSearchFailedError(str(error))

    if not query_embeddings:
        raise SemanticSearchFailedError("Could not generate an embedding for this query.")

    chunks = document_chunk_repository.search_chunks_for_query(
        db, user_id, query_embeddings[0], subject_id=subject_id
    )

    results = [
        SemanticSearchResult(
            document_id=document_id,
            document_title=filename,
            subject_id=doc_subject_id,
            chunk_text=content,
            similarity_percentage=distance_to_similarity_percentage(distance),
        )
        for document_id, filename, doc_subject_id, content, distance in chunks
    ]
    return SemanticSearchResponse(query=query, results=results)