import json

from dataclasses import asdict
from datetime import datetime

from dacite import Config, from_dict
from dacite.data import Data

from src.application.analytics.queries.dtos import DashboardStatisticsDTO
from src.core.time import datetime_naive_to_aware
from src.infrastructure.common.exceptions import MappingException


def dict_to_dto(data: Data | dict) -> DashboardStatisticsDTO:
    def str_to_datetime(value: str) -> datetime:
        dt = datetime.fromisoformat(value)
        return datetime_naive_to_aware(dt) if dt.tzinfo is None else dt

    config = Config(
        type_hooks={datetime: str_to_datetime},
    )
    return from_dict(DashboardStatisticsDTO, data, config=config)


def dto_to_json_bytes(data: DashboardStatisticsDTO) -> bytes:
    """Сериализует DashboardStatisticsDTO в JSON bytes."""
    try:
        dto_dict = asdict(data)
        json_str = json.dumps(dto_dict, default=str)
        return json_str.encode("utf-8")
    except Exception as e:
        raise MappingException(f"Ошибка маппинга DTO -> JSON bytes для DashboardStatistics: {e}") from e


def json_bytes_to_dto(data: bytes) -> DashboardStatisticsDTO:
    """Десериализует JSON bytes в DashboardStatisticsDTO."""
    try:
        json_str = data.decode("utf-8")
        data_dict = json.loads(json_str)
        return dict_to_dto(data_dict)
    except Exception as e:
        raise MappingException(f"Ошибка маппинга JSON bytes -> DTO для DashboardStatistics: {e}") from e
