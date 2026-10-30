"""
Deprecated ``yahoo_web_*`` attributes

The Yahoo Finance website scraper was removed in 1.5.0 because every dataset
it scraped is available from the Yahoo Finance API. The old attribute names
still work: each one emits a ``DeprecationWarning`` and returns the data from
its ``yahoo_api_*`` replacement. The column layout of the returned frames
follows the API method, not the old scraped table. The security type checks
of the old attributes are kept.

One dataset is no longer available: the S&P 500 benchmark row of
``yahoo_web_growth_estimates``. The API only returns the company's own growth
estimates.

These attributes will be removed in 2.0.
"""

import re
import warnings

import pandas as pd

from stockdex.config import VALID_SECURITY_TYPES
from stockdex.lib import check_security_type
from stockdex.ticker_base import TickerBase

REMOVAL_VERSION = "2.0"

# Old attribute -> replacement shown in the warning
REPLACEMENTS = {
    "yahoo_web_financials_table": (
        "yahoo_api_income_statement(), yahoo_api_balance_sheet() or "
        "yahoo_api_cash_flow()"
    ),
    "yahoo_web_income_stmt": "yahoo_api_income_statement()",
    "yahoo_web_balance_sheet": "yahoo_api_balance_sheet()",
    "yahoo_web_cashflow": "yahoo_api_cash_flow()",
    "yahoo_web_calls": 'yahoo_api_options_chain(option_type="calls")',
    "yahoo_web_puts": 'yahoo_api_options_chain(option_type="puts")',
    "yahoo_web_description": 'yahoo_api_profile().loc["longBusinessSummary"]',
    "yahoo_web_key_executives": "yahoo_api_officers()",
    "yahoo_web_corporate_governance": "yahoo_api_profile() (the *Risk rows)",
    "yahoo_web_major_holders": "yahoo_api_major_holders()",
    "yahoo_web_top_institutional_holders": "yahoo_api_institutional_holders()",
    "yahoo_web_top_mutual_fund_holders": "yahoo_api_fund_holders()",
    "yahoo_web_summary": "yahoo_api_market_price() and yahoo_api_summary_detail()",
    "yahoo_web_valuation_measures": (
        "yahoo_api_valuation_measures() for the history and "
        'yahoo_api_valuation_measures(frequency="trailing") for current values'
    ),
    "yahoo_web_financial_highlights": (
        "yahoo_api_financial_data() and yahoo_api_key_statistics()"
    ),
    "yahoo_web_trading_information": (
        "yahoo_api_key_statistics() and yahoo_api_summary_detail()"
    ),
    "yahoo_web_full_name": "yahoo_api_company_name()",
    "yahoo_web_earnings_estimate": "yahoo_api_earnings_trend() (earningsEstimate_*)",
    "yahoo_web_revenue_estimate": "yahoo_api_earnings_trend() (revenueEstimate_*)",
    "yahoo_web_earnings_history": "yahoo_api_earnings_history()",
    "yahoo_web_eps_trend": "yahoo_api_earnings_trend() (epsTrend_*)",
    "yahoo_web_eps_revisions": "yahoo_api_earnings_trend() (epsRevisions_*)",
    "yahoo_web_growth_estimates": (
        "yahoo_api_earnings_trend() (growth; the S&P 500 benchmark is no "
        "longer available)"
    ),
}

# Security types each old attribute accepted. Attributes not listed had no check.
VALID_TYPES = {
    **{
        name: ["stock"]
        for name in REPLACEMENTS
        if name not in ("yahoo_web_calls", "yahoo_web_puts", "yahoo_web_description")
    },
    "yahoo_web_calls": ["stock", "etf"],
    "yahoo_web_puts": ["stock", "etf"],
}
del VALID_TYPES["yahoo_web_financials_table"]

# Fields the old tables showed from a second quoteSummary module
FINANCIAL_HIGHLIGHT_DATES = ("lastFiscalYearEnd", "mostRecentQuarter")
TRADING_SUMMARY_FIELDS = (
    "fiftyTwoWeekHigh",
    "fiftyTwoWeekLow",
    "fiftyDayAverage",
    "twoHundredDayAverage",
    "averageVolume",
    "averageVolume10days",
    "beta",
    "dividendRate",
    "dividendYield",
    "trailingAnnualDividendRate",
    "trailingAnnualDividendYield",
    "fiveYearAvgDividendYield",
    "payoutRatio",
    "exDividendDate",
)

# URL suffix of the old statement pages -> replacement method
STATEMENT_URLS = {
    "financials": "yahoo_api_income_statement",
    "balance-sheet": "yahoo_api_balance_sheet",
    "cash-flow": "yahoo_api_cash_flow",
}


def _warn(name: str, stacklevel: int = 3) -> None:
    warnings.warn(
        f"{name} is deprecated and will be removed in stockdex {REMOVAL_VERSION}. "
        f"Use {REPLACEMENTS[name]} instead; the returned columns follow the "
        "Yahoo Finance API layout.",
        DeprecationWarning,
        stacklevel=stacklevel,
    )


def _combine(first: pd.DataFrame, second: pd.DataFrame, fields=None) -> pd.DataFrame:
    """Append rows of ``second`` that ``first`` does not have yet"""
    extra = second.loc[[i for i in second.index if i not in first.index]]
    if fields is not None:
        extra = extra.loc[[i for i in extra.index if i in fields]]
    if extra.empty:
        return first
    if first.empty:
        return extra
    return pd.concat([first, extra.set_axis(first.columns, axis=1)])


class YahooWebDeprecated(TickerBase):
    """``yahoo_web_*`` aliases that forward to the Yahoo Finance API methods"""

    def __init__(
        self,
        ticker: str = "",
        isin: str = "",
        security_type: VALID_SECURITY_TYPES = "stock",
    ) -> None:
        self.isin = isin
        self.ticker = ticker
        self.security_type = security_type

    def _deprecated(self, name: str) -> None:
        """Warn, then apply the old attribute's security type check"""
        _warn(name, stacklevel=4)
        if name in VALID_TYPES:
            check_security_type(
                security_type=self.security_type, valid_types=VALID_TYPES[name]
            )

    def _earnings_trend_part(self, *columns: str, prefix: str = "") -> pd.DataFrame:
        frame = self.yahoo_api_earnings_trend()
        keep = [
            column
            for column in frame.columns
            if column in ("period", "endDate", *columns)
            or (prefix and column.startswith(prefix))
        ]
        return frame[keep]

    def yahoo_web_financials_table(
        self, url: str, frequency: str = "annual"
    ) -> pd.DataFrame:
        """
        Deprecated: get a financial statement by its old Yahoo website URL

        Supported URLs end in ``/financials``, ``/balance-sheet`` or
        ``/cash-flow``. Any other URL raises ``ValueError``, because the
        website scraper that read other pages has been removed.
        """
        _warn("yahoo_web_financials_table")
        suffix = url.split("?")[0].rstrip("/").split("/")[-1]
        if suffix not in STATEMENT_URLS:
            raise ValueError(
                f"yahoo_web_financials_table only supports statement URLs ending "
                f"in {', '.join('/' + s for s in STATEMENT_URLS)}; got {url!r}. "
                "The Yahoo website scraper has been removed."
            )
        if frequency not in ("annual", "quarterly"):
            raise ValueError(
                f"frequency must be 'annual' or 'quarterly', got {frequency!r}"
            )
        return getattr(self, STATEMENT_URLS[suffix])(frequency=frequency)

    @property
    def yahoo_web_income_stmt(self) -> pd.DataFrame:
        self._deprecated("yahoo_web_income_stmt")
        return self.yahoo_api_income_statement()

    @property
    def yahoo_web_balance_sheet(self) -> pd.DataFrame:
        self._deprecated("yahoo_web_balance_sheet")
        return self.yahoo_api_balance_sheet()

    @property
    def yahoo_web_cashflow(self) -> pd.DataFrame:
        self._deprecated("yahoo_web_cashflow")
        return self.yahoo_api_cash_flow()

    @property
    def yahoo_web_calls(self) -> pd.DataFrame:
        self._deprecated("yahoo_web_calls")
        return self.yahoo_api_options_chain(option_type="calls")

    @property
    def yahoo_web_puts(self) -> pd.DataFrame:
        self._deprecated("yahoo_web_puts")
        return self.yahoo_api_options_chain(option_type="puts")

    @property
    def yahoo_web_description(self) -> str:
        self._deprecated("yahoo_web_description")
        profile = self.yahoo_api_profile()
        if "longBusinessSummary" not in profile.index:
            return ""
        return str(profile.loc["longBusinessSummary"].iloc[0])

    @property
    def yahoo_web_key_executives(self) -> pd.DataFrame:
        self._deprecated("yahoo_web_key_executives")
        return self.yahoo_api_officers()

    @property
    def yahoo_web_corporate_governance(self) -> str:
        self._deprecated("yahoo_web_corporate_governance")
        profile = self.yahoo_api_profile()
        rows = [index for index in profile.index if str(index).endswith("Risk")]
        return "\n".join(f"{row}: {profile.loc[row].iloc[0]}" for row in rows)

    @property
    def yahoo_web_major_holders(self) -> pd.DataFrame:
        self._deprecated("yahoo_web_major_holders")
        return self.yahoo_api_major_holders()

    @property
    def yahoo_web_top_institutional_holders(self) -> pd.DataFrame:
        self._deprecated("yahoo_web_top_institutional_holders")
        return self.yahoo_api_institutional_holders()

    @property
    def yahoo_web_top_mutual_fund_holders(self) -> pd.DataFrame:
        self._deprecated("yahoo_web_top_mutual_fund_holders")
        return self.yahoo_api_fund_holders()

    @property
    def yahoo_web_summary(self) -> pd.DataFrame:
        """Price fields (e.g. regularMarketPrice, marketState) then summary detail"""
        self._deprecated("yahoo_web_summary")
        return _combine(self.yahoo_api_market_price(), self.yahoo_api_summary_detail())

    @property
    def yahoo_web_valuation_measures(self) -> pd.DataFrame:
        """Quarterly history plus the latest trailing snapshot as ``Current``"""
        self._deprecated("yahoo_web_valuation_measures")
        history = self.yahoo_api_valuation_measures()
        trailing = self.yahoo_api_valuation_measures(frequency="trailing")
        if trailing.empty:
            return history
        current = trailing.sort_index().iloc[[-1]]
        current = current.set_axis(
            [str(c).replace("trailing", "quarterly", 1) for c in current.columns],
            axis=1,
        ).set_axis(["Current"])
        return pd.concat([history, current])

    @property
    def yahoo_web_financial_highlights(self) -> pd.DataFrame:
        """Financial data plus fiscal year end and most recent quarter dates"""
        self._deprecated("yahoo_web_financial_highlights")
        return _combine(
            self.yahoo_api_financial_data(),
            self.yahoo_api_key_statistics(),
            FINANCIAL_HIGHLIGHT_DATES,
        )

    @property
    def yahoo_web_trading_information(self) -> pd.DataFrame:
        """Key statistics plus 52-week range, averages and dividend fields"""
        self._deprecated("yahoo_web_trading_information")
        return _combine(
            self.yahoo_api_key_statistics(),
            self.yahoo_api_summary_detail(),
            TRADING_SUMMARY_FIELDS,
        )

    @property
    def yahoo_web_full_name(self) -> str:
        self._deprecated("yahoo_web_full_name")
        # The scraper stripped punctuation, e.g. "Apple Inc." -> "Apple Inc"
        name = self.yahoo_api_company_name()
        match = re.findall(r"[\w\s]+", name)
        return match[0].strip() if match else name

    @property
    def yahoo_web_earnings_estimate(self) -> pd.DataFrame:
        self._deprecated("yahoo_web_earnings_estimate")
        return self._earnings_trend_part(prefix="earningsEstimate_")

    @property
    def yahoo_web_revenue_estimate(self) -> pd.DataFrame:
        self._deprecated("yahoo_web_revenue_estimate")
        return self._earnings_trend_part(prefix="revenueEstimate_")

    @property
    def yahoo_web_earnings_history(self) -> pd.DataFrame:
        self._deprecated("yahoo_web_earnings_history")
        return self.yahoo_api_earnings_history()

    @property
    def yahoo_web_eps_trend(self) -> pd.DataFrame:
        self._deprecated("yahoo_web_eps_trend")
        return self._earnings_trend_part(prefix="epsTrend_")

    @property
    def yahoo_web_eps_revisions(self) -> pd.DataFrame:
        self._deprecated("yahoo_web_eps_revisions")
        return self._earnings_trend_part(prefix="epsRevisions_")

    @property
    def yahoo_web_growth_estimates(self) -> pd.DataFrame:
        """The company's growth estimates. The S&P 500 benchmark is not available."""
        self._deprecated("yahoo_web_growth_estimates")
        return self._earnings_trend_part("growth")
