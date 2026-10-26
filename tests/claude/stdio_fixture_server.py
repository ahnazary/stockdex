"""Test-only subprocess harness; never imported by the production entry point."""

from datetime import datetime, timezone

from curl_cffi import requests

from stockdex.claude_adapter import StockdexAdapter
from stockdex.claude_mcp import create_server
from tests.claude.conftest import FakeTicker


def deny_network(*args, **kwargs):
    raise AssertionError("Network forbidden in stdio test subprocess")


requests.Session.request = deny_network
create_server(
    StockdexAdapter(
        FakeTicker,
        lambda: datetime(2026, 10, 3, tzinfo=timezone.utc),
    )
).run(transport="stdio")
