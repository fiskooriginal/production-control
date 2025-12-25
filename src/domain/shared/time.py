from datetime import UTC, datetime


def utc_now() -> datetime:
    """Возвращает текущее UTC время"""
    return datetime.now(UTC)
