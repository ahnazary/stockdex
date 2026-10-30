"""Offline tests for the Finviz tools: revenue breakdown, insiders, earnings."""

import pandas as pd
import pytest

from stockdex.claude_adapter import _finviz_date
from stockdex.exceptions import LayoutChangedError


@pytest.mark.parametrize("dataset", ["segment", "region", "product"])
def test_revenue_breakdown(adapter, dataset):
    result = adapter.get_revenue_breakdown("AAPL", dataset=dataset)
    assert result["ok"] and result["source"] == "finviz"
    assert result["columns"] == ["fiscal_year", "period_end", dataset, "revenue"]
    # Newest year first, largest category first; zero placeholders are dropped.
    assert result["records"] == [
        {
            "fiscal_year": 2025,
            "period_end": "2025-09-27",
            dataset: "Americas",
            "revenue": 178353000000.0,
        },
        {
            "fiscal_year": 2024,
            "period_end": "2024-09-28",
            dataset: "Americas",
            "revenue": 167045000000.0,
        },
        {
            "fiscal_year": 2024,
            "period_end": "2024-09-28",
            dataset: "Europe",
            "revenue": 101328000000.0,
        },
    ]


def test_revenue_breakdown_empty_is_no_data(adapter, provider, monkeypatch):
    monkeypatch.setattr(provider, "finviz_revenue_by_segment", lambda: {})
    assert adapter.get_revenue_breakdown("AAPL")["error"]["code"] == "no_data"


def test_revenue_breakdown_layout_change(adapter, provider, monkeypatch):
    monkeypatch.setattr(
        provider,
        "finviz_revenue_by_segment",
        lambda: {"x": pd.DataFrame({"year": [1]})},
    )
    assert adapter.get_revenue_breakdown("AAPL")["error"]["code"] == "layout_changed"


def test_revenue_breakdown_rejects_dataset(adapter):
    result = adapter.get_revenue_breakdown("AAPL", dataset="customer")
    assert result["error"]["code"] == "invalid_input"


def test_insider_trades(adapter):
    result = adapter.get_insider_trades("AAPL")
    assert result["ok"] and result["source"] == "finviz"
    assert result["records"][0] == {
        "date": "2026-10-27",
        "insider": "Newstead Jennifer",
        "relationship": "SVP, GC",
        "transaction": "Proposed Sale",
        "price": 343.36,
        "shares": 2399.0,
        "value_usd": 823721.0,
        "shares_held_after": None,
        "filed": "Oct 29 06:30 PM",
    }
    assert result["records"][1]["date"] == "2026-10-20"
    assert any("not instructions" in w for w in result["warnings"])


def test_insider_trades_layout_change(adapter, provider, monkeypatch):
    frame = provider.finviz_get_insider_trading().assign(Date="2026-10-27")
    monkeypatch.setattr(provider, "finviz_get_insider_trading", lambda: frame)
    assert adapter.get_insider_trades("AAPL")["error"]["code"] == "layout_changed"


@pytest.mark.parametrize(
    "column", ["#Shares", "Value ($)", "#Shares Total", "SEC Form 4"]
)
def test_insider_trades_missing_column_is_layout_change(
    adapter, provider, monkeypatch, column
):
    frame = provider.finviz_get_insider_trading().drop(columns=[column])
    monkeypatch.setattr(provider, "finviz_get_insider_trading", lambda: frame)
    assert adapter.get_insider_trades("AAPL")["error"]["code"] == "layout_changed"


@pytest.mark.parametrize(
    "text, iso",
    [("Oct 27 '26", "2026-10-27"), ("Jan 02 '25", "2025-01-02")],
)
def test_finviz_date(text, iso):
    assert _finviz_date(text) == iso


@pytest.mark.parametrize("text", ["27 Oct 2026", "Foo 27 '26", ""])
def test_finviz_date_rejects(text):
    with pytest.raises(LayoutChangedError):
        _finviz_date(text)


def test_price_reaction(adapter):
    result = adapter.get_earnings_reaction("AAPL")
    assert result["ok"] and result["source"] == "finviz"
    newest, previous = result["records"]
    assert newest["report_date"] == "2026-11-02"
    assert newest["open_pct"] is None
    assert previous == {
        "fiscal_period": "2026Q3",
        "report_date": "2026-07-30",
        "day_before_pct": -1.41,
        "day_before_vs_spy_pct": -3.08,
        "open_pct": -8.58,
        "open_vs_spy_pct": -8.99,
        "day_after_close_pct": -7.35,
        "day_after_close_vs_spy_pct": -8.07,
        "one_week_pct": 2.1,
        "one_week_vs_spy_pct": 1.1,
        "one_month_pct": None,
        "one_month_vs_spy_pct": None,
    }


def test_surprises(adapter):
    result = adapter.get_earnings_reaction("AAPL", dataset="surprises")
    assert result["ok"]
    upcoming, reported = result["records"]
    assert upcoming["fiscal_period"] == "2026Q4"
    assert upcoming["eps_actual"] is None and upcoming["eps_surprise_pct"] is None
    assert reported["eps_actual"] == 2.02
    assert reported["eps_surprise_pct"] == 6.77
    assert reported["revenue_actual"] == 109417.0


@pytest.mark.parametrize(
    "column", ["salesActual", "salesEstimate", "earningsDate", "epsAnalysts"]
)
def test_surprises_missing_column_is_layout_change(
    adapter, provider, monkeypatch, column
):
    frame = provider.finviz_earnings_data().drop(columns=[column])
    monkeypatch.setattr(provider, "finviz_earnings_data", lambda: frame)
    result = adapter.get_earnings_reaction("AAPL", dataset="surprises")
    assert result["error"]["code"] == "layout_changed"


def test_revisions_keep_latest_per_period(adapter):
    result = adapter.get_earnings_reaction("AAPL", dataset="revisions")
    assert result["ok"]
    assert [(r["estimate"], r["as_of"]) for r in result["records"]] == [
        ("eps", "2026-10-30"),
        ("revenue", "2026-10-30"),
    ]
    assert result["records"] == [
        {
            "fiscal_period": "2026Q4",
            "estimate": "eps",
            "as_of": "2026-10-30",
            "mean": 1.9897,
            "high": 2.1,
            "low": 1.9,
            "analysts": 28,
            "up_revisions": 3,
            "down_revisions": 0,
        },
        {
            "fiscal_period": "2026Q4",
            "estimate": "revenue",
            "as_of": "2026-10-30",
            "mean": 113401.2137,
            "high": 117628.0,
            "low": 112525.022,
            "analysts": 26,
            "up_revisions": 1,
            "down_revisions": 2,
        },
    ]


@pytest.mark.parametrize(
    "column", ["high", "low", "estimates", "upRevisions", "downRevisions"]
)
def test_revisions_missing_column_is_layout_change(
    adapter, provider, monkeypatch, column
):
    frame = provider.finviz_earnings_revisions_data().drop(columns=[column])
    monkeypatch.setattr(provider, "finviz_earnings_revisions_data", lambda: frame)
    result = adapter.get_earnings_reaction("AAPL", dataset="revisions")
    assert result["error"]["code"] == "layout_changed"


def test_revisions_latest_row_keeps_its_nulls(adapter, provider, monkeypatch):
    frame = provider.finviz_earnings_revisions_data()
    # The newest EPS snapshot has no high or revision counts.
    frame.loc[1, ["high", "upRevisions"]] = [float("nan"), float("nan")]
    monkeypatch.setattr(provider, "finviz_earnings_revisions_data", lambda: frame)
    result = adapter.get_earnings_reaction("AAPL", dataset="revisions")
    eps = result["records"][0]
    assert eps["as_of"] == "2026-10-30" and eps["mean"] == 1.9897
    # Not filled in from the older 2026-10-26 snapshot.
    assert eps["high"] is None and eps["up_revisions"] is None


def test_earnings_reaction_rejects_dataset(adapter):
    result = adapter.get_earnings_reaction("AAPL", dataset="guidance")
    assert result["error"]["code"] == "invalid_input"


def test_earnings_reaction_layout_change(adapter, provider, monkeypatch):
    frame = pd.DataFrame(
        {"fiscalPeriod": ["2026Q3"], "reportDate": ["2026-07-30"], "reactions": ["x"]}
    )
    monkeypatch.setattr(
        provider, "finviz_price_reaction_to_earnings_report", lambda: frame
    )
    assert adapter.get_earnings_reaction("AAPL")["error"]["code"] == "layout_changed"


def test_revision_type_names():
    from stockdex.claude_adapter import _REVISION_TYPES

    assert _REVISION_TYPES == {"E": "eps", "R": "eps_reported", "S": "revenue"}
