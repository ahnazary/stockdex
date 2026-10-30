"""Exercise the adapter on the real Digrin parser with HTML fixtures, offline."""

from pathlib import Path
from types import SimpleNamespace

import pytest

from stockdex import Ticker
from stockdex.claude_adapter import StockdexAdapter

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures" / "digrin"


def adapter_for(monkeypatch, html):
    ticker = Ticker("AAPL")
    monkeypatch.setattr(
        ticker, "get_response", lambda url: SimpleNamespace(content=html.encode())
    )
    return StockdexAdapter(lambda **kw: ticker)


def test_valid_dividends(monkeypatch):
    html = (FIXTURES / "dividends_valid.html").read_text()
    result = adapter_for(monkeypatch, html).get_dividends("AAPL")
    assert result["ok"] and result["records"][0]["amount"] == 0.26


def test_empty_table_is_no_data(monkeypatch):
    html = (FIXTURES / "dividends_empty.html").read_text()
    result = adapter_for(monkeypatch, html).get_dividends("AAPL")
    assert result["error"]["code"] == "no_data"


@pytest.mark.parametrize(
    "html",
    [
        "<html>Access denied</html>",
        (FIXTURES / "dividends_malformed.html").read_text(),
    ],
)
def test_changed_layout_is_reported(monkeypatch, html):
    result = adapter_for(monkeypatch, html).get_dividends("AAPL")
    assert result["error"]["code"] == "layout_changed"
