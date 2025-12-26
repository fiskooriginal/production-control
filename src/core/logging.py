import logging
import sys
from typing import Any


def setup_logging(level: str = "INFO") -> None:
    """
    Настраивает централизованное логирование для всего приложения.

    Args:
        level: Уровень логирования (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    log_level = getattr(logging, level.upper(), logging.INFO)

    formatter = logging.Formatter(
        fmt="%(asctime)s %(levelname)-8s [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.handlers.clear()
    root_logger.addHandler(handler)

    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.pool").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    Возвращает логгер с указанным именем.

    Args:
        name: Имя логгера (обычно __name__ модуля)

    Returns:
        Настроенный логгер
    """
    return logging.getLogger(name)


def log_dict(logger: logging.Logger, level: int, message: str, data: dict[str, Any]) -> None:
    """
    Логирует сообщение с дополнительными данными в виде словаря.

    Args:
        logger: Логгер для вывода
        level: Уровень логирования
        message: Основное сообщение
        data: Дополнительные данные для логирования
    """
    data_str = " ".join(f"{k}={v}" for k, v in data.items())
    logger.log(level, f"{message} {data_str}")
