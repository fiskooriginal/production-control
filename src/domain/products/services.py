from uuid import UUID

from src.domain.products.value_objects import ProductCode
from src.domain.repositories.products import ProductRepositoryProtocol


async def validate_product_code_uniqueness(code: ProductCode, repository: ProductRepositoryProtocol) -> bool:
    """Проверяет уникальность кода продукта"""
    existing_product = await repository.get_by_unique_code(code.value)
    return existing_product is None


async def validate_all_products_aggregated(batch_id: UUID, repository: ProductRepositoryProtocol) -> bool:
    """Проверяет, что все продукты в партии агрегированы"""
    aggregated_products = await repository.get_aggregated()
    batch_aggregated = [p for p in aggregated_products if p.batch_id == batch_id]
    all_products_result = await repository.list(filters={"batch_id": batch_id})
    all_products = all_products_result.items
    return len(batch_aggregated) == len(all_products) and len(all_products) > 0
