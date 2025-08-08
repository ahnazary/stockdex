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

    def get_insider_trading(self) -> pd.DataFrame:
        """Fetch insider trading data for the specified ticker."""

        url = f"{FINVIZ_BASE_URL}{self.ticker}"
        response = self.get_response(
            url,
        )

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
