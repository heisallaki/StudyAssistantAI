import logging

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy import text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from app.db.session import get_db

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/health")
def health_check(response: Response, db: Session = Depends(get_db)):
    database_status = "connected"
    try:
        db.execute(text("SELECT 1"))
    except OperationalError as error:
        logger.error("Database health check failed: %s", error)
        database_status = "unavailable"
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return {
        "status": "ok" if database_status == "connected" else "degraded",
        "database": database_status,
    }