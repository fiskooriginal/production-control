from email.message import EmailMessage

import aiosmtplib

from src.application.common.email.interfaces import EmailServiceProtocol
from src.core.logging import get_logger
from src.core.settings import EmailSettings
from src.infrastructure.common.email.exceptions import EmailConfigurationError, EmailConnectionError, EmailSendError

logger = get_logger("email.smtp")


class SMTPEmailService(EmailServiceProtocol):
    """Сервис для отправки email через SMTP."""

    def __init__(self, email_settings: EmailSettings):
        if not email_settings.is_configured():
            raise EmailConfigurationError(
                "Email service is not configured. "
                "Please set SMTP_HOST, SMTP_USER, and SMTP_PASSWORD environment variables.",
            )
        self._settings = email_settings

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
            EmailSendError: При ошибке отправки
            EmailConnectionError: При ошибке подключения к SMTP серверу
        """
        if not self._settings.host:
            raise EmailConfigurationError("SMTP_HOST is not configured")

        message = EmailMessage()
        message["From"] = self._settings.from_email or self._settings.user
        message["To"] = to
        message["Subject"] = subject

        if html_body:
            message.set_content(body)
            message.add_alternative(html_body, subtype="html")
        else:
            message.set_content(body)

        if attachments:
            for filename, content, content_type in attachments:
                if "/" in content_type:
                    maintype, subtype = content_type.split("/", 1)
                else:
                    maintype = content_type
                    subtype = ""
                message.add_attachment(content, filename=filename, maintype=maintype, subtype=subtype)

        try:
            async with aiosmtplib.SMTP(
                hostname=self._settings.host,
                port=self._settings.port,
                use_tls=self._settings.use_tls,
                start_tls=not self._settings.use_tls,
            ) as smtp:
                if self._settings.user and self._settings.password:
                    await smtp.login(self._settings.user, self._settings.password)

                await smtp.send_message(message)
                logger.info(f"Email sent successfully to {to} with subject: {subject}")
        except aiosmtplib.SMTPException as e:
            logger.error(f"Failed to send email to {to}: {e}")
            raise EmailSendError(f"Failed to send email to {to}: {e}") from e
        except (ConnectionError, OSError) as e:
            logger.error(f"Failed to connect to SMTP server {self._settings.host}:{self._settings.port}: {e}")
            raise EmailConnectionError(
                f"Failed to connect to SMTP server {self._settings.host}:{self._settings.port}: {e}",
            ) from e
        except Exception as e:
            logger.error(f"Unexpected error while sending email to {to}: {e}")
            raise EmailSendError(f"Unexpected error while sending email to {to}: {e}") from e
