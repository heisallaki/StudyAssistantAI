"""create flashcard decks, flashcards, and flashcard progress tables

Revision ID: 5e13218ac643
Revises: edfbc66cfdf8
Create Date: 2026-08-30 13:26:36.565952

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import pgvector


revision: str = '5e13218ac643'
down_revision: Union[str, None] = 'edfbc66cfdf8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('flashcard_decks',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('user_id', sa.Uuid(), nullable=False),
    sa.Column('subject_id', sa.Uuid(), nullable=True),
    sa.Column('title', sa.String(length=200), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['subject_id'], ['subjects.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_flashcard_decks_subject_id'), 'flashcard_decks', ['subject_id'], unique=False)
    op.create_index(op.f('ix_flashcard_decks_user_id'), 'flashcard_decks', ['user_id'], unique=False)
    op.create_table('flashcards',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('deck_id', sa.Uuid(), nullable=False),
    sa.Column('front', sa.Text(), nullable=False),
    sa.Column('back', sa.Text(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['deck_id'], ['flashcard_decks.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_flashcards_deck_id'), 'flashcards', ['deck_id'], unique=False)
    op.create_table('flashcard_progress',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('flashcard_id', sa.Uuid(), nullable=False),
    sa.Column('status', sa.String(length=20), nullable=False),
    sa.Column('times_reviewed', sa.Integer(), nullable=False),
    sa.Column('times_correct', sa.Integer(), nullable=False),
    sa.Column('correct_streak', sa.Integer(), nullable=False),
    sa.Column('last_reviewed_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['flashcard_id'], ['flashcards.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_flashcard_progress_flashcard_id'), 'flashcard_progress', ['flashcard_id'], unique=True)


def downgrade() -> None:
    op.drop_index(op.f('ix_flashcard_progress_flashcard_id'), table_name='flashcard_progress')
    op.drop_table('flashcard_progress')
    op.drop_index(op.f('ix_flashcards_deck_id'), table_name='flashcards')
    op.drop_table('flashcards')
    op.drop_index(op.f('ix_flashcard_decks_user_id'), table_name='flashcard_decks')
    op.drop_index(op.f('ix_flashcard_decks_subject_id'), table_name='flashcard_decks')
    op.drop_table('flashcard_decks')