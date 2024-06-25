import pandas as pd
import pytest

from stockdex.ticker import Ticker


@pytest.mark.parametrize(
    "ticker",
    [
        ("PANW"),
        ("BAC"),
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
        ("PANW"),
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
        ("BAC"),
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


@pytest.mark.parametrize(
    "ticker",
    [
        ("PANW"),
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
