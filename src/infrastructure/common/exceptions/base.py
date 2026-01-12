class InfrastructureException(Exception):
    """Базовое исключение для ошибок уровня инфраструктуры"""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)
