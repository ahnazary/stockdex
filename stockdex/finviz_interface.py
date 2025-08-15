import json
from functools import lru_cache

import pandas as pd
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

    def finviz_price_reaction_to_earnings_report(self) -> pd.DataFrame:
        """
        Fetch price reaction to earnings data for the specified ticker

        :return: DataFrame containing price reaction data
        """

        raw_data = self._finviz_earnings_reaction_raw_data()

        price_reaction_data = raw_data.get("priceReactionData", [])
        df = pd.DataFrame(price_reaction_data, columns=price_reaction_data[0].keys())

        return df

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
