from typing import Protocol
from uuid import UUID


class ReportStorageProtocol(Protocol):
    """Протокол для хранения отчетов"""

    async def save_report(self, batch_id: UUID, content: bytes, format: str) -> str:
        """Сохраняет отчет и возвращает путь к файлу"""
        ...

    async def get_report_path(self, batch_id: UUID, format: str) -> str | None:
        """Получает путь к последнему отчету для партии и формата"""
        ...

    async def delete_report(self, batch_id: UUID, format: str) -> None:
        """Удаляет отчет для партии и формата"""
        ...
