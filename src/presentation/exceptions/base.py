class PresentationException(Exception):
    """Базовое исключение для ошибок уровня представления"""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)
