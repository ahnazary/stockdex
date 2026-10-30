"""Offline tests for the deprecated yahoo_web_* aliases and their replacements."""

import warnings

import pandas as pd
import pytest

from stockdex import Ticker
from stockdex.yahoo_web_deprecated import REPLACEMENTS

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


@pytest.mark.parametrize("name", sorted(REPLACEMENTS))
def test_every_alias_warns_and_names_replacement(ticker, name):
    with pytest.warns(DeprecationWarning, match="removed in stockdex 2.0") as record:
        getattr(ticker, name)
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
        ("yahoo_web_summary", "yahoo_api_summary_detail"),
        ("yahoo_web_valuation_measures", "yahoo_api_valuation_measures"),
        ("yahoo_web_financial_highlights", "yahoo_api_financial_data"),
        ("yahoo_web_trading_information", "yahoo_api_key_statistics"),
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
