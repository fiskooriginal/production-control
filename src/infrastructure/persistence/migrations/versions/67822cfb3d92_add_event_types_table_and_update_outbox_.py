"""add_event_types_table_and_update_outbox_webhook_deliveries

Revision ID: 67822cfb3d92
Revises: 5af293df7ed6
Create Date: 2026-01-04 11:11:03.499550

"""
from typing import Sequence, Union

import sqlmodel
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text


# revision identifiers, used by Alembic.
revision: str = '67822cfb3d92'
down_revision: Union[str, Sequence[str], None] = '5af293df7ed6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Создаем таблицу event_types
    op.create_table(
        "event_types",
        sa.Column("uuid", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False, server_default=sa.text("1")),
        sa.Column("webhook_enabled", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("description", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.PrimaryKeyConstraint("uuid"),
        sa.UniqueConstraint("uuid"),
        schema="public",
    )

    op.create_index("idx_event_type_name", "event_types", ["name"], unique=False, schema="public")
    op.create_index("idx_event_type_version", "event_types", ["version"], unique=False, schema="public")

    # Вставляем 11 захардкоженных событий из EventTypesEnum
    event_types_data = [
        ("batch.created", 1, True),
        ("batch.closed", 1, True),
        ("batch.opened", 1, True),
        ("batch.product_added", 1, True),
        ("batch.product_removed", 1, True),
        ("batch.aggregated", 1, True),
        ("batch.deleted", 1, True),
        ("batch.report_generated", 1, True),
        ("product.aggregated", 1, True),
        ("work_center.deleted", 1, True),
        ("batch.import_completed", 1, True),
    ]

    connection = op.get_bind()
    for event_name, event_version, webhook_enabled in event_types_data:
        connection.execute(
            text(
                """
                INSERT INTO public.event_types (uuid, created_at, name, version, webhook_enabled)
                VALUES (gen_random_uuid(), NOW(), :name, :version, :webhook_enabled)
                """
            ),
            {"name": event_name, "version": event_version, "webhook_enabled": webhook_enabled},
        )

    # Добавляем колонку event_type_id в outbox_events
    op.add_column(
        "outbox_events",
        sa.Column("event_type_id", sa.Uuid(), nullable=True),
        schema="public",
    )

    # Заполняем event_type_id на основе event_name (JOIN)
    connection.execute(
        text(
            """
            UPDATE public.outbox_events oe
            SET event_type_id = et.uuid
            FROM public.event_types et
            WHERE oe.event_name = et.name AND oe.event_version = et.version
            """
        )
    )

    # Делаем event_name nullable в outbox_events
    op.alter_column(
        "outbox_events",
        "event_name",
        existing_type=sqlmodel.sql.sqltypes.AutoString(),
        nullable=True,
        schema="public",
    )

    # Добавляем FK outbox_events.event_type_id -> event_types.uuid
    op.create_foreign_key(
        "fk_outbox_events_event_type_id",
        "outbox_events",
        "event_types",
        ["event_type_id"],
        ["uuid"],
        source_schema="public",
        referent_schema="public",
    )

    # Добавляем индекс на outbox_events.event_type_id
    op.create_index(
        "idx_outbox_event_type_id",
        "outbox_events",
        ["event_type_id"],
        unique=False,
        schema="public",
    )

    # Добавляем колонку event_type_id в webhook_deliveries
    op.add_column(
        "webhook_deliveries",
        sa.Column("event_type_id", sa.Uuid(), nullable=True),
        schema="public",
    )

    # Заполняем event_type_id на основе event_type enum (через маппинг)
    # Маппинг: WebhookEventType enum -> EventTypesEnum values
    # В PostgreSQL enum хранится как имя enum (BATCH_CREATED), а не значение
    connection.execute(
        text(
            """
            UPDATE public.webhook_deliveries wd
            SET event_type_id = et.uuid
            FROM public.event_types et
            WHERE (
              (wd.event_type::text = 'BATCH_CREATED' AND et.name = 'batch.created') OR
              (wd.event_type::text = 'BATCH_CLOSED' AND et.name = 'batch.closed') OR
              (wd.event_type::text = 'BATCH_OPENED' AND et.name = 'batch.opened') OR
              (wd.event_type::text = 'BATCH_PRODUCT_ADDED' AND et.name = 'batch.product_added') OR
              (wd.event_type::text = 'BATCH_PRODUCT_REMOVED' AND et.name = 'batch.product_removed') OR
              (wd.event_type::text = 'BATCH_AGGREGATED' AND et.name = 'batch.aggregated') OR
              (wd.event_type::text = 'BATCH_DELETED' AND et.name = 'batch.deleted') OR
              (wd.event_type::text = 'BATCH_REPORT_GENERATED' AND et.name = 'batch.report_generated') OR
              (wd.event_type::text = 'BATCH_IMPORT_COMPLETED' AND et.name = 'batch.import_completed') OR
              (wd.event_type::text = 'PRODUCT_AGGREGATED' AND et.name = 'product.aggregated') OR
              (wd.event_type::text = 'WORK_CENTER_DELETED' AND et.name = 'work_center.deleted')
            )
            AND et.version = 1
            """
        )
    )

    # Делаем event_type nullable в webhook_deliveries
    op.alter_column(
        "webhook_deliveries",
        "event_type",
        existing_type=sa.Enum("BATCH_CREATED", "BATCH_CLOSED", name="webhookeventtype"),
        nullable=True,
        schema="public",
    )

    # Добавляем FK webhook_deliveries.event_type_id -> event_types.uuid
    op.create_foreign_key(
        "fk_webhook_deliveries_event_type_id",
        "webhook_deliveries",
        "event_types",
        ["event_type_id"],
        ["uuid"],
        source_schema="public",
        referent_schema="public",
    )

    # Добавляем индекс на webhook_deliveries.event_type_id
    op.create_index(
        "idx_webhook_delivery_event_type_id",
        "webhook_deliveries",
        ["event_type_id"],
        unique=False,
        schema="public",
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Удаляем индексы
    op.drop_index("idx_webhook_delivery_event_type_id", table_name="webhook_deliveries", schema="public")
    op.drop_index("idx_outbox_event_type_id", table_name="outbox_events", schema="public")

    # Удаляем FK
    op.drop_constraint("fk_webhook_deliveries_event_type_id", "webhook_deliveries", schema="public", type_="foreignkey")
    op.drop_constraint("fk_outbox_events_event_type_id", "outbox_events", schema="public", type_="foreignkey")

    # Восстанавливаем event_type как NOT NULL
    op.alter_column(
        "webhook_deliveries",
        "event_type",
        existing_type=sa.Enum("BATCH_CREATED", "BATCH_CLOSED", name="webhookeventtype"),
        nullable=False,
        schema="public",
    )

    # Восстанавливаем event_name как NOT NULL
    op.alter_column(
        "outbox_events",
        "event_name",
        existing_type=sqlmodel.sql.sqltypes.AutoString(),
        nullable=False,
        schema="public",
    )

    # Удаляем колонки event_type_id
    op.drop_column("webhook_deliveries", "event_type_id", schema="public")
    op.drop_column("outbox_events", "event_type_id", schema="public")

    # Удаляем таблицу event_types
    op.drop_index("idx_event_type_version", table_name="event_types", schema="public")
    op.drop_index("idx_event_type_name", table_name="event_types", schema="public")
    op.drop_table("event_types", schema="public")
