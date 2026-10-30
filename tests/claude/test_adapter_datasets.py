"""Offline tests for the adapter's generic Yahoo dataset operation."""

import pandas as pd
import pytest

from stockdex.claude_adapter import YAHOO_DATASETS, StockdexAdapter, _scalar
from stockdex.yahoo_api_interface import YahooAPI


class DatasetTicker:
    def __init__(self):
        self.calls = []

    def yahoo_api_profile(self):
        self.calls.append("profile")
        return pd.DataFrame(
            {"AAPL": ["Cupertino", 166000, pd.Timestamp("2026-10-28", tz="UTC")]},
            index=["city", "fullTimeEmployees", "governanceEpochDate"],
        )

    def yahoo_api_upgrades_downgrades(self):
        return pd.DataFrame(
            {"firm": [f"Firm {i}" for i in range(30)], "action": ["up"] * 30}
        )

    def yahoo_api_fund_sector_weightings(self):
        return pd.DataFrame(
            {"weight": [0.40, 0.11]}, index=["technology", "financial_services"]
        )

    def yahoo_api_sec_filings(self):
        return pd.DataFrame(
            {
                "type": ["10-K"],
                "exhibits": [[{"type": "10-K", "url": "https://example.com/a"}]],
            }
        )

    def yahoo_api_fund_top_holdings(self):
        return pd.DataFrame()


@pytest.fixture
def ticker():
    return DatasetTicker()


@pytest.fixture
def adapter(ticker):
    return StockdexAdapter(ticker_factory=lambda **kwargs: ticker)


def test_every_dataset_maps_to_a_real_yahoo_method():
    for dataset, (method, kind) in YAHOO_DATASETS.items():
        assert hasattr(YahooAPI, method), (dataset, method)
        assert kind in ("record", "table")


def test_record_dataset_becomes_field_value_rows(adapter):
    result = adapter.get_dataset("aapl", "profile")
    assert result["ok"] and result["ticker"] == "AAPL"
    assert result["source"] == "yahoo_api"
    assert result["operation"] == "dataset"
    assert result["columns"] == ["field", "value"]
    assert result["records"][0] == {"field": "city", "value": "Cupertino"}
    assert result["records"][2]["value"] == "2026-10-28T00:00:00+00:00"
    assert result["parameters"]["limit"] == 500


def test_table_dataset_defaults_to_20_rows(adapter):
    result = adapter.get_dataset("AAPL", "upgrades_downgrades")
    assert result["returned_rows"] == 20
    assert result["total_rows"] == 30
    assert result["truncated"] is True


def test_explicit_limit(adapter):
    result = adapter.get_dataset("AAPL", "upgrades_downgrades", limit=5)
    assert result["returned_rows"] == 5


def test_named_index_kept_as_column(adapter):
    result = adapter.get_dataset("SPY", "fund_sectors")
    assert result["columns"] == ["key", "weight"]
    assert result["records"][0] == {"key": "technology", "weight": 0.40}


def test_nested_values_serialize(adapter):
    result = adapter.get_dataset("AAPL", "sec_filings")
    assert result["records"][0]["exhibits"][0]["url"] == "https://example.com/a"


def test_empty_dataset_is_no_data(adapter):
    result = adapter.get_dataset("AAPL", "fund_top_holdings")
    assert result["error"]["code"] == "no_data"


@pytest.mark.parametrize(
    "kwargs",
    [
        {"dataset": "nope"},
        {"dataset": "profile", "limit": 0},
        {"dataset": "profile", "limit": 501},
        {"dataset": "profile", "limit": "5"},
    ],
)
def test_invalid_input_rejected_before_request(adapter, ticker, kwargs):
    result = adapter.get_dataset("AAPL", **kwargs)
    assert result["error"]["code"] == "invalid_input"
    assert ticker.calls == []


def test_scalar_handles_nested_values():
    assert _scalar([1, {"a": float("nan")}]) == [1, {"a": None}]
