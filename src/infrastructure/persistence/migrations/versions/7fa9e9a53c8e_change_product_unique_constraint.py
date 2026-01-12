"""change_product_unique_constraint

Revision ID: 7fa9e9a53c8e
Revises: 4de5d7d1f365
Create Date: 2026-01-15 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7fa9e9a53c8e'
down_revision: Union[str, Sequence[str], None] = '4de5d7d1f365'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_constraint("uq_product_unique_code", "products", type_="unique", schema="public")
    op.create_unique_constraint(
        "uq_product_batch_id_unique_code",
        "products",
        ["batch_id", "unique_code"],
        schema="public",
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint("uq_product_batch_id_unique_code", "products", type_="unique", schema="public")
    op.create_unique_constraint(
        "uq_product_unique_code",
        "products",
        ["unique_code"],
        schema="public",
    )

