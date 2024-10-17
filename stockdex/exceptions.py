"""
Module for custom exceptions
"""

from stockdex.config import VALID_DATA_SOURCES


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


class WrongDataSource(Exception):
    """
    The exception to be shown when a method is called on the wrong data source
    """

    def __init__(
        self,
        given_source: str = None,
    ) -> None:
        self.given_source = given_source

    def __str__(self) -> str:
        return f"""
            Wrong data source has been used,
            make sure to use one of the following: {VALID_DATA_SOURCES}
            """


class FieldNotExists(Exception):
    """
    The exception to be shown when a field is called that does not exist in the dataframe
    """

    def __init__(
        self,
        available_fields: list,
        message: str = "Field does not exist",
        given_field: str = None,
    ) -> None:
        self.message = message
        self.given_field = given_field
        self.available_fields = available_fields
        super().__init__(self.message)

    def __str__(self) -> str:
        return f"""
            {self.message}. The field {self.given_field} does not exist in the dataframe.
            Make sure to choose a field from the following: {self.available_fields}
            """
