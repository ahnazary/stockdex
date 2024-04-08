"""
Interface for NASDAQ stock data
"""

from typing import Literal

import pandas as pd

from stockdex.config import NASDAQ_BASE_URL
from stockdex.lib import get_user_agent
from stockdex.selenium_interface import selenium_interface
from stockdex.ticker_base import TickerBase


class NASDAQInterface(TickerBase):
    def __init__(
        self,
        ticker: str = "",
        isin: str = "",
        security_type: str = Literal["stock", "etf"],
    ) -> None:
        self.isin = isin
        self.ticker = ticker
        self.security_type = security_type

        self.request_headers = {
            "User-Agent": get_user_agent()[0],
        }

    def quarterly_earnings_surprise(self) -> pd.DataFrame:
        """
        Get quarterly earnings for the stock

        Returns:
        ----------------
        pd.DataFrame: Quarterly earnings surprise data
        The columns might include:
        - 'Fiscal Quarter End'
        - 'Date Reported'
        - 'Earnings Per Share*'
        - 'Consensus EPS* Forecast'
        - '% Surprise'
        """

        url = f"{NASDAQ_BASE_URL}/{self.ticker.lower()}/earnings"

        # build selenium interface object if not already built
        if not hasattr(self, "selenium_interface"):
            self.selenium_interface = selenium_interface(use_custom_user_agent=True)

        soup = self.selenium_interface.get_html_content(url)

        earnings_table = soup.find("table", {"class": "earnings-surprise__table"})
        columns = earnings_table.find(
            "tr", {"class": "earnings-surprise__header"}
        ).find_all("th")
        columns = [column.text for column in columns]

        data = []
        table_body = earnings_table.find(
            "tbody", {"class": "earnings-surprise__table-body"}
        )
        for row in table_body.find_all("tr"):
            row_data_th = [cell.text for cell in row.find_all("th")]
            row_data_td = [cell.text for cell in row.find_all("td")]
            row_data = row_data_th + row_data_td
            data.append(row_data)

        return pd.DataFrame(data, columns=columns)

    def yearly_earnings_forecast(self) -> pd.DataFrame:
        """
        Get yearly earnings for the stock

        Returns:
        ----------------
        pd.DataFrame: Yearly earnings data
        The columns might include:
        - Fiscal Year End
        - Consensus EPS* Forecast
        - High EPS* Forecast
        - Low EPS* Forecast
        - Number Of Estimates
        - Over The Last 4 Weeks Number Of Revisions - Up
        - Over The Last 4 Weeks Number Of Revisions - Down
        """

        url = f"{NASDAQ_BASE_URL}/{self.ticker.lower()}/earnings"

        # build selenium interface object if not already built
        if not hasattr(self, "selenium_interface"):
            self.selenium_interface = selenium_interface(use_custom_user_agent=True)

        soup = self.selenium_interface.get_html_content(url)
        earnings_table = soup.find("table", {"class": "earnings-forecast__table"})

        columns = earnings_table.find(
            "tr", {"class": "earnings-forecast__header"}
        ).find_all("th")
        columns = [column.text for column in columns]

        data = []
        table_body = earnings_table.find(
            "tbody", {"class": "earnings-forecast__table-body"}
        )
        for row in table_body.find_all("tr"):
            row_data_th = [cell.text for cell in row.find_all("th")]
            row_data_td = [cell.text for cell in row.find_all("td")]
            row_data = row_data_th + row_data_td
            data.append(row_data)

        return pd.DataFrame(data, columns=columns)

    def quarterly_earnings_forecast(self) -> pd.DataFrame:
        """
        Get quarterly earnings forecast for the stock

        Returns:
        ----------------
        pd.DataFrame: Quarterly earnings forecast data
        The columns might include:
        - Fiscal Quarter End
        - Consensus EPS* Forecast
        - High EPS* Forecast
        - Low EPS* Forecast
        - Number Of Estimates
        - Over The Last 4 Weeks Number Of Revisions - Up
        - Over The Last 4 Weeks Number Of Revisions - Down
        """

        url = f"{NASDAQ_BASE_URL}/{self.ticker.lower()}/earnings"

        # build selenium interface object if not already built
        if not hasattr(self, "selenium_interface"):
            self.selenium_interface = selenium_interface(use_custom_user_agent=True)

        soup = self.selenium_interface.get_html_content(url)
        earnings_table = soup.find_all("table", {"class": "earnings-forecast__table"})[
            1
        ]

        columns = earnings_table.find(
            "tr", {"class": "earnings-forecast__header"}
        ).find_all("th")
        columns = [column.text for column in columns]

        data = []
        table_body = earnings_table.find(
            "tbody", {"class": "earnings-forecast__table-body"}
        )
        for row in table_body.find_all("tr"):
            row_data_th = [cell.text for cell in row.find_all("th")]
            row_data_td = [cell.text for cell in row.find_all("td")]
            row_data = row_data_th + row_data_td
            data.append(row_data)

        return pd.DataFrame(data, columns=columns)
