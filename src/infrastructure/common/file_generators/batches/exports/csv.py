import asyncio
import csv

from dataclasses import fields
from functools import partial
from io import StringIO

from src.application.batches.dtos.raw_data import BatchRawDataDTO
from src.application.batches.mappers import raw_data_dto_to_row
from src.core.logging import get_logger
from src.infrastructure.common.exceptions.batches import BatchExcelGenerationError

logger = get_logger("batches.export.csv")


class BatchesExportCsvGenerator:
    """Генератор CSV файлов для экспорта списка партий."""

    async def generate(self, raw_data: list[BatchRawDataDTO]) -> bytes:
        """
        Генерирует CSV файл со списком партий.

        Args:
            batches: Список партий для экспорта

        Returns:
            Байты сгенерированного CSV файла

        Raises:
            BatchExcelGenerationError: При ошибке генерации CSV
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, partial(self._generate_sync, raw_data))

    def _generate_sync(self, batches: list[BatchRawDataDTO]) -> bytes:
        """
        Синхронная генерация CSV файла.

        Args:
            batches: Список партий для экспорта

        Returns:
            Байты сгенерированного CSV файла

        Raises:
            BatchExcelGenerationError: При ошибке генерации CSV
        """
        try:
            output = StringIO()
            writer = csv.writer(output, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL)

            headers = [field.name for field in fields(BatchRawDataDTO)]
            writer.writerow(headers)

            for batch in batches:
                row = raw_data_dto_to_row(batch)
                writer.writerow(row)

            output.seek(0)
            result_bytes = output.getvalue().encode("utf-8-sig")

            logger.info(f"Сгенерирован CSV файл для экспорта {len(batches)} партий")
            return result_bytes
        except Exception as e:
            logger.error(f"Ошибка генерации CSV файла для экспорта: {e}")
            raise BatchExcelGenerationError(f"Ошибка генерации CSV файла для экспорта: {e}") from e
