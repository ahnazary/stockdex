"""Offline tests for the company, key statistics and valuation MCP tools."""

import pytest

from stockdex.claude_adapter import StockdexAdapter
from tests.claude.conftest import FakeTicker


@pytest.fixture
def adapter():
    return StockdexAdapter(ticker_factory=FakeTicker)


def test_company_profile_record(adapter):
    result = adapter.get_dataset("AAPL", "profile")
    assert result["ok"]
    assert result["records"] == [
        {"field": "city", "value": "Cupertino"},
        {"field": "sector", "value": "Technology"},
    ]


def test_key_statistics_summary(adapter):
    result = adapter.get_dataset("AAPL", "summary")
    assert {"field": "marketCap", "value": 5.09e12} in result["records"]


def test_valuation_history_strips_prefix_and_sorts_newest_first(adapter):
    result = adapter.get_valuation_history("AAPL", frequency="annual")
    assert result["ok"]
    assert result["columns"] == ["date", "MarketCap", "PeRatio"]
    assert result["records"][0] == {
        "date": "2026-06-30",
        "MarketCap": 3.5e12,
        "PeRatio": 35.0,
    }
    assert result["warnings"]


@pytest.mark.parametrize("frequency", ["monthly", "", None])
def test_valuation_history_rejects_frequency(adapter, frequency):
    result = adapter.get_valuation_history("AAPL", frequency=frequency)
    assert result["error"]["code"] == "invalid_input"


def test_mcp_tools_expose_only_their_datasets():
    pytest.importorskip("mcp")
    import anyio

    from stockdex.claude_mcp import create_server

    tools = {t.name: t for t in anyio.run(create_server(adapter=None).list_tools)}
    profile = tools["get_company_profile"].input_schema["properties"]["dataset"]
    assert set(profile["enum"]) == {"profile", "officers", "similar_symbols"}
    stats = tools["get_key_statistics"].input_schema["properties"]["dataset"]
    assert set(stats["enum"]) == {
        "summary",
        "key_statistics",
        "financial_data",
        "market_price",
    }
