from typing import ClassVar

from src.application.common.ports.file_parser import FileParserProtocol
from src.infrastructure.common.file_parsers.csv import CsvFileParser
from src.infrastructure.common.file_parsers.xlsx import XlsxFileParser


class FileParserFactory:
    """
    Фабрика для создания парсеров файлов на основе расширения файла.
    """

    _parsers: ClassVar[dict[str, type[FileParserProtocol]]] = {
        "xlsx": XlsxFileParser,
        "csv": CsvFileParser,
    }

    @classmethod
    def create(cls, file_extension: str) -> FileParserProtocol:
        """
        Создает парсер на основе расширения файла.

        Args:
            file_extension: Расширение файла (xlsx, csv)

        Returns:
            Экземпляр парсера, реализующий FileParserProtocol

        Raises:
            ValueError: Если формат файла не поддерживается
        """
        extension_lower = file_extension.lower().lstrip(".")

        parser_class = cls._parsers.get(extension_lower)
        if parser_class is None:
            supported_formats = ", ".join(cls._parsers.keys())
            raise ValueError(f"Неподдерживаемый формат файла: {file_extension}. Поддерживаются: {supported_formats}")

        return parser_class()
