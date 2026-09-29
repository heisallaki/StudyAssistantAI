import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.otp_code import OtpCode


def create(db: Session, user_id: uuid.UUID, purpose: str, code_hash: str, expires_at: datetime) -> OtpCode:
    otp = OtpCode(user_id=user_id, purpose=purpose, code_hash=code_hash, expires_at=expires_at)
    db.add(otp)
    db.commit()
    db.refresh(otp)
    return otp


def get_latest_active(db: Session, user_id: uuid.UUID, purpose: str) -> OtpCode | None:
    return (
        db.query(OtpCode)
        .filter(OtpCode.user_id == user_id, OtpCode.purpose == purpose, OtpCode.consumed_at.is_(None))
        .order_by(OtpCode.created_at.desc())
        .first()
    )


def increment_attempts(db: Session, otp: OtpCode) -> None:
    otp.attempts += 1
    db.commit()


def mark_consumed(db: Session, otp: OtpCode) -> None:
    otp.consumed_at = datetime.now(timezone.utc)
    db.commit()


def delete_active_for_purpose(db: Session, user_id: uuid.UUID, purpose: str) -> None:
    db.query(OtpCode).filter(
        OtpCode.user_id == user_id, OtpCode.purpose == purpose, OtpCode.consumed_at.is_(None)
    ).delete()
    db.commit()