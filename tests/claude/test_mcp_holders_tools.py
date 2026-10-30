"""Offline tests for the holders and SEC filings MCP tools."""

import pytest

from stockdex.claude_adapter import StockdexAdapter
from tests.claude.conftest import FakeTicker


@pytest.fixture
def adapter():
    return StockdexAdapter(ticker_factory=FakeTicker)


def test_institutional_holders(adapter):
    result = adapter.get_dataset("AAPL", "institutional_holders")
    assert result["records"] == [{"organization": "Blackrock Inc.", "pctHeld": 0.0797}]


def test_sec_filings_keep_exhibit_links(adapter):
    result = adapter.get_dataset("AAPL", "sec_filings")
    record = result["records"][0]
    assert record["type"] == "8-K"
    assert record["exhibits"] == [{"type": "8-K", "url": "https://example.com/x"}]


def test_holders_tool_schema():
    pytest.importorskip("mcp")
    import anyio

    from stockdex.claude_mcp import create_server

    tools = {t.name: t for t in anyio.run(create_server(adapter=None).list_tools)}
    holders = tools["get_holders"].input_schema["properties"]["dataset"]
    assert set(holders["enum"]) == {
        "institutional_holders",
        "fund_holders",
        "ownership_breakdown",
        "insiders",
        "insider_transactions",
        "insider_activity",
    }
