"""
Module for interfacing with the Macrotrends website.
"""

import re
from functools import lru_cache
from typing import Literal, Union

import pandas as pd
import plotly.express as px
from bs4 import BeautifulSoup

from stockdex.config import MACROTRENDS_BASE_URL, VALID_SECURITY_TYPES
from stockdex.exceptions import FieldNotExists
from stockdex.lib import check_security_type, plot_dataframe
from stockdex.selenium_interface import selenium_interface
from stockdex.ticker_base import TickerBase


class MacrotrendsInterface(TickerBase):
    """
    Interface for interacting with the Macrotrends website.
    """

    def __init__(
        self,
        ticker: str = "",
        isin: str = "",
        security_type: VALID_SECURITY_TYPES = "stock",
    ) -> None:
        self.isin = isin
        self.ticker = ticker
        self.security_type = security_type

    @property
    @lru_cache(maxsize=None)
    def full_name(self) -> str:
        """
        Retrieve the full name of the security.
        """
        full_name = self.yahoo_web_full_name
        full_name = full_name.replace(" ", "-").lower()

        return full_name

    def _find_table_in_url(
        self, text_to_look_for: str, soup: BeautifulSoup
    ) -> pd.DataFrame:
        """
        Retrieve the table with the given id from the given URL.

        Args:
        ----------
        url: str
            The URL to retrieve the table from.
        text_to_look_for: str
            The text to look for in the table.

        Returns:
        ----------
        pd.DataFrame
            The table as a pandas DataFrame.
        """
        table = self.find_parent_by_text(soup=soup, tag="div", text=text_to_look_for)

        data = []
        # get var originalData from the table
        for script in table.find_all("script"):
            if "originalData" in script.get_text():
                original_data = script.get_text()
                break

        # get the data from the script
        for line in original_data.split("\n"):
            if "originalData" in line:
                data = line.split(" = ")[1]
                break

        # convert the data to a pandas DataFrame
        data = data.replace(";", "")
        data = data.replace("null", "None")
        data = data.replace("\\/", "/")
        data = eval(data)
        data = pd.DataFrame(data)

        return data

    @lru_cache(maxsize=None)
    def macrotrends_income_statement(
        self, frequency: Literal["quarterly", "annual"]
    ) -> pd.DataFrame:
        """
        Retrieve the income statement for the given ticker.
        """
        check_security_type(self.security_type, valid_types=["stock"])
        frequency_suffix = "?freq=A" if frequency == "annual" else "?freq=Q"

        url = (
            f"{MACROTRENDS_BASE_URL}/{self.ticker}/{self.get_company_slug(self.ticker)}/income-statement{frequency_suffix}"  # Noqa E501
            if frequency == "quarterly"
            else f"{MACROTRENDS_BASE_URL}/{self.ticker}/TBD/income-statement{frequency_suffix}"
        )

        response = self.get_response(url)

        # Parse the HTML content of the website
        soup = BeautifulSoup(response.content, "html.parser")

        data = self._find_table_in_url("Revenue", soup)

        data["field_name"] = data["field_name"].apply(
            lambda x: re.search(">(.*)<", x).group(1)
        )
        data = data.set_index("field_name")
        data.drop(columns=["popup_icon"], inplace=True)

        return data

    @lru_cache(maxsize=None)
    def macrotrends_balance_sheet(
        self, frequency: Literal["quarterly", "annual"]
    ) -> pd.DataFrame:
        """
        Retrieve the balance sheet for the given ticker.
        """
        check_security_type(self.security_type, valid_types=["stock"])
        frequency_suffix = "?freq=A" if frequency == "annual" else "?freq=Q"

        url = (
            f"{MACROTRENDS_BASE_URL}/{self.ticker}/{self.get_company_slug(self.ticker)}/balance-sheet{frequency_suffix}"  # Noqa E501
            if frequency == "quarterly"
            else f"{MACROTRENDS_BASE_URL}/{self.ticker}/TBD/balance-sheet{frequency_suffix}"
        )

        # build selenium interface object if not already built
        if not hasattr(self, "selenium_interface"):
            self.selenium_interface = selenium_interface()

        soup = self.selenium_interface.get_html_content(url)

        data = self._find_table_in_url("Cash On Hand", soup)

        data["field_name"] = data["field_name"].apply(
            lambda x: re.search(">(.*)<", x).group(1)
        )
        data = data.set_index("field_name")
        data.drop(columns=["popup_icon"], inplace=True)

        return data

    @lru_cache(maxsize=None)
    def macrotrends_cash_flow(
        self, frequency: Literal["quarterly", "annual"]
    ) -> pd.DataFrame:
        """
        Retrieve the cash flow statement for the given ticker.
        """
        check_security_type(self.security_type, valid_types=["stock"])
        frequency_suffix = "?freq=A" if frequency == "annual" else "?freq=Q"

        url = (
            f"{MACROTRENDS_BASE_URL}/{self.ticker}/{self.get_company_slug(self.ticker)}/cash-flow-statement{frequency_suffix}"  # Noqa E501
            if frequency == "quarterly"
            else f"{MACROTRENDS_BASE_URL}/{self.ticker}/TBD/cash-flow-statement{frequency_suffix}"
        )

        # build selenium interface object if not already built
        if not hasattr(self, "selenium_interface"):
            self.selenium_interface = selenium_interface()

        soup = self.selenium_interface.get_html_content(url)

        data = self._find_table_in_url("Net Income/Loss", soup)

        data["field_name"] = data["field_name"].apply(
            lambda x: re.search(">(.*)<", x).group(1)
        )
        data = data.set_index("field_name")
        data.drop(columns=["popup_icon"], inplace=True)

        return data

    @property
    @lru_cache(maxsize=None)
    def macrotrends_key_financial_ratios(self) -> pd.DataFrame:
        """
        Retrieve the key financial ratios for the given ticker.
        """
        check_security_type(self.security_type, valid_types=["stock"])
        url = f"{MACROTRENDS_BASE_URL}/{self.ticker}/TBD/financial-ratios"

        # build selenium interface object if not already built
        if not hasattr(self, "selenium_interface"):
            self.selenium_interface = selenium_interface()

        soup = self.selenium_interface.get_html_content(url)

        data = self._find_table_in_url("Current Ratio", soup)

        data["field_name"] = data["field_name"].apply(
            lambda x: re.search(">(.*)<", x).group(1)
        )
        data = data.set_index("field_name")
        data.drop(columns=["popup_icon"], inplace=True)

        return data

    def _find_margins_table(self, url: str, text_to_look_for: str):
        response = self.get_response(url)

        # Parse the HTML content of the website
        soup = BeautifulSoup(response.content, "html.parser")

        data = []
        headers = []

        table = self.find_parent_by_text(soup=soup, tag="table", text=text_to_look_for)

        headers = [
            row.text
            for row in table.find_all("thead")[1].find_all("tr")[0].find_all("th")
        ]
        data = [
            [cell.text for cell in row.find_all("td")]
            for row in table.find_all("tr")[1:]
        ]
        data = pd.DataFrame(data, columns=headers)

        return data

    @property
    @lru_cache(maxsize=None)
    def macrotrends_operating_margin(self) -> pd.DataFrame:
        """
        Retrieve the operating margin for the given ticker.
        """
        check_security_type(self.security_type, valid_types=["stock"])
        url = f"{MACROTRENDS_BASE_URL}/{self.ticker}/TBD/operating-margin"

        return self._find_margins_table(url, "TTM Operating Income")

    @property
    @lru_cache(maxsize=None)
    def macrotrends_gross_margin(self) -> pd.DataFrame:
        """
        Retrieve the gross margin for the given ticker.
        """
        check_security_type(self.security_type, valid_types=["stock"])
        url = f"{MACROTRENDS_BASE_URL}/{self.ticker}/TBD/gross-margin"

        return self._find_margins_table(url, "Gross Margin")

    @property
    @lru_cache(maxsize=None)
    def macrotrends_ebitda_margin(self) -> pd.DataFrame:
        """
        Retrieve the EBITDA margin for the given ticker.
        """
        check_security_type(self.security_type, valid_types=["stock"])
        url = f"{MACROTRENDS_BASE_URL}/{self.ticker}/TBD/ebitda-margin"

        return self._find_margins_table(url, "TTM EBITDA")

    @property
    @lru_cache(maxsize=None)
    def macrotrends_pre_tax_margin(self) -> pd.DataFrame:
        """
        Retrieve the pre-tax margin for the given ticker.
        """
        check_security_type(self.security_type, valid_types=["stock"])
        url = f"{MACROTRENDS_BASE_URL}/{self.ticker}/TBD/pre-tax-profit-margin"

        return self._find_margins_table(url, "TTM Pre-Tax Income")

    @property
    @lru_cache(maxsize=None)
    def macrotrends_net_margin(self) -> pd.DataFrame:
        """
        Retrieve the net profit margin for the given ticker.
        """
        check_security_type(self.security_type, valid_types=["stock"])
        url = f"{MACROTRENDS_BASE_URL}/{self.ticker}/TBD/net-profit-margin"

        return self._find_margins_table(url, "TTM Net Income")

    @lru_cache(maxsize=None)
    def macrotrends_revenue(
        self, frequency: Literal["annual", "quarterly"] = "annual"
    ) -> pd.DataFrame:
        """
        Retrieve the revenue for the given ticker.
        """
        check_security_type(self.security_type, valid_types=["stock"])
        url = f"{MACROTRENDS_BASE_URL}/{self.ticker}/TBD/revenue"

        # build selenium interface object if not already built
        if not hasattr(self, "selenium_interface"):
            self.selenium_interface = selenium_interface()

        soup = self.selenium_interface.get_html_content(url)

        # find tables with class = historical_data_table
        tables = soup.find_all("table", class_="historical_data_table")

        if frequency == "annual":
            df = pd.read_html(str(tables[0]))[0]
        elif frequency == "quarterly":
            df = pd.read_html(str(tables[1]))[0]

        return df

    @lru_cache(maxsize=None)
    def plot_macrotrends_income_statement(
        self,
        fields_to_include: list = ["Revenue", "Income After Taxes"],
        frequency: Literal["annual", "quarterly"] = "annual",
        group_by: Literal["field", "timeframe"] = "timeframe",
        show_plot: bool = True,
    ) -> Union[px.line, px.bar]:
        """
        Plot the income statement for the given ticker.

        Args:
        ----------
        fields_to_include : list
            The fields to include in the plot.
        frequency : Literal["annual", "quarterly"]
            The frequency of the data to plot.
        group_by : Literal["field", "timeframe"]
            The level at which to group the data.
        show_plot : bool
            If the plot should be shown or not.
            If dash is used, this should be set to False
            Default is True (show the plot)

        Returns:
        ----------------
        Union[px.line, px.bar]: The plotly figure
        """
        df = self._transform_df_for_plotting_macrotrends(
            self.macrotrends_income_statement(frequency=frequency),
            fields_to_include,
            group_by,
        )

        fig = plot_dataframe(
            df,
            title=f"{self.ticker} Income Statement (from Macrotrends)",
            show_plot=show_plot,
        )

        return fig

    def plot_macrotrends_balance_sheet(
        self,
        fields_to_include: list = ["Cash On Hand", "Total Assets", "Total Liabilities"],
        frequency: Literal["annual", "quarterly"] = "annual",
        group_by: Literal["field", "timeframe"] = "timeframe",
        show_plot: bool = True,
    ) -> Union[px.line, px.bar]:
        """
        Plot the balance sheet for the given ticker.

        Args:
        ----------
        fields_to_include : list
            The fields to include in the plot.
        frequency : Literal["annual", "quarterly"]
            The frequency of the data to plot.
        group_by : Literal["field", "timeframe"]
            The level at which to group the data.
        show_plot : bool
            If the plot should be shown or not.
            If dash is used, this should be set to False
            Default is True (show the plot)

        Returns:
        ----------------
        Union[px.line, px.bar]: The plotly figure
        """
        df = self._transform_df_for_plotting_macrotrends(
            self.macrotrends_balance_sheet(frequency=frequency),
            fields_to_include,
            group_by,
        )

        fig = plot_dataframe(
            df,
            title=f"{self.ticker} Balance Sheet (from Macrotrends)",
            show_plot=show_plot,
        )

        return fig

    def plot_macrotrends_cash_flow(
        self,
        fields_to_include: list = [
            r"Net Income/Loss",  # noqa: W605
            "Common Stock Dividends Paid",
            "Net Long-Term Debt",
        ],
        frequency: Literal["annual", "quarterly"] = "annual",
        group_by: Literal["field", "timeframe"] = "timeframe",
        show_plot: bool = True,
    ) -> None:
        """
        Plot the cash flow statement for the given ticker.

        Args:
        ----------
        fields_to_include : list
            The fields to include in the plot.
        frequency : Literal["annual", "quarterly"]
            The frequency of the data to plot.
        group_by : Literal["field", "timeframe"]
            The level at which to group the data.
        show_plot : bool
            If the plot should be shown or not.
            If dash is used, this should be set to False
            Default is True (show the plot)

        Returns:
        ----------------
        Union[px.line, px.bar]: The plotly figure
        """
        df = self._transform_df_for_plotting_macrotrends(
            self.macrotrends_cash_flow(frequency=frequency), fields_to_include, group_by
        )

        fig = plot_dataframe(
            df,
            title=f"{self.ticker} Cash Flow Statement (from Macrotrends) using {frequency} data",
            show_plot=show_plot,
        )

        return fig

    def _transform_df_for_plotting_macrotrends(
        self, df: pd.DataFrame, fields_to_include: list, group_by: str
    ) -> pd.DataFrame:
        """
        Transform the DataFrame for plotting.

        Parameters:
        ----------
        df: pd.DataFrame
            The DataFrame to transform.

        fields_to_include: list
            The fields to include in the DataFrame.

        group_by: str
            The way to group the DataFrame.

        Returns:
        ----------
        pd.DataFrame
            The transformed DataFrame.
        """

        for field in fields_to_include:
            if field not in df.index:
                raise FieldNotExists(
                    f"The field {field} does not exist in the DataFrame."
                )

        df = df.loc[fields_to_include]

        # set index name
        df.index.name = "field_name"

        # fill NaN values with 0
        df = df.fillna(0)

        # convert all values to float if they are not and replace empty cells with 0
        df = df.replace(r"^\s*$", "0", regex=True).applymap(
            lambda x: float(x.replace(",", "")) if isinstance(x, str) else x
        )

        # sort index in ascending order
        df = df.T.sort_index()

        if group_by == "field":
            df = df.T

        return df
