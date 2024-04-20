"""
Moduel for the Ticker class
"""

import pandas as pd
from bs4 import BeautifulSoup

from stockdex.config import VALID_SECURITY_TYPES
from stockdex.digrin_interface import Digrin_Interface
from stockdex.justetf import JustETF
from stockdex.nasdaq_interface import NASDAQInterface
from stockdex.ticker_api import TickerAPI
from stockdex.yahoo_web import YahooWeb


class Ticker(TickerAPI, JustETF, NASDAQInterface, Digrin_Interface, YahooWeb):
    """
    Class for the Ticker
    """

    def __init__(
        self,
        ticker: str = "",
        isin: str = "",
        security_type: VALID_SECURITY_TYPES = "stock",
    ) -> None:
        """
        Initialize the Ticker class

        Args:
        ticker (str): The ticker of the stock
        isin (str): The ISIN of the etf
        security_type (str): The security type of the ticker
            default is "stock"
        """

        self.ticker = ticker
        self.isin = isin
        self.security_type = security_type if security_type else "stock"

        if not ticker and not isin:
            raise Exception("Please provide either a ticker or an ISIN")

        super().__init__(ticker=ticker, isin=isin, security_type=security_type)

    @property
    def statistics(self) -> pd.DataFrame:
        """
        Get statistics for the ticker

        Returns:
        pd.DataFrame: A pandas DataFrame including the statistics
        visible in the Yahoo Finance statistics page for the ticker
        """

        # URL of the website to scrape
        url = f"https://finance.yahoo.com/quote/{self.ticker}/key-statistics"
        response = self.get_response(url)

        # Parse the HTML content of the website
        soup = BeautifulSoup(response.content, "html.parser")
        raw_data = soup.find_all("tr", {"class": True})

        data_df = pd.DataFrame()
        for item in raw_data:
            cols = item.find_all("td")
            cols = [ele.text.strip() for ele in cols]
            data_df[cols[0]] = [cols[1]]

        return data_df.T
