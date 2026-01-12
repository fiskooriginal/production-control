from typing import ClassVar

from src.application.common.ports.file_generator import FileGeneratorProtocol
from src.infrastructure.common.file_generators.batches.exports.csv import BatchesExportCsvGenerator
from src.infrastructure.common.file_generators.batches.exports.xlsx import BatchesExportExcelGenerator


class BatchesExportGeneratorFactory:
    """
    Фабрика для создания генераторов файлов экспорта партий на основе формата файла.
    """

    _generators: ClassVar[dict[str, type[FileGeneratorProtocol]]] = {
        "xlsx": BatchesExportExcelGenerator,
        "csv": BatchesExportCsvGenerator,
    }

    @classmethod
    def create(cls, file_format: str) -> FileGeneratorProtocol:
        """
        Создает генератор на основе формата файла.

        Args:
            file_format: Формат файла (xlsx, csv)

        Returns:
            Экземпляр генератора, реализующий FileGeneratorProtocol

        Raises:
            ValueError: Если формат файла не поддерживается
        """
        format_lower = file_format.lower().lstrip(".")

        generator_class = cls._generators.get(format_lower)
        if generator_class is None:
            supported_formats = ", ".join(cls._generators.keys())
            raise ValueError(f"Неподдерживаемый формат файла: {file_format}. Поддерживаются: {supported_formats}")

        return generator_class()
