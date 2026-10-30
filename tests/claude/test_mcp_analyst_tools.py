"""Offline tests for the analyst estimates and earnings calendar MCP tools."""

import pytest

from stockdex.claude_adapter import StockdexAdapter
from tests.claude.conftest import FakeTicker


@pytest.fixture
def adapter():
    return StockdexAdapter(ticker_factory=FakeTicker)


def test_estimates_table(adapter):
    result = adapter.get_dataset("AAPL", "estimates")
    assert result["columns"] == ["period", "earningsEstimate_avg"]
    assert result["records"][0] == {"period": "0q", "earningsEstimate_avg": 1.98}


def test_earnings_calendar_dates_are_iso_utc(adapter):
    result = adapter.get_dataset("AAPL", "earnings_calendar")
    assert result["records"][0] == {
        "field": "earningsDate",
        "value": "2026-11-02T20:00:00+00:00",
    }


def test_analyst_tool_schema():
    pytest.importorskip("mcp")
    import anyio

    from stockdex.claude_mcp import create_server

    tools = {t.name: t for t in anyio.run(create_server(adapter=None).list_tools)}
    estimates = tools["get_analyst_estimates"].input_schema["properties"]["dataset"]
    assert set(estimates["enum"]) == {
        "estimates",
        "recommendations",
        "upgrades_downgrades",
        "earnings_history",
    }
    calendar = tools["get_earnings_calendar"].input_schema["properties"]["dataset"]
    assert calendar.get("enum", [calendar.get("const")]) == ["earnings_calendar"]
