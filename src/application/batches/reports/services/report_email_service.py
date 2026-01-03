from datetime import datetime
from uuid import UUID

from src.application.batches.queries.service import BatchQueryServiceProtocol
from src.application.batches.reports.adapters import ReportStorageAdapter
from src.application.batches.reports.dtos import ReportFormatEnum
from src.application.common.email.interfaces import EmailServiceProtocol
from src.core.logging import get_logger
from src.domain.batches import BatchEntity

logger = get_logger("service.reports.email_service")


class ReportEmailService:
    """Сервис для отправки email-уведомлений с отчетами"""

    def __init__(
        self,
        email_service: EmailServiceProtocol | None,
        report_storage: ReportStorageAdapter,
        batch_query_service: BatchQueryServiceProtocol | None = None,
    ) -> None:
        self._email_service = email_service
        self._report_storage = report_storage
        self._batch_query_service = batch_query_service

    def _format_datetime_for_filename(self, dt: datetime) -> str:
        """Форматирует datetime для использования в имени файла"""
        return dt.strftime("%Y-%m-%d_%H-%M")

    def _get_attachment_filename(self, batch: BatchEntity, format: ReportFormatEnum) -> str:
        """Формирует имя файла-вложения"""
        start_str = self._format_datetime_for_filename(batch.shift_time_range.start)
        end_str = self._format_datetime_for_filename(batch.shift_time_range.end)
        extension = format.value
        return f"Отчёт о партии с {start_str} по {end_str}.{extension}"

    def _get_content_type(self, format: ReportFormatEnum) -> str:
        """Возвращает MIME-тип для формата отчета"""
        return (
            "application/pdf"
            if format == ReportFormatEnum.PDF
            else "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    async def send_email(self, user_email: str, batch_id: UUID, format: ReportFormatEnum, report_path: str) -> None:
        """
        Отправляет email-уведомление с прикрепленным файлом отчета.

        Args:
            user_email: Email адрес получателя
            batch_id: ID партии
            format: Формат отчета
            report_path: Путь к файлу отчета в хранилище

        Raises:
            ValueError: Если email сервис не настроен или партия не найдена
        """
        if not self._email_service:
            logger.warning(f"Email service is not available, skipping email notification for batch {batch_id}")
            return

        if not self._batch_query_service:
            logger.warning(f"BatchQueryService is not available, cannot send email notification for batch {batch_id}")
            return

        batch = await self._batch_query_service.get(batch_id)
        if not batch:
            logger.warning(f"Batch {batch_id} not found, cannot send email notification")
            return

        try:
            report_content = await self._report_storage.download_report(report_path)
            attachment_filename = self._get_attachment_filename(batch, format)
            content_type = self._get_content_type(format)

            start_str = batch.shift_time_range.start.strftime("%d.%m.%Y %H:%M")
            end_str = batch.shift_time_range.end.strftime("%d.%m.%Y %H:%M")

            subject = f"Отчет о партии {batch_id!s}"
            body = (
                f"Отчет о партии успешно сгенерирован.\n\n"
                f"ID партии: {batch_id!s}\n"
                f"Формат отчета: {format.value.upper()}\n"
                f"Временной диапазон смены: с {start_str} по {end_str}\n\n"
                f"Файл отчета прикреплен к письму."
            )

            await self._email_service.send_email(
                to=user_email,
                subject=subject,
                body=body,
                attachments=[(attachment_filename, report_content, content_type)],
            )
            logger.info(f"Email notification sent successfully to {user_email} for batch {batch_id}")
        except Exception as e:
            logger.exception(f"Failed to send email notification for batch {batch_id}: {e}")
