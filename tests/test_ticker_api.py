from datetime import datetime

import pandas as pd
import pytest

from stockdex.ticker import Ticker


@pytest.mark.parametrize(
    "ticker, range, dataGranularity",
    [
        ("AAPL", "1d", "1h"),
        ("GOOGL", "1d", "1h"),
        ("MSFT", "1d", "1d"),
        ("AAPL", "1h", "1m"),
        ("GOOGL", "5d", "1d"),
        ("MSFT", "1d", "1d"),
        ("NVDA", "max", "3mo"),
        ("SAP", "1y", "1mo"),
    ],
)
def test_price(ticker, range, dataGranularity):
    """
    Test the price property of the TickerAPI class
    """

    ticker = Ticker(ticker)
    price = ticker.price(range=range, dataGranularity=dataGranularity)

    assert price.columns.tolist() == [
        "timestamp",
        "volume",
        "close",
        "open",
        "high",
        "low",
        "currency",
        "timezone",
        "exchangeTimezoneName",
        "exchangeName",
        "instrumentType",
    ]
    assert len(price) > 0


@pytest.mark.parametrize(
    "ticker",
    [
        ("AAPL"),
        ("ASML"),
    ],
)
def test_current_trading_period(ticker):
    """
    Test the price property of the TickerAPI class
    """

    ticker = Ticker(ticker)
    current_trading_period = ticker.current_trading_period

    assert current_trading_period.columns.tolist() == [
        "pre",
        "regular",
        "post",
    ]
    assert len(current_trading_period) == 4

    expected_columns = [
        "timezone",
        "start",
        "end",
        "gmtoffset",
    ]

    for column in expected_columns:
        assert column in current_trading_period.index.tolist()


@pytest.mark.parametrize(
    "ticker, frequency, format, period1, period2",
    [
        ("AAPL", "quarterly", "fmt", datetime(2020, 1, 1), datetime.today()),
        ("GOOGL", "quarterly", "fmt", datetime(2021, 1, 1), datetime.today()),
        ("MSFT", "quarterly", "fmt", datetime(2023, 1, 1), datetime(2024, 1, 1)),
        ("NVDA", "quarterly", "raw", datetime(2020, 1, 1), datetime.today()),
        ("FMC", "quarterly", "raw", datetime(2021, 1, 1), datetime.today()),
    ],
)
def test_income_statement(ticker, frequency, format, period1, period2):
    ticker = Ticker(ticker)
    income_statement = ticker.income_statement(
        frequency=frequency, format=format, period1=period1, period2=period2
    )

    assert isinstance(income_statement, pd.DataFrame)
    assert income_statement.shape[0] > 0
    assert income_statement.shape[1] > 0


@pytest.mark.parametrize(
    "ticker, frequency, format, period1, period2",
    [
        ("AAPL", "quarterly", "fmt", datetime(2020, 1, 1), datetime.today()),
        ("GOOGL", "quarterly", "fmt", datetime(2021, 1, 1), datetime.today()),
        ("MSFT", "quarterly", "fmt", datetime(2023, 1, 1), datetime(2024, 1, 1)),
        ("NVDA", "quarterly", "raw", datetime(2020, 1, 1), datetime.today()),
        ("FMC", "quarterly", "raw", datetime(2021, 1, 1), datetime.today()),
    ],
)
def test_cash_flow(ticker, frequency, format, period1, period2):
    ticker = Ticker(ticker)
    cash_flow = ticker.cash_flow(
        frequency=frequency, format=format, period1=period1, period2=period2
    )

    assert isinstance(cash_flow, pd.DataFrame)
    assert cash_flow.shape[0] > 0
    assert cash_flow.shape[1] > 0


@pytest.mark.parametrize(
    "ticker, frequency, format, period1, period2",
    [
        ("AAPL", "quarterly", "fmt", datetime(2020, 1, 1), datetime.today()),
        ("GOOGL", "quarterly", "fmt", datetime(2021, 1, 1), datetime.today()),
        ("MSFT", "quarterly", "fmt", datetime(2023, 1, 1), datetime(2024, 1, 1)),
        ("NVDA", "quarterly", "raw", datetime(2020, 1, 1), datetime.today()),
        ("FMC", "quarterly", "raw", datetime(2021, 1, 1), datetime.today()),
    ],
)
def test_balance_sheet(ticker, frequency, format, period1, period2):
    ticker = Ticker(ticker)
    balance_sheet = ticker.balance_sheet(
        frequency=frequency, format=format, period1=period1, period2=period2
    )

    assert isinstance(balance_sheet, pd.DataFrame)
    assert balance_sheet.shape[0] > 0
    assert balance_sheet.shape[1] > 0


@pytest.mark.parametrize(
    "ticker, frequency, format, period1, period2",
    [
        ("AAPL", "quarterly", "fmt", datetime(2020, 1, 1), datetime.today()),
        ("GOOGL", "quarterly", "fmt", datetime(2021, 1, 1), datetime.today()),
        ("MSFT", "quarterly", "fmt", datetime(2023, 1, 1), datetime(2024, 1, 1)),
        ("NVDA", "quarterly", "raw", datetime(2020, 1, 1), datetime.today()),
        ("FMC", "quarterly", "raw", datetime(2021, 1, 1), datetime.today()),
    ],
)
def test_financials(ticker, frequency, format, period1, period2):
    ticker = Ticker(ticker)
    financials = ticker.financials(
        frequency=frequency, format=format, period1=period1, period2=period2
    )

    assert isinstance(financials, pd.DataFrame)
    assert financials.shape[0] > 0
    assert financials.shape[1] > 0
