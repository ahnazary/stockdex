"""
Moduel for the Ticker class
"""

import warnings

import pandas as pd
import requests
from bs4 import BeautifulSoup

from stockdex.lib import get_user_agent


class Ticker:
    """
    Class for the Ticker
    """

    def __init__(self, ticker: str) -> None:
        if any(map(str.islower, ticker)):
            warnings.warn(
                """Ticker symbols are usually uppercase.
                Please check your symbol or convert it to uppercase.""",
                UserWarning,
            )
        self.ticker = ticker.upper()
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
        response = requests.get(url, headers=headers)
        # If the HTTP GET request can't be served
        if response.status_code != 200:
            raise Exception("Failed to load page, check if the ticker symbol exists")

        return response

    @property
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

    @property
    def statistics(self) -> pd.DataFrame:
        """
        Get statistics for the ticker

        Returns:
        pd.DataFrame: A pandas DataFrame including the statistics
        visible in the Yahoo Finance statistics page for the ticker
        """

        # URL of the website to scrape
        url = f"https://finance.yahoo.com/quote/{self.ticker}/key-statistics"
        response = self.get_response(url, self.request_headers)

        # Parse the HTML content of the website
        soup = BeautifulSoup(response.content, "html.parser")
        raw_data = soup.find_all("tr", {"class": True})

        data_df = pd.DataFrame()
        for item in raw_data:
            cols = item.find_all("td")
            cols = [ele.text.strip() for ele in cols]
            data_df[cols[0]] = [cols[1]]

        return data_df.T

    @property
    def income_stmt(self) -> pd.DataFrame:
        """
        Get income statement for the ticker

        Returns:
        pd.DataFrame: A pandas DataFrame including the income statement
        visible in the Yahoo Finance statistics page for the ticker
        """

        # URL of the website to scrape
        url = f"https://finance.yahoo.com/quote/{self.ticker}/financials"
        response = self.get_response(url, self.request_headers)

        # Parse the HTML content of the website
        soup = BeautifulSoup(response.content, "html.parser")

        # <div class="" data-test="fin-row">
        raw_data = soup.find_all("div", {"data-test": "fin-row"})

        data_df = pd.DataFrame()
        for item in raw_data:
            # get criteria. e.g. "Total Revenue"
            major_div = item.find_all("div", {"class": True})[0]
            criteria = major_div.find_all("div", {"class": True})[0].find("span").text

            # get data. e.g. "274515000000"
            minor_div = major_div.find_all("div", {"class": "Ta(c)"})
            data_list = []
            for div in minor_div:
                data_list.append(div.text)

            data_df[criteria] = data_list

        return data_df.T

    @property
    def balance_sheet(self) -> pd.DataFrame:
        """
        Get balance sheet for the ticker

        Returns:
        pd.DataFrame: A pandas DataFrame including the balance sheet
        visible in the Yahoo Finance statistics page for the ticker
        """

        # URL of the website to scrape
        url = f"https://finance.yahoo.com/quote/{self.ticker}/balance-sheet"
        response = self.get_response(url, self.request_headers)

        # Parse the HTML content of the website
        soup = BeautifulSoup(response.content, "html.parser")

        # <div class="" data-test="fin-row">
        raw_data = soup.find_all("div", {"data-test": "fin-row"})

        data_df = pd.DataFrame()
        for item in raw_data:
            # get criteria. e.g. "Total Revenue"
            major_div = item.find_all("div", {"class": True})[0]
            criteria = major_div.find_all("div", {"class": True})[0].find("span").text

            # get data. e.g. "274515000000"
            minor_div = major_div.find_all("div", {"class": "Ta(c)"})
            data_list = []
            for div in minor_div:
                data_list.append(div.text)

            data_df[criteria] = data_list

        return data_df.T

    @property
    def cash_flow(self) -> pd.DataFrame:
        """
        Get cash flow for the ticker

        Returns:
        pd.DataFrame: A pandas DataFrame including the cash flow
        visible in the Yahoo Finance statistics page for the ticker
        """

        # URL of the website to scrape
        url = f"https://finance.yahoo.com/quote/{self.ticker}/cash-flow"
        response = self.get_response(url, self.request_headers)

        # Parse the HTML content of the website
        soup = BeautifulSoup(response.content, "html.parser")

        # <div class="" data-test="fin-row">
        raw_data = soup.find_all("div", {"data-test": "fin-row"})

        data_df = pd.DataFrame()
        for item in raw_data:
            # get criteria. e.g. "Total Revenue"
            major_div = item.find_all("div", {"class": True})[0]
            criteria = major_div.find_all("div", {"class": True})[0].find("span").text

            # get data. e.g. "274515000000"
            minor_div = major_div.find_all("div", {"class": "Ta(c)"})
            data_list = []
            for div in minor_div:
                data_list.append(div.text)

            data_df[criteria] = data_list

        return data_df.T

    @property
    def analysis(self) -> pd.DataFrame:
        """
        Get analysis for the ticker

        Returns:
        pd.DataFrame: A pandas DataFrame including the analysis
        visible in the Yahoo Finance statistics page for the ticker
        """

        # URL of the website to scrape
        url = f"https://finance.yahoo.com/quote/{self.ticker}/analysis"
        response = self.get_response(url, self.request_headers)

        # Parse the HTML content of the website
        soup = BeautifulSoup(response.content, "html.parser")

        raw_data = soup.find_all("tbody")

        data_df = pd.DataFrame()
        for item in raw_data:
            for row in item.find_all("tr"):
                row = row.find_all("td")
                criteria = row[0].text

                # the rest of the row is the data
                data_list = []
                for data in row[1:]:
                    data_list.append(data.text)

                data_df[criteria] = data_list

        return data_df.T

    @property
    def calls(self) -> pd.DataFrame:
        """
        Get calls for the ticker

        Returns:
        pd.DataFrame: A pandas DataFrame including the calls
        visible in the Yahoo Finance statistics page for the ticker
        """

        # URL of the website to scrape
        url = f"https://finance.yahoo.com/quote/{self.ticker}/options"
        response = self.get_response(url, self.request_headers)

        # Parse the HTML content of the website
        soup = BeautifulSoup(response.content, "html.parser")

        # gets calls and puts
        tables = soup.find_all("table")
        headers, data = [], []

        thead = tables[0].find("thead")
        tbody = tables[0].find("tbody")
        data_df = pd.DataFrame()

        # get headers
        for th in thead.find_all("th"):
            headers.append(th.text)

        # get data
        for tr in tbody.find_all("tr"):
            row = tr.find_all("td")
            data.append([data.text for data in row])

        data_df = pd.DataFrame(data, columns=headers)

        return data_df

    @property
    def puts(self) -> pd.DataFrame:
        """
        Get puts for the ticker

        Returns:
        pd.DataFrame: A pandas DataFrame including the puts
        visible in the Yahoo Finance statistics page for the ticker
        """

        # URL of the website to scrape
        url = f"https://finance.yahoo.com/quote/{self.ticker}/options"
        response = self.get_response(url, self.request_headers)

        # Parse the HTML content of the website
        soup = BeautifulSoup(response.content, "html.parser")

        # gets calls and puts
        tables = soup.find_all("table")
        headers, data = [], []

        thead = tables[1].find("thead")
        tbody = tables[1].find("tbody")
        data_df = pd.DataFrame()

        # get headers
        for th in thead.find_all("th"):
            headers.append(th.text)

        # get data
        for tr in tbody.find_all("tr"):
            row = tr.find_all("td")
            data.append([data.text for data in row])

        data_df = pd.DataFrame(data, columns=headers)

        return data_df

    @property
    def profile_key_executives(self) -> pd.DataFrame:
        """
        Get profile key executives for the ticker

        Returns:
        pd.DataFrame: A pandas DataFrame including the profile key executives
        visible in the Yahoo Finance statistics page for the ticker
        """

        # URL of the website to scrape
        url = f"https://finance.yahoo.com/quote/{self.ticker}/profile"
        response = self.get_response(url, self.request_headers)

        # Parse the HTML content of the website
        soup = BeautifulSoup(response.content, "html.parser")

        raw_data = soup.find_all("table")

        data_df = pd.DataFrame()
        data = []

        criteria = [th.text for th in raw_data[0].find_all("thead")[0].find_all("th")]
        for tr in raw_data[0].find_all("tbody")[0].find_all("tr"):
            data.append([td.text for td in tr.find_all("td")])

        data_df = pd.DataFrame(data, columns=criteria)

        return data_df
