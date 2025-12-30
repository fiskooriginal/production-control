from dataclasses import dataclass

from src.application.batches.queries import BatchReadDTO
from src.core.time import datetime_now


@dataclass(frozen=True, slots=True, kw_only=True)
class ReportStatisticsDTO:
    total_products: int
    aggregated_products: int
    remaining_products: int
    completion_percentage: float
    average_speed: float


def calculate_statistics(batch: BatchReadDTO) -> ReportStatisticsDTO:
    """Вычисляет статистику для отчета на основе данных партии"""
    total_products = len(batch.products)
    aggregated_products = sum(1 for product in batch.products if product.is_aggregated)
    remaining_products = total_products - aggregated_products

    completion_percentage = (aggregated_products / total_products * 100.0) if total_products > 0 else 0.0

    # Вычисляем среднюю скорость (продуктов в час)
    end_time = batch.closed_at or datetime_now()

    time_delta = end_time - batch.shift_start
    hours_worked = time_delta.total_seconds() / 3600.0

    average_speed = aggregated_products / hours_worked if hours_worked > 0 else 0.0

    return ReportStatisticsDTO(
        total_products=total_products,
        aggregated_products=aggregated_products,
        remaining_products=remaining_products,
        completion_percentage=completion_percentage,
        average_speed=average_speed,
    )
