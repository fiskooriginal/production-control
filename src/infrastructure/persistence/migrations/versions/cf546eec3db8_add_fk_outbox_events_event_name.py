"""add_fk_outbox_events_event_name

Revision ID: cf546eec3db8
Revises: d5e4bad425dc
Create Date: 2026-01-04 10:12:46.641039

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cf546eec3db8'
down_revision: Union[str, Sequence[str], None] = 'd5e4bad425dc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_foreign_key(
        "fk_outbox_events_event_name",
        "outbox_events",
        "event_types",
        ["event_name"],
        ["event_name"],
        source_schema="public",
        referent_schema="public",
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint("fk_outbox_events_event_name", "outbox_events", type_="foreignkey", schema="public")
