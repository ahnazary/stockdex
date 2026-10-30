"""Offline tests for Yahoo options, batch quotes, search and similar symbols."""

from types import SimpleNamespace

import pandas as pd
import pytest

from stockdex import Ticker
from stockdex.yahoo_api_interface import YahooAPI

CALL = {
    "contractSymbol": "AAPL261120C00350000",
    "strike": 350.0,
    "bid": 9.5,
    "ask": 9.8,
    "expiration": 1795132800,
    "lastTradeDate": 1793035429,
    "inTheMoney": False,
}
PUT = {**CALL, "contractSymbol": "AAPL261120P00350000", "bid": 10.1}
OPTIONS = {
    "optionChain": {
        "result": [
            {
                "underlyingSymbol": "AAPL",
                "expirationDates": [1795132800, 1793318400],
                "options": [
                    {"expirationDate": 1795132800, "calls": [CALL], "puts": [PUT]}
                ],
            }
        ]
    }
}


def fake(ticker, monkeypatch, payload):
    ticker.urls = []

    def response(url):
        ticker.urls.append(url)
        return SimpleNamespace(json=lambda: payload)

    monkeypatch.setattr(ticker, "get_response", response)
    return ticker


def test_option_expirations_sorted_utc(monkeypatch):
    ticker = fake(Ticker("AAPL"), monkeypatch, OPTIONS)
    dates = ticker.yahoo_api_option_expirations()
    assert dates == [
        pd.Timestamp(1793318400, unit="s", tz="UTC"),
        pd.Timestamp(1795132800, unit="s", tz="UTC"),
    ]


def test_options_chain_both(monkeypatch):
    ticker = fake(Ticker("AAPL"), monkeypatch, OPTIONS)
    chain = ticker.yahoo_api_options_chain()
    assert list(chain["optionType"]) == ["call", "put"]
    assert chain.loc[1, "bid"] == 10.1
    assert chain.loc[0, "expiration"] == pd.Timestamp("2026-11-20", tz="UTC")
    assert "?date=" not in ticker.urls[0]


def test_options_chain_puts_for_expiration(monkeypatch):
    ticker = fake(Ticker("AAPL"), monkeypatch, OPTIONS)
    chain = ticker.yahoo_api_options_chain("2026-11-20", option_type="puts")
    assert set(chain["optionType"]) == {"put"}
    assert ticker.urls[0].endswith("?date=1795132800")


def test_no_options_gives_empty(monkeypatch):
    empty = {"optionChain": {"result": [], "error": None}}
    ticker = fake(Ticker("VFIAX"), monkeypatch, empty)
    assert ticker.yahoo_api_options_chain().empty
    assert ticker.yahoo_api_option_expirations() == []


@pytest.fixture
def static_response(monkeypatch):
    calls = []

    def install(payload):
        def response(self, url):
            calls.append(url)
            return SimpleNamespace(json=lambda: payload)

        monkeypatch.setattr(YahooAPI, "get_response", response)
        return calls

    return install


def test_quotes(static_response):
    calls = static_response(
        {
            "quoteResponse": {
                "result": [
                    {
                        "symbol": "AAPL",
                        "regularMarketPrice": 348.91,
                        "regularMarketTime": 1793304001,
                    },
                    {"symbol": "MSFT", "regularMarketPrice": 530.14},
                ]
            }
        }
    )
    frame = YahooAPI.yahoo_api_quotes(["aapl", " msft ", ""])
    assert calls[0].endswith("?symbols=AAPL,MSFT")
    assert frame.loc["MSFT", "regularMarketPrice"] == 530.14
    assert frame.loc["AAPL", "regularMarketTime"] == pd.Timestamp(
        1793304001, unit="s", tz="UTC"
    )


def test_quotes_requires_symbols():
    with pytest.raises(ValueError):
        YahooAPI.yahoo_api_quotes(["", " "])


def test_search_selects_columns_and_encodes_query(static_response):
    calls = static_response(
        {
            "quotes": [
                {
                    "symbol": "BMW.DE",
                    "shortname": "BMW",
                    "quoteType": "EQUITY",
                    "exchange": "GER",
                    "score": 1.0,
                    "isYahooFinance": True,
                }
            ]
        }
    )
    frame = YahooAPI.yahoo_api_search("bayerische motoren", limit=3)
    assert "q=bayerische%20motoren" in calls[0]
    assert "quotesCount=3" in calls[0]
    assert list(frame.columns) == ["symbol", "shortname", "quoteType", "exchange"]
    assert frame.loc[0, "symbol"] == "BMW.DE"


def test_search_no_results(static_response):
    static_response({"quotes": []})
    frame = YahooAPI.yahoo_api_search("zzzqqqxx")
    assert frame.empty and "symbol" in frame.columns


@pytest.mark.parametrize("query, limit", [("", 10), ("  ", 10), ("ok", 0), ("ok", 51)])
def test_search_validation(query, limit):
    with pytest.raises(ValueError):
        YahooAPI.yahoo_api_search(query, limit)


def test_similar_symbols_sorted(monkeypatch):
    payload = {
        "finance": {
            "result": [
                {
                    "symbol": "AAPL",
                    "recommendedSymbols": [
                        {"symbol": "MSFT", "score": 0.14},
                        {"symbol": "AMZN", "score": 0.18},
                    ],
                }
            ]
        }
    }
    ticker = fake(Ticker("AAPL"), monkeypatch, payload)
    frame = ticker.yahoo_api_similar_symbols()
    assert list(frame["symbol"]) == ["AMZN", "MSFT"]
