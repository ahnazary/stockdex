"""
Module for interfacing with the Macrotrends website.
"""

import json
import re
from io import StringIO
from typing import Literal, Union

import pandas as pd
import plotly.express as px
from bs4 import BeautifulSoup

from stockdex.config import MACROTRENDS_BASE_URL, VALID_SECURITY_TYPES
from stockdex.exceptions import FieldNotExists, LayoutChangedError
from stockdex.lib import check_security_type, instance_cache, plot_dataframe
from stockdex.ticker_base import TickerBase

_ORIGINAL_DATA = re.compile(r"originalData\s*=\s*(\[.*?\])\s*;", re.DOTALL)
_FIELD_NAME = re.compile(r">([^<]*)<")


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
    @instance_cache
    def full_name(self) -> str:
        """
        Retrieve the full name of the security as a URL slug, e.g. "apple-inc"
        """
        name = self.yahoo_api_company_name()
        name = re.sub(r"[^\w\s-]", "", name).strip()

        return re.sub(r"\s+", "-", name).lower()

    def _find_table_in_url(
        self, text_to_look_for: str, soup: BeautifulSoup
    ) -> pd.DataFrame:
        """
        Read the ``originalData`` table embedded in a Macrotrends page

        Args:
        ----------
        text_to_look_for: str
            A field name the table must contain, e.g. "Revenue".
        soup: BeautifulSoup
            The parsed page.

        Returns:
        ----------
        pd.DataFrame
            One row per field with a ``field_name`` column and one column per
            period.

        Raises:
        ----------
        LayoutChangedError
            If the page has no parsable ``originalData`` block.
        """
        match = None
        for script in soup.find_all("script"):
            match = _ORIGINAL_DATA.search(script.get_text())
            if match:
                break

        if match is None:
            raise LayoutChangedError(
                "Macrotrends", f"no originalData table for '{text_to_look_for}'"
            )

        # The block is a JSON array literal; never evaluate it as code.
        try:
            rows = json.loads(match.group(1))
        except json.JSONDecodeError as error:
            raise LayoutChangedError(
                "Macrotrends", f"originalData for '{text_to_look_for}' is not JSON"
            ) from error

        if not isinstance(rows, list) or not all(isinstance(r, dict) for r in rows):
            raise LayoutChangedError(
                "Macrotrends", f"originalData for '{text_to_look_for}' is not a table"
            )
        data = pd.DataFrame(rows)
        if "field_name" not in data:
            raise LayoutChangedError("Macrotrends", "table has no field_name column")
        return data

    def _statement_frame(self, url: str, text_to_look_for: str) -> pd.DataFrame:
        """Fetch one Macrotrends statement page as a field x period frame"""
        response = self.get_response(url)
        soup = BeautifulSoup(response.content, "html.parser")
        data = self._find_table_in_url(text_to_look_for, soup)

        def field(value):
            found = _FIELD_NAME.search(str(value))
            return found.group(1).strip() if found else str(value).strip()

        data["field_name"] = data["field_name"].apply(field)
        data = data.set_index("field_name")
        return data.drop(columns=["popup_icon"], errors="ignore")

    @instance_cache
    def macrotrends_income_statement(
        self, frequency: Literal["quarterly", "annual"] = "annual"
    ) -> pd.DataFrame:
        """
        Retrieve the income statement for the given ticker.
        """
        check_security_type(self.security_type, valid_types=["stock"])
        frequency_suffix = "?freq=A" if frequency == "annual" else "?freq=Q"

        url = (
            f"{MACROTRENDS_BASE_URL}/{self.ticker}/{self.get_company_slug(self.ticker)}/income-statement{frequency_suffix}"  # NOQA: E501
            if frequency == "quarterly"
            else f"{MACROTRENDS_BASE_URL}/{self.ticker}/TBD/income-statement{frequency_suffix}"
        )

        return self._statement_frame(url, "Revenue")

    @instance_cache
    def macrotrends_balance_sheet(
        self, frequency: Literal["quarterly", "annual"] = "annual"
    ) -> pd.DataFrame:
        """
        Retrieve the balance sheet for the given ticker.
        """
        check_security_type(self.security_type, valid_types=["stock"])
        frequency_suffix = "?freq=A" if frequency == "annual" else "?freq=Q"

        url = (
            f"{MACROTRENDS_BASE_URL}/{self.ticker}/{self.get_company_slug(self.ticker)}/balance-sheet{frequency_suffix}"  # NOQA: E501
            if frequency == "quarterly"
            else f"{MACROTRENDS_BASE_URL}/{self.ticker}/TBD/balance-sheet{frequency_suffix}"
        )

        return self._statement_frame(url, "Cash On Hand")

    @instance_cache
    def macrotrends_cash_flow(
        self, frequency: Literal["quarterly", "annual"] = "annual"
    ) -> pd.DataFrame:
        """
        Retrieve the cash flow statement for the given ticker.
        """
        check_security_type(self.security_type, valid_types=["stock"])
        frequency_suffix = "?freq=A" if frequency == "annual" else "?freq=Q"

        url = (
            f"{MACROTRENDS_BASE_URL}/{self.ticker}/{self.get_company_slug(self.ticker)}/cash-flow-statement{frequency_suffix}"  # NOQA: E501
            if frequency == "quarterly"
            else f"{MACROTRENDS_BASE_URL}/{self.ticker}/TBD/cash-flow-statement{frequency_suffix}"
        )

        return self._statement_frame(url, "Net Income/Loss")

    @property
    @instance_cache
    def macrotrends_key_financial_ratios(self) -> pd.DataFrame:
        """
        Retrieve the key financial ratios for the given ticker.
        """
        check_security_type(self.security_type, valid_types=["stock"])
        url = f"{MACROTRENDS_BASE_URL}/{self.ticker}/TBD/financial-ratios"

        return self._statement_frame(url, "Current Ratio")

    def _find_margins_table(self, url: str, text_to_look_for: str):
        response = self.get_response(url)

        # Parse the HTML content of the website
        soup = BeautifulSoup(response.content, "html.parser")

        table = self.find_parent_by_text(soup=soup, tag="table", text=text_to_look_for)
        if table is None:
            raise LayoutChangedError(
                "Macrotrends", f"no table with '{text_to_look_for}'"
            )
        heads = table.find_all("thead")
        if len(heads) < 2 or not heads[1].find("tr"):
            raise LayoutChangedError(
                "Macrotrends", f"'{text_to_look_for}' table has no header row"
            )

        headers = [row.text for row in heads[1].find_all("tr")[0].find_all("th")]
        rows = [
            [cell.text for cell in row.find_all("td")]
            for row in table.find_all("tr")[1:]
        ]
        data = [row for row in rows if len(row) == len(headers)]
        # Spacer rows are a single colspan cell; anything wider that never
        # matches the headers means the table changed
        if not data and any(len(row) > 1 for row in rows):
            raise LayoutChangedError(
                "Macrotrends",
                f"'{text_to_look_for}' rows no longer match its "
                f"{len(headers)} columns",
            )
        return pd.DataFrame(data, columns=headers)

    @property
    @instance_cache
    def macrotrends_operating_margin(self) -> pd.DataFrame:
        """
        Retrieve the operating margin for the given ticker.
        """
        check_security_type(self.security_type, valid_types=["stock"])
        url = f"{MACROTRENDS_BASE_URL}/{self.ticker}/TBD/operating-margin"

        return self._find_margins_table(url, "TTM Operating Income")

    @property
    @instance_cache
    def macrotrends_gross_margin(self) -> pd.DataFrame:
        """
        Retrieve the gross margin for the given ticker.
        """
        check_security_type(self.security_type, valid_types=["stock"])
        url = f"{MACROTRENDS_BASE_URL}/{self.ticker}/TBD/gross-margin"

        return self._find_margins_table(url, "Gross Margin")

    @property
    @instance_cache
    def macrotrends_ebitda_margin(self) -> pd.DataFrame:
        """
        Retrieve the EBITDA margin for the given ticker.
        """
        check_security_type(self.security_type, valid_types=["stock"])
        url = f"{MACROTRENDS_BASE_URL}/{self.ticker}/TBD/ebitda-margin"

        return self._find_margins_table(url, "TTM EBITDA")

    @property
    @instance_cache
    def macrotrends_pre_tax_margin(self) -> pd.DataFrame:
        """
        Retrieve the pre-tax margin for the given ticker.
        """
        check_security_type(self.security_type, valid_types=["stock"])
        url = f"{MACROTRENDS_BASE_URL}/{self.ticker}/TBD/pre-tax-profit-margin"

        return self._find_margins_table(url, "TTM Pre-Tax Income")

    @property
    @instance_cache
    def macrotrends_net_margin(self) -> pd.DataFrame:
        """
        Retrieve the net profit margin for the given ticker.
        """
        check_security_type(self.security_type, valid_types=["stock"])
        url = f"{MACROTRENDS_BASE_URL}/{self.ticker}/TBD/net-profit-margin"

        return self._find_margins_table(url, "TTM Net Income")

    @instance_cache
    def macrotrends_revenue(
        self, frequency: Literal["annual", "quarterly"] = "annual"
    ) -> pd.DataFrame:
        """
        Retrieve the revenue for the given ticker.
        """
        check_security_type(self.security_type, valid_types=["stock"])
        url = f"{MACROTRENDS_BASE_URL}/{self.ticker}/TBD/revenue"

        response = self.get_response(url)

        # Parse the HTML content of the website
        soup = BeautifulSoup(response.content, "html.parser")

        # find tables with class = historical_data_table
        tables = soup.find_all("table", class_="historical_data_table")
        position = 0 if frequency == "annual" else 1
        if len(tables) <= position:
            raise LayoutChangedError("Macrotrends", f"no {frequency} revenue table")

        return pd.read_html(StringIO(str(tables[position])))[0]

    @instance_cache
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
