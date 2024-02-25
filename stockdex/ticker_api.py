"""
Module to retrieve stock data from Yahoo Finance API
The main Ticker class inherits from this class
"""

from typing import Literal

import pandas as pd

from stockdex.ticker_base import TickerBase


class TickerAPI(TickerBase):
    base_url = "https://query2.finance.yahoo.com/v8/finance/"

    def price(
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
        Get the price data for the stock

        Args:
        range (str): The range of the price data to retrieve
        valid values are "1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"

        dataGranularity (str): The granularity of the data to retrieve (interval)
        valid values are "1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h", "1d", "5d", "1wk", "1mo", "3mo""  # noqa: E501
        """

        url = f"{self.base_url}/chart/{self.ticker}?range={range}&interval={dataGranularity}"
        response = self.get_response(url)

        timestamp = response.json()["chart"]["result"][0]["timestamp"]
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

    @property
    def current_trading_period(self) -> pd.DataFrame:
        """
        Get the current trading period for the stock
        """

        url = f"{self.base_url}/chart/{self.ticker}"
        response = self.get_response(url)

        currentTradingPeriod = response.json()["chart"]["result"][0]["meta"][
            "currentTradingPeriod"
        ]

        pre = currentTradingPeriod["pre"]
        regular = currentTradingPeriod["regular"]
        post = currentTradingPeriod["post"]

        # convert timestamps to datetime
        pre["start"] = pd.to_datetime(pre["start"], unit="s")
        pre["end"] = pd.to_datetime(pre["end"], unit="s")
        regular["start"] = pd.to_datetime(regular["start"], unit="s")
        regular["end"] = pd.to_datetime(regular["end"], unit="s")
        post["start"] = pd.to_datetime(post["start"], unit="s")
        post["end"] = pd.to_datetime(post["end"], unit="s")

        return pd.DataFrame(
            {
                "pre": pre,
                "regular": regular,
                "post": post,
            }
        )
