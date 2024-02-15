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


@pytest.mark.parametrize(
    "ticker",
    [
        ("AAPL"),
        ("GOOGL"),
        ("MSFT"),
    ],
)
def test_cash_flow(ticker):
    ticker = Ticker(ticker)
    cash_flow_df = ticker.cash_flow

    # Check if the response is as expected
    assert isinstance(cash_flow_df, pd.DataFrame)
    assert cash_flow_df.shape[0] > 0


@pytest.mark.parametrize(
    "ticker",
    [
        ("AAPL"),
        ("GOOGL"),
        ("MSFT"),
    ],
)
def test_analysis(ticker):
    ticker = Ticker(ticker)
    analysis_df = ticker.analysis

    # Check if the response is as expected
    assert isinstance(analysis_df, pd.DataFrame)
    assert analysis_df.shape[0] > 0


@pytest.mark.parametrize(
    "ticker",
    [
        ("AAPL"),
        ("GOOGL"),
        ("MSFT"),
    ],
)
def test_summary(ticker):
    ticker = Ticker(ticker)
    summary_df = ticker.summary

    # Check if the response is as expected
    assert isinstance(summary_df, pd.DataFrame)
    assert summary_df.shape[0] > 0


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


@pytest.mark.parametrize(
    "ticker",
    [
        ("AAPL"),
        ("GOOGL"),
        ("MSFT"),
    ],
)
def test_income_stmt(ticker):
    ticker = Ticker(ticker)
    income_stmt_df = ticker.income_stmt

    # Check if the response is as expected
    assert isinstance(income_stmt_df, pd.DataFrame)
    assert income_stmt_df.shape[0] > 0


@pytest.mark.parametrize(
    "ticker",
    [
        ("AAPL"),
        ("GOOGL"),
        ("MSFT"),
    ],
)
def test_calls(ticker):
    ticker = Ticker(ticker)
    calls = ticker.calls

    # Check if the response is as expected
    assert isinstance(calls, pd.DataFrame)
    assert calls.shape[0] > 0


@pytest.mark.parametrize(
    "ticker",
    [
        ("AAPL"),
        ("GOOGL"),
        ("MSFT"),
    ],
)
def test_puts(ticker):
    ticker = Ticker(ticker)
    puts = ticker.puts

    # Check if the response is as expected
    assert isinstance(puts, pd.DataFrame)
    assert puts.shape[0] > 0


@pytest.mark.parametrize(
    "ticker",
    [
        ("AAPL"),
        ("GOOGL"),
        ("ASML"),
    ],
)
def test_key_executives(ticker):
    ticker = Ticker(ticker)
    key_executives = ticker.key_executives

    # Check if the response is as expected
    assert isinstance(key_executives, pd.DataFrame)
    assert key_executives.shape[0] > 0


@pytest.mark.parametrize(
    "ticker",
    [
        ("AAPL"),
        ("GOOGL"),
        ("ASML"),
        ("TSLA"),
    ],
)
def test_description(ticker):
    ticker = Ticker(ticker)
    description = ticker.description

    # Check if the response is as expected
    assert isinstance(description, str)
    assert len(description) > 0


@pytest.mark.parametrize(
    "ticker",
    [
        ("AAPL"),
        ("GOOGL"),
        ("ASML"),
        ("TSLA"),
    ],
)
def test_corporate_governance(ticker):
    ticker = Ticker(ticker)
    corporate_governance = ticker.corporate_governance

    # Check if the response is as expected
    assert isinstance(corporate_governance, str)
    assert len(corporate_governance) > 0
