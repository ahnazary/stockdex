import os

import pandas as pd
import pytest

from stockdex.ticker import Ticker

skip_test = bool(os.getenv("SKIP_TEST", False))


@pytest.mark.parametrize(
    "ticker, frequency",
    [
        ("PANW", "quarterly"),
        ("PANW", "annual"),
        ("BAC", "annual"),
        ("BAC", "quarterly"),
    ],
)
def test_macrotrends_income_statement(ticker, frequency):
    ticker = Ticker(ticker=ticker)
    macrotrends_income_statement = ticker.macrotrends_income_statement(
        frequency=frequency
    )

    # Check if the response is as expected
    assert isinstance(macrotrends_income_statement, pd.DataFrame)
    assert macrotrends_income_statement.shape[0] > 0
    assert macrotrends_income_statement.shape[1] > 0
    assert "Revenue" in macrotrends_income_statement.index
    assert "Gross Profit" in macrotrends_income_statement.index
    assert "Operating Income" in macrotrends_income_statement.index
    if frequency == "quarterly":
        assert macrotrends_income_statement.shape[1] > 28
    else:
        assert macrotrends_income_statement.shape[1] > 6


@pytest.mark.skipif(
    skip_test, reason="Skipping in GH action as it reaches the limit of requests"
)
@pytest.mark.parametrize(
    "ticker, frequency",
    [
        ("BAC", "quarterly"),
        ("BAC", "annual"),
    ],
)
def test_macrotrends_balance_sheet(ticker, frequency):
    ticker = Ticker(ticker=ticker)
    macrotrends_balance_sheet = ticker.macrotrends_balance_sheet(frequency=frequency)

    # Check if the response is as expected
    assert isinstance(macrotrends_balance_sheet, pd.DataFrame)
    assert macrotrends_balance_sheet.shape[0] > 0
    assert macrotrends_balance_sheet.shape[1] > 0
    assert "Total Assets" in macrotrends_balance_sheet.index
    if frequency == "quarterly":
        assert macrotrends_balance_sheet.shape[1] > 28
    else:
        assert macrotrends_balance_sheet.shape[1] > 6


@pytest.mark.skipif(
    skip_test, reason="Skipping in GH action as it reaches the limit of requests"
)
@pytest.mark.parametrize(
    "ticker, frequency",
    [
        ("PANW", "quarterly"),
        ("PANW", "annual"),
    ],
)
def test_macrotrends_cash_flow(ticker, frequency):
    ticker = Ticker(ticker=ticker)
    macrotrends_cash_flow = ticker.macrotrends_cash_flow(frequency=frequency)

    # Check if the response is as expected
    assert isinstance(macrotrends_cash_flow, pd.DataFrame)
    assert macrotrends_cash_flow.shape[0] > 0
    assert macrotrends_cash_flow.shape[1] > 0
    assert macrotrends_cash_flow.iloc[0][1] is not None
    if frequency == "quarterly":
        assert macrotrends_cash_flow.shape[1] > 28
    else:
        assert macrotrends_cash_flow.shape[1] > 6


@pytest.mark.skipif(
    skip_test, reason="Skipping in GH action as it reaches the limit of requests"
)
@pytest.mark.parametrize(
    "ticker",
    [
        ("BAC"),
    ],
)
def test_macrotrends_key_financial_ratios(ticker):
    ticker = Ticker(ticker=ticker)
    macrotrends_key_financial_ratios = ticker.macrotrends_key_financial_ratios

    # Check if the response is as expected
    assert isinstance(macrotrends_key_financial_ratios, pd.DataFrame)
    assert macrotrends_key_financial_ratios.shape[0] > 0
    assert macrotrends_key_financial_ratios.shape[1] > 0
    assert "Current Ratio" in macrotrends_key_financial_ratios.index


@pytest.mark.skipif(
    skip_test, reason="Skipping in GH action as it reaches the limit of requests"
)
@pytest.mark.parametrize(
    "ticker",
    [
        ("PANW"),
    ],
)
def test_macrotrends_gross_margin(ticker):
    ticker = Ticker(ticker=ticker)
    macrotrends_gross_margin = ticker.macrotrends_gross_margin

    # Check if the response is as expected
    assert isinstance(macrotrends_gross_margin, pd.DataFrame)
    assert macrotrends_gross_margin.shape[0] > 0
    assert macrotrends_gross_margin.shape[1] > 0


@pytest.mark.skipif(
    skip_test, reason="Skipping in GH action as it reaches the limit of requests"
)
@pytest.mark.parametrize(
    "ticker",
    [
        ("BAC"),
    ],
)
def test_macrotrends_operating_margin(ticker):
    ticker = Ticker(ticker=ticker)
    macrotrends_operating_margin = ticker.macrotrends_operating_margin

    # Check if the response is as expected
    assert isinstance(macrotrends_operating_margin, pd.DataFrame)
    assert macrotrends_operating_margin.shape[0] > 0
    assert macrotrends_operating_margin.shape[1] > 0


@pytest.mark.skipif(
    skip_test, reason="Skipping in GH action as it reaches the limit of requests"
)
@pytest.mark.parametrize(
    "ticker",
    [
        ("BAC"),
    ],
)
def test_macrotrends_ebitda_margin(ticker):
    ticker = Ticker(ticker=ticker)
    macrotrends_ebitda_margin = ticker.macrotrends_ebitda_margin

    # Check if the response is as expected
    assert isinstance(macrotrends_ebitda_margin, pd.DataFrame)
    assert macrotrends_ebitda_margin.shape[0] > 0
    assert macrotrends_ebitda_margin.shape[1] > 0


@pytest.mark.skipif(
    skip_test, reason="Skipping in GH action as it reaches the limit of requests"
)
@pytest.mark.parametrize(
    "ticker",
    [
        ("BAC"),
    ],
)
def test_macrotrends_pre_tax_margin(ticker):
    ticker = Ticker(ticker=ticker)
    macrotrends_pre_tax_margin = ticker.macrotrends_pre_tax_margin

    # Check if the response is as expected
    assert isinstance(macrotrends_pre_tax_margin, pd.DataFrame)
    assert macrotrends_pre_tax_margin.shape[0] > 0
    assert macrotrends_pre_tax_margin.shape[1] > 0


@pytest.mark.skipif(
    skip_test, reason="Skipping in GH action as it reaches the limit of requests"
)
@pytest.mark.parametrize(
    "ticker",
    [
        ("BAC"),
    ],
)
def test_macrotrends_net_margin(ticker):
    ticker = Ticker(ticker=ticker)
    macrotrends_net_margin = ticker.macrotrends_net_margin

    # Check if the response is as expected
    assert isinstance(macrotrends_net_margin, pd.DataFrame)
    assert macrotrends_net_margin.shape[0] > 0
    assert macrotrends_net_margin.shape[1] > 0


@pytest.mark.skipif(skip_test, reason="Skipping in GH action as it is visual")
@pytest.mark.parametrize(
    "ticker, group_by, frequency",
    [
        ("AAPL", "field", "quarterly"),
        ("GOOGL", "timeframe", "annual"),
        ("GOOGL", "timeframe", "quarterly"),
    ],
)
def test_plot_macrotrends_income_statement(ticker, group_by, frequency):
    ticker = Ticker(ticker=ticker)
    ticker.plot_macrotrends_income_statement(group_by=group_by, frequency=frequency)
    assert True


@pytest.mark.skipif(skip_test, reason="Skipping in GH action as it is visual")
@pytest.mark.parametrize(
    "ticker, group_by, frequency",
    [
        ("AAPL", "field", "quarterly"),
        ("GOOGL", "timeframe", "annual"),
        ("GOOGL", "timeframe", "quarterly"),
    ],
)
def test_plot_macrotrends_balance_sheet(ticker, group_by, frequency):
    ticker = Ticker(ticker=ticker)
    ticker.plot_macrotrends_balance_sheet(group_by=group_by, frequency=frequency)


@pytest.mark.skipif(skip_test, reason="Skipping in GH action as it is visual")
@pytest.mark.parametrize(
    "ticker, group_by, frequency",
    [
        ("AAPL", "field", "quarterly"),
        ("GOOGL", "timeframe", "annual"),
        ("GOOGL", "timeframe", "quarterly"),
    ],
)
def test_plot_macrotrends_cash_flow(ticker, group_by, frequency):
    ticker = Ticker(ticker=ticker)
    ticker.plot_macrotrends_cash_flow(group_by=group_by, frequency=frequency)


@pytest.mark.skipif(
    skip_test, reason="Skipping in GH action as it reaches the limit of requests"
)
@pytest.mark.parametrize(
    "ticker, frequency",
    [
        ("PANW", "annual"),
        ("GOOGL", "quarterly"),
    ],
)
def test_macrotrends_revenue(ticker, frequency):
    ticker = Ticker(ticker)
    macrotrends_revenue = ticker.macrotrends_revenue(frequency=frequency)

    # Check if the response is as expected
    assert isinstance(macrotrends_revenue, pd.DataFrame)
    assert macrotrends_revenue.shape[0] > 0
    assert macrotrends_revenue.shape[1] > 0
