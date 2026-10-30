"""Offline tests for the Yahoo quoteSummary ownership, insider and filings methods."""

from types import SimpleNamespace

import pandas as pd
import pytest

from stockdex import Ticker

HOLDER = {
    "maxAge": 1,
    "reportDate": {"raw": 1782777600, "fmt": "2026-06-30"},
    "organization": "Blackrock Inc.",
    "pctHeld": {"raw": 0.0797, "fmt": "7.97%"},
    "position": {"raw": 1162996939, "fmt": "1.16B"},
}

MODULES = {
    "institutionOwnership": {"ownershipList": [HOLDER]},
    "fundOwnership": {"ownershipList": [{**HOLDER, "organization": "Vanguard"}]},
    "majorHoldersBreakdown": {
        "maxAge": 1,
        "insidersPercentHeld": 0.0165,
        "institutionsCount": 7715,
    },
    "insiderHolders": {
        "holders": [
            {
                "maxAge": 1,
                "name": "COOK TIMOTHY D",
                "relation": "Officer and Director",
                "latestTransDate": {"raw": 1790899200, "fmt": "2026-10-02"},
                "positionDirect": {"raw": 3237840, "fmt": "3.24M"},
            }
        ]
    },
    "insiderTransactions": {
        "transactions": [
            {
                "filerName": "OLD",
                "startDate": {"raw": 1700000000},
                "shares": {"raw": 1},
            },
            {
                "filerName": "NEW",
                "startDate": {"raw": 1792454400},
                "shares": {"raw": 2399},
            },
        ]
    },
    "netSharePurchaseActivity": {
        "maxAge": 1,
        "period": "6m",
        "buyInfoCount": {"raw": 12, "fmt": "12"},
        "netInfoShares": {"raw": 257744, "fmt": "257.74k"},
    },
    "secFilings": {
        "filings": [
            {"date": "2025-01-01", "epochDate": 1735689600, "type": "10-K"},
            {
                "date": "2026-09-01",
                "epochDate": 1788220800,
                "type": "8-K/A",
                "exhibits": [{"type": "8-K/A", "url": "https://example.com/x.htm"}],
            },
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


@pytest.mark.parametrize(
    "method, organization",
    [
        ("yahoo_api_institutional_holders", "Blackrock Inc."),
        ("yahoo_api_fund_holders", "Vanguard"),
    ],
)
def test_holder_tables(ticker, method, organization):
    frame = getattr(ticker, method)()
    assert frame.loc[0, "organization"] == organization
    assert frame.loc[0, "pctHeld"] == 0.0797
    assert frame.loc[0, "position"] == 1162996939
    assert frame.loc[0, "reportDate"] == pd.Timestamp("2026-06-30", tz="UTC")
    assert "maxAge" not in frame


def test_major_holders(ticker):
    frame = ticker.yahoo_api_major_holders()
    assert frame.loc["insidersPercentHeld", "AAPL"] == 0.0165
    assert frame.loc["institutionsCount", "AAPL"] == 7715


def test_insider_holders(ticker):
    frame = ticker.yahoo_api_insider_holders()
    assert frame.loc[0, "name"] == "COOK TIMOTHY D"
    assert frame.loc[0, "positionDirect"] == 3237840
    assert frame.loc[0, "latestTransDate"] == pd.Timestamp("2026-10-02", tz="UTC")


def test_insider_transactions_newest_first(ticker):
    frame = ticker.yahoo_api_insider_transactions()
    assert list(frame["filerName"]) == ["NEW", "OLD"]
    assert frame.loc[0, "shares"] == 2399


def test_insider_purchase_activity(ticker):
    frame = ticker.yahoo_api_insider_purchase_activity()
    assert frame.loc["period", "AAPL"] == "6m"
    assert frame.loc["netInfoShares", "AAPL"] == 257744


def test_sec_filings_newest_first_with_exhibits(ticker):
    frame = ticker.yahoo_api_sec_filings()
    assert list(frame["type"]) == ["8-K/A", "10-K"]
    assert frame.loc[0, "exhibits"][0]["url"] == "https://example.com/x.htm"


def test_missing_modules_give_empty_frames(monkeypatch):
    ticker = Ticker("SPY")
    empty = {"quoteSummary": {"result": [{}], "error": None}}
    monkeypatch.setattr(
        ticker, "get_response", lambda url: SimpleNamespace(json=lambda: empty)
    )
    for name in (
        "yahoo_api_institutional_holders",
        "yahoo_api_fund_holders",
        "yahoo_api_major_holders",
        "yahoo_api_insider_holders",
        "yahoo_api_insider_transactions",
        "yahoo_api_insider_purchase_activity",
        "yahoo_api_sec_filings",
    ):
        assert getattr(ticker, name)().empty, name
