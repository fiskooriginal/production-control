from datetime import date
from uuid import UUID

from src.application.batches.queries.filters import BatchReadFilters
from src.application.batches.queries.queries import ListBatchesQuery
from src.application.batches.queries.sort import BatchSortField, BatchSortSpec
from src.application.products.queries.queries import ListProductsQuery
from src.application.products.queries.sort import ProductSortField, ProductSortSpec
from src.application.webhooks.queries.filters import WebhookReadFilters
from src.application.webhooks.queries.queries import ListWebhookDeliveriesQuery, ListWebhookSubscriptionsQuery
from src.application.work_centers.queries.filters import WorkCenterReadFilters
from src.application.work_centers.queries.queries import ListWorkCentersQuery
from src.application.work_centers.queries.sort import WorkCenterSortField, WorkCenterSortSpec
from src.domain.common.queries import PaginationSpec
from src.presentation.api.schemas.batches import BatchFiltersParams
from src.presentation.api.schemas.query_params import PaginationParams, SortParams
from src.presentation.api.schemas.webhooks import WebhookFiltersParams
from src.presentation.api.schemas.work_centers import WorkCenterFiltersParams
from src.presentation.exceptions import SerializationException


def pagination_params_to_spec(params: PaginationParams) -> PaginationSpec | None:
    """Конвертирует PaginationParams в PaginationSpec"""
    try:
        if params.limit is not None and params.offset is not None:
            return PaginationSpec(limit=params.limit, offset=params.offset)
        return None
    except Exception as e:
        raise SerializationException(f"Ошибка сериализации PaginationParams: {e}") from e


def work_center_filters_params_to_query(params: WorkCenterFiltersParams) -> WorkCenterReadFilters | None:
    """Конвертирует WorkCenterFiltersParams в WorkCenterReadFilters"""
    try:
        if params.identifier:
            return WorkCenterReadFilters(identifier=params.identifier)
        return None
    except Exception as e:
        raise SerializationException(f"Ошибка сериализации WorkCenterFiltersParams: {e}") from e


def batch_filters_params_to_query(params: BatchFiltersParams) -> BatchReadFilters | None:
    """Конвертирует BatchFiltersParams в BatchReadFilters"""
    try:
        filter_dict = {}

        if params.is_closed is not None:
            filter_dict["is_closed"] = params.is_closed

        if params.batch_number is not None:
            filter_dict["batch_number"] = params.batch_number

        if params.batch_date:
            filter_dict["batch_date"] = date.fromisoformat(params.batch_date)

        if params.batch_date_from:
            filter_dict["batch_date_from"] = date.fromisoformat(params.batch_date_from)

        if params.batch_date_to:
            filter_dict["batch_date_to"] = date.fromisoformat(params.batch_date_to)

        if params.work_center_id:
            filter_dict["work_center_id"] = UUID(params.work_center_id)

        if params.shift:
            filter_dict["shift"] = params.shift

        return BatchReadFilters(**filter_dict) if filter_dict else None
    except Exception as e:
        raise SerializationException(f"Ошибка сериализации BatchFiltersParams: {e}") from e


def sort_params_to_work_center_sort_spec(params: SortParams) -> WorkCenterSortSpec | None:
    """Конвертирует SortParams в WorkCenterSortSpec"""
    try:
        if params.sort_field and params.sort_direction:
            try:
                sort_field = WorkCenterSortField(params.sort_field)
            except ValueError as ve:
                raise SerializationException(
                    f"Недопустимое поле сортировки для work_centers: {params.sort_field}. "
                    f"Допустимые значения: {', '.join([f.value for f in WorkCenterSortField])}"
                ) from ve
            return WorkCenterSortSpec(field=sort_field, direction=params.sort_direction)
        return None
    except SerializationException:
        raise
    except Exception as e:
        raise SerializationException(f"Ошибка сериализации SortParams: {e}") from e


def sort_params_to_batch_sort_spec(params: SortParams) -> BatchSortSpec | None:
    """Конвертирует SortParams в BatchSortSpec"""
    try:
        if params.sort_field and params.sort_direction:
            try:
                sort_field = BatchSortField(params.sort_field)
            except ValueError as ve:
                raise SerializationException(
                    f"Недопустимое поле сортировки для batches: {params.sort_field}. "
                    f"Допустимые значения: {', '.join([f.value for f in BatchSortField])}"
                ) from ve
            return BatchSortSpec(field=sort_field, direction=params.sort_direction)
        return None
    except SerializationException:
        raise
    except Exception as e:
        raise SerializationException(f"Ошибка сериализации SortParams: {e}") from e


def sort_params_to_product_sort_spec(params: SortParams) -> ProductSortSpec | None:
    """Конвертирует SortParams в ProductSortSpec"""
    try:
        if params.sort_field and params.sort_direction:
            try:
                sort_field = ProductSortField(params.sort_field)
            except ValueError as ve:
                raise SerializationException(
                    f"Недопустимое поле сортировки для products: {params.sort_field}. "
                    f"Допустимые значения: {', '.join([f.value for f in ProductSortField])}"
                ) from ve
            return ProductSortSpec(field=sort_field, direction=params.sort_direction)
        return None
    except SerializationException:
        raise
    except Exception as e:
        raise SerializationException(f"Ошибка сериализации SortParams: {e}") from e


def build_list_work_centers_query(
    filter_params: WorkCenterFiltersParams,
    pagination_params: PaginationParams,
    sort_params: SortParams,
) -> ListWorkCentersQuery:
    """Создает ListWorkCentersQuery из параметров запроса"""
    filters = work_center_filters_params_to_query(filter_params)
    pagination = pagination_params_to_spec(pagination_params)
    sort = sort_params_to_work_center_sort_spec(sort_params)

    return ListWorkCentersQuery(filters=filters, pagination=pagination, sort=sort)


def build_list_batches_query(
    filter_params: BatchFiltersParams,
    pagination_params: PaginationParams,
    sort_params: SortParams,
) -> ListBatchesQuery:
    """Создает ListBatchesQuery из параметров запроса"""
    filters = batch_filters_params_to_query(filter_params)
    pagination = pagination_params_to_spec(pagination_params)
    sort = sort_params_to_batch_sort_spec(sort_params)

    return ListBatchesQuery(filters=filters, pagination=pagination, sort=sort)


def build_list_products_query(
    pagination_params: PaginationParams,
    sort_params: SortParams,
) -> ListProductsQuery:
    """Создает ListProductsQuery из параметров запроса"""
    pagination = pagination_params_to_spec(pagination_params)
    sort = sort_params_to_product_sort_spec(sort_params)

    return ListProductsQuery(pagination=pagination, sort=sort)


def webhook_filters_params_to_query(params: WebhookFiltersParams) -> WebhookReadFilters | None:
    """Конвертирует WebhookFiltersParams в WebhookReadFilters"""
    try:
        if params.event_type is not None:
            return WebhookReadFilters(event_type=params.event_type)
        return None
    except Exception as e:
        raise SerializationException(f"Ошибка сериализации WebhookFiltersParams: {e}") from e


def build_list_webhook_subscriptions_query(
    filter_params: WebhookFiltersParams,
    pagination_params: PaginationParams,
) -> ListWebhookSubscriptionsQuery:
    """Создает ListWebhookSubscriptionsQuery из параметров запроса"""
    filters = webhook_filters_params_to_query(filter_params)
    pagination = pagination_params_to_spec(pagination_params)

    return ListWebhookSubscriptionsQuery(filters=filters, pagination=pagination)


def build_list_webhook_deliveries_query(
    subscription_id: UUID,
    pagination_params: PaginationParams,
) -> ListWebhookDeliveriesQuery:
    """Создает ListWebhookDeliveriesQuery из параметров запроса"""
    pagination = pagination_params_to_spec(pagination_params)

    return ListWebhookDeliveriesQuery(subscription_id=subscription_id, pagination=pagination)
