class DomainException(Exception):
    """Базовое исключение для доменных ошибок"""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)
