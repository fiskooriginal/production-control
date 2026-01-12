from typing import Any, Protocol


class FileGeneratorProtocol(Protocol):
    """Протокол для генераторов файлов экспорта."""

    async def generate(
        self,
        raw_data: list[Any],
    ) -> bytes:
        """
        Генерирует файл экспорта с данными.

        Args:
            raw_data: Список данных для экспорта

        Returns:
            Байты сгенерированного файла

        Raises:
            FileGenerationError: При ошибке генерации файла
        """
        ...
