"""
Module for interfacing with the Macrotrends website.
"""
import re
from functools import lru_cache
from typing import Literal, Union

import requests
import json
import pandas as pd
import plotly.express as px
from bs4 import BeautifulSoup

from stockdex.config import MACROTRENDS_BASE_URL, VALID_SECURITY_TYPES
from stockdex.exceptions import FieldNotExists, SymbolDelisted
from stockdex.lib import check_security_type, plot_dataframe
from stockdex.selenium_interface import selenium_interface
from stockdex.ticker_base import TickerBase


class MacrotrendsInterface(TickerBase):
    """
    Interface for interacting with the Macrotrends website.
    """
    def __init__(self, ticker: str = "", isin: str = "", security_type: str = "stock") -> None:
        super().__init__(ticker=ticker, isin=isin, security_type=security_type)
        self.isin = isin
        self.ticker = ticker
        self.security_type = security_type

        # caches so we don’t re-fetch unnecessarily
        self._income_stmt_cache = {}
        self._balance_sheet_cache = {}
        self._cashflow_stmt_cache = {}


    @property
    def full_name(self) -> str:
        """
        Retrieve the full name of the security.
        """
        full_name = self.yahoo_web_full_name
        full_name = full_name.replace(" ", "-").lower()

        return full_name

    # ---------- Remove the Property Wrappers ----------
    def get_macrotrends_income_statement(self, freq="annual", transpose=False) -> pd.DataFrame:
        if freq not in self._income_stmt_cache:
            stmt = self._fetch_macrotrends_income_statement(freq)
            self._income_stmt_cache[freq] = stmt 
        return self._income_stmt_cache[freq]

    def get_macrotrends_balance_sheet(self, freq="annual", transpose=False) -> pd.DataFrame:
        if freq not in self._balance_sheet_cache:
            stmt = self._fetch_macrotrends_balance_sheet(freq)
            self._balance_sheet_cache[freq] = stmt
        return self._balance_sheet_cache[freq]

    def get_macrotrends_cashflow_statement(self, freq="annual", transpose=False) -> pd.DataFrame:
        if freq not in self._cashflow_stmt_cache:
            stmt = self._fetch_macrotrends_cashflow_statement(freq)
            self._cashflow_stmt_cache[freq] = stmt
        return self._cashflow_stmt_cache[freq]

    # ---------- Private Income Statement Methods ----------
    def _fetch_macrotrends_income_statement(self, freq="annual", transpose=False) -> pd.DataFrame:
        MARKER = "Revenue"
        THING = "income-statement"
        #print(f"_fetch_macrotrends_income_statement: freq is {freq}")
        if freq not in self._income_stmt_cache:
            """
            Retrieve the statement for the given ticker, with annual or quarterly frequency.
            freq: "annual" or "quarterly" (case insensitive); default is "annual".
            """
            check_security_type(self.security_type, valid_types=["stock"])
            freq_map = {"annual": "A", "quarterly": "Q"}
            freq_clean = str(freq).strip().lower()
            freq_param = freq_map.get(freq_clean, "A")  # Default to "A"
            mnemonic = getattr(self, "mnemonic", "TBD")  # use injected mnemonic or fallback
            #print(f"The mnemonic attribute from Ticker Class is: {mnemonic}")
            url = f"{MACROTRENDS_BASE_URL}/{self.ticker}/{mnemonic}/{THING}?freq={freq_param}"
            print(f"The url is: {url}")
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, headers=headers)
            lowercase_resp = response.url.lower()
            #response = self.get_response(url)
            # Detect delisted by URL or page content
            if "delisted" in lowercase_resp:
                raise SymbolDelisted(f"Symbol {self.ticker} appears delisted (detected in URL).")
            # RESERVED - in case we need to do more.
            #delisted_phrases = ["delisted", "no data", "no financials found", "company has been delisted"]
            #if any(phrase in response.text.lower() for phrase in delisted_phrases):
            #    raise SymbolDelisted(f"Symbol {self.ticker} appears delisted (detected by page content).")
            response.raise_for_status()

            # Cloudflare is becoming a nemesis for screen scraping
            pattern = re.compile(r"Cloudflare Ray ID:|You are unable to access|Unable to access")
            error_present = pattern.search(response.text)
            if error_present:
                #print("Cloudflare error detected")
                raise ValueError("Cloudflare error detected")

            # Check for the originalData and bail if we cannot locate it.
            match = re.search(r'var originalData = (\[.*?\]);', response.text)
            if not match:
                raise ValueError("Couldn't find originalData variable in the page")
            data = json.loads(match.group(1))

            # Clean the field names and extract dates
            field_names = [
                BeautifulSoup(row['field_name'], 'html.parser').get_text(strip=True)
                for row in data
            ]
            # Check if marker is present in any field name
            if not any(MARKER in name for name in field_names):
                raise ValueError(f"The expected marker label: {MARKER} was not found in any field_name")

            records = []
            for row in data:
                field_name = BeautifulSoup(row['field_name'], 'html.parser').get_text(strip=True)
                record = {'Metric': field_name}
                for k, v in row.items():
                    if re.match(r'\d{4}-\d{2}-\d{2}', k):  # Date format
                        record[k] = float(v) if v not in (None, '') else None
                records.append(record)

            df = pd.DataFrame(records)

            if (transpose):
                # pivot the table so it looks more like the yahoo format
                print("Transpose set to true...pivoting the result table")
                df_reset = df.reset_index(drop=True)  # Move index to a column named 'Metric'
                df_reset.rename(columns={'Metric': 'index'}, inplace=True)  # Rename the 'Metric' column to 'Item'
                # Transpose the DataFrame
                df_transposed = df_reset.set_index('index').T.reset_index()
                # Rename 'index' column to 'Period'
                df_transposed.rename(columns={'index': 'Period'}, inplace=True)
                df_transposed['Period'] = pd.to_datetime(df_transposed['Period'])  # Convert Period to datetime
                df_transposed.index.name = None  # Remove the name label above the index column
                #print("Transposed df")
                #print(df_transposed)
                return df_transposed
            else:
                #print("Transpose set to false...sending back raw result table")
                df.rename(columns={'index': 'Item', 'Metric': 'Item'}, inplace=True)

            # print(df)
            return(df)

    # ---------- Balance Sheet Methods ----------
    def _fetch_macrotrends_balance_sheet(self, freq: str = "annual", transpose=False) -> pd.DataFrame:
        MARKER = "Cash On Hand"
        THING = "balance-sheet"
        #print(f"_fetch_macrotrends_balance_sheet: freq is {freq}")
        if freq not in self._income_stmt_cache:
            """
            Retrieve the statement for the given ticker, with annual or quarterly frequency.
            freq: "annual" or "quarterly" (case insensitive); default is "annual".
            """
            check_security_type(self.security_type, valid_types=["stock"])
            freq_map = {"annual": "A", "quarterly": "Q"}
            freq_clean = str(freq).strip().lower()
            freq_param = freq_map.get(freq_clean, "A")  # Default to "A"
            mnemonic = getattr(self, "mnemonic", "TBD")  # use injected mnemonic or fallback
            print(f"The mnemonic attribute from Ticker Class is: {mnemonic}")
            url = f"{MACROTRENDS_BASE_URL}/{self.ticker}/{mnemonic}/{THING}?freq={freq_param}"
            print(f"The url is: {url}")
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, headers=headers)
            lowercase_resp = response.url.lower()
            #response = self.get_response(url)
            # Detect delisted by URL or page content
            if "delisted" in lowercase_resp:
                raise SymbolDelisted(f"Symbol {self.ticker} appears delisted (detected in URL).")
            # RESERVED - in case we need to do more.
            #delisted_phrases = ["delisted", "no data", "no financials found", "company has been delisted"]
            #if any(phrase in response.text.lower() for phrase in delisted_phrases):
            #    raise SymbolDelisted(f"Symbol {self.ticker} appears delisted (detected by page content).")
            response.raise_for_status()

            # Cloudflare is becoming a nemesis for screen scraping
            pattern = re.compile(r"Cloudflare Ray ID:|You are unable to access|Unable to access")
            error_present = pattern.search(response.text)
            if error_present:
                print("Cloudflare error detected")
                raise ValueError("Cloudflare error detected")

            # Check for the originalData and bail if we cannot locate it.
            match = re.search(r'var originalData = (\[.*?\]);', response.text)
            if not match:
                raise ValueError("Couldn't find originalData variable in the page")
            data = json.loads(match.group(1))

            # Clean the field names and extract dates
            field_names = [
                BeautifulSoup(row['field_name'], 'html.parser').get_text(strip=True)
                for row in data
            ]
            # Check if marker is present in any field name
            if not any(MARKER in name for name in field_names):
                raise ValueError(f"The expected marker label: {MARKER} was not found in any field_name")

            records = []
            for row in data:
                field_name = BeautifulSoup(row['field_name'], 'html.parser').get_text(strip=True)
                record = {'Metric': field_name}
                for k, v in row.items():
                    if re.match(r'\d{4}-\d{2}-\d{2}', k):  # Date format
                        record[k] = float(v) if v not in (None, '') else None
                records.append(record)

            df = pd.DataFrame(records)

            if (transpose):
                # pivot the table so it looks more like the yahoo format
                print("Transpose set to true...pivoting the result table")
                df_reset = df.reset_index(drop=True)  # Move index to a column named 'Metric'
                df_reset.rename(columns={'Metric': 'index'}, inplace=True)  # Rename the 'Metric' column to 'Item'
                # Transpose the DataFrame
                df_transposed = df_reset.set_index('index').T.reset_index()
                # Rename 'index' column to 'Period'
                df_transposed.rename(columns={'index': 'Period'}, inplace=True)
                df_transposed['Period'] = pd.to_datetime(df_transposed['Period'])  # Convert Period to datetime
                df_transposed.index.name = None  # Remove the name label above the index column
                #print("Transposed df")
                #print(df_transposed)
                return df_transposed
            else:
                #print("Transpose set to false...sending back raw result table")
                df.rename(columns={'index': 'Item', 'Metric': 'Item'}, inplace=True)

            #print(df)
            return(df)


    # ---------- Cash Flow Methods ----------

    def _fetch_macrotrends_cashflow_statement(self, freq: str = "annual", transpose=False) -> pd.DataFrame:
        MARKER = "Net Income/Loss"
        THING = "cash-flow-statement"
        #print(f"_fetch_macrotrends_cashflow_statement: freq is {freq}")
        if freq not in self._income_stmt_cache:
            """
            Retrieve the statement for the given ticker, with annual or quarterly frequency.
            freq: "annual" or "quarterly" (case insensitive); default is "annual".
            """
            check_security_type(self.security_type, valid_types=["stock"])
            freq_map = {"annual": "A", "quarterly": "Q"}
            freq_clean = str(freq).strip().lower()
            freq_param = freq_map.get(freq_clean, "A")  # Default to "A"
            mnemonic = getattr(self, "mnemonic", "TBD")  # use injected mnemonic or fallback
            #print(f"The mnemonic attribute from Ticker Class is: {mnemonic}")
            url = f"{MACROTRENDS_BASE_URL}/{self.ticker}/{mnemonic}/{THING}?freq={freq_param}"
            print(f"The url is: {url}")
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, headers=headers)
            lowercase_resp = response.url.lower()
            #response = self.get_response(url)
            # Detect delisted by URL or page content
            if "delisted" in lowercase_resp:
                raise SymbolDelisted(f"Symbol {self.ticker} appears delisted (detected in URL).")
            # RESERVED - in case we need to do more.
            #delisted_phrases = ["delisted", "no data", "no financials found", "company has been delisted"]
            #if any(phrase in response.text.lower() for phrase in delisted_phrases):
            #    raise SymbolDelisted(f"Symbol {self.ticker} appears delisted (detected by page content).")
            response.raise_for_status()

            # Cloudflare is becoming a nemesis for screen scraping
            pattern = re.compile(r"Cloudflare Ray ID:|You are unable to access|Unable to access")
            error_present = pattern.search(response.text)
            if error_present:
                #print("Cloudflare error detected")
                raise ValueError("Cloudflare error detected")

            # Check for the originalData and bail if we cannot locate it.
            match = re.search(r'var originalData = (\[.*?\]);', response.text)
            if not match:
                raise ValueError("Couldn't find originalData variable in the page")
            data = json.loads(match.group(1))

            # Clean the field names and extract dates
            field_names = [
                BeautifulSoup(row['field_name'], 'html.parser').get_text(strip=True)
                for row in data
            ]
            # Check if marker is present in any field name
            if not any(MARKER in name for name in field_names):
                raise ValueError(f"The expected marker label: {MARKER} was not found in any field_name")

            records = []
            for row in data:
                field_name = BeautifulSoup(row['field_name'], 'html.parser').get_text(strip=True)
                record = {'Metric': field_name}
                for k, v in row.items():
                    if re.match(r'\d{4}-\d{2}-\d{2}', k):  # Date format
                        record[k] = float(v) if v not in (None, '') else None
                records.append(record)

            df = pd.DataFrame(records)

            if (transpose):
                # pivot the table so it looks more like the yahoo format
                print("Transpose set to true...pivoting the result table")
                df_reset = df.reset_index(drop=True)  # Move index to a column named 'Metric'
                df_reset.rename(columns={'Metric': 'index'}, inplace=True)  # Rename the 'Metric' column to 'Item'
                # Transpose the DataFrame
                df_transposed = df_reset.set_index('index').T.reset_index()
                # Rename 'index' column to 'Period'
                df_transposed.rename(columns={'index': 'Period'}, inplace=True)
                df_transposed['Period'] = pd.to_datetime(df_transposed['Period'])  # Convert Period to datetime
                df_transposed.index.name = None  # Remove the name label above the index column
                #print("Transposed df")
                #print(df_transposed)
                return df_transposed
            else:
                #print("Transpose set to false...sending back raw result table")
                df.rename(columns={'index': 'Item', 'Metric': 'Item'}, inplace=True)

            #print(df)
            return(df)

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
