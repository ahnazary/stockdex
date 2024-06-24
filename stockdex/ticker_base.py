"""
Base class for ticker objects to inherit from
"""

from typing import Union

import requests
from bs4 import BeautifulSoup

from stockdex.lib import get_user_agent


class TickerBase:
    request_headers = {
        "User-Agent": get_user_agent(),
    }

    def get_response(self, url: str) -> requests.Response:
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
        response = session.get(url, headers=self.request_headers, timeout=2)
        # If the HTTP GET request can't be served
        if response.status_code != 200:
            raise Exception("Failed to load page, check if the ticker symbol exists")

        return response

    def find_parent_by_text(
        self, soup: BeautifulSoup, tag: str, text: str, condition: dict = {}
    ) -> Union[None, str]:
        """
        Method that finds the parent of a tag by its text from a BeautifulSoup object

        Args:
        ----------
        soup (BeautifulSoup): The BeautifulSoup object
        tag (str): The tag to search for
        text (str): The text to search for
        condition (dict): The condition to search for

        Returns:
        ----------
        Union[None, str]: The parent of the tag if it exists, None otherwise
        """
        for element in soup.find_all(tag, condition):
            if text in element.get_text():
                return element
        return None
