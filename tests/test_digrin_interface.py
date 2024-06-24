"""
Module to test the Digrin_Interface class
"""

import pandas as pd
import pytest

from stockdex.ticker import Ticker


@pytest.mark.parametrize(
    "ticker",
    [
        ("AAPL"),
        ("ASML"),
        ("CAT"),
        ("BAC"),
    ],
)
def test_digrin_dividend(ticker):
    ticker = Ticker(ticker=ticker)
    digrin_dividend = ticker.digrin_dividend

    # Check if the response is as expected
    assert isinstance(digrin_dividend, pd.DataFrame)
    assert digrin_dividend.shape[0] > 0
    assert digrin_dividend.shape[1] == 5


@pytest.mark.parametrize(
    "ticker",
    [
        ("AAPL"),
        ("MSFT"),
        ("ASML"),
        ("CAT"),
        ("BAC"),
    ],
)
def test_digrin_payout_ratio(ticker):
    ticker = Ticker(ticker=ticker)
    digrin_payout_ratio = ticker.digrin_payout_ratio

    # Check if the response is as expected
    assert isinstance(digrin_payout_ratio, pd.DataFrame)
    assert digrin_payout_ratio.shape[0] > 1
    assert digrin_payout_ratio.shape[1] == 2


@pytest.mark.parametrize(
    "ticker",
    [
        ("AAPL"),
        ("MSFT"),
        ("ASML"),
        ("CAT"),
        ("BAC"),
    ],
)
def test_digrin_stock_splits(ticker):
    ticker = Ticker(ticker=ticker)
    digrin_stock_splits = ticker.digrin_stock_splits

    # Check if the response is as expected
    assert isinstance(digrin_stock_splits, pd.DataFrame)
    assert digrin_stock_splits.shape[0] > 1
    assert digrin_stock_splits.shape[1] == 2


@pytest.mark.parametrize(
    "ticker",
    [
        ("AAPL"),
        ("MSFT"),
        ("ASML"),
        ("CAT"),
        ("BAC"),
    ],
)
def test_digrin_price(ticker):
    ticker = Ticker(ticker=ticker)
    digrin_price = ticker.digrin_price

    # Check if the response is as expected
    assert isinstance(digrin_price, pd.DataFrame)
    assert digrin_price.shape[0] > 1
    assert digrin_price.shape[1] == 3


@pytest.mark.parametrize(
    "ticker",
    [
        ("AAPL"),
        ("MSFT"),
        ("ASML"),
        ("CAT"),
        ("BAC"),
    ],
)
def test_digrin_assets_vs_liabilities(ticker):
    ticker = Ticker(ticker=ticker)
    digrin_assets_vs_liabilities = ticker.digrin_assets_vs_liabilities

    # Check if the response is as expected
    assert isinstance(digrin_assets_vs_liabilities, pd.DataFrame)
    assert digrin_assets_vs_liabilities.shape[0] > 1
    assert digrin_assets_vs_liabilities.shape[1] == 3
    assert "Assets" in digrin_assets_vs_liabilities.columns
    assert "Liabilities" in digrin_assets_vs_liabilities.columns
    assert "Date" in digrin_assets_vs_liabilities.columns
    assert digrin_assets_vs_liabilities.iloc[0]["Assets"] != ""


@pytest.mark.parametrize(
    "ticker",
    [
        ("AAPL"),
        ("MSFT"),
        ("ASML"),
        ("CAT"),
        ("BAC"),
    ],
)
def test_digrin_free_cash_flow(ticker):
    ticker = Ticker(ticker=ticker)
    digrin_free_cash_flow = ticker.digrin_free_cash_flow

    # Check if the response is as expected
    assert isinstance(digrin_free_cash_flow, pd.DataFrame)
    assert digrin_free_cash_flow.shape[0] > 1
    assert digrin_free_cash_flow.shape[1] == 3
    assert "Free Cash Flow" in digrin_free_cash_flow.columns
    assert "Date" in digrin_free_cash_flow.columns
    assert digrin_free_cash_flow.iloc[0]["Free Cash Flow"] != ""


@pytest.mark.parametrize(
    "ticker",
    [
        ("AAPL"),
        ("MSFT"),
        ("ASML"),
        ("CAT"),
        ("BAC"),
    ],
)
def test_digrin_net_income(ticker):
    ticker = Ticker(ticker=ticker)
    digrin_net_income = ticker.digrin_net_income

    # Check if the response is as expected
    assert isinstance(digrin_net_income, pd.DataFrame)
    assert digrin_net_income.shape[0] > 1
    assert digrin_net_income.shape[1] == 2
    assert "Net Income" in digrin_net_income.columns
    assert "Date" in digrin_net_income.columns
    assert digrin_net_income.iloc[0]["Net Income"] != ""


@pytest.mark.parametrize(
    "ticker",
    [
        ("AAPL"),
        ("MSFT"),
        ("ASML"),
        ("CAT"),
        ("BAC"),
    ],
)
def test_digrin_cash_and_debt(ticker):
    ticker = Ticker(ticker=ticker)
    digrin_cash_and_debt = ticker.digrin_cash_and_debt

    # Check if the response is as expected
    assert isinstance(digrin_cash_and_debt, pd.DataFrame)
    assert digrin_cash_and_debt.shape[0] > 1
    assert digrin_cash_and_debt.shape[1] == 4
    assert "Cash" in digrin_cash_and_debt.columns
    assert "Debt" in digrin_cash_and_debt.columns
    assert "Date" in digrin_cash_and_debt.columns


@pytest.mark.parametrize(
    "ticker",
    [
        ("AAPL"),
        ("MSFT"),
        ("ASML"),
        ("CAT"),
        ("BAC"),
    ],
)
def test_digrin_shares_outstanding(ticker):
    ticker = Ticker(ticker=ticker)
    digrin_shares_outstanding = ticker.digrin_shares_outstanding

    # Check if the response is as expected
    assert isinstance(digrin_shares_outstanding, pd.DataFrame)
    assert digrin_shares_outstanding.shape[0] > 1
    assert digrin_shares_outstanding.shape[1] == 2
    assert "Shares Outstanding" in digrin_shares_outstanding.columns
    assert "Date" in digrin_shares_outstanding.columns
    assert digrin_shares_outstanding.iloc[0]["Shares Outstanding"] != ""


@pytest.mark.parametrize(
    "ticker",
    [
        ("AAPL"),
        ("MSFT"),
        ("ASML"),
        ("CAT"),
        ("BAC"),
    ],
)
def test_digrin_expenses(ticker):
    ticker = Ticker(ticker=ticker)
    digrin_expenses = ticker.digrin_expenses

    # Check if the response is as expected
    assert isinstance(digrin_expenses, pd.DataFrame)
    assert digrin_expenses.shape[0] > 1
    assert digrin_expenses.shape[1] == 5
    assert "Date" in digrin_expenses.columns


@pytest.mark.parametrize(
    "ticker",
    [
        ("AAPL"),
        ("MSFT"),
        ("ASML"),
        ("CAT"),
        ("BAC"),
    ],
)
def test_digrin_cost_of_revenue(ticker):
    ticker = Ticker(ticker=ticker)
    digrin_cost_of_revenue = ticker.digrin_cost_of_revenue

    # Check if the response is as expected
    assert isinstance(digrin_cost_of_revenue, pd.DataFrame)
    assert digrin_cost_of_revenue.shape[0] > 1
    assert digrin_cost_of_revenue.shape[1] == 3
    assert "Date" in digrin_cost_of_revenue.columns
    assert "Cost of Revenue" in digrin_cost_of_revenue.columns
    assert digrin_cost_of_revenue.iloc[0]["Cost of Revenue"] != ""


@pytest.mark.parametrize(
    "ticker",
    [
        ("AAPL"),
        ("MSFT"),
        ("ASML"),
        ("CAT"),
        ("BAC"),
    ],
)
def test_digrin_dgr3(ticker):
    ticker = Ticker(ticker=ticker)
    digrin_dgr3 = ticker.digrin_dgr3

    # Check if the response is as expected
    assert isinstance(digrin_dgr3, pd.DataFrame)
    assert digrin_dgr3.shape[0] > 1
    assert digrin_dgr3.shape[1] == 3
    assert "Year" in digrin_dgr3.columns


@pytest.mark.parametrize(
    "ticker",
    [
        ("AAPL"),
        ("MSFT"),
        ("CAT"),
        ("BAC"),
    ],
)
def test_digrin_dgr5(ticker):
    ticker = Ticker(ticker=ticker)
    digrin_dgr5 = ticker.digrin_dgr5

    # Check if the response is as expected
    assert isinstance(digrin_dgr5, pd.DataFrame)
    assert digrin_dgr5.shape[0] > 1
    assert digrin_dgr5.shape[1] == 3
    assert "Year" in digrin_dgr5.columns


@pytest.mark.parametrize(
    "ticker",
    [
        ("AAPL"),
        ("MSFT"),
        ("ASML"),
        ("CAT"),
        ("BAC"),
    ],
)
def test_digrin_dgr10(ticker):
    ticker = Ticker(ticker=ticker)
    digrin_dgr10 = ticker.digrin_dgr10

    # Check if the response is as expected
    assert isinstance(digrin_dgr10, pd.DataFrame)
    assert digrin_dgr10.shape[0] > 1
    assert digrin_dgr10.shape[1] == 3
    assert "Year" in digrin_dgr10.columns


@pytest.mark.parametrize(
    "ticker",
    [
        ("AAPL"),
        ("ASML"),
        ("CAT"),
        ("BAC"),
    ],
)
def test_digrin_upcoming_estimated_earnings(ticker):
    ticker = Ticker(ticker=ticker)
    digrin_upcoming_estimated_earnings = ticker.digrin_upcoming_estimated_earnings

    # Check if the response is as expected
    assert isinstance(digrin_upcoming_estimated_earnings, pd.DataFrame)
    assert digrin_upcoming_estimated_earnings.shape[0] >= 1
    assert digrin_upcoming_estimated_earnings.shape[1] == 5
    assert "Date" in digrin_upcoming_estimated_earnings.columns
