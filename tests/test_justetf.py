"""
Module to test the justetf module.
"""

import pandas as pd
import pytest

from stockdex.justetf import JustETF


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
    etf = JustETF(isin)

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
    etf = JustETF(isin)

    wkn = etf.wkn
    assert isinstance(wkn, str)
    assert wkn == expected
