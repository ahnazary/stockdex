"""
Interface for NASDAQ stock data

Reads the JSON API behind nasdaq.com (``api.nasdaq.com``); no browser needed.
"""

import pandas as pd

from stockdex.config import NASDAQ_API_URL, VALID_SECURITY_TYPES
from stockdex.exceptions import LayoutChangedError, NoDataError
from stockdex.lib import check_security_type, instance_cache
from stockdex.ticker_base import TickerBase


class NASDAQInterface(TickerBase):
    def __init__(
        self,
        ticker: str = "",
        isin: str = "",
        security_type: VALID_SECURITY_TYPES = "stock",
    ) -> None:
        self.isin = isin
        self.ticker = ticker
        self.security_type = security_type

    @instance_cache
    def _nasdaq_data(self, path: str) -> dict:
        """
        The ``data`` object of one Nasdaq API endpoint, fetched once

        Args:
        ----------------
        path (str): e.g. "company/AAPL/earnings-surprise"

        Raises:
        ----------------
        NoDataError: Nasdaq has no data for the ticker
        LayoutChangedError: The response is not the expected JSON envelope
        """
        check_security_type(security_type=self.security_type, valid_types=["stock"])

        response = self.get_response(
            f"{NASDAQ_API_URL}/{path}", headers={"Accept": "application/json"}
        )
        try:
            payload = response.json()
        except ValueError as error:
            raise LayoutChangedError("Nasdaq", f"{path} is not JSON") from error
        if not isinstance(payload, dict):
            raise LayoutChangedError("Nasdaq", f"{path} has no data object")
        data = payload.get("data")
        if not data:
            raise NoDataError(f"Nasdaq has no data for the ticker {self.ticker}")
        return data

    @staticmethod
    def _nasdaq_table(table: dict, name: str) -> pd.DataFrame:
        """
        A Nasdaq ``{"headers": {key: label}, "rows": [...]}`` table as a
        DataFrame whose columns are the header labels, in header order
        """
        if not isinstance(table, dict) or not isinstance(table.get("headers"), dict):
            raise LayoutChangedError("Nasdaq", f"{name} table has no headers")
        headers = table["headers"]
        rows = table.get("rows") or []
        return pd.DataFrame(
            [[row.get(key) for key in headers] for row in rows],
            columns=list(headers.values()),
        )

    def _earnings_forecast(self, key: str) -> pd.DataFrame:
        data = self._nasdaq_data(f"analyst/{self.ticker.upper()}/earnings-forecast")
        return self._nasdaq_table(data.get(key), key)

    @property
    def quarterly_earnings_surprise(self) -> pd.DataFrame:
        """
        Get quarterly earnings for the stock

        Returns:
        ----------------
        pd.DataFrame: Quarterly earnings surprise data, newest first
        The columns might include:
        - 'Fiscal Quarter End'
        - 'Date Reported'
        - 'Earnings Per Share*'
        - 'Consensus EPS* Forecast'
        - '% Surprise'
        """
        data = self._nasdaq_data(f"company/{self.ticker.upper()}/earnings-surprise")
        return self._nasdaq_table(
            data.get("earningsSurpriseTable"), "earnings surprise"
        )

    @property
    def yearly_earnings_forecast(self) -> pd.DataFrame:
        """
        Get yearly earnings for the stock

        Returns:
        ----------------
        pd.DataFrame: Yearly earnings data
        The columns might include:
        - Fiscal Year End
        - Consensus EPS* Forecast
        - High EPS* Forecast
        - Low EPS* Forecast
        - Number of Estimates
        - Over the Last 4 Weeks Number of Revisions - Up
        - Over the Last 4 Weeks Number of Revisions - Down
        """
        return self._earnings_forecast("yearlyForecast")

    @property
    def quarterly_earnings_forecast(self) -> pd.DataFrame:
        """
        Get quarterly earnings forecast for the stock

        Returns:
        ----------------
        pd.DataFrame: Quarterly earnings forecast data
        The columns might include:
        - Fiscal Quarter End
        - Consensus EPS* Forecast
        - High EPS* Forecast
        - Low EPS* Forecast
        - Number of Estimates
        - Over the Last 4 Weeks Number of Revisions - Up
        - Over the Last 4 Weeks Number of Revisions - Down
        """
        return self._earnings_forecast("quarterlyForecast")

    def _peg_data(self) -> dict:
        return self._nasdaq_data(f"analyst/{self.ticker.upper()}/peg-ratio")

    @property
    def price_to_earnings_ratio(self) -> pd.DataFrame:
        """
        Get the price to earnings ratio for the stock

        Returns:
        ----------------
        pd.DataFrame: Price to earnings ratio per fiscal year, indexed by
        period label such as "2025 Actual" or "2026 Estimates", with the
        column "Price to Earnings Ratio"
        """
        chart = (self._peg_data().get("per") or {}).get("peRatioChart")
        if not isinstance(chart, list):
            raise LayoutChangedError("Nasdaq", "P/E ratio chart not found")

        return pd.DataFrame(
            [point.get("y") for point in chart],
            index=[point.get("x") for point in chart],
            columns=["Price to Earnings Ratio"],
        )

    @property
    def forecast_peg_rate(self) -> pd.DataFrame:
        """
        Get the forecast price to earning growth rate for the stock

        Returns:
        ----------------
        pd.DataFrame: Forecast earnings growth rate (percent) per fiscal year,
        indexed by year, with the column
        "Forecast Price to Earning Growth Rate". The 12-month forward PEG
        ratio is the row "Forecast 12 Month Forward PEG Ratio".
        """
        data = self._peg_data()
        chart = (data.get("gr") or {}).get("peGrowthChart")
        if not isinstance(chart, list):
            raise LayoutChangedError("Nasdaq", "P/E growth chart not found")

        index, value = [], []
        for point in chart:
            if point.get("z") == "Growth":
                index.append(point.get("x"))
                value.append(point.get("y"))

        pegr = data.get("pegr") or {}
        if pegr.get("pegValue") is not None:
            index.append(pegr.get("label") or "Forecast 12 Month Forward PEG Ratio")
            value.append(pegr["pegValue"])

        return pd.DataFrame(
            value, index=index, columns=["Forecast Price to Earning Growth Rate"]
        )
