from dataclasses import dataclass


@dataclass
class FileInfo:
    """Информация о файле в хранилище."""

    name: str
    size: int
    last_modified: str
    etag: str | None = None
