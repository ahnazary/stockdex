"""
Interface for NASDAQ stock data
"""

import pandas as pd
import requests
from bs4 import BeautifulSoup

from stockdex.lib import get_user_agent


class NASDAQInterface:
    def __init__(self, ticker):
        self.ticker = ticker
        self.base_url = "https://www.nasdaq.com/market-activity/stocks/"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"  # noqa E501
        }

    def get_chart(self):
        """
        Get historical data for the stock
        """

        url = f"{self.base_url}/{self.ticker}/chart"
        # send a get request to the website
        response = requests.get(url=url, headers=self.headers).json()

        return response

    def quarterly_earnings(self):
        """
        Get quarterly earnings for the stock
        """

        url = f"{self.base_url}/{self.ticker}/earnings"
        # send a get request to the website
        response = requests.get(url=url, headers=self.headers).json()

        soup = BeautifulSoup(response, "html.parser")

        raw_data = soup.find_all("table", class_="earnings-surprise__table-body")

        headers = [
            item.text
            for item in soup.find_all("th", class_="earnings-surprise__table-header")
        ]
