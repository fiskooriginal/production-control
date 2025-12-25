"""add outbox events table

Revision ID: outbox_events_001
Revises: 2d4e172e89bf
Create Date: 2024-12-24 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
import sqlmodel
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = 'outbox_events_001'
down_revision: Union[str, Sequence[str], None] = '2d4e172e89bf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'outbox_events',
        sa.Column('uuid', sa.Uuid(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('event_name', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('event_version', sa.Integer(), nullable=False),
        sa.Column('aggregate_id', sa.Uuid(), nullable=False),
        sa.Column('payload', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('occurred_at', sa.DateTime(), nullable=False),
        sa.Column('status', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('attempts', sa.Integer(), nullable=False),
        sa.Column('locked_until', sa.DateTime(), nullable=True),
        sa.Column('processed_at', sa.DateTime(), nullable=True),
        sa.Column('last_error', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('correlation_id', sa.Uuid(), nullable=True),
        sa.Column('causation_id', sa.Uuid(), nullable=True),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('dedup_key', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.PrimaryKeyConstraint('uuid'),
        sa.UniqueConstraint('uuid'),
        sa.UniqueConstraint('dedup_key', name='uq_outbox_dedup_key'),
        schema='public'
    )
    op.create_index('idx_outbox_event_name', 'outbox_events', ['event_name'], unique=False, schema='public')
    op.create_index('idx_outbox_aggregate_id', 'outbox_events', ['aggregate_id'], unique=False, schema='public')
    op.create_index('idx_outbox_status', 'outbox_events', ['status'], unique=False, schema='public')
    op.create_index('idx_outbox_created_at', 'outbox_events', ['created_at'], unique=False, schema='public')
    op.create_index('idx_outbox_status_locked', 'outbox_events', ['status', 'locked_until'], unique=False, schema='public')


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('idx_outbox_status_locked', table_name='outbox_events', schema='public')
    op.drop_index('idx_outbox_created_at', table_name='outbox_events', schema='public')
    op.drop_index('idx_outbox_status', table_name='outbox_events', schema='public')
    op.drop_index('idx_outbox_aggregate_id', table_name='outbox_events', schema='public')
    op.drop_index('idx_outbox_event_name', table_name='outbox_events', schema='public')
    op.drop_table('outbox_events', schema='public')

