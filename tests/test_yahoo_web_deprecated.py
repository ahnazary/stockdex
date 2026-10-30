"""Offline tests for the deprecated yahoo_web_* aliases and their replacements."""

import warnings
from datetime import datetime, timedelta

import pandas as pd
import pytest

from stockdex import Ticker
from stockdex.exceptions import WrongSecurityType
from stockdex.yahoo_web_deprecated import REPLACEMENTS, VALID_TYPES

FRAME = pd.DataFrame({"x": [1]})


@pytest.fixture
def ticker(monkeypatch):
    """A Ticker whose yahoo_api_* methods return canned data, no network."""
    ticker = Ticker("AAPL")
    calls = []

    def stub(name, value):
        def method(*args, **kwargs):
            calls.append((name, args, kwargs))
            return value

        monkeypatch.setattr(ticker, name, method)

    for name in (
        "yahoo_api_income_statement",
        "yahoo_api_balance_sheet",
        "yahoo_api_cash_flow",
        "yahoo_api_options_chain",
        "yahoo_api_officers",
        "yahoo_api_major_holders",
        "yahoo_api_institutional_holders",
        "yahoo_api_fund_holders",
        "yahoo_api_summary_detail",
        "yahoo_api_valuation_measures",
        "yahoo_api_financial_data",
        "yahoo_api_key_statistics",
        "yahoo_api_earnings_history",
    ):
        stub(name, FRAME)
    stub(
        "yahoo_api_profile",
        pd.DataFrame(
            {"AAPL": ["Apple designs phones.", 1, 2]},
            index=["longBusinessSummary", "auditRisk", "boardRisk"],
        ),
    )
    stub(
        "yahoo_api_market_price",
        pd.DataFrame(
            {"AAPL": ["Apple Inc.", "Apple"]}, index=["longName", "shortName"]
        ),
    )
    stub(
        "yahoo_api_earnings_trend",
        pd.DataFrame(
            {
                "period": ["0q"],
                "endDate": ["2026-12-31"],
                "growth": [0.1],
                "earningsEstimate_avg": [1.0],
                "revenueEstimate_avg": [2.0],
                "epsTrend_current": [3.0],
                "epsRevisions_upLast7days": [4],
            }
        ),
    )
    ticker.calls = calls
    return ticker


def _access(ticker, name):
    """Read a deprecated attribute, calling the one that is a method"""
    value = getattr(ticker, name)
    if name == "yahoo_web_financials_table":
        return value("https://finance.yahoo.com/quote/AAPL/financials")
    return value


@pytest.mark.parametrize("name", sorted(REPLACEMENTS))
def test_every_alias_warns_and_names_replacement(ticker, name):
    with pytest.warns(DeprecationWarning, match="removed in stockdex 2.0") as record:
        _access(ticker, name)
    message = str(record[0].message)
    assert name in message
    assert REPLACEMENTS[name].split("(")[0] in message


def test_warning_points_at_caller(ticker):
    with warnings.catch_warnings(record=True) as record:
        warnings.simplefilter("always")
        ticker.yahoo_web_cashflow
    assert record[0].filename == __file__


@pytest.mark.parametrize(
    "name, target",
    [
        ("yahoo_web_income_stmt", "yahoo_api_income_statement"),
        ("yahoo_web_balance_sheet", "yahoo_api_balance_sheet"),
        ("yahoo_web_cashflow", "yahoo_api_cash_flow"),
        ("yahoo_web_key_executives", "yahoo_api_officers"),
        ("yahoo_web_major_holders", "yahoo_api_major_holders"),
        ("yahoo_web_top_institutional_holders", "yahoo_api_institutional_holders"),
        ("yahoo_web_top_mutual_fund_holders", "yahoo_api_fund_holders"),
        ("yahoo_web_earnings_history", "yahoo_api_earnings_history"),
    ],
)
def test_frame_aliases_forward(ticker, name, target):
    with pytest.warns(DeprecationWarning):
        result = getattr(ticker, name)
    assert result is FRAME
    assert ticker.calls[-1][0] == target


@pytest.mark.parametrize("name, option_type", [("calls", "calls"), ("puts", "puts")])
def test_options_aliases(ticker, name, option_type):
    with pytest.warns(DeprecationWarning):
        getattr(ticker, f"yahoo_web_{name}")
    assert ticker.calls[-1] == (
        "yahoo_api_options_chain",
        (),
        {"option_type": option_type},
    )


def test_profile_text_aliases(ticker):
    with pytest.warns(DeprecationWarning):
        assert ticker.yahoo_web_description == "Apple designs phones."
    with pytest.warns(DeprecationWarning):
        governance = ticker.yahoo_web_corporate_governance
    assert governance == "auditRisk: 1\nboardRisk: 2"


def test_full_name_strips_punctuation(ticker):
    with pytest.warns(DeprecationWarning):
        assert ticker.yahoo_web_full_name == "Apple Inc"


@pytest.mark.parametrize(
    "name, column",
    [
        ("yahoo_web_earnings_estimate", "earningsEstimate_avg"),
        ("yahoo_web_revenue_estimate", "revenueEstimate_avg"),
        ("yahoo_web_eps_trend", "epsTrend_current"),
        ("yahoo_web_eps_revisions", "epsRevisions_upLast7days"),
        ("yahoo_web_growth_estimates", "growth"),
    ],
)
def test_earnings_trend_slices(ticker, name, column):
    with pytest.warns(DeprecationWarning):
        frame = getattr(ticker, name)
    assert list(frame.columns) == ["period", "endDate", column]


def test_company_name(ticker):
    assert ticker.yahoo_api_company_name() == "Apple Inc."


@pytest.mark.parametrize(
    "index, values, expected",
    [
        (["shortName"], ["Apple"], "Apple"),
        (["longName", "shortName"], [None, "Apple"], "Apple"),
        (["regularMarketPrice"], [1.0], "AAPL"),
    ],
)
def test_company_name_fallbacks(monkeypatch, index, values, expected):
    ticker = Ticker("AAPL")
    monkeypatch.setattr(
        ticker,
        "yahoo_api_market_price",
        lambda: pd.DataFrame({"AAPL": values}, index=index),
    )
    assert ticker.yahoo_api_company_name() == expected


def test_macrotrends_full_name_uses_api(monkeypatch):
    ticker = Ticker("BRK-B")
    monkeypatch.setattr(
        ticker, "yahoo_api_company_name", lambda: "Berkshire Hathaway Inc."
    )
    with warnings.catch_warnings():
        warnings.simplefilter("error", DeprecationWarning)
        assert ticker.full_name == "berkshire-hathaway-inc"


def test_scraper_module_removed():
    with pytest.raises(ModuleNotFoundError):
        __import__("stockdex.yahoo_web_interface")


def _record(**values):
    return pd.DataFrame({"AAPL": list(values.values())}, index=list(values))


def test_summary_combines_price_and_detail(ticker, monkeypatch):
    monkeypatch.setattr(
        ticker,
        "yahoo_api_market_price",
        lambda: _record(regularMarketPrice=200.0, marketState="REGULAR", marketCap=1),
    )
    monkeypatch.setattr(
        ticker,
        "yahoo_api_summary_detail",
        lambda: _record(previousClose=199.0, marketCap=2),
    )
    with pytest.warns(DeprecationWarning):
        frame = ticker.yahoo_web_summary
    assert list(frame.index) == [
        "regularMarketPrice",
        "marketState",
        "marketCap",
        "previousClose",
    ]
    assert frame.loc["marketCap", "AAPL"] == 1


def test_financial_highlights_include_dates(ticker, monkeypatch):
    monkeypatch.setattr(
        ticker, "yahoo_api_financial_data", lambda: _record(totalRevenue=10)
    )
    monkeypatch.setattr(
        ticker,
        "yahoo_api_key_statistics",
        lambda: _record(lastFiscalYearEnd="2025-09-27", mostRecentQuarter="q", beta=1),
    )
    with pytest.warns(DeprecationWarning):
        frame = ticker.yahoo_web_financial_highlights
    assert list(frame.index) == [
        "totalRevenue",
        "lastFiscalYearEnd",
        "mostRecentQuarter",
    ]


def test_trading_information_includes_52_week_range(ticker, monkeypatch):
    monkeypatch.setattr(
        ticker, "yahoo_api_key_statistics", lambda: _record(sharesOutstanding=5)
    )
    monkeypatch.setattr(
        ticker,
        "yahoo_api_summary_detail",
        lambda: _record(fiftyTwoWeekHigh=250, fiftyTwoWeekLow=150, open=1),
    )
    with pytest.warns(DeprecationWarning):
        frame = ticker.yahoo_web_trading_information
    assert list(frame.index) == [
        "sharesOutstanding",
        "fiftyTwoWeekHigh",
        "fiftyTwoWeekLow",
    ]


def test_valuation_measures_add_current_row(ticker, monkeypatch):
    def valuation(frequency="quarterly"):
        if frequency == "trailing":
            return pd.DataFrame(
                {"trailingPeRatio": [30.0, 31.0]}, index=["2026-10-01", "2026-10-29"]
            )
        return pd.DataFrame({"quarterlyPeRatio": [28.0]}, index=["2026-06-30"])

    monkeypatch.setattr(ticker, "yahoo_api_valuation_measures", valuation)
    with pytest.warns(DeprecationWarning):
        frame = ticker.yahoo_web_valuation_measures
    assert list(frame.index) == ["2026-06-30", "Current"]
    assert frame.loc["Current", "quarterlyPeRatio"] == 31.0


def test_valuation_measures_without_trailing_data(ticker, monkeypatch):
    history = pd.DataFrame({"quarterlyPeRatio": [28.0]}, index=["2026-06-30"])
    monkeypatch.setattr(
        ticker,
        "yahoo_api_valuation_measures",
        lambda frequency="quarterly": (
            pd.DataFrame() if frequency == "trailing" else history
        ),
    )
    with pytest.warns(DeprecationWarning):
        assert ticker.yahoo_web_valuation_measures is history


@pytest.mark.parametrize(
    "url, target",
    [
        ("https://finance.yahoo.com/quote/AAPL/financials", "income_statement"),
        ("https://finance.yahoo.com/quote/AAPL/balance-sheet/", "balance_sheet"),
        ("https://finance.yahoo.com/quote/AAPL/cash-flow?p=AAPL", "cash_flow"),
    ],
)
def test_financials_table_dispatches_by_url(ticker, url, target):
    with pytest.warns(DeprecationWarning):
        assert ticker.yahoo_web_financials_table(url, "quarterly") is FRAME
    assert ticker.calls[-1] == (
        f"yahoo_api_{target}",
        (),
        {"frequency": "quarterly"},
    )


@pytest.mark.parametrize(
    "url, frequency",
    [
        ("https://finance.yahoo.com/quote/AAPL/profile", "annual"),
        ("https://finance.yahoo.com/quote/AAPL/financials", "monthly"),
    ],
)
def test_financials_table_rejects_unsupported(ticker, url, frequency):
    with pytest.warns(DeprecationWarning), pytest.raises(ValueError):
        ticker.yahoo_web_financials_table(url, frequency)


@pytest.mark.parametrize("name", sorted(VALID_TYPES))
def test_security_type_checks_kept(ticker, name):
    ticker.security_type = "fund"
    with pytest.warns(DeprecationWarning), pytest.raises(WrongSecurityType):
        getattr(ticker, name)


def test_options_allowed_for_etfs(ticker):
    ticker.security_type = "etf"
    with pytest.warns(DeprecationWarning):
        ticker.yahoo_web_calls
    with pytest.warns(DeprecationWarning), pytest.raises(WrongSecurityType):
        ticker.yahoo_web_income_stmt


def test_description_has_no_type_check(ticker):
    ticker.security_type = "etf"
    with pytest.warns(DeprecationWarning):
        assert ticker.yahoo_web_description == "Apple designs phones."


def test_statement_dates_resolved_per_call(monkeypatch):
    ticker = Ticker("AAPL")
    urls = []

    class Response:
        def json(self):
            return {"timeseries": {"result": []}}

    monkeypatch.setattr(
        ticker, "get_response", lambda url: urls.append(url) or Response()
    )
    before = datetime.today()
    ticker.yahoo_api_income_statement()
    params = dict(p.split("=") for p in urls[-1].split("?", 1)[1].split("&"))
    # build_url reads naive datetimes as UTC, so read them back the same way
    period2 = pd.Timestamp(int(params["period2"]), unit="s").to_pydatetime()
    period1 = pd.Timestamp(int(params["period1"]), unit="s").to_pydatetime()
    assert abs(period2 - before) < timedelta(minutes=1)
    assert 365 * 5 - 2 <= (period2 - period1).days <= 365 * 5 + 2
