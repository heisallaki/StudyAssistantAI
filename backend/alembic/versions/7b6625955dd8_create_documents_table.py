"""create documents table

Revision ID: 7b6625955dd8
Revises: 80c58e21d975
Create Date: 2026-08-17
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "7b6625955dd8"
down_revision: Union[str, None] = "80c58e21d975"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass

def downgrade() -> None:
    pass