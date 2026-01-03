import asyncio
import csv

from io import BytesIO, TextIOWrapper

from src.application.common.exceptions.file_parser import FileParseError
from src.application.common.ports.file_parser import FileParserProtocol


class CsvFileParser(FileParserProtocol):
    """
    Парсер для CSV файлов.

    Использует стандартную библиотеку csv для чтения CSV файлов.
    Работает в асинхронном режиме через executor для блокирующих операций.
    """

    def __init__(self, delimiter: str = ",", encoding: str = "utf-8-sig"):
        """
        Инициализирует CSV парсер.

        Args:
            delimiter: Разделитель полей в CSV файле (по умолчанию запятая)
            encoding: Кодировка файла (по умолчанию UTF-8)
        """
        self._delimiter = delimiter
        self._encoding = encoding

    async def parse(self, file_data: bytes) -> list[dict[str, str]]:
        """
        Парсит CSV файл и возвращает список словарей с данными.

        Args:
            file_data: Байты CSV файла

        Returns:
            Список словарей, где каждый словарь представляет строку данных.
            Ключи словаря - это значения из первой строки (заголовки).

        Raises:
            FileParseError: При ошибке парсинга файла
        """
        try:
            return await asyncio.to_thread(self._parse_sync, file_data)
        except FileParseError:
            raise
        except Exception as e:
            raise FileParseError(f"Ошибка парсинга CSV файла: {e}") from e

    def _parse_sync(self, file_data: bytes) -> list[dict[str, str]]:
        """
        Синхронный метод парсинга CSV файла.

        Args:
            file_data: Байты CSV файла

        Returns:
            Список словарей с данными

        Raises:
            FileParseError: При ошибке парсинга
        """
        try:
            file_stream = BytesIO(file_data)
            text_stream = TextIOWrapper(file_stream, encoding=self._encoding)

            reader = csv.DictReader(text_stream, delimiter=self._delimiter)

            result = []
            for row in reader:
                if not row or all(not value for value in row.values()):
                    continue

                result.append(dict(row))

            text_stream.close()
            return result

        except UnicodeDecodeError as e:
            raise FileParseError(f"Ошибка декодирования CSV файла (кодировка: {self._encoding}): {e}") from e
        except csv.Error as e:
            raise FileParseError(f"Ошибка парсинга CSV файла: {e}") from e
        except Exception as e:
            raise FileParseError(f"Ошибка чтения CSV файла: {e}") from e
