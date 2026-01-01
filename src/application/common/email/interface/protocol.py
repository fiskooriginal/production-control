from typing import Protocol


class EmailServiceProtocol(Protocol):
    """Протокол для сервиса отправки email."""

    async def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        html_body: str | None = None,
        attachments: list[tuple[str, bytes, str]] | None = None,
    ) -> None:
        """
        Отправляет email.

        Args:
            to: Email адрес получателя
            subject: Тема письма
            body: Текст письма (plain text)
            html_body: HTML версия письма (опционально)
            attachments: Список вложений в формате (имя файла, содержимое, MIME-тип)

        Raises:
            EmailError: При ошибке отправки
        """
        ...
