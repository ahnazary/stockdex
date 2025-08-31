"""
Base class for ticker objects to inherit from
"""

import time
from functools import lru_cache
from typing import Union

from bs4 import BeautifulSoup
from curl_cffi import requests

from stockdex.config import MACROTRENDS_BASE_URL, RESPONSE_TIMEOUT
from stockdex.lib import get_user_agent


class TickerBase:
    session = requests.Session(impersonate="chrome110")
    request_headers = {
        "User-Agent": get_user_agent(),
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://finance.yahoo.com/",
        "Origin": "https://finance.yahoo.com",
        "Connection": "keep-alive",
    }
    _yahoo_crumb: Union[str, None] = None

    def _get_yahoo_crumb(self) -> str:
        try:
            self.session.get("https://fc.yahoo.com", timeout=10, allow_redirects=True)
            response = self.session.get(
                "https://query1.finance.yahoo.com/v1/test/getcrumb",
                timeout=10,
                allow_redirects=True,
            )
            crumb = response.text.strip()
            if response.status_code == 429 or "Too Many Requests" in crumb:
                raise RuntimeError("Rate limited while getting crumb")
            if crumb == "" or "<html>" in crumb:
                raise RuntimeError("Invalid crumb received")
            return crumb
        except Exception as e:
            raise RuntimeError(f"Error fetching Yahoo crumb: {e}")

    def get_response(self, url: str) -> requests.Response:
        if self._yahoo_crumb is None:
            self._yahoo_crumb = self._get_yahoo_crumb()

        response = self.session.get(
            url,
            headers=self.request_headers,
            timeout=RESPONSE_TIMEOUT,
            params={"crumb": self._yahoo_crumb},
        )

        if response.status_code == 200:
            return response

        if response.status_code == 429:
            for _ in range(5):
                time.sleep(10)
                response = self.session.get(
                    url,
                    headers=self.request_headers,
                    timeout=RESPONSE_TIMEOUT,
                    params={"crumb": self._yahoo_crumb},
                )
                if response.status_code == 200:
                    return response

        raise RuntimeError(
            f"Failed to fetch URL (status {response.status_code}): {url}"
        )

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

    @lru_cache(maxsize=None)
    def get_company_slug(self, ticker: str) -> str:
        """
        Retrieve the company slug for the given ticker using macrotrends.


        :param ticker: The stock ticker symbol
        :return: The company slug, e.g. "BAC" -> "bank-of-america"
        """
        url = f"{MACROTRENDS_BASE_URL}/{ticker}/TBD/income-statement"
        response = self.get_response(url)
        company_slug = response.url.split("/")[-2]

        return company_slug
