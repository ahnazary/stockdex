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
