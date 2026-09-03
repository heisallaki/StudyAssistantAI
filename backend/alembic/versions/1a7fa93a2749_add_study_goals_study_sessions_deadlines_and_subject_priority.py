"""add study goals, study sessions, deadlines, and subject priority

Revision ID: 1a7fa93a2749
Revises: 5e13218ac643
Create Date: 2026-08-31 22:44:02.122607

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '1a7fa93a2749'
down_revision: Union[str, None] = '5e13218ac643'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('deadlines',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('user_id', sa.Uuid(), nullable=False),
    sa.Column('subject_id', sa.Uuid(), nullable=True),
    sa.Column('title', sa.String(length=200), nullable=False),
    sa.Column('due_date', sa.Date(), nullable=False),
    sa.Column('is_completed', sa.Boolean(), nullable=False),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['subject_id'], ['subjects.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_deadlines_due_date'), 'deadlines', ['due_date'], unique=False)
    op.create_index(op.f('ix_deadlines_subject_id'), 'deadlines', ['subject_id'], unique=False)
    op.create_index(op.f('ix_deadlines_user_id'), 'deadlines', ['user_id'], unique=False)
    op.create_table('study_goals',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('user_id', sa.Uuid(), nullable=False),
    sa.Column('subject_id', sa.Uuid(), nullable=True),
    sa.Column('title', sa.String(length=200), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('target_date', sa.Date(), nullable=True),
    sa.Column('status', sa.String(length=20), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['subject_id'], ['subjects.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_study_goals_subject_id'), 'study_goals', ['subject_id'], unique=False)
    op.create_index(op.f('ix_study_goals_user_id'), 'study_goals', ['user_id'], unique=False)
    op.create_table('study_sessions',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('user_id', sa.Uuid(), nullable=False),
    sa.Column('subject_id', sa.Uuid(), nullable=True),
    sa.Column('goal_id', sa.Uuid(), nullable=True),
    sa.Column('title', sa.String(length=200), nullable=False),
    sa.Column('scheduled_date', sa.Date(), nullable=False),
    sa.Column('start_time', sa.Time(), nullable=True),
    sa.Column('duration_minutes', sa.Integer(), nullable=False),
    sa.Column('status', sa.String(length=20), nullable=False),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['goal_id'], ['study_goals.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['subject_id'], ['subjects.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_study_sessions_goal_id'), 'study_sessions', ['goal_id'], unique=False)
    op.create_index(op.f('ix_study_sessions_scheduled_date'), 'study_sessions', ['scheduled_date'], unique=False)
    op.create_index(op.f('ix_study_sessions_subject_id'), 'study_sessions', ['subject_id'], unique=False)
    op.create_index(op.f('ix_study_sessions_user_id'), 'study_sessions', ['user_id'], unique=False)
    op.add_column('subjects', sa.Column('priority', sa.String(length=10), nullable=False, server_default='medium'))


def downgrade() -> None:
    op.drop_column('subjects', 'priority')
    op.drop_index(op.f('ix_study_sessions_user_id'), table_name='study_sessions')
    op.drop_index(op.f('ix_study_sessions_subject_id'), table_name='study_sessions')
    op.drop_index(op.f('ix_study_sessions_scheduled_date'), table_name='study_sessions')
    op.drop_index(op.f('ix_study_sessions_goal_id'), table_name='study_sessions')
    op.drop_table('study_sessions')
    op.drop_index(op.f('ix_study_goals_user_id'), table_name='study_goals')
    op.drop_index(op.f('ix_study_goals_subject_id'), table_name='study_goals')
    op.drop_table('study_goals')
    op.drop_index(op.f('ix_deadlines_user_id'), table_name='deadlines')
    op.drop_index(op.f('ix_deadlines_subject_id'), table_name='deadlines')
    op.drop_index(op.f('ix_deadlines_due_date'), table_name='deadlines')
    op.drop_table('deadlines')