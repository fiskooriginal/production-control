from src.application.products.queries import ProductReadDTO
from src.infrastructure.persistence.models.product import Product


def product_model_to_read_dto(model: Product) -> ProductReadDTO:
    """Преобразует модель SQLAlchemy в ProductReadDTO"""
    return ProductReadDTO(
        uuid=model.uuid,
        created_at=model.created_at,
        updated_at=model.updated_at,
        unique_code=model.unique_code,
        batch_id=model.batch_id,
        is_aggregated=model.is_aggregated,
        aggregated_at=model.aggregated_at,
    )
