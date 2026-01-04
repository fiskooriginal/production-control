"""add_unique_constraint_event_type_name

Revision ID: e6dd48bd9c15
Revises: 42134d911e11
Create Date: 2026-01-04 12:30:06.719470

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e6dd48bd9c15'
down_revision: Union[str, Sequence[str], None] = '42134d911e11'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_index("idx_event_type_name", table_name="event_types", schema="public")
    op.create_unique_constraint(
        "uq_event_type_name",
        "event_types",
        ["name"],
        schema="public",
    )
    op.create_index(
        "idx_event_type_name",
        "event_types",
        ["name"],
        unique=False,
        schema="public",
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("idx_event_type_name", table_name="event_types", schema="public")
    op.drop_constraint("uq_event_type_name", "event_types", type_="unique", schema="public")
    op.create_index(
        "idx_event_type_name",
        "event_types",
        ["name"],
        unique=False,
        schema="public",
    )
