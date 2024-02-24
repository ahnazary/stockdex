"""
Module to retrieve stock data from Yahoo Finance API
The main Ticker class inherits from this class
"""

import pandas as pd

from stockdex.ticker_base import TickerBase


class TickerAPI(TickerBase):
    base_url = "https://query2.finance.yahoo.com/v8/finance/"

    @property
    def chart(self, range: str = "1d"):
        """
        Get the chart data for the stock
        """

        url = f"{self.base_url}/chart/{self.ticker}?range={range}"
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
