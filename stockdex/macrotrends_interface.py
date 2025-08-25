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

    # ---------- Income Statement Methods with LRU Cache ----------

    @lru_cache(maxsize=None)
    def _get_macrotrends_income_statement_annual(self) -> pd.DataFrame:
        """
        Retrieve the annual income statement for the given ticker.
        This method is cached to prevent repeated API calls.
        """
        return self._get_macrotrends_income_statement(freq="annual")

    @lru_cache(maxsize=None)
    def _get_macrotrends_income_statement_quarterly(self) -> pd.DataFrame:
        """
        Retrieve the quarterly income statement for the given ticker.
        This method is cached to prevent repeated API calls.
        """
        return self._get_macrotrends_income_statement(freq="quarterly")

    @property
    def macrotrends_income_statement_annual(self) -> pd.DataFrame:
        return self._get_macrotrends_income_statement_annual()

    @property
    def macrotrends_income_statement_quarterly(self) -> pd.DataFrame:
        return self._get_macrotrends_income_statement_quarterly()

    @property
    def macrotrends_income_statement(self) -> pd.DataFrame:
        """
        So we don't break anything currently running the old way.
        We could or should put a deprecated tag on this.
        """
        return self._get_macrotrends_income_statement_annual()

    def _get_macrotrends_income_statement(self, freq: str) -> pd.DataFrame:
        """
        Retrieve the income statement for the given ticker, with annual or quarterly frequency.
        freq: "annual" or "quarterly" (case insensitive); default is "annual".
        """
        check_security_type(self.security_type, valid_types=["stock"])
        freq_map = {"annual": "A", "quarterly": "Q"}
        freq_clean = str(freq).strip().lower()
        freq_param = freq_map.get(freq_clean, "A")  # Default to "A"
        url = f"{MACROTRENDS_BASE_URL}/{self.ticker}/TBD/income-statement?freq={freq_param}"
        response = self.get_response(url)
        soup = BeautifulSoup(response.content, "html.parser")
        data = self._find_table_in_url("Revenue", soup)
        data["field_name"] = data["field_name"].apply(
            lambda x: re.search(">(.*)<", x).group(1)
        )
        data = data.set_index("field_name")
        data.drop(columns=["popup_icon"], inplace=True)
        return data

    # ---------- Balance Sheet Methods with LRU Cache ----------

    @lru_cache(maxsize=None)
    def _get_macrotrends_balance_sheet_annual(self) -> pd.DataFrame:
        """
        Retrieve the annual balance sheet for the given ticker.
        This method is cached to prevent repeated API calls.
        """
        return self._get_macrotrends_balance_sheet(freq="annual")

    @lru_cache(maxsize=None)
    def _get_macrotrends_balance_sheet_quarterly(self) -> pd.DataFrame:
        """
        Retrieve the quarterly balance sheet for the given ticker.
        This method is cached to prevent repeated API calls.
        """
        return self._get_macrotrends_balance_sheet(freq="quarterly")

    @property
    def macrotrends_balance_sheet_annual(self) -> pd.DataFrame:
        return self._get_macrotrends_balance_sheet_annual()

    @property
    def macrotrends_balance_sheet_quarterly(self) -> pd.DataFrame:
        return self._get_macrotrends_balance_sheet_quarterly()

    @property
    def macrotrends_balance_sheet(self) -> pd.DataFrame:
        """
        So we don't break anything currently running the old way.
        We could or should put a deprecated tag on this.
        """
        return self._get_macrotrends_balance_sheet_annual()

    def _get_macrotrends_balance_sheet(self, freq: str = "annual") -> pd.DataFrame:
        """
        Retrieve the balance sheet for the given ticker, with annual or quarterly frequency.
        freq: "annual" or "quarterly" (case insensitive); default is "annual".
        """
        check_security_type(self.security_type, valid_types=["stock"])
        freq_map = {"annual": "A", "quarterly": "Q"}
        freq_clean = str(freq).strip().lower()
        freq_param = freq_map.get(freq_clean, "A")  # Default to "A"
        url = f"{MACROTRENDS_BASE_URL}/{self.ticker}/TBD/balance-sheet?freq={freq_param}"

        # build selenium interface object if not already built
        if not hasattr(self, "selenium_interface"):
            self.selenium_interface = selenium_interface()

        soup = self.selenium_interface.get_html_content(url)

        # first row value marker to locate and validate the table.  
        # if this is changed or replaced, no soup for you.
        data = self._find_table_in_url("Cash On Hand", soup)

        data["field_name"] = data["field_name"].apply(
            lambda x: re.search(">(.*)<", x).group(1)
        )
        data = data.set_index("field_name")
        data.drop(columns=["popup_icon"], inplace=True)

        return data

    # ---------- Cash Flow Methods with LRU Cache ----------

    @lru_cache(maxsize=None)
    def _get_macrotrends_cashflow_statement_annual(self) -> pd.DataFrame:
        """
        Retrieve the annual cash flow statement for the given ticker.
        This method is cached to prevent repeated API calls.
        """
        return self._get_macrotrends_cashflow_statement(freq="annual")

    @lru_cache(maxsize=None)
    def _get_macrotrends_cashflow_statement_quarterly(self) -> pd.DataFrame:
        """
        Retrieve the quarterly cash flow statement for the given ticker.
        This method is cached to prevent repeated API calls.
        """
        return self._get_macrotrends_cashflow_statement(freq="quarterly")

    @property
    def macrotrends_cashflow_statement_annual(self) -> pd.DataFrame:
        return self._get_macrotrends_cashflow_statement_annual()

    @property
    def macrotrends_cashflow_statement_quarterly(self) -> pd.DataFrame:
        return self._get_macrotrends_cashflow_statement_quarterly()

    @property
    def macrotrends_cashflow_statement(self) -> pd.DataFrame:
        """
        So we don't break anything currently running the old way.
        We could or should put a deprecated tag on this.
        """
        return self._get_macrotrends_cashflow_statement_annual()

    def _get_macrotrends_cashflow_statement(self, freq: str = "annual") -> pd.DataFrame:
        """
        Retrieve the cash flow statement for the given ticker, with annual or quarterly frequency.
        freq: "annual" or "quarterly" (case insensitive); default is "annual".
        """
        check_security_type(self.security_type, valid_types=["stock"])
        freq_map = {"annual": "A", "quarterly": "Q"}
        freq_clean = str(freq).strip().lower()
        freq_param = freq_map.get(freq_clean, "A")  # Default to "A"
        url = f"{MACROTRENDS_BASE_URL}/{self.ticker}/TBD/cash-flow-statement?freq={freq_param}"

        # build selenium interface object if not already built
        if not hasattr(self, "selenium_interface"):
            self.selenium_interface = selenium_interface()

        soup = self.selenium_interface.get_html_content(url)

        # --- DEBUG: check if HTML was actually fetched ---
        if soup is None or len(soup.text.strip()) == 0:
            raise ValueError(f"No HTML returned for {self.ticker} at {url}")

        # first row value marker to locate and validate the table.  
        # if this is changed or replaced, no soup for you.
        data = self._find_table_in_url("Net Income/Loss", soup)
        # --- DEBUG: check if table was found ---
        if data is None:
            # Optionally, list all tables found
            all_tables = soup.find_all("table")
            for i, t in enumerate(all_tables):
                text_snippet = t.get_text(strip=True)[:100]
                print(f"Table {i} snippet: {text_snippet}")
            raise ValueError("Cannot continue, table not found")

        # for some reason the cash flow table comes in with duplicate columns. not sure why.
        # Remove duplicate columns by column name, keep first occurrence
        # TODO: we should probably check those other statements more thoroughly also.
        data = data.loc[:, ~data.columns.duplicated()].copy()
        # At this point, data should be a DataFrame
        # print(f"Columns before renaming: {data.columns.tolist()}")

        # Extract the field_name
        def extract_field_name(x):
            m = re.search(">(.*)<", x)
            return m.group(1) if m else x

        data["field_name"] = data["field_name"].apply(extract_field_name)
        data = data.set_index("field_name")
        data.drop(columns=["popup_icon"], inplace=True)

        return data

    @property
    def macrotrends_key_financial_ratios(self) -> pd.DataFrame:
        """
        Retrieve the key financial ratios for the given ticker.
        NOTE: the financial ratios are all encompassing ANNUAL ratios
              from period X to period Y. this is a time and processing
              saver if you are wanting annual ratios in a fell swoop.
              if you want quarterly ratios you will need to self-calculate 
              those from the statements yourself.
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
    def macrotrends_operating_margin(self) -> pd.DataFrame:
        """
        Retrieve the operating margin for the given ticker.
        NOTE: this call does not seem to work with a frequency parameter.
              but it DOES have parameters for the graphs which are 
              currently unsupported.
        """
        check_security_type(self.security_type, valid_types=["stock"])
        url = f"{MACROTRENDS_BASE_URL}/{self.ticker}/TBD/operating-margin"

        return self._find_margins_table(url, "TTM Operating Income")

    @property
    def macrotrends_gross_margin(self) -> pd.DataFrame:
        """
        Retrieve the gross margin for the given ticker.
        NOTE: this call does not seem to work with a frequency parameter.
              but it DOES have parameters for the graphs which are 
              currently unsupported.
        """
        check_security_type(self.security_type, valid_types=["stock"])
        url = f"{MACROTRENDS_BASE_URL}/{self.ticker}/TBD/gross-margin"

        return self._find_margins_table(url, "Gross Margin")

    @property
    def macrotrends_ebitda_margin(self) -> pd.DataFrame:
        """
        Retrieve the EBITDA margin for the given ticker.
        NOTE: this call does not seem to work with a frequency parameter.
              but it DOES have parameters for the graphs which are 
              currently unsupported.
        """
        check_security_type(self.security_type, valid_types=["stock"])
        url = f"{MACROTRENDS_BASE_URL}/{self.ticker}/TBD/ebitda-margin"

        return self._find_margins_table(url, "TTM EBITDA")

    @property
    def macrotrends_pre_tax_margin(self) -> pd.DataFrame:
        """
        Retrieve the pre-tax margin for the given ticker.
        NOTE: this call does not seem to work with a frequency parameter.
              but it DOES have parameters for the graphs which are 
              currently unsupported.
        """
        check_security_type(self.security_type, valid_types=["stock"])
        url = f"{MACROTRENDS_BASE_URL}/{self.ticker}/TBD/pre-tax-profit-margin"

        return self._find_margins_table(url, "TTM Pre-Tax Income")

    @property
    def macrotrends_net_margin(self) -> pd.DataFrame:
        """
        Retrieve the net profit margin for the given ticker.
        NOTE: this call does not seem to work with a frequency parameter.
              but it DOES have parameters for the graphs which are 
              currently unsupported.
        """
        check_security_type(self.security_type, valid_types=["stock"])
        url = f"{MACROTRENDS_BASE_URL}/{self.ticker}/TBD/net-profit-margin"

        return self._find_margins_table(url, "TTM Net Income")

    def macrotrends_revenue(
        self, frequency: Literal["annual", "quarterly"] = "annual"
    ) -> pd.DataFrame:
        """
        Retrieve the revenue for the given ticker.
        NOTE: this call does not seem to work with a frequency parameter.
              but it DOES have parameters for the graphs which are 
              currently unsupported.
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

    def plot_macrotrends_income_statement(
        self,
        fields_to_include: list = ["Revenue", "Income After Taxes"],
        group_by: Literal["field", "timeframe"] = "timeframe",
        show_plot: bool = True,
    ) -> Union[px.line, px.bar]:
        """
        Plot the income statement for the given ticker.

        Args:
        ----------
        show_plot : bool
            If the plot should be shown or not.
            If dash is used, this should be set to False
            Default is True (show the plot)

        Returns:
        ----------------
        Union[px.line, px.bar]: The plotly figure
        """
        df = self._transform_df_for_plotting_macrotrends(
            self.macrotrends_income_statement, fields_to_include, group_by
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
        group_by: Literal["field", "timeframe"] = "timeframe",
        show_plot: bool = True,
    ) -> Union[px.line, px.bar]:
        """
        Plot the balance sheet for the given ticker.

        Args:
        ----------
        show_plot : bool
            If the plot should be shown or not.
            If dash is used, this should be set to False
            Default is True (show the plot)

        Returns:
        ----------------
        Union[px.line, px.bar]: The plotly figure
        """
        df = self._transform_df_for_plotting_macrotrends(
            self.macrotrends_balance_sheet,
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
        group_by: Literal["field", "timeframe"] = "timeframe",
        show_plot: bool = True,
    ) -> None:
        """
        Plot the cash flow statement for the given ticker.

        Args:
        ----------
        show_plot : bool
            If the plot should be shown or not.
            If dash is used, this should be set to False
            Default is True (show the plot)

        Returns:
        ----------------
        Union[px.line, px.bar]: The plotly figure
        """
        df = self._transform_df_for_plotting_macrotrends(
            self.macrotrends_cashflow_statement, fields_to_include, group_by
        )

        fig = plot_dataframe(
            df,
            title=f"{self.ticker} Cash Flow Statement (from Macrotrends)",
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

        # convert all values to float and replace empty cells with 0
        df = df.replace(r"^\s*$", "0", regex=True).applymap(
            lambda x: float(x.replace(",", ""))
        )

        # sort index in ascending order
        df = df.T.sort_index()

        if group_by == "field":
            df = df.T

        return df
