"""
Module to test the YahooWeb class.
"""

import pandas as pd
import pytest

from stockdex.exceptions import WrongSecurityType
from stockdex.ticker import Ticker


@pytest.mark.parametrize(
    "ticker",
    [
        ("AAPL"),
        ("GOOGL"),
        ("MSFT"),
    ],
)
def test_yahoo_web_cashflow(ticker):
    ticker = Ticker(ticker)
    yahoo_web_cashflow_df = ticker.yahoo_web_cashflow

    # Check if the response is as expected
    assert isinstance(yahoo_web_cashflow_df, pd.DataFrame)
    assert yahoo_web_cashflow_df.shape[0] >= 3
    assert yahoo_web_cashflow_df.shape[1] >= 5


def test_yahoo_web_cashflow_wrong_security_type():
    with pytest.raises(WrongSecurityType):
        ticker = Ticker(ticker="AAPL", security_type="etf")
        ticker.yahoo_web_cashflow


@pytest.mark.parametrize(
    "ticker",
    [("AAPL"), ("GOOGL"), ("TSLA"), ("TNK")],
)
def test_yahoo_web_balance_sheet(ticker):
    ticker = Ticker(ticker)
    yahoo_web_balance_sheet_df = ticker.yahoo_web_balance_sheet

    # Check if the response is as expected
    assert isinstance(yahoo_web_balance_sheet_df, pd.DataFrame)
    assert yahoo_web_balance_sheet_df.shape[0] >= 3
    assert yahoo_web_balance_sheet_df.shape[1] >= 4


def test_yahoo_web_balance_sheet_wrong_security_type():
    with pytest.raises(WrongSecurityType):
        ticker = Ticker(ticker="AAPL", security_type="etf")
        ticker.yahoo_web_balance_sheet


@pytest.mark.parametrize(
    "ticker",
    [("AAPL"), ("GOOGL"), ("TSLA")],
)
def test_yahoo_web_income_stmt(ticker):
    ticker = Ticker(ticker)
    yahoo_web_income_stmt_df = ticker.yahoo_web_income_stmt

    # Check if the response is as expected
    assert isinstance(yahoo_web_income_stmt_df, pd.DataFrame)
    assert yahoo_web_income_stmt_df.shape[0] >= 3
    assert yahoo_web_income_stmt_df.shape[1] >= 4


def test_yahoo_web_income_stmt_wrong_security_type():
    with pytest.raises(WrongSecurityType):
        ticker = Ticker(ticker="AAPL", security_type="etf")
        ticker.yahoo_web_income_stmt


@pytest.mark.parametrize(
    "ticker, security_type",
    [
        ("AAPL", "stock"),
        ("GOOGL", "stock"),
        ("MSFT", "stock"),
        ("QQQ", "etf"),
    ],
)
def test_yahoo_web_calls(ticker, security_type):
    ticker = Ticker(ticker, security_type=security_type)
    yahoo_web_calls = ticker.yahoo_web_calls

    # Check if the response is as expected
    assert isinstance(yahoo_web_calls, pd.DataFrame)
    assert yahoo_web_calls.shape[0] > 0


def test_yahoo_web_calls_wrong_security_type():
    with pytest.raises(WrongSecurityType):
        ticker = Ticker(ticker="AAPL", security_type="wrong_type")
        ticker.yahoo_web_calls


@pytest.mark.parametrize(
    "ticker, security_type",
    [
        ("AAPL", "stock"),
        ("GOOGL", "stock"),
        ("MSFT", "stock"),
        ("QQQ", "etf"),
    ],
)
def test_yahoo_web_puts(ticker, security_type):
    ticker = Ticker(ticker, security_type=security_type)
    yahoo_web_puts = ticker.yahoo_web_puts

    # Check if the response is as expected
    assert isinstance(yahoo_web_puts, pd.DataFrame)
    assert yahoo_web_puts.shape[0] > 0


def test_yahoo_web_puts_wrong_security_type():
    with pytest.raises(WrongSecurityType):
        ticker = Ticker(ticker="AAPL", security_type="wrong_type")
        ticker.yahoo_web_puts


@pytest.mark.parametrize(
    "ticker",
    [
        ("AAPL"),
        ("GOOGL"),
        ("ASML"),
        ("TSLA"),
    ],
)
def test_yahoo_web_description(ticker):
    ticker = Ticker(ticker)
    yahoo_web_description = ticker.yahoo_web_description

    # Check if the response is as expected
    assert isinstance(yahoo_web_description, str)
    assert len(yahoo_web_description) > 0


# skip this test because the yahoo finance does not provide the data
@pytest.mark.skip(
    reason="skip this test because the yahoo finance does not provide the data"  # noqa E501
)
@pytest.mark.parametrize(
    "ticker",
    [
        ("AAPL"),
        ("TSLA"),
    ],
)
def test_yahoo_web_key_executives(ticker):
    ticker = Ticker(ticker)
    yahoo_web_key_executives = ticker.yahoo_web_key_executives

    # Check if the response is as expected
    assert isinstance(yahoo_web_key_executives, pd.DataFrame)
    assert yahoo_web_key_executives.shape[0] > 0


def test_yahoo_web_key_executives_wrong_security_type():
    with pytest.raises(WrongSecurityType):
        ticker = Ticker(ticker="AAPL", security_type="etf")
        ticker.yahoo_web_key_executives


@pytest.mark.parametrize(
    "ticker",
    [
        ("AAPL"),
        ("GOOGL"),
        ("ASML"),
        ("TSLA"),
    ],
)
def test_yahoo_web_corporate_governance(ticker):
    ticker = Ticker(ticker)
    yahoo_web_corporate_governance = ticker.yahoo_web_corporate_governance

    # Check if the response is as expected
    assert isinstance(yahoo_web_corporate_governance, str)
    assert len(yahoo_web_corporate_governance) > 0


def test_yahoo_web_corporate_governance_wrong_security_type():
    with pytest.raises(WrongSecurityType):
        ticker = Ticker(ticker="AAPL", security_type="etf")
        ticker.yahoo_web_corporate_governance


@pytest.mark.parametrize(
    "ticker",
    [
        ("AAPL"),
        ("GOOGL"),
        ("ASML"),
        ("TSLA"),
    ],
)
def test_yahoo_web_major_holders(ticker):
    ticker = Ticker(ticker)
    yahoo_web_major_holders = ticker.yahoo_web_major_holders

    # Check if the response is as expected
    assert isinstance(yahoo_web_major_holders, pd.DataFrame)
    assert yahoo_web_major_holders.shape[0] > 0
    assert yahoo_web_major_holders.shape[1] == 2


def test_yahoo_web_major_holders_wrong_security_type():
    with pytest.raises(WrongSecurityType):
        ticker = Ticker(ticker="AAPL", security_type="etf")
        ticker.yahoo_web_major_holders


@pytest.mark.parametrize(
    "ticker",
    [
        ("AAPL"),
        ("GOOGL"),
        ("ASML"),
        ("TSLA"),
    ],
)
def test_yahoo_web_top_institutional_holders(ticker):
    ticker = Ticker(ticker)
    yahoo_web_top_institutional_holders = ticker.yahoo_web_top_institutional_holders

    # Check if the response is as expected
    assert isinstance(yahoo_web_top_institutional_holders, pd.DataFrame)
    assert yahoo_web_top_institutional_holders.shape[0] > 0
    assert yahoo_web_top_institutional_holders.shape[1] == 5


def test_yahoo_web_top_institutional_holders_wrong_security_type():
    with pytest.raises(WrongSecurityType):
        ticker = Ticker(ticker="AAPL", security_type="etf")
        ticker.yahoo_web_top_institutional_holders


@pytest.mark.parametrize(
    "ticker",
    [
        ("AAPL"),
        ("GOOGL"),
        ("ASML"),
        ("TSLA"),
    ],
)
def test_yahoo_web_top_mutual_fund_holders(ticker):
    ticker = Ticker(ticker)
    yahoo_web_top_mutual_fund_holders = ticker.yahoo_web_top_mutual_fund_holders

    # Check if the response is as expected
    assert isinstance(yahoo_web_top_mutual_fund_holders, pd.DataFrame)
    assert yahoo_web_top_mutual_fund_holders.shape[0] > 0
    assert yahoo_web_top_mutual_fund_holders.shape[1] == 5


def test_yahoo_web_top_mutual_fund_holders_wrong_security_type():
    with pytest.raises(WrongSecurityType):
        ticker = Ticker(ticker="AAPL", security_type="etf")
        ticker.yahoo_web_top_mutual_fund_holders


@pytest.mark.parametrize(
    "ticker",
    [
        ("AAPL"),
        ("GOOGL"),
        ("MSFT"),
    ],
)
def test_yahoo_web_summary(ticker):
    ticker = Ticker(ticker)
    yahoo_web_summary_df = ticker.yahoo_web_summary

    # Check if the response is as expected
    assert isinstance(yahoo_web_summary_df, pd.DataFrame)
    assert yahoo_web_summary_df.shape[0] > 0


def test_yahoo_web_summary_wrong_security_type():
    with pytest.raises(WrongSecurityType):
        ticker = Ticker(ticker="AAPL", security_type="etf")
        ticker.yahoo_web_summary


@pytest.mark.parametrize(
    "ticker",
    [
        ("AAPL"),
        ("GOOGL"),
        ("MSFT"),
    ],
)
def test_yahoo_web_valuation_measures(ticker):
    ticker = Ticker(ticker)
    yahoo_web_valuation_measures_df = ticker.yahoo_web_valuation_measures

    # Check if the response is as expected
    assert isinstance(yahoo_web_valuation_measures_df, pd.DataFrame)
    assert yahoo_web_valuation_measures_df.shape[0] > 0
    assert yahoo_web_valuation_measures_df.shape[1] > 3
    assert isinstance(yahoo_web_valuation_measures_df.iloc[0, 0], (int, float, str))


def test_yahoo_web_valuation_measures_wrong_security_type():
    with pytest.raises(WrongSecurityType):
        ticker = Ticker(ticker="AAPL", security_type="etf")
        ticker.yahoo_web_valuation_measures


@pytest.mark.parametrize(
    "ticker",
    [
        ("AAPL"),
        ("GOOGL"),
        ("MSFT"),
    ],
)
def test_yahoo_web_financial_highlights(ticker):
    ticker = Ticker(ticker)
    yahoo_web_financial_highlights_df = ticker.yahoo_web_financial_highlights

    # Check if the response is as expected
    assert isinstance(yahoo_web_financial_highlights_df, pd.DataFrame)
    assert yahoo_web_financial_highlights_df.shape[0] > 0
    assert yahoo_web_financial_highlights_df.shape[1] == 1
    assert isinstance(yahoo_web_financial_highlights_df.iloc[0, 0], (int, float, str))


def test_yahoo_web_financial_highlights_wrong_security_type():
    with pytest.raises(WrongSecurityType):
        ticker = Ticker(ticker="AAPL", security_type="etf")
        ticker.yahoo_web_financial_highlights


@pytest.mark.parametrize(
    "ticker",
    [
        ("AAPL"),
        ("GOOGL"),
        ("MSFT"),
    ],
)
def test_yahoo_web_trading_information(ticker):
    ticker = Ticker(ticker)
    yahoo_web_trading_information_df = ticker.yahoo_web_trading_information

    # Check if the response is as expected
    assert isinstance(yahoo_web_trading_information_df, pd.DataFrame)
    assert yahoo_web_trading_information_df.shape[0] > 0
    assert yahoo_web_trading_information_df.shape[1] == 1
    assert isinstance(yahoo_web_trading_information_df.iloc[0, 0], (int, float, str))


def test_yahoo_web_trading_information_wrong_security_type():
    with pytest.raises(WrongSecurityType):
        ticker = Ticker(ticker="AAPL", security_type="etf")
        ticker.yahoo_web_trading_information


@pytest.mark.parametrize(
    "ticker, expected_name",
    [
        ("PANW", "Palo Alto Networks"),
        ("AAPL", "Apple Inc"),
        ("GOOGL", "Alphabet Inc"),
        ("MSFT", "Microsoft Corporation"),
    ],
)
def test_yahoo_web_full_name(ticker, expected_name):
    ticker = Ticker(ticker)
    yahoo_web_full_name = ticker.yahoo_web_full_name

    # Check if the response is as expected
    assert isinstance(yahoo_web_full_name, str)
    assert len(yahoo_web_full_name) > 0
    assert yahoo_web_full_name == expected_name


@pytest.mark.parametrize(
    "ticker",
    [
        ("AAPL"),
        ("GOOGL"),
        ("MSFT"),
    ],
)
def test_yahoo_web_earnings_estimate(ticker):
    ticker = Ticker(ticker)
    yahoo_web_earnings_estimate = ticker.yahoo_web_earnings_estimate

    # Check if the response is as expected
    assert isinstance(yahoo_web_earnings_estimate, pd.DataFrame)
    assert yahoo_web_earnings_estimate.shape[0] >= 2
    assert yahoo_web_earnings_estimate.shape[1] >= 5


def test_yahoo_web_earnings_estimate_wrong_security_type():
    with pytest.raises(WrongSecurityType):
        ticker = Ticker(ticker="AAPL", security_type="etf")
        ticker.yahoo_web_earnings_estimate


@pytest.mark.parametrize(
    "ticker",
    [
        ("AAPL"),
        ("GOOGL"),
        ("MSFT"),
    ],
)
def test_yahoo_web_revenue_estimate(ticker):
    ticker = Ticker(ticker)
    yahoo_web_revenue_estimate = ticker.yahoo_web_revenue_estimate

    # Check if the response is as expected
    assert isinstance(yahoo_web_revenue_estimate, pd.DataFrame)
    assert yahoo_web_revenue_estimate.shape[0] >= 2
    assert yahoo_web_revenue_estimate.shape[1] >= 5


def test_yahoo_web_revenue_estimate_wrong_security_type():
    with pytest.raises(WrongSecurityType):
        ticker = Ticker(ticker="AAPL", security_type="etf")
        ticker.yahoo_web_revenue_estimate


@pytest.mark.parametrize(
    "ticker",
    [
        ("AAPL"),
        ("GOOGL"),
        ("MSFT"),
    ],
)
def test_yahoo_web_earnings_history(ticker):
    ticker = Ticker(ticker)
    yahoo_web_earnings_history = ticker.yahoo_web_earnings_history

    # Check if the response is as expected
    assert isinstance(yahoo_web_earnings_history, pd.DataFrame)
    assert yahoo_web_earnings_history.shape[0] >= 2
    assert yahoo_web_earnings_history.shape[1] >= 5


def test_yahoo_web_earnings_history_wrong_security_type():
    with pytest.raises(WrongSecurityType):
        ticker = Ticker(ticker="AAPL", security_type="etf")
        ticker.yahoo_web_earnings_history


@pytest.mark.parametrize(
    "ticker",
    [
        ("AAPL"),
        ("GOOGL"),
        ("MSFT"),
    ],
)
def test_yahoo_web_eps_trend(ticker):
    ticker = Ticker(ticker)
    yahoo_web_eps_trend = ticker.yahoo_web_eps_trend

    # Check if the response is as expected
    assert isinstance(yahoo_web_eps_trend, pd.DataFrame)
    assert yahoo_web_eps_trend.shape[0] >= 2
    assert yahoo_web_eps_trend.shape[1] >= 5


def test_yahoo_web_eps_trend_wrong_security_type():
    with pytest.raises(WrongSecurityType):
        ticker = Ticker(ticker="AAPL", security_type="etf")
        ticker.yahoo_web_eps_trend


@pytest.mark.parametrize(
    "ticker",
    [
        ("AAPL"),
        ("GOOGL"),
        ("MSFT"),
    ],
)
def test_yahoo_web_eps_revisions(ticker):
    ticker = Ticker(ticker)
    yahoo_web_eps_revisions = ticker.yahoo_web_eps_revisions

    # Check if the response is as expected
    assert isinstance(yahoo_web_eps_revisions, pd.DataFrame)
    assert yahoo_web_eps_revisions.shape[0] >= 2
    assert yahoo_web_eps_revisions.shape[1] >= 5


def test_yahoo_web_eps_revisions_wrong_security_type():
    with pytest.raises(WrongSecurityType):
        ticker = Ticker(ticker="AAPL", security_type="etf")
        ticker.yahoo_web_eps_revisions


@pytest.mark.parametrize(
    "ticker",
    [
        ("AAPL"),
        ("GOOGL"),
        ("MSFT"),
    ],
)
def test_yahoo_web_growth_estimates(ticker):
    ticker = Ticker(ticker)
    yahoo_web_growth_estimates = ticker.yahoo_web_growth_estimates

    # Check if the response is as expected
    assert isinstance(yahoo_web_growth_estimates, pd.DataFrame)
    assert yahoo_web_growth_estimates.shape[0] >= 2
    assert yahoo_web_growth_estimates.shape[1] >= 5


def test_yahoo_web_growth_estimates_wrong_security_type():
    with pytest.raises(WrongSecurityType):
        ticker = Ticker(ticker="AAPL", security_type="etf")
        ticker.yahoo_web_growth_estimates
