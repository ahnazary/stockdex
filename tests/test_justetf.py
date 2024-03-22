"""
Module to test the justetf module.
"""

import pandas as pd
import pytest

from stockdex.ticker import Ticker


@pytest.mark.parametrize(
    "isin",
    [
        ("IE00B4L5Y983"),
    ],
)
def test_general_info(isin: str) -> None:
    """
    Test the ter property of the JustETF class
    """
    etf = Ticker(isin=isin, security_type="etf")

    general_info = etf.general_info
    assert isinstance(general_info, pd.DataFrame)
    assert general_info.shape[0] == 1
    assert general_info.shape[1] >= 5


@pytest.mark.parametrize(
    "isin, expected",
    [
        ("IE00B4L5Y983", "A0RPWH"),
    ],
)
def test_wkn(isin: str, expected: str) -> None:
    """
    Test the wkn property of the JustETF class
    """
    etf = Ticker(isin=isin, security_type="etf")

    wkn = etf.wkn
    assert isinstance(wkn, str)
    assert wkn == expected


def test_no_isin() -> None:
    """
    Test the NoISINError exception
    """
    with pytest.raises(Exception):
        Ticker(isin="", security_type="etf")


@pytest.mark.parametrize(
    "isin",
    [
        ("IE00B4L5Y983"),
    ],
)
def test_description(isin: str) -> None:
    """
    Test the description property of the JustETF class
    """
    etf = Ticker(isin=isin, security_type="etf")

    description = etf.description
    assert isinstance(description, str)
    assert len(description) > 0
