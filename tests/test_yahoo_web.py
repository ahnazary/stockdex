"""
Module to test the YahooWeb class.
"""

import pandas as pd
import pytest

from stockdex.exceptions import WrongSecurityType
from stockdex.ticker import Ticker


@pytest.mark.parametrize(
    "ticker",
    [
        ("AAPL"),
        ("GOOGL"),
        ("MSFT"),
    ],
)
def test_cashflow_web(ticker):
    ticker = Ticker(ticker)
    cashflow_web_df = ticker.cashflow_web

    # Check if the response is as expected
    assert isinstance(cashflow_web_df, pd.DataFrame)
    assert cashflow_web_df.shape[0] >= 3
    assert cashflow_web_df.shape[1] > 5


def test_cashflow_web_wrong_security_type():
    with pytest.raises(WrongSecurityType):
        ticker = Ticker(isin="AAPL", security_type="etf")
        ticker.cashflow_web


@pytest.mark.parametrize(
    "ticker",
    [("AAPL"), ("GOOGL"), ("TSLA")],
)
def test_balance_sheet_web(ticker):
    ticker = Ticker(ticker)
    balance_sheet_web_df = ticker.balance_sheet_web

    # Check if the response is as expected
    assert isinstance(balance_sheet_web_df, pd.DataFrame)
    assert balance_sheet_web_df.shape[0] >= 3
    assert balance_sheet_web_df.shape[1] > 5


def test_balance_sheet_web_wrong_security_type():
    with pytest.raises(WrongSecurityType):
        ticker = Ticker(isin="AAPL", security_type="etf")
        ticker.balance_sheet_web


@pytest.mark.parametrize(
    "ticker",
    [("AAPL"), ("GOOGL"), ("TSLA")],
)
def test_income_stmt_web(ticker):
    ticker = Ticker(ticker)
    income_stmt_web_df = ticker.income_stmt_web

    # Check if the response is as expected
    assert isinstance(income_stmt_web_df, pd.DataFrame)
    assert income_stmt_web_df.shape[0] >= 3
    assert income_stmt_web_df.shape[1] > 5


def test_income_stmt_web_wrong_security_type():
    with pytest.raises(WrongSecurityType):
        ticker = Ticker(isin="AAPL", security_type="etf")
        ticker.income_stmt_web
