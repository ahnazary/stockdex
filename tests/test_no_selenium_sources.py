"""Offline tests for the justETF and Nasdaq parsers (no browser, no network)."""

import json
import pathlib
from types import SimpleNamespace

import pandas as pd
import pytest

from stockdex.exceptions import (LayoutChangedError, NoDataError,
                                 WrongSecurityType)
from stockdex.justetf_interface import JUSTETF_PRICE_COLUMNS
from stockdex.ticker import Ticker

FIXTURES = pathlib.Path(__file__).parent / "fixtures"
ISIN = "IE00B4L5Y983"
PROFILE_URL = f"https://www.justetf.com/en/etf-profile.html?isin={ISIN}"


def _response(text="", url=PROFILE_URL, payload=None):
    def json_():
        if payload is None:
            raise ValueError("not JSON")
        return payload

    return SimpleNamespace(text=text, url=url, json=json_)


@pytest.fixture
def etf(monkeypatch):
    html = (FIXTURES / "justetf" / "profile.html").read_text(encoding="utf-8")
    quote = json.loads((FIXTURES / "justetf" / "quote.json").read_text())
    ticker = Ticker(isin=ISIN, security_type="etf")
    calls = []

    def get_response(url, headers=None):
        calls.append((url, headers))
        if "/api/etfs/" in url:
            return _response(payload=quote, url=url)
        return _response(html)

    monkeypatch.setattr(ticker, "get_response", get_response)
    ticker.calls = calls
    return ticker


def test_profile_page_is_fetched_once(etf):
    etf.justetf_general_info
    etf.justetf_basics
    etf.justetf_holdings_companies
    etf.justetf_holdings_countries
    etf.justetf_holdings_sectors
    etf.justetf_wkn
    etf.justetf_description
    assert len(etf.calls) == 1


def test_general_info(etf):
    info = etf.justetf_general_info
    assert info.shape[0] == 1
    assert info.iloc[0]["TER"].strip() == "0.20% p.a."
    assert "Fundsize" in info.columns


def test_basics(etf):
    basics = etf.justetf_basics
    assert basics.shape[0] == 1
    for column in ("Fund size", "Fund domicile", "Legal structure", "Replication"):
        assert basics[column].iloc[0] != ""
    assert basics["Fund domicile"].iloc[0] == "Ireland"


@pytest.mark.parametrize(
    "attribute, index_name, first",
    [
        ("justetf_holdings_companies", "company name", ("NVIDIA Corp.", "5.79%")),
        ("justetf_holdings_countries", "country name", None),
        ("justetf_holdings_sectors", "sector name", None),
    ],
)
def test_weights(etf, attribute, index_name, first):
    frame = getattr(etf, attribute)
    assert frame.index.name == index_name
    assert frame.columns.tolist() == ["shares in percent"]
    assert len(frame) >= 2
    assert frame["shares in percent"].str.endswith("%").all()
    if first:
        assert (frame.index[0], frame.iloc[0, 0]) == first
    if attribute == "justetf_holdings_companies":
        assert len(frame) == 10


def test_identifier_and_description(etf):
    assert etf.justetf_wkn == "IWDA"
    assert "MSCI World" in etf.justetf_description


def test_price_uses_json_api(etf):
    price = etf.justetf_price
    assert price.columns.tolist() == JUSTETF_PRICE_COLUMNS
    row = price.iloc[0]
    assert row["price"] == 129.62
    assert row["currency"] == "EUR"
    assert row["date"] == "2026-10-30"
    assert row["exchange"] == "XETRA"
    assert row["daily_change_percent"] == -1.47
    assert row["52_week_high"] == 131.96
    assert row["time"] is None and row["spread"] is None
    url, headers = etf.calls[-1]
    assert "currency=EUR" in url and headers == {"Accept": "application/json"}


def test_quote_currency(etf):
    etf.justetf_quote("usd")
    assert "currency=USD" in etf.calls[-1][0]


def test_unknown_isin_redirects_to_search(monkeypatch):
    ticker = Ticker(isin="XX0000000000", security_type="etf")
    search = "https://www.justetf.com/en/search.html?query=XX0000000000"
    monkeypatch.setattr(
        ticker, "get_response", lambda url, headers=None: _response("", url=search)
    )
    with pytest.raises(NoDataError):
        ticker.justetf_basics


def test_missing_section_is_layout_change(monkeypatch):
    ticker = Ticker(isin=ISIN, security_type="etf")
    monkeypatch.setattr(
        ticker,
        "get_response",
        lambda url, headers=None: _response("<html><body></body></html>"),
    )
    with pytest.raises(LayoutChangedError):
        ticker.justetf_holdings_sectors


def test_justetf_needs_etf():
    with pytest.raises(WrongSecurityType):
        Ticker(isin=ISIN, security_type="stock").justetf_basics


@pytest.fixture
def nasdaq(monkeypatch):
    payloads = {
        "earnings-surprise": "earnings_surprise.json",
        "earnings-forecast": "earnings_forecast.json",
        "peg-ratio": "peg_ratio.json",
    }
    ticker = Ticker(ticker="AAPL")
    calls = []

    def get_response(url, headers=None):
        calls.append(url)
        name = payloads[url.rsplit("/", 1)[-1]]
        return _response(
            payload=json.loads((FIXTURES / "nasdaq" / name).read_text()), url=url
        )

    monkeypatch.setattr(ticker, "get_response", get_response)
    ticker.calls = calls
    return ticker


def test_nasdaq_earnings_surprise(nasdaq):
    frame = nasdaq.quarterly_earnings_surprise
    assert frame.columns.tolist() == [
        "Fiscal Quarter End",
        "Date Reported",
        "Earnings Per Share*",
        "Consensus EPS* Forecast",
        "% Surprise",
    ]
    assert frame.iloc[0].tolist() == ["Jun 2026", "7/30/2026", 1.91, "1.88", "1.6"]
    assert nasdaq.calls == ["https://api.nasdaq.com/api/company/AAPL/earnings-surprise"]


def test_nasdaq_forecasts_share_one_request(nasdaq):
    yearly = nasdaq.yearly_earnings_forecast
    quarterly = nasdaq.quarterly_earnings_forecast
    assert yearly.columns[0] == "Fiscal Year End"
    assert quarterly.columns[0] == "Fiscal Quarter End"
    assert "High EPS* Forecast" in yearly.columns
    assert yearly.iloc[0]["Consensus EPS* Forecast"] == 8.75
    assert len(quarterly) == 5
    assert len(nasdaq.calls) == 1


def test_nasdaq_pe_and_peg(nasdaq):
    pe = nasdaq.price_to_earnings_ratio
    assert pe.columns.tolist() == ["Price to Earnings Ratio"]
    assert pe.loc["2025 Actual"].iloc[0] == 46.2
    peg = nasdaq.forecast_peg_rate
    assert peg.columns.tolist() == ["Forecast Price to Earning Growth Rate"]
    assert peg.loc["2026"].iloc[0] == 17.31
    assert peg.loc["Forecast 12 Month Forward PEG Ratio"].iloc[0] == 2.99
    assert len(nasdaq.calls) == 1


def test_nasdaq_empty_data_is_no_data(monkeypatch):
    ticker = Ticker(ticker="ZZZZ")
    monkeypatch.setattr(
        ticker,
        "get_response",
        lambda url, headers=None: _response(payload={"data": None}, url=url),
    )
    with pytest.raises(NoDataError):
        ticker.quarterly_earnings_surprise


def test_nasdaq_needs_stock():
    with pytest.raises(WrongSecurityType):
        Ticker(ticker="SPY", security_type="etf").yearly_earnings_forecast


def test_nasdaq_frames_are_dataframes(nasdaq):
    for name in (
        "quarterly_earnings_surprise",
        "yearly_earnings_forecast",
        "quarterly_earnings_forecast",
        "price_to_earnings_ratio",
        "forecast_peg_rate",
    ):
        assert isinstance(getattr(nasdaq, name), pd.DataFrame)
