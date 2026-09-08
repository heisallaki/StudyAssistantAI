import uuid

from pydantic import BaseModel, Field


class SearchResult(BaseModel):
    result_type: str
    id: uuid.UUID
    title: str
    snippet: str | None
    subject_id: uuid.UUID | None


class SearchResponse(BaseModel):
    query: str
    results: list[SearchResult]


class SemanticSearchRequest(BaseModel):
    query: str = Field(min_length=1, max_length=500)
    subject_id: uuid.UUID | None = None


class SemanticSearchResult(BaseModel):
    document_id: uuid.UUID
    document_title: str
    subject_id: uuid.UUID | None
    chunk_text: str
    similarity_percentage: int


class SemanticSearchResponse(BaseModel):
    query: str
    results: list[SemanticSearchResult]