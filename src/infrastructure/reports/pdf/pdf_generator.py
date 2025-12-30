from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from src.application.batches.reports.dtos import BatchReportDataDTO
from src.core.logging import get_logger
from src.infrastructure.reports.exceptions import BatchPDFGenerationError

logger = get_logger("batches.reports.pdf")


class BatchPDFReportGenerator:
    """Генератор PDF отчетов для батчей."""

    def generate(self, batch_data: BatchReportDataDTO) -> bytes:
        """
        Генерирует PDF отчет для батча.

        Args:
            batch_data: Данные для генерации отчета

        Returns:
            Байты сгенерированного PDF файла

        Raises:
            BatchPDFGenerationError: При ошибке генерации PDF
        """
        try:
            if not batch_data:
                raise BatchPDFGenerationError("batch_data не может быть None")

            buffer = BytesIO()
            doc = SimpleDocTemplate(
                buffer, pagesize=A4, rightMargin=2 * cm, leftMargin=2 * cm, topMargin=2 * cm, bottomMargin=2 * cm
            )
            story = []

            styles = getSampleStyleSheet()

            self._create_header(story, batch_data, styles)
            story.append(Spacer(1, 0.5 * cm))

            self._create_products_table(story, batch_data, styles)
            story.append(Spacer(1, 0.5 * cm))

            self._create_statistics_section(story, batch_data, styles)

            doc.build(story)
            buffer.seek(0)

            result_bytes = buffer.getvalue()

            logger.info(f"Сгенерирован PDF отчет для партии {batch_data.batch.batch_number}")
            return result_bytes
        except BatchPDFGenerationError:
            raise
        except Exception as e:
            logger.error(f"Ошибка генерации PDF отчета: {e}")
            raise BatchPDFGenerationError(f"Ошибка генерации PDF отчета: {e}") from e

    @staticmethod
    def _create_header(story: list, batch_data: BatchReportDataDTO, styles: dict) -> None:
        """Создает заголовок с информацией о партии."""
        batch = batch_data.batch

        title_style = styles["Heading1"]
        title_style.textColor = colors.HexColor("#4472C4")
        story.append(Paragraph("Информация о партии", title_style))
        story.append(Spacer(1, 0.3 * cm))

        data = [
            ("Номер партии", str(batch.batch_number)),
            ("Дата партии", batch.batch_date.strftime("%d.%m.%Y")),
            ("Номенклатура", batch.nomenclature),
            ("Код ЕКН", batch.ekn_code),
            ("Смена", batch.shift),
            ("Бригада", batch.team),
        ]

        if batch_data.work_center_name:
            data.append(("Рабочий центр", batch_data.work_center_name))

        data.extend(
            [
                ("Описание задачи", batch.task_description),
                ("Начало смены", batch.shift_start.strftime("%d.%m.%Y %H:%M")),
                ("Конец смены", batch.shift_end.strftime("%d.%m.%Y %H:%M")),
                ("Статус", "Закрыта" if batch.is_closed else "Открыта"),
            ]
        )

        if batch.closed_at:
            data.append(("Дата закрытия", batch.closed_at.strftime("%d.%m.%Y %H:%M")))

        table_data = [["Параметр", "Значение"]]
        for key, value in data:
            table_data.append([key, value])

        table = Table(table_data, colWidths=[5 * cm, 12 * cm])
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4472C4")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 11),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                    ("BACKGROUND", (0, 1), (0, -1), colors.HexColor("#E7E6E6")),
                    ("FONTNAME", (0, 1), (0, -1), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 1), (0, -1), 10),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 6),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                    ("TOPPADDING", (0, 0), (-1, -1), 6),
                    ("BOTTOMPADDING", (0, 1), (-1, -1), 6),
                ]
            )
        )

        story.append(table)

    @staticmethod
    def _create_products_table(story: list, batch_data: BatchReportDataDTO, styles: dict) -> None:
        """Создает таблицу продукции."""
        batch = batch_data.batch

        title_style = styles["Heading1"]
        title_style.textColor = colors.HexColor("#4472C4")
        story.append(Paragraph("Продукция", title_style))
        story.append(Spacer(1, 0.3 * cm))

        table_data = [["ID", "Уникальный код", "Аггрегирована", "Дата аггрегации"]]

        for product in batch.products:
            aggregated_value = "Да" if product.is_aggregated else "Нет"
            aggregated_date = product.aggregated_at.strftime("%d.%m.%Y %H:%M") if product.aggregated_at else ""
            table_data.append([str(product.uuid), product.unique_code, aggregated_value, aggregated_date])

        table = Table(table_data, colWidths=[5 * cm, 4 * cm, 3 * cm, 5 * cm])
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4472C4")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, 0), "CENTER"),
                    ("ALIGN", (0, 1), (0, -1), "LEFT"),
                    ("ALIGN", (1, 1), (1, -1), "LEFT"),
                    ("ALIGN", (2, 1), (2, -1), "CENTER"),
                    ("ALIGN", (3, 1), (3, -1), "LEFT"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 11),
                    ("FONTSIZE", (0, 1), (-1, -1), 9),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 6),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                    ("TOPPADDING", (0, 0), (-1, -1), 6),
                    ("BOTTOMPADDING", (0, 1), (-1, -1), 6),
                ]
            )
        )

        story.append(table)

    @staticmethod
    def _create_statistics_section(story: list, batch_data: BatchReportDataDTO, styles: dict) -> None:
        """Создает блок статистики."""
        stats = batch_data.statistics

        title_style = styles["Heading1"]
        title_style.textColor = colors.HexColor("#4472C4")
        story.append(Paragraph("Статистика", title_style))
        story.append(Spacer(1, 0.3 * cm))

        data = [
            ("Всего продукции", str(stats.total_products)),
            ("Аггрегировано", str(stats.aggregated_products)),
            ("Осталось", str(stats.remaining_products)),
            ("Процент выполнения", f"{stats.completion_percentage:.2f}%"),
            ("Средняя скорость (продуктов/час)", f"{stats.average_speed:.2f}"),
        ]

        table_data = [["Параметр", "Значение"]]
        for key, value in data:
            table_data.append([key, value])

        table = Table(table_data, colWidths=[8 * cm, 9 * cm])
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4472C4")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("ALIGN", (1, 1), (1, -1), "RIGHT"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 11),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                    ("BACKGROUND", (0, 1), (0, -1), colors.HexColor("#E7E6E6")),
                    ("FONTNAME", (0, 1), (0, -1), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 1), (0, -1), 10),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 6),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                    ("TOPPADDING", (0, 0), (-1, -1), 6),
                    ("BOTTOMPADDING", (0, 1), (-1, -1), 6),
                ]
            )
        )

        story.append(table)
