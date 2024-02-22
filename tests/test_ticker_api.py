"""
Module to test the TickerAPI class
"""

import pytest
from stockdex.ticker_api import TickerAPI


@pytest.mark.parametrize(
    "ticker",
    [
        ("AAPL"),
        ("GOOGL"),
        ("MSFT"),
    ],
)
def test_get_chart(ticker):
    ticker_api = TickerAPI(ticker)
    response = ticker_api.get_chart()

    assert response is not None
