"""
Module for fetching data from Yahoo Finance website
"""

import pandas as pd
from bs4 import BeautifulSoup

from stockdex.config import VALID_SECURITY_TYPES
from stockdex.lib import check_security_type
from stockdex.ticker_base import TickerBase


class YahooWeb(TickerBase):
    def __init__(
        self,
        ticker: str = "",
        isin: str = "",
        security_type: VALID_SECURITY_TYPES = "stock",
    ) -> None:
        self.isin = isin
        self.ticker = ticker
        self.security_type = security_type

    def get_financials_table(self, url: str) -> pd.DataFrame:
        """
        Get financials table from the Yahoo Finance website

        Args:
        url (str): URL of the Yahoo Finance website

        Returns:
        pd.DataFrame: A pandas DataFrame including the financials table
        """
        response = self.get_response(url)
        soup = BeautifulSoup(response.content, "html.parser")

        raw_data = soup.find("div", {"class": "table svelte-1pgoo1f"})

        data_df = pd.DataFrame()

        headers = [
            item.text
            for item in raw_data.find("div", {"class": "row svelte-1ezv2n5"}).find_all(
                "div"
            )
        ]
        data_df = pd.DataFrame(columns=headers)
        rows = raw_data.find_all("div", {"class": "row lv-0 svelte-1xjz32c"})

        for row in rows:
            data = [item.text for item in row.find_all("div")][-len(headers) :]  # noqa
            data_df.loc[len(data_df)] = data

        return data_df.set_index("Breakdown").T

    @property
    def cashflow_web(self) -> pd.DataFrame:
        """
        Get cash flow for the ticker

        Returns:
        pd.DataFrame: A pandas DataFrame including the cash flow
        visible in the Yahoo Finance statistics page for the ticker
        """
        check_security_type(security_type=self.security_type, valid_types=["stock"])

        # URL of the website to scrape
        url = f"https://finance.yahoo.com/quote/{self.ticker}/cash-flow"
        return self.get_financials_table(url)

    @property
    def balance_sheet_web(self) -> pd.DataFrame:
        """
        Get balance sheet for the ticker

        Returns:
        pd.DataFrame: A pandas DataFrame including the balance sheet
        visible in the Yahoo Finance statistics page for the ticker
        """

        check_security_type(security_type=self.security_type, valid_types=["stock"])

        # URL of the website to scrape
        url = f"https://finance.yahoo.com/quote/{self.ticker}/balance-sheet"
        return self.get_financials_table(url)

    @property
    def income_stmt_web(self) -> pd.DataFrame:
        """
        Get income statement for the ticker

        Returns:
        pd.DataFrame: A pandas DataFrame including the income statement
        visible in the Yahoo Finance statistics page for the ticker
        """

        check_security_type(security_type=self.security_type, valid_types=["stock"])

        # URL of the website to scrape
        url = f"https://finance.yahoo.com/quote/{self.ticker}/financials"
        return self.get_financials_table(url)
