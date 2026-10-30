"""Offline tests for the Yahoo quoteSummary company and market-data methods."""

from types import SimpleNamespace

import pandas as pd
import pytest

from stockdex import Ticker

MODULES = {
    "assetProfile": {
        "maxAge": 86400,
        "city": "Cupertino",
        "sector": "Technology",
        "fullTimeEmployees": 166000,
        "governanceEpochDate": 1793145600,
        "companyOfficers": [
            {
                "maxAge": 1,
                "name": "Mr. Timothy D. Cook",
                "title": "CEO",
                "totalPay": {"raw": 16759518, "fmt": "16.76M"},
                "exercisedValue": {},
            }
        ],
    },
    "price": {
        "maxAge": 1,
        "regularMarketPrice": {"raw": 348.91, "fmt": "348.91"},
        "regularMarketTime": 1793304001,
        "currency": "USD",
        "marketState": "CLOSED",
    },
    "summaryDetail": {
        "maxAge": 1,
        "marketCap": {"raw": 5.09e12, "fmt": "5.09T"},
        "dividendYield": {"raw": 0.0031, "fmt": "0.31%"},
        "exDividendDate": {"raw": 1786320000, "fmt": "2026-08-10"},
    },
    "defaultKeyStatistics": {
        "maxAge": 1,
        "forwardPE": {"raw": 36.49, "fmt": "36.49"},
        "lastSplitDate": {"raw": 1598832000, "fmt": "2020-08-31"},
        "lastSplitFactor": "4:1",
    },
    "financialData": {
        "maxAge": 86400,
        "currentPrice": {"raw": 348.91, "fmt": "348.91"},
        "targetMeanPrice": {"raw": 332.39, "fmt": "332.39"},
        "recommendationKey": "buy",
    },
    "calendarEvents": {
        "maxAge": 1,
        "earnings": {
            "earningsDate": [
                {"raw": 1793649600, "fmt": "2026-11-02"},
                {"raw": 1794254400, "fmt": "2026-11-09"},
            ],
            "earningsCallDate": [{"raw": 1793656800, "fmt": "2026-11-02"}],
            "isEarningsDateEstimate": True,
            "earningsAverage": {"raw": 1.98, "fmt": "1.98"},
            "revenueAverage": {"raw": 113322287400, "fmt": "113.32B"},
        },
        "exDividendDate": {"raw": 1786320000, "fmt": "2026-08-10"},
        "dividendDate": {"raw": 1786579200, "fmt": "2026-08-13"},
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


def utc(text):
    return pd.Timestamp(text, tz="UTC")


def test_profile_excludes_nested_officers(ticker):
    frame = ticker.yahoo_api_profile()
    assert list(frame.columns) == ["AAPL"]
    assert frame.loc["city", "AAPL"] == "Cupertino"
    assert frame.loc["fullTimeEmployees", "AAPL"] == 166000
    assert frame.loc["governanceEpochDate", "AAPL"] == utc("2026-10-28")
    assert "companyOfficers" not in frame.index
    assert "maxAge" not in frame.index


def test_officers(ticker):
    frame = ticker.yahoo_api_officers()
    assert frame.loc[0, "name"] == "Mr. Timothy D. Cook"
    assert frame.loc[0, "totalPay"] == 16759518
    assert frame.loc[0, "exercisedValue"] is None
    assert "maxAge" not in frame


def test_market_price_converts_epoch(ticker):
    frame = ticker.yahoo_api_market_price()
    assert frame.loc["regularMarketPrice", "AAPL"] == 348.91
    assert frame.loc["regularMarketTime", "AAPL"] == pd.Timestamp(
        1793304001, unit="s", tz="UTC"
    )


def test_summary_detail_raw_and_fmt(ticker):
    raw = ticker.yahoo_api_summary_detail()
    assert raw.loc["marketCap", "AAPL"] == 5.09e12
    assert raw.loc["exDividendDate", "AAPL"] == utc("2026-08-10")
    fmt = ticker.yahoo_api_summary_detail(format="fmt")
    assert fmt.loc["marketCap", "AAPL"] == "5.09T"
    assert fmt.loc["exDividendDate", "AAPL"] == "2026-08-10"


def test_key_statistics(ticker):
    frame = ticker.yahoo_api_key_statistics()
    assert frame.loc["forwardPE", "AAPL"] == 36.49
    assert frame.loc["lastSplitDate", "AAPL"] == utc("2020-08-31")
    assert frame.loc["lastSplitFactor", "AAPL"] == "4:1"


def test_financial_data(ticker):
    frame = ticker.yahoo_api_financial_data()
    assert frame.loc["targetMeanPrice", "AAPL"] == 332.39
    assert frame.loc["recommendationKey", "AAPL"] == "buy"


def test_calendar_events_flattens_date_lists(ticker):
    frame = ticker.yahoo_api_calendar_events()
    values = frame["AAPL"]
    assert values["earningsDate_1"] == utc("2026-11-02 20:00")
    assert values["earningsDate_2"] == utc("2026-11-09 20:00")
    assert values["earningsCallDate"] == utc("2026-11-02 22:00")
    assert values["isEarningsDateEstimate"] is True
    assert values["revenueAverage"] == 113322287400
    assert values["dividendDate"] == utc("2026-08-13")


def test_missing_module_gives_empty_frame(monkeypatch):
    ticker = Ticker("ZZZZ")
    empty = {"quoteSummary": {"result": [{}], "error": None}}
    monkeypatch.setattr(
        ticker, "get_response", lambda url: SimpleNamespace(json=lambda: empty)
    )
    assert ticker.yahoo_api_profile().empty
    assert ticker.yahoo_api_officers().empty
    assert ticker.yahoo_api_calendar_events().empty
