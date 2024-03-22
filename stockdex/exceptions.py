"""
Module for custom exceptions
"""


class NoISINError(Exception):
    def __init__(self, message: str = "No ISIN provided") -> None:
        self.message = message
        super().__init__(self.message)

    def __str__(self) -> str:
        return self.message


class NoDataError(Exception):
    def __init__(self, message: str = "No data found") -> None:
        self.message = message
        super().__init__(self.message)

    def __str__(self) -> str:
        return self.message
