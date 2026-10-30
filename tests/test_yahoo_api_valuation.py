"""Offline tests for Yahoo valuation measures from the fundamentals timeseries."""

from datetime import datetime
from types import SimpleNamespace

import pytest

from stockdex import Ticker, config

PAYLOAD = {
    "timeseries": {
        "result": [
            {
                "meta": {"type": ["quarterlyPeRatio"]},
                "quarterlyPeRatio": [
                    {
                        "asOfDate": "2026-06-30",
                        "reportedValue": {"raw": 35.03, "fmt": "35.03"},
                    },
                    {
                        "asOfDate": "2026-03-31",
                        "reportedValue": {"raw": 33.1, "fmt": "33.10"},
                    },
                ],
            },
            {
                "meta": {"type": ["quarterlyMarketCap"]},
                "quarterlyMarketCap": [
                    {
                        "asOfDate": "2026-03-31",
                        "reportedValue": {"raw": 3.2e12, "fmt": "3.2T"},
                    },
                    {
                        "asOfDate": "2026-06-30",
                        "reportedValue": {"raw": 3.5e12, "fmt": "3.5T"},
                    },
                ],
            },
            # A requested key that Yahoo has no data for.
            {"meta": {"type": ["quarterlyPegRatio"]}},
        ]
    }
}


@pytest.fixture
def ticker(monkeypatch):
    ticker = Ticker("AAPL")
    ticker.urls = []

    def response(url):
        ticker.urls.append(url)
        return SimpleNamespace(json=lambda: PAYLOAD)

    monkeypatch.setattr(ticker, "get_response", response)
    return ticker


def test_valuation_measures_raw(ticker):
    frame = ticker.yahoo_api_valuation_measures(format="raw")
    assert list(frame.index) == ["2026-03-31", "2026-06-30"]
    assert frame.loc["2026-06-30", "quarterlyPeRatio"] == 35.03
    assert frame.loc["2026-03-31", "quarterlyMarketCap"] == 3.2e12
    assert "quarterlyPegRatio" not in frame


def test_requests_every_valuation_key_with_frequency_prefix(ticker):
    ticker.yahoo_api_valuation_measures(
        frequency="trailing",
        period1=datetime(2025, 1, 1),
        period2=datetime(2026, 1, 1),
    )
    url = ticker.urls[0]
    for column in config.VALUATION_COLUMNS:
        assert f"trailing{column}" in url
    assert "quarterly" not in url


def test_formatted_values(ticker):
    frame = ticker.yahoo_api_valuation_measures()
    assert frame.loc["2026-06-30", "quarterlyMarketCap"] == "3.5T"
