"""
Module to test the NasdaqInterface class
"""

import pandas as pd
import pytest

from stockdex.nasdaq_interface import NASDAQInterface


@pytest.mark.skip(reason="Under development")
@pytest.mark.parametrize(
    "ticker",
    [
        ("NVDA"),
        ("AAPL"),
        ("GOOGL"),
        ("MSFT"),
    ],
)
def test_quarterly_earnings(ticker):
    nasdaq_interface = NASDAQInterface(ticker)
    response = nasdaq_interface.quarterly_earnings()

    assert response is not None
    assert isinstance(response, pd.DataFrame)
    assert response.shape[0] > 0
