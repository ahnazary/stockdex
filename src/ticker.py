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

    def __init__(self, symbol):
        self.symbol = symbol

    def get_data(self) -> pd.DataFrame:
        """
        Get data for the ticker

        Returns:
        pd.DataFrame: A pandas DataFrame including the data
        visible in the Yahoo Finance first page for the ticker
        """

        # URL of the website to scrape
        url = "https://finance.yahoo.com/quote/AAPL"

        # Send an HTTP GET request to the website
        # response = httpx.get(url)
        response = requests.get(url)

        # If the HTTP GET request can't be served
        if response.status_code != 200:
            raise Exception("Failed to load page")

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


if __name__ == "__main__":
    ticker = Ticker("AAPL")
    ticker.get_data()
