class ApplicationException(Exception):
    """Базовое исключение для ошибок уровня приложения"""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)
