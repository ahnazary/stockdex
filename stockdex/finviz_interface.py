import json

import pandas as pd
import plotly.express as px
from bs4 import BeautifulSoup

from stockdex.config import FINVIZ_BASE_URL, VALID_SECURITY_TYPES
from stockdex.exceptions import LayoutChangedError
from stockdex.lib import instance_cache
from stockdex.ticker_base import TickerBase


def _records_frame(records) -> pd.DataFrame:
    """A list of dicts as a DataFrame; an empty list gives an empty frame."""
    if not isinstance(records, list) or not all(isinstance(r, dict) for r in records):
        raise LayoutChangedError("Finviz", "expected a list of records")
    return pd.DataFrame(records)


class FinvizInterface(TickerBase):
    def __init__(
        self,
        ticker: str,
        isin: str = "",
        security_type: VALID_SECURITY_TYPES = "stock",
    ) -> None:
        self.isin = isin
        self.ticker = ticker
        self.security_type = security_type

    def finviz_get_insider_trading(self) -> pd.DataFrame:
        """Fetch insider trading data for the specified ticker."""

        url = f"{FINVIZ_BASE_URL}{self.ticker}"
        response = self.get_response(url)

        soup = BeautifulSoup(response.text, "html.parser")

        table = self.find_parent_by_text(
            soup,
            tag="table",
            text="Insider Trading",
            condition={"class": "body-table"},
        )

        if table is None:
            raise LayoutChangedError("Finviz", "insider trading table not found")

        columns = table.find_all("th")
        column_names = [col.get_text(strip=True) for col in columns]

        rows = table.find_all("tr")[1:]  # Skip header row
        data = []

        for row in rows:
            cells = row.find_all("td")
            if len(cells) != len(column_names):
                continue
            row_data = [cell.get_text(strip=True) for cell in cells]
            data.append(row_data)

        return pd.DataFrame(data, columns=column_names)

    def _finviz_route_data(self, view: str) -> dict:
        """The JSON data block Finviz embeds in a quote sub-page"""
        url = f"{FINVIZ_BASE_URL}{self.ticker}&ty={view}&p=d"
        response = self.get_response(url)

        soup = BeautifulSoup(response.text, "html.parser")

        raw_data = soup.find("script", {"id": "route-init-data"})
        if raw_data is None or not raw_data.string:
            raise LayoutChangedError("Finviz", f"no route-init-data on the {view} page")
        try:
            data = json.loads(raw_data.string)
        except json.JSONDecodeError as error:
            raise LayoutChangedError(
                "Finviz", f"route-init-data on the {view} page is not JSON"
            ) from error
        if not isinstance(data, dict):
            raise LayoutChangedError("Finviz", f"unexpected {view} data layout")
        return data

    @instance_cache
    def _finviz_earnings_reaction_raw_data(self) -> dict:
        """
        Return and caches the raw earnings reaction data.
        """
        return self._finviz_route_data("ea")

    @instance_cache
    def _finviz_dividend_payout_history_raw_data(self) -> dict:
        """
        Return and caches the raw dividend payout history data.
        """
        return self._finviz_route_data("dv")

    @instance_cache
    def _finviz_revenue_raw_data(self) -> dict:
        """
        Return and caches the raw revenue data.
        """
        return self._finviz_route_data("rv")

    def finviz_earnings_revisions_data(self) -> pd.DataFrame:
        """
        Fetch earnings revisions data for the specified ticker

        :return: DataFrame containing earnings revisions data
        """

        raw_data = self._finviz_earnings_reaction_raw_data()

        df = _records_frame(raw_data.get("earningsRevisionsData", []))
        if not df.empty:
            df["ticker"] = self.ticker

        return df

    def finviz_earnings_annual_data(self) -> pd.DataFrame:
        """
        Fetch earnings annual data for the specified ticker

        :return: DataFrame containing earnings annual data
        """

        raw_data = self._finviz_earnings_reaction_raw_data()

        df = _records_frame(raw_data.get("earningsAnnualData", []))
        if not df.empty:
            df["ticker"] = self.ticker

        return df

    def finviz_earnings_data(self) -> pd.DataFrame:
        """
        Fetch earnings data for the specified ticker

        :return: DataFrame containing earnings data
        """

        raw_data = self._finviz_earnings_reaction_raw_data()

        df = _records_frame(raw_data.get("earningsData", []))
        if not df.empty:
            df["ticker"] = self.ticker

        return df

    def finviz_overall_dividend(self) -> pd.DataFrame:
        """
        Fetch overall dividend data for the specified ticker

        :return: DataFrame containing overall dividend data
        """

        raw_data = dict(self._finviz_dividend_payout_history_raw_data())

        raw_data.pop("dividendsData", None)
        raw_data.pop("dividendsAnnualData", None)

        df = pd.DataFrame([raw_data])

        return df

    def finviz_dividends_date_data(self) -> pd.DataFrame:
        """
        Fetch dividend date data for the specified ticker

        :return: DataFrame containing dividend date data
        """

        raw_data = self._finviz_dividend_payout_history_raw_data()

        df = _records_frame(raw_data.get("dividendsData", []))
        if df.empty:
            df = pd.DataFrame(columns=["Ticker", "Exdate", "Ordinary", "Special"])

        return df

    def finviz_dividends_annual_data(self) -> pd.DataFrame:
        """
        Fetch annual dividend data for the specified ticker

        :return: DataFrame containing annual dividend data
        """

        raw_data = self._finviz_dividend_payout_history_raw_data()

        return _records_frame(raw_data.get("dividendsAnnualData", []))

    def _finviz_revenue_breakdown(self, key: str) -> dict:
        raw_data = self._finviz_revenue_raw_data()

        revenue_data_raw = raw_data.get(key)
        if revenue_data_raw is None:
            return {}
        revenue_data = revenue_data_raw.get("revenues") or {}
        if not isinstance(revenue_data, dict):
            raise LayoutChangedError("Finviz", f"unexpected {key} revenue layout")

        return {name: pd.DataFrame(rows) for name, rows in revenue_data.items()}

    def finviz_revenue_by_products_and_services(self) -> dict:
        """
        Fetch revenue by products and services data for the specified ticker

        :return: a dict of dataframes for each service or product
        """
        return self._finviz_revenue_breakdown("products_and_services")

    def finviz_revenue_by_segment(self) -> dict:
        """
        Fetch revenue by segment data for the specified ticker

        :return: a dict of dataframes for each segment
        """
        return self._finviz_revenue_breakdown("segment")

    def finviz_revenue_by_regions(self) -> dict:
        """
        Fetch revenue by regions data for the specified ticker

        :return: a dict of dataframes for each region
        """
        return self._finviz_revenue_breakdown("regions")

    def finviz_price_reaction_to_earnings_report(self) -> pd.DataFrame:
        """
        Fetch price reaction to earnings report data for the specified ticker

        :return: DataFrame containing price reaction to earnings report data
        """
        raw_data = self._finviz_earnings_reaction_raw_data()

        return _records_frame(raw_data.get("priceReactionData", []))

    def _plot_finviz_revenue_data(self, data: dict, logarithmic: False) -> px.bar:
        for key, df in data.items():
            df["category"] = key

        fig = px.bar(
            pd.concat(data.values()),
            x="fiscal_year",
            y="value",
            color="category",
            title=f"Revenue by category for {self.ticker}",
            barmode="group",
            log_y=logarithmic,
        )

        fig.update_xaxes(title_text="Fiscal Year")
        fig.update_yaxes(title_text="Revenue")
        return fig

    def plot_finviz_revenue_by_regions(self, logarithmic: bool) -> None:
        """
        Plot revenue by regions data for the specified ticker

        :return: None
        """
        data = self.finviz_revenue_by_regions()
        fig = self._plot_finviz_revenue_data(data, logarithmic=logarithmic)

        fig.show()

    def plot_finviz_revenue_by_segments(self, logarithmic: bool) -> None:
        """
        Plot revenue by segments data for the specified ticker

        :return: None
        """
        data = self.finviz_revenue_by_segment()
        fig = self._plot_finviz_revenue_data(data, logarithmic=logarithmic)

        fig.show()

    def plot_finviz_revenue_by_products_and_services(self, logarithmic: bool) -> None:
        """
        Plot revenue by products and services data for the specified ticker

        :return: None
        """
        data = self.finviz_revenue_by_products_and_services()
        fig = self._plot_finviz_revenue_data(data, logarithmic=logarithmic)

        fig.show()
