"""Errors raised while fetching the Yahoo crumb must keep their type through the adapter."""

from types import SimpleNamespace

import pytest
from curl_cffi.requests.exceptions import RequestException

from stockdex import Ticker
from stockdex.claude_adapter import StockdexAdapter


class CrumbSession:
    """Stand-in for the shared curl_cffi session used during crumb acquisition."""

    def __init__(self, crumb_response=None, error=None):
        self.crumb_response = crumb_response
        self.error = error

    def get(self, url, **kwargs):
        if self.error is not None:
            raise self.error
        if "getcrumb" in url:
            return self.crumb_response
        return SimpleNamespace(status_code=200, text="", headers={})


@pytest.fixture
def fresh_ticker(monkeypatch):
    def make(session):
        ticker = Ticker("AAPL")
        monkeypatch.setattr(ticker, "session", session)
        monkeypatch.setattr(ticker, "_yahoo_crumb", None)
        return StockdexAdapter(lambda **kw: ticker)

    return make


def test_crumb_transport_error_is_network_error(fresh_ticker):
    adapter = fresh_ticker(CrumbSession(error=RequestException("dns secret")))
    result = adapter.get_prices("AAPL")
    assert result["error"]["code"] == "network_error"
    assert "secret" not in str(result)


def test_crumb_rate_limit_is_rate_limited(fresh_ticker):
    response = SimpleNamespace(
        status_code=429, text="Too Many Requests", headers={"Retry-After": "30"}
    )
    result = fresh_ticker(CrumbSession(crumb_response=response)).get_prices("AAPL")
    assert result["error"]["code"] == "rate_limited"


def test_invalid_crumb_is_provider_error(fresh_ticker):
    response = SimpleNamespace(status_code=200, text="<html>consent</html>", headers={})
    result = fresh_ticker(CrumbSession(crumb_response=response)).get_prices("AAPL")
    assert result["error"]["code"] == "provider_error"
