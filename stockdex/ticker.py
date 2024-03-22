"""
Moduel for the Ticker class
"""

from typing import Literal

import pandas as pd
from bs4 import BeautifulSoup

from stockdex.justetf import JustETF
from stockdex.ticker_api import TickerAPI


class Ticker(TickerAPI, JustETF):
    """
    Class for the Ticker
    """

    def __init__(
        self,
        ticker: str = "",
        isin: str = "",
        security_type: str = Literal["stock", "etf"],
    ) -> None:
        """
        Initialize the Ticker class

        Args:
        ticker (str): The ticker of the stock
        isin (str): The ISIN of the etf
        security_type (str): The security type of the ticker
            default is "stock"
        """

        self.ticker = ticker
        self.isin = isin
        self.security_type = security_type if security_type else "stock"

        if not ticker and not isin:
            raise Exception("Please provide either a ticker or an ISIN")

        if security_type == "etf":
            super().__init__(isin=isin)
        else:
            super().__init__(ticker=ticker)

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
        response = self.get_response(url)

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
        response = self.get_response(url)

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
    def balance_sheet_web(self) -> pd.DataFrame:
        """
        Get balance sheet for the ticker

        Returns:
        pd.DataFrame: A pandas DataFrame including the balance sheet
        visible in the Yahoo Finance statistics page for the ticker
        """

        # URL of the website to scrape
        url = f"https://finance.yahoo.com/quote/{self.ticker}/balance-sheet"
        response = self.get_response(url)

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
    def cashflow_web(self) -> pd.DataFrame:
        """
        Get cash flow for the ticker

        Returns:
        pd.DataFrame: A pandas DataFrame including the cash flow
        visible in the Yahoo Finance statistics page for the ticker
        """

        # URL of the website to scrape
        url = f"https://finance.yahoo.com/quote/{self.ticker}/cash-flow"
        response = self.get_response(url)
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
        response = self.get_response(url)

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
        response = self.get_response(url)

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
        response = self.get_response(url)

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
    def key_executives(self) -> pd.DataFrame:
        """
        Get profile key executives for the ticker

        Returns:
        pd.DataFrame: A pandas DataFrame including the profile key executives
        visible in the Yahoo Finance statistics page for the ticker
        """

        # URL of the website to scrape
        url = f"https://finance.yahoo.com/quote/{self.ticker}/profile"
        response = self.get_response(url)

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

    @property
    def description(self) -> str:
        """
        Get the description of the ticker

        Returns:
        str: A string including the description of the ticker
        visible in the Yahoo Finance profile page for the ticker
        """
        if self.security_type == "etf":
            return self.etf_description

        # URL of the website to scrape
        url = f"https://finance.yahoo.com/quote/{self.ticker}/profile"
        response = self.get_response(url)

        # Parse the HTML content of the website
        soup = BeautifulSoup(response.content, "html.parser")

        raw_data = soup.find_all("p")

        return raw_data[2].text

    @property
    def corporate_governance(self) -> str:
        """
        Get the description of the ticker

        Returns:
        str: A string including the description of the ticker
        visible in the Yahoo Finance profile page for the ticker
        """

        # URL of the website to scrape
        url = f"https://finance.yahoo.com/quote/{self.ticker}/profile"
        response = self.get_response(url)

        # Parse the HTML content of the website
        soup = BeautifulSoup(response.content, "html.parser")

        raw_data = soup.find_all("p")

        return raw_data[3].text

    @property
    def major_holders(self) -> pd.DataFrame:
        """
        Get major holders for the ticker

        Returns:
        pd.DataFrame: A pandas DataFrame including the major holders
        visible in the Yahoo Finance statistics page for the ticker
        """

        # URL of the website to scrape
        url = f"https://finance.yahoo.com/quote/{self.ticker}/holders"
        response = self.get_response(url)

        # Parse the HTML content of the website
        soup = BeautifulSoup(response.content, "html.parser")

        raw_data = soup.find_all("div", {"data-test": "holder-summary"})

        data_df = pd.DataFrame()
        data = []

        table = raw_data[0].find_all("tr")
        for tr in table:
            data.append([td.text for td in tr.find_all("td")])

        data_df = pd.DataFrame(data)
        data_df.columns = ["percentage", "holders"]
        return data_df

    @property
    def top_institutional_holders(self) -> pd.DataFrame:
        """
        Get top institutional holders for the ticker

        Returns:
        pd.DataFrame: A pandas DataFrame including the top institutional holders
        visible in the Yahoo Finance statistics page for the ticker
        """

        # URL of the website to scrape
        url = f"https://finance.yahoo.com/quote/{self.ticker}/holders"
        response = self.get_response(url)

        # Parse the HTML content of the website
        soup = BeautifulSoup(response.content, "html.parser")
        raw_data = soup.find_all("table")

        data_df = pd.DataFrame()
        data = []

        table = raw_data[1].find_all("tr")
        for tr in table:
            data.append([td.text for td in tr.find_all("td")])

        data_df = pd.DataFrame(data)
        data_df.columns = ["holder", "shares", "date_reported", "percentage", "value"]
        return data_df

    @property
    def top_mutual_fund_holders(self) -> pd.DataFrame:
        """
        Get top mutual fund holders for the ticker

        Returns:
        pd.DataFrame: A pandas DataFrame including the top mutual fund holders
        visible in the Yahoo Finance statistics page for the ticker
        """

        # URL of the website to scrape
        url = f"https://finance.yahoo.com/quote/{self.ticker}/holders"
        response = self.get_response(url)

        # Parse the HTML content of the website
        soup = BeautifulSoup(response.content, "html.parser")
        raw_data = soup.find_all("table")

        data_df = pd.DataFrame()
        data = []

        table = raw_data[2].find_all("tr")
        for tr in table:
            data.append([td.text for td in tr.find_all("td")])

        data_df = pd.DataFrame(data)
        data_df.columns = ["holder", "shares", "date_reported", "percentage", "value"]
        return data_df

    @property
    def dividend(self) -> pd.DataFrame:
        """
        Get dividends for the ticker

        Args:
        period (str): The period for the dividends

        Returns:
        pd.DataFrame: A pandas DataFrame including the dividends
        visible in the digrin website for the ticker
        """

        # URL of the website to scrape
        url = f"https://www.digrin.com/stocks/detail/{self.ticker}"
        response = self.get_response(url)

        # Parse the HTML content of the website
        soup = BeautifulSoup(response.content, "html.parser")

        try:
            table = soup.find_all("table")[0]
        except IndexError:
            raise Exception(f"There is no dividend data for the ticker {self.ticker}")

        data_df = pd.DataFrame()
        data = []

        headers = [th.text for th in table.find_all("thead")[0].find_all("th")]
        for tr in table.find_all("tbody")[0].find_all("tr"):
            data.append([td.text for td in tr.find_all("td")])

        data_df = pd.DataFrame(data, columns=headers)
        return data_df
