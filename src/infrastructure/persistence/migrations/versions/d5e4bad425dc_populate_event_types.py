"""populate_event_types

Revision ID: d5e4bad425dc
Revises: 4ade52f0de57
Create Date: 2026-01-04 10:12:18.943248

"""
from datetime import datetime
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text

from src.infrastructure.events.registry import EventRegistry


# revision identifiers, used by Alembic.
revision: str = 'd5e4bad425dc'
down_revision: Union[str, Sequence[str], None] = '4ade52f0de57'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    connection = op.get_bind()
    now = datetime.now()

    event_types_data = []
    for (event_name, event_version), _ in EventRegistry._registry.items():
        event_types_data.append({
            "event_name": event_name,
            "event_version": event_version,
            "description": None,
            "is_webhook_enabled": False,
            "created_at": now,
            "updated_at": None,
        })

    if event_types_data:
        op.bulk_insert(
            sa.table(
                "event_types",
                sa.column("event_name"),
                sa.column("event_version"),
                sa.column("description"),
                sa.column("is_webhook_enabled"),
                sa.column("created_at"),
                sa.column("updated_at"),
            ),
            event_types_data,
        )


def downgrade() -> None:
    """Downgrade schema."""
    op.execute(text("DELETE FROM public.event_types"))
