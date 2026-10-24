"""Offline isolation for the local Claude integration suite only."""

from datetime import datetime, timezone

import pandas as pd
import pytest
from curl_cffi import requests

from stockdex.claude_adapter import StockdexAdapter


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
