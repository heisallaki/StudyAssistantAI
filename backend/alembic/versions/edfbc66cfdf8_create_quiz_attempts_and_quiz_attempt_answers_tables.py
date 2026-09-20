"""create quiz attempts and quiz attempt answers tables

Revision ID: edfbc66cfdf8
Revises: 0687a8446829
Create Date: 2026-08-28 06:24:16.687281

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'edfbc66cfdf8'
down_revision: Union[str, None] = '0687a8446829'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('quiz_attempts',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('quiz_id', sa.Uuid(), nullable=False),
    sa.Column('user_id', sa.Uuid(), nullable=False),
    sa.Column('status', sa.String(length=20), nullable=False),
    sa.Column('score', sa.Integer(), nullable=True),
    sa.Column('total_questions', sa.Integer(), nullable=False),
    sa.Column('started_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['quiz_id'], ['quizzes.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_quiz_attempts_quiz_id'), 'quiz_attempts', ['quiz_id'], unique=False)
    op.create_index(op.f('ix_quiz_attempts_user_id'), 'quiz_attempts', ['user_id'], unique=False)
    op.create_table('quiz_attempt_answers',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('attempt_id', sa.Uuid(), nullable=False),
    sa.Column('question_id', sa.Uuid(), nullable=False),
    sa.Column('submitted_answer', sa.String(length=2000), nullable=False),
    sa.Column('is_correct', sa.Boolean(), nullable=True),
    sa.Column('answered_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['attempt_id'], ['quiz_attempts.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['question_id'], ['quiz_questions.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('attempt_id', 'question_id', name='uq_quiz_attempt_answers_attempt_question')
    )
    op.create_index(op.f('ix_quiz_attempt_answers_attempt_id'), 'quiz_attempt_answers', ['attempt_id'], unique=False)
    op.create_index(op.f('ix_quiz_attempt_answers_question_id'), 'quiz_attempt_answers', ['question_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_quiz_attempt_answers_question_id'), table_name='quiz_attempt_answers')
    op.drop_index(op.f('ix_quiz_attempt_answers_attempt_id'), table_name='quiz_attempt_answers')
    op.drop_table('quiz_attempt_answers')
    op.drop_index(op.f('ix_quiz_attempts_user_id'), table_name='quiz_attempts')
    op.drop_index(op.f('ix_quiz_attempts_quiz_id'), table_name='quiz_attempts')
    op.drop_table('quiz_attempts')