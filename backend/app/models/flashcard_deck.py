import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.flashcard import Flashcard
    from app.models.user import User


class FlashcardDeck(Base):
    __tablename__ = "flashcard_decks"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    subject_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("subjects.id", ondelete="SET NULL"), nullable=True, index=True
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    owner: Mapped["User"] = relationship(back_populates="flashcard_decks")
    flashcards: Mapped[list["Flashcard"]] = relationship(
        back_populates="deck", cascade="all, delete-orphan", order_by="Flashcard.created_at"
    )

    @property
    def card_count(self) -> int:
        return len(self.flashcards)

    @property
    def mastered_count(self) -> int:
        return sum(1 for card in self.flashcards if card.progress.status == "mastered")

    @property
    def mastery_percentage(self) -> int:
        if not self.flashcards:
            return 0
        return round((self.mastered_count / self.card_count) * 100)