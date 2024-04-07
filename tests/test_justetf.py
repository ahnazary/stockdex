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
        ("IE00B53SZB19"),
    ],
)
def test_etf_general_info(isin: str) -> None:
    """
    Test the ter property of the JustETF class
    """
    etf = Ticker(isin=isin, security_type="etf")

    etf_general_info = etf.etf_general_info
    assert isinstance(etf_general_info, pd.DataFrame)
    assert etf_general_info.shape[0] == 1
    assert etf_general_info.shape[1] >= 5
    assert etf_general_info.iloc[0]["TER"] != ""
    for i in range(1, etf_general_info.shape[1]):
        assert etf_general_info.iloc[0][i] != ""


@pytest.mark.parametrize(
    "isin, expected",
    [
        ("IE00B4L5Y983", "A0RPWH"),
        ("IE00B53SZB19", "A0YEDL"),
    ],
)
def test_etf_wkn(isin: str, expected: str) -> None:
    """
    Test the wkn property of the JustETF class
    """
    etf = Ticker(isin=isin, security_type="etf")

    etf_wkn = etf.etf_wkn
    assert isinstance(etf_wkn, str)
    assert etf_wkn == expected


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
        ("IE00B53SZB19"),
    ],
)
def test_etf_description(isin: str) -> None:
    """
    Test the description property of the JustETF class
    """
    etf = Ticker(isin=isin, security_type="etf")

    etf_description = etf.etf_description
    assert isinstance(etf_description, str)
    assert len(etf_description) > 0


# @pytest.mark.parametrize(
#     "isin",
#     [
#         ("IE00B4L5Y983"),
#         ("IE00B53SZB19"),
#     ],
# )
# def test_etf_quote(isin: str) -> None:
#     """
#     Test the quote property of the JustETF class
#     """
#     etf = Ticker(isin=isin, security_type="etf")

#     quote = etf.etf_quote
#     assert isinstance(quote, pd.DataFrame)


@pytest.mark.parametrize(
    "isin",
    [
        ("IE00B4L5Y983"),
        ("IE00B53SZB19"),
    ],
)
def test_etf_basics(isin: str) -> None:
    """
    Test the etf_basics property of the JustETF class
    """
    etf = Ticker(isin=isin, security_type="etf")

    etf_basics = etf.etf_basics
    assert isinstance(etf_basics, pd.DataFrame)
    assert etf_basics.shape[0] == 1
    assert etf_basics.shape[1] >= 5

    expceted_columns = [
        "Fund size",
        "Fund domicile",
        "Legal structure",
        "Replication",
    ]

    for column in expceted_columns:
        assert column in etf_basics.columns
        assert etf_basics[column].iloc[0] != ""


@pytest.mark.parametrize(
    "isin",
    [
        ("IE00B4L5Y983"),
        ("IE00B53SZB19"),
    ],
)
def test_etf_holdings_companies(isin: str) -> None:
    """
    Test the etf_holdings property of the JustETF class
    """
    etf = Ticker(isin=isin, security_type="etf")

    etf_holdings = etf.etf_holdings_companies
    assert isinstance(etf_holdings, pd.DataFrame)
    assert etf_holdings.shape[0] == 10
    assert etf_holdings.shape[1] == 1


@pytest.mark.parametrize(
    "isin",
    [
        ("IE00B4L5Y983"),
        ("IE00B53SZB19"),
    ],
)
def test_etf_holdings_countries(isin: str) -> None:
    """
    Test the etf_holdings property of the JustETF class
    """

    etf = Ticker(isin=isin, security_type="etf")

    etf_holdings = etf.etf_holdings_countries
    assert isinstance(etf_holdings, pd.DataFrame)
    assert etf_holdings.shape[0] >= 2
    assert etf_holdings.shape[1] == 1


@pytest.mark.parametrize(
    "isin",
    [
        ("IE00B4L5Y983"),
        ("IE00B53SZB19"),
    ],
)
def test_etf_holdings_sectors(isin: str) -> None:
    """
    Test the etf_holdings property of the JustETF class
    """

    etf = Ticker(isin=isin, security_type="etf")

    etf_holdings = etf.etf_holdings_sectors
    assert isinstance(etf_holdings, pd.DataFrame)
    assert etf_holdings.shape[0] >= 2
    assert etf_holdings.shape[1] == 1
