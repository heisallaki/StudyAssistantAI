import uuid

from sqlalchemy.orm import Session

from app.models.admin_audit_log import AdminAuditLog


def create(
    db: Session,
    actor_id: uuid.UUID | None,
    actor_email: str,
    target_user_id: uuid.UUID | None,
    target_email: str | None,
    action: str,
    details: str | None,
) -> AdminAuditLog:
    entry = AdminAuditLog(
        actor_id=actor_id,
        actor_email=actor_email,
        target_user_id=target_user_id,
        target_email=target_email,
        action=action,
        details=details,
    )
    db.add(entry)
    return entry


def list_entries(db: Session, page: int, page_size: int) -> tuple[list[AdminAuditLog], int]:
    query = db.query(AdminAuditLog).order_by(AdminAuditLog.created_at.desc())
    total = query.count()
    entries = query.offset((page - 1) * page_size).limit(page_size).all()
    return entries, total