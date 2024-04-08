"""
Module to test the NasdaqInterface class
"""

import pandas as pd
import pytest

from stockdex.ticker import Ticker


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
    ticker = Ticker(ticker)
    response = ticker.quarterly_earnings_surprise()

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


@pytest.mark.parametrize(
    "ticker",
    [
        ("NVDA"),
        ("AAPL"),
        ("GOOGL"),
        ("MSFT"),
    ],
)
def test_yearly_earnings_forecast(ticker):
    ticker = Ticker(ticker)
    response = ticker.yearly_earnings_forecast()

    assert response is not None
    assert isinstance(response, pd.DataFrame)
    assert response.shape[0] > 1
    assert response.shape[1] > 1

    expected_columns = [
        "Fiscal Year End",
        "Consensus EPS* Forecast",
        "High EPS* Forecast",
        "Low EPS* Forecast",
    ]

    for column in expected_columns:
        assert column in response.columns.tolist()


@pytest.mark.parametrize(
    "ticker",
    [
        ("NVDA"),
        ("AAPL"),
        ("GOOGL"),
        ("MSFT"),
    ],
)
def test_quarterly_earnings_forecast(ticker):
    ticker = Ticker(ticker)
    response = ticker.quarterly_earnings_forecast()

    assert response is not None
    assert isinstance(response, pd.DataFrame)
    assert response.shape[0] > 1
    assert response.shape[1] > 1

    expected_columns = [
        "Fiscal Quarter End",
        "Consensus EPS* Forecast",
        "High EPS* Forecast",
        "Low EPS* Forecast",
    ]

    for column in expected_columns:
        assert column in response.columns.tolist()
