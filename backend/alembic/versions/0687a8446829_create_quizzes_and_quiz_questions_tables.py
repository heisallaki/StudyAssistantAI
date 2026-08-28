"""create quizzes and quiz questions tables

Revision ID: 0687a8446829
Revises: 25b536c97cae
Create Date: 2026-08-23 14:05:02.178808

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "0687a8446829"
down_revision: Union[str, None] = "25b536c97cae"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "quizzes",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("subject_id", sa.UUID(), nullable=True),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("difficulty", sa.String(length=20), nullable=False),
        sa.Column("generation_status", sa.String(length=20), nullable=False),
        sa.Column("generation_error", sa.String(length=500), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["subject_id"],
            ["subjects.id"],
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        op.f("ix_quizzes_user_id"),
        "quizzes",
        ["user_id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_quizzes_subject_id"),
        "quizzes",
        ["subject_id"],
        unique=False,
    )

    op.create_table(
        "quiz_questions",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("quiz_id", sa.UUID(), nullable=False),
        sa.Column("order_index", sa.Integer(), nullable=False),
        sa.Column("question_type", sa.String(length=20), nullable=False),
        sa.Column("prompt", sa.Text(), nullable=False),
        sa.Column(
            "options",
            postgresql.ARRAY(sa.String(length=255)),
            nullable=False,
        ),
        sa.Column("correct_answer", sa.String(length=500), nullable=False),
        sa.Column("explanation", sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(
            ["quiz_id"],
            ["quizzes.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        op.f("ix_quiz_questions_quiz_id"),
        "quiz_questions",
        ["quiz_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_quiz_questions_quiz_id"),
        table_name="quiz_questions",
    )
    op.drop_table("quiz_questions")

    op.drop_index(
        op.f("ix_quizzes_subject_id"),
        table_name="quizzes",
    )
    op.drop_index(
        op.f("ix_quizzes_user_id"),
        table_name="quizzes",
    )
    op.drop_table("quizzes")