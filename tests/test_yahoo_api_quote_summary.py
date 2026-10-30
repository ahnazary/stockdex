"""Offline tests for the Yahoo quoteSummary core method."""

from types import SimpleNamespace

import pytest

from stockdex import Ticker
from stockdex.exceptions import NoDataError
from stockdex.yahoo_api_interface import YahooAPI

PAYLOAD = {
    "quoteSummary": {
        "result": [
            {
                "financialData": {
                    "maxAge": 86400,
                    "currentPrice": {"raw": 348.91, "fmt": "348.91"},
                    "totalRevenue": {
                        "raw": 466820000000,
                        "fmt": "466.82B",
                        "longFmt": "466,820,000,000",
                    },
                    "recommendationKey": "buy",
                    "targetMedianPrice": {},
                },
                "calendarEvents": {
                    "earnings": {
                        "earningsDate": [{"raw": 1793649600, "fmt": "2026-11-02"}],
                        "isEarningsDateEstimate": False,
                    }
                },
                "esgScores": None,
            }
        ],
        "error": None,
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


def test_raw_values_are_unwrapped(ticker):
    data = ticker.yahoo_api_quote_summary(["financialData", "calendarEvents"])
    assert data["financialData"]["currentPrice"] == 348.91
    assert data["financialData"]["totalRevenue"] == 466820000000
    assert data["financialData"]["recommendationKey"] == "buy"
    assert data["financialData"]["targetMedianPrice"] is None
    assert data["calendarEvents"]["earnings"]["earningsDate"] == [1793649600]
    assert data["calendarEvents"]["earnings"]["isEarningsDateEstimate"] is False


def test_fmt_values(ticker):
    data = ticker.yahoo_api_quote_summary("financialData", format="fmt")
    assert data["financialData"]["totalRevenue"] == "466.82B"


def test_single_module_string_and_url(ticker):
    ticker.yahoo_api_quote_summary("financialData")
    assert "/v10/finance/quoteSummary/AAPL?modules=financialData" in ticker.urls[0]


def test_missing_module_is_omitted(ticker):
    data = ticker.yahoo_api_quote_summary(["financialData", "esgScores"])
    assert set(data) == {"financialData"}


@pytest.mark.parametrize("modules", [[], "notAModule", ["price", "bogus"]])
def test_unknown_modules_rejected_before_request(ticker, modules):
    with pytest.raises(ValueError, match="Unsupported quoteSummary module"):
        ticker.yahoo_api_quote_summary(modules)
    assert ticker.urls == []


def test_empty_result_returns_empty_dict(monkeypatch):
    ticker = Ticker("ZZZZ")
    empty = {"quoteSummary": {"result": None, "error": None}}
    monkeypatch.setattr(
        ticker, "get_response", lambda url: SimpleNamespace(json=lambda: empty)
    )
    assert ticker.yahoo_api_quote_summary("price") == {}


def _not_found(url):
    raise RuntimeError(f"Failed to fetch URL (status 404): {url}")


def test_404_for_inapplicable_module_returns_empty(monkeypatch):
    ticker = Ticker("AAPL")
    calls = []

    def response(url):
        calls.append(url)
        if "modules=topHoldings" in url:
            _not_found(url)
        return SimpleNamespace(json=lambda: {"quoteSummary": {"result": [{}]}})

    monkeypatch.setattr(ticker, "get_response", response)
    assert ticker.yahoo_api_quote_summary("topHoldings") == {}
    assert "modules=quoteType" in calls[1]


def test_404_for_unknown_symbol_raises_no_data(monkeypatch):
    ticker = Ticker("ZZZZZZQ")
    monkeypatch.setattr(ticker, "get_response", _not_found)
    with pytest.raises(NoDataError, match="ZZZZZZQ"):
        ticker.yahoo_api_quote_summary("price")


def test_other_errors_propagate(monkeypatch):
    ticker = Ticker("AAPL")

    def boom(url):
        raise RuntimeError(f"Failed to fetch URL (status 500): {url}")

    monkeypatch.setattr(ticker, "get_response", boom)
    with pytest.raises(RuntimeError, match="status 500"):
        ticker.yahoo_api_quote_summary("price")


@pytest.mark.parametrize(
    "value, expected",
    [
        ({"raw": 1, "fmt": "1"}, 1),
        ({"fmt": "only fmt"}, "only fmt"),
        ({}, None),
        ([{"raw": 2}, {}], [2, None]),
        ({"a": {"raw": 3}, "b": "x"}, {"a": 3, "b": "x"}),
        ("plain", "plain"),
    ],
)
def test_unwrap(value, expected):
    assert YahooAPI._unwrap(value) == expected
