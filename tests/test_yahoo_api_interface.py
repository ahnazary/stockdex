from datetime import datetime, timedelta

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


@pytest.mark.parametrize("ticker", ["KO", "AAPL"])
def test_yahoo_api_dividends(ticker):
    dividends = Ticker(ticker).yahoo_api_dividends(range="5y")
    assert len(dividends) >= 8
    assert {"amount", "currency"} <= set(dividends.columns)
    assert (dividends["amount"] > 0).all()
    assert dividends.index.is_monotonic_increasing


def test_yahoo_api_splits():
    splits = Ticker("AAPL").yahoo_api_splits()
    # Apple's 4:1 split on 2020-08-31.
    assert "4:1" in set(splits["splitRatio"])
    assert {"numerator", "denominator", "splitRatio"} <= set(splits.columns)


def test_yahoo_api_capital_gains_for_stock_is_empty_or_valid():
    gains = Ticker("AAPL").yahoo_api_capital_gains(range="5y")
    assert gains.empty or "amount" in gains.columns


@pytest.mark.parametrize("frequency", ["annual", "quarterly", "trailing"])
def test_yahoo_api_valuation_measures(frequency):
    frame = Ticker("AAPL").yahoo_api_valuation_measures(
        frequency=frequency, format="raw"
    )
    assert len(frame) >= 3
    assert f"{frequency}MarketCap" in frame.columns
    assert f"{frequency}PeRatio" in frame.columns
    assert frame.index.is_monotonic_increasing


def test_yahoo_api_quote_summary():
    data = Ticker("AAPL").yahoo_api_quote_summary(
        ["price", "summaryDetail", "financialData"]
    )
    assert set(data) == {"price", "summaryDetail", "financialData"}
    assert isinstance(data["financialData"]["currentPrice"], float)
    assert data["price"]["currency"] == "USD"


@pytest.mark.parametrize(
    "method, field",
    [
        ("yahoo_api_profile", "sector"),
        ("yahoo_api_market_price", "regularMarketPrice"),
        ("yahoo_api_summary_detail", "marketCap"),
        ("yahoo_api_key_statistics", "enterpriseValue"),
        ("yahoo_api_financial_data", "targetMeanPrice"),
    ],
)
def test_yahoo_api_company_records(method, field):
    frame = getattr(Ticker("AAPL"), method)()
    assert list(frame.columns) == ["AAPL"]
    assert field in frame.index


def test_yahoo_api_officers():
    officers = Ticker("AAPL").yahoo_api_officers()
    assert len(officers) > 0
    assert {"name", "title"} <= set(officers.columns)


def test_yahoo_api_calendar_events():
    events = Ticker("AAPL").yahoo_api_calendar_events()
    assert any(index.startswith("earningsDate") for index in events.index)


@pytest.mark.parametrize(
    "method, column",
    [
        ("yahoo_api_earnings_history", "epsActual"),
        ("yahoo_api_earnings_trend", "earningsEstimate_avg"),
        ("yahoo_api_recommendation_trend", "strongBuy"),
        ("yahoo_api_upgrades_downgrades", "firm"),
    ],
)
def test_yahoo_api_analyst_tables(method, column):
    frame = getattr(Ticker("AAPL"), method)()
    assert len(frame) > 0
    assert column in frame.columns


@pytest.mark.parametrize(
    "method, column",
    [
        ("yahoo_api_institutional_holders", "organization"),
        ("yahoo_api_fund_holders", "organization"),
        ("yahoo_api_insider_holders", "name"),
        ("yahoo_api_insider_transactions", "filerName"),
        ("yahoo_api_sec_filings", "type"),
    ],
)
def test_yahoo_api_ownership_tables(method, column):
    frame = getattr(Ticker("AAPL"), method)()
    assert len(frame) > 0
    assert column in frame.columns


@pytest.mark.parametrize(
    "method, field",
    [
        ("yahoo_api_major_holders", "institutionsPercentHeld"),
        ("yahoo_api_insider_purchase_activity", "period"),
    ],
)
def test_yahoo_api_ownership_records(method, field):
    frame = getattr(Ticker("AAPL"), method)()
    assert field in frame.index


@pytest.mark.parametrize("symbol", ["SPY", "VFIAX"])
def test_yahoo_api_fund_methods(symbol):
    fund = Ticker(symbol, security_type="etf")
    assert len(fund.yahoo_api_fund_top_holdings()) > 0
    assert fund.yahoo_api_fund_sector_weightings()["weight"].sum() > 0.9
    assert "stockPosition" in fund.yahoo_api_fund_asset_allocation().index
    assert "categoryName" in fund.yahoo_api_fund_profile().index
    performance = fund.yahoo_api_fund_performance()
    assert {"fund", "category"} == set(performance.columns)
    assert "oneYear" in performance.index


def test_yahoo_api_fund_methods_empty_for_stock():
    stock = Ticker("AAPL")
    assert stock.yahoo_api_fund_top_holdings().empty
    assert stock.yahoo_api_fund_performance().empty


def test_yahoo_api_options_chain():
    ticker = Ticker("AAPL")
    expirations = ticker.yahoo_api_option_expirations()
    assert len(expirations) > 3
    chain = ticker.yahoo_api_options_chain(expirations[1])
    assert {"call", "put"} == set(chain["optionType"])
    assert (chain["expiration"] == expirations[1]).all()


def test_yahoo_api_quotes():
    quotes = Ticker.yahoo_api_quotes(["AAPL", "MSFT"])
    assert {"AAPL", "MSFT"} == set(quotes.index)
    assert (quotes["regularMarketPrice"] > 0).all()


def test_yahoo_api_search():
    results = Ticker.yahoo_api_search("apple", limit=5)
    assert "AAPL" in set(results["symbol"])


def test_yahoo_api_similar_symbols():
    similar = Ticker("AAPL").yahoo_api_similar_symbols()
    assert len(similar) > 0
    assert similar["score"].is_monotonic_decreasing


@pytest.mark.parametrize(
    "ticker, frequency, format, period1, period2",
    [
        # 2 years ago
        (
            "AAPL",
            "quarterly",
            "fmt",
            datetime.today() - timedelta(days=365 * 1),
            datetime.today(),
        ),
        (
            "GOOGL",
            "quarterly",
            "fmt",
            datetime.today() - timedelta(days=365 * 1),
            datetime.today(),
        ),
        (
            "MSFT",
            "quarterly",
            "fmt",
            datetime.today() - timedelta(days=365 * 1),
            datetime.today(),
        ),
        (
            "NVDA",
            "quarterly",
            "raw",
            datetime.today() - timedelta(days=365 * 1),
            datetime.today(),
        ),
        (
            "FMC",
            "quarterly",
            "raw",
            datetime.today() - timedelta(days=365 * 1),
            datetime.today(),
        ),
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
        (
            "AAPL",
            "quarterly",
            "fmt",
            datetime.today() - timedelta(days=365 * 1),
            datetime.today(),
        ),
        (
            "GOOGL",
            "quarterly",
            "fmt",
            datetime.today() - timedelta(days=365 * 1),
            datetime.today(),
        ),
        (
            "MSFT",
            "quarterly",
            "fmt",
            datetime.today() - timedelta(days=365 * 1),
            datetime.today(),
        ),
        (
            "NVDA",
            "quarterly",
            "raw",
            datetime.today() - timedelta(days=365 * 1),
            datetime.today(),
        ),
        (
            "FMC",
            "quarterly",
            "raw",
            datetime.today() - timedelta(days=365 * 1),
            datetime.today(),
        ),
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
        (
            "AAPL",
            "quarterly",
            "fmt",
            datetime.today() - timedelta(days=365 * 1),
            datetime.today(),
        ),
        (
            "GOOGL",
            "quarterly",
            "fmt",
            datetime.today() - timedelta(days=365 * 1),
            datetime.today(),
        ),
        (
            "MSFT",
            "quarterly",
            "fmt",
            datetime.today() - timedelta(days=365 * 1),
            datetime.today(),
        ),
        (
            "NVDA",
            "quarterly",
            "raw",
            datetime.today() - timedelta(days=365 * 1),
            datetime.today(),
        ),
        (
            "FMC",
            "quarterly",
            "raw",
            datetime.today() - timedelta(days=365 * 1),
            datetime.today(),
        ),
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
        (
            "AAPL",
            "quarterly",
            "fmt",
            datetime.today() - timedelta(days=365 * 1),
            datetime.today(),
        ),
        (
            "GOOGL",
            "quarterly",
            "fmt",
            datetime.today() - timedelta(days=365 * 1),
            datetime.today(),
        ),
        (
            "MSFT",
            "quarterly",
            "fmt",
            datetime.today() - timedelta(days=365 * 1),
            datetime.today(),
        ),
        (
            "NVDA",
            "quarterly",
            "raw",
            datetime.today() - timedelta(days=365 * 1),
            datetime.today(),
        ),
        (
            "FMC",
            "quarterly",
            "raw",
            datetime.today() - timedelta(days=365 * 1),
            datetime.today(),
        ),
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
        (
            "AAPL",
            "quarterly",
            "field",
            datetime.today() - timedelta(days=365 * 1),
            datetime.today(),
        ),
        (
            "GOOGL",
            "quarterly",
            "timeframe",
            datetime.today() - timedelta(days=365 * 1),
            datetime.today(),
        ),
        (
            "MSFT",
            "annual",
            "field",
            datetime.today() - timedelta(days=365 * 2),
            datetime.today(),
        ),
        (
            "NVDA",
            "quarterly",
            "field",
            datetime.today() - timedelta(days=365 * 1),
            datetime.today(),
        ),
        (
            "FMC",
            "quarterly",
            "field",
            datetime.today() - timedelta(days=365 * 1),
            datetime.today(),
        ),
    ],
)
def test_plot_yahoo_api_income_statement(ticker, frequency, group_by, period1, period2):
    ticker = Ticker(ticker)
    ticker.plot_yahoo_api_income_statement(
        frequency=frequency,
        period1=period1,
        period2=period2,
        group_by=group_by,
        show_plot=False,
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
        (
            "AAPL",
            "quarterly",
            "field",
            datetime.today() - timedelta(days=365 * 1),
            datetime.today(),
        ),
        (
            "GOOGL",
            "quarterly",
            "timeframe",
            datetime.today() - timedelta(days=365 * 1),
            datetime.today(),
        ),
        (
            "MSFT",
            "annual",
            "field",
            datetime.today() - timedelta(days=365 * 2),
            datetime.today(),
        ),
        (
            "NVDA",
            "quarterly",
            "field",
            datetime.today() - timedelta(days=365 * 1),
            datetime.today(),
        ),
        (
            "FMC",
            "quarterly",
            "field",
            datetime.today() - timedelta(days=365 * 1),
            datetime.today(),
        ),
    ],
)
def test_plot_yahoo_api_cash_flow(ticker, frequency, group_by, period1, period2):
    ticker = Ticker(ticker)
    ticker.plot_yahoo_api_cash_flow(
        frequency=frequency,
        period1=period1,
        period2=period2,
        group_by=group_by,
        show_plot=False,
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
        (
            "AAPL",
            "quarterly",
            "field",
            datetime.today() - timedelta(days=365 * 1),
            datetime.today(),
        ),
        (
            "GOOGL",
            "quarterly",
            "timeframe",
            datetime.today() - timedelta(days=365 * 1),
            datetime.today(),
        ),
        (
            "MSFT",
            "annual",
            "field",
            datetime.today() - timedelta(days=365 * 2),
            datetime.today(),
        ),
        (
            "NVDA",
            "quarterly",
            "field",
            datetime.today() - timedelta(days=365 * 1),
            datetime.today(),
        ),
        (
            "FMC",
            "quarterly",
            "field",
            datetime.today() - timedelta(days=365 * 1),
            datetime.today(),
        ),
    ],
)
def test_plot_yahoo_api_balance_sheet(ticker, frequency, group_by, period1, period2):
    ticker = Ticker(ticker)
    ticker.plot_yahoo_api_balance_sheet(
        frequency=frequency,
        period1=period1,
        period2=period2,
        group_by=group_by,
        show_plot=False,
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
        (
            "AAPL",
            "quarterly",
            "field",
            datetime.today() - timedelta(days=365 * 1),
            datetime.today(),
        ),
        (
            "GOOGL",
            "quarterly",
            "timeframe",
            datetime.today() - timedelta(days=365 * 1),
            datetime.today(),
        ),
        (
            "MSFT",
            "annual",
            "field",
            datetime.today() - timedelta(days=365 * 2),
            datetime.today(),
        ),
        (
            "NVDA",
            "quarterly",
            "field",
            datetime.today() - timedelta(days=365 * 1),
            datetime.today(),
        ),
        (
            "FMC",
            "quarterly",
            "field",
            datetime.today() - timedelta(days=365 * 1),
            datetime.today(),
        ),
    ],
)
def test_plot_yahoo_api_financials(ticker, frequency, group_by, period1, period2):
    ticker = Ticker(ticker)
    ticker.plot_yahoo_api_financials(
        frequency=frequency,
        period1=period1,
        period2=period2,
        group_by=group_by,
        show_plot=False,
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
