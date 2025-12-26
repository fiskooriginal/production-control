from datetime import UTC, datetime


def utc_now(naive: bool = False) -> datetime:
    """Возвращает текущее UTC время (aware или naive)"""
    if naive:
        return datetime.now()
    return datetime.now(UTC)
