"""
Moduel for the Ticker class
"""

import requests
from bs4 import BeautifulSoup
import httpx

class Ticker:
    """
    Class for the Ticker
    """

    def __init__(self, symbol):
        self.symbol = symbol

    def get_data(self):
        """
        Get data for the ticker
        """


        # URL of the website to scrape
        url = "https://finance.yahoo.com/quote/AAPL"

        # Send an HTTP GET request to the website
        response = httpx.get(url)

        # If the HTTP GET request can't be served
        if response.status_code != 200:
            raise Exception("Failed to load page")
        
        # Parse the HTML content of the website
        soup = BeautifulSoup(response.content, 'html.parser')
        print(soup.prettify())
        # write to a file
        with open('soup.html', 'w') as file:
            file.write(str(soup.prettify()))

if __name__ == "__main__":
    ticker = Ticker('AAPL')
    ticker.get_data()