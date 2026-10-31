"""Offline tests for how scraped sources report blocked requests and layout changes."""

import json
from types import SimpleNamespace

import pandas as pd
import pytest

from stockdex import Ticker
from stockdex.exceptions import (
    LayoutChangedError,
    NoDataError,
    ProviderBlockedError,
    RateLimitError,
)
from stockdex.ticker_base import TickerBase


def page(html):
    return SimpleNamespace(
        content=html.encode(), text=html, url="https://x/AAPL/apple/"
    )


def serve(monkeypatch, ticker, html):
    monkeypatch.setattr(ticker, "get_response", lambda url: page(html))
    return ticker


# -- TickerBase -------------------------------------------------------------


def fake_session(monkeypatch, statuses):
    calls = []

    def get(*args, **kwargs):
        calls.append(args)
        status = statuses[min(len(calls), len(statuses)) - 1]
        return SimpleNamespace(status_code=status, headers={})

    monkeypatch.setattr(TickerBase, "session", SimpleNamespace(get=get))
    monkeypatch.setattr(TickerBase, "_external_request_delay", 0)
    return calls


def test_persistent_403_raises_provider_blocked(monkeypatch):
    calls = fake_session(monkeypatch, [403])
    base = TickerBase()
    base.forbidden_retries, base.forbidden_retry_delay = 2, 0

    with pytest.raises(ProviderBlockedError) as error:
        base.get_response("https://www.macrotrends.net/x")

    assert error.value.status_code == 403
    # Message keeps the old form so callers matching "status 403" still work.
    assert "status 403" in str(error.value)
    assert isinstance(error.value, RuntimeError)
    assert len(calls) == 3


def test_403_then_200_recovers(monkeypatch):
    fake_session(monkeypatch, [403, 200])
    base = TickerBase()
    base.forbidden_retry_delay = 0
    assert base.get_response("https://finviz.com/x").status_code == 200


def test_403_then_429_is_rate_limit(monkeypatch):
    fake_session(monkeypatch, [403, 429])
    base = TickerBase()
    base.forbidden_retry_delay = 0
    with pytest.raises(RateLimitError):
        base.get_response("https://finviz.com/x")


def test_401_is_blocked_without_retry(monkeypatch):
    calls = fake_session(monkeypatch, [401])
    with pytest.raises(ProviderBlockedError):
        TickerBase().get_response("https://finviz.com/x")
    assert len(calls) == 1


def test_other_status_is_plain_runtime_error(monkeypatch):
    fake_session(monkeypatch, [500])
    with pytest.raises(RuntimeError) as error:
        TickerBase().get_response("https://finviz.com/x")
    assert not isinstance(error.value, ProviderBlockedError)


# -- Macrotrends ------------------------------------------------------------

ROWS = [
    {
        "field_name": "<a href='/x'>Revenue</a>",
        "popup_icon": "<div></div>",
        "2025-09-30": "416161",
        "2024-09-30": "391035",
    },
    {
        "field_name": "<a href='/x'>Net Income</a>",
        "popup_icon": "<div></div>",
        "2025-09-30": "112010",
        "2024-09-30": None,
    },
]


def statement_page(rows=ROWS):
    data = json.dumps(rows).replace("/", "\\/")
    return f"<html><script>\n var originalData = {data};\n</script></html>"


def test_macrotrends_statement_parses_json(monkeypatch):
    ticker = serve(monkeypatch, Ticker("AAPL"), statement_page())
    frame = ticker.macrotrends_income_statement("annual")
    assert list(frame.index) == ["Revenue", "Net Income"]
    assert list(frame.columns) == ["2025-09-30", "2024-09-30"]
    assert frame.loc["Revenue", "2025-09-30"] == "416161"
    # Missing cells are None or NaN depending on the pandas version
    assert pd.isna(frame.loc["Net Income", "2024-09-30"])


def test_macrotrends_never_evaluates_page_code(monkeypatch):
    marker = []
    evil = "<script>var originalData = [__import__('builtins').print('x')];</script>"
    monkeypatch.setattr("builtins.print", lambda *a: marker.append(a))
    ticker = serve(monkeypatch, Ticker("AAPL"), evil)
    with pytest.raises(LayoutChangedError):
        ticker.macrotrends_balance_sheet("annual")
    assert marker == []


@pytest.mark.parametrize(
    "html",
    [
        "<html>Just a moment...</html>",
        "<script>var originalData = [1, 2];</script>",
        statement_page([{"no_field": 1}]),
    ],
)
def test_macrotrends_layout_changes(monkeypatch, html):
    ticker = serve(monkeypatch, Ticker("AAPL"), html)
    with pytest.raises(LayoutChangedError, match="Macrotrends"):
        ticker.macrotrends_cash_flow("annual")


def margin_page(header="TTM Operating Income"):
    return f"""
    <table>
      <thead><tr><th>Operating Margin</th></tr></thead>
      <thead><tr><th>Date</th><th>TTM Revenue</th><th>{header}</th>
      <th>Operating Margin</th></tr></thead>
      <tbody>
        <tr><td colspan="4"></td></tr>
        <tr><td>2025-09-30</td><td>$416.16B</td><td>$133.05B</td><td>31.97%</td></tr>
      </tbody>
    </table>"""


def test_macrotrends_margin_table(monkeypatch):
    frame = serve(
        monkeypatch, Ticker("AAPL"), margin_page()
    ).macrotrends_operating_margin
    assert list(frame.columns) == [
        "Date",
        "TTM Revenue",
        "TTM Operating Income",
        "Operating Margin",
    ]
    assert frame.to_dict(orient="records") == [
        {
            "Date": "2025-09-30",
            "TTM Revenue": "$416.16B",
            "TTM Operating Income": "$133.05B",
            "Operating Margin": "31.97%",
        }
    ]


def test_macrotrends_margin_missing(monkeypatch):
    ticker = serve(monkeypatch, Ticker("AAPL"), margin_page("Something else"))
    with pytest.raises(LayoutChangedError):
        ticker.macrotrends_operating_margin


def test_macrotrends_margin_rows_changed_width(monkeypatch):
    html = margin_page().replace("<td>31.97%</td>", "<td>31.97%</td><td>x</td>")
    ticker = serve(monkeypatch, Ticker("AAPL"), html)
    with pytest.raises(LayoutChangedError, match="no longer match its 4 columns"):
        ticker.macrotrends_operating_margin


def test_macrotrends_margin_only_spacers_is_empty(monkeypatch):
    html = margin_page().replace(
        "<tr><td>2025-09-30</td><td>$416.16B</td><td>$133.05B</td><td>31.97%</td></tr>",
        "",
    )
    assert serve(monkeypatch, Ticker("AAPL"), html).macrotrends_operating_margin.empty


def test_macrotrends_cache_is_per_instance(monkeypatch):
    first = serve(monkeypatch, Ticker("AAPL"), margin_page())
    assert first.macrotrends_operating_margin is first.macrotrends_operating_margin
    second = serve(monkeypatch, Ticker("AAPL"), margin_page())
    assert second.macrotrends_operating_margin is not first.macrotrends_operating_margin


def test_macrotrends_revenue_missing_table(monkeypatch):
    ticker = serve(monkeypatch, Ticker("AAPL"), "<html></html>")
    with pytest.raises(LayoutChangedError, match="annual revenue"):
        ticker.macrotrends_revenue("annual")


# -- Finviz -----------------------------------------------------------------


def route_page(data):
    return (
        '<html><script id="route-init-data" type="application/json">'
        f"{json.dumps(data)}</script></html>"
    )


def test_finviz_missing_route_data(monkeypatch):
    ticker = serve(monkeypatch, Ticker("AAPL"), "<html>blocked</html>")
    with pytest.raises(LayoutChangedError, match="route-init-data"):
        ticker.finviz_earnings_data()


def test_finviz_route_data_not_json(monkeypatch):
    html = '<script id="route-init-data">not json</script>'
    ticker = serve(monkeypatch, Ticker("AAPL"), html)
    with pytest.raises(LayoutChangedError, match="not JSON"):
        ticker.finviz_price_reaction_to_earnings_report()


@pytest.mark.parametrize(
    "method",
    [
        "finviz_earnings_data",
        "finviz_earnings_annual_data",
        "finviz_earnings_revisions_data",
        "finviz_price_reaction_to_earnings_report",
    ],
)
def test_finviz_empty_lists_are_empty_frames(monkeypatch, method):
    ticker = serve(monkeypatch, Ticker("AAPL"), route_page({}))
    assert getattr(ticker, method)().empty


@pytest.mark.parametrize("value", [{}, False, None, "x", [1, 2]])
def test_finviz_malformed_lists_are_layout_changes(monkeypatch, value):
    ticker = serve(monkeypatch, Ticker("AAPL"), route_page({"earningsData": value}))
    with pytest.raises(LayoutChangedError, match="list of records"):
        ticker.finviz_earnings_data()


def test_finviz_raw_data_cached_per_instance(monkeypatch):
    calls = []
    ticker = serve(monkeypatch, Ticker("AAPL"), route_page({"earningsData": []}))
    original = ticker.get_response
    monkeypatch.setattr(
        ticker, "get_response", lambda url: calls.append(url) or original(url)
    )
    ticker.finviz_earnings_data()
    ticker.finviz_earnings_annual_data()
    assert len(calls) == 1
    assert "_cache__finviz_earnings_reaction_raw_data" in vars(ticker)


def test_finviz_dividends_annual_empty(monkeypatch):
    ticker = serve(monkeypatch, Ticker("AAPL"), route_page({"dividendsAnnualData": []}))
    assert ticker.finviz_dividends_annual_data().empty


def test_finviz_overall_dividend_does_not_mutate_cache(monkeypatch):
    data = {"lastClose": 1.0, "dividendsData": [{"Exdate": "2026-01-01"}]}
    ticker = serve(monkeypatch, Ticker("AAPL"), route_page(data))
    assert list(ticker.finviz_overall_dividend().columns) == ["lastClose"]
    assert len(ticker.finviz_dividends_date_data()) == 1


def test_finviz_revenue_layout(monkeypatch):
    data = {
        "segment": {
            "revenues": {
                "Americas": [
                    {
                        "fiscal_year": "2025",
                        "report_end_date": "2025-09-27",
                        "value": 1.0,
                    }
                ]
            }
        }
    }
    ticker = serve(monkeypatch, Ticker("AAPL"), route_page(data))
    frames = ticker.finviz_revenue_by_segment()
    assert list(frames) == ["Americas"]
    assert isinstance(frames["Americas"], pd.DataFrame)
    assert ticker.finviz_revenue_by_regions() == {}


def test_finviz_insider_table_missing(monkeypatch):
    ticker = serve(monkeypatch, Ticker("AAPL"), "<html>Access denied</html>")
    with pytest.raises(LayoutChangedError, match="insider"):
        ticker.finviz_get_insider_trading()


# -- Digrin -----------------------------------------------------------------


def test_digrin_table_missing_is_no_data(monkeypatch):
    ticker = serve(monkeypatch, Ticker("AAPL"), "<html></html>")
    with pytest.raises(NoDataError):
        ticker.digrin_payout_ratio


def test_digrin_table_without_body_is_layout_change(monkeypatch):
    html = "<table><tr><td>Payout ratio</td></tr></table>"
    ticker = serve(monkeypatch, Ticker("AAPL"), html)
    with pytest.raises(LayoutChangedError, match="Digrin"):
        ticker.digrin_payout_ratio


def test_digrin_table_parses(monkeypatch):
    html = """<table><thead><tr><th>Date</th><th>Payout ratio</th><th>PE ratio</th>
    </tr></thead><tbody><tr><td>2026Q3 </td><td>13.55%</td><td>34.78</td></tr>
    <tr><td colspan="3">note</td></tr></tbody></table>"""
    frame = serve(monkeypatch, Ticker("AAPL"), html).digrin_payout_ratio
    assert frame.to_dict(orient="records") == [
        {"Date": "2026Q3 ", "Payout ratio": "13.55%", "PE ratio": "34.78"}
    ]


def test_digrin_rows_changed_width_is_layout_change(monkeypatch):
    html = """<table><thead><tr><th>Date</th><th>Payout ratio</th></tr></thead>
    <tbody><tr><td>2026Q3</td><td>13.55%</td><td>new</td></tr></tbody></table>"""
    ticker = serve(monkeypatch, Ticker("AAPL"), html)
    with pytest.raises(LayoutChangedError, match="no longer match its 2 columns"):
        ticker.digrin_payout_ratio


def test_digrin_empty_body_is_empty_frame(monkeypatch):
    html = """<table><thead><tr><th>Date</th><th>Payout ratio</th></tr></thead>
    <tbody></tbody></table>"""
    assert serve(monkeypatch, Ticker("AAPL"), html).digrin_payout_ratio.empty


def test_layout_changed_is_a_value_error():
    # Existing callers that catch ValueError for Digrin layout changes still work.
    assert issubclass(LayoutChangedError, ValueError)
