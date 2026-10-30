"""Offline tests for the ETF and fund MCP tools."""

import pytest

from stockdex.claude_adapter import StockdexAdapter
from tests.claude.conftest import FakeTicker


@pytest.fixture
def adapter():
    return StockdexAdapter(ticker_factory=FakeTicker)


def test_fund_top_holdings(adapter):
    result = adapter.get_dataset("SPY", "fund_top_holdings")
    assert result["records"][0] == {"symbol": "NVDA", "holdingPercent": 0.0836}


def test_fund_performance_keeps_period_as_key(adapter):
    result = adapter.get_dataset("SPY", "fund_performance")
    assert result["columns"] == ["key", "fund", "category"]
    assert result["records"][1] == {"key": "2025", "fund": 0.1772, "category": 0.1554}


def test_fund_tool_schemas():
    pytest.importorskip("mcp")
    import anyio

    from stockdex.claude_mcp import create_server

    tools = {t.name: t for t in anyio.run(create_server(adapter=None).list_tools)}
    holdings = tools["get_fund_holdings"].input_schema["properties"]["dataset"]
    assert set(holdings["enum"]) == {
        "fund_top_holdings",
        "fund_sectors",
        "fund_asset_allocation",
    }
    profile = tools["get_fund_profile"].input_schema["properties"]["dataset"]
    assert set(profile["enum"]) == {"fund_profile", "fund_performance"}
