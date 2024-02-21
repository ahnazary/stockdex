"""
Module to retrieve stock data from Yahoo Finance API
"""

import requests


class TickerAPI:
    def __init__(self, ticker):
        self.ticker = ticker
        self.base_url = "https://query2.finance.yahoo.com/v8/finance/"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'  # noqa E501
        }

    def get_chart(self):
        """
        Get historical data for the stock
        """

        url = f"{self.base_url}chart/{self.ticker}"
        # send a get request to the website
        response = requests.get(url=url, headers=self.headers).json()

        return response
