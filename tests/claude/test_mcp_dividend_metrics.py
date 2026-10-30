"""Offline tests for get_dividend_metrics (Digrin and Finviz)."""

import pandas as pd
import pytest

from stockdex.claude_adapter import DIVIDEND_METRICS
from stockdex.exceptions import RateLimitError


def test_payout_ratio(adapter):
    result = adapter.get_dividend_metrics("KO")
    assert result["ok"] and result["source"] == "digrin"
    assert result["parameters"]["dataset"] == "payout_ratio"
    assert result["records"] == [
        {"quarter": "2026Q3", "payout_ratio_pct": 56.87, "pe_ratio": 23.02},
        {"quarter": "2026Q2", "payout_ratio_pct": 51.55, "pe_ratio": 20.42},
    ]


@pytest.mark.parametrize("dataset", ["growth_3y", "growth_5y", "growth_10y"])
def test_growth_projections(adapter, dataset):
    result = adapter.get_dividend_metrics("KO", dataset=dataset)
    assert result["ok"] and result["source"] == "digrin"
    assert result["records"][0] == {
        "year": 2027,
        "projected_dividend": 2.162,
        "currency": "USD",
        "yield_on_cost_pct": 2.29,
    }
    years = dataset[len("growth_") : -1]
    assert any(
        "Projections, not history" in w and f"{years}-year" in w
        for w in result["warnings"]
    )


def test_annual_from_finviz(adapter):
    result = adapter.get_dividend_metrics("KO", dataset="annual")
    assert result["ok"] and result["source"] == "finviz"
    assert result["records"] == [
        {
            "fiscal_year": 2026,
            "amount": 2.12,
            "yield_pct": None,
            "payout_pct": None,
            "estimate": True,
        },
        {
            "fiscal_year": 2025,
            "amount": 2.04,
            "yield_pct": 2.87,
            "payout_pct": 67.3,
            "estimate": False,
        },
    ]


def test_summary_from_finviz(adapter):
    result = adapter.get_dividend_metrics("KO", dataset="summary")
    assert result["ok"] and result["source"] == "finviz"
    assert {r["field"]: r["value"] for r in result["records"]} == {
        "last_close": 94.559,
        "next_ex_dividend_date": "2026-12-01",
        "next_12m_dividend_estimate": 2.198,
        "trailing_12m_dividend": 2.1,
    }


def test_rejects_unknown_dataset(adapter, provider):
    result = adapter.get_dividend_metrics("KO", dataset="yield")
    assert result["error"]["code"] == "invalid_input"
    assert set(DIVIDEND_METRICS) <= set(
        result["error"]["message"].replace(",", " ").split()
    )


@pytest.mark.parametrize(
    "dataset, source",
    [("annual", "finviz"), ("summary", "finviz"), ("payout_ratio", "digrin")],
)
def test_invalid_input_keeps_dataset_source(adapter, provider, dataset, source):
    result = adapter.get_dividend_metrics("KO", dataset=dataset, limit=0)
    assert result["error"]["code"] == "invalid_input"
    assert result["source"] == source
    assert not provider.calls


def test_changed_payout_periods_are_layout_changed(adapter, provider, monkeypatch):
    frame = pd.DataFrame(
        {"Date": ["Q3 2026"], "Payout ratio": ["1%"], "PE ratio": ["2"]}
    )
    monkeypatch.setattr(
        type(provider), "digrin_payout_ratio", property(lambda s: frame)
    )
    result = adapter.get_dividend_metrics("KO")
    assert result["error"]["code"] == "layout_changed"
    assert result["source"] == "digrin"


def test_changed_fiscal_periods_are_layout_changed(adapter, provider, monkeypatch):
    frame = provider.finviz_dividends_annual_data().assign(FiscalPeriod="FY25")
    monkeypatch.setattr(provider, "finviz_dividends_annual_data", lambda: frame)
    result = adapter.get_dividend_metrics("KO", dataset="annual")
    assert result["error"]["code"] == "layout_changed"


def test_rate_limited_digrin(adapter, provider, monkeypatch):
    def limited(self):
        raise RateLimitError("https://www.digrin.com/secret", "60")

    monkeypatch.setattr(type(provider), "digrin_dgr5", property(limited))
    result = adapter.get_dividend_metrics("KO", dataset="growth_5y")
    assert result["error"]["code"] == "rate_limited"


def test_empty_is_no_data(adapter, provider, monkeypatch):
    monkeypatch.setattr(provider, "finviz_dividends_annual_data", pd.DataFrame)
    result = adapter.get_dividend_metrics("KO", dataset="annual")
    assert result["error"]["code"] == "no_data"
