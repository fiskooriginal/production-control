"""add_unique_constraint_batch_number_date

Revision ID: 4de5d7d1f365
Revises: 5c95b4bd555d
Create Date: 2026-01-01 14:52:12.136199

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4de5d7d1f365'
down_revision: Union[str, Sequence[str], None] = '5c95b4bd555d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_index("idx_batch_number_date", table_name="batches", schema="public")
    op.create_unique_constraint(
        "uq_batch_number_date",
        "batches",
        ["batch_number", "batch_date"],
        schema="public",
    )
    op.create_index(
        "idx_batch_number_date",
        "batches",
        ["batch_number", "batch_date"],
        unique=False,
        schema="public",
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("idx_batch_number_date", table_name="batches", schema="public")
    op.drop_constraint("uq_batch_number_date", "batches", type_="unique", schema="public")
    op.create_index(
        "idx_batch_number_date",
        "batches",
        ["batch_number", "batch_date"],
        unique=False,
        schema="public",
    )
