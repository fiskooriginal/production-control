from src.core.time import datetime_aware_to_naive, datetime_naive_to_aware
from src.domain.products import ProductEntity
from src.domain.products.value_objects import ProductCode
from src.infrastructure.common.exceptions import MappingException
from src.infrastructure.persistence.models.product import Product


def to_domain_entity(product_model: Product) -> ProductEntity:
    """Конвертирует persistence модель Product в domain domain_entity ProductEntity"""
    try:
        return ProductEntity(
            uuid=product_model.uuid,
            created_at=datetime_naive_to_aware(product_model.created_at),
            updated_at=datetime_naive_to_aware(product_model.updated_at),
            unique_code=ProductCode(product_model.unique_code),
            batch_id=product_model.batch_id,
            is_aggregated=product_model.is_aggregated,
            aggregated_at=datetime_naive_to_aware(product_model.aggregated_at),
        )
    except Exception as e:
        raise MappingException(f"Ошибка маппинга persistence -> domain для Product: {e}") from e


def to_persistence_model(product_entity: ProductEntity) -> Product:
    """Конвертирует domain domain_entity ProductEntity в persistence модель Product"""
    try:
        return Product(
            uuid=product_entity.uuid,
            created_at=datetime_aware_to_naive(product_entity.created_at),
            updated_at=datetime_aware_to_naive(product_entity.updated_at),
            unique_code=product_entity.unique_code.value,
            batch_id=product_entity.batch_id,
            is_aggregated=product_entity.is_aggregated,
            aggregated_at=datetime_aware_to_naive(product_entity.aggregated_at),
        )
    except Exception as e:
        raise MappingException(f"Ошибка маппинга domain -> persistence для Product: {e}") from e
