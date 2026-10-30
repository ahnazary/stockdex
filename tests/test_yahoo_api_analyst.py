"""Offline tests for the Yahoo quoteSummary analyst and earnings methods."""

from types import SimpleNamespace

import pandas as pd
import pytest

from stockdex import Ticker

MODULES = {
    "earningsHistory": {
        "maxAge": 86400,
        "history": [
            {
                "maxAge": 1,
                "epsActual": {"raw": 2.84, "fmt": "2.84"},
                "epsEstimate": {"raw": 2.67, "fmt": "2.67"},
                "quarter": {"raw": 1767139200, "fmt": "2025-12-31"},
                "period": "-3q",
                "currency": "USD",
            },
            {
                "maxAge": 1,
                "epsActual": {"raw": 1.85, "fmt": "1.85"},
                "epsEstimate": {"raw": 1.77, "fmt": "1.77"},
                "quarter": {"raw": 1759190400, "fmt": "2025-09-30"},
                "period": "-4q",
                "currency": "USD",
            },
        ],
    },
    "earningsTrend": {
        "trend": [
            {
                "maxAge": 1,
                "period": "0q",
                "endDate": "2026-09-30",
                "growth": {"raw": 0.0717, "fmt": "7.17%"},
                "earningsEstimate": {
                    "avg": {"raw": 1.98, "fmt": "1.98"},
                    "numberOfAnalysts": {"raw": 27, "fmt": "27"},
                },
                "epsTrend": {"current": {"raw": 1.98}, "30daysAgo": {"raw": 1.95}},
            }
        ]
    },
    "recommendationTrend": {
        "trend": [{"period": "0m", "strongBuy": 6, "buy": 18, "hold": 13, "sell": 3}]
    },
    "upgradeDowngradeHistory": {
        "history": [
            {"epochGradeDate": 1700000000, "firm": "Old", "action": "up"},
            {"epochGradeDate": 1792519228, "firm": "New", "action": "down"},
        ]
    },
}


@pytest.fixture
def ticker(monkeypatch):
    ticker = Ticker("AAPL")

    def response(url):
        requested = url.split("modules=")[1].split("&")[0].split(",")
        result = {m: MODULES[m] for m in requested if m in MODULES}
        payload = {"quoteSummary": {"result": [result], "error": None}}
        return SimpleNamespace(json=lambda: payload)

    monkeypatch.setattr(ticker, "get_response", response)
    return ticker


def test_earnings_history_sorted_oldest_first(ticker):
    frame = ticker.yahoo_api_earnings_history()
    assert list(frame["period"]) == ["-4q", "-3q"]
    assert frame.loc[0, "quarter"] == pd.Timestamp("2025-09-30", tz="UTC")
    assert frame.loc[1, "epsActual"] == 2.84
    assert "maxAge" not in frame


def test_earnings_trend_flattens_nested_estimates(ticker):
    frame = ticker.yahoo_api_earnings_trend()
    row = frame.iloc[0]
    assert row["period"] == "0q"
    assert row["growth"] == 0.0717
    assert row["earningsEstimate_avg"] == 1.98
    assert row["earningsEstimate_numberOfAnalysts"] == 27
    assert row["epsTrend_30daysAgo"] == 1.95
    assert "maxAge" not in frame


def test_recommendation_trend(ticker):
    frame = ticker.yahoo_api_recommendation_trend()
    assert frame.loc[0, "strongBuy"] == 6
    assert frame.loc[0, "period"] == "0m"


def test_upgrades_downgrades_newest_first(ticker):
    frame = ticker.yahoo_api_upgrades_downgrades()
    assert list(frame["firm"]) == ["New", "Old"]
    assert frame.loc[0, "epochGradeDate"] == pd.Timestamp(
        1792519228, unit="s", tz="UTC"
    )


def test_missing_modules_give_empty_frames(monkeypatch):
    ticker = Ticker("SPY")
    empty = {"quoteSummary": {"result": [{}], "error": None}}
    monkeypatch.setattr(
        ticker, "get_response", lambda url: SimpleNamespace(json=lambda: empty)
    )
    for name in (
        "yahoo_api_earnings_history",
        "yahoo_api_earnings_trend",
        "yahoo_api_recommendation_trend",
        "yahoo_api_upgrades_downgrades",
    ):
        assert getattr(ticker, name)().empty, name
