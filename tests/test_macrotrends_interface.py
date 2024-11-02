import os

import pandas as pd
import pytest

from stockdex.ticker import Ticker

skip_test = bool(os.getenv("SKIP_TEST", False))


@pytest.mark.parametrize(
    "ticker",
    [
        ("PANW"),
    ],
)
def test_macrotrends_income_statement(ticker):
    ticker = Ticker(ticker=ticker)
    macrotrends_income_statement = ticker.macrotrends_income_statement

    # Check if the response is as expected
    assert isinstance(macrotrends_income_statement, pd.DataFrame)
    assert macrotrends_income_statement.shape[0] > 0
    assert macrotrends_income_statement.shape[1] > 0
    assert "Revenue" in macrotrends_income_statement.index


@pytest.mark.parametrize(
    "ticker",
    [
        ("BAC"),
    ],
)
def test_macrotrends_balance_sheet(ticker):
    ticker = Ticker(ticker=ticker)
    macrotrends_balance_sheet = ticker.macrotrends_balance_sheet

    # Check if the response is as expected
    assert isinstance(macrotrends_balance_sheet, pd.DataFrame)
    assert macrotrends_balance_sheet.shape[0] > 0
    assert macrotrends_balance_sheet.shape[1] > 0
    assert "Total Assets" in macrotrends_balance_sheet.index


@pytest.mark.parametrize(
    "ticker",
    [
        ("PANW"),
    ],
)
def test_macrotrends_cash_flow(ticker):
    ticker = Ticker(ticker=ticker)
    macrotrends_cash_flow = ticker.macrotrends_cash_flow

    # Check if the response is as expected
    assert isinstance(macrotrends_cash_flow, pd.DataFrame)
    assert macrotrends_cash_flow.shape[0] > 0
    assert macrotrends_cash_flow.shape[1] > 0
    assert macrotrends_cash_flow.iloc[0][1] is not None


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
    "ticker, group_by",
    [
        ("AAPL", "field"),
        ("GOOGL", "timeframe"),
    ],
)
def test_plot_macrotrends_income_statement(ticker, group_by):
    ticker = Ticker(ticker=ticker)
    ticker.plot_macrotrends_income_statement(group_by=group_by)
    assert True


@pytest.mark.skipif(skip_test, reason="Skipping in GH action as it is visual")
@pytest.mark.parametrize(
    "ticker, group_by",
    [
        ("AAPL", "field"),
        ("GOOGL", "timeframe"),
    ],
)
def test_plot_macrotrends_balance_sheet(ticker, group_by):
    ticker = Ticker(ticker=ticker)
    ticker.plot_macrotrends_balance_sheet(group_by=group_by)


@pytest.mark.skipif(skip_test, reason="Skipping in GH action as it is visual")
@pytest.mark.parametrize(
    "ticker, group_by",
    [
        ("AAPL", "field"),
        ("GOOGL", "timeframe"),
    ],
)
def test_plot_macrotrends_cash_flow(ticker, group_by):
    ticker = Ticker(ticker=ticker)
    ticker.plot_macrotrends_cash_flow(group_by=group_by)
