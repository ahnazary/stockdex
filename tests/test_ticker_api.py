"""
Module to test the TickerAPI class
"""

import pytest
from stockdex.ticker_api import TickerAPI


@pytest.mark.parametrize(
    "ticker, expected_response",
    [
        ("AAPL", 200),
        ("GOOGL", 200),
        ("MSFT", 200),
    ],
)
def test_get_chart(ticker, expected_response):
    ticker_api = TickerAPI(ticker)
    response = ticker_api.get_chart()

    # Check if the response is as expected
    assert response.status_code == expected_response
    assert response.json() is not None
