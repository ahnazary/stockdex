"""Offline isolation for the local Claude integration suite only."""

from datetime import datetime, timezone

import pandas as pd
import pytest
from curl_cffi import requests

from stockdex.claude_adapter import StockdexAdapter

# Every MCP tool the server must expose. Add new tools here and in claude_mcp.
EXPECTED_TOOLS = {
    "get_prices",
    "get_financial_statement",
    "get_dividends",
    "search_ticker",
    "get_company_profile",
    "get_key_statistics",
    "get_valuation_history",
    "get_analyst_estimates",
    "get_earnings_calendar",
    "get_holders",
    "get_sec_filings",
    "get_fund_holdings",
    "get_fund_profile",
    "get_splits",
    "get_options_chain",
    "get_quotes",
}


@pytest.fixture(autouse=True)
def deny_network(monkeypatch):
    def denied(*args, **kwargs):
        pytest.fail(
            "Financial provider networking is forbidden in the local Claude tests"
        )

    # curl_cffi bypasses Python sockets; block its real network entry point.
    monkeypatch.setattr(requests.Session, "request", denied)


class FakeTicker:
    def __init__(self, ticker):
        self.ticker = ticker
        self.calls = []

    def yahoo_api_price(self, **kwargs):
        self.calls.append(kwargs)
        return pd.DataFrame(
            {
                "timestamp": pd.to_datetime(["2026-01-01", "2026-01-02"]),
                "open": [10, 11],
                "high": [12, 13],
                "low": [9, 10],
                "close": [11, float("nan")],
                "volume": [100, 200],
                "currency": ["USD", "USD"],
            }
        )

    def yahoo_api_income_statement(self, **kwargs):
        self.calls.append(kwargs)
        return pd.DataFrame(
            {
                "annualTotalRevenue": [1000, 2000],
                "annualNetIncome": [10, float("inf")],
            },
            index=["2024-12-31", "2025-12-31"],
        )

    yahoo_api_cash_flow = yahoo_api_income_statement
    yahoo_api_balance_sheet = yahoo_api_income_statement

    @staticmethod
    def yahoo_api_search(query, limit=10):
        return pd.DataFrame(
            {
                "symbol": ["BMW.DE", "BMWKY"],
                "shortname": ["BMW", "BMW ADR"],
                "quoteType": ["EQUITY", "EQUITY"],
                "exchange": ["GER", "PNK"],
            }
        ).head(limit)

    def yahoo_api_profile(self):
        return pd.DataFrame(
            {self.ticker: ["Cupertino", "Technology"]}, index=["city", "sector"]
        )

    def yahoo_api_summary_detail(self):
        return pd.DataFrame({self.ticker: [5.09e12, 1.07]}, index=["marketCap", "beta"])

    def yahoo_api_valuation_measures(self, frequency="quarterly", format="raw"):
        return pd.DataFrame(
            {
                f"{frequency}MarketCap": [3.2e12, 3.5e12],
                f"{frequency}PeRatio": [33.1, 35.0],
            },
            index=["2026-03-31", "2026-06-30"],
        )

    def yahoo_api_earnings_trend(self):
        return pd.DataFrame(
            {"period": ["0q", "+1q"], "earningsEstimate_avg": [1.98, 2.1]}
        )

    def yahoo_api_calendar_events(self):
        return pd.DataFrame(
            {self.ticker: [pd.Timestamp("2026-11-02 20:00", tz="UTC"), 1.98]},
            index=["earningsDate", "earningsAverage"],
        )

    def yahoo_api_institutional_holders(self):
        return pd.DataFrame({"organization": ["Blackrock Inc."], "pctHeld": [0.0797]})

    def yahoo_api_sec_filings(self):
        return pd.DataFrame(
            {
                "date": ["2026-09-01"],
                "type": ["8-K"],
                "exhibits": [[{"type": "8-K", "url": "https://example.com/x"}]],
            }
        )

    def yahoo_api_fund_top_holdings(self):
        return pd.DataFrame(
            {"symbol": ["NVDA", "AAPL"], "holdingPercent": [0.0836, 0.0735]}
        )

    def yahoo_api_fund_performance(self):
        return pd.DataFrame(
            {"fund": [0.1268, 0.1772], "category": [0.0514, 0.1554]},
            index=["ytd", "2025"],
        )

    def yahoo_api_dividends(self, range="max"):
        return pd.DataFrame(
            {"amount": [0.25, 0.26], "currency": ["USD", "USD"]},
            index=pd.DatetimeIndex(["2025-10-02", "2026-01-02"], tz="UTC", name="date"),
        )

    def yahoo_api_splits(self, range="max"):
        return pd.DataFrame(
            {"numerator": [4.0], "denominator": [1.0], "splitRatio": ["4:1"]},
            index=pd.DatetimeIndex(["2020-08-31"], tz="UTC", name="date"),
        )

    def yahoo_api_options_chain(self, expiration=None, option_type="both"):
        self.calls.append({"expiration": expiration, "option_type": option_type})
        kinds = ["call", "put"] if option_type == "both" else [option_type[:-1]]
        return pd.DataFrame(
            {
                "optionType": kinds,
                "strike": [350.0] * len(kinds),
                "bid": [9.5] * len(kinds),
                "expiration": [pd.Timestamp("2026-11-20", tz="UTC")] * len(kinds),
                "internalField": ["x"] * len(kinds),
            }
        )

    @staticmethod
    def yahoo_api_quotes(symbols):
        return pd.DataFrame(
            {
                "regularMarketPrice": [348.91, 530.14][: len(symbols)],
                "currency": ["USD", "USD"][: len(symbols)],
                "language": ["en-US", "en-US"][: len(symbols)],
            },
            index=pd.Index(symbols, name="symbol"),
        )

    @property
    def digrin_dividend(self):
        return pd.DataFrame(
            {
                "Ex-dividend date": ["2025-01-02", "2026-01-02"],
                "Payable date": ["-", "2026-01-10"],
                "Dividend amount (change)": ["—", "0.2600 USD (4%)"],
            }
        )


@pytest.fixture
def provider():
    return FakeTicker("AAPL")


@pytest.fixture
def adapter(provider):
    return StockdexAdapter(
        ticker_factory=lambda **kwargs: provider,
        clock=lambda: datetime(2026, 10, 3, tzinfo=timezone.utc),
    )
