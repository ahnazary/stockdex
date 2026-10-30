"""Offline tests for the adapter's ticker search operation."""

import pytest

from stockdex.claude_adapter import StockdexAdapter
from tests.claude.conftest import FakeTicker


@pytest.fixture
def adapter():
    return StockdexAdapter(ticker_factory=FakeTicker)


def test_search_returns_matches(adapter):
    result = adapter.search("  bayerische   motoren ", limit=1)
    assert result["ok"]
    assert result["operation"] == "search"
    assert result["ticker"] is None
    assert result["parameters"] == {"query": "bayerische motoren", "limit": 1}
    assert result["records"] == [
        {
            "symbol": "BMW.DE",
            "shortname": "BMW",
            "quoteType": "EQUITY",
            "exchange": "GER",
        }
    ]


@pytest.mark.parametrize(
    "query, limit",
    [
        ("https://evil.example", 10),
        ("", 10),
        ("   ", 10),
        ("a" * 65, 10),
        ("apple\n", 10),
        ("apple;rm -rf /", 10),
        (None, 10),
        ("apple", 0),
        ("apple", 26),
        ("apple", "5"),
    ],
)
def test_search_rejects_bad_input(adapter, query, limit):
    result = adapter.search(query, limit=limit)
    assert result["error"]["code"] == "invalid_input"


@pytest.mark.parametrize(
    "query", ["Apple", "BRK-B", "Procter & Gamble", "^GSPC", "L'Oreal"]
)
def test_search_accepts_names_and_symbols(adapter, query):
    assert adapter.search(query)["ok"]


def test_search_no_matches_is_no_data():
    class Empty(FakeTicker):
        @staticmethod
        def yahoo_api_search(query, limit=10):
            import pandas as pd

            return pd.DataFrame(columns=["symbol"])

    result = StockdexAdapter(ticker_factory=Empty).search("zzzqqq")
    assert result["error"]["code"] == "no_data"
