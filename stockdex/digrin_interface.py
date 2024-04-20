"""
Module to extract data from Digrin website
"""

import pandas as pd
from bs4 import BeautifulSoup

from stockdex.config import DIGRIN_BASE_URL, VALID_SECURITY_TYPES
from stockdex.ticker_base import TickerBase


class Digrin_Interface(TickerBase):
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
    def dividend(self) -> pd.DataFrame:
        """
        Get dividends for the ticker

        Args:
        period (str): The period for the dividends

        Returns:
        pd.DataFrame: A pandas DataFrame including the dividends
        visible in the digrin website for the ticker
        """

        # URL of the website to scrape
        url = f"{DIGRIN_BASE_URL}/{self.ticker}"
        response = self.get_response(url)

        # Parse the HTML content of the website
        soup = BeautifulSoup(response.content, "html.parser")

        try:
            table = soup.find_all("table")[0]
        except IndexError:
            raise Exception(f"There is no dividend data for the ticker {self.ticker}")

        data_df = pd.DataFrame()
        data = []

        headers = [th.text for th in table.find_all("thead")[0].find_all("th")]
        for tr in table.find_all("tbody")[0].find_all("tr"):
            data.append([td.text for td in tr.find_all("td")])

        data_df = pd.DataFrame(data, columns=headers)
        return data_df

    @property
    def payout_ratio(self) -> pd.DataFrame:
        """
        Get payout ratio for the ticker

        Returns:
        pd.DataFrame: A pandas DataFrame including the payout ratio
        visible in the digrin website for the ticker
        """

        # URL of the website to scrape
        url = f"{DIGRIN_BASE_URL}/{self.ticker}/payout_ratio"
        response = self.get_response(url)

        # Parse the HTML content of the website
        soup = BeautifulSoup(response.content, "html.parser")

        try:
            table = soup.find("table")
        except IndexError:
            raise Exception(
                f"There is no payout ratio data for the ticker {self.ticker}"
            )

        data_df = pd.DataFrame()
        data = []

        headers = [th.text for th in table.find_all("thead")[0].find_all("th")]
        for tr in table.find_all("tbody")[0].find_all("tr"):
            data.append([td.text for td in tr.find_all("td")])

        data_df = pd.DataFrame(data, columns=headers)
        return data_df

    @property
    def stock_splits(self) -> pd.DataFrame:
        """
        Get stock splits for the ticker

        Returns:
        pd.DataFrame: A pandas DataFrame including the stock splits
        visible in the digrin website for the ticker
        """

        # URL of the website to scrape
        url = f"{DIGRIN_BASE_URL}/{self.ticker}/stock_split"
        response = self.get_response(url)

        # Parse the HTML content of the website
        soup = BeautifulSoup(response.content, "html.parser")

        try:
            table = soup.find("table")
        except IndexError:
            raise Exception(
                f"There is no stock split data for the ticker {self.ticker}"
            )

        data_df = pd.DataFrame()
        data = []

        headers = [th.text for th in table.find_all("thead")[0].find_all("th")]
        for tr in table.find_all("tbody")[0].find_all("tr"):
            data.append([td.text for td in tr.find_all("td")])

        data_df = pd.DataFrame(data, columns=headers)
        return data_df
