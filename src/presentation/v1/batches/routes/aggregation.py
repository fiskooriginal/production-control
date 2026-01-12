from uuid import UUID

from fastapi import APIRouter, status

from src.infrastructure.background_tasks import states
from src.infrastructure.background_tasks.tasks import aggregate_batch as aggregate_batch_task
from src.presentation.v1.background_tasks.schemas import TaskStartedResponse
from src.presentation.v1.batches.di.commands import aggregate_batch
from src.presentation.v1.batches.mappers import aggregate_batch_request_to_input_dto, domain_to_response
from src.presentation.v1.batches.schemas.requests import AggregateBatchRequest, AggregateBatchTaskRequest
from src.presentation.v1.batches.schemas.responses import BatchResponse

router = APIRouter()


@router.patch("/{batch_id}/aggregate", response_model=BatchResponse, status_code=status.HTTP_202_ACCEPTED)
async def aggregate_batch(batch_id: UUID, request: AggregateBatchRequest, command: aggregate_batch) -> BatchResponse:
    """
    Агрегирует партию и все продукты в ней.
    """
    input_dto = aggregate_batch_request_to_input_dto(batch_id, request)
    batch_entity = await command.execute(input_dto)
    return domain_to_response(batch_entity)


@router.patch("/{batch_id}/aggregate_async", response_model=TaskStartedResponse, status_code=status.HTTP_202_ACCEPTED)
async def aggregate_batch_async(
    batch_id: UUID,
    request: AggregateBatchTaskRequest,
) -> TaskStartedResponse:
    """
    Запускает фоновую задачу для агрегации партии и продуктов в ней.

    Если указаны unique_codes, агрегируются только указанные продукты.
    Если unique_codes не указан, агрегируются все продукты партии.
    """
    aggregated_at_str = None
    if request.aggregated_at:
        aggregated_at_str = request.aggregated_at.isoformat()

    task = aggregate_batch_task.delay(
        batch_id=str(batch_id), unique_codes=request.unique_codes, aggregated_at=aggregated_at_str
    )

    return TaskStartedResponse(
        task_id=task.id,
        status=states.PENDING,
        message="Aggregation task started",
    )
