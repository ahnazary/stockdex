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


class WrongSecurityType(Exception):
    """
    The exception to be shown when a method is called on the wrong security type
    """

    def __init__(
        self,
        message: str = "Wrong security type",
        valid_types: list = None,
        given_type: str = None,
    ) -> None:
        self.message = message
        self.valid_types = valid_types
        self.given_type = given_type
        super().__init__(self.message)

    def __str__(self) -> str:
        return f"""
            {self.message}. Wrong security type has been used,
            make sure to use one of the following: {self.valid_types}
            """
