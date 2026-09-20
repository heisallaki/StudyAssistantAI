"""create user profiles table

Revision ID: ab45b2810c55
Revises: 09e3b334aae6
Create Date: 2026-08-14 19:27:59.319420

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "ab45b2810c55"
down_revision: Union[str, None] = "09e3b334aae6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "user_profiles",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=True),
        sa.Column("academic_level", sa.String(length=50), nullable=True),
        sa.Column("institution", sa.String(length=255), nullable=True),
        sa.Column("program", sa.String(length=255), nullable=True),
        sa.Column(
            "subjects",
            postgresql.ARRAY(sa.String(length=100)),
            nullable=False,
        ),
        sa.Column("academic_goals", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            postgresql.TIMESTAMP(timezone=True),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name="fk_user_profiles_user_id_users",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id"),
    )


def downgrade() -> None:
    op.drop_table("user_profiles")