import pandas as pd
import pytest

from stockdex.ticker import Ticker


@pytest.mark.parametrize(
    "ticker, expected_response",
    [
        ("AAPL", 200),
        ("GOOGL", 200),
        ("MSFT", 200),
    ],
)
def test_get_response(ticker, expected_response):
    # Create a Ticker object
    ticker = Ticker(ticker)

    # Send an HTTP GET request to the website
    response = ticker.get_response(f"https://finance.yahoo.com/quote/{ticker.ticker}")

    # Check if the response is as expected
    assert response.status_code == expected_response


@pytest.mark.skip(
    reason="This test is skipped because github actions is not able to access the yahoo finance page"  # noqa E501
)
@pytest.mark.parametrize(
    "ticker",
    [
        ("AAPL"),
        ("GOOGL"),
        ("MSFT"),
    ],
)
def test_statistics(ticker):
    ticker = Ticker(ticker)
    statistics_df = ticker.statistics()

    # Check if the response is as expected
    assert isinstance(statistics_df, pd.DataFrame)
    assert statistics_df.shape[0] > 0
