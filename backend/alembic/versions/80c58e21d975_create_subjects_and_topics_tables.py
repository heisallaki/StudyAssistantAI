"""create subjects and topics tables

Revision ID: 80c58e21d975
Revises: ab45b2810c55
Create Date: 2026-08-16 18:47:34.954763

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "80c58e21d975"
down_revision: Union[str, None] = "ab45b2810c55"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "subjects",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("color", sa.String(length=20), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        op.f("ix_subjects_user_id"),
        "subjects",
        ["user_id"],
        unique=False,
    )

    op.create_table(
        "topics",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("subject_id", sa.UUID(), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_completed", sa.Boolean(), nullable=False),
        sa.Column("order_index", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["subject_id"],
            ["subjects.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        op.f("ix_topics_subject_id"),
        "topics",
        ["subject_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_topics_subject_id"), table_name="topics")
    op.drop_table("topics")

    op.drop_index(op.f("ix_subjects_user_id"), table_name="subjects")
    op.drop_table("subjects")