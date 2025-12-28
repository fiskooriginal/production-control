from typing import Protocol


class CacheServiceProtocol(Protocol):
    async def get(self, key: str) -> bytes | None:
        """Получает значение по ключу. Возвращает None при ошибке."""
        ...

    async def set(self, key: str, value: bytes, ttl: int | None = None) -> None:
        """Устанавливает значение с опциональным TTL. Молча игнорирует ошибки."""
        ...

    async def delete(self, key: str) -> None:
        """Удаляет значение по ключу. Молча игнорирует ошибки."""
        ...

    async def delete_pattern(self, pattern: str) -> None:
        """Удаляет все ключи по паттерну. Молча игнорирует ошибки."""
        ...
