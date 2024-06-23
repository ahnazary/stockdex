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
