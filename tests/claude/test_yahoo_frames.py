"""Exercise the real Yahoo parsers with synthetic JSON, not a live API."""

from datetime import datetime, timezone
from types import SimpleNamespace

from stockdex import Ticker
from stockdex.claude_adapter import StockdexAdapter


def test_actual_price_parser(monkeypatch):
    provider = Ticker("AAPL")
    payload = {
        "chart": {
            "result": [
                {
                    "meta": {
                        "currency": "USD",
                        "exchangeTimezoneName": "America/New_York",
                        "timezone": "EST",
                        "exchangeName": "NMS",
                        "instrumentType": "EQUITY",
                    },
                    "timestamp": [1767225600],
                    "indicators": {
                        "quote": [
                            {
                                "volume": [100],
                                "close": [12],
                                "open": [10],
                                "high": [13],
                                "low": [9],
                            }
                        ]
                    },
                }
            ]
        }
    }
    monkeypatch.setattr(
        provider, "get_response", lambda url: SimpleNamespace(json=lambda: payload)
    )
    result = StockdexAdapter(lambda **kw: provider).get_prices("AAPL")
    assert result["ok"]
    assert result["records"][0]["timestamp"] == "2026-01-01T00:00:00+00:00"
    assert result["records"][0]["exchangeTimezoneName"] == "America/New_York"


def test_actual_financial_parser(monkeypatch):
    provider = Ticker("AAPL")
    payload = {
        "timeseries": {
            "result": [
                {
                    "meta": {"type": ["annualTotalRevenue"]},
                    "annualTotalRevenue": [
                        {
                            "asOfDate": "2025-12-31",
                            "reportedValue": {"raw": 1000000000, "fmt": "1B"},
                        }
                    ],
                }
            ]
        }
    }
    urls = []

    def response(url):
        urls.append(url)
        return SimpleNamespace(json=lambda: payload)

    monkeypatch.setattr(provider, "get_response", response)
    adapter = StockdexAdapter(
        lambda **kw: provider, lambda: datetime(2026, 10, 3, tzinfo=timezone.utc)
    )
    result = adapter.get_financial_statement("AAPL", metrics=["TotalRevenue"])
    assert result["ok"]
    assert result["records"] == [
        {"date": "2025-12-31", "annualTotalRevenue": 1000000000}
    ]
    assert "period1=" in urls[0] and "period2=" in urls[0]
