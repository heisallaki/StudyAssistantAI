from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.ai.providers.embedding_base import EmbeddingProvider
from app.api.deps import get_current_user, get_embedding_provider
from app.core.exceptions import SemanticSearchFailedError
from app.db.session import get_db
from app.models.user import User
from app.schemas.search import SearchResponse, SemanticSearchRequest, SemanticSearchResponse
from app.services import search_service

router = APIRouter()


@router.get("", response_model=SearchResponse)
def search(
    q: str = Query(min_length=1, max_length=200),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return search_service.search(db, current_user.id, q)


@router.post("/semantic", response_model=SemanticSearchResponse)
async def semantic_search(
    data: SemanticSearchRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    embedding_provider: EmbeddingProvider = Depends(get_embedding_provider),
):
    try:
        return await search_service.semantic_search(
            db, embedding_provider, current_user.id, data.query, data.subject_id
        )
    except SemanticSearchFailedError as error:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(error))