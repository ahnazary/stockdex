import os

import pandas as pd
import pytest

from stockdex.finviz_interface import FinvizInterface

skip_test = bool(os.getenv("SKIP_TEST", False))


@pytest.mark.parametrize(
    "ticker",
    [
        "AAPL",
        "GOOGL",
        "TSLA",
        "BAC",
    ],
)
def test_finviz_get_insider_trading(ticker):
    """Test the get_insider_trading method of FinvizInterface."""
    finviz = FinvizInterface(ticker=ticker)
    result = finviz.finviz_get_insider_trading()

    assert isinstance(result, pd.DataFrame)
    expected_columns = [
        "Insider Trading",
        "Relationship",
        "Date",
        "Transaction",
        "Cost",
    ]
    assert all(col in result.columns for col in expected_columns)
    assert result.shape[0] > 0, "Insider trading data should not be empty"
    assert (
        result["Insider Trading"].notnull().all()
    ), "Insider Trading column should not have null values"
    assert result["Date"].notnull().all(), "Date column should not have null values"
    assert (
        result["Transaction"].notnull().all()
    ), "Transaction column should not have null values"
    assert result["Cost"].notnull().all(), "Cost column should not have null values"

    assert pd.api.types.is_string_dtype(
        result["Insider Trading"]
    ), "Insider Trading column should be string"
    assert pd.api.types.is_string_dtype(result["Date"]), "Date column should be string"
    assert pd.api.types.is_string_dtype(
        result["Transaction"]
    ), "Transaction column should be string"
    assert pd.api.types.is_string_dtype(result["Cost"]), "Cost column should be string"


@pytest.mark.parametrize(
    "ticker",
    [
        "AAPL",
        "GOOGL",
        "TSLA",
        "BAC",
    ],
)
def test_finviz_price_reaction_to_earnings_report(ticker):
    """Test the price_reaction_to_earnings_report method of FinvizInterface."""
    finviz = FinvizInterface(ticker=ticker)
    result = finviz.finviz_price_reaction_to_earnings_report()

    assert isinstance(result, pd.DataFrame)
    expected_columns = [
        "reactions",
        "ticker",
        "fiscalPeriod",
        "rsi",
        "chartEndDate",
        "chartStartDate",
        "fiscalEndDate",
    ]
    assert all(col in result.columns for col in expected_columns)
    assert result.shape[0] > 0, "Price reaction to earnings data should not be empty"
    assert (
        result["reactions"].notnull().all()
    ), "Reactions column should not have null values"
    assert result["rsi"].notnull().all(), "RSI column should not have null values"
    assert (
        result["chartEndDate"].notnull().all()
    ), "Chart end date column should not have null values"
    assert (
        result["chartStartDate"].notnull().all()
    ), "Chart start date column should not have null values"
    assert (
        result["fiscalEndDate"].notnull().all()
    ), "Fiscal end date column should not have null values"
    assert pd.api.types.is_numeric_dtype(result["rsi"]), "RSI column should be numeric"
    assert pd.api.types.is_string_dtype(
        result["chartEndDate"]
    ), "Chart end date column should be string"
    assert pd.api.types.is_string_dtype(
        result["chartStartDate"]
    ), "Chart start date column should be string"
    assert pd.api.types.is_string_dtype(
        result["fiscalEndDate"]
    ), "Fiscal end date column should be string"


@pytest.mark.parametrize(
    "ticker",
    [
        "AAPL",
        "GOOGL",
        "TSLA",
        "BAC",
    ],
)
def test_finviz_earnings_revisions(ticker):
    """Test the earnings_revisions_data method of FinvizInterface."""
    finviz = FinvizInterface(ticker=ticker)
    result = finviz.finviz_earnings_revisions_data()

    assert isinstance(result, pd.DataFrame)
    expected_columns = [
        "ticker",
        "fiscalPeriod",
        "estimateType",
        "estimateDate",
        "downRevisions",
        "high",
        "low",
    ]
    assert all(col in result.columns for col in expected_columns)
    assert result.shape[0] > 0, "Earnings revisions data should not be empty"
    assert result["ticker"].notnull().all(), "Ticker column should not have null values"
    assert (
        result["fiscalPeriod"].notnull().all()
    ), "Fiscal period column should not have null values"
    assert (
        result["estimateType"].notnull().all()
    ), "Estimate type column should not have null values"
    assert (
        result["estimateDate"].notnull().all()
    ), "Estimate date column should not have null values"
    assert (
        result["downRevisions"].notnull().all()
    ), "Down revisions column should not have null values"
    assert result["high"].notnull().all(), "High column should not have null values"
    assert result["low"].notnull().all(), "Low column should not have null values"
    assert pd.api.types.is_numeric_dtype(
        result["high"]
    ), "High column should be numeric"
    assert pd.api.types.is_numeric_dtype(result["low"]), "Low column should be numeric"


@pytest.mark.parametrize(
    "ticker",
    [
        "AAPL",
        "GOOGL",
        "TSLA",
        "BAC",
    ],
)
def test_finviz_earnings_annual_data(ticker):
    """Test the earnings_annual_data method of FinvizInterface."""
    finviz = FinvizInterface(ticker=ticker)
    result = finviz.finviz_earnings_annual_data()

    assert isinstance(result, pd.DataFrame)
    expected_columns = [
        "ticker",
        "fiscalPeriod",
        "earningsDate",
        "fiscalEndDate",
        "epsActual",
        "epsEstimate",
        "epsReportedActual",
        "epsReportedEstimate",
        "salesActual",
        "salesEstimate",
        "epsAnalysts",
        "epsReportedAnalysts",
        "salesAnalysts",
    ]
    assert all(col in result.columns for col in expected_columns)
    assert result.shape[0] > 0, "Earnings annual data should not be empty"
    assert result["ticker"].notnull().all(), "Ticker column should not have null values"
    assert (
        result["fiscalPeriod"].notnull().all()
    ), "Fiscal period column should not have null values"


@pytest.mark.parametrize(
    "ticker",
    [
        "AAPL",
        "GOOGL",
        "TSLA",
        "BAC",
    ],
)
def test_finviz_earnings_data(ticker):
    """Test the earnings_data method of FinvizInterface."""
    finviz = FinvizInterface(ticker=ticker)
    result = finviz.finviz_earnings_data()

    assert isinstance(result, pd.DataFrame)
    expected_columns = [
        "ticker",
        "fiscalPeriod",
        "earningsDate",
        "fiscalEndDate",
        "epsActual",
        "epsEstimate",
        "epsReportedActual",
        "epsReportedEstimate",
        "salesActual",
        "salesEstimate",
        "epsAnalysts",
        "epsReportedAnalysts",
        "salesAnalysts",
    ]
    assert all(col in result.columns for col in expected_columns)
    assert result.shape[0] > 0, "Earnings data should not be empty"
    assert result["ticker"].notnull().all(), "Ticker column should not have null values"


@pytest.mark.parametrize(
    "ticker",
    [
        "AAPL",
        "GOOGL",
        "TSLA",
        "BAC",
    ],
)
def test_finviz_overall_dividend(ticker):
    """Test the overall_dividend method of FinvizInterface."""
    finviz = FinvizInterface(ticker=ticker)
    result = finviz.finviz_overall_dividend()

    assert isinstance(result, pd.DataFrame)
    expected_columns = [
        "lastClose",
        "dividendExDate",
        "dividendEstimate",
        "dividendTTM",
    ]
    assert all(col in result.columns for col in expected_columns)
    assert result.shape[0] > 0, "Overall dividend data should not be empty"


@pytest.mark.parametrize(
    "ticker",
    [
        "AAPL",
        "GOOGL",
        "TSLA",
        "BAC",
    ],
)
def test_finviz_dividends_date_data(ticker):
    """Test the dividends_date_data method of FinvizInterface."""
    finviz = FinvizInterface(ticker=ticker)
    result = finviz.finviz_dividends_date_data()

    assert isinstance(result, pd.DataFrame)
    expected_columns = [
        "Ticker",
        "Exdate",
        "Ordinary",
        "Special",
    ]
    assert all(col in result.columns for col in expected_columns)

    if not result.empty:
        assert result.shape[0] > 0, "Dividend date data should not be empty"
        assert (
            result["Ticker"].notnull().all()
        ), "Ticker column should not have null values"
    assert result.shape[1] > 0, "DataFrame should have 4 columns even if empty"


@pytest.mark.parametrize(
    "ticker",
    [
        "AAPL",
        "GOOGL",
        "TSLA",
        "BAC",
    ],
)
def test_finviz_dividends_annual_data(ticker):
    """Test the dividends_annual_data method of FinvizInterface."""
    finviz = FinvizInterface(ticker=ticker)
    result = finviz.finviz_dividends_annual_data()

    assert isinstance(result, pd.DataFrame)
    expected_columns = [
        "Ticker",
        "FiscalPeriod",
        "Amount",
        "Yield",
        "Payout",
        "Estimate",
    ]
    assert all(col in result.columns for col in expected_columns)

    if not result.empty:
        assert result.shape[0] > 0, "Dividend annual data should not be empty"
        assert (
            result["Ticker"].notnull().all()
        ), "Ticker column should not have null values"
    assert (
        result.shape[1] > 0
    ), "DataFrame should have more than 0 columns even if empty"


@pytest.mark.parametrize(
    "ticker",
    [
        "AAPL",
        "GOOGL",
        "TSLA",
        "BAC",
    ],
)
def test__finviz_revenue_raw_data(ticker):
    """Test the _finviz_revenue_raw_data method of FinvizInterface."""
    finviz = FinvizInterface(ticker=ticker)
    result = finviz._finviz_revenue_raw_data()

    assert isinstance(result, dict)


@pytest.mark.parametrize(
    "ticker",
    [
        "AAPL",
        "GOOGL",
        "TSLA",
        "BAC",
    ],
)
def test_finviz_revenue_by_products_and_services(ticker):
    """Test the finviz_revenue_by_products_and_services method of FinvizInterface."""
    finviz = FinvizInterface(ticker=ticker)
    result = finviz.finviz_revenue_by_products_and_services()

    assert isinstance(result, dict)
    for key, df in result.items():
        assert isinstance(df, pd.DataFrame)
        assert not df.empty, f"DataFrame for {key} should not be empty"


@pytest.mark.parametrize(
    "ticker",
    [
        "AAPL",
        "GOOGL",
        "TSLA",
        "BAC",
    ],
)
def test_finviz_revenue_by_segment(ticker):
    """Test the finviz_revenue_by_segment method of FinvizInterface."""
    finviz = FinvizInterface(ticker=ticker)
    result = finviz.finviz_revenue_by_segment()

    assert isinstance(result, dict)
    for key, df in result.items():
        assert isinstance(df, pd.DataFrame)
        assert not df.empty, f"DataFrame for {key} should not be empty"


@pytest.mark.parametrize(
    "ticker",
    [
        "AAPL",
        "GOOGL",
        "TSLA",
        "BAC",
    ],
)
def test_finviz_revenue_by_regions(ticker):
    """Test the finviz_revenue_by_regions method of FinvizInterface."""
    finviz = FinvizInterface(ticker=ticker)
    result = finviz.finviz_revenue_by_regions()

    assert isinstance(result, dict)
    for key, df in result.items():
        assert isinstance(df, pd.DataFrame)
        assert not df.empty, f"DataFrame for {key} should not be empty"


@pytest.mark.skipif(skip_test, reason="Skipping in GH action as it throws error 403")
@pytest.mark.parametrize(
    "ticker, logarithmic",
    [
        ("AAPL", False),
        ("AAPL", True),
        ("MSFT", True),
    ],
)
def test_plot_finviz_revenue_by_regions(ticker, logarithmic):
    """Test the plot_finviz_revenue_by_regions method of FinvizInterface."""
    finviz = FinvizInterface(ticker=ticker)
    result = finviz.plot_finviz_revenue_by_regions(logarithmic=logarithmic)

    assert result is None


@pytest.mark.skipif(skip_test, reason="Skipping in GH action as it throws error 403")
@pytest.mark.parametrize(
    "ticker, logarithmic",
    [
        ("AAPL", False),
        ("AAPL", True),
        ("MSFT", True),
    ],
)
def test_plot_finviz_revenue_by_segments(ticker, logarithmic):
    """Test the plot_finviz_revenue_by_segments method of FinvizInterface."""
    finviz = FinvizInterface(ticker=ticker)
    result = finviz.plot_finviz_revenue_by_segments(logarithmic=logarithmic)

    assert result is None


@pytest.mark.skipif(skip_test, reason="Skipping in GH action as it throws error 403")
@pytest.mark.parametrize(
    "ticker, logarithmic",
    [("AAPL", False), ("AAPL", True), ("MSFT", True), ("NVDA", True), ("NVDA", False)],
)
def test_plot_finviz_revenue_by_products_and_services(ticker, logarithmic):
    """Test the plot_finviz_revenue_by_products_and_services method of FinvizInterface."""
    finviz = FinvizInterface(ticker=ticker)
    result = finviz.plot_finviz_revenue_by_products_and_services(
        logarithmic=logarithmic
    )

    assert result is None
