"""
Module to test the YahooWeb class.
"""

import pandas as pd
import pytest

from stockdex.exceptions import WrongSecurityType
from stockdex.ticker import TickerFactory


@pytest.mark.parametrize(
    "ticker",
    [
        ("AAPL"),
        ("GOOGL"),
        ("MSFT"),
    ],
)
def test_cashflow_web(ticker):
    ticker = TickerFactory(ticker, data_source="yahoo_web").ticker
    cashflow_web_df = ticker.cashflow_web

    # Check if the response is as expected
    assert isinstance(cashflow_web_df, pd.DataFrame)
    assert cashflow_web_df.shape[0] >= 3
    assert cashflow_web_df.shape[1] > 5


def test_cashflow_web_wrong_security_type():
    with pytest.raises(WrongSecurityType):
        ticker = TickerFactory(
            ticker="AAPL", security_type="etf", data_source="yahoo_web"
        ).ticker
        ticker.cashflow_web


@pytest.mark.parametrize(
    "ticker",
    [("AAPL"), ("GOOGL"), ("TSLA")],
)
def test_balance_sheet_web(ticker):
    ticker = TickerFactory(ticker, data_source="yahoo_web").ticker
    balance_sheet_web_df = ticker.balance_sheet_web

    # Check if the response is as expected
    assert isinstance(balance_sheet_web_df, pd.DataFrame)
    assert balance_sheet_web_df.shape[0] >= 3
    assert balance_sheet_web_df.shape[1] > 5


def test_balance_sheet_web_wrong_security_type():
    with pytest.raises(WrongSecurityType):
        ticker = TickerFactory(
            ticker="AAPL", security_type="etf", data_source="yahoo_web"
        ).ticker
        ticker.balance_sheet_web


@pytest.mark.parametrize(
    "ticker",
    [("AAPL"), ("GOOGL"), ("TSLA")],
)
def test_income_stmt_web(ticker):
    ticker = TickerFactory(ticker, data_source="yahoo_web").ticker
    income_stmt_web_df = ticker.income_stmt_web

    # Check if the response is as expected
    assert isinstance(income_stmt_web_df, pd.DataFrame)
    assert income_stmt_web_df.shape[0] >= 3
    assert income_stmt_web_df.shape[1] > 5


def test_income_stmt_web_wrong_security_type():
    with pytest.raises(WrongSecurityType):
        ticker = TickerFactory(
            ticker="AAPL", security_type="etf", data_source="yahoo_web"
        ).ticker
        ticker.income_stmt_web


@pytest.mark.parametrize(
    "ticker, security_type",
    [
        ("AAPL", "stock"),
        ("GOOGL", "stock"),
        ("MSFT", "stock"),
        ("QQQ", "etf"),
    ],
)
def test_calls(ticker, security_type):
    ticker = TickerFactory(
        ticker, security_type=security_type, data_source="yahoo_web"
    ).ticker
    calls = ticker.calls

    # Check if the response is as expected
    assert isinstance(calls, pd.DataFrame)
    assert calls.shape[0] > 0


def test_calls_wrong_security_type():
    with pytest.raises(WrongSecurityType):
        ticker = TickerFactory(
            ticker="AAPL", security_type="wrong_type", data_source="yahoo_web"
        ).ticker
        ticker.calls


@pytest.mark.parametrize(
    "ticker, security_type",
    [
        ("AAPL", "stock"),
        ("GOOGL", "stock"),
        ("MSFT", "stock"),
        ("QQQ", "etf"),
    ],
)
def test_puts(ticker, security_type):
    ticker = TickerFactory(
        ticker, security_type=security_type, data_source="yahoo_web"
    ).ticker
    puts = ticker.puts

    # Check if the response is as expected
    assert isinstance(puts, pd.DataFrame)
    assert puts.shape[0] > 0


def test_puts_wrong_security_type():
    with pytest.raises(WrongSecurityType):
        ticker = TickerFactory(
            ticker="AAPL", security_type="wrong_type", data_source="yahoo_web"
        ).ticker
        ticker.puts


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
    ticker = TickerFactory(ticker, data_source="yahoo_web").ticker
    description = ticker.description

    # Check if the response is as expected
    assert isinstance(description, str)
    assert len(description) > 0


@pytest.mark.parametrize(
    "ticker",
    [
        ("AAPL"),
        ("TSLA"),
    ],
)
def test_key_executives(ticker):
    ticker = TickerFactory(ticker, data_source="yahoo_web").ticker
    key_executives = ticker.key_executives

    # Check if the response is as expected
    assert isinstance(key_executives, pd.DataFrame)
    assert key_executives.shape[0] > 0


def test_key_executives_wrong_security_type():
    with pytest.raises(WrongSecurityType):
        ticker = TickerFactory(
            ticker="AAPL", security_type="etf", data_source="yahoo_web"
        ).ticker
        ticker.key_executives


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
    ticker = TickerFactory(ticker, data_source="yahoo_web").ticker
    corporate_governance = ticker.corporate_governance

    # Check if the response is as expected
    assert isinstance(corporate_governance, str)
    assert len(corporate_governance) > 0


def test_corporate_governance_wrong_security_type():
    with pytest.raises(WrongSecurityType):
        ticker = TickerFactory(
            ticker="AAPL", security_type="etf", data_source="yahoo_web"
        ).ticker
        ticker.corporate_governance


@pytest.mark.parametrize(
    "ticker",
    [
        ("AAPL"),
        ("GOOGL"),
        ("ASML"),
        ("TSLA"),
    ],
)
def test_major_holders(ticker):
    ticker = TickerFactory(ticker, data_source="yahoo_web").ticker
    major_holders = ticker.major_holders

    # Check if the response is as expected
    assert isinstance(major_holders, pd.DataFrame)
    assert major_holders.shape[0] > 0
    assert major_holders.shape[1] == 2


def test_major_holders_wrong_security_type():
    with pytest.raises(WrongSecurityType):
        ticker = TickerFactory(
            ticker="AAPL", security_type="etf", data_source="yahoo_web"
        ).ticker
        ticker.major_holders


@pytest.mark.parametrize(
    "ticker",
    [
        ("AAPL"),
        ("GOOGL"),
        ("ASML"),
        ("TSLA"),
    ],
)
def test_top_institutional_holders(ticker):
    ticker = TickerFactory(ticker, data_source="yahoo_web").ticker
    top_institutional_holders = ticker.top_institutional_holders

    # Check if the response is as expected
    assert isinstance(top_institutional_holders, pd.DataFrame)
    assert top_institutional_holders.shape[0] > 0
    assert top_institutional_holders.shape[1] == 5


def test_top_institutional_holders_wrong_security_type():
    with pytest.raises(WrongSecurityType):
        ticker = TickerFactory(
            ticker="AAPL", security_type="etf", data_source="yahoo_web"
        ).ticker
        ticker.top_institutional_holders


@pytest.mark.parametrize(
    "ticker",
    [
        ("AAPL"),
        ("GOOGL"),
        ("ASML"),
        ("TSLA"),
    ],
)
def test_top_mutual_fund_holders(ticker):
    ticker = TickerFactory(ticker, data_source="yahoo_web").ticker
    top_mutual_fund_holders = ticker.top_mutual_fund_holders

    # Check if the response is as expected
    assert isinstance(top_mutual_fund_holders, pd.DataFrame)
    assert top_mutual_fund_holders.shape[0] > 0
    assert top_mutual_fund_holders.shape[1] == 5


def test_top_mutual_fund_holders_wrong_security_type():
    with pytest.raises(WrongSecurityType):
        ticker = TickerFactory(
            ticker="AAPL", security_type="etf", data_source="yahoo_web"
        ).ticker
        ticker.top_mutual_fund_holders


@pytest.mark.parametrize(
    "ticker",
    [
        ("AAPL"),
        ("GOOGL"),
        ("MSFT"),
    ],
)
def test_summary(ticker):
    ticker = TickerFactory(ticker, data_source="yahoo_web").ticker
    summary_df = ticker.summary

    # Check if the response is as expected
    assert isinstance(summary_df, pd.DataFrame)
    assert summary_df.shape[0] > 0


def test_summary_wrong_security_type():
    with pytest.raises(WrongSecurityType):
        ticker = TickerFactory(
            ticker="AAPL", security_type="etf", data_source="yahoo_web"
        ).ticker
        ticker.summary


@pytest.mark.parametrize(
    "ticker",
    [
        ("AAPL"),
        ("GOOGL"),
        ("MSFT"),
    ],
)
def test_analysis(ticker):
    ticker = TickerFactory(ticker, data_source="yahoo_web").ticker
    analysis_df = ticker.analysis

    # Check if the response is as expected
    assert isinstance(analysis_df, pd.DataFrame)
    assert analysis_df.shape[0] > 0


def test_analysis_wrong_security_type():
    with pytest.raises(WrongSecurityType):
        ticker = TickerFactory(
            ticker="AAPL", security_type="etf", data_source="yahoo_web"
        ).ticker
        ticker.analysis


# @pytest.mark.skip(
#     reason="This test is skipped because github actions is not able to access the yahoo finance page"  # noqa E501
# )
@pytest.mark.parametrize(
    "ticker",
    [
        ("AAPL"),
        ("GOOGL"),
        ("MSFT"),
    ],
)
def test_valuation_measures(ticker):
    ticker = TickerFactory(ticker, data_source="yahoo_web").ticker
    valuation_measures_df = ticker.valuation_measures

    # Check if the response is as expected
    assert isinstance(valuation_measures_df, pd.DataFrame)
    assert valuation_measures_df.shape[0] > 0
    assert valuation_measures_df.shape[1] > 3
    assert isinstance(valuation_measures_df.iloc[0, 0], (int, float, str))


def test_valuation_measures_wrong_security_type():
    with pytest.raises(WrongSecurityType):
        ticker = TickerFactory(
            ticker="AAPL", security_type="etf", data_source="yahoo_web"
        ).ticker
        ticker.valuation_measures


@pytest.mark.parametrize(
    "ticker",
    [
        ("AAPL"),
        ("GOOGL"),
        ("MSFT"),
    ],
)
def test_financial_highlights(ticker):
    ticker = TickerFactory(ticker, data_source="yahoo_web").ticker
    financial_highlights_df = ticker.financial_highlights

    # Check if the response is as expected
    assert isinstance(financial_highlights_df, pd.DataFrame)
    assert financial_highlights_df.shape[0] > 0
    assert financial_highlights_df.shape[1] == 1
    assert isinstance(financial_highlights_df.iloc[0, 0], (int, float, str))


def test_financial_highlights_wrong_security_type():
    with pytest.raises(WrongSecurityType):
        ticker = TickerFactory(
            ticker="AAPL", security_type="etf", data_source="yahoo_web"
        ).ticker
        ticker.financial_highlights


@pytest.mark.parametrize(
    "ticker",
    [
        ("AAPL"),
        ("GOOGL"),
        ("MSFT"),
    ],
)
def test_trading_information(ticker):
    ticker = TickerFactory(ticker, data_source="yahoo_web").ticker
    trading_information_df = ticker.trading_information

    # Check if the response is as expected
    assert isinstance(trading_information_df, pd.DataFrame)
    assert trading_information_df.shape[0] > 0
    assert trading_information_df.shape[1] == 1
    assert isinstance(trading_information_df.iloc[0, 0], (int, float, str))


def test_trading_information_wrong_security_type():
    with pytest.raises(WrongSecurityType):
        ticker = TickerFactory(
            ticker="AAPL", security_type="etf", data_source="yahoo_web"
        ).ticker
        ticker.trading_information
