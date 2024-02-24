"""
Module to retrieve stock data from Yahoo Finance API
The main Ticker class inherits from this class
"""

from typing import Literal

import pandas as pd

from stockdex.ticker_base import TickerBase


class TickerAPI(TickerBase):
    base_url = "https://query2.finance.yahoo.com/v8/finance/"

    def chart(
        self,
        range: Literal[
            "1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"
        ] = "1d",
        dataGranularity: Literal[
            "1m",
            "2m",
            "5m",
            "15m",
            "30m",
            "60m",
            "90m",
            "1h",
            "1d",
            "5d",
            "1wk",
            "1mo",
            "3mo",
        ] = "1m",
    ) -> pd.DataFrame:
        """
        Get the chart data for the stock

        Args:
        range (str): The range of the chart data to retrieve
            valid values are "1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"

        dataGranularity (str): The granularity of the data to retrieve (interval)
            valid values are "1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h", "1d", "5d", "1wk", "1mo", "3mo""  # noqa: E501
        """

        url = f"{self.base_url}/chart/{self.ticker}?range={range}&interval={dataGranularity}"
        # send a get request to the website
        response = self.get_response(url)

        timestamp = response.json()["chart"]["result"][0]["timestamp"]
        # convert the timestamp to datetime
        timestamp = pd.to_datetime(timestamp, unit="s")

        indicators = response.json()["chart"]["result"][0]["indicators"]
        volume = indicators["quote"][0]["volume"]
        close = indicators["quote"][0]["close"]
        open = indicators["quote"][0]["open"]
        high = indicators["quote"][0]["high"]
        low = indicators["quote"][0]["low"]

        return pd.DataFrame(
            {
                "timestamp": timestamp,
                "volume": volume,
                "close": close,
                "open": open,
                "high": high,
                "low": low,
            }
        )
