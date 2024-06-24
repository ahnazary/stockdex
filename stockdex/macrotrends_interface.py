"""
Module for interfacing with the Macrotrends website.
"""

import re

import pandas as pd
from bs4 import BeautifulSoup

from stockdex.config import MACROTRENDS_BASE_URL, VALID_SECURITY_TYPES
from stockdex.lib import check_security_type
from stockdex.ticker_base import TickerBase


class MacrotrendsInterface(TickerBase):
    """
    Interface for interacting with the Macrotrends website.
    """

    def __init__(
        self,
        ticker: str = "",
        isin: str = "",
        security_type: VALID_SECURITY_TYPES = "stock",
    ) -> None:
        self.isin = isin
        self.ticker = ticker
        self.security_type = security_type

    @property
    def full_name(self) -> str:
        """
        Retrieve the full name of the security.
        """
        full_name = self.yahoo_web_full_name
        full_name = full_name.replace(" ", "-").lower()

        return full_name

    def _find_table_in_url(self, url: str, text_to_look_for: str) -> pd.DataFrame:
        """
        Retrieve the table with the given id from the given URL.

        Args:
        ----------
        url: str
            The URL to retrieve the table from.
        text_to_look_for: str
            The text to look for in the table.

        Returns:
        ----------
        pd.DataFrame
            The table as a pandas DataFrame.
        """
        response = self.get_response(url)

        # Parse the HTML content of the website
        soup = BeautifulSoup(response.content, "html.parser")

        table = self.find_parent_by_text(soup=soup, tag="div", text=text_to_look_for)

        data = []
        # get var originalData from the table
        for script in table.find_all("script"):
            if "originalData" in script.get_text():
                original_data = script.get_text()
                break

        # get the data from the script
        for line in original_data.split("\n"):
            if "originalData" in line:
                data = line.split(" = ")[1]
                break

        # convert the data to a pandas DataFrame
        data = data.replace(";", "")
        data = data.replace("null", "None")
        data = eval(data)
        data = pd.DataFrame(data)

        return data

    def macrotrends_income_statement(self) -> pd.DataFrame:
        """
        Retrieve the income statement for the given ticker.
        """
        check_security_type(self.security_type, valid_types=["stock"])
        url = f"{MACROTRENDS_BASE_URL}/{self.ticker}/TBD/income-statement"

        data = self._find_table_in_url(url, "Revenue")

        data["field_name"] = data["field_name"].apply(
            lambda x: re.search(">(.*)<", x).group(1)
        )
        data = data.set_index("field_name")
        data.drop(columns=["popup_icon"], inplace=True)

        return data
