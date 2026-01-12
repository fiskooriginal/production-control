from dataclasses import dataclass


@dataclass
class ImportBatchesInputDTO:
    minio_file_path: str
    update_existing: bool


@dataclass
class ImportBatchesOutputDTO:
    total: int
    created: int
    updated: int
    failed: int
    errors: list


@dataclass
class ImportRowResult:
    created: bool
    updated: bool
    error: str | None
