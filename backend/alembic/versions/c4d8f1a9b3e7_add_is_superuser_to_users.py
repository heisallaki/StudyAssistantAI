"""add is_superuser to users

Revision ID: c4d8f1a9b3e7
Revises: 08a34e9dedf9
Create Date: 2026-09-11 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "c4d8f1a9b3e7"
down_revision: Union[str, None] = "08a34e9dedf9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("is_superuser", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.alter_column("users", "is_superuser", server_default=None)


def downgrade() -> None:
    op.drop_column("users", "is_superuser")