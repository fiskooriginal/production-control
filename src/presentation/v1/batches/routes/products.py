from uuid import UUID

from fastapi import APIRouter

from src.presentation.v1.batches.di.commands import add_product_to_batch, remove_product_from_batch
from src.presentation.v1.batches.mappers import domain_to_response
from src.presentation.v1.batches.schemas.requests import AddProductToBatchRequest
from src.presentation.v1.batches.schemas.responses import BatchResponse

router = APIRouter()


@router.post("/{batch_id}/products", response_model=BatchResponse)
async def add_product_to_batch(
    batch_id: UUID, request: AddProductToBatchRequest, command: add_product_to_batch
) -> BatchResponse:
    """
    Добавляет продукт в партию.
    """
    batch_entity = await command.execute(batch_id, request.unique_code)
    return domain_to_response(batch_entity)


@router.delete("/{batch_id}/products/{product_id}", response_model=BatchResponse)
async def remove_product_from_batch(
    batch_id: UUID, product_id: UUID, command: remove_product_from_batch
) -> BatchResponse:
    """
    Удаляет продукт из партии.

    ВАЖНО: Продукт будет полностью удален из БД, так как batch_id NOT NULL.
    """
    batch_entity = await command.execute(batch_id, product_id)
    return domain_to_response(batch_entity)
