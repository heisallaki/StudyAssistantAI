"""add security hardening (login lockout, admin audit log)

Revision ID: f2a7c9d4e1b6
Revises: c4d8f1a9b3e7
Create Date: 2026-09-11 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "f2a7c9d4e1b6"
down_revision: Union[str, None] = "c4d8f1a9b3e7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("failed_login_attempts", sa.Integer(), nullable=False, server_default="0"),
    )
    op.alter_column("users", "failed_login_attempts", server_default=None)
    op.add_column(
        "users",
        sa.Column("locked_until", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_table(
        "admin_audit_logs",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("actor_id", sa.Uuid(), nullable=True),
        sa.Column("actor_email", sa.String(length=255), nullable=False),
        sa.Column("target_user_id", sa.Uuid(), nullable=True),
        sa.Column("target_email", sa.String(length=255), nullable=True),
        sa.Column("action", sa.String(length=50), nullable=False),
        sa.Column("details", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["actor_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["target_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_admin_audit_logs_actor_id"), "admin_audit_logs", ["actor_id"], unique=False)
    op.create_index(
        op.f("ix_admin_audit_logs_target_user_id"), "admin_audit_logs", ["target_user_id"], unique=False
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_admin_audit_logs_target_user_id"), table_name="admin_audit_logs")
    op.drop_index(op.f("ix_admin_audit_logs_actor_id"), table_name="admin_audit_logs")
    op.drop_table("admin_audit_logs")
    op.drop_column("users", "locked_until")
    op.drop_column("users", "failed_login_attempts")