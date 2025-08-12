import pandas as pd
import pytest

from stockdex.finviz_interface import FinvizInterface


@pytest.mark.parametrize(
    "ticker",
    [
        "AAPL",
        "GOOGL",
        "TSLA",
        "BAC",
    ],
)
def test_get_insider_trading(ticker):
    """Test the get_insider_trading method of FinvizInterface."""
    finviz = FinvizInterface(ticker=ticker)
    result = finviz.get_insider_trading()

    assert isinstance(result, pd.DataFrame)
    expected_columns = [
        "Insider Trading",
        "Relationship",
        "Date",
        "Transaction",
        "Cost",
    ]
    assert all(col in result.columns for col in expected_columns)
    assert result.shape[0] > 0, "Insider trading data should not be empty"
    assert (
        result["Insider Trading"].notnull().all()
    ), "Insider Trading column should not have null values"


@pytest.mark.parametrize(
    "ticker",
    [
        "AAPL",
        "GOOGL",
        "TSLA",
        "BAC",
    ],
)
def test_price_reaction_to_earnings_report(ticker):
    """Test the price_reaction_to_earnings_report method of FinvizInterface."""
    finviz = FinvizInterface(ticker=ticker)
    result = finviz.price_reaction_to_earnings_report()

    assert isinstance(result, pd.DataFrame)
    expected_columns = [
        "Date",
        "EPS Estimate",
        "Reported EPS",
        "Price Reaction",
    ]
    assert all(col in result.columns for col in expected_columns)
    assert result.shape[0] > 0, "Price reaction to earnings data should not be empty"
    assert result["Date"].notnull().all(), "Date column should not have null values"
