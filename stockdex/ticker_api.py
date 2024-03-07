"""
Module to retrieve stock data from Yahoo Finance API
The main Ticker class inherits from this class
"""

from typing import Literal

import pandas as pd

from stockdex import config
from stockdex.ticker_base import TickerBase


class TickerAPI(TickerBase):
    current_timestamp = int(pd.Timestamp("now").timestamp())
    five_years_ago = int(pd.Timestamp("now").timestamp()) - 5 * 365 * 24 * 60 * 60

    def price(
        self,
        range: Literal[
            "1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"
        ] = "1d",
        dataGranularity: Literal[
            "1m",
            "2m",
            "5m",
            "15m",
            "30m",
            "60m",
            "90m",
            "1h",
            "1d",
            "5d",
            "1wk",
            "1mo",
            "3mo",
        ] = "1m",
    ) -> pd.DataFrame:
        """
        Get the price data for the stock

        Args:
        range (str): The range of the price data to retrieve
        valid values are "1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"

        dataGranularity (str): The granularity of the data to retrieve (interval)
        valid values are "1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h", "1d", "5d", "1wk", "1mo", "3mo""  # noqa: E501
        """

        url = f"{config.BASE_URL}/chart/{self.ticker}?range={range}&interval={dataGranularity}"
        response = self.get_response(url)

        meta = response.json()["chart"]["result"][0]["meta"]
        currency = meta["currency"]
        exchangeTimezoneName = meta["exchangeTimezoneName"]
        timezone = meta["timezone"]
        exchangeName = meta["exchangeName"]
        instrumentType = meta["instrumentType"]

        timestamp = response.json()["chart"]["result"][0]["timestamp"]
        timestamp = pd.to_datetime(timestamp, unit="s")

        indicators = response.json()["chart"]["result"][0]["indicators"]
        volume = indicators["quote"][0]["volume"]
        close = indicators["quote"][0]["close"]
        open = indicators["quote"][0]["open"]
        high = indicators["quote"][0]["high"]
        low = indicators["quote"][0]["low"]

        return pd.DataFrame(
            {
                "timestamp": timestamp,
                "volume": volume,
                "close": close,
                "open": open,
                "high": high,
                "low": low,
                "currency": currency,
                "timezone": timezone,
                "exchangeTimezoneName": exchangeTimezoneName,
                "exchangeName": exchangeName,
                "instrumentType": instrumentType,
            }
        )

    @property
    def current_trading_period(self) -> pd.DataFrame:
        """
        Get the current trading period for the stock
        """

        url = f"{config.BASE_URL}/chart/{self.ticker}"
        response = self.get_response(url)

        currentTradingPeriod = response.json()["chart"]["result"][0]["meta"][
            "currentTradingPeriod"
        ]

        pre = currentTradingPeriod["pre"]
        regular = currentTradingPeriod["regular"]
        post = currentTradingPeriod["post"]

        # convert timestamps to datetime
        pre["start"] = pd.to_datetime(pre["start"], unit="s")
        pre["end"] = pd.to_datetime(pre["end"], unit="s")
        regular["start"] = pd.to_datetime(regular["start"], unit="s")
        regular["end"] = pd.to_datetime(regular["end"], unit="s")
        post["start"] = pd.to_datetime(post["start"], unit="s")
        post["end"] = pd.to_datetime(post["end"], unit="s")

        return pd.DataFrame(
            {
                "pre": pre,
                "regular": regular,
                "post": post,
            }
        )

    # TODO: periods must be strings
    def income_statement(
        self,
        frequency: Literal["annual", "quarterly"] = "annual",
        format: Literal["fmt", "raw"] = "fmt",
        period1: int = five_years_ago,
        period2: int = current_timestamp,
    ) -> pd.DataFrame:
        """
        Get the income statement for the stock

        Args:
        frequency (str): The frequency of the data to retrieve
        valid values are "annual", "quarterly"

        format (str): The format of the data to retrieve
        valid values are "fmt", "raw"
        if "fmt" is used, the data will be in a human readable format, e.g. 1B
        if "raw" is used, the data will be in a raw format, e.g. 1000000000
        """
        url = self.build_url(frequency, period1, period2, "income_statement")

        response = self.get_response(url).json()["timeseries"]["result"]

        return self.extract_dataframe(response, format)

    def cash_flow(
        self,
        frequency: Literal["annual", "quarterly"] = "annual",
        format: Literal["fmt", "raw"] = "fmt",
        period1: int = five_years_ago,
        period2: int = current_timestamp,
    ) -> pd.DataFrame:
        """
        Get the cash flow statement for the stock

        Args:
        frequency (str): The frequency of the data to retrieve
        valid values are "annual", "quarterly"

        format (str): The format of the data to retrieve
        valid values are "fmt", "raw"
        if "fmt" is used, the data will be in a human readable format, e.g. 1B
        if "raw" is used, the data will be in a raw format, e.g. 1000000000
        """
        url = self.build_url(frequency, period1, period2, "cash_flow")

        response = self.get_response(url).json()["timeseries"]["result"]

        return self.extract_dataframe(response, format)

    def balance_sheet(
        self,
        frequency: Literal["annual", "quarterly"] = "annual",
        format: Literal["fmt", "raw"] = "fmt",
        period1: int = five_years_ago,
        period2: int = current_timestamp,
    ) -> pd.DataFrame:
        """
        Get the balance sheet for the stock

        Args:
        frequency (str): The frequency of the data to retrieve
        valid values are "annual", "quarterly"

        format (str): The format of the data to retrieve
        valid values are "fmt", "raw"
        if "fmt" is used, the data will be in a human readable format, e.g. 1B
        if "raw" is used, the data will be in a raw format, e.g. 1000000000
        """
        url = self.build_url(frequency, period1, period2, "balance_sheet")

        response = self.get_response(url).json()["timeseries"]["result"]

        return self.extract_dataframe(response, format)

    def financials(
        self,
        frequency: Literal["annual", "quarterly"] = "annual",
        format: Literal["fmt", "raw"] = "fmt",
        period1: int = five_years_ago,
        period2: int = current_timestamp,
    ) -> pd.DataFrame:
        """
        Get the financials for the stock

        Args:
        frequency (str): The frequency of the data to retrieve
        valid values are "annual", "quarterly"

        format (str): The format of the data to retrieve
        valid values are "fmt", "raw"
        if "fmt" is used, the data will be in a human readable format, e.g. 1B
        if "raw" is used, the data will be in a raw format, e.g. 1000000000
        """
        url = self.build_url(frequency, period1, period2, "financials")

        response = self.get_response(url).json()["timeseries"]["result"]

        return self.extract_dataframe(response, format)

    def build_url(
        self,
        frequency: str,
        period1: int,
        period2: int,
        desired_entity: str,
    ) -> str:
        """
        Build the URL for the income statement, balance sheet, and cash flow statement
        """
        columns = ",".join(
            getattr(config, f"{frequency.upper()}_{desired_entity.upper()}_COLUMNS")
        )
        url = f"{config.FUNDAMENTALS_BASE_URL}/{self.ticker}/?symbol={self.ticker}"
        url += f"&type={columns}"
        url += f"&period1={period1}&period2={period2}"
        return url

    def extract_dataframe(self, response, format="fmt") -> pd.DataFrame:
        """
        Extract the dataframes from the response
        """
        row = {}
        for item in response:
            column = item["meta"]["type"][0]

            # skip if there is no data for in the response
            if column not in item:
                continue

            data = item[column]
            dated_index = [i["asOfDate"] for i in data]
            values = [i["reportedValue"][format] for i in data]

            row[column] = pd.Series(values, index=dated_index)

        return pd.DataFrame(row, index=dated_index)
