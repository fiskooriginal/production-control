from uuid import UUID

from src.domain.products.interfaces.repository import ProductRepositoryProtocol


async def validate_all_products_aggregated(batch_id: UUID, repository: ProductRepositoryProtocol) -> bool:
    """Проверяет, что все продукты в партии агрегированы."""
    aggregated_products = await repository.get_aggregated()
    batch_aggregated = [p for p in aggregated_products if p.batch_id == batch_id]

    all_products_result = await repository.list(filters={"batch_id": batch_id})
    all_products = all_products_result.items

    return len(batch_aggregated) == len(all_products) and bool(all_products)
