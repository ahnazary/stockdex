"""Offline tests for dividends source/fallback, splits, options and quotes."""

import pandas as pd
import pytest

from stockdex.claude_adapter import StockdexAdapter
from stockdex.exceptions import RateLimitError
from tests.claude.conftest import FakeTicker


@pytest.fixture
def provider():
    return FakeTicker("AAPL")


@pytest.fixture
def adapter(provider):
    return StockdexAdapter(ticker_factory=lambda **kw: provider)


def test_dividends_default_still_digrin(adapter):
    result = adapter.get_dividends("AAPL")
    assert result["ok"] and result["source"] == "digrin"
    assert result["parameters"]["source"] == "digrin"


def test_dividends_from_yahoo(adapter):
    result = adapter.get_dividends("AAPL", source="yahoo")
    assert result["source"] == "yahoo_api"
    assert result["records"][0] == {
        "ex_dividend_date": "2026-01-02",
        "amount": 0.26,
        "currency": "USD",
    }


def test_dividends_auto_falls_back_on_rate_limit(monkeypatch):
    class Limited(FakeTicker):
        @property
        def digrin_dividend(self):
            raise RateLimitError("https://www.digrin.com/x", "60")

    adapter = StockdexAdapter(ticker_factory=lambda **kw: Limited("AAPL"))
    result = adapter.get_dividends("AAPL", source="auto")
    assert result["ok"] and result["source"] == "yahoo_api"
    assert any("Yahoo Finance" in w for w in result["warnings"])

    strict = adapter.get_dividends("AAPL", source="digrin")
    assert strict["error"]["code"] == "rate_limited"


def test_dividends_rejects_unknown_source(adapter):
    assert (
        adapter.get_dividends("AAPL", source="nasdaq")["error"]["code"]
        == "invalid_input"
    )


def test_splits(adapter):
    result = adapter.get_splits("AAPL")
    assert result["records"] == [
        {
            "split_date": "2020-08-31",
            "numerator": 4.0,
            "denominator": 1.0,
            "splitRatio": "4:1",
        }
    ]


def test_options_chain_selects_public_columns(adapter, provider):
    result = adapter.get_options_chain(
        "AAPL", expiration="2026-11-20", option_type="puts"
    )
    assert result["ok"]
    assert provider.calls[-1] == {"expiration": "2026-11-20", "option_type": "puts"}
    assert result["columns"] == ["optionType", "strike", "bid", "expiration"]
    assert result["records"][0]["optionType"] == "put"
    assert result["records"][0]["expiration"] == "2026-11-20T00:00:00+00:00"


@pytest.mark.parametrize(
    "kwargs",
    [
        {"expiration": "2026-02-30"},
        {"expiration": "next friday"},
        {"option_type": "straddle"},
    ],
)
def test_options_chain_validation(adapter, kwargs):
    assert (
        adapter.get_options_chain("AAPL", **kwargs)["error"]["code"] == "invalid_input"
    )


def test_quotes_normalise_and_dedupe():
    adapter = StockdexAdapter(ticker_factory=FakeTicker)
    result = adapter.get_quotes(["aapl", "MSFT", "AAPL"])
    assert result["ok"] and result["ticker"] is None
    assert result["parameters"]["symbols"] == ["AAPL", "MSFT"]
    assert result["columns"] == ["symbol", "currency", "regularMarketPrice"]
    assert result["records"][1] == {
        "symbol": "MSFT",
        "currency": "USD",
        "regularMarketPrice": 530.14,
    }


@pytest.mark.parametrize(
    "symbols",
    [
        [],
        ["AAPL"] * 0,
        [f"S{i}" for i in range(21)],
        ["https://x"],
        [None],
        "AAPL;MSFT",
    ],
)
def test_quotes_validation(symbols):
    adapter = StockdexAdapter(ticker_factory=FakeTicker)
    assert adapter.get_quotes(symbols)["error"]["code"] == "invalid_input"


def test_quotes_single_string_accepted():
    adapter = StockdexAdapter(ticker_factory=FakeTicker)
    assert adapter.get_quotes("aapl")["parameters"]["symbols"] == ["AAPL"]


def test_quotes_empty_is_no_data():
    class Empty(FakeTicker):
        @staticmethod
        def yahoo_api_quotes(symbols):
            return pd.DataFrame()

    adapter = StockdexAdapter(ticker_factory=Empty)
    assert adapter.get_quotes(["ZZZZ"])["error"]["code"] == "no_data"
