"""remove_author_from_work_centers

Revision ID: 8e068efda6c5
Revises: e6dd48bd9c15
Create Date: 2026-01-11 10:24:59.721082

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8e068efda6c5'
down_revision: Union[str, Sequence[str], None] = 'e6dd48bd9c15'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_column('work_centers', 'author', schema='public')


def downgrade() -> None:
    """Downgrade schema."""
    op.add_column(
        'work_centers',
        sa.Column('author', sa.Uuid(), nullable=False),
        schema='public'
    )
