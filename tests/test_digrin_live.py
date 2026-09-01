"""Small, opt-in smoke suite for the live Digrin website."""

import pandas as pd
import pytest

from stockdex.ticker import Ticker

pytestmark = [pytest.mark.integration, pytest.mark.live]


def test_live_digrin_aapl_assets():
    data = Ticker(ticker="AAPL").digrin_assets_vs_liabilities

    assert isinstance(data, pd.DataFrame)
    assert {"Date", "Assets", "Liabilities"}.issubset(data.columns)
    assert not data.empty


def test_live_digrin_aapl_free_cash_flow():
    # Uses the same /financials page as the assets smoke test. The session
    # cache should serve it without making a second request.
    data = Ticker(ticker="AAPL").digrin_free_cash_flow

    assert isinstance(data, pd.DataFrame)
    assert {"Date", "Free Cash Flow"}.issubset(data.columns)
    assert not data.empty


def test_live_digrin_international_price():
    data = Ticker(ticker="ASML").digrin_price

    assert isinstance(data, pd.DataFrame)
    assert {"Date", "Real price", "Adjusted price"}.issubset(data.columns)
    assert not data.empty
