"""add composite indexes for high-traffic list queries

Revision ID: a8e3f19c7d42
Revises: f2a7c9d4e1b6
Create Date: 2026-09-13 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op


revision: str = "a8e3f19c7d42"
down_revision: Union[str, None] = "f2a7c9d4e1b6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index(
        "ix_notifications_user_id_created_at",
        "notifications",
        ["user_id", "created_at"],
    )
    op.create_index(
        "ix_documents_user_id_created_at",
        "documents",
        ["user_id", "created_at"],
    )
    op.create_index(
        "ix_quiz_attempts_user_id_started_at",
        "quiz_attempts",
        ["user_id", "started_at"],
    )
    op.create_index(
        "ix_conversations_user_id_updated_at",
        "conversations",
        ["user_id", "updated_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_conversations_user_id_updated_at", table_name="conversations")
    op.drop_index("ix_quiz_attempts_user_id_started_at", table_name="quiz_attempts")
    op.drop_index("ix_documents_user_id_created_at", table_name="documents")
    op.drop_index("ix_notifications_user_id_created_at", table_name="notifications")