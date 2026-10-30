"""
Deprecated ``yahoo_web_*`` attributes

The Yahoo Finance website scraper was removed in 1.5.0 because every dataset
it scraped is available from the Yahoo Finance API. The old attribute names
still work: each one emits a ``DeprecationWarning`` and returns the data from
its ``yahoo_api_*`` replacement. The column layout of the returned frames
follows the API method, not the old scraped table.

These attributes will be removed in 2.0.
"""

import re
import warnings

import pandas as pd

from stockdex.config import VALID_SECURITY_TYPES
from stockdex.ticker_base import TickerBase

REMOVAL_VERSION = "2.0"

# Old attribute -> replacement shown in the warning
REPLACEMENTS = {
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
    "yahoo_web_summary": "yahoo_api_summary_detail()",
    "yahoo_web_valuation_measures": "yahoo_api_valuation_measures()",
    "yahoo_web_financial_highlights": "yahoo_api_financial_data()",
    "yahoo_web_trading_information": "yahoo_api_key_statistics()",
    "yahoo_web_full_name": "yahoo_api_company_name()",
    "yahoo_web_earnings_estimate": "yahoo_api_earnings_trend() (earningsEstimate_*)",
    "yahoo_web_revenue_estimate": "yahoo_api_earnings_trend() (revenueEstimate_*)",
    "yahoo_web_earnings_history": "yahoo_api_earnings_history()",
    "yahoo_web_eps_trend": "yahoo_api_earnings_trend() (epsTrend_*)",
    "yahoo_web_eps_revisions": "yahoo_api_earnings_trend() (epsRevisions_*)",
    "yahoo_web_growth_estimates": "yahoo_api_earnings_trend() (growth)",
}


def _warn(name: str) -> None:
    warnings.warn(
        f"{name} is deprecated and will be removed in stockdex {REMOVAL_VERSION}. "
        f"Use {REPLACEMENTS[name]} instead; the returned columns follow the "
        "Yahoo Finance API layout.",
        DeprecationWarning,
        stacklevel=3,
    )


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

    def _earnings_trend_part(self, *columns: str, prefix: str = "") -> pd.DataFrame:
        frame = self.yahoo_api_earnings_trend()
        keep = [
            column
            for column in frame.columns
            if column in ("period", "endDate", *columns)
            or (prefix and column.startswith(prefix))
        ]
        return frame[keep]

    @property
    def yahoo_web_income_stmt(self) -> pd.DataFrame:
        _warn("yahoo_web_income_stmt")
        return self.yahoo_api_income_statement()

    @property
    def yahoo_web_balance_sheet(self) -> pd.DataFrame:
        _warn("yahoo_web_balance_sheet")
        return self.yahoo_api_balance_sheet()

    @property
    def yahoo_web_cashflow(self) -> pd.DataFrame:
        _warn("yahoo_web_cashflow")
        return self.yahoo_api_cash_flow()

    @property
    def yahoo_web_calls(self) -> pd.DataFrame:
        _warn("yahoo_web_calls")
        return self.yahoo_api_options_chain(option_type="calls")

    @property
    def yahoo_web_puts(self) -> pd.DataFrame:
        _warn("yahoo_web_puts")
        return self.yahoo_api_options_chain(option_type="puts")

    @property
    def yahoo_web_description(self) -> str:
        _warn("yahoo_web_description")
        profile = self.yahoo_api_profile()
        if "longBusinessSummary" not in profile.index:
            return ""
        return str(profile.loc["longBusinessSummary"].iloc[0])

    @property
    def yahoo_web_key_executives(self) -> pd.DataFrame:
        _warn("yahoo_web_key_executives")
        return self.yahoo_api_officers()

    @property
    def yahoo_web_corporate_governance(self) -> str:
        _warn("yahoo_web_corporate_governance")
        profile = self.yahoo_api_profile()
        rows = [index for index in profile.index if str(index).endswith("Risk")]
        return "\n".join(f"{row}: {profile.loc[row].iloc[0]}" for row in rows)

    @property
    def yahoo_web_major_holders(self) -> pd.DataFrame:
        _warn("yahoo_web_major_holders")
        return self.yahoo_api_major_holders()

    @property
    def yahoo_web_top_institutional_holders(self) -> pd.DataFrame:
        _warn("yahoo_web_top_institutional_holders")
        return self.yahoo_api_institutional_holders()

    @property
    def yahoo_web_top_mutual_fund_holders(self) -> pd.DataFrame:
        _warn("yahoo_web_top_mutual_fund_holders")
        return self.yahoo_api_fund_holders()

    @property
    def yahoo_web_summary(self) -> pd.DataFrame:
        _warn("yahoo_web_summary")
        return self.yahoo_api_summary_detail()

    @property
    def yahoo_web_valuation_measures(self) -> pd.DataFrame:
        _warn("yahoo_web_valuation_measures")
        return self.yahoo_api_valuation_measures()

    @property
    def yahoo_web_financial_highlights(self) -> pd.DataFrame:
        _warn("yahoo_web_financial_highlights")
        return self.yahoo_api_financial_data()

    @property
    def yahoo_web_trading_information(self) -> pd.DataFrame:
        _warn("yahoo_web_trading_information")
        return self.yahoo_api_key_statistics()

    @property
    def yahoo_web_full_name(self) -> str:
        _warn("yahoo_web_full_name")
        # The scraper stripped punctuation, e.g. "Apple Inc." -> "Apple Inc"
        name = self.yahoo_api_company_name()
        match = re.findall(r"[\w\s]+", name)
        return match[0].strip() if match else name

    @property
    def yahoo_web_earnings_estimate(self) -> pd.DataFrame:
        _warn("yahoo_web_earnings_estimate")
        return self._earnings_trend_part(prefix="earningsEstimate_")

    @property
    def yahoo_web_revenue_estimate(self) -> pd.DataFrame:
        _warn("yahoo_web_revenue_estimate")
        return self._earnings_trend_part(prefix="revenueEstimate_")

    @property
    def yahoo_web_earnings_history(self) -> pd.DataFrame:
        _warn("yahoo_web_earnings_history")
        return self.yahoo_api_earnings_history()

    @property
    def yahoo_web_eps_trend(self) -> pd.DataFrame:
        _warn("yahoo_web_eps_trend")
        return self._earnings_trend_part(prefix="epsTrend_")

    @property
    def yahoo_web_eps_revisions(self) -> pd.DataFrame:
        _warn("yahoo_web_eps_revisions")
        return self._earnings_trend_part(prefix="epsRevisions_")

    @property
    def yahoo_web_growth_estimates(self) -> pd.DataFrame:
        _warn("yahoo_web_growth_estimates")
        return self._earnings_trend_part("growth")
