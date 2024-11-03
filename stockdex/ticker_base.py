"""
Base class for ticker objects to inherit from
"""

import time
from logging import getLogger
from typing import Union

import requests
from bs4 import BeautifulSoup

from stockdex.config import RESPONSE_TIMEOUT
from stockdex.lib import get_user_agent


class TickerBase:
    request_headers = {
        "User-Agent": get_user_agent(),
    }
    logger = getLogger(__name__)

    def get_response(self, url: str) -> requests.Response:
        """
        Send an HTTP GET request to the website

        Args:
        ----------
        url: str
            The URL to send the HTTP GET request to


        Returns:
        ----------
        requests.Response
            The response from the website
        """

        # Send an HTTP GET request to the website
        session = requests.Session()
        response = session.get(
            url, headers=self.request_headers, timeout=RESPONSE_TIMEOUT
        )
        # If the HTTP GET request can't be served
        if response.status_code != 200 and response.status_code != 429:
            raise Exception(
                f"""
                Failed to load page (status code: {response.status_code}).
                Check if the ticker symbol exists
                """
            )

        # sleep if rate limit is reached and retry after time is given
        elif response.status_code == 429:
            # retry 5 times with 10 seconds intervals and after that raise an exception
            for _ in range(5):
                retry_after = 10
                self.logger.warning(
                    f"Rate limit reached. Retrying after {retry_after} seconds"
                )
                time.sleep(retry_after)
                response = session.get(
                    url, headers=self.request_headers, timeout=RESPONSE_TIMEOUT
                )
                if response.status_code == 200:
                    break

        return response

    def find_parent_by_text(
        self,
        soup: BeautifulSoup,
        tag: str,
        text: str,
        condition: dict = {},
        skip: int = 0,
    ) -> Union[None, str]:
        """
        Method that finds the parent of a tag by its text from a BeautifulSoup object

        Args:
        ----------
        soup: BeautifulSoup
            The BeautifulSoup object to search
        tag: str
            The tag to search for
        text: str
            The text to search for
        condition: dict
            The condition to search for
        skip: int
            The number of elements to skip before returning the parent

        Returns:
        ----------
        Union[None, str]: The parent of the tag if it exists, None otherwise
        """
        for element in soup.find_all(tag, condition):
            if text in element.get_text():
                for _ in range(skip):
                    element = element.find_next(tag)
                return element
        return None
