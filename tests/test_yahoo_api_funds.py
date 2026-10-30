"""Offline tests for the Yahoo quoteSummary ETF and mutual fund methods."""

from types import SimpleNamespace

import pytest

from stockdex import Ticker

MODULES = {
    "topHoldings": {
        "maxAge": 1,
        "cashPosition": {"raw": 0.0025, "fmt": "0.25%"},
        "stockPosition": {"raw": 0.9975, "fmt": "99.75%"},
        "bondPosition": {"raw": 0.0, "fmt": "0.00%"},
        "holdings": [
            {
                "symbol": "NVDA",
                "holdingName": "NVIDIA Corp",
                "holdingPercent": {"raw": 0.0836, "fmt": "8.36%"},
            },
            {
                "symbol": "AAPL",
                "holdingName": "Apple Inc",
                "holdingPercent": {"raw": 0.0735, "fmt": "7.35%"},
            },
        ],
        "sectorWeightings": [
            {"realestate": {"raw": 0.017, "fmt": "1.70%"}},
            {"technology": {"raw": 0.4045, "fmt": "40.45%"}},
            {"energy": {}},
        ],
        "equityHoldings": {"priceToEarnings": {"raw": 0.04}},
    },
    "fundProfile": {
        "maxAge": 1,
        "family": "State Street Investment Management",
        "categoryName": "Large Blend",
        "legalType": "Exchange Traded Fund",
        "managementInfo": {"managerName": None},
        "feesExpensesInvestment": {
            "annualReportExpenseRatio": {"raw": 0.000945, "fmt": "0.09%"},
            "frontEndSalesLoad": {},
        },
        "feesExpensesInvestmentCat": {
            "annualReportExpenseRatio": {"raw": 0.0072, "fmt": "0.72%"},
        },
    },
    "fundPerformance": {
        "trailingReturns": {
            "asOfDate": {"raw": 1793145600, "fmt": "2026-10-28"},
            "ytd": {"raw": 0.1268, "fmt": "12.68%"},
            "oneYear": {"raw": 0.1563, "fmt": "15.63%"},
            "lastBullMkt": {"raw": 0.0, "fmt": "0.00%"},
        },
        "trailingReturnsCat": {"ytd": 0.0514, "oneYear": 0.2772},
        "annualTotalReturns": {
            "returns": [{"year": "2025", "annualValue": 0.1772}],
            "returnsCat": [{"year": "2025", "annualValue": 0.1554}],
        },
    },
}


@pytest.fixture
def fund(monkeypatch):
    ticker = Ticker("SPY", security_type="etf")

    def response(url):
        requested = url.split("modules=")[1].split("&")[0].split(",")
        result = {m: MODULES[m] for m in requested if m in MODULES}
        payload = {"quoteSummary": {"result": [result], "error": None}}
        return SimpleNamespace(json=lambda: payload)

    monkeypatch.setattr(ticker, "get_response", response)
    return ticker


def test_top_holdings(fund):
    frame = fund.yahoo_api_fund_top_holdings()
    assert list(frame["symbol"]) == ["NVDA", "AAPL"]
    assert frame.loc[0, "holdingPercent"] == 0.0836


def test_sector_weightings_sorted_and_skip_missing(fund):
    frame = fund.yahoo_api_fund_sector_weightings()
    assert list(frame.index) == ["technology", "realestate"]
    assert frame.loc["technology", "weight"] == 0.4045


def test_asset_allocation(fund):
    frame = fund.yahoo_api_fund_asset_allocation()
    assert frame.loc["stockPosition", "SPY"] == 0.9975
    assert frame.loc["bondPosition", "SPY"] == 0.0
    assert "equityHoldings" not in frame.index


def test_fund_profile_flattens_fees(fund):
    frame = fund.yahoo_api_fund_profile()
    values = frame["SPY"]
    assert values["family"] == "State Street Investment Management"
    assert values["annualReportExpenseRatio"] == 0.000945
    assert values["annualReportExpenseRatio_category"] == 0.0072
    assert "frontEndSalesLoad" not in frame.index
    assert "managementInfo" not in frame.index


def test_fund_performance_fund_vs_category(fund):
    frame = fund.yahoo_api_fund_performance()
    assert list(frame.columns) == ["fund", "category"]
    assert frame.loc["ytd", "fund"] == 0.1268
    assert frame.loc["oneYear", "category"] == 0.2772
    assert frame.loc["2025", "fund"] == 0.1772
    assert frame.loc["2025", "category"] == 0.1554
    assert "asOfDate" not in frame.index
    assert "lastBullMkt" not in frame.index


def test_stock_gets_empty_frames(monkeypatch):
    stock = Ticker("AAPL")
    calls = []

    def response(url):
        calls.append(url)
        if "modules=quoteType" in url:
            return SimpleNamespace(json=lambda: {"quoteSummary": {"result": [{}]}})
        raise RuntimeError(f"Failed to fetch URL (status 404): {url}")

    monkeypatch.setattr(stock, "get_response", response)
    for name in (
        "yahoo_api_fund_top_holdings",
        "yahoo_api_fund_sector_weightings",
        "yahoo_api_fund_asset_allocation",
        "yahoo_api_fund_profile",
        "yahoo_api_fund_performance",
    ):
        assert getattr(stock, name)().empty, name
