import json
from functools import lru_cache

import pandas as pd
import plotly.express as px
from bs4 import BeautifulSoup

from stockdex.config import FINVIZ_BASE_URL, VALID_SECURITY_TYPES
from stockdex.ticker_base import TickerBase


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
            raise RuntimeError("Insider trading data not found")

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

    @lru_cache(maxsize=None)
    def _finviz_earnings_reaction_raw_data(self) -> dict:
        """
        Return and caches the raw earnings reaction data.
        """

        url = f"{FINVIZ_BASE_URL}{self.ticker}&ty=ea&p=d"
        response = self.get_response(url)

        soup = BeautifulSoup(response.text, "html.parser")

        raw_data = soup.find("script", {"id": "route-init-data"})
        raw_data_json = json.loads(raw_data.string)

        return raw_data_json

    @lru_cache
    def _finviz_dividend_payout_history_raw_data(self) -> dict:
        """
        Return and caches the raw dividend payout history data.
        """

        url = f"{FINVIZ_BASE_URL}{self.ticker}&ty=dv&p=d"
        response = self.get_response(url)

        soup = BeautifulSoup(response.text, "html.parser")

        raw_data = soup.find("script", {"id": "route-init-data"})
        raw_data_json = json.loads(raw_data.string)

        return raw_data_json

    @lru_cache
    def _finviz_revenue_raw_data(self) -> dict:
        """
        Return and caches the raw revenue data.
        Fetch price reaction to earnings data for the specified ticker

        :return: DataFrame containing price reaction data
        """

        url = f"{FINVIZ_BASE_URL}{self.ticker}&ty=rv&p=d"

        response = self.get_response(url)

        soup = BeautifulSoup(response.text, "html.parser")

        raw_data = soup.find("script", {"id": "route-init-data"})
        raw_data_json = json.loads(raw_data.string)

        return raw_data_json

    def finviz_earnings_revisions_data(self) -> pd.DataFrame:
        """
        Fetch earnings revisions data for the specified ticker

        :return: DataFrame containing earnings revisions data
        """

        raw_data = self._finviz_earnings_reaction_raw_data()

        earnings_revisions_data = raw_data.get("earningsRevisionsData", [])
        df = pd.DataFrame(
            earnings_revisions_data, columns=earnings_revisions_data[0].keys()
        )
        df["ticker"] = self.ticker

        return df

    def finviz_earnings_annual_data(self) -> pd.DataFrame:
        """
        Fetch earnings annual data for the specified ticker

        :return: DataFrame containing earnings annual data
        """

        raw_data = self._finviz_earnings_reaction_raw_data()

        earnings_annual_data = raw_data.get("earningsAnnualData", [])
        df = pd.DataFrame(earnings_annual_data, columns=earnings_annual_data[0].keys())
        df["ticker"] = self.ticker

        return df

    def finviz_earnings_data(self) -> pd.DataFrame:
        """
        Fetch earnings data for the specified ticker

        :return: DataFrame containing earnings data
        """

        raw_data = self._finviz_earnings_reaction_raw_data()

        earnings_data = raw_data.get("earningsData", [])
        df = pd.DataFrame(earnings_data, columns=earnings_data[0].keys())
        df["ticker"] = self.ticker

        return df

    def finviz_overall_dividend(self) -> pd.DataFrame:
        """
        Fetch overall dividend data for the specified ticker

        :return: DataFrame containing overall dividend data
        """

        raw_data = self._finviz_dividend_payout_history_raw_data()

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

        dividend_date_data = raw_data.get("dividendsData", [])

        if dividend_date_data:
            df = pd.DataFrame(dividend_date_data, columns=dividend_date_data[0].keys())
        else:
            df = pd.DataFrame(columns=["Ticker", "Exdate", "Ordinary", "Special"])

        return df

    def finviz_dividends_annual_data(self) -> pd.DataFrame:
        """
        Fetch annual dividend data for the specified ticker

        :return: DataFrame containing annual dividend data
        """

        raw_data = self._finviz_dividend_payout_history_raw_data()

        dividend_annual_data = raw_data.get("dividendsAnnualData", [])
        df = pd.DataFrame(dividend_annual_data, columns=dividend_annual_data[0].keys())

        return df

    def finviz_revenue_by_products_and_services(self) -> dict:
        """
        Fetch revenue by products and services data for the specified ticker

        :return: a dict of dataframes for each service or product
        """

        raw_data = self._finviz_revenue_raw_data()

        revenue_data_raw = raw_data.get("products_and_services")
        if revenue_data_raw is None:
            return {}
        revenue_data = revenue_data_raw.get("revenues", [])

        result = {}
        for key, service_or_product in revenue_data.items():
            df = pd.DataFrame(service_or_product)
            result[key] = df

        return result

    def finviz_revenue_by_segment(self) -> dict:
        """
        Fetch revenue by segment data for the specified ticker

        :return: a dict of dataframes for each segment
        """

        raw_data = self._finviz_revenue_raw_data()

        revenue_data_raw = raw_data.get("segment")
        if revenue_data_raw is None:
            return {}
        revenue_data = revenue_data_raw.get("revenues", [])

        result = {}
        for key, segment in revenue_data.items():
            df = pd.DataFrame(segment)
            result[key] = df

        return result

    def finviz_revenue_by_regions(self) -> dict:
        """
        Fetch revenue by regions data for the specified ticker

        :return: a dict of dataframes for each region
        """

        raw_data = self._finviz_revenue_raw_data()

        revenue_data_raw = raw_data.get("regions")
        if revenue_data_raw is None:
            return {}
        revenue_data = revenue_data_raw.get("revenues", [])

        result = {}
        for key, region in revenue_data.items():
            df = pd.DataFrame(region)
            result[key] = df

        return result

    def finviz_price_reaction_to_earnings_report(self) -> pd.DataFrame:
        """
        Fetch price reaction to earnings report data for the specified ticker

        :return: DataFrame containing price reaction to earnings report data
        """
        raw_data = self._finviz_earnings_reaction_raw_data()

        price_reaction_data = raw_data.get("priceReactionData", [])
        df = pd.DataFrame(price_reaction_data, columns=price_reaction_data[0].keys())

        return df

    def _plot_finviz_revenue_data(self, data: dict, logarithmic: False) -> px.bar:
        for key, df in data.items():
            df["category"] = key

        fig = px.bar(
            pd.concat(data.values()),
            x="fiscal_year",
            y="value",
            color="category",
            title="Revenue by category",
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
