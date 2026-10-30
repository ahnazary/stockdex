"""Offline isolation for the local Claude integration suite only."""

from datetime import datetime, timezone

import pandas as pd
import pytest
from curl_cffi import requests

from stockdex.claude_adapter import StockdexAdapter

# Every MCP tool the server must expose. Add new tools here and in claude_mcp.
EXPECTED_TOOLS = {
    "get_prices",
    "get_financial_statement",
    "get_dividends",
    "search_ticker",
    "get_company_profile",
    "get_key_statistics",
    "get_valuation_history",
    "get_analyst_estimates",
    "get_earnings_calendar",
    "get_holders",
    "get_sec_filings",
    "get_fund_holdings",
    "get_fund_profile",
    "get_splits",
    "get_options_chain",
    "get_quotes",
    "get_margins_and_ratios",
    "get_dividend_metrics",
    "get_revenue_breakdown",
    "get_insider_trades",
    "get_earnings_reaction",
}


@pytest.fixture(autouse=True)
def deny_network(monkeypatch):
    def denied(*args, **kwargs):
        pytest.fail(
            "Financial provider networking is forbidden in the local Claude tests"
        )

    # curl_cffi bypasses Python sockets; block its real network entry point.
    monkeypatch.setattr(requests.Session, "request", denied)


class FakeTicker:
    def __init__(self, ticker):
        self.ticker = ticker
        self.calls = []

    def yahoo_api_price(self, **kwargs):
        self.calls.append(kwargs)
        return pd.DataFrame(
            {
                "timestamp": pd.to_datetime(["2026-01-01", "2026-01-02"]),
                "open": [10, 11],
                "high": [12, 13],
                "low": [9, 10],
                "close": [11, float("nan")],
                "volume": [100, 200],
                "currency": ["USD", "USD"],
            }
        )

    def yahoo_api_income_statement(self, **kwargs):
        self.calls.append(kwargs)
        return pd.DataFrame(
            {
                "annualTotalRevenue": [1000, 2000],
                "annualNetIncome": [10, float("inf")],
            },
            index=["2024-12-31", "2025-12-31"],
        )

    yahoo_api_cash_flow = yahoo_api_income_statement
    yahoo_api_balance_sheet = yahoo_api_income_statement

    @staticmethod
    def yahoo_api_search(query, limit=10):
        return pd.DataFrame(
            {
                "symbol": ["BMW.DE", "BMWKY"],
                "shortname": ["BMW", "BMW ADR"],
                "quoteType": ["EQUITY", "EQUITY"],
                "exchange": ["GER", "PNK"],
            }
        ).head(limit)

    def yahoo_api_profile(self):
        return pd.DataFrame(
            {self.ticker: ["Cupertino", "Technology"]}, index=["city", "sector"]
        )

    def yahoo_api_summary_detail(self):
        return pd.DataFrame({self.ticker: [5.09e12, 1.07]}, index=["marketCap", "beta"])

    def yahoo_api_valuation_measures(self, frequency="quarterly", format="raw"):
        return pd.DataFrame(
            {
                f"{frequency}MarketCap": [3.2e12, 3.5e12],
                f"{frequency}PeRatio": [33.1, 35.0],
            },
            index=["2026-03-31", "2026-06-30"],
        )

    def yahoo_api_earnings_trend(self):
        return pd.DataFrame(
            {"period": ["0q", "+1q"], "earningsEstimate_avg": [1.98, 2.1]}
        )

    def yahoo_api_calendar_events(self):
        return pd.DataFrame(
            {self.ticker: [pd.Timestamp("2026-11-02 20:00", tz="UTC"), 1.98]},
            index=["earningsDate", "earningsAverage"],
        )

    def yahoo_api_institutional_holders(self):
        return pd.DataFrame({"organization": ["Blackrock Inc."], "pctHeld": [0.0797]})

    def yahoo_api_sec_filings(self):
        return pd.DataFrame(
            {
                "date": ["2026-09-01"],
                "type": ["8-K"],
                "exhibits": [[{"type": "8-K", "url": "https://example.com/x"}]],
            }
        )

    def yahoo_api_fund_top_holdings(self):
        return pd.DataFrame(
            {"symbol": ["NVDA", "AAPL"], "holdingPercent": [0.0836, 0.0735]}
        )

    def yahoo_api_fund_performance(self):
        return pd.DataFrame(
            {"fund": [0.1268, 0.1772], "category": [0.0514, 0.1554]},
            index=["ytd", "2025"],
        )

    def yahoo_api_dividends(self, range="max"):
        return pd.DataFrame(
            {"amount": [0.25, 0.26], "currency": ["USD", "USD"]},
            index=pd.DatetimeIndex(["2025-10-02", "2026-01-02"], tz="UTC", name="date"),
        )

    def yahoo_api_splits(self, range="max"):
        return pd.DataFrame(
            {"numerator": [4.0], "denominator": [1.0], "splitRatio": ["4:1"]},
            index=pd.DatetimeIndex(["2020-08-31"], tz="UTC", name="date"),
        )

    def yahoo_api_options_chain(self, expiration=None, option_type="both"):
        self.calls.append({"expiration": expiration, "option_type": option_type})
        kinds = ["call", "put"] if option_type == "both" else [option_type[:-1]]
        return pd.DataFrame(
            {
                "optionType": kinds,
                "strike": [350.0] * len(kinds),
                "bid": [9.5] * len(kinds),
                "expiration": [pd.Timestamp("2026-11-20", tz="UTC")] * len(kinds),
                "internalField": ["x"] * len(kinds),
            }
        )

    @staticmethod
    def yahoo_api_quotes(symbols):
        return pd.DataFrame(
            {
                "regularMarketPrice": [348.91, 530.14][: len(symbols)],
                "currency": ["USD", "USD"][: len(symbols)],
                "language": ["en-US", "en-US"][: len(symbols)],
            },
            index=pd.Index(symbols, name="symbol"),
        )

    @property
    def digrin_dividend(self):
        return pd.DataFrame(
            {
                "Ex-dividend date": ["2025-01-02", "2026-01-02"],
                "Payable date": ["-", "2026-01-10"],
                "Dividend amount (change)": ["—", "0.2600 USD (4%)"],
            }
        )

    def macrotrends_income_statement(self, frequency="annual"):
        self.calls.append({"macrotrends": "income_statement", "frequency": frequency})
        return pd.DataFrame(
            {
                "2025-09-30": ["416161", "112010", "7.46"],
                "2024-09-30": ["391035", "93736", ""],
                "2023-09-30": ["383285", "96995", "6.13"],
            },
            index=pd.Index(
                ["Revenue", "Net Income", "EPS - Earnings Per Share"],
                name="field_name",
            ),
        )

    macrotrends_cash_flow = macrotrends_income_statement
    macrotrends_balance_sheet = macrotrends_income_statement

    @staticmethod
    def _margin_frame(profit, margin, values):
        """A Macrotrends margin table with the dataset's own headers"""
        (revenue1, profit1, pct1), (revenue2, profit2, pct2) = values
        return pd.DataFrame(
            {
                "Date": ["", "2025-09-30", "2025-06-30"],
                "TTM Revenue": ["", revenue1, revenue2],
                profit: ["", profit1, profit2],
                margin: ["", pct1, pct2],
            }
        )

    @property
    def macrotrends_gross_margin(self):
        return self._margin_frame(
            "TTM Gross Profit",
            "Gross Margin",
            [("$416.16B", "$195.20B", "46.91%"), ("$408.62B", "$190.74B", "46.68%")],
        )

    @property
    def macrotrends_operating_margin(self):
        return self._margin_frame(
            "TTM Operating Income",
            "Operating Margin",
            [("$416.16B", "$133.05B", "31.97%"), ("$408.62B", "$130.21B", "31.87%")],
        )

    @property
    def macrotrends_ebitda_margin(self):
        return self._margin_frame(
            "TTM EBITDA",
            "EBITDA Margin",
            [("$416.16B", "$144.75B", "34.78%"), ("$408.62B", "$141.70B", "34.68%")],
        )

    @property
    def macrotrends_pre_tax_margin(self):
        return self._margin_frame(
            "TTM Pre-Tax Income",
            "Pre-Tax Margin",
            [("$416.16B", "$132.73B", "31.89%"), ("$408.62B", "$129.98B", "31.81%")],
        )

    @property
    def macrotrends_net_margin(self):
        return self._margin_frame(
            "TTM Net Income",
            "Net Margin",
            [("$416.16B", "$112.01B", "26.92%"), ("$408.62B", "$99.28B", "24.30%")],
        )

    @property
    def macrotrends_key_financial_ratios(self):
        return pd.DataFrame(
            {"2025-09-30": ["0.8933", "1.3436"], "2024-09-30": ["0.8673", ""]},
            index=pd.Index(["Current Ratio", "Debt/Equity Ratio"], name="field_name"),
        )

    @property
    def digrin_payout_ratio(self):
        return pd.DataFrame(
            {
                "Date": ["2026Q2 ", "2026Q3 "],
                "Payout ratio": ["51.55%", "56.87%"],
                "PE ratio": ["20.42", "23.02"],
            }
        )

    @property
    def digrin_dgr5(self):
        return pd.DataFrame(
            {
                "Year": ["2028 ", "2027 "],
                "Dividend": ["2.270USD ", "2.162USD "],
                "Estimated Yield on Cost": ["2.40%", "2.29%"],
            }
        )

    digrin_dgr3 = digrin_dgr5
    digrin_dgr10 = digrin_dgr5

    def finviz_dividends_annual_data(self):
        return pd.DataFrame(
            {
                "Ticker": ["KO", "KO"],
                "FiscalPeriod": ["2025FY", "2026FY"],
                "Amount": [2.04, 2.12],
                "Yield": [2.87, float("nan")],
                "Payout": [67.3, float("nan")],
                "Estimate": [False, True],
            }
        )

    def finviz_overall_dividend(self):
        return pd.DataFrame(
            [
                {
                    "lastClose": 94.559,
                    "dividendExDate": "2026-12-01T00:00:00",
                    "dividendEstimate": 2.198,
                    "dividendTTM": 2.1,
                }
            ]
        )

    def finviz_revenue_by_segment(self):
        rows = lambda values: pd.DataFrame(  # noqa: E731
            {
                "fiscal_year": ["2024", "2025"],
                "report_end_date": ["2024-09-28", "2025-09-27"],
                "source_filing_url": ["https://www.sec.gov/x", ""],
                "value": values,
            }
        )
        return {
            "Americas": rows([167045000000.0, 178353000000.0]),
            "Europe": rows([101328000000.0, 0.0]),
        }

    finviz_revenue_by_regions = finviz_revenue_by_segment
    finviz_revenue_by_products_and_services = finviz_revenue_by_segment

    def finviz_get_insider_trading(self):
        return pd.DataFrame(
            {
                "Insider Trading": ["Borders Ben", "Newstead Jennifer"],
                "Relationship": ["Principal Accounting Officer", "SVP, GC"],
                "Date": ["Oct 20 '26", "Oct 27 '26"],
                "Transaction": ["Sale", "Proposed Sale"],
                "Cost": ["339.62", "343.36"],
                "#Shares": ["2,399", "2,399"],
                "Value ($)": ["814,748", "823,721"],
                "#Shares Total": ["34,795", ""],
                "SEC Form 4": ["Oct 22 06:32 PM", "Oct 29 06:30 PM"],
            }
        )

    def finviz_earnings_data(self):
        return pd.DataFrame(
            {
                "ticker": ["AAPL", "AAPL"],
                "fiscalPeriod": ["2026Q3", "2026Q4"],
                "earningsDate": ["2026-07-30T16:30:00", "2026-11-02T16:30:00"],
                "fiscalEndDate": ["2026-06-30", "2026-09-30"],
                "epsActual": [2.02, float("nan")],
                "epsEstimate": [1.8919, 1.9897],
                "salesActual": [109417.0, float("nan")],
                "salesEstimate": [109038.8999, 113388.4769],
                "epsAnalysts": [32.0, 28.0],
            }
        )

    def finviz_earnings_revisions_data(self):
        return pd.DataFrame(
            {
                "fiscalPeriod": ["2026Q4", "2026Q4", "2026Q4"],
                "estimateType": ["E", "E", "S"],
                "estimateDate": [
                    "2026-10-26T00:00:00",
                    "2026-10-30T00:00:00",
                    "2026-10-30T00:00:00",
                ],
                "estimates": [28, 28, 26],
                "upRevisions": [2, 3, 1],
                "downRevisions": [0, 0, 2],
                "mean": [1.98, 1.9897, 113401.2137],
                "high": [2.1, 2.1, 117628.0],
                "low": [1.9, 1.9, 112525.022],
            }
        )

    def finviz_price_reaction_to_earnings_report(self):
        def point(diff, spy):
            return {"priceDiff": diff, "spyPriceDiff": spy}

        return pd.DataFrame(
            {
                "fiscalPeriod": ["2026Q3", "2026Q4"],
                "reportDate": ["2026-07-30T16:30:00", "2026-11-02T16:30:00"],
                "reactions": [
                    {
                        "minus_1_day": point(-1.4075012, 1.6765823),
                        "open": point(-8.583511, 0.40312958),
                        "close": point(-7.3538666, 0.71997833),
                        "plus_1_week": point(2.1, 1.0),
                        "plus_1_month": point(None, None),
                    },
                    {"minus_1_day": point(None, None)},
                ],
            }
        )


@pytest.fixture
def provider():
    return FakeTicker("AAPL")


@pytest.fixture
def adapter(provider):
    return StockdexAdapter(
        ticker_factory=lambda **kwargs: provider,
        clock=lambda: datetime(2026, 10, 3, tzinfo=timezone.utc),
    )
