import pandas as pd
import pytest

from stockdex.ticker import Ticker


@pytest.mark.parametrize(
    "ticker",
    [
        ("PANW"),
        ("AAPL"),
        ("ASML"),
        ("CAT"),
        ("BAC"),
    ],
)
def test_macrotrends_income_statement(ticker):
    ticker = Ticker(ticker=ticker)
    macrotrends_income_statement = ticker.macrotrends_income_statement()

    # Check if the response is as expected
    assert isinstance(macrotrends_income_statement, pd.DataFrame)
    assert macrotrends_income_statement.shape[0] > 0
    assert macrotrends_income_statement.shape[1] > 0
    assert "Revenue" in macrotrends_income_statement.index
