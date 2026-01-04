"""change_webhook_deliveries_event_type_to_string

Revision ID: 42134d911e11
Revises: 67822cfb3d92
Create Date: 2026-01-04 11:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '42134d911e11'
down_revision: Union[str, Sequence[str], None] = '67822cfb3d92'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Преобразуем колонку event_type из enum в varchar
    op.execute(
        """
        ALTER TABLE public.webhook_deliveries 
        ALTER COLUMN event_type TYPE varchar USING event_type::varchar
        """
    )

    # Удаляем тип webhookeventtype
    op.execute("DROP TYPE IF EXISTS public.webhookeventtype")


def downgrade() -> None:
    """Downgrade schema."""
    # Восстанавливаем enum тип
    op.execute(
        """
        CREATE TYPE public.webhookeventtype AS ENUM (
            'BATCH_CREATED', 'BATCH_CLOSED', 'BATCH_OPENED', 
            'BATCH_PRODUCT_ADDED', 'BATCH_PRODUCT_REMOVED', 
            'BATCH_AGGREGATED', 'BATCH_DELETED', 
            'BATCH_REPORT_GENERATED', 'BATCH_IMPORT_COMPLETED', 
            'PRODUCT_AGGREGATED', 'WORK_CENTER_DELETED'
        )
        """
    )

    # Преобразуем колонку обратно в enum
    op.execute(
        """
        ALTER TABLE public.webhook_deliveries 
        ALTER COLUMN event_type TYPE public.webhookeventtype 
        USING event_type::public.webhookeventtype
        """
    )
