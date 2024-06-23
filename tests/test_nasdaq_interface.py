"""
Module to test the NasdaqInterface class
"""

import pandas as pd
import pytest

from stockdex.exceptions import WrongSecurityType
from stockdex.ticker import Ticker

pytestmark = pytest.mark.skip(
    reason="""Skip the entire module as nasdaq is
              not supported anymore due to nasdaq
              website changes"""
)


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
    ticker = Ticker(ticker, data_source="nasdaq")
    response = ticker.quarterly_earnings_surprise

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


def test_quarterly_earnings_surprise_wrong_securiy_type():
    with pytest.raises(WrongSecurityType):
        ticker = Ticker(
            ticker="AAPL", security_type="wrong_security_type", data_source="nasdaq"
        )
        ticker.quarterly_earnings_surprise


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
    ticker = Ticker(ticker, data_source="nasdaq")
    response = ticker.yearly_earnings_forecast

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


def test_yearly_earnings_forecast_wrong_securiy_type():
    with pytest.raises(WrongSecurityType):
        ticker = Ticker(
            ticker="AAPL", security_type="wrong_security_type", data_source="nasdaq"
        )
        ticker.yearly_earnings_forecast


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
    ticker = Ticker(ticker, data_source="nasdaq")
    response = ticker.quarterly_earnings_forecast

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


def test_quarterly_earnings_forecast_wrong_securiy_type():
    with pytest.raises(WrongSecurityType):
        ticker = Ticker(
            ticker="AAPL", security_type="wrong_security_type", data_source="nasdaq"
        )
        ticker.quarterly_earnings_forecast


@pytest.mark.parametrize(
    "ticker",
    [
        ("NVDA"),
        ("AAPL"),
        ("GOOGL"),
        ("MSFT"),
    ],
)
def test_price_to_earnings_ratio(ticker):
    ticker = Ticker(ticker, data_source="nasdaq")
    price_to_earnings_ratio = ticker.price_to_earnings_ratio

    assert price_to_earnings_ratio is not None
    assert isinstance(price_to_earnings_ratio, pd.DataFrame)
    assert price_to_earnings_ratio.shape[0] > 1
    assert price_to_earnings_ratio.shape[1] == 1


def test_price_to_earnings_ratio_wrong_securiy_type():
    with pytest.raises(WrongSecurityType):
        ticker = Ticker(
            ticker="AAPL", security_type="wrong_security_type", data_source="nasdaq"
        )
        ticker.price_to_earnings_ratio


@pytest.mark.parametrize(
    "ticker",
    [
        ("NVDA"),
        ("AAPL"),
        ("GOOGL"),
        ("MSFT"),
    ],
)
def test_forecast_peg_rate(ticker):
    ticker = Ticker(ticker, data_source="nasdaq")
    forecast_peg_rate = ticker.forecast_peg_rate

    assert forecast_peg_rate is not None
    assert isinstance(forecast_peg_rate, pd.DataFrame)
    assert forecast_peg_rate.shape[0] > 1
    assert forecast_peg_rate.shape[1] == 1


def test_forecast_peg_rate_wrong_securiy_type():
    with pytest.raises(WrongSecurityType):
        ticker = Ticker(
            ticker="AAPL", security_type="wrong_security_type", data_source="nasdaq"
        )
        ticker.forecast_peg_rate
