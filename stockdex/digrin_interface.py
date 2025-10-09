"""
Module to extract data from Digrin website
"""

from typing import Union

import pandas as pd
from bs4 import BeautifulSoup
from plotly import express as px

from stockdex.config import DIGRIN_BASE_URL, VALID_SECURITY_TYPES
from stockdex.exceptions import NoDataError
from stockdex.lib import plot_dataframe
from stockdex.ticker_base import TickerBase


class DigrinInterface(TickerBase):
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
    def digrin_dividend(self) -> pd.DataFrame:
        """
        Get dividends for the ticker

        Args:
        period (str): The period for the dividends

        Returns:
        pd.DataFrame: A pandas DataFrame including the dividends
        visible in the digrin website for the ticker
        """

        # URL of the website to scrape
        url = f"{DIGRIN_BASE_URL}/{self.ticker}"
        response = self.get_response(url)

        # Parse the HTML content of the website
        soup = BeautifulSoup(response.content, "html.parser")

        try:
            table = self.find_parent_by_text(soup, "table", "Ex-dividend date")
        except IndexError:
            raise Exception(f"There is no dividend data for the ticker {self.ticker}")

        data_df = pd.DataFrame()
        data = []

        try:
            headers = [th.text for th in table.find_all("thead")[0].find_all("th")]
        except IndexError:
            raise ValueError(
                f"There are no dividends data for ticker: {self.ticker}. For details, check out {url}"  # noqa
            )

        for tr in table.find_all("tbody")[0].find_all("tr"):
            data.append([td.text for td in tr.find_all("td")])

        data_df = pd.DataFrame(data, columns=headers).replace("\n", "", regex=True)
        return data_df

    @property
    def digrin_payout_ratio(self) -> pd.DataFrame:
        """
        Get payout ratio for the ticker

        Returns:
        pd.DataFrame: A pandas DataFrame including the payout ratio
        visible in the digrin website for the ticker
        """

        # URL of the website to scrape
        url = f"{DIGRIN_BASE_URL}/{self.ticker}/payout_ratio"
        response = self.get_response(url)

        # Parse the HTML content of the website
        soup = BeautifulSoup(response.content, "html.parser")

        try:
            table = self.find_parent_by_text(soup, "table", "Payout ratio")
        except IndexError:
            raise Exception(
                f"There is no payout ratio data for the ticker {self.ticker}"
            )

        data_df = pd.DataFrame()
        data = []

        headers = [th.text for th in table.find_all("thead")[0].find_all("th")]
        for tr in table.find_all("tbody")[0].find_all("tr"):
            data.append([td.text for td in tr.find_all("td")])

        data_df = pd.DataFrame(data, columns=headers).replace("\n", "", regex=True)
        return data_df

    @property
    def digrin_price(self) -> pd.DataFrame:
        """
        Get price for the ticker

        Returns:
        pd.DataFrame: A pandas DataFrame including the price
        visible in the digrin website for the ticker
        """

        # URL of the website to scrape
        url = f"{DIGRIN_BASE_URL}/{self.ticker}/price"
        response = self.get_response(url)

        # Parse the HTML content of the website
        soup = BeautifulSoup(response.content, "html.parser")

        try:
            table = self.find_parent_by_text(soup, "table", "Adjusted price")
        except IndexError:
            raise Exception(f"There is no price data for the ticker {self.ticker}")

        data_df = pd.DataFrame()
        data = []

        headers = [th.text for th in table.find_all("thead")[0].find_all("th")]
        for tr in table.find_all("tbody")[0].find_all("tr"):
            data.append([td.text for td in tr.find_all("td")])

        data_df = pd.DataFrame(data, columns=headers).replace("\n", "", regex=True)
        return data_df

    @property
    def digrin_stock_splits(self) -> pd.DataFrame:
        """
        Get stock splits for the ticker

        Returns:
        pd.DataFrame: A pandas DataFrame including the stock splits
        visible in the digrin website for the ticker
        """

        # URL of the website to scrape
        url = f"{DIGRIN_BASE_URL}/{self.ticker}/stock_split"
        response = self.get_response(url)

        # Parse the HTML content of the website
        soup = BeautifulSoup(response.content, "html.parser")

        try:
            table = self.find_parent_by_text(soup, "table", "Split Ratio")
        except IndexError:
            raise Exception(
                f"There is no stock split data for the ticker {self.ticker}"
            )

        data_df = pd.DataFrame()
        data = []

        headers = [th.text for th in table.find_all("thead")[0].find_all("th")]
        for tr in table.find_all("tbody")[0].find_all("tr"):
            data.append([td.text for td in tr.find_all("td")])

        data_df = pd.DataFrame(data, columns=headers).replace("\n", "", regex=True)
        return data_df

    def _get_table_from_url(self, keyword: str, url: str) -> pd.DataFrame:
        """
        Get the table from the financials page for the ticker

        Args:
        keyword (str): The keyword to search for in the table

        Returns:
        pd.DataFrame: A pandas DataFrame including the table
        visible in the digrin website for the ticker
        """

        # URL of the website to scrape
        url = url
        response = self.get_response(url)

        # Parse the HTML content of the website
        soup = BeautifulSoup(response.content, "html.parser")

        try:
            table = self.find_parent_by_text(soup, "table", keyword)
        except IndexError:
            raise NoDataError(
                f"There is no {keyword} data for the ticker {self.ticker}"
            )

        if table is None:
            raise NoDataError(
                f"There is no {keyword} data for the ticker {self.ticker}"
            )

        data_df = pd.DataFrame()
        data = []

        headers = [th.text for th in table.find_all("thead")[0].find_all("th")]
        for tr in table.find_all("tbody")[0].find_all("tr"):
            data.append([td.text for td in tr.find_all("td")])

        data_df = pd.DataFrame(data, columns=headers).replace("\n", "", regex=True)
        return data_df

    @property
    def digrin_assets_vs_liabilities(self) -> pd.DataFrame:
        """
        Get assets vs liabilities for the ticker

        Returns:
        pd.DataFrame: A pandas DataFrame including the assets vs liabilities
        visible in the digrin website for the ticker
        """

        return self._get_table_from_url(
            "Assets", f"{DIGRIN_BASE_URL}/{self.ticker}/financials"
        )

    @property
    def digrin_free_cash_flow(self) -> pd.DataFrame:
        """
        Get free cash flow for the ticker

        Returns:
        pd.DataFrame: A pandas DataFrame including the free cash flow
        visible in the digrin website for the ticker
        """

        return self._get_table_from_url(
            "Free Cash Flow", f"{DIGRIN_BASE_URL}/{self.ticker}/financials"
        )

    @property
    def digrin_net_income(self) -> pd.DataFrame:
        """
        Get net income for the ticker

        Returns:
        pd.DataFrame: A pandas DataFrame including the net income
        visible in the digrin website for the ticker
        """

        return self._get_table_from_url(
            "Net Income", f"{DIGRIN_BASE_URL}/{self.ticker}/financials"
        )

    @property
    def digrin_cash_and_debt(self) -> pd.DataFrame:
        """
        Get cash and debt for the ticker

        Returns:
        pd.DataFrame: A pandas DataFrame including the cash and debt
        visible in the digrin website for the ticker
        """

        return self._get_table_from_url(
            "Capital Lease", f"{DIGRIN_BASE_URL}/{self.ticker}/financials"
        )

    @property
    def digrin_shares_outstanding(self) -> pd.DataFrame:
        """
        Get shares outstanding for the ticker

        Returns:
        pd.DataFrame: A pandas DataFrame including the shares outstanding
        visible in the digrin website for the ticker
        """

        return self._get_table_from_url(
            "Shares Outstanding", f"{DIGRIN_BASE_URL}/{self.ticker}/financials"
        )

    @property
    def digrin_expenses(self) -> pd.DataFrame:
        """
        Get expenses for the ticker

        Returns:
        pd.DataFrame: A pandas DataFrame including the expenses
        visible in the digrin website for the ticker
        """

        return self._get_table_from_url(
            "Capex", f"{DIGRIN_BASE_URL}/{self.ticker}/financials"
        )

    @property
    def digrin_cost_of_revenue(self) -> pd.DataFrame:
        """
        Get cost of revenue for the ticker

        Returns:
        pd.DataFrame: A pandas DataFrame including the cost of revenue
        visible in the digrin website for the ticker
        """

        return self._get_table_from_url(
            "Cost of Revenue", f"{DIGRIN_BASE_URL}/{self.ticker}/financials"
        )

    @property
    def digrin_dgr3(self) -> pd.DataFrame:
        """
        Get dgr3 for the ticker

        Returns:
        pd.DataFrame: A pandas DataFrame including the dgr3
        visible in the digrin website for the ticker
        """

        return self._get_table_from_url(
            "Estimated Yield on Cost", f"{DIGRIN_BASE_URL}/{self.ticker}/dgr3"
        )

    @property
    def digrin_dgr5(self) -> pd.DataFrame:
        """
        Get dgr5 for the ticker

        Returns:
        pd.DataFrame: A pandas DataFrame including the dgr5
        visible in the digrin website for the ticker
        """

        return self._get_table_from_url(
            "Estimated Yield on Cost", f"{DIGRIN_BASE_URL}/{self.ticker}/dgr5"
        )

    @property
    def digrin_dgr10(self) -> pd.DataFrame:
        """
        Get dgr10 for the ticker

        Returns:
        pd.DataFrame: A pandas DataFrame including the dgr10
        visible in the digrin website for the ticker
        """

        return self._get_table_from_url(
            "Estimated Yield on Cost", f"{DIGRIN_BASE_URL}/{self.ticker}/dgr10"
        )

    @property
    def digrin_upcoming_estimated_earnings(self) -> pd.DataFrame:
        """
        Get upcoming estimated earnings for the ticker

        Returns:
        pd.DataFrame: A pandas DataFrame including the upcoming estimated earnings
        visible in the digrin website for the ticker
        """

        return self._get_table_from_url(
            "Actual / Estimated EPS", f"{DIGRIN_BASE_URL}/{self.ticker}/earnings"
        )

    def plot_digrin_shares_outstanding(
        self, show_plot: bool = True
    ) -> Union[px.line, px.bar]:
        """
        Plot the shares outstanding for the ticker

        Args:
        ----------------
        show_plot : bool
            If the plot should be shown or not.
            If dash is used, this should be set to False
            Default is True (show the plot)

        Returns:
        ----------------
        Union[px.line, px.bar]: The plotly figure
        """

        data = self.digrin_shares_outstanding

        data["Date"] = data["Date"].apply(self._human_date_format_to_raw)
        data["Date"] = pd.to_datetime(data["Date"])
        data["Shares Outstanding"] = (
            data["Shares Outstanding"]
            .replace("?", "0")
            .apply(self._human_number_format_to_raw)
        )
        data.set_index("Date", inplace=True)
        data = data[["Shares Outstanding"]]

        fig = plot_dataframe(
            data,
            x_axis_title="Date",
            y_axis_title="Amount",
            title=f"{self.ticker} Shares Outstanding from Digrin",
            show_plot=show_plot,
        )

        return fig

    def plot_digrin_price(self, show_plot: bool = True) -> Union[px.line, px.bar]:
        """
        Plot the price for the ticker

        Args:
        ----------------
        show_plot : bool
            If the plot should be shown or not.
            If dash is used, this should be set to False
            Default is True (show the plot)

        Returns:
        ----------------
        Union[px.line, px.bar]: The plotly figure
        """

        data = self.digrin_price
        data["Date"] = pd.to_datetime(data["Date"])
        data["Real Price"] = data["Real price"].apply(self._human_number_format_to_raw)
        data["Adjusted Price"] = data["Adjusted price"].apply(
            self._human_number_format_to_raw
        )

        # drop the original columns
        data.drop(columns=["Real price", "Adjusted price"], inplace=True)
        data.set_index("Date", inplace=True)

        fig = plot_dataframe(
            data,
            x_axis_title="Date",
            y_axis_title="Price",
            title=f"{self.ticker} Stock Price (Real vs Adjusted) from Digrin",
            draw_line_chart=True,
            show_plot=show_plot,
        )

        return fig

    def plot_digrin_dividend(self, show_plot: bool = True) -> Union[px.line, px.bar]:
        """
        Plot the dividend for the ticker

        Args:
        ----------------
        show_plot : bool
            If the plot should be shown or not.
            If dash is used, this should be set to False
            Default is True (show the plot)

        Returns:
        ----------------
        Union[px.line, px.bar]: The plotly figure
        """

        data = self.digrin_dividend
        data["Ex-dividend date"] = pd.to_datetime(data["Ex-dividend date"])
        data["Dividend"] = (
            data["Dividend amount (change)"]
            .str.split(" ", expand=True)[0]
            .astype(float)
        )

        data.set_index("Ex-dividend date", inplace=True)
        data = data[["Dividend"]]

        fig = plot_dataframe(
            data,
            x_axis_title="Ex-dividend date",
            y_axis_title="Dividend",
            title=f"{self.ticker} Dividend from Digrin",
            draw_line_chart=True,
            show_plot=show_plot,
        )

        return fig

    def plot_digrin_assets_vs_liabilities(
        self, show_plot: bool = True
    ) -> Union[px.line, px.bar]:
        """
        Plot the assets vs liabilities for the ticker

        Args:
        ----------------
        show_plot : bool
            If the plot should be shown or not.
            If dash is used, this should be set to False
            Default is True (show the plot)

        Returns:
        ----------------
        Union[px.line, px.bar]: The plotly figure
        """

        data = self.digrin_assets_vs_liabilities

        data["Date"] = data["Date"].apply(self._human_date_format_to_raw)
        data["Date"] = pd.to_datetime(data["Date"])
        data["Assets"] = data["Assets"].apply(self._human_number_format_to_raw)
        data["Liabilities"] = data["Liabilities"].apply(
            self._human_number_format_to_raw
        )
        data.set_index("Date", inplace=True)
        data = data[["Assets", "Liabilities"]]

        fig = plot_dataframe(
            data,
            x_axis_title="Date",
            y_axis_title="Amount",
            title=f"{self.ticker} Assets vs Liabilities from Digrin",
            show_plot=show_plot,
        )

        return fig

    def _human_number_format_to_raw(self, entry: str) -> float:
        """
        Convert human readable format to raw format

        Handles various input formats:
        - Numbers with commas: "1,077.60" -> 1077.60
        - Numbers with suffixes: "1.5 B", "250 M", "5.2 K", "2 T"
        - Zero/null indicators: "?", "N/A", "-", etc.
        - Regular numbers: "123.45"

        Args:
            entry (str): Human-readable number string

        Returns:
            float: Raw numeric value
        """
        # Handle empty or whitespace-only strings
        if not entry or entry.strip() == "":
            return 0.0

        # Clean the entry
        entry = entry.strip()

        # Define entries to consider as zero
        entries_to_consider_zero = [
            "?",
            "N/A",
            "n/a",
            "nan",
            "NAN",
            "Nan",
            "_",
            "-",
            "—",  # em dash
            "–",  # en dash
        ]

        if entry in entries_to_consider_zero:
            return 0.0

        # Remove currency symbols if present
        entry = (
            entry.replace("$", "")
            .replace("€", "")
            .replace("£", "")
            .replace("¥", "")
            .strip()
        )

        # Handle percentage signs
        is_percentage = entry.endswith("%")
        if is_percentage:
            entry = entry[:-1].strip()

        # Check for suffix multipliers (case insensitive)
        entry_lower = entry.lower()
        multiplier = 1.0

        # Check for full word suffixes first
        if "trillion" in entry_lower:
            multiplier = 1_000_000_000_000
            entry = entry_lower.replace("trillion", "").strip()
        elif "billion" in entry_lower:
            multiplier = 1_000_000_000
            entry = entry_lower.replace("billion", "").strip()
        elif "million" in entry_lower:
            multiplier = 1_000_000
            entry = entry_lower.replace("million", "").strip()
        elif "thousand" in entry_lower:
            multiplier = 1_000
            entry = entry_lower.replace("thousand", "").strip()
        elif (
            "t" in entry_lower
            and not entry_lower.replace(".", "").replace(",", "").isdigit()
        ):
            # Trillion - but make sure it's not just a number containing 't'
            if entry_lower.endswith("t") or " t" in entry_lower:
                multiplier = 1_000_000_000_000
                entry = entry_lower.replace("t", "").strip()
        elif (
            "b" in entry_lower
            and not entry_lower.replace(".", "").replace(",", "").isdigit()
        ):
            # Billion - but make sure it's not just a number containing 'b'
            if entry_lower.endswith("b") or " b" in entry_lower:
                multiplier = 1_000_000_000
                entry = entry_lower.replace("b", "").strip()
        elif (
            "m" in entry_lower
            and not entry_lower.replace(".", "").replace(",", "").isdigit()
        ):
            # Million - but make sure it's not just a number containing 'm'
            if entry_lower.endswith("m") or " m" in entry_lower:
                multiplier = 1_000_000
                entry = entry_lower.replace("m", "").strip()
        elif (
            "k" in entry_lower
            and not entry_lower.replace(".", "").replace(",", "").isdigit()
        ):
            # Thousand - but make sure it's not just a number containing 'k'
            if entry_lower.endswith("k") or " k" in entry_lower:
                multiplier = 1_000
                entry = entry_lower.replace("k", "").strip()

        # Remove commas (thousands separators)
        entry = entry.replace(",", "")

        # Handle negative numbers
        is_negative = entry.startswith("-") or entry.startswith("(")
        if entry.startswith("(") and entry.endswith(")"):
            entry = entry[1:-1]  # Remove parentheses
            is_negative = True
        elif entry.startswith("-"):
            entry = entry[1:]  # Remove minus sign, we'll apply it later

        # Convert to float
        try:
            result = float(entry) * multiplier
            if is_negative:
                result = -result
            if is_percentage:
                result = result / 100.0
            return result
        except ValueError as e:
            raise ValueError(
                f"Could not convert '{entry}' to float. Original input: '{entry}'. Error: {e}"
            )

    def _human_date_format_to_raw(self, entry: str) -> str:
        """
        Convert human readable date format (e.g. "Dec. 31, 2023") to raw format (e.g. 2023-12-31)

        Handles various input formats:
        - "Dec. 31, 2023" -> "2023-12-31"
        - "Dec 31, 2023" -> "2023-12-31"
        - "March 1, 2023" -> "2023-03-01"
        - Single digit days are zero-padded
        """
        conversion_dict = {
            "Jan": "01",
            "Feb": "02",
            "Mar": "03",
            "March": "03",
            "Apr": "04",
            "May": "05",
            "June": "06",
            "Jul": "07",
            "Aug": "08",
            "Sept": "09",
            "Sep": "09",
            "Oct": "10",
            "Nov": "11",
            "Dec": "12",
        }

        # Split the date string
        parts = entry.split(" ")
        if len(parts) != 3:
            raise ValueError(
                f"Invalid date format: {entry}. Expected format: 'Month Day, Year'"
            )

        month_str, day_str, year_str = parts

        # Clean up month (remove periods)
        month_str = month_str.replace(".", "").strip()

        # Clean up day (remove commas)
        day_str = day_str.replace(",", "").strip()

        # Clean up year (should already be clean)
        year_str = year_str.strip()

        # Convert month to number
        if month_str not in conversion_dict:
            raise ValueError(f"Unknown month: {month_str}")
        month = conversion_dict[month_str]

        # Zero-pad day if needed
        day = day_str.zfill(2)

        return f"{year_str}-{month}-{day}"

    def plot_digrin_free_cash_flow(
        self, show_plot: bool = True
    ) -> Union[px.line, px.bar]:
        """
        Plot the free cash flow for the ticker

        Args:
        ----------------
        show_plot : bool
            If the plot should be shown or not.
            If dash is used, this should be set to False
            Default is True (show the plot)

        Returns:
        ----------------
        Union[px.line, px.bar]: The plotly figure
        """

        data = self.digrin_free_cash_flow

        data["Date"] = data["Date"].apply(self._human_date_format_to_raw)
        data["Date"] = pd.to_datetime(data["Date"])
        data["Free Cash Flow"] = (
            data["Free Cash Flow"]
            .replace("?", "0")
            .apply(self._human_number_format_to_raw)
        )
        data["Stock based compensation"] = (
            data["Stock based compensation"]
            .replace("?", "0")
            .apply(self._human_number_format_to_raw)
        )
        data.set_index("Date", inplace=True)
        data = data[["Free Cash Flow", "Stock based compensation"]]

        fig = plot_dataframe(
            data,
            x_axis_title="Date",
            y_axis_title="Amount",
            title=f"{self.ticker} Free Cash Flow from Digrin",
            show_plot=show_plot,
        )

        return fig

    def plot_digrin_net_income(self, show_plot: bool = True) -> Union[px.line, px.bar]:
        """
        Plot the net income for the ticker

        Args:
        ----------------
        show_plot : bool
            If the plot should be shown or not.
            If dash is used, this should be set to False
            Default is True (show the plot)

        Returns:
        ----------------
        Union[px.line, px.bar]: The plotly figure
        """

        data = self.digrin_net_income

        data["Date"] = data["Date"].apply(self._human_date_format_to_raw)
        data["Date"] = pd.to_datetime(data["Date"])
        data["Net Income"] = (
            data["Net Income"].replace("?", "0").apply(self._human_number_format_to_raw)
        )

        data.set_index("Date", inplace=True)
        data = data[["Net Income"]]

        fig = plot_dataframe(
            data,
            x_axis_title="Date",
            y_axis_title="Amount",
            title=f"{self.ticker} Net Income from Digrin",
            show_plot=show_plot,
        )

        return fig

    def plot_digrin_cash_and_debt(
        self, show_plot: bool = True
    ) -> Union[px.line, px.bar]:
        """
        Plot the cash and debt for the ticker

        Args:
        ----------------
        show_plot : bool
            If the plot should be shown or not.
            If dash is used, this should be set to False
            Default is True (show the plot)

        Returns:
        ----------------
        Union[px.line, px.bar]: The plotly figure
        """

        data = self.digrin_cash_and_debt

        data["Date"] = data["Date"].apply(self._human_date_format_to_raw)
        data["Date"] = pd.to_datetime(data["Date"])
        data["Cash"] = data["Cash"].apply(self._human_number_format_to_raw)
        data["Debt"] = data["Debt"].apply(self._human_number_format_to_raw)
        data.set_index("Date", inplace=True)
        data = data[["Cash", "Debt"]]

        fig = plot_dataframe(
            data,
            x_axis_title="Date",
            y_axis_title="Amount",
            title=f"{self.ticker} Cash and Debt from Digrin",
            show_plot=show_plot,
        )

        return fig

    def plot_digrin_expenses(self, show_plot: bool = True) -> Union[px.line, px.bar]:
        """
        Plot the expenses for the ticker

        Args:
        ----------------
        show_plot : bool
            If the plot should be shown or not.
            If dash is used, this should be set to False
            Default is True (show the plot)

        Returns:
        ----------------
        Union[px.line, px.bar]: The plotly figure
        """

        data = self.digrin_expenses

        data["Date"] = data["Date"].apply(self._human_date_format_to_raw)
        data["Date"] = pd.to_datetime(data["Date"])
        data["Capex"] = data["Capex"].apply(self._human_number_format_to_raw)
        data["R&D"] = data["R&D"].apply(self._human_number_format_to_raw)
        data["G&A"] = data["G&A"].apply(self._human_number_format_to_raw)
        data["S&M"] = data["S&M"].apply(self._human_number_format_to_raw)
        data.set_index("Date", inplace=True)
        data = data[["Capex", "R&D", "G&A", "S&M"]]

        fig = plot_dataframe(
            data,
            x_axis_title="Date",
            y_axis_title="Amount",
            title=f"{self.ticker} Expenses from Digrin",
            show_plot=show_plot,
        )

        return fig

    def plot_digrin_cost_of_revenue(
        self, show_plot: bool = True
    ) -> Union[px.line, px.bar]:
        """
        Plot the cost of revenue for the ticker

        Args:
        ----------------
        show_plot : bool
            If the plot should be shown or not.
            If dash is used, this should be set to False
            Default is True (show the plot)

        Returns:
        ----------------
        Union[px.line, px.bar]: The plotly figure
        """

        data = self.digrin_cost_of_revenue

        data["Date"] = data["Date"].apply(self._human_date_format_to_raw)
        data["Date"] = pd.to_datetime(data["Date"])
        data["Cost of Revenue"] = (
            data["Cost of Revenue"]
            .replace("?", "0")
            .apply(self._human_number_format_to_raw)
        )
        data["Revenue"] = (
            data["Revenue"].replace("?", "0").apply(self._human_number_format_to_raw)
        )
        data.set_index("Date", inplace=True)
        data = data[["Cost of Revenue", "Revenue"]]

        fig = plot_dataframe(
            data,
            x_axis_title="Date",
            y_axis_title="Amount",
            title=f"{self.ticker} Cost of Revenue from Digrin",
            show_plot=show_plot,
        )

        return fig
