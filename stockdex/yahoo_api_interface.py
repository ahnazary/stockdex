"""
Module to retrieve stock data from Yahoo Finance API
The main Ticker class inherits from this class
"""

from datetime import datetime
from typing import Literal, Union
from urllib.parse import quote as requests_quote

import pandas as pd
import plotly.express as px

from stockdex import config
from stockdex.config import VALID_DATA_SOURCES, VALID_SECURITY_TYPES
from stockdex.exceptions import FieldNotExists, NoDataError
from stockdex.lib import plot_dataframe
from stockdex.ticker_base import TickerBase


class YahooAPI(TickerBase):
    def __init__(
        self,
        ticker: str = "",
        isin: str = "",
        security_type: VALID_SECURITY_TYPES = "stock",
        data_source: VALID_DATA_SOURCES = "yahoo_api",
    ) -> None:
        self.ticker = ticker
        self.isin = isin
        self.security_type = security_type
        self.data_source = data_source

    today = datetime.today()
    five_years_ago = today.replace(year=today.year - 5)

    def yahoo_api_price(
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
        ----------------
        range (str): The range of the price data to retrieve
        valid values are "1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"

        dataGranularity (str): The granularity of the data to retrieve (interval)
        valid values are "1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h", "1d", "5d", "1wk", "1mo", "3mo""  # noqa: E501

        Returns:
        ----------------
        pd.DataFrame: The price data
        """

        url = f"{config.BASE_URL}/chart/{self.ticker}?range={range}&interval={dataGranularity}"
        response = self.get_response(url)

        meta = response.json()["chart"]["result"][0]["meta"]
        currency = meta["currency"]
        exchangeTimezoneName = meta["exchangeTimezoneName"]
        timezone = meta["timezone"]
        exchangeName = meta["exchangeName"]
        instrumentType = meta["instrumentType"]

        timestamp = (
            response.json()["chart"]["result"][0]["timestamp"]
            if "timestamp" in response.json()["chart"]["result"][0]
            else None
        )
        timestamp = (
            pd.to_datetime(timestamp, unit="s") if timestamp else ["Data Not Available"]
        )

        indicators = (
            response.json()
            .get("chart", {})
            .get("result", [{}])[0]
            .get("indicators", {})
        )

        quote = indicators.get("quote", [{}])[0]  # Get the first item safely

        volume = quote.get("volume", ["Data Not Available"])
        close = quote.get("close", ["Data Not Available"])
        open = quote.get("open", ["Data Not Available"])
        high = quote.get("high", ["Data Not Available"])
        low = quote.get("low", ["Data Not Available"])

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
            },
        )

    @property
    def yahoo_api_current_trading_period(self) -> pd.DataFrame:
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

    def yahoo_api_income_statement(
        self,
        frequency: Literal["annual", "quarterly"] = "annual",
        format: Literal["fmt", "raw"] = "fmt",
        period1: datetime = five_years_ago,
        period2: datetime = today,
    ) -> pd.DataFrame:
        """
        Get the income statement for the stock

        Args:
        ----------------
        frequency (str): The frequency of the data to retrieve
        valid values are "annual", "quarterly"

        format (str): The format of the data to retrieve
        valid values are "fmt", "raw"
        if "fmt" is used, the data will be in a human readable format, e.g. 1B
        if "raw" is used, the data will be in a raw format, e.g. 1000000000

        period1 (datetime): The start date of the data to retrieve
        default is five years ago as that is the maximum period the API supports data retrieval for

        period2 (datetime): The end date of the data to retrieve
        default is the current date

        Returns:
        ----------------
        pd.DataFrame: The income statement data
        """
        url = self.build_url(frequency, period1, period2, "income_statement")

        response = self.get_response(url).json()["timeseries"]["result"]

        return self.extract_dataframe(response, format)

    def yahoo_api_cash_flow(
        self,
        frequency: Literal["annual", "quarterly"] = "annual",
        format: Literal["fmt", "raw"] = "fmt",
        period1: datetime = five_years_ago,
        period2: datetime = today,
    ) -> pd.DataFrame:
        """
        Get the cash flow statement for the stock

        Args:
        ----------------
        frequency (str): The frequency of the data to retrieve
        valid values are "annual", "quarterly"

        format (str): The format of the data to retrieve
        valid values are "fmt", "raw"
        if "fmt" is used, the data will be in a human readable format, e.g. 1B
        if "raw" is used, the data will be in a raw format, e.g. 1000000000

        period1 (datetime): The start date of the data to retrieve
        default is five years ago as that is the maximum period the API supports data retrieval for

        period2 (datetime): The end date of the data to retrieve
        default is the current date

        Returns:
        ----------------
        pd.DataFrame: The cash flow statement data
        """
        url = self.build_url(frequency, period1, period2, "cash_flow")

        response = self.get_response(url).json()["timeseries"]["result"]

        return self.extract_dataframe(response, format)

    def yahoo_api_balance_sheet(
        self,
        frequency: Literal["annual", "quarterly"] = "annual",
        format: Literal["fmt", "raw"] = "fmt",
        period1: datetime = five_years_ago,
        period2: datetime = today,
    ) -> pd.DataFrame:
        """
        Get the balance sheet for the stock

        Args:
        ----------------
        frequency (str): The frequency of the data to retrieve
        valid values are "annual", "quarterly"

        format (str): The format of the data to retrieve
        valid values are "fmt", "raw"
        if "fmt" is used, the data will be in a human readable format, e.g. 1B
        if "raw" is used, the data will be in a raw format, e.g. 1000000000

        period1 (datetime): The start date of the data to retrieve
        default is five years ago as that is the maximum period the API supports data retrieval for

        period2 (datetime): The end date of the data to retrieve
        default is the current date

        Returns:
        ----------------
        pd.DataFrame: The balance sheet data
        """
        url = self.build_url(frequency, period1, period2, "balance_sheet")

        response = self.get_response(url).json()["timeseries"]["result"]

        return self.extract_dataframe(response, format)

    def yahoo_api_financials(
        self,
        frequency: Literal["annual", "quarterly"] = "annual",
        format: Literal["fmt", "raw"] = "fmt",
        period1: datetime = five_years_ago,
        period2: datetime = today,
    ) -> pd.DataFrame:
        """
        Get the financials for the stock

        Args:
        ----------------
        frequency (str): The frequency of the data to retrieve
        valid values are "annual", "quarterly"

        format (str): The format of the data to retrieve
        valid values are "fmt", "raw"
        if "fmt" is used, the data will be in a human readable format, e.g. 1B
        if "raw" is used, the data will be in a raw format, e.g. 1000000000

        period1 (datetime): The start date of the data to retrieve
        default is five years ago as that is the maximum period the API supports data retrieval for

        period2 (datetime): The end date of the data to retrieve
        default is the current date

        Returns:
        ----------------
        pd.DataFrame: The financials data
        """
        url = self.build_url(frequency, period1, period2, "financials")

        response = self.get_response(url).json()["timeseries"]["result"]

        return self.extract_dataframe(response, format)

    def yahoo_api_valuation_measures(
        self,
        frequency: Literal["annual", "quarterly", "trailing"] = "quarterly",
        format: Literal["fmt", "raw"] = "fmt",
        period1: datetime = five_years_ago,
        period2: datetime = today,
    ) -> pd.DataFrame:
        """
        Get valuation measures over time for the stock

        Columns are market cap, enterprise value, trailing and forward P/E,
        PEG, price/sales, price/book, EV/revenue and EV/EBITDA, each prefixed
        with the frequency (e.g. ``quarterlyPeRatio``).

        Args:
        ----------------
        frequency (str): The frequency of the data to retrieve
        valid values are "annual", "quarterly", "trailing"
        "trailing" returns recent daily snapshots (trailing twelve months)

        format (str): The format of the data to retrieve
        valid values are "fmt", "raw"
        if "fmt" is used, the data will be in a human readable format, e.g. 1B
        if "raw" is used, the data will be in a raw format, e.g. 1000000000

        period1 (datetime): The start date of the data to retrieve
        default is five years ago

        period2 (datetime): The end date of the data to retrieve
        default is the current date

        Returns:
        ----------------
        pd.DataFrame: The valuation measures, indexed by as-of date
        """
        url = self.build_url(frequency, period1, period2, "valuation")

        response = self.get_response(url).json()["timeseries"]["result"]

        return self.extract_dataframe(response, format).sort_index()

    def build_url(
        self,
        frequency: str,
        period1: datetime,
        period2: datetime,
        desired_entity: str,
    ) -> str:
        """
        Build the URL for the income statement, balance sheet, and cash flow statement

        Args:
        ----------------
        frequency: str
            The frequency of the data to retrieve
            valid values are "annual", "quarterly"

        period1: datetime
            The start date of the data to retrieve

        period2: datetime
            The end date of the data to retrieve

        desired_entity: str
            The entity to retrieve the data for

        Returns:
        ----------------
        str: The URL to retrieve the data from
        """
        # convert period1 and period2 to timestamps
        period1 = int(pd.Timestamp(period1).timestamp())
        period2 = int(pd.Timestamp(period2).timestamp())

        columns = ",".join(getattr(config, f"{desired_entity.upper()}_COLUMNS"))

        columns = ",".join([f"{frequency}{i}" for i in columns.split(",")])

        url = f"{config.FUNDAMENTALS_BASE_URL}/{self.ticker}/?symbol={self.ticker}"
        url += f"&type={columns}"
        url += f"&period1={period1}&period2={period2}"
        return url

    def extract_dataframe(self, response, format="fmt") -> pd.DataFrame:
        """
        Extract the dataframes from the response

        Args:
        ----------------
        response: dict
            The response from the API

        format: str
            The format of the data to retrieve

        Returns:
        ----------------
        pd.DataFrame: The data in a dataframe
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

        return pd.DataFrame(row)

    def _yahoo_api_chart_events(
        self, event: Literal["dividends", "splits", "capitalGains"], range: str
    ) -> pd.DataFrame:
        """
        Get one corporate-action event series from the Yahoo chart endpoint

        Args:
        ----------------
        event (str): "dividends", "splits" or "capitalGains"
        range (str): The range to retrieve, e.g. "5y" or "max"

        Returns:
        ----------------
        pd.DataFrame: One row per event, oldest first, indexed by event date (UTC).
        Empty if the security has no events of this type in the range.
        """
        # A monthly interval keeps the price payload small; events are returned
        # in full regardless of the bar interval.
        url = (
            f"{config.BASE_URL}/chart/{self.ticker}"
            f"?range={range}&interval=1mo&events=div,splits,capitalGains"
        )
        result = self.get_response(url).json()["chart"]["result"][0]
        currency = result.get("meta", {}).get("currency")
        events = result.get("events", {}).get(event, {})

        frame = pd.DataFrame(list(events.values()))
        if frame.empty:
            return frame
        frame["date"] = pd.to_datetime(frame["date"], unit="s", utc=True)
        if event != "splits" and "currency" not in frame:
            frame["currency"] = currency
        return frame.sort_values("date").set_index("date")

    def yahoo_api_dividends(
        self,
        range: Literal["1y", "2y", "5y", "10y", "ytd", "max"] = "max",
    ) -> pd.DataFrame:
        """
        Get the dividend history from Yahoo Finance

        Args:
        ----------------
        range (str): The range of history to retrieve
        valid values are "1y", "2y", "5y", "10y", "ytd", "max"

        Returns:
        ----------------
        pd.DataFrame: One row per dividend, indexed by ex-dividend date (UTC),
        with columns ``amount`` and ``currency``. Empty if no dividends were paid.
        """
        return self._yahoo_api_chart_events("dividends", range)

    def yahoo_api_splits(
        self,
        range: Literal["1y", "2y", "5y", "10y", "ytd", "max"] = "max",
    ) -> pd.DataFrame:
        """
        Get the stock split history from Yahoo Finance

        Args:
        ----------------
        range (str): The range of history to retrieve
        valid values are "1y", "2y", "5y", "10y", "ytd", "max"

        Returns:
        ----------------
        pd.DataFrame: One row per split, indexed by split date (UTC), with
        columns ``numerator``, ``denominator`` and ``splitRatio`` (e.g. "4:1").
        Empty if the stock never split.
        """
        return self._yahoo_api_chart_events("splits", range)

    def yahoo_api_capital_gains(
        self,
        range: Literal["1y", "2y", "5y", "10y", "ytd", "max"] = "max",
    ) -> pd.DataFrame:
        """
        Get capital gain distributions from Yahoo Finance (ETFs and mutual funds)

        Args:
        ----------------
        range (str): The range of history to retrieve
        valid values are "1y", "2y", "5y", "10y", "ytd", "max"

        Returns:
        ----------------
        pd.DataFrame: One row per distribution, indexed by date (UTC), with
        columns ``amount`` and ``currency``. Empty for most stocks.
        """
        return self._yahoo_api_chart_events("capitalGains", range)

    @staticmethod
    def _unwrap(value, format: Literal["fmt", "raw"] = "raw"):
        """
        Replace Yahoo's ``{"raw": ..., "fmt": ...}`` wrappers with one value

        Empty wrappers (``{}``), which Yahoo uses for missing values, become
        ``None``. Nested dicts and lists are unwrapped recursively.
        """
        if isinstance(value, dict):
            if "raw" in value or "fmt" in value:
                # Fall back to whichever representation Yahoo did send.
                return value.get(format, value.get("raw", value.get("fmt")))
            if not value:
                return None
            return {k: YahooAPI._unwrap(v, format) for k, v in value.items()}
        if isinstance(value, list):
            return [YahooAPI._unwrap(v, format) for v in value]
        return value

    def yahoo_api_quote_summary(
        self,
        modules: Union[str, list],
        format: Literal["fmt", "raw"] = "raw",
    ) -> dict:
        """
        Get one or more modules from Yahoo's quoteSummary endpoint

        This is the building block for the company, analyst, ownership and fund
        methods. Use it directly to fetch any module listed in
        ``stockdex.config.QUOTE_SUMMARY_MODULES``.

        Args:
        ----------------
        modules (str | list): One module name or a list of module names,
        e.g. ``"financialData"`` or ``["price", "summaryDetail"]``

        format (str): "raw" for numbers and epoch timestamps (default),
        "fmt" for Yahoo's human readable strings, e.g. "1.2B" or "2026-11-02"

        Returns:
        ----------------
        dict: Module name to module data. A requested module that Yahoo does
        not provide for this security is omitted.

        Raises:
        ----------------
        ValueError: If a module name is not supported
        """
        if isinstance(modules, str):
            modules = [modules]
        unknown = sorted(set(modules) - set(config.QUOTE_SUMMARY_MODULES))
        if not modules or unknown:
            raise ValueError(
                f"Unsupported quoteSummary module(s): {unknown or modules}. "
                f"Valid modules: {', '.join(config.QUOTE_SUMMARY_MODULES)}"
            )

        url = (
            f"{config.QUOTE_SUMMARY_URL}/{self.ticker}"
            f"?modules={','.join(modules)}&formatted=true"
        )
        try:
            response = self.get_response(url)
        except RuntimeError as error:
            # Yahoo answers 404 both for unknown symbols and when none of the
            # requested modules apply (e.g. fund modules for a stock).
            if "status 404" not in str(error):
                raise
            return self._quote_summary_not_found()
        results = response.json()["quoteSummary"]["result"] or [{}]
        data = results[0]
        return {
            module: self._unwrap(data[module], format)
            for module in modules
            if data.get(module) is not None
        }

    def _quote_summary_not_found(self) -> dict:
        """
        Decide what a quoteSummary 404 means for this ticker

        Returns an empty dict when the symbol exists (the requested modules
        just don't apply to it) and raises NoDataError when Yahoo does not
        know the symbol at all.
        """
        probe = (
            f"{config.QUOTE_SUMMARY_URL}/{self.ticker}?modules=quoteType&formatted=true"
        )
        try:
            self.get_response(probe)
        except RuntimeError as error:
            if "status 404" in str(error):
                raise NoDataError(
                    f"Yahoo Finance has no quote for symbol {self.ticker}"
                ) from None
            raise
        return {}

    _EPOCH_FIELDS = {
        "exDividendDate",
        "dividendDate",
        "lastDividendDate",
        "lastFiscalYearEnd",
        "nextFiscalYearEnd",
        "mostRecentQuarter",
        "lastSplitDate",
        "firstTradeDateEpochUtc",
        "regularMarketTime",
        "preMarketTime",
        "postMarketTime",
        "governanceEpochDate",
        "compensationAsOfEpochDate",
        "sharesShortPreviousMonthDate",
        "dateShortInterest",
        "epochGradeDate",
        "startDate",
        "reportDate",
        "latestTransDate",
        "positionDirectDate",
        "quarter",
        "epochDate",
    }

    @classmethod
    def _to_datetime(cls, key, value):
        """Convert known epoch-second fields to UTC timestamps."""
        if key in cls._EPOCH_FIELDS and isinstance(value, (int, float)):
            return pd.to_datetime(value, unit="s", utc=True)
        return value

    def _quote_summary_record(
        self, module: str, format: Literal["fmt", "raw"] = "raw", drop=()
    ) -> pd.DataFrame:
        """
        One quoteSummary module as a single-column DataFrame (field -> value)

        Nested values (dicts and lists) are left out; dedicated methods expose
        the nested parts that are useful on their own.
        """
        data = self.yahoo_api_quote_summary(module, format).get(module, {})
        values = {
            key: self._to_datetime(key, value) if format == "raw" else value
            for key, value in data.items()
            if key not in ("maxAge", *drop) and not isinstance(value, (dict, list))
        }
        return pd.DataFrame.from_dict(values, orient="index", columns=[self.ticker])

    def _quote_summary_table(
        self,
        module: str,
        key: str,
        format: Literal["fmt", "raw"] = "raw",
        data: Union[dict, None] = None,
    ) -> pd.DataFrame:
        """
        A list inside a quoteSummary module as a DataFrame, one row per item
        """
        if data is None:
            data = self.yahoo_api_quote_summary(module, format).get(module, {})
        rows = [
            {
                k: self._to_datetime(k, v) if format == "raw" else v
                for k, v in item.items()
                if k != "maxAge"
            }
            for item in data.get(key) or []
        ]
        return pd.DataFrame(rows)

    def yahoo_api_profile(self) -> pd.DataFrame:
        """
        Get the company profile from Yahoo Finance

        Returns:
        ----------------
        pd.DataFrame: Address, website, sector, industry, number of employees,
        business summary and governance risk scores, one row per field
        """
        return self._quote_summary_record("assetProfile", drop=("companyOfficers",))

    def yahoo_api_officers(self) -> pd.DataFrame:
        """
        Get the company's key executives from Yahoo Finance

        Returns:
        ----------------
        pd.DataFrame: One row per officer with name, title, age, year born,
        fiscal year and total pay (raw numbers)
        """
        return self._quote_summary_table("assetProfile", "companyOfficers")

    def yahoo_api_market_price(
        self, format: Literal["fmt", "raw"] = "raw"
    ) -> pd.DataFrame:
        """
        Get the current market price block from Yahoo Finance

        Includes regular, pre-market and post-market price and change,
        market state, currency, exchange and market cap.

        Args:
        ----------------
        format (str): "raw" for numbers and timestamps, "fmt" for display strings

        Returns:
        ----------------
        pd.DataFrame: One row per field
        """
        return self._quote_summary_record("price", format)

    def yahoo_api_summary_detail(
        self, format: Literal["fmt", "raw"] = "raw"
    ) -> pd.DataFrame:
        """
        Get the quote summary details from Yahoo Finance

        Includes previous close, open, day and 52-week ranges, volume,
        market cap, beta, trailing and forward P/E, dividend rate and yield,
        and ex-dividend date.

        Args:
        ----------------
        format (str): "raw" for numbers and timestamps, "fmt" for display strings

        Returns:
        ----------------
        pd.DataFrame: One row per field
        """
        return self._quote_summary_record("summaryDetail", format)

    def yahoo_api_key_statistics(
        self, format: Literal["fmt", "raw"] = "raw"
    ) -> pd.DataFrame:
        """
        Get key statistics from Yahoo Finance

        Includes enterprise value, forward P/E, PEG, price/book, shares
        outstanding and float, short interest, insider and institutional
        ownership, book value, last split and fiscal year dates.

        Args:
        ----------------
        format (str): "raw" for numbers and timestamps, "fmt" for display strings

        Returns:
        ----------------
        pd.DataFrame: One row per field
        """
        return self._quote_summary_record("defaultKeyStatistics", format)

    def yahoo_api_financial_data(
        self, format: Literal["fmt", "raw"] = "raw"
    ) -> pd.DataFrame:
        """
        Get financial data and analyst price targets from Yahoo Finance

        Includes current price, analyst target high/low/mean/median,
        recommendation, revenue, margins, cash flow, debt, return on equity
        and growth rates.

        Args:
        ----------------
        format (str): "raw" for numbers, "fmt" for display strings

        Returns:
        ----------------
        pd.DataFrame: One row per field
        """
        return self._quote_summary_record("financialData", format)

    def yahoo_api_calendar_events(self) -> pd.DataFrame:
        """
        Get upcoming earnings and dividend dates from Yahoo Finance

        Returns:
        ----------------
        pd.DataFrame: One row per field: next earnings date(s), earnings call
        date, whether the date is an estimate, EPS and revenue estimate
        average/low/high, ex-dividend date and dividend payment date
        """
        data = self.yahoo_api_quote_summary("calendarEvents").get("calendarEvents", {})
        earnings = data.get("earnings") or {}
        values = {}
        for key, value in earnings.items():
            if key in ("earningsDate", "earningsCallDate"):
                dates = [pd.to_datetime(v, unit="s", utc=True) for v in value or []]
                for i, date in enumerate(dates):
                    suffix = "" if len(dates) == 1 else f"_{i + 1}"
                    values[f"{key}{suffix}"] = date
            else:
                values[key] = value
        for key in ("exDividendDate", "dividendDate"):
            if data.get(key) is not None:
                values[key] = self._to_datetime(key, data[key])
        return pd.DataFrame.from_dict(values, orient="index", columns=[self.ticker])

    def yahoo_api_earnings_history(self) -> pd.DataFrame:
        """
        Get reported vs estimated EPS for the last four quarters

        Returns:
        ----------------
        pd.DataFrame: One row per quarter, oldest first, with ``quarter``
        (UTC timestamp), ``period`` (e.g. "-4q"), ``epsActual``,
        ``epsEstimate``, ``epsDifference``, ``surprisePercent`` and ``currency``
        """
        frame = self._quote_summary_table("earningsHistory", "history")
        if not frame.empty and "quarter" in frame:
            frame = frame.sort_values("quarter").reset_index(drop=True)
        return frame

    def yahoo_api_earnings_trend(self) -> pd.DataFrame:
        """
        Get analyst EPS and revenue estimates, trend and revisions

        Returns:
        ----------------
        pd.DataFrame: One row per period ("0q" current quarter, "+1q" next
        quarter, "0y" current year, "+1y" next year, plus long-term growth),
        with ``endDate``, ``growth`` and flattened estimate columns:
        ``earningsEstimate_*``, ``revenueEstimate_*``, ``epsTrend_*`` and
        ``epsRevisions_*``
        """
        data = self.yahoo_api_quote_summary("earningsTrend").get("earningsTrend", {})
        rows = []
        for item in data.get("trend") or []:
            row = {}
            for key, value in item.items():
                if key == "maxAge":
                    continue
                if isinstance(value, dict):
                    for sub_key, sub_value in value.items():
                        row[f"{key}_{sub_key}"] = sub_value
                else:
                    row[key] = value
            rows.append(row)
        return pd.DataFrame(rows)

    def yahoo_api_recommendation_trend(self) -> pd.DataFrame:
        """
        Get analyst recommendation counts for the last few months

        Returns:
        ----------------
        pd.DataFrame: One row per period ("0m" this month, "-1m" last month,
        ...) with ``strongBuy``, ``buy``, ``hold``, ``sell`` and ``strongSell``
        """
        return self._quote_summary_table("recommendationTrend", "trend")

    def yahoo_api_upgrades_downgrades(self) -> pd.DataFrame:
        """
        Get analyst upgrade and downgrade history

        Returns:
        ----------------
        pd.DataFrame: One row per rating action, newest first, with
        ``epochGradeDate`` (UTC timestamp), ``firm``, ``fromGrade``,
        ``toGrade``, ``action`` (up, down, main, init, reit) and price target
        changes
        """
        frame = self._quote_summary_table("upgradeDowngradeHistory", "history")
        if not frame.empty and "epochGradeDate" in frame:
            frame = frame.sort_values("epochGradeDate", ascending=False)
            frame = frame.reset_index(drop=True)
        return frame

    def yahoo_api_institutional_holders(self) -> pd.DataFrame:
        """
        Get the top institutional holders from Yahoo Finance

        Returns:
        ----------------
        pd.DataFrame: One row per institution with ``organization``,
        ``reportDate`` (UTC timestamp), ``pctHeld``, ``position`` (shares),
        ``value`` and ``pctChange``
        """
        return self._quote_summary_table("institutionOwnership", "ownershipList")

    def yahoo_api_fund_holders(self) -> pd.DataFrame:
        """
        Get the top mutual fund holders from Yahoo Finance

        Returns:
        ----------------
        pd.DataFrame: One row per fund with ``organization``, ``reportDate``
        (UTC timestamp), ``pctHeld``, ``position`` (shares), ``value`` and
        ``pctChange``
        """
        return self._quote_summary_table("fundOwnership", "ownershipList")

    def yahoo_api_major_holders(self) -> pd.DataFrame:
        """
        Get the ownership breakdown from Yahoo Finance

        Returns:
        ----------------
        pd.DataFrame: One row per field: ``insidersPercentHeld``,
        ``institutionsPercentHeld``, ``institutionsFloatPercentHeld`` and
        ``institutionsCount``
        """
        return self._quote_summary_record("majorHoldersBreakdown")

    def yahoo_api_insider_holders(self) -> pd.DataFrame:
        """
        Get insiders and their direct holdings from Yahoo Finance

        Returns:
        ----------------
        pd.DataFrame: One row per insider with ``name``, ``relation``,
        ``transactionDescription``, ``latestTransDate``, ``positionDirect``
        and ``positionDirectDate``
        """
        return self._quote_summary_table("insiderHolders", "holders")

    def yahoo_api_insider_transactions(self) -> pd.DataFrame:
        """
        Get recent insider transactions from Yahoo Finance

        Returns:
        ----------------
        pd.DataFrame: One row per transaction, newest first, with
        ``filerName``, ``filerRelation``, ``transactionText``, ``startDate``
        (UTC timestamp), ``shares``, ``value`` and ``ownership`` ("D" direct,
        "I" indirect)
        """
        frame = self._quote_summary_table("insiderTransactions", "transactions")
        if not frame.empty and "startDate" in frame:
            frame = frame.sort_values("startDate", ascending=False)
            frame = frame.reset_index(drop=True)
        return frame

    def yahoo_api_insider_purchase_activity(self) -> pd.DataFrame:
        """
        Get the net insider buying and selling summary from Yahoo Finance

        Returns:
        ----------------
        pd.DataFrame: One row per field for the reporting ``period`` (e.g.
        "6m"): buy, sell and net transaction counts and shares, percent of
        insider shares, total insider shares held and net institutional
        shares bought
        """
        return self._quote_summary_record("netSharePurchaseActivity")

    def yahoo_api_sec_filings(self) -> pd.DataFrame:
        """
        Get recent SEC filings from Yahoo Finance (US-listed companies)

        Returns:
        ----------------
        pd.DataFrame: One row per filing, newest first, with ``date``,
        ``type`` (e.g. "10-K", "8-K"), ``title`` and ``edgarUrl``. The
        ``exhibits`` column holds the filing's exhibit links.
        """
        frame = self._quote_summary_table("secFilings", "filings")
        if not frame.empty and "epochDate" in frame:
            frame = frame.sort_values("epochDate", ascending=False)
            frame = frame.reset_index(drop=True)
        return frame

    def _fund_module(self, module: str) -> dict:
        """Fetch one ETF/fund quoteSummary module (empty dict for stocks)."""
        return self.yahoo_api_quote_summary(module).get(module) or {}

    def yahoo_api_fund_top_holdings(self) -> pd.DataFrame:
        """
        Get the top holdings of an ETF or mutual fund

        Returns:
        ----------------
        pd.DataFrame: One row per holding with ``symbol``, ``holdingName``
        and ``holdingPercent`` (fraction of the fund, e.g. 0.083 = 8.3%).
        Empty for individual stocks.
        """
        return self._quote_summary_table(
            "topHoldings", "holdings", data=self._fund_module("topHoldings")
        )

    def yahoo_api_fund_sector_weightings(self) -> pd.DataFrame:
        """
        Get the sector weightings of an ETF or mutual fund

        Returns:
        ----------------
        pd.DataFrame: One row per sector (e.g. ``technology``,
        ``realestate``) with a ``weight`` column (fraction of the fund),
        largest first. Empty for individual stocks.
        """
        weightings = self._fund_module("topHoldings").get("sectorWeightings") or []
        weights = {
            sector: weight
            for item in weightings
            for sector, weight in item.items()
            if weight is not None
        }
        frame = pd.DataFrame.from_dict(weights, orient="index", columns=["weight"])
        return frame.sort_values("weight", ascending=False)

    def yahoo_api_fund_asset_allocation(self) -> pd.DataFrame:
        """
        Get the asset class allocation of an ETF or mutual fund

        Returns:
        ----------------
        pd.DataFrame: One row per position type (``stockPosition``,
        ``bondPosition``, ``cashPosition``, ``preferredPosition``,
        ``convertiblePosition``, ``otherPosition``) with the fraction of the
        fund. Empty for individual stocks.
        """
        data = self._fund_module("topHoldings")
        values = {
            key: value
            for key, value in data.items()
            if key.endswith("Position") and value is not None
        }
        return pd.DataFrame.from_dict(values, orient="index", columns=[self.ticker])

    def yahoo_api_fund_profile(self) -> pd.DataFrame:
        """
        Get the profile and fees of an ETF or mutual fund

        Returns:
        ----------------
        pd.DataFrame: One row per field: fund ``family``, ``categoryName``,
        ``legalType``, ``annualReportExpenseRatio``,
        ``annualHoldingsTurnover``, ``totalNetAssets`` and the category
        averages (suffixed ``_category``). Empty for individual stocks.
        """
        data = self._fund_module("fundProfile")
        values = {
            key: value
            for key, value in data.items()
            if key != "maxAge" and not isinstance(value, (dict, list))
        }
        fees = data.get("feesExpensesInvestment") or {}
        category = data.get("feesExpensesInvestmentCat") or {}
        for source, suffix in ((fees, ""), (category, "_category")):
            for key, value in source.items():
                if value is not None and not isinstance(value, (dict, list)):
                    values[f"{key}{suffix}"] = value
        return pd.DataFrame.from_dict(values, orient="index", columns=[self.ticker])

    def yahoo_api_fund_performance(self) -> pd.DataFrame:
        """
        Get trailing and annual total returns of an ETF or mutual fund

        Returns:
        ----------------
        pd.DataFrame: Rows are periods (``ytd``, ``oneMonth``, ``threeMonth``,
        ``oneYear``, ``threeYear``, ``fiveYear``, ``tenYear``, then calendar
        years such as ``2025``), with ``fund`` and ``category`` return
        columns as fractions (0.15 = 15%). Empty for individual stocks.
        """
        data = self._fund_module("fundPerformance")
        if not data:
            return pd.DataFrame()

        def trailing(block):
            return {
                key: value
                for key, value in (block or {}).items()
                if key not in ("asOfDate", "lastBullMkt", "lastBearMkt")
                and value is not None
            }

        def annual(items):
            return {
                str(item["year"]): item.get("annualValue")
                for item in items or []
                if item.get("annualValue") is not None
            }

        annual_returns = data.get("annualTotalReturns") or {}
        fund = {
            **trailing(data.get("trailingReturns")),
            **annual(annual_returns.get("returns")),
        }
        category = {
            **trailing(data.get("trailingReturnsCat")),
            **annual(annual_returns.get("returnsCat")),
        }
        return pd.DataFrame({"fund": fund, "category": category})

    def yahoo_api_option_expirations(self) -> list:
        """
        Get the available option expiration dates

        Returns:
        ----------------
        list: Expiration dates as UTC timestamps, nearest first. Empty if the
        security has no listed options.
        """
        results = (
            self.get_response(f"{config.OPTIONS_URL}/{self.ticker}")
            .json()
            .get("optionChain", {})
            .get("result")
            or []
        )
        dates = results[0].get("expirationDates", []) if results else []
        return [pd.to_datetime(d, unit="s", utc=True) for d in sorted(dates)]

    def yahoo_api_options_chain(
        self,
        expiration: Union[str, datetime, None] = None,
        option_type: Literal["calls", "puts", "both"] = "both",
    ) -> pd.DataFrame:
        """
        Get the options chain for one expiration date

        Args:
        ----------------
        expiration (str | datetime | None): Expiration date, e.g.
        "2026-11-20". Must be one of ``yahoo_api_option_expirations()``.
        Default is the nearest expiration.

        option_type (str): "calls", "puts" or "both" (default)

        Returns:
        ----------------
        pd.DataFrame: One row per contract with ``optionType`` ("call" or
        "put"), ``contractSymbol``, ``strike``, ``lastPrice``, ``bid``,
        ``ask``, ``change``, ``percentChange``, ``volume``, ``openInterest``,
        ``impliedVolatility``, ``inTheMoney``, ``expiration`` and
        ``lastTradeDate`` (UTC timestamps). Empty if there are no options.
        """
        url = f"{config.OPTIONS_URL}/{self.ticker}"
        if expiration is not None:
            timestamp = pd.Timestamp(expiration)
            if timestamp.tzinfo is None:
                timestamp = timestamp.tz_localize("UTC")
            url += f"?date={int(timestamp.timestamp())}"

        results = (
            self.get_response(url).json().get("optionChain", {}).get("result") or []
        )
        chains = results[0].get("options", []) if results else []
        if not chains:
            return pd.DataFrame()

        kinds = ("calls", "puts") if option_type == "both" else (option_type,)
        frames = []
        for kind in kinds:
            frame = pd.DataFrame(chains[0].get(kind) or [])
            if not frame.empty:
                frame.insert(0, "optionType", kind[:-1])
                frames.append(frame)
        if not frames:
            return pd.DataFrame()

        chain = pd.concat(frames, ignore_index=True)
        for column in ("expiration", "lastTradeDate"):
            if column in chain:
                chain[column] = pd.to_datetime(chain[column], unit="s", utc=True)
        return chain

    @staticmethod
    def yahoo_api_quotes(symbols: Union[str, list]) -> pd.DataFrame:
        """
        Get current quotes for several symbols in one request

        Args:
        ----------------
        symbols (str | list): One symbol or a list, e.g. ["AAPL", "MSFT"]

        Returns:
        ----------------
        pd.DataFrame: One row per symbol, indexed by symbol, with price,
        change, volume, market cap, 52-week range, P/E, dividend yield and
        market state. Symbols Yahoo does not recognise are left out.

        Raises:
        ----------------
        ValueError: If no symbols are given
        """
        if isinstance(symbols, str):
            symbols = [symbols]
        symbols = [s.strip().upper() for s in symbols if s and s.strip()]
        if not symbols:
            raise ValueError("Provide at least one symbol")

        url = f"{config.QUOTE_URL}?symbols={','.join(symbols)}"
        results = (
            YahooAPI().get_response(url).json().get("quoteResponse", {}).get("result")
            or []
        )
        frame = pd.DataFrame(results)
        if frame.empty:
            return frame
        for column in ("regularMarketTime", "preMarketTime", "postMarketTime"):
            if column in frame:
                frame[column] = pd.to_datetime(frame[column], unit="s", utc=True)
        return frame.set_index("symbol")

    @staticmethod
    def yahoo_api_search(query: str, limit: int = 10) -> pd.DataFrame:
        """
        Search Yahoo Finance for symbols matching a company name or ticker

        Args:
        ----------------
        query (str): Company name or partial symbol, e.g. "apple" or "BMW"
        limit (int): Maximum number of results, 1–50 (default 10)

        Returns:
        ----------------
        pd.DataFrame: Best match first, with ``symbol``, ``shortname``,
        ``longname``, ``quoteType`` (EQUITY, ETF, INDEX, ...), ``exchange``,
        ``exchDisp``, ``sector`` and ``industry`` where available

        Raises:
        ----------------
        ValueError: If the query is empty or the limit is out of range
        """
        if not query or not query.strip():
            raise ValueError("query must not be empty")
        if not 1 <= limit <= 50:
            raise ValueError("limit must be between 1 and 50")

        params = (
            f"q={requests_quote(query.strip())}&quotesCount={limit}"
            "&newsCount=0&listsCount=0&enableFuzzyQuery=false"
        )
        quotes = (
            YahooAPI()
            .get_response(f"{config.SEARCH_URL}?{params}")
            .json()
            .get("quotes")
            or []
        )
        columns = [
            "symbol",
            "shortname",
            "longname",
            "quoteType",
            "exchange",
            "exchDisp",
            "sector",
            "industry",
        ]
        frame = pd.DataFrame(quotes)
        if frame.empty:
            return pd.DataFrame(columns=columns)
        return frame[[c for c in columns if c in frame]]

    def yahoo_api_similar_symbols(self) -> pd.DataFrame:
        """
        Get symbols Yahoo Finance recommends as similar to this one

        Returns:
        ----------------
        pd.DataFrame: One row per related symbol with ``symbol`` and a
        relevance ``score``, highest first
        """
        results = (
            self.get_response(f"{config.RECOMMENDATIONS_URL}/{self.ticker}")
            .json()
            .get("finance", {})
            .get("result")
            or []
        )
        related = results[0].get("recommendedSymbols", []) if results else []
        frame = pd.DataFrame(related, columns=["symbol", "score"])
        return frame.sort_values("score", ascending=False).reset_index(drop=True)

    def plot_yahoo_api_income_statement(
        self,
        frequency: Literal["annual", "quarterly"] = "annual",
        period1: datetime = five_years_ago,
        period2: datetime = today,
        group_by: Literal["timeframe", "field"] = "timeframe",
        fields_to_include: list = [
            "TotalRevenue",
            "EBITDA",
            "TotalExpenses",
            "NetIncomeCommonStockholders",
            "NetIncome",
        ],
        show_plot: bool = True,
    ) -> Union[px.line, px.bar]:
        """
        Plots the income statement for the stock using matplotlib grouped bar chart

        Parameters
        ----------------
        frequency: str
            The frequency of the data to retrieve
            valid values are "annual", "quarterly"

        period1: datetime
            The start date of the data to retrieve

        period2: datetime
            The end date of the data to retrieve

        group_by: str
            The group by parameter

        fields_to_include: list
            The fields to include in the chart in the x-axis

        show_plot : bool
            If the plot should be shown or not.
            If dash is used, this should be set to False
            Default is True (show the plot)

        Returns:
        ----------------
        Union[px.line, px.bar]: The plotly figure
        """

        income_statement = self.yahoo_api_income_statement(
            frequency=frequency, period1=period1, period2=period2, format="raw"
        )

        income_statement = self._transform_df_for_plotting(
            df=income_statement,
            group_by=group_by,
            fields_to_include=fields_to_include,
            frequency=frequency,
        )

        x_axis_title = "Date" if group_by == "field" else "Field"

        # plot the income statement
        fig = plot_dataframe(
            income_statement,
            title=f"Income Statement for {self.ticker} ({frequency})",
            x_axis_title=x_axis_title,
            show_plot=show_plot,
        )

        return fig

    def plot_yahoo_api_cash_flow(
        self,
        frequency: Literal["annual", "quarterly"] = "annual",
        period1: datetime = five_years_ago,
        period2: datetime = today,
        group_by: Literal["timeframe", "field"] = "timeframe",
        fields_to_include: list = [
            "OperatingCashFlow",
            "FreeCashFlow",
        ],
        show_plot: bool = True,
    ) -> Union[px.line, px.bar]:
        """
        Plots the cash flow statement for the stock using matplotlib grouped bar chart

        Parameters
        ----------------
        frequency: str
            The frequency of the data to retrieve
            valid values are "annual", "quarterly"

        period1: datetime
            The start date of the data to retrieve

        period2: datetime
            The end date of the data to retrieve

        group_by: str
            The group by parameter

        fields_to_include: list
            The fields to include in the chart in the x-axis

        show_plot : bool
            If the plot should be shown or not.
            If dash is used, this should be set to False
            Default is True (show the plot)

        Returns:
        ----------------
        Union[px.line, px.bar]: The plotly figure
        """

        cash_flow = self.yahoo_api_cash_flow(
            frequency=frequency, period1=period1, period2=period2, format="raw"
        )

        cash_flow = self._transform_df_for_plotting(
            df=cash_flow,
            group_by=group_by,
            fields_to_include=fields_to_include,
            frequency=frequency,
        )

        x_axis_title = "Date" if group_by == "field" else "Field"

        # plot the cash flow
        fig = plot_dataframe(
            cash_flow,
            title=f"Cash Flow Statement for {self.ticker} ({frequency})",
            x_axis_title=x_axis_title,
            show_plot=show_plot,
        )

        return fig

    def plot_yahoo_api_balance_sheet(
        self,
        frequency: Literal["annual", "quarterly"] = "annual",
        period1: datetime = five_years_ago,
        period2: datetime = today,
        group_by: Literal["timeframe", "field"] = "timeframe",
        fields_to_include: list = [
            "TotalAssets",
            "TotalDebt",
        ],
        show_plot: bool = True,
    ) -> Union[px.line, px.bar]:
        """
        Plots the balance sheet for the stock using matplotlib grouped bar chart

        Parameters
        ----------------
        frequency: str
            The frequency of the data to retrieve
            valid values are "annual", "quarterly"

        period1: datetime
            The start date of the data to retrieve

        period2: datetime
            The end date of the data to retrieve

        group_by: str
            The group by parameter

        fields_to_include: list
            The fields to include in the chart in the x-axis

        show_plot : bool
            If the plot should be shown or not.
            If dash is used, this should be set to False
            Default is True (show the plot)

        Returns:
        ----------------
        Union[px.line, px.bar]: The plotly figure
        """

        balance_sheet = self.yahoo_api_balance_sheet(
            frequency=frequency, period1=period1, period2=period2, format="raw"
        )

        balance_sheet = self._transform_df_for_plotting(
            df=balance_sheet,
            group_by=group_by,
            fields_to_include=fields_to_include,
            frequency=frequency,
        )

        x_axis_title = "Date" if group_by == "field" else "Field"

        # plot the balance sheet
        fig = plot_dataframe(
            balance_sheet,
            title=f"Balance Sheet for {self.ticker} ({frequency})",
            x_axis_title=x_axis_title,
            show_plot=show_plot,
        )

        return fig

    def plot_yahoo_api_financials(
        self,
        frequency: Literal["annual", "quarterly"] = "annual",
        period1: datetime = five_years_ago,
        period2: datetime = today,
        group_by: Literal["timeframe", "field"] = "timeframe",
        fields_to_include: list = [
            "TotalRevenue",
            "EBITDA",
            "TotalExpenses",
            "NetIncomeCommonStockholders",
            "NetIncome",
        ],
        show_plot: bool = True,
    ) -> Union[px.line, px.bar]:
        """
        Plots the financials for the stock using matplotlib grouped bar chart

        Parameters
        ----------------
        frequency: str
            The frequency of the data to retrieve
            valid values are "annual", "quarterly"

        period1: datetime
            The start date of the data to retrieve

        period2: datetime
            The end date of the data to retrieve

        group_by: str
            The group by parameter

        fields_to_include: list
            The fields to include in the chart in the x-axis

        show_plot : bool
            If the plot should be shown or not.
            If dash is used, this should be set to False
            Default is True (show the plot)

        Returns:
        ----------------
        Union[px.line, px.bar]: The plotly figure
        """

        financials = self.yahoo_api_financials(
            frequency=frequency, period1=period1, period2=period2, format="raw"
        )

        financials = self._transform_df_for_plotting(
            df=financials,
            group_by=group_by,
            fields_to_include=fields_to_include,
            frequency=frequency,
        )

        x_axis_title = "Date" if group_by == "field" else "Field"

        # plot the financials
        fig = plot_dataframe(
            financials,
            title=f"Financials for {self.ticker} ({frequency})",
            x_axis_title=x_axis_title,
            show_plot=show_plot,
        )

        return fig

    def _transform_df_for_plotting(
        self, df: pd.DataFrame, group_by: str, fields_to_include: list, frequency: str
    ) -> pd.DataFrame:
        """
        Transform the dataframe for plotting

        Args:
        ----------------
        df: pd.DataFrame
            The dataframe to transform

        group_by: str
            The group by parameter

        fields_to_include: list
            The fields to include in the chart in the x-axis

        frequency: str
            The frequency of the data to retrieve
            valid values are "annual", "quarterly"


        Returns:
        ----------------
        pd.DataFrame: The transformed dataframe
        """
        fields_to_include = [f"{frequency}{i}" for i in fields_to_include]

        for field in fields_to_include:
            if field not in df.columns:
                raise FieldNotExists(available_fields=df.columns, given_field=field)

        # check if the fields to include are in the dataframe
        for field in fields_to_include:
            if field not in df.columns:
                raise ValueError(f"{field} is not in the cash flow")

        # remove the columns that are not needed
        df = df[fields_to_include]

        # remove the rows that are not needed
        df = df.dropna()

        if group_by == "timeframe":
            df = df.T

        return df
