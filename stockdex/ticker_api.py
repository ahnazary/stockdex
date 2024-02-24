"""
Module to retrieve stock data from Yahoo Finance API
"""

import pandas as pd
import requests

from stockdex.lib import get_user_agent


class TickerAPI:
    def __init__(self, ticker):
        self.ticker = ticker
        self.base_url = "https://query2.finance.yahoo.com/v8/finance/"
        self.request_headers = {
            "User-Agent": get_user_agent()[0],
        }

    def get_response(self, url: str, headers: dict = None) -> requests.Response:
        """
        Send an HTTP GET request to the website

        Args:
        url (str): The URL of the website
        headers (dict): The headers to be sent with the HTTP GET request

        Returns:
        requests.Response: The response of the HTTP GET request
        """

        # Send an HTTP GET request to the website
        session = requests.Session()
        response = session.get(url, headers=headers)
        # If the HTTP GET request can't be served
        if response.status_code != 200:
            raise Exception("Failed to load page, check if the ticker symbol exists")

        return response

    @property
    def chart(self, range: str = "1d"):
        """
        Get the chart data for the stock
        """

        url = f"{self.base_url}/chart/{self.ticker}?range={range}"
        # send a get request to the website
        response = self.get_response(url, headers=self.request_headers)

        timestamp = response.json()["chart"]["result"][0]["timestamp"]
        # convert the timestamp to datetime
        timestamp = pd.to_datetime(timestamp, unit="s")
        volume = response.json()["chart"]["result"][0]["indicators"]["quote"][0][
            "volume"
        ]
        close = response.json()["chart"]["result"][0]["indicators"]["quote"][0]["close"]
        open = response.json()["chart"]["result"][0]["indicators"]["quote"][0]["open"]
        high = response.json()["chart"]["result"][0]["indicators"]["quote"][0]["high"]
        low = response.json()["chart"]["result"][0]["indicators"]["quote"][0]["low"]

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
