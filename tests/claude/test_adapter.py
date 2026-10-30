import json
from datetime import datetime, timezone

import numpy as np
import pandas as pd
import pytest
from curl_cffi.requests.exceptions import RequestException

from stockdex import config
from stockdex.claude_adapter import (
    _PROVIDER_LOCK,
    DEFAULT_METRICS,
    StockdexAdapter,
    _scalar,
    encode_json,
)
from stockdex.exceptions import (
    LayoutChangedError,
    NoDataError,
    ProviderBlockedError,
    RateLimitError,
)


def test_default_metrics_are_known():
    for statement, metrics in DEFAULT_METRICS.items():
        assert set(metrics) <= set(getattr(config, statement.upper() + "_COLUMNS"))


def test_prices(adapter, provider):
    result = adapter.get_prices("aapl", limit=1)
    assert result["ok"]
    assert result["ticker"] == "AAPL"
    assert result["source"] == "yahoo_api"
    assert provider.calls == [{"range": "1mo", "dataGranularity": "1d"}]
    assert result["records"][0]["timestamp"] == "2026-01-02T00:00:00+00:00"
    assert result["records"][0]["close"] is None
    assert result["total_rows"] == 2
    assert result["returned_rows"] == 1
    assert result["truncated"]
    assert json.loads(encode_json(result)) == result


@pytest.mark.parametrize(
    "symbol",
    [
        "https://example.com",
        "../AAPL",
        "AAPL;id",
        "AAPL\n",
        "A" * 21,
        "",
        None,
        "AAPL?x=1",
        "AAPL/TEST",
        "ß",
        "^",
        "^^GSPC",
        "GC==F",
        "AAPL^",
        "=X",
    ],
)
def test_reject_symbols_before_network(adapter, provider, symbol):
    result = adapter.get_prices(symbol)
    assert result["error"]["code"] == "invalid_input"
    assert provider.calls == []


@pytest.mark.parametrize(
    "symbol", ["BRK-B", "BMW.DE", "7203.T", "^GSPC", "GC=F", "EURUSD=X", "^n225"]
)
def test_exchange_symbols(adapter, symbol):
    assert adapter.get_prices(symbol)["ok"]


@pytest.mark.parametrize("limit", [0, 501, -1, True, 1.5, "20"])
def test_reject_limit(adapter, provider, limit):
    assert adapter.get_prices("AAPL", limit=limit)["error"]["code"] == "invalid_input"
    assert provider.calls == []


def test_reject_price_range(adapter):
    assert adapter.get_prices("AAPL", range="max")["error"]["code"] == "invalid_input"


def test_financials(adapter, provider):
    result = adapter.get_financial_statement("AAPL")
    assert result["ok"]
    assert result["records"][0] == {
        "date": "2025-12-31",
        "annualTotalRevenue": 2000,
        "annualNetIncome": None,
        "annualBasicEPS": None,
    }
    assert "annualBasicEPS" in result["warnings"][0]
    assert provider.calls[0] == {
        "frequency": "annual",
        "format": "raw",
        "period1": datetime(2021, 10, 3, tzinfo=timezone.utc),
        "period2": datetime(2026, 10, 3, tzinfo=timezone.utc),
    }


def test_end_date_is_exclusive(adapter):
    result = adapter.get_financial_statement(
        "AAPL", start_date="2024-12-31", end_date="2025-12-31"
    )
    assert [r["date"] for r in result["records"]] == ["2024-12-31"]


def test_leap_year_defaults(provider):
    adapter = StockdexAdapter(
        lambda **kw: provider, lambda: datetime(2024, 2, 29, tzinfo=timezone.utc)
    )
    result = adapter.get_financial_statement("AAPL")
    assert result["parameters"]["start_date"] == "2019-02-28"
    assert provider.calls[0]["period1"].day == 28


@pytest.mark.parametrize(
    "kwargs",
    [
        {"statement": "arbitrary_method"},
        {"frequency": "monthly"},
        {"start_date": "2026-02-30"},
        {"end_date": "2027-01-01"},
        {"end_date": "0001-01-01"},
        {"start_date": "2026-10-03", "end_date": "2026-10-03"},
        {"start_date": "2000-01-01"},
        {"metrics": []},
        {"metrics": ["NotAMetric"]},
        {"metrics": "TotalRevenue"},
        {"metrics": ["TotalRevenue", "TotalRevenue"]},
    ],
)
def test_reject_financial_arguments(adapter, provider, kwargs):
    assert (
        adapter.get_financial_statement("AAPL", **kwargs)["error"]["code"]
        == "invalid_input"
    )
    assert not provider.calls


@pytest.mark.parametrize(
    "statement,metric,method",
    [
        ("cash_flow", "FreeCashFlow", "yahoo_api_cash_flow"),
        ("balance_sheet", "TotalAssets", "yahoo_api_balance_sheet"),
    ],
)
def test_statement_dispatch(adapter, provider, monkeypatch, statement, metric, method):
    calls = []

    def fetch(**kwargs):
        calls.append(kwargs)
        return pd.DataFrame({"quarterly" + metric: [12]}, index=["2026-06-30"])

    monkeypatch.setattr(provider, method, fetch)
    result = adapter.get_financial_statement(
        "AAPL", statement=statement, frequency="quarterly", metrics=[metric]
    )
    assert result["records"][0]["quarterly" + metric] == 12
    assert calls[0]["format"] == "raw"


def test_dividends(adapter):
    result = adapter.get_dividends("AAPL")
    assert result["ok"] and result["source"] == "digrin"
    assert result["records"][0]["amount"] == 0.26
    assert result["records"][0]["currency"] == "USD"
    assert result["records"][1]["amount"] is None
    assert result["records"][1]["payable_date"] is None
    assert result["warnings"]


@pytest.mark.parametrize("value", [np.nan, np.inf, -np.inf, pd.NaT, pd.NA, None])
def test_missing_values(value):
    assert _scalar(value) is None


@pytest.mark.parametrize(
    "error,code",
    [
        (RateLimitError("https://private/secret", "5"), "rate_limited"),
        (ProviderBlockedError("https://private/secret", 403), "provider_blocked"),
        (LayoutChangedError("Finviz", "secret"), "layout_changed"),
        (NoDataError(), "no_data"),
        (RequestException("secret"), "network_error"),
        (KeyError("secret"), "provider_schema_error"),
        (RuntimeError("secret"), "provider_error"),
    ],
)
def test_errors_are_sanitized(adapter, provider, monkeypatch, error, code):
    def fail(**kwargs):
        raise error

    monkeypatch.setattr(provider, "yahoo_api_price", fail)
    result = adapter.get_prices("AAPL")
    assert not result["ok"] and result["error"]["code"] == code
    assert "secret" not in encode_json(result)
    assert result["records"] == []
    assert not _PROVIDER_LOCK.locked()


def test_busy_does_not_call_provider(adapter, provider):
    with _PROVIDER_LOCK:
        assert adapter.get_prices("AAPL")["error"]["code"] == "busy"
    assert not provider.calls


def test_empty_data(adapter, provider, monkeypatch):
    monkeypatch.setattr(provider, "yahoo_api_price", lambda **kw: pd.DataFrame())
    assert adapter.get_prices("AAPL")["error"]["code"] == "no_data"


def test_unavailable_price_placeholder_is_no_data(adapter, provider, monkeypatch):
    unavailable = "Data Not Available"
    frame = pd.DataFrame(
        {
            column: [unavailable]
            for column in ("timestamp", "open", "high", "low", "close", "volume")
        }
    ).assign(currency="USD")
    monkeypatch.setattr(provider, "yahoo_api_price", lambda **kw: frame)
    assert adapter.get_prices("AAPL")["error"]["code"] == "no_data"


def test_byte_budget(adapter, provider, monkeypatch):
    original = provider.yahoo_api_price

    def large(**kwargs):
        frame = original(**kwargs)
        frame["exchangeName"] = "x" * 150_000
        return frame

    monkeypatch.setattr(provider, "yahoo_api_price", large)
    result = adapter.get_prices("AAPL")
    assert result["ok"] and result["truncated"]
    assert result["returned_rows"] == 1
    assert len(encode_json(result).encode()) <= 256 * 1024


def test_caller_parameters_are_not_mutated(adapter):
    parameters = {"range": "1mo", "limit": 5}
    result = adapter._request("prices", "AAPL", parameters)
    assert result["parameters"]["interval"] == "1d"
    assert parameters == {"range": "1mo", "limit": 5}
