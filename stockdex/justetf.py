"""
Module for extracting ETF data from JustETF website
"""

from typing import Literal

import pandas as pd
from bs4 import BeautifulSoup

from stockdex import config
from stockdex.exceptions import NoISINError
from stockdex.ticker_base import TickerBase


class JustETF(TickerBase):
    def __init__(
        self,
        ticker: str = "",
        isin: str = "",
        security_type: str = Literal["stock", "etf"],
    ) -> None:
        self.isin = isin
        self.ticker = ticker
        self.security_type = security_type
        if not isin:
            raise NoISINError("No ISIN provided, please provide an ISIN")

    @property
    def general_info(self) -> pd.DataFrame:
        """
        Get the general information of the ETF
        genral information includes TER, distribution policy, replication method, etc.
        """
        url = f"{config.JUSTETF_BASE_URL}/etf-profile.html?isin={self.isin}"
        response = self.get_response(url)

        soup = BeautifulSoup(response.text, "html.parser")

        data_df = pd.DataFrame()

        general_info = soup.find("div", {"class": "data-overview mt-4 mb-3"})
        labels = general_info.find_all("div", {"class": "vallabel"})

        for label in labels:
            column = label.text.replace(" ", "")
            value = label.find_next_sibling("div").text

            data_df[column] = [value]

        return data_df

    @property
    def wkn(self) -> str:
        """
        Get the WKN of the ETF
        """
        url = f"{config.JUSTETF_BASE_URL}/etf-profile.html?isin={self.isin}"
        response = self.get_response(url)

        soup = BeautifulSoup(response.text, "html.parser")

        wkn = soup.find("span", {"id": "etf-second-id"}).text

        return wkn

    @property
    def etf_description(self) -> str:
        """
        Get the description of the ETF
        """
        url = f"{config.JUSTETF_BASE_URL}/etf-profile.html?isin={self.isin}"
        response = self.get_response(url)

        soup = BeautifulSoup(response.text, "html.parser")

        description = soup.find("div", {"id": "etf-description"}).text

        return description
