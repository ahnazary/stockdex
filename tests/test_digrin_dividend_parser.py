"""Offline tests for the Digrin dividend table parser using HTML fixtures."""

import logging
from pathlib import Path
from types import SimpleNamespace

import pytest

from stockdex import Ticker

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "digrin"


def fixture_ticker(monkeypatch, html):
    ticker = Ticker("AAPL")
    monkeypatch.setattr(
        ticker, "get_response", lambda url: SimpleNamespace(content=html.encode())
    )
    return ticker


def read(name):
    return (FIXTURES / name).read_text()


def test_valid_table(monkeypatch):
    frame = fixture_ticker(monkeypatch, read("dividends_valid.html")).digrin_dividend
    assert len(frame) == 2
    assert list(frame.columns) == [
        "Ex-dividend date",
        "Payable date",
        "Dividend amount (change)",
    ]
    assert frame.iloc[0]["Dividend amount (change)"] == "0.2600 USD (4%)"


def test_empty_table(monkeypatch):
    assert fixture_ticker(
        monkeypatch, read("dividends_empty.html")
    ).digrin_dividend.empty


def test_unexpected_rows_are_skipped(monkeypatch, caplog):
    ticker = fixture_ticker(monkeypatch, read("dividends_mixed_rows.html"))
    with caplog.at_level(logging.WARNING, logger="stockdex.digrin_interface"):
        frame = ticker.digrin_dividend
    assert list(frame["Ex-dividend date"]) == ["2026-01-02", "2025-10-02"]
    assert "Skipped 1 Digrin dividend row" in caplog.text


@pytest.mark.parametrize(
    "html",
    [
        "<html>Access denied</html>",
        "<table>Ex-dividend date</table>",
        "<table><thead><tr><th>Ex-dividend date</th></tr></thead><tbody></tbody></table>",
        read("dividends_malformed.html"),
    ],
)
def test_changed_layout_raises(monkeypatch, html):
    with pytest.raises(ValueError):
        _ = fixture_ticker(monkeypatch, html).digrin_dividend
