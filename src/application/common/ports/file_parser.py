from typing import Any, Protocol


class FileParserProtocol(Protocol):
    """Протокол для парсеров файлов импорта."""

    async def parse(self, file_data: bytes) -> list[dict[str, Any]]:
        """
        Парсит файл и возвращает список словарей с данными доменной сущности.

        Args:
            file_data: Байты файла для парсинга

        Returns:
            Список словарей с данными домаенной сущности

        Raises:
            FileParseError: При ошибке парсинга файла (неверная структура, формат)
        """
        ...
