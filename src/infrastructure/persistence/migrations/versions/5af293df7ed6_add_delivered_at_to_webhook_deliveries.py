"""add_delivered_at_to_webhook_deliveries

Revision ID: 5af293df7ed6
Revises: 7fa9e9a53c8e
Create Date: 2026-01-15 14:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5af293df7ed6'
down_revision: Union[str, Sequence[str], None] = '7fa9e9a53c8e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        'webhook_deliveries',
        sa.Column('delivered_at', sa.DateTime(), nullable=True),
        schema='public'
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('webhook_deliveries', 'delivered_at', schema='public')

