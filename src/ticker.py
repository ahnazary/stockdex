"""
Moduel for the Ticker class
"""

import httpx
import pandas as pd
import requests
from bs4 import BeautifulSoup


class Ticker:
    """
    Class for the Ticker
    """

    def __init__(self, ticker: str) -> None:
        self.ticker = ticker

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
        response = requests.get(url, headers=headers)

        # If the HTTP GET request can't be served
        if response.status_code != 200:
            raise Exception("Failed to load page")

        return response

    def summary(self) -> pd.DataFrame:
        """
        Get data for the ticker

        Returns:
        pd.DataFrame: A pandas DataFrame including the data
        visible in the Yahoo Finance first page for the ticker
        """

        # URL of the website to scrape
        url = f"https://finance.yahoo.com/quote/{self.ticker}"
        response = self.get_response(url)

        # Parse the HTML content of the website
        soup = BeautifulSoup(response.content, "html.parser")

        # for data in the table, generating 16 rows
        raw_data = soup.find_all("td", {"data-test": True})
        data_df = pd.DataFrame()
        for item in raw_data:
            data_df[item["data-test"].replace("-value", "")] = [item.text]

        # for data in top of the page, generating 10 rows
        raw_data = soup.find_all("fin-streamer", {"data-field": True})
        for item in raw_data:
            data_df[item["data-field"]] = [item.text]

        return data_df.T

    def statistics(self) -> pd.DataFrame:
        """
        Get statistics for the ticker

        Returns:
        pd.DataFrame: A pandas DataFrame including the statistics
        visible in the Yahoo Finance statistics page for the ticker
        """

        # URL of the website to scrape
        url = f"https://finance.yahoo.com/quote/{self.ticker}/key-statistics"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        }
        response = self.get_response(url, headers)

        # Parse the HTML content of the website
        soup = BeautifulSoup(response.content, "html.parser")
        raw_data = soup.find_all("tr", {"class": True})

        data_df = pd.DataFrame()
        for item in raw_data:
            cols = item.find_all("td")
            cols = [ele.text.strip() for ele in cols]
            data_df[cols[0]] = [cols[1]]

        return data_df.T


if __name__ == "__main__":
    ticker = Ticker("AAPL")
    ticker.summary()
    ticker.statistics()
