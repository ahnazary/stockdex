"""
Interface for NASDAQ stock data
"""

import requests
from bs4 import BeautifulSoup

from stockdex.lib import get_user_agent


class NASDAQInterface:
    def __init__(self, ticker):
        self.ticker = ticker
        self.base_url = "https://www.nasdaq.com/market-activity/stocks/"
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

    def quarterly_earnings(self):
        """
        Get quarterly earnings for the stock
        """

        url = f"{self.base_url}/{self.ticker}/earnings"
        # send a get request to the website
        response = self.get_response(url, headers=self.request_headers)

        soup = BeautifulSoup(response.content, "html.parser")

        tables = soup.find_all("table")

        # TODO: Fix this as it does not return anything now
        headers = [header.content for header in tables[0].find_all("th")]
        data = [data.content for data in tables[0].find_all("td")]

        return headers, data
