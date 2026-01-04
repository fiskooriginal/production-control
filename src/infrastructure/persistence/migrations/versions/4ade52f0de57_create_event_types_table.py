"""create_event_types_table

Revision ID: 4ade52f0de57
Revises: 5af293df7ed6
Create Date: 2026-01-04 10:12:03.820935

"""
from typing import Sequence, Union

import sqlmodel
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4ade52f0de57'
down_revision: Union[str, Sequence[str], None] = '5af293df7ed6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "event_types",
        sa.Column("event_name", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("event_version", sa.Integer(), nullable=False, server_default=sa.text("1")),
        sa.Column("description", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("is_webhook_enabled", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("event_name"),
        schema="public",
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("event_types", schema="public")
