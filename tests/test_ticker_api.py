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
def test_chart(ticker):
    """
    Test the chart property of the TickerAPI class
    """

    api = TickerAPI(ticker)
    chart = api.chart

    assert chart.columns.tolist() == [
        "timestamp",
        "volume",
        "close",
        "open",
        "high",
        "low",
    ]
    assert len(chart) > 0
