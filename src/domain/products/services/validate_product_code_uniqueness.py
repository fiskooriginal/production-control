from uuid import UUID

from src.domain.products.interfaces.repository import ProductRepositoryProtocol
from src.domain.products.value_objects import ProductCode


async def validate_product_code_uniqueness(
    code: ProductCode, batch_id: UUID, repository: ProductRepositoryProtocol
) -> bool:
    """Проверяет уникальность кода продукта в рамках партии."""
    existing_product = await repository.get_by_unique_code(code.value, batch_id)
    return existing_product is None
