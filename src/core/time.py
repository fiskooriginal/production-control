from datetime import UTC, datetime


def datetime_now(naive: bool = False) -> datetime:
    """Возвращает текущее UTC время (aware или naive)"""
    if naive:
        return datetime.now()
    return datetime.now(UTC)


def datetime_naive_to_aware(dt: datetime | None) -> datetime | None:
    """Конвертирует naive datetime в aware (UTC)"""
    if dt is None:
        return None
    if dt.tzinfo is not None:
        return dt
    return dt.replace(tzinfo=UTC)


def datetime_aware_to_naive(dt: datetime | None) -> datetime | None:
    """Конвертирует aware datetime в naive (предполагая UTC)"""
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt
    return dt.replace(tzinfo=None)
