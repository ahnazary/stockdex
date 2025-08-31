"""
Module for fetching data from Yahoo Finance website
"""

import re

import pandas as pd
from bs4 import BeautifulSoup

from stockdex.config import VALID_SECURITY_TYPES, YAHOO_WEB_BASE_URL
from stockdex.lib import check_security_type
from stockdex.ticker_base import TickerBase


class YahooWeb(TickerBase):
    def __init__(
        self,
        ticker: str = "",
        isin: str = "",
        security_type: VALID_SECURITY_TYPES = "stock",
    ) -> None:
        self.isin = isin
        self.ticker = ticker
        self.security_type = security_type

    def yahoo_web_financials_table(self, url: str) -> pd.DataFrame:
        """
        Get financials table from the Yahoo Finance website

        Args:
        ----------------
        url (str)
            The URL of the website to scrape


        Returns:
        ----------------
        pd.DataFrame: A pandas DataFrame including the financials table
        """
        response = self.get_response(url)
        soup = BeautifulSoup(response.content, "html.parser")

        table = self.find_parent_by_text(soup, "div", "Breakdown")

        # Extract column headers
        header_row = table.find("div", class_="tableHeader")
        columns = [
            col.get_text(strip=True)
            for col in header_row.find_all("div", class_="column")
        ]

        # Add 'Breakdown' to the columns
        columns.insert(0, "Breakdown")

        # Extract data rows
        data_rows = soup.find("div", class_="tableBody").find_all("div", class_="row")

        # Parse each row into a list of values
        data = []
        for row in data_rows:
            cells = row.find_all("div", class_="column")
            row_data = [
                row.find("div", class_="rowTitle").get_text(strip=True)
            ]  # Extract the Breakdown value
            row_data += [
                cell.get_text(strip=True) for cell in cells
            ]  # Extract the rest of the row's data
            data.append(row_data)

        # Create a Pandas DataFrame
        df = pd.DataFrame(data, columns=columns).set_index("Breakdown")

        # index is a tuple, get only first element
        df.index = [index[0] for index in df.index]

        return df

    @property
    def yahoo_web_cashflow(self) -> pd.DataFrame:
        """
        Get cash flow for the ticker

        Returns:
        pd.DataFrame: A pandas DataFrame including the cash flow
        visible in the Yahoo Finance statistics page for the ticker
        """
        check_security_type(security_type=self.security_type, valid_types=["stock"])

        # URL of the website to scrape
        url = f"{YAHOO_WEB_BASE_URL}/{self.ticker}/cash-flow"
        return self.yahoo_web_financials_table(url)

    @property
    def yahoo_web_balance_sheet(self) -> pd.DataFrame:
        """
        Get balance sheet for the ticker

        Returns:
        pd.DataFrame: A pandas DataFrame including the balance sheet
        visible in the Yahoo Finance statistics page for the ticker
        """

        check_security_type(security_type=self.security_type, valid_types=["stock"])

        # URL of the website to scrape
        url = f"{YAHOO_WEB_BASE_URL}/{self.ticker}/balance-sheet"
        return self.yahoo_web_financials_table(url)

    @property
    def yahoo_web_income_stmt(self) -> pd.DataFrame:
        """
        Get income statement for the ticker

        Returns:
        pd.DataFrame: A pandas DataFrame including the income statement
        visible in the Yahoo Finance statistics page for the ticker
        """

        check_security_type(security_type=self.security_type, valid_types=["stock"])

        # URL of the website to scrape
        url = f"{YAHOO_WEB_BASE_URL}/{self.ticker}/financials"
        return self.yahoo_web_financials_table(url)

    @property
    def yahoo_web_calls(self) -> pd.DataFrame:
        """
        Get calls for the ticker

        Returns:
        pd.DataFrame: A pandas DataFrame including the calls
        visible in the Yahoo Finance statistics page for the ticker
        """
        check_security_type(
            security_type=self.security_type, valid_types=["stock", "etf"]
        )

        # URL of the website to scrape
        url = f"{YAHOO_WEB_BASE_URL}/{self.ticker}/options"
        response = self.get_response(url)

        # Parse the HTML content of the website
        soup = BeautifulSoup(response.content, "html.parser")

        # gets calls and puts
        table = self.find_parent_by_text(soup, "table", "Contract Name")

        headers = [item.text for item in table.find_all("th")]
        data = [
            [item.text for item in row.find_all("td")]
            for row in table.find_all("tr")[1:]
        ]

        data_df = pd.DataFrame(data, columns=headers)

        return data_df

    @property
    def yahoo_web_puts(self) -> pd.DataFrame:
        """
        Get puts for the ticker

        Returns:
        pd.DataFrame: A pandas DataFrame including the puts
        visible in the Yahoo Finance statistics page for the ticker
        """

        check_security_type(
            security_type=self.security_type, valid_types=["stock", "etf"]
        )

        # URL of the website to scrape
        url = f"{YAHOO_WEB_BASE_URL}/{self.ticker}/options"
        response = self.get_response(url)

        # Parse the HTML content of the website
        soup = BeautifulSoup(response.content, "html.parser")

        # gets calls and puts
        table = self.find_parent_by_text(soup, "table", "Contract Name", skip=1)

        headers = [item.text for item in table.find_all("th")]
        data = [
            [item.text for item in row.find_all("td")]
            for row in table.find_all("tr")[1:]
        ]

        data_df = pd.DataFrame(data, columns=headers)

        return data_df

    @property
    def yahoo_web_description(self) -> str:
        """
        Get the description of the ticker

        Returns:
        str: A string including the description of the ticker
        visible in the Yahoo Finance profile page for the ticker
        """

        # URL of the website to scrape
        url = f"{YAHOO_WEB_BASE_URL}/{self.ticker}/profile"
        response = self.get_response(url)

        # Parse the HTML content of the website
        soup = BeautifulSoup(response.content, "html.parser")

        return soup.find("section", {"data-testid": "description"}).find("p").text

    @property
    def yahoo_web_key_executives(self) -> pd.DataFrame:
        """
        Get profile key executives for the ticker

        Returns:
        pd.DataFrame: A pandas DataFrame including the profile key executives
        visible in the Yahoo Finance statistics page for the ticker
        """
        check_security_type(security_type=self.security_type, valid_types=["stock"])

        # URL of the website to scrape
        url = f"{YAHOO_WEB_BASE_URL}/{self.ticker}/profile"
        response = self.get_response(url)

        # Parse the HTML content of the website
        soup = BeautifulSoup(response.content, "html.parser")

        raw_data = soup.find("section", {"data-testid": "key-executives"})

        data_df = pd.DataFrame()
        data = []

        headers = [th.text for th in raw_data.find("thead").find("tr").find_all("th")]
        for tr in raw_data.find("tbody").find_all("tr"):
            data.append([td.text for td in tr.find_all("td")])

        data_df = pd.DataFrame(data, columns=headers)

        return data_df

    @property
    def yahoo_web_corporate_governance(self) -> str:
        """
        Get the description of the ticker

        Returns:
        str: A string including the description of the ticker
        visible in the Yahoo Finance profile page for the ticker
        """
        check_security_type(security_type=self.security_type, valid_types=["stock"])

        # URL of the website to scrape
        url = f"{YAHOO_WEB_BASE_URL}/{self.ticker}/profile"
        response = self.get_response(url)

        # Parse the HTML content of the website
        soup = BeautifulSoup(response.content, "html.parser")

        return (
            soup.find("section", {"data-testid": "corporate-governance"})
            .find("div")
            .text
        )

    @property
    def yahoo_web_major_holders(self) -> pd.DataFrame:
        """
        Get major holders for the ticker

        Returns:
        pd.DataFrame: A pandas DataFrame including the major holders
        visible in the Yahoo Finance statistics page for the ticker
        """
        check_security_type(security_type=self.security_type, valid_types=["stock"])

        # URL of the website to scrape
        url = f"{YAHOO_WEB_BASE_URL}/{self.ticker}/holders"
        response = self.get_response(url)

        # Parse the HTML content of the website
        soup = BeautifulSoup(response.content, "html.parser")

        section = soup.find("section", {"data-testid": "holders-major-holders-table"})
        table = section.find("table")

        data_df = pd.DataFrame()
        data = []

        headers, data = [], []

        headers = [item.text for item in table.find_all("th")].append("description")
        data = [
            [item.text for item in row.find_all("td")]
            for row in table.find_all("tr")[1:]
        ]

        data_df = pd.DataFrame(data, columns=headers)

        return data_df

    @property
    def yahoo_web_top_institutional_holders(self) -> pd.DataFrame:
        """
        Get top institutional holders for the ticker

        Returns:
        pd.DataFrame: A pandas DataFrame including the top institutional holders
        visible in the Yahoo Finance statistics page for the ticker
        """
        check_security_type(security_type=self.security_type, valid_types=["stock"])

        # URL of the website to scrape
        url = f"{YAHOO_WEB_BASE_URL}/{self.ticker}/holders"
        response = self.get_response(url)

        # Parse the HTML content of the website
        soup = BeautifulSoup(response.content, "html.parser")

        section = soup.find(
            "section", {"data-testid": "holders-top-institutional-holders"}
        )
        table = section.find("table")

        data_df = pd.DataFrame()
        data = []

        headers, data = [], []

        headers = [item.text for item in table.find_all("th")]
        data = [
            [item.text for item in row.find_all("td")]
            for row in table.find_all("tr")[1:]
        ]

        data_df = pd.DataFrame(data, columns=headers)

        return data_df

    @property
    def yahoo_web_top_mutual_fund_holders(self) -> pd.DataFrame:
        """
        Get top mutual fund holders for the ticker

        Returns:
        pd.DataFrame: A pandas DataFrame including the top mutual fund holders
        visible in the Yahoo Finance statistics page for the ticker
        """
        check_security_type(security_type=self.security_type, valid_types=["stock"])

        # URL of the website to scrape
        url = f"{YAHOO_WEB_BASE_URL}/{self.ticker}/holders"
        response = self.get_response(url)

        # Parse the HTML content of the website
        soup = BeautifulSoup(response.content, "html.parser")
        table = self.find_parent_by_text(
            soup, "div", "Top Institutional Holders"
        ).find_all("tr")

        data_df = pd.DataFrame()
        data = []

        for tr in table:
            data.append([td.text for td in tr.find_all("td")])

        # drop the first row as it is none
        data_df = pd.DataFrame(data[1:])
        data_df.columns = ["holder", "shares", "date_reported", "percentage", "value"]
        return data_df

    @property
    def yahoo_web_summary(self) -> pd.DataFrame:
        """
        Get data for the ticker

        Returns:
        pd.DataFrame: A pandas DataFrame including the data
        visible in the Yahoo Finance first page for the ticker
        """
        check_security_type(security_type=self.security_type, valid_types=["stock"])

        # URL of the website to scrape
        url = f"{YAHOO_WEB_BASE_URL}/{self.ticker}"
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
    def yahoo_web_valuation_measures(self) -> pd.DataFrame:
        """
        Get valuation measures for the ticker

        Returns:
        pd.DataFrame: A pandas DataFrame including the valuation measures
        visible in the Yahoo Finance statistics page for the ticker
        """
        check_security_type(security_type=self.security_type, valid_types=["stock"])

        # URL of the website to scrape
        url = f"{YAHOO_WEB_BASE_URL}/{self.ticker}/key-statistics"
        response = self.get_response(url)

        # Parse the HTML content of the website
        soup = BeautifulSoup(response.content, "html.parser")

        # find element with test Valuation Measures
        parent_section = self.find_parent_by_text(
            soup, "h3", "Valuation Measures"
        ).parent.parent

        # looking for "table svelte-104jbnt"
        table = parent_section.find("table")

        data_df = pd.DataFrame()

        headers = [item.text for item in table.find("thead").find("tr").find_all("th")]
        data_df = pd.DataFrame(columns=headers)

        for row in table.find("tbody").find_all("tr"):
            data = [item.text for item in row.find_all("td")]
            data_df.loc[len(data_df)] = data

        return data_df.set_index("")

    @property
    def yahoo_web_financial_highlights(self) -> pd.DataFrame:
        """
        Get financial highlights for the ticker

        Returns:
        pd.DataFrame: A pandas DataFrame including the financial highlights
        """

        check_security_type(security_type=self.security_type, valid_types=["stock"])

        # URL of the website to scrape
        url = f"{YAHOO_WEB_BASE_URL}/{self.ticker}/key-statistics"
        response = self.get_response(url)

        # Parse the HTML content of the website
        soup = BeautifulSoup(response.content, "html.parser")

        raw_data = soup.find("div", {"data-testid": "stats-highlight"}).find_all(
            "section", recursive=False
        )[0]
        data_df = pd.DataFrame(columns=["Criteria", "Value"])

        sections = raw_data.find_all("section")
        for section in sections:
            for row in section.find("table").find("tbody").find_all("tr"):
                data = [item.text.strip() for item in row.find_all("td")]
                data_df.loc[len(data_df)] = data

        return data_df.set_index("Criteria")

    @property
    def yahoo_web_trading_information(self) -> pd.DataFrame:
        """
        Get trading information for the ticker

        Returns:
        pd.DataFrame: A pandas DataFrame including the trading information
        visible in the Yahoo Finance statistics page for the ticker
        """
        check_security_type(security_type=self.security_type, valid_types=["stock"])

        # URL of the website to scrape
        url = f"{YAHOO_WEB_BASE_URL}/{self.ticker}/key-statistics"
        response = self.get_response(url)

        # Parse the HTML content of the website
        soup = BeautifulSoup(response.content, "html.parser")

        raw_data = soup.find("div", {"data-testid": "stats-highlight"}).find_all(
            "section", recursive=False
        )[1]
        data_df = pd.DataFrame(columns=["Criteria", "Value"])

        sections = raw_data.find_all("section")
        for section in sections:
            for row in section.find("table").find("tbody").find_all("tr"):
                data = [item.text.strip() for item in row.find_all("td")]
                data_df.loc[len(data_df)] = data

        return data_df.set_index("Criteria")

    @property
    def yahoo_web_full_name(self) -> str:
        """
        Get the full name of the ticker

        Returns:
        str: A string including the full name of the ticker
        visible in the Yahoo Finance profile page for the ticker
        """
        check_security_type(security_type=self.security_type, valid_types=["stock"])

        # URL of the website to scrape
        url = f"{YAHOO_WEB_BASE_URL}/{self.ticker}/"
        response = self.get_response(url)

        # Parse the HTML content of the website
        soup = BeautifulSoup(response.content, "html.parser")

        header = self.find_parent_by_text(soup, "h1", f"({self.ticker})")

        # get the word till the first special character including space
        return re.findall(r"[\w\s]+", header.text)[0].strip()

    @property
    def yahoo_web_earnings_estimate(self) -> pd.DataFrame:
        """
        Get earnings estimate for the ticker

        Returns:
        ----------------
        pd.DataFrame: A pandas DataFrame including the earnings estimate
        visible in the Yahoo Finance statistics page for the ticker
        """
        check_security_type(security_type=self.security_type, valid_types=["stock"])

        # URL of the website to scrape
        url = f"{YAHOO_WEB_BASE_URL}/{self.ticker}/analysis"
        response = self.get_response(url)

        # Parse the HTML content of the website
        soup = BeautifulSoup(response.content, "html.parser")

        section = soup.find("section", {"data-testid": "earningsEstimate"})

        # find thead and tbody
        table = section.find("table")

        headers = [item.text for item in table.find("thead").find_all("th")]
        data = [
            [item.text for item in row.find_all("td")]
            for row in table.find("tbody").find_all("tr")
        ]

        data_df = pd.DataFrame(data, columns=headers)

        return data_df

    @property
    def yahoo_web_revenue_estimate(self) -> pd.DataFrame:
        """
        Get revenue estimate for the ticker

        Returns:
        ----------------
        pd.DataFrame: A pandas DataFrame including the revenue estimate
        visible in the Yahoo Finance statistics page for the ticker
        """

        check_security_type(security_type=self.security_type, valid_types=["stock"])

        # URL of the website to scrape
        url = f"{YAHOO_WEB_BASE_URL}/{self.ticker}/analysis"
        response = self.get_response(url)

        # Parse the HTML content of the website
        soup = BeautifulSoup(response.content, "html.parser")

        section = soup.find("section", {"data-testid": "revenueEstimate"})

        # find thead and tbody
        table = section.find("table")

        headers = [item.text for item in table.find("thead").find_all("th")]
        data = [
            [item.text for item in row.find_all("td")]
            for row in table.find("tbody").find_all("tr")
        ]

        data_df = pd.DataFrame(data, columns=headers)

        return data_df

    @property
    def yahoo_web_earnings_history(self) -> pd.DataFrame:
        """
        Get earnings history for the ticker

        Returns:
        ----------------
        pd.DataFrame: A pandas DataFrame including the earnings history
        visible in the Yahoo Finance statistics page for the ticker
        """

        check_security_type(security_type=self.security_type, valid_types=["stock"])

        # URL of the website to scrape
        url = f"{YAHOO_WEB_BASE_URL}/{self.ticker}/analysis"
        response = self.get_response(url)

        # Parse the HTML content of the website
        soup = BeautifulSoup(response.content, "html.parser")

        section = soup.find("section", {"data-testid": "earningsHistory"})

        # find thead and tbody
        table = section.find("table")

        headers = [item.text for item in table.find("thead").find_all("th")]
        data = [
            [item.text for item in row.find_all("td")]
            for row in table.find("tbody").find_all("tr")
        ]

        data_df = pd.DataFrame(data, columns=headers)

        return data_df

    @property
    def yahoo_web_eps_trend(self) -> pd.DataFrame:
        """
        Get EPS trend for the ticker

        Returns:
        ----------------
        pd.DataFrame: A pandas DataFrame including the EPS trend
        visible in the Yahoo Finance statistics page for the ticker
        """

        check_security_type(security_type=self.security_type, valid_types=["stock"])

        # URL of the website to scrape
        url = f"{YAHOO_WEB_BASE_URL}/{self.ticker}/analysis"
        response = self.get_response(url)

        # Parse the HTML content of the website
        soup = BeautifulSoup(response.content, "html.parser")

        section = soup.find("section", {"data-testid": "epsTrend"})

        # find thead and tbody
        table = section.find("table")

        headers = [item.text for item in table.find("thead").find_all("th")]
        data = [
            [item.text for item in row.find_all("td")]
            for row in table.find("tbody").find_all("tr")
        ]

        data_df = pd.DataFrame(data, columns=headers)

        return data_df

    @property
    def yahoo_web_eps_revisions(self) -> pd.DataFrame:
        """
        Get EPS revisions for the ticker

        Returns:
        ----------------
        pd.DataFrame: A pandas DataFrame including the EPS revisions
        visible in the Yahoo Finance statistics page for the ticker
        """

        check_security_type(security_type=self.security_type, valid_types=["stock"])

        # URL of the website to scrape
        url = f"{YAHOO_WEB_BASE_URL}/{self.ticker}/analysis"
        response = self.get_response(url)

        # Parse the HTML content of the website
        soup = BeautifulSoup(response.content, "html.parser")

        section = soup.find("section", {"data-testid": "epsRevisions"})

        # find thead and tbody
        table = section.find("table")

        headers = [item.text for item in table.find("thead").find_all("th")]
        data = [
            [item.text for item in row.find_all("td")]
            for row in table.find("tbody").find_all("tr")
        ]

        data_df = pd.DataFrame(data, columns=headers)

        return data_df

    @property
    def yahoo_web_growth_estimates(self) -> pd.DataFrame:
        """
        Get growth estimates for the ticker

        Returns:
        ----------------
        pd.DataFrame: A pandas DataFrame including the growth estimates
        visible in the Yahoo Finance statistics page for the ticker
        """

        check_security_type(security_type=self.security_type, valid_types=["stock"])

        # URL of the website to scrape
        url = f"{YAHOO_WEB_BASE_URL}/{self.ticker}/analysis"
        response = self.get_response(url)

        # Parse the HTML content of the website
        soup = BeautifulSoup(response.content, "html.parser")

        section = soup.find("section", {"data-testid": "growthEstimate"})

        # find thead and tbody
        table = section.find("table")

        headers = [item.text for item in table.find("thead").find_all("th")]
        data = [
            [item.text for item in row.find_all("td")]
            for row in table.find("tbody").find_all("tr")
        ]

        data_df = pd.DataFrame(data, columns=headers)

        return data_df
