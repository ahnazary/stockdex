"""
Module to test the justetf module.
"""

import os

import pandas as pd
import pytest

from stockdex.exceptions import WrongSecurityType
from stockdex.ticker import Ticker

skip_test = bool(os.getenv("SKIP_TEST", False))


@pytest.mark.skipif(
    skip_test, reason="Skipping in GH action as it reaches the limit of requests"
)
@pytest.mark.parametrize(
    "isin",
    [
        ("IE00B4L5Y983"),
        ("IE00B53SZB19"),
    ],
)
def test_justetf_general_info(isin: str) -> None:
    """
    Test the ter property of the JustETF class
    """
    etf = Ticker(isin=isin, security_type="etf")

    justetf_general_info = etf.justetf_general_info
    assert isinstance(justetf_general_info, pd.DataFrame)
    assert justetf_general_info.shape[0] == 1
    assert justetf_general_info.shape[1] >= 5
    assert justetf_general_info.iloc[0]["TER"] != ""
    for i in range(1, justetf_general_info.shape[1]):
        assert justetf_general_info.iloc[0][i] != ""


@pytest.mark.skipif(
    skip_test, reason="Skipping in GH action as it reaches the limit of requests"
)
def test_justetf_general_info_wrong_security_type() -> None:
    """
    Test the WrongSecurityType exception
    """
    with pytest.raises(WrongSecurityType):
        ticker = Ticker(isin="IE00B4L5Y983", security_type="wrong_security_type")
        ticker.justetf_general_info


@pytest.mark.skipif(
    skip_test, reason="Skipping in GH action as it reaches the limit of requests"
)
@pytest.mark.parametrize(
    "isin, expected",
    [
        ("IE00B4L5Y983", "A0RPWH"),
        ("IE00B53SZB19", "A0YEDL"),
    ],
)
def test_justetf_wkn(isin: str, expected: str) -> None:
    """
    Test the wkn property of the JustETF class
    """
    etf = etf = Ticker(isin=isin, security_type="etf")

    justetf_wkn = etf.justetf_wkn
    assert isinstance(justetf_wkn, str)
    assert justetf_wkn == expected


def test_justetf_wkn_wrong_security_type() -> None:
    """
    Test the WrongSecurityType exception
    """
    with pytest.raises(WrongSecurityType):
        ticker = Ticker(
            isin="IE00B4L5Y983",
            security_type="wrong_security_type",
        )
        ticker.justetf_wkn


@pytest.mark.skipif(
    skip_test, reason="Skipping in GH action as it reaches the limit of requests"
)
def test_no_isin() -> None:
    """
    Test the NoISINError exception
    """
    with pytest.raises(Exception):
        Ticker(isin="")


@pytest.mark.parametrize(
    "isin",
    [
        ("IE00B4L5Y983"),
    ],
)
def test_justetf_description(isin: str) -> None:
    """
    Test the description property of the JustETF class
    """
    etf = etf = Ticker(isin=isin, security_type="etf")

    justetf_description = etf.justetf_description
    assert isinstance(justetf_description, str)
    assert len(justetf_description) > 0


@pytest.mark.skipif(
    skip_test, reason="Skipping in GH action as it reaches the limit of requests"
)
def test_justetf_description_wrong_security_type() -> None:
    """
    Test the WrongSecurityType exception
    """
    with pytest.raises(WrongSecurityType):
        ticker = Ticker(
            isin="IE00B4L5Y983",
            security_type="wrong_security_type",
        )
        ticker.justetf_description


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
#     etf = etf = Ticker(isin=isin, security_type="etf")

#     quote = etf.etf_quote
#     assert isinstance(quote, pd.DataFrame)


@pytest.mark.skipif(
    skip_test, reason="Skipping in GH action as it reaches the limit of requests"
)
@pytest.mark.parametrize(
    "isin",
    [
        ("IE00B4L5Y983"),
        ("IE00B53SZB19"),
    ],
)
def test_justetf_basics(isin: str) -> None:
    """
    Test the justetf_basics property of the JustETF class
    """
    etf = etf = Ticker(isin=isin, security_type="etf")

    justetf_basics = etf.justetf_basics
    assert isinstance(justetf_basics, pd.DataFrame)
    assert justetf_basics.shape[0] == 1
    assert justetf_basics.shape[1] >= 5

    expceted_columns = [
        "Fund size",
        "Fund domicile",
        "Legal structure",
        "Replication",
    ]

    for column in expceted_columns:
        assert column in justetf_basics.columns
        assert justetf_basics[column].iloc[0] != ""


def test_justetf_basics_wrong_security_type() -> None:
    """
    Test the WrongSecurityType exception
    """
    with pytest.raises(WrongSecurityType):
        ticker = Ticker(
            isin="IE00B4L5Y983",
            security_type="wrong_security_type",
        )
        ticker.justetf_basics


@pytest.mark.skipif(
    skip_test, reason="Skipping in GH action as it reaches the limit of requests"
)
@pytest.mark.parametrize(
    "isin",
    [
        ("IE00B4L5Y983"),
        ("IE00B53SZB19"),
    ],
)
def test_justetf_holdings_companies(isin: str) -> None:
    """
    Test the etf_holdings property of the JustETF class
    """
    etf = etf = Ticker(isin=isin, security_type="etf")

    etf_holdings = etf.justetf_holdings_companies
    assert isinstance(etf_holdings, pd.DataFrame)
    assert etf_holdings.shape[0] == 10
    assert etf_holdings.shape[1] == 1


@pytest.mark.skipif(
    skip_test, reason="Skipping in GH action as it reaches the limit of requests"
)
def test_justetf_holdings_companies_wrong_security_type() -> None:
    """
    Test the WrongSecurityType exception
    """
    with pytest.raises(WrongSecurityType):
        ticker = Ticker(
            isin="IE00B4L5Y983",
            security_type="wrong_security_type",
        )
        ticker.justetf_holdings_companies


@pytest.mark.skipif(
    skip_test, reason="Skipping in GH action as it reaches the limit of requests"
)
@pytest.mark.parametrize(
    "isin",
    [
        ("IE00B4L5Y983"),
        ("IE00B53SZB19"),
    ],
)
def test_justetf_holdings_countries(isin: str) -> None:
    """
    Test the etf_holdings property of the JustETF class
    """

    etf = etf = Ticker(isin=isin, security_type="etf")

    etf_holdings = etf.justetf_holdings_countries
    assert isinstance(etf_holdings, pd.DataFrame)
    assert etf_holdings.shape[0] >= 2
    assert etf_holdings.shape[1] == 1


@pytest.mark.skipif(
    skip_test, reason="Skipping in GH action as it reaches the limit of requests"
)
def test_justetf_holdings_countries_wrong_security_type() -> None:
    """
    Test the WrongSecurityType exception
    """
    with pytest.raises(WrongSecurityType):
        ticker = Ticker(
            isin="IE00B4L5Y983",
            security_type="wrong_security_type",
        )
        ticker.justetf_holdings_countries


@pytest.mark.parametrize(
    "isin",
    [
        ("IE00B4L5Y983"),
    ],
)
def test_justetf_holdings_sectors(isin: str) -> None:
    """
    Test the etf_holdings property of the JustETF class
    """

    etf = etf = Ticker(isin=isin, security_type="etf")

    etf_holdings = etf.justetf_holdings_sectors
    assert isinstance(etf_holdings, pd.DataFrame)
    assert etf_holdings.shape[0] >= 2
    assert etf_holdings.shape[1] == 1


@pytest.mark.skipif(
    skip_test, reason="Skipping in GH action as it reaches the limit of requests"
)
def test_justetf_holdings_sectors_wrong_security_type() -> None:
    """
    Test the WrongSecurityType exception
    """
    with pytest.raises(WrongSecurityType):
        ticker = Ticker(
            isin="IE00B4L5Y983",
            security_type="wrong_security_type",
        )
        ticker.justetf_holdings_sectors


@pytest.mark.skipif(
    skip_test, reason="Skipping in GH action as it reaches the limit of requests"
)
@pytest.mark.parametrize(
    "isin",
    [
        ("IE00B4L5Y983"),
        # ("IE00B53SZB19"),
        # ("IE00BTJRMP35"),
        # ("IE00B4L5Y983"),
    ],
)
def test_justetf_price(isin: str) -> None:
    """
    Test the etf_holdings property of the JustETF class
    """

    etf = etf = Ticker(isin=isin, security_type="etf")

    etf_holdings = etf.justetf_price
    assert isinstance(etf_holdings, pd.DataFrame)
    assert etf_holdings.shape[0] == 1
    assert etf_holdings.shape[1] >= 5
    assert etf_holdings.iloc[0]["price"] != ""
    for i in range(1, etf_holdings.shape[1]):
        assert etf_holdings.iloc[0][i] != ""
