import pytest

from stockdex.exceptions import WrongDataSource
from stockdex.ticker import TickerFactory


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
    ticker = TickerFactory(ticker=ticker).ticker

    # Send an HTTP GET request to the website
    response = ticker.get_response(f"https://finance.yahoo.com/quote/{ticker.ticker}")

    # Check if the response is as expected
    assert response.status_code == expected_response


def test_data_source_invalid():
    # Create a Ticker object
    ticker = TickerFactory(ticker="AAPL")

    # Check if the exception is raised
    with pytest.raises(WrongDataSource):
        ticker.data_source = "invalid_data_source"
