"""
Module to test the NasdaqInterface class
"""

import pandas as pd
import pytest

from stockdex.nasdaq_interface import NASDAQInterface


@pytest.mark.parametrize(
    "ticker",
    [
        ("NVDA"),
        ("AAPL"),
        ("GOOGL"),
        ("MSFT"),
    ],
)
def test_quarterly_earnings_surprise(ticker):
    nasdaq_interface = NASDAQInterface(ticker)
    response = nasdaq_interface.quarterly_earnings_surprise()

    assert response is not None
    assert isinstance(response, pd.DataFrame)
    assert response.shape[0] > 1
    assert response.shape[1] > 1

    expected_columns = [
        "Fiscal Quarter End",
        "Date Reported",
        "Earnings Per Share*",
        "Consensus EPS* Forecast",
        "% Surprise",
    ]
    assert response.columns.tolist() == expected_columns
