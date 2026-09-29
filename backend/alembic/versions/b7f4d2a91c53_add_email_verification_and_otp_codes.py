"""add email verification and otp codes

Revision ID: b7f4d2a91c53
Revises: a8e3f19c7d42
Create Date: 2026-09-18 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "b7f4d2a91c53"
down_revision: Union[str, None] = "a8e3f19c7d42"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("is_email_verified", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.alter_column("users", "is_email_verified", server_default=None)

    op.create_table(
        "otp_codes",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("purpose", sa.String(length=50), nullable=False),
        sa.Column("code_hash", sa.String(length=64), nullable=False),
        sa.Column("attempts", sa.Integer(), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("consumed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_otp_codes_user_id"), "otp_codes", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_otp_codes_user_id"), table_name="otp_codes")
    op.drop_table("otp_codes")
    op.drop_column("users", "is_email_verified")