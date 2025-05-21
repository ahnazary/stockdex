from datetime import datetime

import pandas as pd
import pytest

from stockdex.exceptions import FieldNotExists
from stockdex.ticker import Ticker


@pytest.mark.parametrize(
    "ticker, range, dataGranularity",
    [
        ("AAPL", "1d", "1h"),
        ("GOOGL", "1d", "1h"),
        ("MSFT", "1d", "1d"),
        ("AAPL", "1h", "1m"),
        ("MSFT", "1h", "1m"),
        ("GOOGL", "5d", "1d"),
        ("MSFT", "1d", "1d"),
        ("NVDA", "max", "3mo"),
        ("SAP", "1y", "1mo"),
        ("ASML", "1y", "1mo"),
        ("AAPL", "1d", "1m"),
        ("SPCE", "1d", "1d"),
    ],
)
def test_yahoo_api_price(ticker, range, dataGranularity):
    """
    Test the price property of the YahooAPI class
    """

    ticker = Ticker(ticker)
    yahoo_api_price = ticker.yahoo_api_price(
        range=range, dataGranularity=dataGranularity
    )

    assert yahoo_api_price.columns.tolist() == [
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
    assert len(yahoo_api_price) > 0


@pytest.mark.parametrize(
    "ticker",
    [
        ("AAPL"),
        ("ASML"),
    ],
)
def test_yahoo_api_current_trading_period(ticker):
    """
    Test the price property of the YahooAPI class
    """

    ticker = Ticker(ticker)
    yahoo_api_current_trading_period = ticker.yahoo_api_current_trading_period

    assert yahoo_api_current_trading_period.columns.tolist() == [
        "pre",
        "regular",
        "post",
    ]
    assert len(yahoo_api_current_trading_period) == 4

    expected_columns = [
        "timezone",
        "start",
        "end",
        "gmtoffset",
    ]

    for column in expected_columns:
        assert column in yahoo_api_current_trading_period.index.tolist()


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
def test_yahoo_api_income_statement(ticker, frequency, format, period1, period2):
    ticker = Ticker(ticker)
    yahoo_api_income_statement = ticker.yahoo_api_income_statement(
        frequency=frequency, format=format, period1=period1, period2=period2
    )

    assert isinstance(yahoo_api_income_statement, pd.DataFrame)
    assert yahoo_api_income_statement.shape[0] > 0
    assert yahoo_api_income_statement.shape[1] > 0


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
def test_yahoo_api_cash_flow(ticker, frequency, format, period1, period2):
    ticker = Ticker(ticker)
    yahoo_api_cash_flow = ticker.yahoo_api_cash_flow(
        frequency=frequency, format=format, period1=period1, period2=period2
    )

    assert isinstance(yahoo_api_cash_flow, pd.DataFrame)
    assert yahoo_api_cash_flow.shape[0] > 0
    assert yahoo_api_cash_flow.shape[1] > 0


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
def test_yahoo_api_balance_sheet(ticker, frequency, format, period1, period2):
    ticker = Ticker(ticker)
    yahoo_api_balance_sheet = ticker.yahoo_api_balance_sheet(
        frequency=frequency, format=format, period1=period1, period2=period2
    )

    assert isinstance(yahoo_api_balance_sheet, pd.DataFrame)
    assert yahoo_api_balance_sheet.shape[0] > 0
    assert yahoo_api_balance_sheet.shape[1] > 0


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
def test_yahoo_api_financials(ticker, frequency, format, period1, period2):
    ticker = Ticker(ticker)
    yahoo_api_financials = ticker.yahoo_api_financials(
        frequency=frequency, format=format, period1=period1, period2=period2
    )

    assert isinstance(yahoo_api_financials, pd.DataFrame)
    assert yahoo_api_financials.shape[0] > 0
    assert yahoo_api_financials.shape[1] > 0


@pytest.mark.parametrize(
    "ticker, frequency, group_by, period1, period2",
    [
        ("AAPL", "quarterly", "field", datetime(2020, 1, 1), datetime.today()),
        ("GOOGL", "quarterly", "timeframe", datetime(2021, 1, 1), datetime.today()),
        ("MSFT", "annual", "field", datetime(2021, 1, 1), datetime(2024, 1, 1)),
        ("NVDA", "quarterly", "field", datetime(2020, 1, 1), datetime.today()),
        ("FMC", "quarterly", "field", datetime(2021, 1, 1), datetime.today()),
    ],
)
def test_plot_yahoo_api_income_statement(ticker, frequency, group_by, period1, period2):
    ticker = Ticker(ticker)
    ticker.plot_yahoo_api_income_statement(
        frequency=frequency, period1=period1, period2=period2, group_by=group_by
    )


def test_plot_yahoo_api_income_statement_wrong_field():
    ticker = Ticker("AAPL")
    with pytest.raises(FieldNotExists):
        ticker.plot_yahoo_api_income_statement(
            frequency="quarterly",
            period1=datetime(2020, 1, 1),
            period2=datetime.today(),
            fields_to_include=["wrong_field"],
        )


@pytest.mark.parametrize(
    "ticker, frequency, group_by, period1, period2",
    [
        ("AAPL", "quarterly", "field", datetime(2020, 1, 1), datetime.today()),
        ("GOOGL", "quarterly", "timeframe", datetime(2021, 1, 1), datetime.today()),
        ("MSFT", "annual", "field", datetime(2021, 1, 1), datetime(2024, 1, 1)),
        ("NVDA", "quarterly", "field", datetime(2020, 1, 1), datetime.today()),
        ("FMC", "quarterly", "field", datetime(2021, 1, 1), datetime.today()),
    ],
)
def test_plot_yahoo_api_cash_flow(ticker, frequency, group_by, period1, period2):
    ticker = Ticker(ticker)
    ticker.plot_yahoo_api_cash_flow(
        frequency=frequency, period1=period1, period2=period2, group_by=group_by
    )


def test_plot_yahoo_api_cash_flow_wrong_field():
    ticker = Ticker("AAPL")
    with pytest.raises(FieldNotExists):
        ticker.plot_yahoo_api_cash_flow(
            frequency="quarterly",
            period1=datetime(2020, 1, 1),
            period2=datetime.today(),
            fields_to_include=["wrong_field"],
        )


@pytest.mark.parametrize(
    "ticker, frequency, group_by, period1, period2",
    [
        ("AAPL", "quarterly", "field", datetime(2020, 1, 1), datetime.today()),
        ("GOOGL", "quarterly", "timeframe", datetime(2021, 1, 1), datetime.today()),
        ("MSFT", "annual", "field", datetime(2021, 1, 1), datetime(2024, 1, 1)),
        ("NVDA", "quarterly", "field", datetime(2020, 1, 1), datetime.today()),
        ("FMC", "quarterly", "field", datetime(2021, 1, 1), datetime.today()),
    ],
)
def test_plot_yahoo_api_balance_sheet(ticker, frequency, group_by, period1, period2):
    ticker = Ticker(ticker)
    ticker.plot_yahoo_api_balance_sheet(
        frequency=frequency, period1=period1, period2=period2, group_by=group_by
    )


def test_plot_yahoo_api_balance_sheet_wrong_field():
    ticker = Ticker("AAPL")
    with pytest.raises(FieldNotExists):
        ticker.plot_yahoo_api_balance_sheet(
            frequency="quarterly",
            period1=datetime(2020, 1, 1),
            period2=datetime.today(),
            fields_to_include=["wrong_field"],
        )


@pytest.mark.parametrize(
    "ticker, frequency, group_by, period1, period2",
    [
        ("AAPL", "quarterly", "field", datetime(2020, 1, 1), datetime.today()),
        ("GOOGL", "quarterly", "timeframe", datetime(2021, 1, 1), datetime.today()),
        ("MSFT", "annual", "field", datetime(2021, 1, 1), datetime(2024, 1, 1)),
        ("NVDA", "quarterly", "field", datetime(2020, 1, 1), datetime.today()),
        ("FMC", "quarterly", "field", datetime(2021, 1, 1), datetime.today()),
    ],
)
def test_plot_yahoo_api_financials(ticker, frequency, group_by, period1, period2):
    ticker = Ticker(ticker)
    ticker.plot_yahoo_api_financials(
        frequency=frequency, period1=period1, period2=period2, group_by=group_by
    )


def test_plot_yahoo_api_financials_wrong_field():
    ticker = Ticker("AAPL")
    with pytest.raises(FieldNotExists):
        ticker.plot_yahoo_api_financials(
            frequency="quarterly",
            period1=datetime(2020, 1, 1),
            period2=datetime.today(),
            fields_to_include=["wrong_field"],
        )
