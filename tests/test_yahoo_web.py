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
def test_cashflow_web(ticker):
    ticker = Ticker(ticker)
    cashflow_web_df = ticker.cashflow_web

    # Check if the response is as expected
    assert isinstance(cashflow_web_df, pd.DataFrame)
    assert cashflow_web_df.shape[0] > 0


def test_cashflow_web_wrong_security_type():
    with pytest.raises(WrongSecurityType):
        ticker = Ticker(isin="AAPL", security_type="etf")
        ticker.cashflow_web
