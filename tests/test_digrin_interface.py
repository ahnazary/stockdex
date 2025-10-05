"""
Module to test the Digrin_Interface class
"""

import os

import pandas as pd
import pytest

from stockdex.exceptions import NoDataError
from stockdex.ticker import Ticker

skip_test = bool(os.getenv("SKIP_TEST", False))


@pytest.mark.skipif(skip_test, reason="Skipping in GH action as it throws error 403")
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


@pytest.mark.skipif(skip_test, reason="Skipping in GH action as it throws error 403")
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


@pytest.mark.skipif(skip_test, reason="Skipping in GH action as it throws error 403")
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


@pytest.mark.skipif(skip_test, reason="Skipping in GH action as it throws error 403")
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


@pytest.mark.skipif(skip_test, reason="Skipping in GH action as it throws error 403")
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


@pytest.mark.skipif(skip_test, reason="Skipping in GH action as it throws error 403")
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


@pytest.mark.skipif(skip_test, reason="Skipping in GH action as it throws error 403")
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


@pytest.mark.skipif(skip_test, reason="Skipping in GH action as it throws error 403")
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


@pytest.mark.skipif(skip_test, reason="Skipping in GH action as it throws error 403")
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


@pytest.mark.skipif(skip_test, reason="Skipping in GH action as it throws error 403")
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


@pytest.mark.skipif(skip_test, reason="Skipping in GH action as it throws error 403")
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


@pytest.mark.skipif(skip_test, reason="Skipping in GH action as it throws error 403")
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


@pytest.mark.skipif(skip_test, reason="Skipping in GH action as it throws error 403")
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


@pytest.mark.skipif(skip_test, reason="Skipping in GH action as it throws error 403")
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


@pytest.mark.skipif(skip_test, reason="Skipping in GH action as it throws error 403")
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


@pytest.mark.skipif(skip_test, reason="Skipping in GH action as it is visual")
@pytest.mark.parametrize(
    "ticker",
    [
        ("AAPL"),
        ("CAT"),
    ],
)
def test_plot_digrin_price(ticker):
    ticker = Ticker(ticker=ticker)
    ticker.plot_digrin_price()
    assert True


@pytest.mark.skipif(skip_test, reason="Skipping in GH action as it is visual")
@pytest.mark.parametrize(
    "ticker",
    [("AAPL"), ("BAC")],
)
def test_plot_digrin_dividend(ticker):
    ticker = Ticker(ticker=ticker)
    ticker.plot_digrin_dividend()
    assert True


@pytest.mark.skipif(skip_test, reason="Skipping in GH action as it is visual")
@pytest.mark.parametrize(
    "ticker",
    [("AAPL"), ("BAC"), ("CAT"), ("ASML"), ("MSFT")],
)
def test_plot_digrin_assets_vs_liabilities(ticker):
    ticker = Ticker(ticker=ticker)
    ticker.plot_digrin_assets_vs_liabilities()
    assert True


@pytest.mark.skipif(skip_test, reason="Skipping in GH action as it is visual")
@pytest.mark.parametrize(
    "ticker",
    [("AAPL"), ("BAC"), ("CAT"), ("ASML"), ("MSFT"), ("PLTR")],
)
def test_plot_digrin_free_cash_flow(ticker):
    ticker = Ticker(ticker=ticker)
    ticker.plot_digrin_free_cash_flow()
    assert True


@pytest.mark.skipif(skip_test, reason="Skipping in GH action as it is visual")
@pytest.mark.parametrize(
    "ticker",
    [("AAPL"), ("BAC"), ("CAT"), ("ASML"), ("MSFT"), ("DHL.DE")],
)
def test_plot_digrin_net_income(ticker):
    ticker = Ticker(ticker=ticker)
    ticker.plot_digrin_net_income()
    assert True


@pytest.mark.skipif(skip_test, reason="Skipping in GH action as it throws error 403")
def test_plot_digrin_net_income_no_data():
    with pytest.raises(NoDataError):
        ticker = Ticker(ticker="PLTR")
        ticker.plot_digrin_net_income()


@pytest.mark.skipif(skip_test, reason="Skipping in GH action as it is visual")
@pytest.mark.parametrize(
    "ticker",
    [("AAPL"), ("BAC"), ("CAT"), ("ASML"), ("MSFT"), ("PLTR"), ("DHL.DE")],
)
def test_plot_digrin_cash_and_debt(ticker):
    ticker = Ticker(ticker=ticker)
    ticker.plot_digrin_cash_and_debt()
    assert True


@pytest.mark.skipif(skip_test, reason="Skipping in GH action as it is visual")
@pytest.mark.parametrize(
    "ticker",
    [("AAPL"), ("BAC"), ("CAT"), ("ASML"), ("MSFT"), ("PLTR"), ("DHL.DE")],
)
def test_plot_digrin_shares_outstanding(ticker):
    ticker = Ticker(ticker=ticker)
    ticker.plot_digrin_shares_outstanding()
    assert True


@pytest.mark.skipif(skip_test, reason="Skipping in GH action as it is visual")
@pytest.mark.parametrize(
    "ticker, show_plot",
    [
        ("AAPL", False),
        ("BAC", True),
        ("CAT", True),
        ("ASML", True),
        ("MSFT", True),
        ("PLTR", True),
        ("DHL.DE", True),
    ],
)
def test_plot_digrin_expenses(ticker, show_plot):
    ticker = Ticker(ticker=ticker)
    ticker.plot_digrin_expenses(show_plot=show_plot)
    assert True


@pytest.mark.skipif(skip_test, reason="Skipping in GH action as it is visual")
@pytest.mark.parametrize(
    "ticker, show_plot",
    [
        ("AAPL", False),
        ("BAC", True),
        ("CAT", True),
        ("ASML", True),
        ("MSFT", True),
        ("PLTR", True),
        ("DHL.DE", True),
    ],
)
def test_plot_digrin_cost_of_revenue(ticker, show_plot):
    ticker = Ticker(ticker=ticker)
    ticker.plot_digrin_cost_of_revenue(show_plot=show_plot)
    assert True


@pytest.mark.parametrize(
    "input_date, expected_output",
    [
        # Test standard formats
        ("Dec. 31, 2023", "2023-12-31"),
        ("Jan. 1, 2024", "2024-01-01"),
        ("Feb. 15, 2022", "2022-02-15"),
        ("March 31, 2023", "2023-03-31"),
        ("Apr. 30, 2024", "2024-04-30"),
        ("May 15, 2023", "2023-05-15"),
        ("June 30, 2024", "2024-06-30"),
        ("Jul. 4, 2023", "2023-07-04"),
        ("Aug. 25, 2024", "2024-08-25"),
        ("Sept. 30, 2023", "2023-09-30"),
        ("Oct. 15, 2024", "2024-10-15"),
        ("Nov. 30, 2023", "2023-11-30"),
        # Test without periods
        ("Dec 31, 2023", "2023-12-31"),
        ("Jan 1, 2024", "2024-01-01"),
        ("March 15, 2022", "2022-03-15"),
        # Test single digit days
        ("Dec. 1, 2023", "2023-12-01"),
        ("Jan. 5, 2024", "2024-01-05"),
        ("Feb. 9, 2022", "2022-02-09"),
        # Test alternative month abbreviations
        ("Mar. 15, 2023", "2023-03-15"),
        ("Sep. 22, 2024", "2024-09-22"),
        # Test edge cases for days
        ("Jan. 01, 2023", "2023-01-01"),
        ("Dec. 09, 2024", "2024-12-09"),
    ],
)
def test_human_date_format_to_raw(input_date, expected_output):
    """Test the _human_date_format_to_raw function with various date formats"""
    ticker = Ticker(ticker="AAPL")
    result = ticker._human_date_format_to_raw(input_date)
    assert result == expected_output


@pytest.mark.parametrize(
    "invalid_input",
    [
        "Invalid date",
        "Dec 31",  # Missing year
        "2023-12-31",  # Wrong format
        "13. 31, 2023",  # Invalid month
        "Unknown 15, 2023",  # Unknown month name
        "",  # Empty string
    ],
)
def test_human_date_format_to_raw_invalid_inputs(invalid_input):
    """Test the _human_date_format_to_raw function with invalid inputs"""
    ticker = Ticker(ticker="AAPL")
    with pytest.raises((ValueError, KeyError, IndexError)):
        ticker._human_date_format_to_raw(invalid_input)
