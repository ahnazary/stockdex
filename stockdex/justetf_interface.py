"""
Module for extracting ETF data from JustETF website
"""

from typing import Callable, Union

import pandas as pd
from bs4 import BeautifulSoup

from stockdex.config import JUSTETF_API_URL, JUSTETF_BASE_URL, VALID_SECURITY_TYPES
from stockdex.exceptions import LayoutChangedError, NoDataError, NoISINError
from stockdex.lib import check_security_type, instance_cache
from stockdex.ticker_base import TickerBase

# Columns of ``justetf_price``. justETF's quote API has no time of day,
# bid/ask or spread, so those columns are kept for compatibility and are None.
JUSTETF_PRICE_COLUMNS = [
    "price",
    "currency",
    "date",
    "time",
    "exchange",
    "daily_change",
    "daily_change_percent",
    "buy|sell",
    "spread",
    "previous_close",
    "previous_date",
    "52_week_low",
    "52_week_high",
]


class JustETF(TickerBase):
    def __init__(
        self,
        ticker: str = "",
        isin: str = "",
        security_type: VALID_SECURITY_TYPES = "etf",
    ) -> None:
        self.isin = isin
        self.ticker = ticker
        self.security_type = security_type
        if not isin or isin == "":
            raise NoISINError("No ISIN provided, please provide an ISIN")

    @instance_cache
    def _justetf_profile_soup(self) -> BeautifulSoup:
        """
        Download the ETF profile page once per instance

        Every profile section (overview, basics, holdings, countries,
        sectors, description) is in the static HTML of this page.

        Raises:
        ----------------
        NoDataError: justETF has no ETF with this ISIN (it redirects unknown
        ISINs to its search page)
        """
        check_security_type(self.security_type, valid_types=["etf"])

        url = f"{JUSTETF_BASE_URL}/etf-profile.html?isin={self.isin}"
        response = self.get_response(url)

        if "etf-profile.html" not in str(getattr(response, "url", url)):
            raise NoDataError(f"justETF has no ETF with the ISIN {self.isin}")

        return BeautifulSoup(response.text, "html.parser")

    def _justetf_find(self, finder: Callable, section: str):
        """Run ``finder`` on the profile page; a missing section is a layout change"""
        element = finder(self._justetf_profile_soup())
        if element is None:
            raise LayoutChangedError("justETF", f"{section} section not found")
        return element

    @property
    def justetf_general_info(self) -> pd.DataFrame:
        """
        Get the general information of the ETF
        genral information includes TER, distribution policy, replication method, etc.
        """
        check_security_type(self.security_type, valid_types=["etf"])

        general_info = self._justetf_find(
            lambda soup: soup.find("div", {"class": "data-overview mt-4 mb-3"}),
            "overview",
        )

        data_df = pd.DataFrame()
        for label in general_info.find_all("div", {"class": "vallabel"}):
            column = label.text.replace(" ", "")
            value = label.find_next_sibling("div").text

            data_df[column] = [value]

        return data_df

    @property
    def justetf_wkn(self) -> str:
        """
        Get the identifier justETF shows next to the ISIN

        This is the WKN for ETFs listed in Germany; for some ETFs justETF
        shows the exchange ticker (e.g. ``IWDA``) instead.
        """
        check_security_type(self.security_type, valid_types=["etf"])

        # <span class="d-inline-block" id="etf_identifier_1">A0RPWH</span>
        return self._justetf_find(
            lambda soup: soup.find("span", {"id": "etf_identifier_1"}), "identifier"
        ).text

    @property
    def justetf_description(self) -> str:
        """
        Get the description of the ETF
        """
        check_security_type(self.security_type, valid_types=["etf"])

        return self._justetf_find(
            lambda soup: soup.find("div", {"id": "etf-description"}), "description"
        ).text

    @property
    def justetf_basics(self) -> pd.DataFrame:
        """
        Get the baisc information of the ETF

        columns may include:
        - Fund size
        - Fund domicile
        - Legal structure
        - Replication

        Returns:
        ----------------
        pd.DataFrame: DataFrame containing the basic information of the ETF
        """
        check_security_type(self.security_type, valid_types=["etf"])

        table = self._justetf_find(
            lambda soup: soup.find("table", {"class": "table etf-data-table"}),
            "basics",
        )

        data_df = pd.DataFrame()
        for row in table.find_all("tr"):
            column = row.find_all("td")
            if len(column) < 2:
                continue
            data_df[column[0].text.strip()] = [column[1].text.strip()]

        return data_df

    def _justetf_weights(self, heading: str, index_name: str) -> pd.DataFrame:
        """
        Read a two-column weight table that follows an ``<h3>`` heading

        Returns:
        ----------------
        pd.DataFrame: indexed by ``index_name``, one column "shares in percent"
        """
        check_security_type(self.security_type, valid_types=["etf"])

        def finder(soup):
            title = soup.find(lambda tag: tag.name == "h3" and heading in tag.text)
            table = title.find_next("table") if title else None
            return table.find("tbody") if table else None

        table_body = self._justetf_find(finder, heading)

        names, shares_percent = [], []
        for row in table_body.find_all("tr"):
            columns = row.find_all("td")
            if len(columns) < 2:
                continue
            names.append(columns[0].text.strip())
            shares_percent.append(columns[1].text.strip())

        data_df = pd.DataFrame({index_name: names, "shares in percent": shares_percent})
        return data_df.set_index(index_name)

    @property
    def justetf_holdings_companies(self) -> pd.DataFrame:
        """
        Get the top 10 holdings of the ETF by companies

        columns may include:
        - company name
        - shares in percent

        Returns:
        ----------------
        pd.DataFrame: DataFrame containing the holdings of the ETF
        """
        return self._justetf_weights("Top 10 Holdings", "company name")

    @property
    def justetf_holdings_countries(self) -> pd.DataFrame:
        """
        Get the holdings of the ETF by countries

        columns may include:
        - country name
        - shares in percent

        Returns:
        ----------------
        pd.DataFrame: DataFrame containing the holdings of the ETF
        """
        return self._justetf_weights("Countries", "country name")

    @property
    def justetf_holdings_sectors(self) -> pd.DataFrame:
        """
        Get the holdings of the ETF by sectors

        columns may include:
        - sector name
        - shares in percent

        Returns:
        ----------------
        pd.DataFrame: DataFrame containing the holdings of the ETF
        """
        return self._justetf_weights("Sectors", "sector name")

    @property
    def justetf_price(self) -> pd.DataFrame:
        """
        Get the latest quote of the ETF in EUR

        Same as ``justetf_quote("EUR")``.
        """
        return self.justetf_quote()

    @instance_cache
    def justetf_quote(self, currency: str = "EUR") -> pd.DataFrame:
        """
        Get the latest quote of the ETF from justETF's quote API

        Args:
        ----------------
        currency (str): Currency of the quote, e.g. "EUR", "USD", "GBP", "CHF"

        Returns:
        ----------------
        pd.DataFrame: One row with the columns in ``JUSTETF_PRICE_COLUMNS``:
        ``price``, ``currency``, ``date`` (YYYY-MM-DD), ``time`` (None),
        ``exchange``, ``daily_change``, ``daily_change_percent``,
        ``buy|sell`` (None), ``spread`` (None), ``previous_close``,
        ``previous_date``, ``52_week_low`` and ``52_week_high``.
        Prices are numbers, not localized strings.
        """
        check_security_type(self.security_type, valid_types=["etf"])
        currency = str(currency).upper()

        url = (
            f"{JUSTETF_API_URL}/etfs/{self.isin}/quote"
            f"?locale=en&currency={currency}&isin={self.isin}"
        )
        response = self.get_response(url, headers={"Accept": "application/json"})
        try:
            data = response.json()
        except ValueError as error:
            raise LayoutChangedError("justETF", "quote is not JSON") from error
        if not isinstance(data, dict) or "latestQuote" not in data:
            raise NoDataError(f"justETF has no quote for the ISIN {self.isin}")

        def raw(value: Union[dict, None]):
            return value.get("raw") if isinstance(value, dict) else None

        low_high = data.get("quoteLowHigh") or {}
        row = {
            "price": raw(data.get("latestQuote")),
            "currency": currency,
            "date": data.get("latestQuoteDate"),
            "time": None,
            "exchange": data.get("quoteTradingVenue"),
            "daily_change": raw(data.get("dtdAmt")),
            "daily_change_percent": raw(data.get("dtdPrc")),
            "buy|sell": None,
            "spread": None,
            "previous_close": raw(data.get("previousQuote")),
            "previous_date": data.get("previousQuoteDate"),
            "52_week_low": raw(low_high.get("low")),
            "52_week_high": raw(low_high.get("high")),
        }
        if row["price"] is None:
            raise NoDataError(f"justETF has no quote for the ISIN {self.isin}")

        return pd.DataFrame([row], columns=JUSTETF_PRICE_COLUMNS)
