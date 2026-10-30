"""Offline tests for Yahoo chart corporate-action events."""

from types import SimpleNamespace

import pandas as pd
import pytest

from stockdex import Ticker

CHART = {
    "chart": {
        "result": [
            {
                "meta": {"currency": "USD"},
                "events": {
                    "dividends": {
                        "1732890600": {"amount": 0.485, "date": 1732890600},
                        "1700000000": {"amount": 0.46, "date": 1700000000},
                    },
                    "splits": {
                        "1598880600": {
                            "date": 1598880600,
                            "numerator": 4.0,
                            "denominator": 1.0,
                            "splitRatio": "4:1",
                        }
                    },
                    "capitalGains": {
                        "1702900000": {
                            "amount": 1.25,
                            "date": 1702900000,
                            "currency": "EUR",
                        }
                    },
                },
            }
        ]
    }
}


@pytest.fixture
def ticker(monkeypatch):
    ticker = Ticker("KO")
    urls = []

    def response(url):
        urls.append(url)
        return SimpleNamespace(json=lambda: CHART)

    monkeypatch.setattr(ticker, "get_response", response)
    ticker.urls = urls
    return ticker


def test_dividends_sorted_with_currency(ticker):
    frame = ticker.yahoo_api_dividends(range="5y")
    assert list(frame["amount"]) == [0.46, 0.485]
    assert set(frame["currency"]) == {"USD"}
    assert frame.index.name == "date"
    assert str(frame.index.tz) == "UTC"
    assert "range=5y" in ticker.urls[0]
    assert "events=div,splits,capitalGains" in ticker.urls[0]


def test_splits(ticker):
    frame = ticker.yahoo_api_splits()
    assert frame.iloc[0]["splitRatio"] == "4:1"
    assert frame.iloc[0]["numerator"] == 4.0
    assert "currency" not in frame
    assert frame.index[0] == pd.Timestamp("2020-08-31 13:30:00", tz="UTC")


def test_capital_gains_keep_event_currency(ticker):
    frame = ticker.yahoo_api_capital_gains()
    assert frame.iloc[0]["amount"] == 1.25
    assert frame.iloc[0]["currency"] == "EUR"


def test_no_events_returns_empty_frame(monkeypatch):
    ticker = Ticker("BRK-A")
    empty = {"chart": {"result": [{"meta": {"currency": "USD"}}]}}
    monkeypatch.setattr(
        ticker, "get_response", lambda url: SimpleNamespace(json=lambda: empty)
    )
    assert ticker.yahoo_api_dividends().empty
    assert ticker.yahoo_api_splits().empty
