def _get_content_type(file_extension: str | None = None) -> str:
    """
    Определить Content-Type по расширению файла.

    Args:
        file_extension: Расширение файла (например, ".xlsx" или "xlsx")

    Returns:
        MIME-тип файла
    """
    if file_extension is None:
        return "application/octet-stream"

    ext = file_extension.lower()
    if not ext.startswith("."):
        ext = f".{ext}"

    content_types = {
        ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        ".xls": "application/vnd.ms-excel",
        ".csv": "text/csv",
        ".pdf": "application/pdf",
        ".json": "application/json",
    }

    return content_types.get(ext, "application/octet-stream")
