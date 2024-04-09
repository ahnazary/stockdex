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
def test_dividend(ticker):
    ticker = Ticker(ticker)
    dividend = ticker.dividend

    # Check if the response is as expected
    assert isinstance(dividend, pd.DataFrame)
    assert dividend.shape[0] > 0
    assert dividend.shape[1] == 5


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
def test_payout_ratio(ticker):
    ticker = Ticker(ticker)
    payout_ratio = ticker.payout_ratio

    # Check if the response is as expected
    assert isinstance(payout_ratio, pd.DataFrame)
    assert payout_ratio.shape[0] > 1
    assert payout_ratio.shape[1] == 2


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
def test_stock_splits(ticker):
    ticker = Ticker(ticker)
    stock_splits = ticker.stock_splits

    # Check if the response is as expected
    assert isinstance(stock_splits, pd.DataFrame)
    assert stock_splits.shape[0] > 1
    assert stock_splits.shape[1] == 2
