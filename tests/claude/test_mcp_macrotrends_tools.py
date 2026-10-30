"""Offline tests for the Macrotrends statement source and margins/ratios tool."""

import pytest

from stockdex.claude_adapter import (
    MACROTRENDS_DATASETS,
    MACROTRENDS_DEFAULT_METRICS,
    _money,
    _percent,
)
from stockdex.exceptions import ProviderBlockedError


def test_statement_from_macrotrends(adapter, provider):
    result = adapter.get_financial_statement("AAPL", source="macrotrends")
    assert result["ok"]
    assert result["source"] == "macrotrends"
    assert (
        result["parameters"]["metrics"]
        == MACROTRENDS_DEFAULT_METRICS["income_statement"]
    )
    assert result["columns"] == [
        "date",
        "Revenue",
        "Net Income",
        "EPS - Earnings Per Share",
    ]
    assert result["records"][0] == {
        "date": "2025-09-30",
        "Revenue": 416161,
        "Net Income": 112010,
        "EPS - Earnings Per Share": 7.46,
    }
    # Empty provider cells are null, never zero.
    assert result["records"][1]["EPS - Earnings Per Share"] is None
    assert any("millions" in w for w in result["warnings"])
    assert provider.calls[-1] == {
        "macrotrends": "income_statement",
        "frequency": "annual",
    }


def test_statement_source_default_is_yahoo(adapter):
    result = adapter.get_financial_statement("AAPL")
    assert result["source"] == "yahoo_api"
    assert result["parameters"]["source"] == "yahoo"


def test_macrotrends_metrics_are_case_insensitive_and_missing_warns(adapter):
    result = adapter.get_financial_statement(
        "AAPL", source="macrotrends", metrics=["revenue", "Goodwill"]
    )
    assert result["ok"]
    assert result["columns"] == ["date", "revenue", "Goodwill"]
    assert result["records"][0]["Goodwill"] is None
    warning = result["warnings"][0]
    assert "Goodwill" in warning and "Available rows: Revenue" in warning


def test_macrotrends_unknown_metrics_only_is_no_data(adapter):
    result = adapter.get_financial_statement(
        "AAPL", source="macrotrends", metrics=["TotalRevenue"]
    )
    assert result["error"]["code"] == "no_data"
    # The caller still learns which row names Macrotrends has.
    assert any(
        "TotalRevenue" in w and "Available rows: Revenue" in w
        for w in result["warnings"]
    )


def test_macrotrends_date_window(adapter):
    result = adapter.get_financial_statement(
        "AAPL",
        source="macrotrends",
        start_date="2024-01-01",
        end_date="2025-09-30",
    )
    assert [r["date"] for r in result["records"]] == ["2024-09-30"]


@pytest.mark.parametrize(
    "kwargs",
    [
        {"source": "finviz"},
        {"metrics": ["<script>"]},
        {"metrics": []},
        {"metrics": ["Revenue", "Revenue"]},
        {"end_date": "2027-01-01"},
        {"start_date": "2025-01-01", "end_date": "2024-01-01"},
    ],
)
def test_macrotrends_rejects_bad_arguments(adapter, provider, kwargs):
    kwargs.setdefault("source", "macrotrends")
    result = adapter.get_financial_statement("AAPL", **kwargs)
    assert result["error"]["code"] == "invalid_input"
    assert not provider.calls
    if kwargs["source"] == "macrotrends":
        assert result["source"] == "macrotrends"


def test_macrotrends_window_is_not_limited_to_five_years(adapter):
    result = adapter.get_financial_statement(
        "AAPL", source="macrotrends", start_date="2010-01-01"
    )
    assert result["ok"]


MARGIN_EXPECTED = {
    "gross_margin": ("ttm_gross_profit", "gross_margin_pct", 195.20e9, 46.91, 46.68),
    "operating_margin": (
        "ttm_operating_income",
        "operating_margin_pct",
        133.05e9,
        31.97,
        31.87,
    ),
    "ebitda_margin": ("ttm_ebitda", "ebitda_margin_pct", 144.75e9, 34.78, 34.68),
    "pre_tax_margin": (
        "ttm_pre_tax_income",
        "pre_tax_margin_pct",
        132.73e9,
        31.89,
        31.81,
    ),
    "net_margin": ("ttm_net_income", "net_margin_pct", 112.01e9, 26.92, 24.30),
}


def test_margin_expectations_cover_every_dataset():
    assert set(MARGIN_EXPECTED) == set(MACROTRENDS_DATASETS) - {"key_ratios"}


@pytest.mark.parametrize("dataset", sorted(MARGIN_EXPECTED))
def test_margins(adapter, dataset):
    profit, margin, latest_profit, latest_pct, previous_pct = MARGIN_EXPECTED[dataset]
    result = adapter.get_margins_and_ratios("AAPL", dataset=dataset)
    assert result["ok"] and result["source"] == "macrotrends"
    assert result["columns"] == ["date", "ttm_revenue", profit, margin]
    # The empty spacer row Macrotrends puts first is dropped.
    assert [r["date"] for r in result["records"]] == ["2025-09-30", "2025-06-30"]
    latest, previous = result["records"]
    assert latest["ttm_revenue"] == 416160000000.0
    assert latest[profit] == pytest.approx(latest_profit, rel=1e-2)
    assert latest[margin] == pytest.approx(latest_pct, rel=1e-2)
    assert previous[margin] == pytest.approx(previous_pct, rel=1e-2)


def test_margins_reject_unknown_dataset(adapter):
    result = adapter.get_margins_and_ratios("AAPL", dataset="roe")
    assert result["error"]["code"] == "invalid_input"


def test_blocked_macrotrends_reports_provider_blocked(adapter, provider, monkeypatch):
    def blocked(frequency="annual"):
        raise ProviderBlockedError("https://www.macrotrends.net/secret", 403)

    monkeypatch.setattr(provider, "macrotrends_income_statement", blocked)
    result = adapter.get_financial_statement("AAPL", source="macrotrends")
    assert result["error"]["code"] == "provider_blocked"
    assert result["source"] == "macrotrends"
    assert "secret" not in str(result)


@pytest.mark.parametrize(
    "text, value",
    [
        ("$416.16B", 416.16e9),
        ("$1.2M", 1.2e6),
        ("-$5.00K", -5e3),
        ("$-5.00K", -5e3),
        ("$1,234", 1234.0),
        ("", None),
        ("n/a", None),
        (None, None),
        (12, 12.0),
    ],
)
def test_money(text, value):
    assert (
        _money(text) == pytest.approx(value)
        if value is not None
        else _money(text) is None
    )


@pytest.mark.parametrize(
    "text, value",
    [("31.97%", 31.97), ("-4.5%", -4.5), ("", None), ("x", None), (None, None)],
)
def test_percent(text, value):
    assert _percent(text) == value
