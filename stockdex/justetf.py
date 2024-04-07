"""
Module for extracting ETF data from JustETF website
"""

from typing import Literal

import pandas as pd
from bs4 import BeautifulSoup

from stockdex import config
from stockdex.exceptions import NoISINError
from stockdex.selenium_interface import selenium_interface
from stockdex.ticker_base import TickerBase


class JustETF(TickerBase):
    def __init__(
        self,
        ticker: str = "",
        isin: str = "",
        security_type: str = Literal["stock", "etf"],
    ) -> None:
        self.isin = isin
        self.ticker = ticker
        self.security_type = security_type
        if not isin or isin == "":
            raise NoISINError("No ISIN provided, please provide an ISIN")

    @property
    def etf_general_info(self) -> pd.DataFrame:
        """
        Get the general information of the ETF
        genral information includes TER, distribution policy, replication method, etc.
        """
        url = f"{config.JUSTETF_BASE_URL}/etf-profile.html?isin={self.isin}"
        response = self.get_response(url)

        soup = BeautifulSoup(response.text, "html.parser")

        data_df = pd.DataFrame()

        general_info = soup.find("div", {"class": "data-overview mt-4 mb-3"})
        labels = general_info.find_all("div", {"class": "vallabel"})

        for label in labels:
            column = label.text.replace(" ", "")
            value = label.find_next_sibling("div").text

            data_df[column] = [value]

        return data_df

    @property
    def etf_wkn(self) -> str:
        """
        Get the WKN of the ETF
        """
        url = f"{config.JUSTETF_BASE_URL}/etf-profile.html?isin={self.isin}"
        response = self.get_response(url)

        soup = BeautifulSoup(response.text, "html.parser")

        wkn = soup.find("span", {"id": "etf-second-id"}).text

        return wkn

    @property
    def etf_description(self) -> str:
        """
        Get the description of the ETF
        """
        url = f"{config.JUSTETF_BASE_URL}/etf-profile.html?isin={self.isin}"
        response = self.get_response(url)

        soup = BeautifulSoup(response.text, "html.parser")

        description = soup.find("div", {"id": "etf-description"}).text

        return description

    # @property
    # def etf_quote(self) -> pd.DataFrame:
    #     """
    #     Get the quote of the ETF

    #     columns may include:
    #     - Currency
    #     - Price

    #     Args:
    #     ----------------
    #     isin (str): ISIN of the ETF

    #     Returns:
    #     ----------------
    #     pd.DataFrame: DataFrame containing the quote of the ETF
    #     """
    #     url = f"{config.JUSTETF_BASE_URL}/etf-profile.html?isin={self.isin}"

    #     # build selenium interface object if not already built
    #     if not hasattr(self, "selenium_interface"):
    #         self.selenium_interface = selenium_interface()

    #     soup = self.selenium_interface.get_html_content(url)

    #     data_df = pd.DataFrame()

    #     quote = soup.find("div", {"id": "realtime-quotes"})
    #     currency, price = tuple(
    #         quote.find("div", {"class": "col-xs-7"})
    #         .find("div", {"class": "val"})
    #         .text.split(" ")
    #     )

    #     data_df["currency"] = [currency]
    #     data_df["price"] = [price]

    @property
    def etf_basics(self) -> pd.DataFrame:
        """
        Get the baisc information of the ETF

        columns may include:
        - Fund size
        - Fund domicile
        - Legal structure
        - Replication

        Args:
        ----------------
        isin (str): ISIN of the ETF

        Returns:
        ----------------
        pd.DataFrame: DataFrame containing the basic information of the ETF
        """
        url = f"{config.JUSTETF_BASE_URL}/etf-profile.html?isin={self.isin}#basics"

        # build selenium interface object if not already built
        if not hasattr(self, "selenium_interface"):
            self.selenium_interface = selenium_interface()

        soup = self.selenium_interface.get_html_content(url)

        data_df = pd.DataFrame()

        table = soup.find("table", {"class": "table etf-data-table"})

        for row in table.find_all("tr"):
            column = row.find_all("td")
            data_df[column[0].text.strip()] = [column[1].text.strip()]

        return data_df

    @property
    def etf_holdings_companies(self) -> pd.DataFrame:
        """
        Get the top 10 holdings of the ETF by companies

        columns may include:
        - company name
        - shares in percent

        Args:
        ----------------
        isin (str): ISIN of the ETF

        Returns:
        ----------------
        pd.DataFrame: DataFrame containing the holdings of the ETF
        """
        url = f"{config.JUSTETF_BASE_URL}/etf-profile.html?isin={self.isin}#holdings"

        # build selenium interface object if not already built
        if not hasattr(self, "selenium_interface"):
            self.selenium_interface = selenium_interface()

        soup = self.selenium_interface.get_html_content(url)

        data_df = pd.DataFrame()
        companies = []
        shares_percent = []

        table_body = (
            soup.find(lambda tag: tag.name == "h3" and "Top 10 Holdings" in tag.text)
            .find_next("table")
            .find("tbody")
        )

        for row in table_body.find_all("tr"):
            columns = row.find_all("td")
            companies.append(columns[0].text.strip())
            shares_percent.append(columns[1].text.strip())

        data_df["company name"] = companies
        data_df["shares in percent"] = shares_percent
        data_df.set_index("company name", inplace=True)

        return data_df

    @property
    def etf_holdings_countries(self) -> pd.DataFrame:
        """
        Get the top 10 holdings of the ETF by countries

        columns may include:
        - country name
        - shares in percent

        Args:
        ----------------
        isin (str): ISIN of the ETF

        Returns:
        ----------------
        pd.DataFrame: DataFrame containing the holdings of the ETF
        """
        url = f"{config.JUSTETF_BASE_URL}/etf-profile.html?isin={self.isin}#holdings"

        # build selenium interface object if not already built
        if not hasattr(self, "selenium_interface"):
            self.selenium_interface = selenium_interface()

        soup = self.selenium_interface.get_html_content(url)

        data_df = pd.DataFrame()
        countries = []
        shares_percent = []

        table_body = (
            soup.find(lambda tag: tag.name == "h3" and "Countries" in tag.text)
            .find_next("table")
            .find("tbody")
        )

        for row in table_body.find_all("tr"):
            columns = row.find_all("td")
            countries.append(columns[0].text.strip())
            shares_percent.append(columns[1].text.strip())

        data_df["country name"] = countries
        data_df["shares in percent"] = shares_percent
        data_df.set_index("country name", inplace=True)

        return data_df

    @property
    def etf_holdings_sectors(self) -> pd.DataFrame:
        """
        Get the top 10 holdings of the ETF by sectors

        columns may include:
        - sector name
        - shares in percent

        Args:
        ----------------
        isin (str): ISIN of the ETF

        Returns:
        ----------------
        pd.DataFrame: DataFrame containing the holdings of the ETF
        """
        url = f"{config.JUSTETF_BASE_URL}/etf-profile.html?isin={self.isin}#holdings"

        # build selenium interface object if not already built
        if not hasattr(self, "selenium_interface"):
            self.selenium_interface = selenium_interface()

        soup = self.selenium_interface.get_html_content(url)

        data_df = pd.DataFrame()
        sectors = []
        shares_percent = []

        table_body = (
            soup.find(lambda tag: tag.name == "h3" and "Sectors" in tag.text)
            .find_next("table")
            .find("tbody")
        )

        for row in table_body.find_all("tr"):
            columns = row.find_all("td")
            sectors.append(columns[0].text.strip())
            shares_percent.append(columns[1].text.strip())

        data_df["sector name"] = sectors
        data_df["shares in percent"] = shares_percent
        data_df.set_index("sector name", inplace=True)

        return data_df
